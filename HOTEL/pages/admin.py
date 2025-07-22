import streamlit as st
import json
import os
from datetime import datetime
import time

# File path
ORDERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'orders.json')

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🧑‍🍳 Admin Panel - Live Orders")

# Load orders
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# Save orders
def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

# Handle delete served orders
def delete_served_orders():
    orders = load_orders()
    orders = [o for o in orders if o.get("status") != "Served"]
    save_orders(orders)

# Update status for a specific order ID
def update_order_status(order_id, new_status):
    orders = load_orders()
    for order in orders:
        if order.get("id") == order_id:
            order["status"] = new_status
            break
    save_orders(orders)
    st.experimental_rerun()

# Admin UI
orders = load_orders()
if not orders:
    st.info("No orders yet.")
    st.stop()

# Sort orders by time
orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)

# Delete button
if st.button("🗑️ Delete All Served Orders"):
    delete_served_orders()
    st.success("Deleted all served orders.")
    st.experimental_rerun()

# Show orders
for order in orders:
    order_id = order.get("id", "N/A")
    table = order.get("table", "N/A")
    timestamp = datetime.fromtimestamp(order.get("timestamp", time.time())).strftime('%I:%M %p')
    status = order.get("status", "Preparing")
    items = order.get("items", {})

    status_color = {
        "Preparing": "#3498db",
        "Ready": "#f39c12",
        "Served": "#2ecc71"
    }.get(status, "gray")

    st.markdown(f"""
        <div style='
            border: 2px solid {status_color}; 
            border-radius: 12px; 
            padding: 16px; 
            margin-bottom: 16px; 
            background-color: #1e1e1e;
            color: white;
        '>
            <strong>🧾 Order ID:</strong> {order_id}<br>
            <strong>🪑 Table:</strong> {table}<br>
            <strong>⏰ Time:</strong> {timestamp}<br>
            <strong>Status:</strong> <span style='color:{status_color}; font-weight:bold'>{status}</span><br>
            <strong>Items:</strong><br>
    """, unsafe_allow_html=True)

    for item in items.values():
        st.markdown(
            f"<span style='color:white'>- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}</span>",
            unsafe_allow_html=True
        )

    # Status buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛠 Preparing", key=f"prep_{order_id}"):
            update_order_status(order_id, "Preparing")
    with col2:
        if st.button("✅ Ready", key=f"ready_{order_id}"):
            update_order_status(order_id, "Ready")
    with col3:
        if st.button("🍽️ Served", key=f"served_{order_id}"):
            update_order_status(order_id, "Served")

    st.markdown("</div>", unsafe_allow_html=True)