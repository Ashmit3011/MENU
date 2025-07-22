import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

# Load/save functions
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# UI settings
st.set_page_config(page_title="Smart Menu", layout="wide")
st.markdown("<h1 style='text-align:center;'>🍽️ Smart Table Menu</h1>", unsafe_allow_html=True)

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .menu-card {
            background: #f9fafb;
            padding: 1.2rem;
            border-radius: 15px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        .menu-title {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .price {
            color: green;
        }
    </style>
""", unsafe_allow_html=True)

# Enter table number
table_num = st.text_input("Enter your Table Number", key="table_input")

# Load menu
menu = load_json(MENU_FILE, {})

# Get all categories
all_categories = sorted(set(item.get("category", "Uncategorized") for item in menu.values()))

selected_category = st.selectbox("Select Category", ["All"] + all_categories)
if st.button("🔍 Filter Menu"):
    if selected_category != "All":
        filtered_menu = {k: v for k, v in menu.items() if v.get("category") == selected_category}
    else:
        filtered_menu = menu
else:
    filtered_menu = menu

# Shopping cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

st.subheader("📜 Menu")
if not filtered_menu:
    st.info("No items in this category.")
else:
    for item_name, details in filtered_menu.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<div class='menu-card'><span class='menu-title'>{item_name}</span><br>"
                        f"<small>{details.get('category', '')}</small><br>"
                        f"<span class='price'>₹{details['price']}</span></div>", unsafe_allow_html=True)
        with col2:
            qty = st.number_input(f"Qty for {item_name}", min_value=0, max_value=10, step=1, key=f"qty_{item_name}")
            if qty > 0:
                st.session_state.cart[item_name] = {
                    "quantity": qty,
                    "price": details["price"]
                }
            elif item_name in st.session_state.cart:
                del st.session_state.cart[item_name]

# Show cart
st.markdown("---")
st.subheader("🛒 Your Order")
if not st.session_state.cart:
    st.info("Cart is empty.")
else:
    total = 0
    for name, info in st.session_state.cart.items():
        subtotal = info["price"] * info["quantity"]
        total += subtotal
        st.write(f"{name} x {info['quantity']} = ₹{subtotal}")
    st.write(f"### 💰 Total: ₹{total}")
    if st.button("✅ Confirm Order"):
        if not table_num:
            st.warning("Please enter your table number.")
        else:
            orders = load_json(ORDERS_FILE, [])
            orders.append({
                "table": table_num,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": st.session_state.cart,
                "status": "Pending"
            })
            save_json(ORDERS_FILE, orders)
            st.success("✅ Order placed successfully!")
            st.session_state.cart = {}

# Feedback after completion
orders = load_json(ORDERS_FILE, [])
feedbacks = load_json(FEEDBACK_FILE, [])

completed_orders = [o for o in orders if o.get("table") == table_num and o.get("status") == "Completed"]
if completed_orders:
    st.markdown("---")
    st.subheader("📝 Leave Feedback")
    feedback_msg = st.text_area("How was your experience?", key="feedback")
    if st.button("📨 Submit Feedback"):
        feedbacks.append({
            "table": table_num,
            "message": feedback_msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(FEEDBACK_FILE, feedbacks)
        st.success("🙌 Thank you for your feedback!")