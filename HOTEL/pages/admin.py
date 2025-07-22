import streamlit as st
import json
import os
from datetime import datetime
import time

# Page setup
st.set_page_config(page_title="Admin Panel", layout="wide")
st.markdown("<h1>🧑‍🍳 Admin Panel - Live Orders</h1>", unsafe_allow_html=True)

ORDERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'orders.json')

# --- Helper functions ---
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

def update_status(order_id, new_status):
    orders = load_orders()
    for order in orders:
        if order.get("id") == order_id:
            order["status"] = new_status
            break
    save_orders(orders)
    st.experimental_rerun()

def delete_completed_orders():
    orders = load_orders()
    filtered = [order for order in orders if order.get("status") != "Served"]
    save_orders(filtered)
    st.success("✅ Deleted completed orders.")
    st.rerun()

# --- Load and Display Orders ---
orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

# Sort by latest timestamp
orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)

# Delete button
if st.button("🗑️ Delete Completed Orders"):
    delete_completed_orders()

# Display each order
for order in orders:
    status = order.get("status", "Unknown")
    status_color = {
        "Preparing": "#3498db",
        "Ready": "#f39c12",
        "Served": "#2ecc71"
    }.get(status, "gray")

    try:
        timestamp = float(order.get("timestamp", time.time()))
        time_str = datetime.fromtimestamp(timestamp).strftime('%I:%M %p')
    except:
        time_str = "N/A"

    with st.container():
        st.markdown(f"""
            <div style='
                border: 2px solid {status_color}; 
                border-radius: 12px; 
                padding: 16px; 
                margin-bottom: 8px; 
                background-color: #1e1e1e;
                color: white;
            '>
            <strong>🧾 Order ID:</strong> {order.get('id')}<br>
            <strong>🪑 Table:</strong> {order.get('table')}<br>
            <strong>⏰ Time:</strong> {time_str}<br>
            <strong>Status:</strong> <span style='color:{status_color}; font-weight:bold'>{status}</span><br>
            <strong>Items:</strong>
            </div>
        """, unsafe_allow_html=True)

        items = order.get("items", {})
        if isinstance(items, dict):
            for item in items.values():
                st.markdown(
                    f"<span style='color:white'>- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}</span>",
                    unsafe_allow_html=True
                )
        else:
            st.warning("⚠️ Items data is invalid or missing.")

        # Buttons to change status
        col1, col2, col3 = st.columns(3)
        with col1:
            if status != "Preparing" and st.button(f"Set Preparing 🧑‍🍳", key=f"prep_{order['id']}"):
                update_status(order["id"], "Preparing")
        with col2:
            if status != "Ready" and st.button(f"Set Ready ✅", key=f"ready_{order['id']}"):
                update_status(order["id"], "Ready")
        with col3:
            if status != "Served" and st.button(f"Set Served 🍽️", key=f"serve_{order['id']}"):
                update_status(order["id"], "Served")

        st.markdown("---")