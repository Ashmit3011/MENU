import streamlit as st
import json
import time
from datetime import datetime

st.set_page_config(page_title="Admin Panel", layout="wide")
ORDERS_FILE = "orders.json"

# Load orders safely
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save orders
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Safe timestamp parsing
def safe_timestamp(order):
    try:
        return float(order.get("timestamp", 0))
    except (ValueError, TypeError):
        return 0

# Load and sort
orders = load_orders()
orders = sorted(orders, key=safe_timestamp, reverse=True)

st.title("🛠️ Admin Panel – Live Orders")

if not orders:
    st.info("No orders yet.")
    st.stop()

status_colors = {
    "Pending": "#fdd835",
    "Preparing": "#42a5f5",
    "Ready": "#66bb6a",
    "Served": "#9e9e9e"
}

# Display orders
for order in orders:
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🧾 Order ID: `{order['id']}` | Table: **{order['table']}**")
        order_time = datetime.fromtimestamp(safe_timestamp(order)).strftime("%I:%M %p")
        st.caption(f"🕒 Placed at {order_time}")
        for item in order["items"].values():
            st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        st.success(f"Total: ₹{order['total']}")
    with col2:
        status = order["status"]
        new_status = st.selectbox(
            f"Update Status for `{order['id']}`",
            ["Pending", "Preparing", "Ready", "Served"],
            index=["Pending", "Preparing", "Ready", "Served"].index(status),
            key=order["id"]
        )
        if new_status != status:
            order["status"] = new_status
            save_orders(orders)
            st.success(f"✅ Status updated for `{order['id']}`")
            st.experimental_rerun()

    st.markdown(
        f"<div style='padding:6px;border-radius:8px;background-color:{status_colors[order['status']]};color:white;width:120px;text-align:center'>"
        f"{order['status']}</div>",
        unsafe_allow_html=True
    )

# Optional: Auto-refresh every 10s
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 10000);
</script>
""", unsafe_allow_html=True)
