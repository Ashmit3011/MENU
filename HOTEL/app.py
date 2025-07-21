import streamlit as st
import json
import os
from datetime import datetime

# Setup file paths using os.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDER_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# Load menu data
def load_menu():
    if not os.path.exists(MENU_FILE):
        return []
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Save order to orders.json
def save_order(order):
    orders = []
    if os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "r", encoding="utf-8") as f:
            try:
                orders = json.load(f)
            except json.JSONDecodeError:
                pass
    orders.append(order)
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

# Save feedback
def save_feedback(feedback):
    feedbacks = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            try:
                feedbacks = json.load(f)
            except json.JSONDecodeError:
                pass
    feedbacks.append(feedback)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

# Hide sidebar
st.set_page_config(page_title="Smart Restaurant Ordering", layout="wide", initial_sidebar_state="collapsed")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Title
st.title("🍽️ Welcome to Smart Restaurant Ordering")

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""

# Load menu
menu = load_menu()

# Category filter
categories = sorted(set(item["category"] for item in menu))
selected_category = st.selectbox("📂 Select Category", ["All"] + categories)

# Menu listing
st.subheader("📋 Menu")
for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue

    with st.container():
        st.markdown(f"### {item['name']} - ₹{item['price']}")
        st.caption(f"{item.get('description', '')}")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"🌶️ Spicy: {item.get('spicy', 'No')} | 🥗 Veg: {item.get('veg', 'Yes')}")
        with col2:
            qty = st.number_input(f"Qty for {item['name']}", min_value=0, max_value=10, key=f"qty_{item['id']}")
            if qty > 0:
                st.session_state.cart.append({**item, "qty": qty})
                st.success(f"Added {qty} x {item['name']} to cart.")

# Cart display
st.subheader("🛒 Your Cart")
if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']
    st.markdown(f"### 🧾 Total: ₹{total}")

    st.session_state.table = st.text_input("Enter Table Number", value=st.session_state.table)

    if st.button("✅ Place Order"):
        if not st.session_state.table.strip():
            st.warning("Please enter your table number.")
        else:
            order = {
                "id": int(datetime.now().timestamp()),
                "table": st.session_state.table,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cart": st.session_state.cart,
                "status": "Pending"
            }
            save_order(order)
            st.session_state.cart = []
            st.success("✅ Order placed successfully!")

            st.balloons()
else:
    st.info("🛒 Your cart is empty.")

# Feedback section
st.markdown("---")
st.subheader("💬 Leave Feedback")
with st.form("feedback_form"):
    fb_table = st.text_input("Table Number", value=st.session_state.table)
    rating = st.slider("Rating", 1, 5, 4)
    comments = st.text_area("Any comments?")
    submitted = st.form_submit_button("Submit Feedback")
    if submitted:
        feedback = {
            "table": fb_table,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_feedback(feedback)
        st.success("🙏 Thank you for your feedback!")
