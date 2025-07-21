import streamlit as st
import json
import os
from datetime import datetime

# ---------- FILE PATHS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🧑‍🍳 Admin Panel - Manage Orders")

# ---------- FUNCTIONS ----------
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

status_list = ["Pending", "Preparing", "Ready", "Served"]

# ---------- UI ----------
orders = load_orders()
if not orders:
    st.info("No orders yet.")
else:
    orders = sorted(orders, key=lambda x: x['timestamp'], reverse=True)
    for order in orders:
        with st.expander(f"🧾 Order #{order['id']} | Table {order['table']} | Status: {order['status']}"):
            st.caption(f"🕒 Placed at {datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')}")
            for item in order['items'].values():
                st.markdown(f"- **{item['name']}** × {item['qty']} = ₹{item['qty'] * item['price']}")
            st.markdown(f"**Total:** ₹{order['total']}")
            
            selected_status = st.selectbox("Update Status", status_list,
                                           index=status_list.index(order['status']),
                                           key=order['id'])
            if selected_status != order['status']:
                order['status'] = selected_status
                save_orders(orders)
                st.success(f"✅ Order {order['id']} status updated to {selected_status}")
