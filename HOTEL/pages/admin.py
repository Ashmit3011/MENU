import streamlit as st
import json
import os
import time
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
ORDER_FILE = BASE_DIR / "orders.json"
MENU_FILE = BASE_DIR / "menu.json"

# Utilities
def load_json(file):
    if not file.exists():
        return []
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

# App config
st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("🔧 Admin Dashboard - Smart Restaurant")

# Load Orders
orders = load_json(ORDER_FILE)
if not orders:
    st.info("📭 No orders received yet.")
else:
    updated = False
    new_orders_detected = False

    for order in orders:
        status_color = {
            "Pending": "#f9c74f",
            "Preparing": "#90be6d",
            "Served": "#577590",
            "Completed": "#adb5bd"
        }.get(order['status'], "#ccc")

        with st.container():
            st.markdown(
                f"""
                <div style="border-left: 6px solid {status_color}; padding: 1rem; margin-bottom: 1rem; background-color: #f8f9fa; border-radius: 10px;">
                    <h4 style="margin-bottom: 0.2rem;">Order #{order['id']} - Table {order['table']}</h4>
                    <p style="margin: 0.2rem 0;">⏰ {order['timestamp']}</p>
                    <p style="margin: 0.2rem 0;">🧾 <b>Status:</b> <code>{order['status']}</code></p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("View Order Details"):
                total = 0
                for item in order['cart']:
                    st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                    total += item['qty'] * item['price']
                st.markdown(f"**Total: ₹{total}**")

            # Update Status Dropdown
            new_status = st.selectbox(
                f"Update Status for Order #{order['id']}",
                ["Pending", "Preparing", "Served", "Completed"],
                index=["Pending", "Preparing", "Served", "Completed"].index(order['status']),
                key=f"status_{order['id']}"
            )

            if new_status != order['status']:
                order['status'] = new_status
                updated = True
                st.toast(f"✅ Order #{order['id']} marked as {new_status}")

    if updated:
        save_json(ORDER_FILE, orders)

# Delete completed orders
if st.button("🗑️ Delete Completed Orders"):
    orders = [o for o in orders if o['status'] != 'Completed']
    save_json(ORDER_FILE, orders)
    st.success("Completed orders deleted.")
    st.rerun()

# Auto-refresh every 10s
st.markdown("""
<script>
setTimeout(function() {
    window.location.reload();
}, 10000);
</script>
""", unsafe_allow_html=True)
