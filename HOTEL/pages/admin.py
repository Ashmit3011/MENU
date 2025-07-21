import streamlit as st
import json
import os
from datetime import datetime

# === File Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "../menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "../orders.json")

# === Utility Functions ===
def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            with open(ORDERS_FILE, "w") as f:
                json.dump([], f)
            return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# === Load State ===
st.set_page_config(page_title="Kitchen Admin", layout="wide")

if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

orders = load_orders()

# === Detect New Orders ===
new_order_detected = len(orders) > st.session_state.last_order_count
st.session_state.last_order_count = len(orders)

# === Alert for New Orders ===
if new_order_detected:
    st.toast("🔔 New order received!", icon="🛎️")
    st.markdown(
        """
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
        </audio>
        """,
        unsafe_allow_html=True
    )

st.title("👨‍🍳 Kitchen Admin Panel")

if not orders:
    st.info("No orders yet.")
else:
    orders.sort(key=lambda x: x["time"], reverse=True)
    for idx, order in enumerate(orders):
        with st.expander(f"🧾 Table {order['table']} - ₹{order['total']} ({order['status']})", expanded=(idx == 0)):
            st.markdown(f"**🕒 Time:** {order['time']}")
            for item in order["items"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            st.markdown(f"### 💰 Total: ₹{order['total']}")

            # Update status
            new_status = st.selectbox(
                "Update Status",
                ["Pending", "Preparing", "Ready", "Served"],
                index=["Pending", "Preparing", "Ready", "Served"].index(order["status"]),
                key=f"status_{idx}"
            )

            if new_status != order["status"]:
                order["status"] = new_status
                save_orders(orders)
                st.success(f"✅ Status updated to {new_status}")
                st.rerun()

# === Auto-refresh every 5 seconds (force reload without blinking) ===
st.markdown("""
<script>
setTimeout(() => {
    window.location.reload();
}, 3000);
</script>
""", unsafe_allow_html=True)
