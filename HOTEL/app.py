import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# === Absolute File Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Utility Functions ===
def load_json(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# === Load Menu & Orders ===
menu = load_json(MENU_FILE, {})
orders = load_json(ORDERS_FILE, [])
feedbacks = load_json(FEEDBACK_FILE, [])

# === Hide Sidebar ===
st.set_page_config(page_title="Smart Menu", layout="wide")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# === Table Number Input ===
st.markdown("## 🪑 Welcome! Please enter your Table Number")
table_number = st.text_input("Table Number", key="table_number_input", label_visibility="collapsed", placeholder="Enter table number")

if table_number:
    st.session_state.table_number = table_number

# === Session State Initialization ===
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"

# === Menu Section ===
st.markdown("---")
st.markdown("## 🍽️ Menu")

all_categories = sorted(list(set([item.get("category", "Other") for item in menu.values()])))
selected = st.selectbox("Select Category", ["All"] + all_categories)
if st.button("🔍 Filter Menu"):
    st.session_state.selected_category = selected

category = st.session_state.selected_category
filtered_menu = {k: v for k, v in menu.items() if v.get("category") == category} if category != "All" else menu

for key, item in filtered_menu.items():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**{item['name']}**")
        st.markdown(f"💸 ₹{item['price']}")
    with col2:
        qty = st.number_input("Qty", min_value=0, max_value=20, key=f"qty_{key}")
    with col3:
        if st.button("➕ Add", key=f"add_{key}"):
            if key in st.session_state.cart:
                st.session_state.cart[key]["quantity"] += qty
            else:
                st.session_state.cart[key] = {
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": qty
                }
            st.success(f"{item['name']} added to cart!")

# === Cart Section ===
st.markdown("---")
st.markdown("## 🛒 Your Cart")

if st.session_state.cart:
    total = 0
    for item in st.session_state.cart.values():
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        st.markdown(f"- {item['name']} x {item['quantity']} = ₹{subtotal}")
    st.markdown(f"### 💰 Total: ₹{total}")
    
    if st.button("✅ Place Order"):
        new_order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "total": total,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        save_json(ORDERS_FILE, orders)
        st.success("🎉 Order placed successfully!")

        # Clear cart
        st.session_state.cart = {}

        # Show feedback form
        with st.form("feedback_form"):
            st.markdown("### 📝 Leave Feedback")
            message = st.text_area("How was your experience?")
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                feedbacks.append({
                    "table": st.session_state.table_number,
                    "message": message,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_json(FEEDBACK_FILE, feedbacks)
                st.success("🙏 Thanks for your feedback!")

else:
    st.info("Your cart is empty.")

from streamlit_autorefresh import st_autorefresh

# Add this near the end of your file
st_autorefresh(interval=5000, key="refresh")