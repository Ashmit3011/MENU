import streamlit as st
import json
import os
from datetime import datetime

# Set base directory and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Streamlit setup
st.set_page_config(page_title="Admin - Kitchen View", layout="wide")
st.title("👨‍🍳 Kitchen Admin Panel")

st.markdown("Real-time order tracking. Refreshes every 5 seconds.")
st.markdown("---")

orders = load_orders()

status_colors = {
    "Pending": "orange",
    "Preparing": "blue",
    "Ready": "green",
    "Served": "gray"
}

# Show orders in reverse (latest first)
for idx, order in enumerate(orders[::-1]):
    container = st.container()
    with container:
        st.markdown(f"### 🧾 Table {order['table']} • `{order['status']}`")
        st.markdown(f"_Time: {order['time']}_")
        for item in order["items"]:
            st.markdown(f"- {item['name']} x {item['qty']}")
        st.markdown(f"💰 **Total: ₹{order['total']}**")

        current_status = order["status"]
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Preparing", key=f"prep_{idx}"):
                orders[-(idx+1)]["status"] = "Preparing"
                save_orders(orders)
                st.experimental_rerun()
        with col2:
            if st.button("Ready", key=f"ready_{idx}"):
                orders[-(idx+1)]["status"] = "Ready"
                save_orders(orders)
                st.experimental_rerun()
        with col3:
            if st.button("Served", key=f"served_{idx}"):
                orders[-(idx+1)]["status"] = "Served"
                save_orders(orders)
                st.experimental_rerun()

        st.markdown(f"<hr style='border:1px solid {status_colors[current_status]}'/>", unsafe_allow_html=True)

# Auto-refresh
st.markdown("<script>setTimeout(() => location.reload(), 5000);</script>", unsafe_allow_html=True)
