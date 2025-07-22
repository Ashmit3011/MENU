import streamlit as st
import json, os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"

st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.title("🍽️ Smart Table Ordering System")

# Load menu
def load_menu():
    if not os.path.exists(MENU_FILE):
        return []
    with open(MENU_FILE, "r") as f:
        return json.load(f)

# Load orders
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

# Save orders
def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

menu = load_menu()
orders = load_orders()

table_no = st.selectbox("Select your Table Number", list(range(1, 11)), index=0)
selected_items = st.multiselect("Select Menu Items", [item["name"] for item in menu])

if st.button("✅ Place Order") and selected_items:
    new_order = {
        "table": table_no,
        "items": selected_items,
        "status": "Received",
        "time": datetime.now().strftime("%H:%M:%S")
    }
    orders.append(new_order)
    save_orders(orders)
    st.success("Order placed successfully!")

# Display live order status for current table
st.subheader("📦 Live Order Tracker")
for order in orders:
    if order["table"] == table_no:
        st.write(f"🧾 Order at {order['time']}")
        st.write("Items:", ", ".join(order["items"]))
        st.progress(["Received", "Preparing", "Ready", "Completed"].index(order["status"]) / 3)
        st.info(f"Current Status: {order['status']}")

        if order["status"] not in ["Completed", "Cancelled"]:
            if st.button(f"❌ Cancel Order (Table {table_no})", key=str(order)+str(table_no)):
                order["status"] = "Cancelled"
                save_orders(orders)
                st.warning("Order cancelled.")