import streamlit as st
import json
import os
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh

# --- Streamlit page setup ---
st.set_page_config(page_title="Admin Panel", layout="wide")
st.markdown("<h1>🧑‍🍳 Admin Panel - Live Orders</h1>", unsafe_allow_html=True)

# --- Auto-refresh every 5 seconds ---
st_autorefresh(interval=5000, key="datarefresh")

# --- File paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'menu_files')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
MENU_FILE = os.path.join(DATA_DIR, 'menu.json')

# --- Load orders ---
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# --- Save orders ---
def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

# --- Load menu (optional, in case needed) ---
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, 'r') as f:
        menu = json.load(f)
else:
    menu = []

# --- Sort by time ---
orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)

# --- Status colors ---
status_colors = {
    "Pending": "#f39c12",
    "Preparing": "#3498db",
    "Ready": "#2ecc71",
    "Served": "#95a5a6"
}
status_options = list(status_colors.keys())

# --- Track if update is needed ---
updated = False

# --- Loop through orders ---
for idx, order in enumerate(orders):
    order_id = order.get("id", f"ORD{idx}")
    table = order.get("table", "N/A")
    status = order.get("status", "Pending")
    color = status_colors.get(status, "gray")

    timestamp = float(order.get("timestamp", time.time()))
    time_str = datetime.fromtimestamp(timestamp).strftime('%I:%M %p')

    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
                <div style='
                    border-left: 6px solid {color}; 
                    padding: 16px; 
                    margin-bottom: 12px;
                    background-color: #1e1e1e;
                    border-radius: 10px;
                    color: white;
                '>
                    <strong>🧾 Order ID:</strong> {order_id}<br>
                    <strong>🪑 Table:</strong> {table}<br>
                    <strong>⏰ Time:</strong> {time_str}<br>
                    <strong>Status:</strong> <span style='color:{color}'><b>{status}</b></span><br>
                    <strong>Items:</strong><br>
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
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            new_status = st.selectbox("Update Status", status_options, index=status_options.index(status), key=order_id)
            if new_status != status:
                orders[idx]["status"] = new_status
                updated = True

            if st.button("🗑️ Delete", key=f"del_{order_id}"):
                orders.pop(idx)
                updated = True
                st.rerun()

# --- Save and refresh if updated ---
if updated:
    save_orders(orders)
    st.success("✅ Order updated.")