import streamlit as st
import json
import time
from datetime import datetime

ORDERS_FILE = "orders.json"

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🧑‍🍳 Admin Panel - Live Orders")

# Load orders
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

# Toast style
st.markdown("""
<style>
.toast {
    position: fixed;
    bottom: 70px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    padding: 16px;
    border-radius: 10px;
    z-index: 10000;
    animation: slideIn 0.5s ease-out;
}
@keyframes slideIn {
    0% {opacity: 0; transform: translateY(20px);}
    100% {opacity: 1; transform: translateY(0);}
}
.order-card {
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    color: white;
}
.pending { background-color: #f39c12; }
.preparing { background-color: #3498db; }
.ready { background-color: #2ecc71; }
.served { background-color: #95a5a6; }
</style>
""", unsafe_allow_html=True)

def toast(msg):
    st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)

# --- MAIN LOGIC ---
orders = load_orders()
if not isinstance(orders, list):
    st.error("Orders format invalid.")
    st.stop()

orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)

if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        status = order.get("status", "Pending")
        status_class = {
            "Pending": "pending",
            "Preparing": "preparing",
            "Ready": "ready",
            "Served": "served"
        }.get(status, "pending")

        with st.container():
            st.markdown(f'<div class="order-card {status_class}">', unsafe_allow_html=True)
            st.markdown(f"### 🧾 Order ID: `{order['id']}`  |  Table: `{order['table']}`")
            st.markdown(f"**Status:** `{status}`")
            ts = datetime.fromtimestamp(order.get("timestamp", time.time()))
            st.caption(f"🕒 Placed at {ts.strftime('%I:%M %p')}")

            items = order.get("items", {})
            if isinstance(items, dict):
                for item in items.values():
                    st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                st.success(f"**Total: ₹{order.get('total', 0)}**")
            else:
                st.warning("⚠️ Malformed items in this order.")

            new_status = st.selectbox("Update Status", ["Pending", "Preparing", "Ready", "Served"], index=["Pending", "Preparing", "Ready", "Served"].index(status), key=order["id"])
            if new_status != status:
                order["status"] = new_status
                save_orders(orders)
                toast(f"✅ Order {order['id']} marked as {new_status}")
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# --- Auto-refresh (no blinking) ---
st.markdown("""
<script>
setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)
