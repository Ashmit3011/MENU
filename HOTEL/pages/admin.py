import streamlit as st
import json
import os
import time
from datetime import datetime
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent.resolve()
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

st.set_page_config(page_title="Admin Panel", layout="wide")

# Load data
def load_json(file):
    if not file.exists():
        file.write_text("[]", encoding="utf-8")
    with open(file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Session init
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0
if "seen_orders" not in st.session_state:
    st.session_state.seen_orders = []

# Admin panel
st.title("🛠️ Admin Panel – Smart Table Ordering")

orders = load_json(ORDER_FILE)
feedbacks = load_json(FEEDBACK_FILE)

# Sound and toast on new order
if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New Order Received!", icon="🔔")
    st.audio("https://www.myinstants.com/media/sounds/bell.mp3", format="audio/mp3")
    st.session_state.last_order_count = len(orders)

# Show orders
if orders:
    for order in reversed(orders):
        status = order.get("status", "Pending")
        status_color = {
            "Pending": "#ffeeba",
            "Preparing": "#bee5eb",
            "Served": "#d4edda",
            "Completed": "#e2e3e5"
        }.get(status, "#f8f9fa")

        with st.container():
            st.markdown(
                f"<div style='background-color: {status_color}; padding: 1rem; border-radius: 1rem;'>",
                unsafe_allow_html=True
            )
            st.subheader(f"Order #{order['id']} – Table {order['table']}")
            st.markdown(f"**Status:** `{status}`")
            st.caption(f"Placed at {order['timestamp']}")

            with st.expander("🧾 View Items"):
                total = 0
                for item in order["cart"]:
                    st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                    total += item['qty'] * item['price']
                st.write(f"**Total: ₹{total}**")

            new_status = st.selectbox(
                f"Update Status for Order #{order['id']}",
                ["Pending", "Preparing", "Served", "Completed"],
                index=["Pending", "Preparing", "Served", "Completed"].index(status),
                key=f"status_{order['id']}"
            )
            if new_status != status:
                order["status"] = new_status
                save_json(ORDER_FILE, orders)
                st.success(f"✅ Status updated to {new_status}")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("No orders yet.")

# Feedback section
st.markdown("---")
st.header("💬 Customer Feedback")
if feedbacks:
    for fb in reversed(feedbacks):
        with st.container():
            st.markdown("-----")
            st.write(f"🕒 {fb['timestamp']} | Table: {fb['table']}")
            st.write(f"⭐ Rating: {fb['rating']} / 5")
            st.write(f"💬 {fb['comments']}")
else:
    st.info("No feedback received yet.")

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
