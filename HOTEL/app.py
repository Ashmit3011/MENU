import streamlit as st
import json
import os
from datetime import datetime

# Page settings
st.set_page_config(page_title="Smart Table Order", layout="wide")
st.title("🍽️ Smart Table Ordering System")

# Full paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "data", "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "data", "orders.json")

# Load menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error("❌ Menu file not found.")
    st.stop()

# Load orders
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Table selection
if "table_number" not in st.session_state:
    table_number = st.text_input("Enter your Table Number")
    if table_number:
        st.session_state.table_number = table_number
        st.rerun()
else:
    st.sidebar.success(f"🪑 Table: {st.session_state.table_number}")
    if st.sidebar.button("🔄 Change Table"):
        del st.session_state.table_number
        if "cart" in st.session_state:
            del st.session_state.cart
        st.rerun()

# Cart init
if "cart" not in st.session_state:
    st.session_state.cart = {}

# Menu display
st.subheader("📋 Menu")

for category, items in menu.items():
    with st.expander(category):
        for item in items:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{item['name']}** - ₹{item['price']}")
            with col2:
                if st.button("➕", key=f"{category}-{item['name']}"):
                    name = item["name"]
                    price = item["price"]
                    if name not in st.session_state.cart:
                        st.session_state.cart[name] = {"price": price, "quantity": 1}
                    else:
                        st.session_state.cart[name]["quantity"] += 1
                    st.rerun()

# Cart display
st.subheader("🛒 Cart")

if st.session_state.cart:
    total = 0
    for name, item in st.session_state.cart.items():
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        st.markdown(f"{name} x {item['quantity']} = ₹{subtotal}")
    st.markdown(f"### Total: ₹{total}")

    # Order submission
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
        st.success("✅ Order Placed!")
        del st.session_state.cart
        st.rerun()
else:
    st.info("🛍️ Your cart is empty.")

# View Order History for this table
st.subheader("📦 Your Orders")
if st.session_state.table_number:
    found = False
    for order in orders[::-1]:
        if order["table"] == st.session_state.table_number:
            found = True
            status = order["status"]
            st.markdown(f"🕒 *{order['timestamp']}* — **Status:** `{status}`")
            for name, item in order["items"].items():
                item_line = f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}"
                if status == "Cancelled":
                    st.markdown(f"<s>{item_line}</s>", unsafe_allow_html=True)
                else:
                    st.markdown(f"{item_line}")
            if status not in ["Completed", "Cancelled"]:
                if st.button(f"❌ Cancel Order ({order['timestamp']})", key=order["timestamp"]):
                    order["status"] = "Cancelled"
                    with open(ORDERS_FILE, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.warning("Order cancelled.")
                    st.rerun()
            st.markdown("---")
    if not found:
        st.info("📭 No orders found.")