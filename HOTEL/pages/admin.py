import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# === Auto-refresh every 5 seconds ===
st_autorefresh(interval=5000, key="admin_autorefresh")

# === File paths ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")

# === Utility Functions ===
def load_json(file_path, default=[]):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to parse {file_path}")
    return default

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Load Data ===
orders = load_json(ORDERS_FILE)
menu = load_json(MENU_FILE)

# === UI Setup ===
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛠️ Admin Panel - Order Management")

if not orders:
    st.info("No orders available yet.")
    st.stop()

# === Display Orders ===
for idx, order in enumerate(reversed(orders)):
    st.markdown("---")
    st.markdown(f"### 🪑 Table: {order['table']} | ⏰ {order['timestamp']}")
    st.markdown(f"**Current Status:** `{order['status']}`")
    st.markdown(f"**Payment Method:** `{order.get('payment_method', 'N/A')}`")

    item_data = []
    for item_id, qty in order['items'].items():
        item = next((i for i in menu if i['id'] == item_id), {"name": "Unknown", "price": 0})
        item_data.append({
            "Item": item['name'],
            "Quantity": qty,
            "Price": item['price'],
            "Total": qty * item['price']
        })

    st.dataframe(pd.DataFrame(item_data), use_container_width=True)

    # === Status update ===
    status_options = ["Preparing", "Ready", "Completed"]
    new_status = st.selectbox(
        f"Update status for Table {order['table']} (Order #{len(orders) - 1 - idx}):",
        status_options,
        index=status_options.index(order['status']) if order['status'] in status_options else 0,
        key=f"status_{idx}"
    )

    if new_status != order['status']:
        order['status'] = new_status
        save_json(ORDERS_FILE, orders)
        st.success(f"✅ Status updated to '{new_status}' for Table {order['table']}")
        st.experimental_rerun()
