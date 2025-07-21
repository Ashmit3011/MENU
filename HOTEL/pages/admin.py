import streamlit as st
import json
import os
from datetime import datetime
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"

st.set_page_config(page_title="Admin Panel", layout="centered")
st.markdown("""
    <style>
    body { background-color: #111; color: #fff; }
    .stButton>button { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

def load_orders():
    if not ORDERS_FILE.exists(): return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_status_color(status):
    return {
        "Pending": "orange",
        "Preparing": "gold",
        "Ready": "deepskyblue",
        "Served": "limegreen"
    }.get(status, "gray")

st.title("🛠️ Admin Dashboard")
orders = load_orders()

if not orders:
    st.info("No orders found.")
else:
    for order in sorted(orders, key=lambda x: x['timestamp'], reverse=True):
        with st.container():
            st.markdown("---")
            st.markdown(f"### 🧾 Order ID: `{order['id']}` | Table: **{order['table']}**")
            status_color = get_status_color(order['status'])
            st.markdown(f"**Status:** <span style='color:{status_color}; font-weight:bold'>{order['status']}</span>", unsafe_allow_html=True)

            with st.expander("View Items"):
                for pid, qty in order['items'].items():
                    st.write(f"🔸 Product ID: {pid}, Qty: {qty}")

            new_status = st.selectbox("Update Status", ["Pending", "Preparing", "Ready", "Served"], index=["Pending", "Preparing", "Ready", "Served"].index(order['status']), key=order['id'])
            if st.button("Update", key=f"update_{order['id']}"):
                order['status'] = new_status
                save_orders(orders)
                st.success("Status updated successfully!")
                st.rerun()

# Auto Refresh Every 5 seconds
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)
