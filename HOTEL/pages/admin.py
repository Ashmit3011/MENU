import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path

ORDERS_FILE = Path(__file__).resolve().parent / "orders.json"
FEEDBACK_FILE = Path(__file__).resolve().parent / "feedback.json"

st.set_page_config(page_title="🛎️ Admin Panel", layout="centered")

# Initialize
if not ORDERS_FILE.exists():
    with open(ORDERS_FILE, "w") as f:
        json.dump([], f)
if not FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f)

if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

st.title("🛎️ Admin Dashboard")

# Load Orders
with open(ORDERS_FILE, "r") as f:
    orders = json.load(f)

orders.sort(key=lambda x: x["time"], reverse=True)

# New Order Detection
if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New Order Received", icon="🧾")
    st.audio("https://www.soundjay.com/buttons/beep-07.wav", autoplay=True)
    st.session_state.last_order_count = len(orders)

if not orders:
    st.info("No orders yet")
else:
    for order in orders:
        st.markdown(f"""
        ### 🍽️ Order #{order['id']}
        **🪑 Table:** {order['table']}  
        **🕒 Time:** {order['time']}  
        **Status:** `{order['status']}`
        """)

        for item in order['items']:
            st.markdown(f"- {item['name']} x {item['qty']} (₹{item['price'] * item['qty']})")

        st.markdown(f"**Total: ₹{order['total']}**")

        col1, col2 = st.columns(2)
        statuses = ["Pending", "Preparing", "Ready", "Served"]
        current_idx = statuses.index(order["status"])

        with col1:
            if current_idx < 3:
                if st.button(f"Next → {statuses[current_idx+1]}", key=f"{order['id']}_next"):
                    order['status'] = statuses[current_idx + 1]
                    with open(ORDERS_FILE, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.rerun()

        with col2:
            if st.button("❌ Remove Order", key=f"{order['id']}_remove"):
                orders.remove(order)
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.rerun()

        st.markdown("---")

# Feedback Viewer
st.markdown("### 💬 Customer Feedback")
with open(FEEDBACK_FILE, "r") as f:
    feedbacks = json.load(f)

if feedbacks:
    for fb in feedbacks[-5:]:
        st.info(f"[{fb['time']}] Table {fb['table']}: {fb['feedback']}")
else:
    st.write("No feedback yet")

# Auto-refresh
time.sleep(5)
st.rerun()
