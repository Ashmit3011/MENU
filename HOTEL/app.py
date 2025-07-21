import streamlit as st
import json
import os
import time
from datetime import datetime

# === File Paths (compatible with older Python versions) ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Initialize Files ===
for file_path, empty_data in [(ORDERS_FILE, []), (MENU_FILE, {}), (FEEDBACK_FILE, [])]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump(empty_data, f)

# === Load Menu ===
with open(MENU_FILE, "r") as f:
    menu = json.load(f)

# === Session State ===
if "cart" not in st.session_state:
    st.session_state.cart = {}

# === Style ===
st.set_page_config(page_title="Smart POS", layout="centered")
st.markdown("""
    <style>
        .food-btn { font-size: 1.2rem; padding: 0.3rem 1rem; }
        .qty-control { font-weight: bold; font-size: 1.2rem; margin: 0 0.5rem; }
        .cart-box { background: #111; color: #fff; padding: 1rem; border-radius: 10px; margin-top: 1rem; }
        .cart-item { border-bottom: 1px solid #444; padding: 0.5rem 0; }
    </style>
""", unsafe_allow_html=True)

# === Header ===
st.title("🍽️ Smart Ordering System")
st.text("Tap + to add items. Tap - to remove. 🧺 Cart updates live.")

# === Display Menu ===
categories = list(menu.keys())
menu_items = [item for cat in menu.values() for item in cat]
st.markdown("### 🍱 Choose Your Food:")
tabs = st.tabs(categories)

for i, category in enumerate(categories):
    with tabs[i]:
        for item in menu[category]:
            col1, col2, col3 = st.columns([5, 2, 3])
            with col1:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"₹{item['price']}")
            with col2:
                if st.button("➕", key=f"add_{item['id']}"):
                    st.session_state.cart[item['id']] = st.session_state.cart.get(item['id'], 0) + 1
                    st.toast(f"Added {item['name']}", icon="🍔")
                if item['id'] in st.session_state.cart and st.session_state.cart[item['id']] > 0:
                    if st.button("➖", key=f"remove_{item['id']}"):
                        st.session_state.cart[item['id']] -= 1
                        if st.session_state.cart[item['id']] <= 0:
                            del st.session_state.cart[item['id']]

# === Cart ===
st.markdown("## 🧺 Your Cart")
total = 0
if st.session_state.cart:
    with st.container():
        for item_id, qty in st.session_state.cart.items():
            item = next((i for i in menu_items if i['id'] == item_id), None)
            if item:
                line_total = item['price'] * qty
                total += line_total
                st.markdown(f"- {item['name']} x {qty} = ₹{line_total}")
else:
    st.info("Cart is empty")

# === Checkout ===
st.markdown(f"### 💰 Total: ₹{total}")
table_no = st.text_input("Enter your table number")
if st.button("📤 Place Order") and st.session_state.cart and table_no:
    new_order = {
        "id": int(time.time()),
        "table": table_no,
        "items": [],
        "total": total,
        "status": "Pending",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    for item_id, qty in st.session_state.cart.items():
        item = next((i for i in menu_items if i['id'] == item_id), None)
        if item:
            new_order["items"].append({"name": item['name'], "price": item['price'], "qty": qty})
    with open(ORDERS_FILE, "r") as f:
        data = json.load(f)
    data.append(new_order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    st.toast("Order placed successfully!", icon="✅")
    st.success("Thank you! Your order is being processed.")
    st.session_state.cart = {}
    st.rerun()
