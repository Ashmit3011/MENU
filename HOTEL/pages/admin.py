import streamlit as st
import json
import os
from datetime import datetime
import time

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDER_FILE = os.path.join(BASE_DIR, "../orders.json")

# Load orders
def load_orders():
    if not os.path.exists(ORDER_FILE):
        return []
    with open(ORDER_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

# Save orders
def save_orders(orders):
    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

# App config
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Dashboard - Smart Restaurant")

# Session state to track order count
if "order_count" not in st.session_state:
    st.session_state.order_count = 0

# Load and sort orders
orders = load_orders()
orders = sorted(orders, key=lambda x: x.get("timestamp", ""), reverse=True)

# 🔔 Play sound and show toast if new order received
if len(orders) > st.session_state.order_count:
    st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg", autoplay=True)
    st.toast("🆕 New order received!", icon="🔔")

# Update tracked count
st.session_state.order_count = len(orders)

# Display orders
if not orders:
    st.info("📭 No orders received yet.")
else:
    for order in orders:
        color = {
            "Pending": "#facc15",
            "Preparing": "#38bdf8",
            "Served": "#4ade80",
            "Completed": "#d4d4d8"
        }.get(order["status"], "#e2e8f0")

        with st.container():
            st.markdown(
                f"""
                <div style="border-left: 8px solid {color}; padding: 1rem; margin-bottom: 1rem; background-color: #1f2937; border-radius: 10px;">
                    <h4 style="margin:0;">🧾 Order #{order['id']} | Table: {order['table']}</h4>
                    <p style="margin:0; font-size: 14px; color: #9ca3af;">🕒 {order['timestamp']}</p>
                    <ul>
                        {''.join([f"<li>{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}</li>" for item in order['cart']])}
                    </ul>
                    <b>Total: ₹{sum([item['qty'] * item['price'] for item in order['cart']])}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

        new_status = st.selectbox(
            f"Update status for Order #{order['id']}",
            ["Pending", "Preparing", "Served", "Completed"],
            index=["Pending", "Preparing", "Served", "Completed"].index(order["status"]),
            key=f"status_{order['id']}"
        )

        if new_status != order["status"]:
            order["status"] = new_status
            save_orders(orders)
            st.success(f"✅ Order #{order['id']} updated to {new_status}")
            st.experimental_rerun()

# Cleanup
st.markdown("---")
if st.button("🧹 Delete Completed Orders"):
    orders = [o for o in orders if o["status"] != "Completed"]
    save_orders(orders)
    st.success("✅ Completed orders removed.")
    st.experimental_rerun()

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
