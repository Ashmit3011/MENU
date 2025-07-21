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
st.subheader("📜 Menu")
for category in categories:
    st.markdown(f"### 🍱 {category}")
    for item in menu[category]:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"₹{item['price']} {'🌶️' if item['spicy'] else ''} {'🌱' if item['veg'] else '🍖'}")
            with col2:
                if st.button("Add", key=item['id']):
                    found = False
                    for c in st.session_state.cart:
                        if c['id'] == item['id']:
                            c['qty'] += 1
                            found = True
                            break
                    if not found:
                        st.session_state.cart.append({"id": item['id'], "name": item['name'], "price": item['price'], "qty": 1})
                    st.success(f"Added {item['name']}")

# === Cart Summary ===
if st.session_state.cart:
    st.markdown("---")
    st.subheader("🛒 Your Cart")
    total = 0
    for item in st.session_state.cart:
        qty = st.number_input(f"{item['name']} (₹{item['price']})", value=item['qty'], min_value=1, key=f"qty_{item['id']}")
        item['qty'] = qty
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
        st.success("Order placed successfully!")
        st.session_state.order_placed = True
        st.session_state.order_id = order['id']
        st.session_state.cart = []

# === Order Status Tracking ===
if st.session_state.order_placed and st.session_state.order_id:
    st.markdown("---")
    st.subheader("📦 Order Status")
    orders = load_orders()
    current = next((o for o in orders if o['id'] == st.session_state.order_id), None)
    if current:
        status = current['status']
        st.markdown(f"**Current Status: `{status}`**")
        st.progress(["Pending", "Preparing", "Ready", "Served"].index(status) / 3)

        # Show feedback form when served
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

# === Real-time Refresh ===
time.sleep(5)
st.rerun()
