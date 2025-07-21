import streamlit as st
import json
import os
from datetime import datetime
import time

# === File Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "../menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "../orders.json")
STATE_FILE = os.path.join(BASE_DIR, "last_seen.txt")

# === Load & Save ===
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

def get_last_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return ""

def set_last_seen(ts):
    with open(STATE_FILE, "w") as f:
        f.write(ts)

# === UI Setup ===
st.set_page_config(page_title="🍳 Admin Kitchen", layout="wide")
st.title("👨‍🍳 Kitchen Admin Panel (Auto-Refresh)")

# === Load Orders ===
orders = load_orders()
orders.sort(key=lambda x: x["time"], reverse=True)

# === Get Last Seen Timestamp
last_seen = get_last_seen()
latest_time = orders[0]["time"] if orders else ""

# === Detect New Order
new_order = latest_time != last_seen

if new_order and orders:
    st.toast("🛎️ New Order Received!", icon="📦")
    st.markdown("""
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
        </audio>
    """, unsafe_allow_html=True)
    set_last_seen(latest_time)

# === Show Orders ===
if not orders:
    st.info("No orders yet.")
else:
    for idx, order in enumerate(orders):
        with st.expander(f"🧾 Table {order['table']} - ₹{order['total']} ({order['status']})", expanded=(idx == 0)):
            st.markdown(f"**🕒 Time:** {order['time']}")
            for item in order["items"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            st.markdown(f"### 💰 Total: ₹{order['total']}")

            # Status update dropdown
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

# === Real-Time Refresh with Streamlit Loop ===
# Note: This reruns the script every 5 seconds
st.markdown("<p style='color:gray'>⏱ Refreshing every 5 seconds…</p>", unsafe_allow_html=True)
time.sleep(5)
st.rerun()
