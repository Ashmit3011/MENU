# admin.py
import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Admin Panel", layout="wide")

# ---------------- FILE PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=5000, limit=None, key="admin_auto_refresh")

# ---------------- UTILITY FUNCTIONS ----------------
def load_orders():
    try:
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

# ---------------- STYLE & TOAST ----------------
st.markdown("""
    <style>
    .toast {
        position: fixed;
        bottom: 80px;
        right: 20px;
        background-color: #28a745;
        color: #fff;
        padding: 14px;
        border-radius: 10px;
        z-index: 9999;
        animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
        0% {opacity: 0; transform: translateY(30px);}
        100% {opacity: 1; transform: translateY(0);}
    }
    [data-testid="stSidebar"], [data-testid="stToolbar"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

def toast(msg):
    st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)
    st.audio("https://www.soundjay.com/buttons/sounds/button-10.mp3", autoplay=True)

# ---------------- MAIN ----------------
st.title("🧑‍🍳 Admin Panel - Manage Orders")

orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

orders = sorted(orders, key=lambda x: x['timestamp'], reverse=True)

# ---------------- NEW ORDER DETECTION ----------------
if 'last_seen' not in st.session_state:
    st.session_state.last_seen = 0

new_orders = [o for o in orders if o['timestamp'] > st.session_state.last_seen]
if new_orders:
    toast("🔔 New Order Received!")
    st.session_state.last_seen = max(o['timestamp'] for o in new_orders)

# ---------------- DISPLAY ORDERS ----------------
status_options = ["Pending", "Preparing", "Ready", "Served"]

for order in orders:
    with st.expander(f"🧾 Order #{order['id']} - Table {order['table']} | ₹{order['total']} | {order['status']}", expanded=True):
        st.write("### Items:")
        for item in order['items'].values():
            st.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

        st.caption("🕒 Placed at: " + datetime.fromtimestamp(order['timestamp']).strftime("%I:%M %p"))

        st.write("---")
        status = st.selectbox("Update Status", status_options, index=status_options.index(order['status']), key=order['id'])
        if status != order['status']:
            order['status'] = status
            save_orders(orders)
            toast(f"✅ Order {order['id']} marked as {status}")
