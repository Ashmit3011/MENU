import streamlit as st
import json
import os
from datetime import datetime

# Fix file paths relative to base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")

# Load JSON data
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        try:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
        except json.JSONDecodeError:
            return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Streamlit app
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Dashboard - Smart Restaurant")

orders = load_json(ORDER_FILE)

if orders:
    st.success(f"📦 {len(orders)} total orders")
    for order in reversed(orders):
        with st.container():
            st.subheader(f"🧾 Order #{order['id']} - Table {order['table']}")
            st.caption(f"🕒 {order['timestamp']}")
            st.markdown(f"**Status:** `{order['status']}`")

            with st.expander("🔍 View Items"):
                for item in order['cart']:
                    st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            new_status = st.selectbox(
                "Update Status",
                ["Pending", "Preparing", "Served", "Completed"],
                index=["Pending", "Preparing", "Served", "Completed"].index(order['status']),
                key=f"status_{order['id']}"
            )
            if new_status != order['status']:
                order['status'] = new_status
                save_json(ORDER_FILE, orders)
                st.success(f"✅ Order #{order['id']} status updated to {new_status}")
else:
    st.info("📭 No orders received yet.")

# Option to clear completed
if st.button("🗑️ Delete Completed Orders"):
    orders = [o for o in orders if o["status"] != "Completed"]
    save_json(ORDER_FILE, orders)
    st.success("✅ Completed orders removed!")

# Debug panel
with st.expander("🛠 Debug: Raw Orders Data"):
    st.json(orders)
