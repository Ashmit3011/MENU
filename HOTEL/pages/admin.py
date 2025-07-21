import streamlit as st
import json
import os
import time
from datetime import datetime

# === File paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# === Helper functions ===
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def next_status(status):
    steps = ["Pending", "Preparing", "Ready", "Served"]
    if status in steps and status != "Served":
        return steps[steps.index(status) + 1]
    return status

# === UI config ===
st.set_page_config(page_title="🛠️ Admin Panel", layout="centered")

st.markdown("""
    <style>
    .order-card {
        background-color: #181818;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        border: 1px solid #333;
    }
    .status-Pending {
        color: orange;
    }
    .status-Preparing {
        color: #00bfff;
    }
    .status-Ready {
        color: green;
    }
    .status-Served {
        color: gray;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛠️ Admin Order Manager")

orders = load_orders()
orders.sort(key=lambda x: x["time"], reverse=True)

if not orders:
    st.info("No orders yet.")
else:
    for i, order in enumerate(orders):
        with st.container():
            st.markdown(f"<div class='order-card'>", unsafe_allow_html=True)
            st.markdown(f"### 🧾 Order ID: `{order['id']}`")
            st.markdown(f"🪑 **Table:** {order['table']}  |  🕒 *{order['time']}*")
            st.markdown(f"💵 **Total:** ₹{order['total']}")

            # Status Display
            st.markdown(f"📦 **Status:** <span class='status-{order['status']}'>{order['status']}</span>", unsafe_allow_html=True)

            # Item list
            st.markdown("**🧺 Items:**")
            for item in order['items']:
                st.markdown(f"- {item['name']} × {item['qty']}")

            # Status control
            col1, col2 = st.columns([1, 2])
            with col1:
                if order['status'] != "Served":
                    if st.button(f"➡️ Next Status", key=f"next_{order['id']}"):
                        orders[i]['status'] = next_status(order['status'])
                        save_orders(orders)
                        st.experimental_rerun()
            with col2:
                st.markdown(f"⬆️ Next: `{next_status(order['status'])}`" if order['status'] != "Served" else "`✅ Order Completed`")
            st.markdown("</div>", unsafe_allow_html=True)

# === Auto-refresh every 5 seconds ===
time.sleep(5)
st.rerun()
