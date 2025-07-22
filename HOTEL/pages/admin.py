import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Autorefresh every 5 seconds
st_autorefresh(interval=5000, key="admin_refresh")

# --- File paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'menu_files')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

# --- Load Orders ---
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# --- Save Orders ---
def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

# --- Page setup ---
st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🧑‍🍳 Admin Dashboard - Live Orders")

# Load current orders
orders = load_orders()
status_stages = ["Pending", "Preparing", "Ready", "Completed"]

if not orders:
    st.info("📭 No active orders.")
else:
    for order in sorted(orders, key=lambda x: x["timestamp"], reverse=True):
        with st.container():
            st.markdown(f"### 🧾 Order `{order['id']}` - {order['table']}")
            st.markdown(f"⏰ Placed: {datetime.fromtimestamp(order['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"📝 Status: **{order['status']}**")

            with st.expander("📋 Items Ordered"):
                for item in order["items"].values():
                    st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                next_index = status_stages.index(order["status"]) + 1 if order["status"] in status_stages else 0
                if next_index < len(status_stages):
                    if st.button(f"➡️ Mark as {status_stages[next_index]}", key=f"next_{order['id']}"):
                        order["status"] = status_stages[next_index]
                        save_orders(orders)
                        st.rerun()

            with col2:
                if st.button("🗑️ Delete (Completed)", key=f"delete_{order['id']}"):
                    if order["status"] == "Completed":
                        orders = [o for o in orders if o["id"] != order["id"]]
                        save_orders(orders)
                        st.success(f"Order `{order['id']}` deleted.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Only completed orders can be deleted.")