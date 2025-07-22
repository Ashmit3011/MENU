# Save as admin.py
import streamlit as st
import json
import os
import time
from datetime import datetime

# Setup
st.set_page_config(page_title="🧑‍🍳 Admin Panel", layout="wide")
st.title("🧑‍🍳 Live Orders Dashboard")

ORDERS_FILE = os.path.join(os.path.dirname(__file__), "orders.json")

# Load orders
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# Save orders
def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

# Status flow
status_flow = ["Pending", "Preparing", "Ready", "Served"]
status_color = {
    "Pending": "#f39c12",
    "Preparing": "#3498db",
    "Ready": "#2ecc71",
    "Served": "#95a5a6"
}

# Load current orders
orders = load_orders()
orders = sorted(orders, key=lambda x: x.get("timestamp", 0), reverse=True)

if not orders:
    st.info("No orders placed yet.")
    st.stop()

updated = False

# Display all orders
for idx, order in enumerate(orders):
    st.markdown(f"""
        <div style='
            border: 2px solid {status_color.get(order['status'], 'gray')}; 
            border-radius: 12px; 
            padding: 16px; 
            margin-bottom: 20px; 
            background-color: #1e1e1e;
            color: white;
        '>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        🧾 **Order ID:** `{order['id']}`  
        🪑 **Table:** {order['table']}  
        ⏰ **Time:** {datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')}  
        📦 **Status:** <span style='color:{status_color[order['status']]}; font-weight:bold'>{order['status']}</span>
        """, unsafe_allow_html=True)

        st.markdown("📝 **Items Ordered:**")
        items = order.get("items", {})
        if isinstance(items, dict):
            for item in items.values():
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        else:
            st.warning("❌ Item format invalid.")

        progress = (status_flow.index(order["status"]) + 1) / len(status_flow)
        st.progress(progress)

    with col2:
        if order["status"] != "Served":
            next_index = status_flow.index(order["status"]) + 1
            if next_index < len(status_flow):
                next_status = status_flow[next_index]
                if st.button(f"➡️ Set to {next_status}", key=f"{order['id']}_next"):
                    orders[idx]["status"] = next_status
                    save_orders(orders)
                    updated = True
                    st.rerun()
        else:
            if st.button("🗑️ Delete", key=f"{order['id']}_delete"):
                del orders[idx]
                save_orders(orders)
                updated = True
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Play sound if updated
if updated and os.path.exists("notification.wav"):
    st.audio("notification.wav", autoplay=True)

# Auto-refresh every 5 seconds
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)