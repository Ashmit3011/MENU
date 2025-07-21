import streamlit as st
import json
import time
from datetime import datetime

st.set_page_config(page_title="🧑‍🍳 Admin Panel - Live Orders", layout="wide")

ORDERS_FILE = "orders.json"

# Load orders
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Helper for safe timestamp sorting
def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

# Load orders safely and sort
orders = load_orders()
orders = [o for o in orders if isinstance(o, dict) and "timestamp" in o]
orders = sorted(orders, key=lambda x: safe_float(x.get("timestamp", 0)), reverse=True)

# Track last seen order in session
st.session_state.setdefault("last_order_id", "")

# Sound effect on new order
if orders and orders[0]['id'] != st.session_state['last_order_id']:
    st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg", format="audio/ogg")
    st.session_state['last_order_id'] = orders[0]['id']

st.title("🧑‍🍳 Admin Panel - Live Orders")

if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        with st.container():
            status_color = {
                "Pending": "orange",
                "Preparing": "blue",
                "Ready": "green",
                "Served": "gray"
            }.get(order["status"], "red")

            st.markdown(f"""
            <div style='border: 2px solid {status_color}; border-radius: 10px; padding: 10px; margin-bottom: 10px;'>
                <strong>🧾 Order ID:</strong> {order['id']} <br>
                <strong>🪑 Table:</strong> {order['table']} <br>
                <strong>⏰ Time:</strong> {datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')} <br>
                <strong>Status:</strong> <span style='color:{status_color}; font-weight:bold'>{order['status']}</span> <br>
                <strong>Items:</strong>
            """, unsafe_allow_html=True)

            try:
                for item in order["items"].values():
                    st.markdown(f"- {item['name']} x {item['qty']}")
            except:
                st.markdown("⚠️ Error loading items.")

            new_status = st.selectbox(
                f"Update status for Order {order['id']}",
                ["Pending", "Preparing", "Ready", "Served"],
                index=["Pending", "Preparing", "Ready", "Served"].index(order["status"]),
                key=order["id"]
            )

            if new_status != order["status"]:
                order["status"] = new_status
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.success(f"✅ Status updated to {new_status}")
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# Live refresh every 5 seconds (without blinking)
st.markdown("""
<script>
setTimeout(() => {
    window.parent.postMessage({streamlitSetFrameHeight: window.innerHeight}, "*");
    window.location.reload();
}, 5000);
</script>
""", unsafe_allow_html=True)
