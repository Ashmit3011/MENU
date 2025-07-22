import streamlit as st
import json
import os
import time
from datetime import datetime
import uuid

# File paths
BASE_DIR = os.path.dirname(__file__)
MENU_FILE = os.path.join(BASE_DIR, 'menu.json')
ORDERS_FILE = os.path.join(BASE_DIR, '..', 'orders.json')  # Save orders in parent dir

# Page setup
st.set_page_config(page_title="Smart Table Menu", layout="wide")
st.title("🍽️ Smart Table Ordering")

# Load menu
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                st.error("⚠️ Menu file is corrupted.")
                return []
    else:
        st.warning("⚠️ Menu not found.")
        return []

menu = load_menu()

if not menu:
    st.stop()

# Group by category
grouped_menu = {}
for item in menu:
    cat = item.get("category", "Others")
    grouped_menu.setdefault(cat, []).append(item)

# Select table number
table = st.selectbox("🪑 Select Your Table Number", [f"Table {i}" for i in range(1, 11)])

# Add to cart state
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Show menu
st.markdown("### 🧾 Menu")
for category, items in grouped_menu.items():
    with st.expander(f"🍱 {category}"):
        for item in items:
            item_key = item["id"]
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.write(f"**{item['name']}**")
                st.caption(f"₹{item['price']} | {'🌶️ Spicy' if item['spicy'] else '🟢 Mild'} | {'Veg' if item['veg'] else 'Non-Veg'}")
            with col2:
                qty = st.number_input(f"Qty", min_value=0, max_value=20, value=0, key=f"{item_key}_qty")
            with col3:
                if st.button("➕ Add", key=f"{item_key}_btn"):
                    if qty > 0:
                        st.session_state.cart[item_key] = {
                            "id": item_key,
                            "name": item["name"],
                            "price": item["price"],
                            "qty": qty
                        }
                        st.success(f"{item['name']} added to cart!")

# Cart display
st.markdown("### 🛒 Your Cart")
if not st.session_state.cart:
    st.info("Cart is empty.")
else:
    total = 0
    for item in st.session_state.cart.values():
        subtotal = item['qty'] * item['price']
        total += subtotal
        st.write(f"- **{item['name']}** x {item['qty']} = ₹{subtotal}")
    st.write(f"### 💵 Total: ₹{total}")

    if st.button("✅ Place Order"):
        order = {
            "id": str(uuid.uuid4())[:8],
            "table": table,
            "timestamp": time.time(),
            "status": "Preparing",
            "items": st.session_state.cart
        }

        # Save order to orders.json
        orders = []
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, 'r') as f:
                try:
                    orders = json.load(f)
                except:
                    orders = []

        orders.append(order)
        with open(ORDERS_FILE, 'w') as f:
            json.dump(orders, f, indent=2)

        st.success("🛎️ Order placed successfully!")
        st.balloons()
        st.session_state.cart = {}  # Clear cart
        st.rerun()