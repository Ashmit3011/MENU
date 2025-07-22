import streamlit as st
import json
import os
from datetime import datetime
import time
import base64

st.set_page_config(page_title="Admin Panel", layout="wide")
st.markdown("<h1>🧑‍🍳 Admin Panel - Live Orders</h1>", unsafe_allow_html=True)

# Unified file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'menu_files')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
MENU_FILE = os.path.join(DATA_DIR, 'menu.json')

# Auto-refresh
st_autorefresh = st.experimental_rerun if st.button("🔁 Refresh Now") else None
st.markdown("""
    <meta http-equiv="refresh" content="10">
""", unsafe_allow_html=True)

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

orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

# Sort orders by timestamp (latest first)
orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)

# Load menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, 'r') as f:
        menu = json.load(f)
else:
    menu = []

# Status options
status_options = ["Pending", "Preparing", "Ready", "Served"]

# Display orders
updated = False
for idx, order in enumerate(orders):
    status = order.get("status", "Pending")
    order_id = order.get("id", f"ORD{idx}")
    status_color = {
        "Pending": "#f39c12",
        "Preparing": "#3498db",
        "Ready": "#2ecc71",
        "Served": "#95a5a6"
    }.get(status, "gray")

    timestamp = float(order.get("timestamp", time.time()))
    time_str = datetime.fromtimestamp(timestamp).strftime('%I:%M %p')

    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
                <div style='
                    border-left: 5px solid {status_color}; 
                    padding: 12px; 
                    margin-bottom: 10px;
                    background-color: #1e1e1e;
                    border-radius: 8px;
                    color: white;
                '>
                    <strong>🧾 Order ID:</strong> {order_id}<br>
                    <strong>🪑 Table:</strong> {order.get('table', 'N/A')}<br>
                    <strong>⏰ Time:</strong> {time_str}<br>
                    <strong>Status:</strong> <span style='color:{status_color}; font-weight:bold'>{status}</span><br>
                    <strong>Items:</strong>
            """, unsafe_allow_html=True)

            items = order.get("items", {})
            if isinstance(items, dict):
                for item in items.values():
                    st.markdown(
                        f"<span style='color:white'>• {item['name']} × {item['qty']} = ₹{item['qty'] * item['price']}</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.warning("⚠️ Items data is invalid.")

        with col2:
            new_status = st.selectbox("Update Status", status_options, index=status_options.index(status), key=order_id)
            if new_status != status:
                orders[idx]["status"] = new_status
                updated = True

            if st.button("🗑️ Delete", key=f"del_{order_id}"):
                if st.confirm(f"Delete Order {order_id}?"):
                    orders.pop(idx)
                    updated = True
                    st.rerun()

# Save updated orders
if updated:
    save_orders(orders)
    st.success("✅ Status updated.")
    time.sleep(1)
    st.rerun()

# Optional sound (HTML5 notification)
st.markdown("""
<audio autoplay>
  <source src="https://notificationsounds.com/storage/sounds/file-sounds-1155-pristine.mp3" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)