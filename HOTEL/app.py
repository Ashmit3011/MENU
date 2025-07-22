import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- Auto Refresh every 5 seconds ---
st_autorefresh(interval=5000, key="autorefresh")

# --- Page Config ---
st.set_page_config(page_title="Smart Table Ordering", layout="centered")
st.title("📲 Smart Table Ordering System")

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'menu_files')
MENU_FILE = os.path.join(DATA_DIR, 'menu.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

# --- Load Menu ---
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, 'r') as f:
            return json.load(f)
    return []

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

# --- Load ---
menu = load_menu()
orders = load_orders()

if not menu:
    st.error("❌ Menu not found or empty. Please check `menu.json` in menu_files.")
    st.stop()

# --- Table Number ---
table_number = st.selectbox("Select Table Number", [f"Table {i}" for i in range(1, 11)])

# --- Select Items ---
st.subheader("📝 Menu")
cart = {}

for item in menu:
    col1, col2 = st.columns([6, 2])
    with col1:
        st.markdown(f"**{item['name']}** - ₹{item['price']}")
    with col2:
        qty = st.number_input(
            label="Qty",
            min_value=0,
            max_value=10,
            step=1,
            key=item['id']
        )
        if qty > 0:
            cart[item['id']] = {
                "name": item["name"],
                "price": item["price"],
                "qty": qty
            }

# --- Place Order Button ---
if st.button("✅ Place Order"):
    if not cart:
        st.warning("🛒 Cart is empty!")
    else:
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
        st.success(f"✅ Order `{order_id}` placed successfully!")
        st.balloons()
        st.rerun()

# --- Live Order Tracking per Table ---
st.divider()
st.subheader("📦 Your Table's Orders")

table_orders = [o for o in orders if o.get("table") == table_number and o.get("status") != "Cancelled"]

if not table_orders:
    st.info("No active orders for this table.")
else:
    for order in sorted(table_orders, key=lambda x: x["timestamp"], reverse=True):
        st.markdown(f"**Order ID:** `{order['id']}`")
        st.markdown(f"🕒 Time: {datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')}")
        st.markdown(f"📌 Status: **{order['status']}**")

        with st.expander("View Items"):
            for item in order["items"].values():
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

        # Cancel option
        if order["status"] == "Pending":
            if st.button(f"❌ Cancel Order `{order['id']}`", key=f"cancel_{order['id']}"):
                order["status"] = "Cancelled"
                save_orders(orders)
                st.success(f"Order `{order['id']}` cancelled.")
                st.rerun()