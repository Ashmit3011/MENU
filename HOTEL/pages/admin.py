import streamlit as st
import json
import os
import time
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

st.set_page_config(page_title="🛎️ Admin Panel", layout="centered")

# === File Setup ===
for file in [ORDERS_FILE, FEEDBACK_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

st.title("🛎️ Live Order Dashboard")

# === Load Orders ===
with open(ORDERS_FILE, "r") as f:
    orders = json.load(f)

orders.sort(key=lambda x: x["time"], reverse=True)

# === New Order Notification ===
if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New Order Received", icon="🧾")
    st.audio("https://www.soundjay.com/buttons/beep-07.wav", autoplay=True)
    st.session_state.last_order_count = len(orders)

# === Show Orders ===
if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        st.markdown(f"""
        ### 🧾 Order #{order['id']}
        **🪑 Table:** {order['table']}  
        **⏱️ Time:** {order['time']}  
        **📦 Status:** `{order['status']}`  
        """)
        for item in order["items"]:
            st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

        st.markdown(f"**💵 Total:** ₹{order['total']}")

        col1, col2 = st.columns(2)
        statuses = ["Pending", "Preparing", "Ready", "Served"]
        current = statuses.index(order["status"])

        with col1:
            if current < len(statuses) - 1:
                if st.button(f"➡️ {statuses[current + 1]}", key=f"next_{order['id']}"):
                    order["status"] = statuses[current + 1]
                    with open(ORDERS_FILE, "w") as f:
                        json.dump(orders, f, indent=2)
                    st.rerun()

        with col2:
            if st.button("❌ Remove Order", key=f"remove_{order['id']}"):
                orders.remove(order)
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.rerun()

        st.markdown("---")

# === Feedback Section ===
st.markdown("### 💬 Recent Feedback")
with open(FEEDBACK_FILE, "r") as f:
    feedbacks = json.load(f)

if feedbacks:
    for fb in feedbacks[-5:]:
        st.success(f"🪑 Table {fb['table']} at {fb['time']}: {fb['feedback']}")
else:
    st.write("No feedback yet.")

# === Auto-refresh ===
time.sleep(5)
st.rerun()
