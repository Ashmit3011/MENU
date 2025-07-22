import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

ORDER_FILE = "orders.json"
MENU_FILE = "menu.json"

st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="apprefresh")

# Load menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error("Menu not found!")
    st.stop()

# Initialize order list
if os.path.exists(ORDER_FILE):
    with open(ORDER_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

st.title("🍽️ Smart Table Ordering System")
table = st.selectbox("Select Table Number", [f"Table {i}" for i in range(1, 11)])

with st.form("place_order"):
    st.subheader("📋 Menu")
    selected_items = {}
    for item in menu:
        qty = st.number_input(f"{item['name']} (₹{item['price']})", 0, 20, step=1)
        if qty > 0:
            selected_items[item['name']] = qty

    submitted = st.form_submit_button("✅ Place Order")
    if submitted and selected_items:
        new_order = {
            "table": table,
            "items": selected_items,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Placed"
        }
        orders.append(new_order)
        with open(ORDER_FILE, "w") as f:
            json.dump(orders, f, indent=2)
        st.success("✅ Order placed successfully!")

# Show current orders
st.subheader("📦 Your Orders")
has_orders = False
for idx, order in enumerate(orders):
    if order["table"] == table:
        has_orders = True
        with st.expander(f"🕒 {order['timestamp']} - Status: {order['status']}"):
            for item, qty in order["items"].items():
                st.write(f"{item} x {qty}")
            if order["status"] in ["Placed", "Preparing"]:
                if st.button("❌ Cancel Order", key=f"cancel_{idx}"):
                    orders[idx]["status"] = "Cancelled"
                    with open(ORDER_FILE, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.warning("Order cancelled.")
                    st.rerun()

if not has_orders:
    st.info("You have no active orders.")