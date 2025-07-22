import streamlit as st
import json
import os
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=5000, key="autorefresh")

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# Page config
st.set_page_config(page_title="Smart Menu", layout="wide")
st.title("🍽️ Smart Table Ordering")

# Load/save JSON
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Load menu
menu = load_json(MENU_FILE, {})

# Session state init
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "table_number" not in st.session_state:
    st.session_state.table_number = ""
if "category" not in st.session_state:
    st.session_state.category = "All"

# Table number input
if not st.session_state.table_number:
    st.session_state.table_number = st.text_input("Enter Table Number:")
    st.stop()

st.markdown(f"**🪑 Table:** {st.session_state.table_number}")

# ---- CATEGORY FILTER ----
all_categories = sorted(set(item.get("category", "Uncategorized") for item in menu.values()))
selected = st.radio("📂 Choose Category", ["All"] + all_categories, index=(["All"] + all_categories).index(st.session_state.category), horizontal=True)
st.session_state.category = selected

# ---- MENU DISPLAY ----
st.markdown("## 🧾 Menu")
filtered_menu = {
    k: v for k, v in menu.items()
    if selected == "All" or v.get("category") == selected
}

if not filtered_menu:
    st.warning("No items in this category.")
else:
    for name, info in filtered_menu.items():
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {name}")
                st.caption(info.get("description", ""))
                st.markdown(f"💵 ₹{info.get('price', 0)}")
            with col2:
                qty = st.number_input(f"Qty - {name}", min_value=0, max_value=10, step=1, key=f"qty_{name}")
                if qty > 0:
                    st.session_state.cart[name] = {
                        "quantity": qty,
                        "price": info["price"]
                    }

# ---- CART SECTION ----
st.markdown("---")
st.markdown("## 🛒 Cart")

if not st.session_state.cart:
    st.info("Cart is empty.")
else:
    total = 0
    for item, details in st.session_state.cart.items():
        qty = details["quantity"]
        price = details["price"]
        subtotal = qty * price
        total += subtotal
        st.markdown(f"- {item} x {qty} = ₹{subtotal}")
    st.markdown(f"### 💰 Total: ₹{total}")

    if st.button("✅ Place Order"):
        orders = load_json(ORDERS_FILE, [])
        orders.append({
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Pending"
        })
        save_json(ORDERS_FILE, orders)
        st.success("✅ Order placed!")
        st.session_state.cart = {}

        # Feedback UI
        st.markdown("---")
        st.markdown("### 📝 Leave Feedback")
        feedback = st.text_area("Write your feedback")
        if st.button("📩 Submit Feedback"):
            all_feedback = load_json(FEEDBACK_FILE, [])
            all_feedback.append({
                "table": st.session_state.table_number,
                "message": feedback,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, all_feedback)
            st.success("Thanks for your feedback!")