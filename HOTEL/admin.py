import streamlit as st
import json
import os
import time
from datetime import datetime

# Path to orders.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDER_FILE = os.path.join(BASE_DIR, "orders.json")

# Load/save helpers
def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(file, 'r', encoding='utf-8') as f:
        try:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
        except json.JSONDecodeError:
            return []

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Auto-refresh
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Panel - Restaurant Orders")
st.caption("Live orders below. Use buttons to update status.")

# Delete completed orders
if st.button("🗑️ Delete Completed Orders"):
    orders = load_json(ORDER_FILE)
    filtered = [o for o in orders if o["status"] != "Completed"]
    save_json(ORDER_FILE, filtered)
    st.success("✅ Completed orders deleted.")
    st.rerun()

st.text(f"Loading from: {ORDER_FILE}")
orders = load_json(ORDER_FILE)
st.markdown("### Loaded Orders:")
st.json(orders)

if not orders:
    st.info("No orders found.")
else:
    for order in sorted(orders, key=lambda o: o['timestamp'], reverse=True):
        status = order.get("status", "Pending")
        color = {
            "Pending": "orange",
            "Preparing": "blue",
            "Served": "green",
            "Completed": "gray"
        }.get(status, "white")

        with st.container():
            st.markdown(f"### 🧾 Order #{order['id']} - Table {order['table']}")
            st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
            st.caption(f"🕒 Placed at: {order['timestamp']}")

            with st.expander("🧺 View Items"):
                total = 0
                for item in order["cart"]:
                    line = f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}"
                    st.markdown(line)
                    total += item['qty'] * item['price']
                st.markdown(f"**Total: ₹{total}**")

            new_status = st.radio(
                f"Update status for Order #{order['id']}",
                ["Pending", "Preparing", "Served", "Completed"],
                index=["Pending", "Preparing", "Served", "Completed"].index(status),
                key=f"status_{order['id']}",
                horizontal=True
            )

            if new_status != status:
                order["status"] = new_status
                save_json(ORDER_FILE, orders)
                st.toast(f"✅ Status updated to {new_status}")
                st.rerun()

# Auto-refresh
time.sleep(5)
st.rerun()
