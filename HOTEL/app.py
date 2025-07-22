import streamlit as st
import json
import os
from datetime import datetime

# ------------------ Setup ------------------
st.set_page_config(page_title="Smart Café", layout="wide")
BASE_DIR = os.getcwd()
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# ------------------ JSON Helpers ------------------
def load_json(path, fallback=[]):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {path}: {e}")
        return fallback

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ------------------ Customer Panel ------------------
def customer_panel():
    st.title("🍽️ Welcome to Smart Café")

    menu = load_json(MENU_FILE)
    if not menu:
        st.error("Menu is empty or failed to load.")
        return

    cart = []
    category_filter = st.selectbox("Select Category", sorted(set(item['category'] for item in menu)))

    for item in menu:
        if item['category'] != category_filter:
            continue
        with st.container():
            cols = st.columns([4, 1, 1])
            cols[0].markdown(f"**{item['name']}**")
            cols[1].markdown(f"${item['price']:.2f}")
            if cols[2].button("Add", key=item['id']):
                cart.append(item)
                st.toast(f"Added {item['name']} to cart", icon="🛒")

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    st.session_state.cart += cart

    if st.session_state.cart:
        st.subheader("🛒 Cart")
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.markdown(f"- {item['name']} (${item['price']:.2f})")
        st.markdown(f"**Total: ${total:.2f}**")

        table = st.text_input("Table Number")
        if st.button("Place Order") and table:
            orders = load_json(ORDERS_FILE)
            order = {
                "order_id": str(len(orders) + 1),
                "table": table,
                "items": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().isoformat()
            }
            orders.append(order)
            save_json(ORDERS_FILE, orders)
            st.success("✅ Order Placed!")
            st.session_state.cart = []

    st.markdown("---")
    st.subheader("💬 Leave Feedback")
    order_id = st.text_input("Order ID")
    rating = st.slider("Rating", 1, 5, 3)
    comment = st.text_area("Comment")
    if st.button("Submit Feedback"):
        feedback = load_json(FEEDBACK_FILE)
        feedback.append({
            "order_id": order_id,
            "table": table if 'table' in locals() else "N/A",
            "rating": rating,
            "comment": comment
        })
        save_json(FEEDBACK_FILE, feedback)
        st.success("✅ Feedback submitted")

# ------------------ Run ------------------
customer_panel()
