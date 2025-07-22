import streamlit as st
import json
import os
import time
from datetime import datetime

# --- Setup paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# --- Utilities ---
def load_json(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# --- Session State ---
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "table_number" not in st.session_state:
    st.session_state.table_number = None

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Smart Menu")
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        #MainMenu, header, footer {visibility: hidden;}
        .category-btn {
            padding: 0.5rem 1rem;
            border-radius: 10px;
            border: 2px solid #ccc;
            margin: 0.3rem;
            background-color: #f3f4f6;
            color: #111827;
            font-weight: 500;
            cursor: pointer;
        }
        .category-btn:hover {
            background-color: #e5e7eb;
        }
        .active-category {
            background-color: #4f46e5 !important;
            color: white !important;
            border-color: #4338ca !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Table Number Input (Not in Sidebar) ---
if not st.session_state.table_number:
    table_input = st.text_input("Enter Your Table Number to Start Ordering:", key="table_input")
    if table_input:
        st.session_state.table_number = table_input
        st.experimental_rerun()
    st.stop()

# --- Load Menu Data ---
menu_data = load_json(MENU_FILE, {})
categories = list(menu_data.keys())

# --- Category Filter ---
st.markdown("### 🍽️ Select a Category")
selected_category = st.query_params.get("category", categories[0] if categories else "")

cols = st.columns(len(categories))
for i, cat in enumerate(categories):
    style_class = "category-btn active-category" if cat == selected_category else "category-btn"
    if cols[i].button(cat, key=f"cat_{cat}"):
        st.query_params(category=cat, t=int(time.time()))
        st.experimental_rerun()

# --- Display Items for Selected Category ---
st.markdown("## 🧾 Menu")

if selected_category in menu_data:
    for item in menu_data[selected_category]:
        name = item["name"]
        price = item["price"]
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{name}** - ₹{price}")
        with col2:
            if st.button("➕ Add", key=f"add_{name}"):
                if name in st.session_state.cart:
                    st.session_state.cart[name]["qty"] += 1
                else:
                    st.session_state.cart[name] = {"price": price, "qty": 1}
                st.experimental_rerun()
else:
    st.warning("No items found in this category.")

# --- Cart Section ---
st.markdown("---")
st.markdown("### 🛒 Cart")

if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for name, item in st.session_state.cart.items():
        qty = item["qty"]
        price = item["price"]
        subtotal = qty * price
        total += subtotal
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        col1.markdown(f"**{name}**")
        col2.markdown(f"{qty}")
        col3.markdown(f"₹{subtotal}")
        if col4.button("🗑️", key=f"remove_{name}"):
            del st.session_state.cart[name]
            st.experimental_rerun()

    st.markdown(f"### 💰 Total: ₹{total}")
    if st.button("✅ Place Order"):
        orders = load_json(ORDERS_FILE, [])
        orders.append({
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "total": total,
            "status": "Received",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(ORDERS_FILE, orders)
        st.success("Order Placed!")
        st.session_state.cart = {}
        st.session_state.feedback_ready = True
        st.experimental_rerun()

# --- Feedback Section ---
if st.session_state.get("feedback_ready"):
    st.markdown("---")
    st.markdown("### 📝 Feedback")
    feedback = st.text_area("Leave your feedback (optional):", key="feedback_text")
    if st.button("📤 Submit Feedback"):
        feedbacks = load_json(FEEDBACK_FILE, [])
        feedbacks.append({
            "table": st.session_state.table_number,
            "message": feedback,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(FEEDBACK_FILE, feedbacks)
        st.success("Thank you for your feedback!")
        del st.session_state["feedback_ready"]