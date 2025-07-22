import streamlit as st
import json
import os
import time
from datetime import datetime

# Hide sidebar
st.set_page_config(page_title="Smart Menu", layout="wide")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# Utility functions
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# Load data
menu_data = load_json(MENU_FILE, {})
orders = load_json(ORDERS_FILE, [])

# Session state initialization
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "table_number" not in st.session_state:
    st.session_state.table_number = ""

# Table number input
st.markdown("### 🪑 Enter Table Number")
st.session_state.table_number = st.text_input("Table Number", st.session_state.table_number, key="table_input")

# Auto-scrollable category bar
st.markdown("### 🍽️ Select a Category")
categories = list(menu_data.keys())

# Show categories horizontally
category_col = st.columns(len(categories))
selected_category = st.query_params.get("category", [categories[0]])[0] if st.query_params.get("category") else categories[0]

for i, cat in enumerate(categories):
    if category_col[i].button(cat, use_container_width=True):
        st.experimental_set_query_params(category=cat, t=str(int(time.time())))
        selected_category = cat

# Menu UI
st.markdown(f"## 📋 Menu - {selected_category}")

if selected_category in menu_data:
    menu_items = menu_data[selected_category]
    item_cols = st.columns(2)
    for idx, item in enumerate(menu_items):
        with item_cols[idx % 2]:
            st.markdown(f"""
                <div style='background-color:#f3f4f6; padding:1rem; margin-bottom:1rem; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.1);'>
                    <h4 style='margin-bottom:0.5rem;'>{item['name']}</h4>
                    <div style='color: #4b5563;'>₹{item['price']}</div>
                    <button style='margin-top:10px; background:#10b981; color:white; border:none; padding:6px 12px; border-radius:5px; cursor:pointer;' onclick="window.location.href='?category={selected_category}&item={item['name']}&t={int(time.time())}'">Add to Cart</button>
                </div>
            """, unsafe_allow_html=True)

# Handle cart addition
params = st.query_params
if "item" in params:
    item_name = params["item"][0]
    for item in menu_data[selected_category]:
        if item["name"] == item_name:
            if item_name not in st.session_state.cart:
                st.session_state.cart[item_name] = {
                    "price": item["price"],
                    "quantity": 1
                }
            else:
                st.session_state.cart[item_name]["quantity"] += 1
            break
    st.experimental_set_query_params(category=selected_category, t=str(int(time.time())))

# Cart display
st.markdown("## 🛒 Your Cart")
if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for name, details in st.session_state.cart.items():
        qty = details["quantity"]
        price = details["price"]
        subtotal = qty * price
        total += subtotal
        st.write(f"**{name}** — ₹{price} × {qty} = ₹{subtotal}")

    st.markdown(f"### 💰 Total: ₹{total}")

    if st.button("✅ Place Order"):
        if st.session_state.table_number:
            orders.append({
                "table": st.session_state.table_number,
                "items": st.session_state.cart,
                "total": total,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(ORDERS_FILE, orders)
            st.success("Order placed successfully!")
            st.session_state.cart.clear()
        else:
            st.warning("Please enter your table number before placing the order.")

# Feedback section after order
if not st.session_state.cart:
    st.markdown("---")
    st.markdown("### 📝 Leave Feedback")
    feedback = st.text_area("How was your experience?")
    if st.button("Submit Feedback"):
        if st.session_state.table_number and feedback.strip():
            feedback_data = load_json(FEEDBACK_FILE, [])
            feedback_data.append({
                "table": st.session_state.table_number,
                "message": feedback.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, feedback_data)
            st.success("Thanks for your feedback!")
        else:
            st.warning("Please enter your table number and feedback.")