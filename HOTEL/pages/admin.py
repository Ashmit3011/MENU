import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

ORDER_FILE = "orders.json"

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠️ Admin Panel - Manage Orders")

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="adminrefresh")

# Load orders
if os.path.exists(ORDER_FILE):
    with open(ORDER_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

statuses = ["Placed", "Preparing", "Ready", "Served", "Cancelled"]

for idx, order in enumerate(orders):
    with st.expander(f"{order['table']} - {order['timestamp']}"):
        for item, qty in order["items"].items():
            st.write(f"{item} x {qty}")
        current_status = order.get("status", "Placed")
        new_status = st.selectbox("Update Status", statuses, index=statuses.index(current_status), key=f"status_{idx}")
        if new_status != current_status:
            orders[idx]["status"] = new_status
            with open(ORDER_FILE, "w") as f:
                json.dump(orders, f, indent=2)
            st.success(f"✅ Status updated to {new_status}")