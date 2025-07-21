# admin.py

import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime

# === File Paths ===
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# === Page Config ===
st.set_page_config(page_title="🛎️ Admin", layout="centered")

# === Styles ===
st.markdown("""
<style>
.order-box {
    background: #1e1e1e;
    border: 1px solid #444;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.status-Pending { color: orange; font-weight: bold; }
.status-Preparing { color: deepskyblue; font-weight: bold; }
.status-Ready { color: yellowgreen; font-weight: bold; }
.status-Served { color: lightgreen; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# === Load Orders ===
def load_orders():
    if not ORDERS_FILE.exists():
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === State ===
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

# === Header ===
st.title("🛎️ Admin Panel")

orders = load_orders()
orders.sort(key=lambda x: x["time"], reverse=True)

if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New order received!", icon="🍽️")
    st.audio("https://www.soundjay.com/buttons/beep-07.wav", autoplay=True)
    st.session_state.last_order_count = len(orders)

if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        st.markdown(f"""
        <div class="order-box">
            <strong>🆔 ID:</strong> {order['id']}<br>
            <strong>🪑 Table:</strong> {order['table']}<br>
            <strong>📅 Time:</strong> {order['time']}<br>
            <strong>📦 Status:</strong> <span class="status-{order['status']}">{order['status']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**🧾 Items:**")
        for item in order["items"]:
            st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['price'] * item['qty']}")

        st.markdown(f"**💰 Total: ₹{order['total']}**")

        # Status Controls
        statuses = ["Pending", "Preparing", "Ready", "Served"]
        current = order["status"]
        if current != "Served":
            next_status = statuses[statuses.index(current) + 1]
            if st.button(f"➡️ Mark as {next_status}", key=order["id"]):
                order["status"] = next_status
                save_orders(orders)
                st.experimental_rerun()
        else:
            st.success("✅ Order Served")

        st.markdown("---")

# === Feedback Viewer ===
if FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, "r") as f:
        feedbacks = json.load(f)
    if feedbacks:
        st.subheader("🗣️ Customer Feedback")
        for fb in feedbacks[::-1]:
            st.info(f"🪑 Table {fb['table']} - {fb['feedback']}")

# Auto-refresh every 10 seconds without blinking
st.markdown("""
    <meta http-equiv="refresh" content="10">
""", unsafe_allow_html=True)


