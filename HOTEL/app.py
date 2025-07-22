import streamlit as st
import json
import os
import time
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.title("🍽️ Smart Table Ordering System")

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# Load menu.json
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error(f"❌ Menu file not found: {MENU_FILE}")
    st.stop()

# Load orders.json
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Setup session state
if "table_number" not in st.session_state:
    table_number = st.text_input("Enter your Table Number:")
    if table_number:
        st.session_state.table_number = table_number
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.success(f"🪑 Table: {st.session_state.table_number}")

# Ensure cart exists
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Option to change table
if st.sidebar.button("🔄 Change Table"):
    del st.session_state["table_number"]
    del st.session_state["cart"]
    st.rerun()

# Show menu with categories
st.subheader("📋 Menu")
for category, items in menu.items():
    with st.expander(f"🍱 {category}"):
        for item in items:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{item['name']}** - ₹{item['price']}")
            with col2:
                if st.button("➕", key=f"{category}_{item['name']}"):
                    name = item["name"]
                    price = item["price"]
                    if name in st.session_state.cart:
                        st.session_state.cart[name]["quantity"] += 1
                    else:
                        st.session_state.cart[name] = {"price": price, "quantity": 1}
                    st.rerun()

# Show cart
st.subheader("🛒 Cart")
cart = st.session_state.get("cart", {})
if cart:
    total = 0
    for name, item in cart.items():
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        st.markdown(f"{name} x {item['quantity']} = ₹{subtotal}")
    st.markdown(f"### 💰 Total: ₹{total}")

    if st.button("✅ Place Order"):
        order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(order)
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)
        st.success("✅ Order placed!")
        st.session_state.cart = {}
        st.rerun()
else:
    st.info("🛒 Your cart is empty.")

# Show past orders for this table
st.subheader("📦 Your Orders")
has_orders = False
for order in reversed(orders):
    if order["table"] == st.session_state.table_number:
        has_orders = True
        st.markdown(f"🕒 `{order['timestamp']}` — **Status:** `{order['status']}`")
        for name, item in order["items"].items():
            line = f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}"
            if order["status"] == "Cancelled":
                st.markdown(f"<s>{line}</s>", unsafe_allow_html=True)
            else:
                st.markdown(line)

        if order["status"] not in ["Completed", "Cancelled"]:
            if st.button(f"❌ Cancel Order ({order['timestamp']})", key=f"cancel_{order['timestamp']}"):
                order["status"] = "Cancelled"
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.warning("Order cancelled.")
                st.rerun()
        st.markdown("---")

if not has_orders:
    st.info("📭 No orders yet.")

# Auto-refresh every 5 seconds
st.query_params(t=int(time.time()))
time.sleep(5)
st.rerun()