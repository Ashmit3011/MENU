import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 🔄 Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="admin_autorefresh")

# File paths (adjusted for Streamlit pages folder)
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "..", "orders.json")
MENU_FILE = os.path.join(os.path.dirname(__file__), "..", "menu.json")

st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Admin Panel - Order Management")

# Load data
def load_json(file_path, default):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception:
        return default

# Save data
def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# Load menu and orders
menu = load_json(MENU_FILE, {})
orders = load_json(ORDERS_FILE, [])

# Status flow
status_flow = ["Pending", "Preparing", "Ready", "Completed"]

# Handle empty state
if not orders:
    st.info("📭 No orders yet.")

# Iterate and display orders
for idx, order in reversed(list(enumerate(orders))):
    with st.container():
        with st.expander(f"🪑 Table {order.get('table', '?')} - {order.get('status', 'Unknown')} - ⏰ {order.get('timestamp', 'Unknown')}", expanded=True):
            # Items
            if "items" in order:
                for item in order["items"]:
                    if isinstance(item, dict):
                        name = item.get("name", "Unnamed")
                        qty = item.get("quantity", 0)
                        price = item.get("price", 0)
                        st.markdown(f"🍽️ **{name}** x {qty} = ₹{price * qty}")

            st.markdown("---")

            # Status update dropdown
            current_status = order.get("status", "Pending")
            next_status_options = [s for s in status_flow if s != current_status]
            new_status = st.selectbox("Change Status", [current_status] + next_status_options, key=f"status_{idx}")
            
            if new_status != current_status:
                if st.button("✅ Update Status", key=f"update_{idx}"):
                    orders[idx]["status"] = new_status
                    save_json(ORDERS_FILE, orders)
                    st.success(f"✅ Status updated to {new_status}")
                    st.experimental_rerun()

            # Cancel/delete
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Cancel Order", key=f"cancel_{idx}"):
                    orders[idx]["status"] = "Cancelled"
                    save_json(ORDERS_FILE, orders)
                    st.warning("Order cancelled.")
                    st.experimental_rerun()
            with col2:
                if order.get("status") == "Completed" and st.button("🗑️ Delete", key=f"delete_{idx}"):
                    orders.pop(idx)
                    save_json(ORDERS_FILE, orders)
                    st.success("🗑️ Order deleted.")
                    st.experimental_rerun()
