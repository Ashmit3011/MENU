import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# Set Streamlit page config
st.set_page_config(page_title="Admin Panel", layout="wide")

# File paths
BASE_DIR = Path(__file__).parent.parent.resolve()
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# Load JSON safely
def load_json(file):
    file.parent.mkdir(parents=True, exist_ok=True)
    if not file.exists():
        file.write_text("[]", encoding="utf-8")
    try:
        with file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

# Save JSON
def save_json(file, data):
    with file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Session state
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

# Load data
orders = load_json(ORDER_FILE)
feedbacks = load_json(FEEDBACK_FILE)

st.title("🛠️ Admin Panel – Smart Table Ordering")

# 🔔 New order detection
if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New Order Received!", icon="🍽️")
    st.audio("https://www.myinstants.com/media/sounds/bell.mp3", format="audio/mp3")
    st.session_state.last_order_count = len(orders)

# 📦 Show Orders
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
                f"<div style='background-color:{color};padding:1rem;border-radius:1rem;margin-bottom:1rem;'>",
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
                st.stop()

            st.markdown("</div>", unsafe_allow_html=True)

    # 🗑️ Button to delete completed orders
    if st.button("🗑️ Delete Completed Orders"):
        orders = [order for order in orders if order.get("status") != "Completed"]
        save_json(ORDER_FILE, orders)
        st.success("✅ Completed orders deleted successfully.")
        st.rerun()
else:
    st.info("📭 No orders received yet.")

# 💬 Customer Feedback
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

# 🔁 Auto-refresh every 5 seconds
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)
