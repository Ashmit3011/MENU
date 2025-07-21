import streamlit as st
import json
import os
from datetime import datetime

# === File Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "../menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "../orders.json")

# === Utility Functions ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("⚠️ orders.json is corrupted. Fixing now...")
            with open(ORDERS_FILE, "w") as f:
                json.dump([], f)
            return []
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# === Streamlit UI ===
st.set_page_config(page_title="Kitchen Admin Panel", layout="wide")
st.title("👨‍🍳 Kitchen Dashboard")

orders = load_orders()

if not orders:
    st.info("No orders found.")
else:
    # Sort orders by time descending
    orders.sort(key=lambda x: x["time"], reverse=True)

    for idx, order in enumerate(orders):
        with st.expander(f"🧾 Table {order['table']} - ₹{order['total']} ({order['status']})", expanded=(idx == 0)):
            st.markdown(f"**🕒 Time:** {order['time']}")
            for item in order["items"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            st.markdown(f"### 💰 Total: ₹{order['total']}")

            # Status selector
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

# === Auto-refresh every 5 seconds ===
st.markdown("<script>setTimeout(() => location.reload(), 5000);</script>", unsafe_allow_html=True)
