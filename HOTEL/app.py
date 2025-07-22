import streamlit as st
import json
import os
import time
from datetime import datetime

# Auto-refresh ready
st.set_page_config(page_title="Smart Table Order", layout="wide")

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")

# Load menu
def load_menu():
    if not os.path.exists(MENU_FILE):
        return {}
    with open(MENU_FILE, "r") as f:
        return json.load(f)

# Load orders
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

# Save orders
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Session state setup
if "table_number" not in st.session_state:
    st.session_state.table_number = None
if "cart" not in st.session_state:
    st.session_state.cart = {}

st.title("🍽️ Smart Table Ordering")

# Step 1: Table Number Input
if st.session_state.table_number is None:
    table_num = st.number_input("Enter your table number:", min_value=1, step=1)
    if st.button("Confirm Table"):
        st.session_state.table_number = table_num
        st.rerun()
else:
    st.success(f"🪑 Table Number: {st.session_state.table_number}")
    if st.button("🔁 Change Table"):
        st.session_state.table_number = None
        st.session_state.cart = {}
        st.rerun()

    # Step 2: Load Menu and Build Cart
    menu = load_menu()
    cart = st.session_state.cart

    st.header("📋 Menu")
    for category, items in menu.items():
        with st.expander(f"🍱 {category}"):
            for item in items:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{item['name']}** - ₹{item['price']}")
                with col2:
                    qty = st.number_input(
                        f"Qty for {item['name']}",
                        min_value=0,
                        step=1,
                        key=item['name']
                    )
                    if qty > 0:
                        cart[item['name']] = {
                            "price": item["price"],
                            "quantity": qty
                        }

    # Step 3: Cart Preview
    st.session_state.cart = cart
    if cart:
        st.subheader("🛒 Cart")
        total = 0
        for name, item in cart.items():
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            st.write(f"{name} x {item['quantity']} = ₹{subtotal}")
        st.markdown(f"### 💰 Total: ₹{total}")

        if st.button("✅ Place Order"):
            order_id = f"{st.session_state.table_number}-{int(time.time())}"
            new_order = {
                "id": order_id,
                "table": st.session_state.table_number,
                "items": cart,
                "total": total,
                "status": "Pending",
                "timestamp": time.time()
            }
            orders = load_orders()
            orders.append(new_order)
            save_orders(orders)
            st.success(f"✅ Order `{order_id}` placed successfully!")
            st.session_state.cart = {}
            st.rerun()
    else:
        st.info("Your cart is empty. Add items from the menu.")