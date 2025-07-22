import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Config
st.set_page_config(page_title="Smart Table Order", layout="wide")

# Paths
CURRENT_FILE = os.path.abspath(__file__)
PAGES_DIR = os.path.dirname(CURRENT_FILE)
ROOT_DIR = os.path.dirname(PAGES_DIR)
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")

# Debug file paths
st.markdown(f"**📄 Current File:** `{CURRENT_FILE}`")
st.markdown(f"**📁 Root Dir:** `{ROOT_DIR}`")
st.markdown(f"**📋 Menu Path:** `{MENU_FILE}`")
st.markdown(f"**📦 Orders Path:** `{ORDERS_FILE}`")

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

# Detect if admin mode
is_admin = st.query_params.get("page") == "admin"

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="autorefresh")

if is_admin:
    st.title("🛠️ Admin Panel")
    st.subheader("📦 All Orders")
    changed = False
    for idx, order in reversed(list(enumerate(orders))):
        st.markdown(f"### Table {order['table']} — {order['status']} — 🕒 {order['timestamp']}")
        for name, item in order["items"].items():
            st.markdown(f"- {name} x {item['quantity']} = ₹{item['price'] * item['quantity']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            if order["status"] == "Pending" and st.button("👨‍🍳 Mark Preparing", key=f"prep-{idx}"):
                orders[idx]["status"] = "Preparing"
                changed = True
        with col2:
            if order["status"] == "Preparing" and st.button("✅ Complete", key=f"comp-{idx}"):
                orders[idx]["status"] = "Completed"
                changed = True
        with col3:
            if order["status"] not in ["Completed", "Cancelled"] and st.button("❌ Cancel", key=f"cancel-{idx}"):
                orders[idx]["status"] = "Cancelled"
                changed = True
        st.markdown("---")

    if changed:
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)
        st.experimental_rerun()

else:
    st.title("🍽️ Smart Table Ordering System")

    # Ensure cart is initialized if table_number exists
    if "table_number" in st.session_state and "cart" not in st.session_state:
        st.session_state.cart = {}

    # Table input
    if "table_number" not in st.session_state:
        table_number = st.text_input("Enter your Table Number")
        if table_number:
            st.session_state.table_number = table_number
            st.session_state.cart = {}
            st.rerun()
    else:
        st.sidebar.success(f"🪑 Table: {st.session_state.table_number}")
        if st.sidebar.button("🔄 Change Table"):
            del st.session_state.table_number
            if "cart" in st.session_state:
                del st.session_state.cart
            st.rerun()

    # Show menu
    st.subheader("📋 Menu")
    if "cart" in st.session_state:
        for category, items in menu.items():
            with st.expander(category):
                for item in items:
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        st.markdown(f"**{item['name']}** — ₹{item['price']}")
                    with col2:
                        if st.button("➕", key=f"{category}-{item['name']}"):
                            name = item["name"]
                            price = item["price"]
                            if name not in st.session_state.cart:
                                st.session_state.cart[name] = {"price": price, "quantity": 1}
                            else:
                                st.session_state.cart[name]["quantity"] += 1
                            st.rerun()

    # Cart
    st.subheader("🛒 Cart")
    if st.session_state.get("cart"):
        total = 0
        for name, item in st.session_state.cart.items():
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            st.markdown(f"{name} x {item['quantity']} = ₹{subtotal}")
        st.markdown(f"### Total: ₹{total}")

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
            st.session_state.cart = {}
            st.rerun()
    else:
        st.info("🛍️ Your cart is empty.")

    # Order history
    st.subheader("📦 Your Orders")
    if "table_number" in st.session_state:
        found = False
        for order in reversed(orders):
            if order["table"] == st.session_state.table_number:
                found = True
                status = order["status"]
                st.markdown(f"🕒 *{order['timestamp']}* — **Status:** `{status}`")
                for name, item in order["items"].items():
                    line = f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}"
                    if status == "Cancelled":
                        st.markdown(f"<s>{line}</s>", unsafe_allow_html=True)
                    else:
                        st.markdown(line)
                st.markdown("---")
        if not found:
            st.info("📭 No orders found.")
