import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# File paths
MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="app_autorefresh")

# Load menu items
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
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)

# UI
st.title("🍔 Smart Table Order")

# Table Number Input
table_number = st.number_input("Enter Table Number:", min_value=1, step=1)

menu = load_menu()
orders = load_orders()

# Show menu and take order
st.subheader("📋 Menu")
order_items = {}
for item in menu:
    qty = st.number_input(f"{item['name']} - ₹{item['price']}", min_value=0, step=1, key=item["id"])
    if qty > 0:
        order_items[item["id"]] = qty

# Submit order
if st.button("✅ Place Order"):
    if order_items:
        new_order = {
            "table": table_number,
            "items": order_items,
            "status": "Placed",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        save_orders(orders)
        st.success("Order placed successfully!")
    else:
        st.warning("Please select at least one item.")

# Show live status for this table
st.subheader("📡 Live Order Tracker")

table_orders = [order for order in orders if order["table"] == table_number]

if not table_orders:
    st.info("No orders yet for this table.")
else:
    for i, order in enumerate(table_orders):
        st.markdown(f"### 🧾 Order #{i+1} - Status: `{order['status']}`")
        for item_id, qty in order["items"].items():
            item_name = next((m['name'] for m in menu if m["id"] == item_id), "Unknown")
            st.markdown(f"- **{item_name}** x {qty}")

        # Cancel button for each active order
        if order["status"] not in ["Completed", "Cancelled"]:
            if st.button(f"❌ Cancel Order #{i+1}", key=f"cancel_{i}"):
                order["status"] = "Cancelled"
                order["cancelled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_orders(orders)
                st.warning("Order cancelled.")
                st.rerun()