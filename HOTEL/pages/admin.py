import streamlit as st
import json
import os
import time
from datetime import datetime
from pathlib import Path

# === File Paths ===
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

st.set_page_config(page_title="🛎️ Admin Panel", layout="wide")

# === UI Style ===
st.markdown("""
    <style>
        .order-box {
            background: #111111dd;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .status-pending { color: orange; font-weight: bold; }
        .status-preparing { color: deepskyblue; font-weight: bold; }
        .status-ready { color: yellowgreen; font-weight: bold; }
        .status-served { color: lightgreen; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# === Load Orders ===
def load_json(file, default):
    if not file.exists():
        with open(file, "w") as f: json.dump(default, f)
        return default
    with open(file, "r") as f: return json.load(f)

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=2)

orders = load_json(ORDERS_FILE, [])
orders.sort(key=lambda x: x["time"], reverse=True)

# === Sound on New Order ===
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New Order Received!", icon="🍽️")
    st.audio("https://www.soundjay.com/buttons/beep-07.wav", autoplay=True)
    st.session_state.last_order_count = len(orders)

# === Show Orders ===
st.title("📋 Orders")
if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        status_class = f"status-{order['status'].lower()}"
        with st.expander(f"🆔 Order {order['id']} — ₹{order['total']} — {order['status']}"):
            st.markdown(f"**Table:** {order['table']}  \n**Time:** {order['time']}")
            st.markdown(f"**Status:** <span class='{status_class}'>{order['status']}</span>", unsafe_allow_html=True)

            st.markdown("#### Items")
            for item in order["items"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

            # === Status Controls ===
            statuses = ["Pending", "Preparing", "Ready", "Served"]
            current_idx = statuses.index(order["status"])
            if current_idx < 3:
                if st.button(f"➡️ Mark as {statuses[current_idx + 1]}", key=f"{order['id']}_next"):
                    order["status"] = statuses[current_idx + 1]
                    save_json(ORDERS_FILE, orders)
                    st.rerun()
            else:
                st.success("✅ Order Served")

# === Feedback Viewer ===
st.markdown("## 💬 Customer Feedback")
feedbacks = load_json(FEEDBACK_FILE, [])
if not feedbacks:
    st.info("No feedback received.")
else:
    for fb in reversed(feedbacks):
        st.markdown(f"🧾 **Order ID**: {fb['order_id']}  \n🕒 {fb['time']}  \n💬 {fb['feedback']}")
        st.markdown("---")

# === Auto Refresh (every 5s) ===
time.sleep(5)
st.rerun()
