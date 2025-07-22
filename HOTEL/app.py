import streamlit as st
import json
import os
import time
from datetime import datetime

# Set page config
st.set_page_config(page_title="Smart Table Order", layout="wide")
st.title("🍽️ Smart Table Ordering System")

# Absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# Load menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error(f"❌ Menu file not found at {MENU_FILE}")
    st.stop()

# Load orders
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Prompt for table number
if "table_number" not in st.session_state:
    table_number = st.text_input("Enter your Table Number")
    if table_number:
        st.session_state.table_number = table_number
        st.session_state.cart = {}
        st.rerun()
else:
    st.sidebar.success(f"🪑 Table: {st.session_state.table_number}")

    if "cart" not in st.session_state:
        st.session_state.cart = {}

    if st.sidebar.button("🔄 Change Table"):
        del st.session_state["table_number"]
        if "cart" in st.session_state:
            del st.session_state["cart"]
        st.rerun()

# Show menu
st.subheader("📋 Menu")

for category, items in menu.items():
    with st.expander(category):
        for item in items:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{item['name']}** — ₹{item['price']}")
            with col2:
                if st.button("➕", key=f"{category}-{item['name']}"):
                    cart = st.session_state.get("cart", {})
                    name = item["name"]
                    price = item["price"]
                    if name not in cart:
                        cart[name] = {"price": price, "quantity": 1}
                    else:
                        cart[name]["quantity"] += 1
                    st.session_state.cart = cart
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
    st.markdown(f"### Total: ₹{total}")

    if st.button("✅ Place Order"):
        if "table_number" not in st.session_state:
            st.error("❗ Please enter your table number before placing the order.")
        else:
            order = {
                "table": st.session_state.get("table_number"),
                "items": cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders.append(order)
            with open(ORDERS_FILE, "w") as f:
                json.dump(orders, f, indent=2)
            st.success("✅ Order placed!")
            del st.session_state["cart"]
            st.rerun()
else:
    st.info("🛍️ Your cart is empty.")

# Real-time auto-refresh for status tracking
if "table_number" in st.session_state:
    st.query_params(t=int(time.time()))  # Force rerun
    time.sleep(5)  # Refresh every 5 seconds
    st.rerun()

# Show order history
st.subheader("📦 Your Orders")

if "table_number" in st.session_state:
    found = False
    for order in reversed(orders):
        if order["table"] == st.session_state["table_number"]:
            found = True
            status = order["status"]
            st.markdown(f"🕒 *{order['timestamp']}* — **Status:** `{status}`")
            for name, item in order["items"].items():
                line = f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}"
                if status == "Cancelled":
                    st.markdown(f"<s>{line}</s>", unsafe_allow_html=True)
                else:
                    st.markdown(line)
            if status not in ["Completed", "Cancelled"]:
                if st.button(f"❌ Cancel Order ({order['timestamp']})", key=f"cancel-{order['timestamp']}"):
                    order["status"] = "Cancelled"
                    with open(ORDERS_FILE, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.warning("Order cancelled.")
                    st.rerun()
            st.markdown("---")
    if not found:
        st.info("📭 No orders found.")