import streamlit as st
import json
import os
import time
from datetime import datetime

# === File paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# === Helper functions ===
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === UI config ===
st.set_page_config(page_title="📋 Admin Dashboard", layout="wide")
st.markdown("""
    <style>
        .order-card {
            background-color: #1a1a1a;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid #333;
        }
        .status-selectbox {
            background-color: #111;
            color: white;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Live Orders Admin Panel")
orders = load_orders()
updated = False

if not orders:
    st.info("No orders yet.")
else:
    for i, order in enumerate(reversed(orders)):
        with st.container():
            st.markdown("<div class='order-card'>", unsafe_allow_html=True)
            st.subheader(f"🧾 Order ID: {order['id']} | Table: {order['table']}")
            st.markdown(f"**Placed:** {order['time']}")
            st.markdown("### Items:")
            for item in order['items']:
                st.markdown(f"- {item['name']} x {item['qty']} — ₹{item['qty'] * item['price']}")
            st.markdown(f"**Total:** ₹{order['total']}")

            status_options = ["Pending", "Preparing", "Ready", "Served"]
            current_status = order.get("status", "Pending")
            new_status = st.selectbox("Update Status", status_options, index=status_options.index(current_status), key=f"status_{i}")

            if new_status != current_status:
                orders[len(orders)-1 - i]['status'] = new_status
                updated = True
                st.success(f"Status updated to {new_status}")

            st.markdown("</div>", unsafe_allow_html=True)

    if updated:
        save_orders(orders)

# === Real-time refresh ===
time.sleep(5)
st.rerun()
