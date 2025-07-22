import streamlit as st
import json
import os
import time
from datetime import datetime

# --- Utility functions ---
def load_json(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- File paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# --- Page config ---
st.set_page_config(page_title="Smart Table Menu", layout="wide", initial_sidebar_state="collapsed")

# --- Table Input UI ---
if "table_number" not in st.session_state:
    st.session_state.table_number = st.number_input("Enter your table number:", min_value=1, step=1)

table_number = st.session_state.table_number

# --- Load menu and orders ---
menu_data = load_json(MENU_FILE, {})
orders_data = load_json(ORDERS_FILE, [])
cart = st.session_state.get("cart", {})

# --- Category filter ---
query_params = st.query_params
selected_category = query_params.get("category", [None])[0]

# --- Category UI (Scrollable Buttons) ---
st.markdown("## 🧾 Menu")
st.markdown("#### 🍽️ Select Category:")
cols = st.columns(len(menu_data))

for i, cat in enumerate(menu_data.keys()):
    with cols[i]:
        if st.button(cat, use_container_width=True):
            st.query_params.update(category=cat, t=int(time.time()))

# --- Menu UI Display ---
if selected_category and selected_category in menu_data:
    items = menu_data[selected_category]
    st.markdown(f"### 📋 Items in **{selected_category}**")
    
    for item in items:
        name = item["name"]
        price = item["price"]
        col1, col2, col3 = st.columns([4, 1, 2])
        with col1:
            st.write(f"**{name}**")
        with col2:
            st.write(f"₹{price}")
        with col3:
            qty = st.number_input(f"Qty for {name}", min_value=0, step=1, key=name)
            if qty > 0:
                cart[name] = {"price": price, "quantity": qty}
else:
    st.info("Please select a category to view items.")

st.session_state.cart = cart

# --- Cart Summary ---
if cart:
    st.markdown("---")
    st.markdown("### 🛒 Your Order")
    total = 0
    for name, item in cart.items():
        price = item["price"]
        qty = item["quantity"]
        subtotal = price * qty
        total += subtotal
        st.write(f"- {name} × {qty} = ₹{subtotal}")
    
    st.markdown(f"### 💵 Total: ₹{total}")

    if st.button("✅ Place Order"):
        new_order = {
            "table": table_number,
            "items": cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders_data.append(new_order)
        save_json(ORDERS_FILE, orders_data)
        st.success("✅ Order placed successfully!")
        st.session_state.cart = {}

# --- Order Status Display ---
st.markdown("---")
st.markdown("### 🔄 Your Previous Orders")

table_orders = [o for o in orders_data if o["table"] == table_number]

if not table_orders:
    st.info("No orders yet.")
else:
    for o in reversed(table_orders[-5:]):
        st.write(f"🕒 {o['timestamp']} - Status: **{o['status']}**")

# --- Feedback Section (Only after order completion) ---
completed_orders = [o for o in table_orders if o["status"] == "Completed"]

if completed_orders:
    st.markdown("---")
    st.markdown("### ✍️ Leave Feedback")

    with st.form("feedback_form"):
        message = st.text_area("Your feedback:")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted and message.strip():
            feedbacks = load_json(FEEDBACK_FILE, [])
            feedbacks.append({
                "table": table_number,
                "message": message.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, feedbacks)
            st.success("✅ Thank you for your feedback!")