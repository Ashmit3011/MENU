import streamlit as st
import json
import os
import time
from datetime import datetime

# === File paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Load helpers ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f)
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_feedback(data):
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([], f)
    with open(FEEDBACK_FILE, "r") as f:
        feedbacks = json.load(f)
    feedbacks.append(data)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedbacks, f, indent=2)

# === UI config ===
st.set_page_config(page_title="📋 Smart Table Ordering", layout="centered")
st.markdown("""
    <style>
    .food-card {
        background-color: #ffffff0c;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #333;
    }
    .cart-card {
        background-color: #111111cc;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 2rem;
        border: 1px solid #444;
    }
    .plus-btn, .minus-btn {
        background-color: #0a84ff;
        color: white;
        font-size: 20px;
        border-radius: 5px;
        width: 40px;
        height: 40px;
        border: none;
        margin: 0 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Welcome to Our Restaurant")

menu = load_menu()
categories = list(menu.keys())

# === Session State Setup ===
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
if "order_id" not in st.session_state:
    st.session_state.order_id = None

# === Table number input ===
st.session_state.table = st.text_input("Enter your Table Number", st.session_state.table)

# === Menu Display ===
st.markdown("## 📜 Menu")
tabs = st.tabs(categories)

for i, category in enumerate(categories):
    with tabs[i]:
        for item in menu[category]:
            qty = 0
            for c in st.session_state.cart:
                if c['id'] == item['id']:
                    qty = c['qty']

            col1, col2 = st.columns([4, 2])
            with col1:
                st.markdown(f"""
                    <div class='food-card'>
                        <strong>{item['name']}</strong><br>
                        ₹{item['price']} {'🌶️' if item['spicy'] else ''} {'🌱' if item['veg'] else '🍖'}<br>
                        <small>Category: {category}</small>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("➖", key=f"minus_{item['id']}"):
                    for c in st.session_state.cart:
                        if c['id'] == item['id']:
                            c['qty'] -= 1
                            if c['qty'] <= 0:
                                st.session_state.cart = [x for x in st.session_state.cart if x['id'] != item['id']]
                            break
                st.write(f"Qty: {qty}")
                if st.button("➕", key=f"plus_{item['id']}"):
                    found = False
                    for c in st.session_state.cart:
                        if c['id'] == item['id']:
                            c['qty'] += 1
                            found = True
                            break
                    if not found:
                        st.session_state.cart.append({"id": item['id'], "name": item['name'], "price": item['price'], "qty": 1})

# === Cart Summary ===
if st.session_state.cart:
    st.markdown("<div class='cart-card'>", unsafe_allow_html=True)
    st.subheader("🛒 Your Cart")
    total = 0
    for item in st.session_state.cart:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
        with col2:
            st.markdown(f"Qty: {item['qty']}")
        with col3:
            if st.button("❌", key=f"remove_{item['id']}"):
                st.session_state.cart = [c for c in st.session_state.cart if c['id'] != item['id']]
                st.rerun()
        total += item['qty'] * item['price']

    st.markdown(f"### Total: ₹{total}")
    if st.button("✅ Place Order"):
        order = {
            "id": f"order{int(time.time())}",
            "table": st.session_state.table,
            "items": st.session_state.cart,
            "total": total,
            "status": "Pending",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        st.success("🎉 Order placed successfully!")
        st.session_state.order_placed = True
        st.session_state.order_id = order['id']
        st.session_state.cart = []
    st.markdown("</div>", unsafe_allow_html=True)

# === Order Status Tracking ===
if st.session_state.order_id:
    orders = load_orders()
    current = next((o for o in orders if o['id'] == st.session_state.order_id), None)
    if current:
        st.markdown("---")
        st.subheader("📦 Order Status")
        status = current['status']
        st.markdown(f"**Current Status:** <span style='color:lightgreen'>{status}</span>", unsafe_allow_html=True)
        st.progress(["Pending", "Preparing", "Ready", "Served"].index(status) / 3)

        if status == "Served":
            st.markdown("---")
            st.subheader("📝 Feedback")
            rating = st.slider("How was your experience?", 1, 5, 4)
            comment = st.text_area("Leave a comment")
            if st.button("Submit Feedback"):
                save_feedback({
                    "table": st.session_state.table,
                    "rating": rating,
                    "comment": comment,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Thanks for your feedback!")

# === Real-time Refresh every 5 sec ===
time.sleep(5)
st.rerun()
