import streamlit as st
import json
import uuid
import os
from datetime import datetime
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# Load JSON data
def load_json(file_path, default):
    if not file_path.exists():
        file_path.write_text(json.dumps(default), encoding="utf-8")
    return json.loads(file_path.read_text(encoding="utf-8"))

def save_json(file_path, data):
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

menu = load_json(MENU_FILE, [])
orders = load_json(ORDER_FILE, [])
feedback = load_json(FEEDBACK_FILE, [])

st.set_page_config(page_title="Smart Table Ordering", layout="centered")
st.markdown("""
    <style>
        .stButton button {margin: 0 5px;}
        .cart-card {box-shadow: 0 4px 8px rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; background: #fff; margin-bottom: 10px;}
        .emoji {font-size: 1.2em; margin-right: 4px;}
        .confirm-box {background: #e0ffe0; padding: 10px; border: 2px dashed green; margin-top: 20px; border-radius: 10px; text-align: center;}
        .tracker {background: #f5f5f5; border-radius: 10px; padding: 10px; margin-top: 20px; text-align: center;}
        .step {display: inline-block; padding: 8px 12px; border-radius: 8px; background: #ddd; margin: 0 5px;}
        .step.active {background: #90ee90; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Welcome to Smart Cafe")

# Cart management
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_id" not in st.session_state:
    st.session_state.order_id = None

# Category filter
categories = sorted(set(item.get("category", "Uncategorized") for item in menu))
selected_category = st.selectbox("Select Category", ["All"] + categories)

# Filtered menu
filtered_menu = [item for item in menu if selected_category in ("All", item.get("category", ""))]

st.subheader("Menu")
for item in filtered_menu:
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"**{item['name']}**")
        st.markdown(f"💰 ₹{item['price']}")
    with col2:
        if st.button("Add", key=f"add_{item['id']}"):
            if item['id'] in st.session_state.cart:
                st.session_state.cart[item['id']]['quantity'] += 1
            else:
                st.session_state.cart[item['id']] = {
                    "name": item['name'],
                    "price": item['price'],
                    "quantity": 1,
                    "id": item['id']
                }

# Cart
st.header("🛒 Your Cart")
cart_items = list(st.session_state.cart.values())
if cart_items:
    total = 0
    for item in cart_items:
        st.markdown(f"""
        <div class="cart-card">
            <strong>{item['name']}</strong><br>
            💸 ₹{item['price']} x {item['quantity']} = ₹{item['price'] * item['quantity']}<br><br>
            <form>
                <button type="submit" name="inc" formaction="" formmethod="POST">➕</button>
                <button type="submit" name="dec" formaction="" formmethod="POST">➖</button>
            </form>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➕", key=f"plus_{item['id']}"):
            item['quantity'] += 1
        if st.button("➖", key=f"minus_{item['id']}"):
            item['quantity'] -= 1
            if item['quantity'] <= 0:
                del st.session_state.cart[item['id']]
        total += item['price'] * item['quantity']
    st.markdown(f"**Total: ₹{total}**")
    table_number = st.text_input("Enter your Table Number")
    if st.button("Place Order") and table_number:
        new_order = {
            "id": str(uuid.uuid4()),
            "table": table_number,
            "items": cart_items,
            "total": total,
            "status": "Placed",
            "timestamp": datetime.now().isoformat()
        }
        orders.append(new_order)
        save_json(ORDER_FILE, orders)
        st.session_state.order_id = new_order["id"]
        st.session_state.cart = {}
        st.success("Order placed successfully!")
        st.markdown("""
            <div class='confirm-box'>✅ Your order has been placed!<br>Track your order status below.</div>
        """, unsafe_allow_html=True)
else:
    st.info("Your cart is empty. Please add items.")

# Order Tracker
if st.session_state.order_id:
    current_order = next((o for o in orders if o['id'] == st.session_state.order_id), None)
    if current_order:
        st.subheader("🚚 Order Tracking")
        status_steps = ["Placed", "Preparing", "Ready", "Served"]
        st.markdown("<div class='tracker'>" +
                    " ".join([f"<span class='step {'active' if step == current_order['status'] else ''}'>{step}</span>" for step in status_steps]) +
                    "</div>", unsafe_allow_html=True)

        if current_order['status'] == "Placed" and st.button("Cancel Order"):
            orders = [o for o in orders if o['id'] != current_order['id']]
            save_json(ORDER_FILE, orders)
            st.session_state.order_id = None
            st.warning("Order cancelled.")

        if current_order['status'] == "Served":
            st.subheader("💬 Feedback")
            feedback_text = st.text_area("How was your experience?")
            if st.button("Submit Feedback"):
                feedback.append({
                    "order_id": current_order['id'],
                    "table": current_order['table'],
                    "message": feedback_text,
                    "time": datetime.now().isoformat()
                })
                save_json(FEEDBACK_FILE, feedback)
                st.success("Thanks for your feedback!")
                st.session_state.order_id = None
