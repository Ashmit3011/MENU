import streamlit as st
import json
import os
from datetime import datetime
import time

# Page setup
st.set_page_config(page_title="Admin Panel", layout="wide")
st.markdown("<h1>🧑‍🍳 Admin Panel - Live Orders</h1>", unsafe_allow_html=True)

ORDERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'orders.json')

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

# Sort orders by timestamp (latest first)
try:
    orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)
except:
    st.error("Some orders are missing timestamps.")

# Display orders
for order in orders:
    status = order.get("status", "Unknown")
    status_color = {
        "Preparing": "#3498db",
        "Ready": "#2ecc71",
        "Served": "#95a5a6"
    }.get(status, "gray")

    try:
        timestamp = float(order.get("timestamp", time.time()))
        time_str = datetime.fromtimestamp(timestamp).strftime('%I:%M %p')
    except:
        time_str = "N/A"

    st.markdown(f"""
        <div style='
            border: 2px solid {status_color}; 
            border-radius: 12px; 
            padding: 16px; 
            margin-bottom: 16px; 
            background-color: #1e1e1e;
            color: white;
        '>
            <strong>🧾 Order ID:</strong> {order.get('id', 'N/A')}<br>
            <strong>🪑 Table:</strong> {order.get('table', 'N/A')}<br>
            <strong>⏰ Time:</strong> {time_str}<br>
            <strong>Status:</strong> <span style='color:{status_color}; font-weight:bold'>{status}</span><br>
            <strong>Items:</strong><br>
    """, unsafe_allow_html=True)

    items = order.get("items", {})
    if isinstance(items, dict):
        for item in items.values():
            try:
                st.markdown(
                    f"<span style='color:white'>- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}</span>",
                    unsafe_allow_html=True
                )
            except:
                st.markdown("<span style='color:orange'>- ❌ Invalid item format</span>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Items data is invalid or missing.")

    st.markdown("</div>", unsafe_allow_html=True)
