import streamlit as st
import json
import os
import time
from datetime import datetime

# ----- Setup -----
st.set_page_config(page_title="Smart Table Ordering", layout="wide", initial_sidebar_state="collapsed")

# ----- Helper Functions -----
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# ----- File Paths -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "..", "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "..", "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "..", "feedback.json")

# ----- Session State Initialization -----
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table_number" not in st.session_state:
    st.session_state.table_number = ""

# ----- Hide Sidebar -----
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ----- Table Number -----
st.markdown("## 🪑 Enter Your Table Number")
st.session_state.table_number = st.text_input("Table Number", st.session_state.table_number, label_visibility="collapsed")

if not st.session_state.table_number:
    st.warning("Please enter your table number to continue.")
    st.stop()

# ----- Load Menu -----
menu_data = load_json(MENU_FILE, {})

# ----- Category Selection -----
st.markdown("## 🍽️ Menu")
categories = list(menu_data.keys())
selected_category = st.selectbox("Select Category", categories)

# ----- Display Menu Items -----
if selected_category and selected_category in menu_data:
    items = menu_data[selected_category]
    for item in items:
        name = item["name"]
        price = item["price"]

        st.markdown(f"""
        <div style='padding:1rem; margin-bottom:1rem; border: 1px solid #ddd; border-radius:10px; background:#f9fafb'>
            <strong>{name}</strong> - ₹{price}
            <button onclick="window.location.href='#{name}'" style='float:right;background:#2563eb;color:white;padding:0.3rem 0.6rem;border:none;border-radius:5px;cursor:pointer;'>Add</button>
        </div>
        """, unsafe_allow_html=True)

        if name not in st.session_state.cart:
            if st.button(f"Add {name}", key=name):
                st.session_state.cart.append({"name": name, "price": price, "quantity": 1})
        else:
            for cart_item in st.session_state.cart:
                if cart_item["name"] == name:
                    cart_item["quantity"] += 1

# ----- Cart Preview -----
st.markdown("## 🛒 Your Cart")
if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for item in st.session_state.cart:
        st.markdown(f"**{item['name']} x {item['quantity']}** — ₹{item['price'] * item['quantity']}")
        total += item['price'] * item['quantity']

    st.markdown(f"### 💰 Total: ₹{total}")

    # ----- Place Order Button -----
    if st.button("✅ Place Order"):
        orders = load_json(ORDERS_FILE, [])
        new_order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        save_json(ORDERS_FILE, orders)

        # clear cart
        st.session_state.cart = []
        st.success("✅ Order placed successfully!")

# ----- Feedback Section -----
        st.markdown("### 📝 Leave Feedback (optional)")
        feedback_message = st.text_area("Your feedback...")
        if st.button("📤 Submit Feedback"):
            feedbacks = load_json(FEEDBACK_FILE, [])
            feedbacks.append({
                "table": st.session_state.table_number,
                "message": feedback_message,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, feedbacks)
            st.success("✅ Thank you for your feedback!")

        st.rerun()

# ----- Auto Refresh -----
st.query_params(t=int(time.time()))