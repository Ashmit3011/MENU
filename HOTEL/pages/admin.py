import streamlit as st
import json
import os
from datetime import datetime

# Paths
ORDERS_FILE = "orders.json"
MENU_FILE = "menu.json"

st.set_page_config(page_title="Admin Panel", layout="centered")
st.markdown("## 🛠️ Admin Panel - Order Management")
st.markdown("### 📦 All Orders")

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

# Load menu
def load_menu():
    if not os.path.exists(MENU_FILE):
        return {}
    with open(MENU_FILE, "r") as f:
        return json.load(f)

orders = load_orders()
menu = load_menu()

status_options = ["Pending", "Preparing", "Ready", "Completed"]

if not orders:
    st.info("No orders yet.")

for idx, order in enumerate(orders):
    with st.container():
        with st.expander(f"🪑 Table {order.get('table', '?')} - {order.get('status', 'Unknown')}", expanded=True):
            st.markdown(f"**📅 {order.get('timestamp', 'Unknown')}**")

            if "items" in order:
                for item in order["items"]:
                    if isinstance(item, dict):
                        name = item.get("name", "Unnamed")
                        qty = item.get("quantity", 0)
                        price = item.get("price", 0)
                        st.markdown(f"🍴 **{name}** x {qty} = ₹{price * qty}")
                    else:
                        st.warning("⚠️ Invalid item data.")
            else:
                st.warning("⚠️ No items found in order.")

            # Update status button
            current_status = order.get("status", "Pending")
            new_status = st.selectbox("Update Status", status_options, index=status_options.index(current_status), key=f"status_{idx}")
            if st.button("✅ Update Status", key=f"update_{idx}"):
                orders[idx]["status"] = new_status
                save_orders(orders)
                st.success("Order status updated.")

            # Cancel button
            if st.button("❌ Cancel Order", key=f"cancel_{idx}"):
                orders.pop(idx)
                save_orders(orders)
                st.warning("Order cancelled.")
                st.experimental_rerun()
