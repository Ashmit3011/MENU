import streamlit as st
import json
import os
from datetime import datetime

# === File Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "../menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "../orders.json")

# === Load Orders Function ===
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

# === Streamlit Setup ===
st.set_page_config(page_title="Kitchen Admin", layout="wide")
st.title("👨‍🍳 Kitchen Admin Panel")

# === Auto-refresh every 5 seconds ===
st.markdown("""
<script>
setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)

# === Load Orders ===
orders = load_orders()
orders.sort(key=lambda x: x["time"], reverse=True)

# === Load last known time from file
STATE_FILE = os.path.join(BASE_DIR, "last_seen.txt")
last_seen_time = ""

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last_seen_time = f.read().strip()

# === Detect New Orders by Time
latest_time = orders[0]["time"] if orders else ""
new_order = latest_time != last_seen_time

# === Play Sound + Toast for New Orders
if new_order and orders:
    st.toast("🛎️ New order received!", icon="🔔")
    st.markdown("""
    <audio autoplay>
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>
    """, unsafe_allow_html=True)
    with open(STATE_FILE, "w") as f:
        f.write(latest_time)

# === Display Orders ===
if not orders:
    st.info("No orders yet.")
else:
    for idx, order in enumerate(orders):
        with st.expander(f"🧾 Table {order['table']} - ₹{order['total']} ({order['status']})", expanded=(idx == 0)):
            st.markdown(f"**🕒 Time:** {order['time']}")
            for item in order["items"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            st.markdown(f"### 💰 Total: ₹{order['total']}")

            # === Status Update
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
