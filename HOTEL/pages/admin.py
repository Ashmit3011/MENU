import streamlit as st
import json
import os
from datetime import datetime
from uuid import uuid4
import time

st.set_page_config(page_title="🍽️ Admin Panel", layout="wide")

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
orders_file = os.path.join(BASE_DIR, "orders.json")

# === Styling ===
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .order-card {
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            background-color: #f1f5f9;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .pending { border-left: 6px solid #facc15; }
        .preparing { border-left: 6px solid #38bdf8; }
        .served { border-left: 6px solid #4ade80; }
    </style>
""", unsafe_allow_html=True)

# === Auto-refresh logic (no blinking) ===
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 3:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# === Load orders ===
if os.path.exists(orders_file):
    with open(orders_file, "r") as f:
        orders = json.load(f)
else:
    orders = []

st.title("📋 Admin Dashboard - Live Orders")

status_colors = {
    "Pending": "pending",
    "Preparing": "preparing",
    "Served": "served"
}

# === Show orders ===
if orders:
    orders = sorted(orders, key=lambda x: x["timestamp"], reverse=True)
    updated = False

    for order in orders:
        color_class = status_colors.get(order["status"], "pending")
        with st.container():
            st.markdown(f"<div class='order-card {color_class}'>", unsafe_allow_html=True)
            st.markdown(f"**🪑 Table {order['table']}**  &nbsp;&nbsp; 🕒 _{order['timestamp']}_")
            st.markdown(f"**Status:** `{order['status']}`")
            st.markdown("---")
            for item in order.get("cart", []):
                st.write(f"- {item['name']} × {item['quantity']} = ₹{item['price'] * item['quantity']}")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Preparing", key=f"prep_{order['id']}"):
                    order['status'] = "Preparing"
                    st.toast(f"🔧 Order for Table {order['table']} is now Preparing.")
                    updated = True
            with col2:
                if st.button("Served", key=f"serve_{order['id']}"):
                    order['status'] = "Served"
                    st.toast(f"🍽️ Order for Table {order['table']} has been Served!")
                    updated = True
            with col3:
                if st.button("❌ Cancel", key=f"cancel_{order['id']}"):
                    orders.remove(order)
                    st.toast(f"❌ Order for Table {order['table']} has been Cancelled.")
                    updated = True

            st.markdown("</div>", unsafe_allow_html=True)

    if updated:
        with open(orders_file, "w") as f:
            json.dump(orders, f, indent=2)

else:
    st.info("No orders yet.")
