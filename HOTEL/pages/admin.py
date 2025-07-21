import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# File paths
BASE_DIR = Path("/mnt/data")
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

st.set_page_config(page_title="Admin Panel", layout="wide")

# Load JSON helpers
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

# Load data
orders = load_json(ORDER_FILE)
feedbacks = load_json(FEEDBACK_FILE)

# Header
st.title("🛠️ Admin Panel – Smart Table Ordering")

# 🔔 New order detection
if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New Order Received!", icon="🔔")
    st.session_state.last_order_count = len(orders)

# Show orders
st.subheader("📦 Orders")
if orders:
    for order in reversed(orders):
        status = order.get("status", "Pending")
        color = {
            "Pending": "#fff3cd",
            "Preparing": "#d1ecf1",
            "Served": "#d4edda",
            "Completed": "#f8f9fa"
        }.get(status, "#ffffff")

        with st.container():
            st.markdown(
                f"<div style='background-color: {color}; padding: 1rem; border-radius: 1rem;'>",
                unsafe_allow_html=True
            )
            st.subheader(f"Order #{order['id']} – Table {order['table']}")
            st.caption(f"🕒 {order['timestamp']}")
            st.markdown(f"**Status:** `{status}`")

            with st.expander("🧾 Items"):
                total = 0
                for item in order["cart"]:
                    st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                    total += item['qty'] * item['price']
                st.write(f"**Total: ₹{total}**")

            new_status = st.selectbox(
                f"Update status for Order #{order['id']}",
                ["Pending", "Preparing", "Served", "Completed"],
                index=["Pending", "Preparing", "Served", "Completed"].index(status),
                key=f"status_{order['id']}"
            )
            if new_status != status:
                order["status"] = new_status
                save_json(ORDER_FILE, orders)
                st.success(f"✅ Status updated to {new_status}")
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("📭 No orders received yet.")

# 💬 Feedback section
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

# 🔁 Auto-refresh every 5s
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)
