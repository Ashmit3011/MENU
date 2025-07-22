import streamlit as st
import json
import os
import time
from datetime import datetime

# Page setup
st.set_page_config(page_title="Smart Table Ordering", layout="centered")
st.title("📲 Smart Table Ordering System")

# --- File paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'menu_files')
MENU_FILE = os.path.join(DATA_DIR, 'menu.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

# --- Load menu ---
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, 'r') as f:
            return json.load(f)
    return []

# --- Load orders ---
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# --- Save orders ---
def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

# Load menu
menu = load_menu()
if not menu:
    st.error("⚠️ Menu not found or is empty!")
    st.stop()

# --- Select Table ---
table_number = st.selectbox("🪑 Select Your Table", [f"Table {i}" for i in range(1, 11)])

# --- Item selection ---
st.subheader("📝 Select Items")
cart = {}

for item in menu:
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"**{item['name']}** - ₹{item['price']}")
    with col2:
        qty = st.number_input("Qty", min_value=0, max_value=10, step=1, key=f"qty_{item['id']}")
        if qty > 0:
            cart[item['id']] = {
                "name": item["name"],
                "price": item["price"],
                "qty": qty
            }

# --- Place Order ---
if st.button("✅ Place Order"):
    if not cart:
        st.warning("🛒 Your cart is empty!")
    else:
        orders = load_orders()
        timestamp = time.time()
        order_id = f"ORD{int(timestamp)}"

        new_order = {
            "id": order_id,
            "table": table_number,
            "timestamp": timestamp,
            "status": "Pending",
            "items": cart
        }

        orders.append(new_order)
        save_orders(orders)

        st.success(f"🧾 Order `{order_id}` placed successfully!")
        st.balloons()
        st.rerun()

# --- Live Order Tracker ---
st.subheader("📦 Live Order Status Tracker")

orders = load_orders()
table_orders = [order for order in orders if order["table"] == table_number]
latest_order = sorted(table_orders, key=lambda x: x["timestamp"], reverse=True)[0] if table_orders else None

if latest_order:
    st.markdown(f"**Order ID:** `{latest_order['id']}`")
    st.markdown(f"**Placed at:** {datetime.fromtimestamp(latest_order['timestamp']).strftime('%H:%M:%S')}")
    st.markdown(f"**Status:** `{latest_order['status']}`")

    # Status progress bar
    status_stages = ["Pending", "Preparing", "Ready", "Completed"]
    current_stage_index = status_stages.index(latest_order["status"]) if latest_order["status"] in status_stages else 0

    progress = st.progress(0)
    for i in range(current_stage_index + 1):
        progress.progress((i + 1) / len(status_stages))

    # Cancel button (only if status is Pending)
    if latest_order["status"] == "Pending":
        if st.button("❌ Cancel Order"):
            updated_orders = [order for order in orders if order["id"] != latest_order["id"]]
            save_orders(updated_orders)
            st.success("🛑 Order canceled successfully.")
            st.rerun()
    else:
        st.info("ℹ️ Order can no longer be canceled.")

    # Auto-refresh every 5 seconds
    time.sleep(5)
    st.rerun()
else:
    st.info("🕐 No order placed for this table yet.")