import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 🔄 Auto-refresh every 5 seconds
count = st_autorefresh(interval=5000, key="admin_autorefresh")

# File paths
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "..", "orders.json")
MENU_FILE = os.path.join(os.path.dirname(__file__), "..", "menu.json")

st.set_page_config(page_title="Admin Panel", layout="centered")
st.markdown("""
    <style>
    .order-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    .order-box h4 {
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛠️ Admin Panel - Order Management")

# Toast function
def toast(message: str, duration=3000):
    st.markdown(f"""
        <script>
        const toast = document.createElement("div");
        toast.textContent = "{message}";
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #323232;
            color: white;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 15px;
            z-index: 9999;
            animation: fadein 0.3s, fadeout 0.3s ease {duration / 1000 - 0.3}s;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), {duration});
        </script>
    """, unsafe_allow_html=True)

# Load helpers
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load data
menu = load_json(MENU_FILE, {})
orders = load_json(ORDERS_FILE, [])

# Track first run for toast
if "order_count" not in st.session_state:
    st.session_state.order_count = len(orders)

# New order notification
if len(orders) > st.session_state.order_count:
    toast("📦 New order received!")
    st.session_state.order_count = len(orders)

# Status flow
status_flow = ["Pending", "Preparing", "Ready", "Completed"]

# Handle empty state
if not orders:
    st.info("📫 No orders yet.")

# Display orders
for idx, order in reversed(list(enumerate(orders))):
    with st.container():
        st.markdown("<div class='order-box'>", unsafe_allow_html=True)
        st.markdown(f"### 🪑 Table {order.get('table', '?')} - <span style='color: green'>{order.get('status', 'Unknown')}</span>", unsafe_allow_html=True)
        st.caption(f"🕒 {order.get('timestamp', 'Unknown')}")

        st.markdown("#### 🧾 Ordered Items")
        total = 0
        items = order.get("items", {})
        for name, item in items.items():
            qty = item.get("quantity", 0)
            price = item.get("price", 0)
            total += qty * price
            st.markdown(f"🍽️ **{name}** x {qty} = ₹{price * qty}")

        st.markdown(f"💰 **Total: ₹{total}**")

        st.markdown("---")

        current_status = order.get("status", "Pending")
        next_status_options = [s for s in status_flow if s != current_status]
        new_status = st.selectbox("Change Status", [current_status] + next_status_options, key=f"status_{idx}")

        if new_status != current_status:
            if st.button("✅ Update Status", key=f"update_{idx}"):
                orders[idx]["status"] = new_status
                save_json(ORDERS_FILE, orders)
                toast(f"✅ Order updated to {new_status}")
                st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Cancel Order", key=f"cancel_{idx}"):
                orders[idx]["status"] = "Cancelled"
                save_json(ORDERS_FILE, orders)
                toast("❌ Order cancelled")
                st.rerun()

        with col2:
            if order.get("status") == "Completed" and st.button("🗑️ Delete", key=f"delete_{idx}"):
                orders.pop(idx)
                save_json(ORDERS_FILE, orders)
                toast("🗑️ Order deleted")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
