import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="🧑‍🍳 Admin Panel - Live Orders", layout="wide")
st.title("🧑‍🍳 Admin Panel - Live Orders")

ORDERS_FILE = "orders.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

orders = load_orders()

# Handle missing or invalid timestamps gracefully
for order in orders:
    try:
        order['timestamp'] = float(order.get('timestamp', 0))
    except:
        order['timestamp'] = 0

# Sort by latest timestamp
orders = sorted(orders, key=lambda x: x['timestamp'], reverse=True)

status_colors = {
    "Pending": "#FFA500",
    "Preparing": "#3498DB",
    "Ready": "#27AE60",
    "Served": "#8E44AD"
}

st.markdown("### 📦 Current Orders")

if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        status_color = status_colors.get(order['status'], "#000")
        try:
            time_str = datetime.fromtimestamp(order['timestamp']).strftime("%I:%M %p")
        except:
            time_str = "N/A"

        st.markdown(f"""
            <div style='border: 2px solid {status_color}; border-radius: 10px; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9;'>
                <strong>🧾 Order ID:</strong> {order['id']}<br>
                <strong>🪑 Table:</strong> {order['table']}<br>
                <strong>⏰ Time:</strong> {time_str}<br>
                <strong>Status:</strong> <span style='color:{status_color}; font-weight:bold'>{order['status']}</span><br>
                <strong>Items:</strong><br>
        """, unsafe_allow_html=True)

        for item in order.get("items", {}).values():
            st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

        # Status update dropdown
        new_status = st.selectbox(
            "Update Status",
            options=["Pending", "Preparing", "Ready", "Served"],
            index=["Pending", "Preparing", "Ready", "Served"].index(order["status"]),
            key=f"status_{order['id']}"
        )

        if new_status != order["status"]:
            order["status"] = new_status
            save_orders(orders)
            st.success(f"✅ Order {order['id']} status updated to {new_status}")
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# Smooth auto-refresh every 5 seconds
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)
