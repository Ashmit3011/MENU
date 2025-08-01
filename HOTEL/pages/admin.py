import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="admin_autorefresh")

# === File Paths ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")

# === Load JSON Data ===
def load_json(file_path, default=[]):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except json.JSONDecodeError:
        st.error(f"Failed to read {file_path}")
    return default

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

orders = load_json(ORDERS_FILE)
menu = load_json(MENU_FILE)

# === Streamlit UI ===
st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠️ Admin Dashboard")

if not orders:
    st.info("No orders found.")
    st.stop()

# === Order Management ===
for idx, order in enumerate(reversed(orders)):
    st.markdown("---")
    st.subheader(f"🪑 Table: {order['table']} | ⏰ {order['timestamp']}")
    st.markdown(f"**Status:** `{order['status']}`")
    st.markdown(f"**Payment Method:** `{order.get('payment_method', 'N/A')}`")

    item_data = []
    for item_id, qty in order['items'].items():
        item = next((i for i in menu if i["id"] == item_id), {"name": "Unknown", "price": 0})
        item_data.append({
            "Item": item["name"],
            "Quantity": qty,
            "Price": item["price"],
            "Total": qty * item["price"]
        })

    st.dataframe(pd.DataFrame(item_data), use_container_width=True)

    new_status = st.selectbox(
        f"Update Status for Table {order['table']} (Order {len(orders) - idx}):",
        ["Preparing", "Ready", "Completed"],
        index=["Preparing", "Ready", "Completed"].index(order["status"]),
        key=f"status_{idx}"
    )

    if new_status != order["status"]:
        order["status"] = new_status
        save_json(ORDERS_FILE, orders)
        st.success(f"✅ Updated status to '{new_status}'")
