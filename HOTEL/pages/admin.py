import streamlit as st
import json
import os
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="Admin Panel", layout="wide")
st.markdown("<h1>🧑‍🍳 Admin Panel - Live Orders</h1>", unsafe_allow_html=True)

ORDERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'orders.json')

# --- FUNCTIONS ---
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

def delete_completed_orders():
    orders = load_orders()
    filtered = [order for order in orders if order.get("status") != "Served"]
    save_orders(filtered)
    return len(orders) - len(filtered)

# --- DELETE BUTTON ---
if st.button("🗑️ Delete Completed Orders"):
    deleted_count = delete_completed_orders()
    st.success(f"✅ Deleted {deleted_count} completed order(s).")
    st.rerun()

# --- LOAD & DISPLAY ORDERS ---
orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

# Sort by time
orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)

# Display each order
for order in orders:
    status = order.get("status", "Unknown")
    status_color = {
        "Pending": "#f1c40f",
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