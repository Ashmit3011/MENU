import streamlit as st
import json
import os
import time
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# Utilities
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# Set Streamlit page config
st.set_page_config(page_title="Smart Menu", layout="wide")
hide_sidebar_style = """<style>[data-testid="stSidebar"] {display: none !important;}</style>"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# App title
st.markdown("<h1 style='text-align: center;'>🍽️ Smart Table Ordering</h1>", unsafe_allow_html=True)

# Load menu
menu_data = load_json(MENU_FILE, {})

if not menu_data:
    st.error("❌ Menu is empty. Please contact admin.")
    st.stop()

categories = list(menu_data.keys())

# Read category from query params
query_params = st.experimental_get_query_params()
selected_category = query_params.get("category", [categories[0]])[0]

# Table Number Input (Top Bar)
if "table_number" not in st.session_state:
    st.session_state.table_number = st.number_input("Enter Table Number:", min_value=1, step=1, key="table_input")

# Cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Category Selector UI
st.markdown("### 🧾 Choose a Category")
category_container = st.container()
with category_container:
    cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        if cols[i].button(cat):
            st.experimental_set_query_params(category=cat, t=str(int(time.time())))
            selected_category = cat

st.markdown("---")

# Display menu for selected category
st.markdown(f"### 📋 Menu - {selected_category}")
for item in menu_data[selected_category]:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{item['name']}**  \n₹{item['price']}")
    with col2:
        if st.button("Add", key=f"add_{item['name']}"):
            if item["name"] not in st.session_state.cart:
                st.session_state.cart[item["name"]] = {
                    "price": item["price"],
                    "quantity": 1
                }
            else:
                st.session_state.cart[item["name"]]["quantity"] += 1
            st.experimental_set_query_params(category=selected_category, t=str(int(time.time())))

# Divider
st.markdown("---")

# Show Cart
st.markdown("### 🛒 Your Cart")
if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for item, info in st.session_state.cart.items():
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
        with col1:
            st.markdown(f"**{item}**")
        with col2:
            st.markdown(f"₹{info['price']}")
        with col3:
            qty = st.number_input("Qty", min_value=1, value=info["quantity"], key=f"qty_{item}")
            st.session_state.cart[item]["quantity"] = qty
        with col4:
            if st.button("❌ Remove", key=f"remove_{item}"):
                del st.session_state.cart[item]
                st.experimental_rerun()

        total += info["price"] * info["quantity"]

    st.markdown(f"### 💰 Total: ₹{total}")

    if st.button("✅ Place Order"):
        new_order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders = load_json(ORDERS_FILE, [])
        orders.append(new_order)
        save_json(ORDERS_FILE, orders)
        st.success("✅ Order placed successfully!")

        # Save session table and show feedback
        table_no = st.session_state.table_number
        st.session_state.cart = {}

        with st.form("feedback_form"):
            st.markdown("### 💬 Leave Feedback")
            message = st.text_area("Feedback Message", key="feedback_msg")
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                feedbacks = load_json(FEEDBACK_FILE, [])
                feedbacks.append({
                    "table": table_no,
                    "message": message,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_json(FEEDBACK_FILE, feedbacks)
                st.success("🙏 Thank you for your feedback!")