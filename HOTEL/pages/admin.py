import streamlit as st
import json
import os
import time
from datetime import datetime

# Set up page
st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🧑‍🍳 Admin Panel - Order Management")

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# Load orders
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

# Save orders
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Update order status
def update_order_status(order_id, new_status):
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["status"] = new_status
    save_orders(orders)

# Cancel order
def cancel_order(order_id):
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["status"] = "Cancelled"
    save_orders(orders)

# Delete completed orders
def delete_completed_orders():
    orders = load_orders()
    orders = [order for order in orders if order["status"] != "Completed"]
    save_orders(orders)

# Action to delete all completed
if st.button("🗑️ Delete Completed Orders"):
    delete_completed_orders()
    st.success("✅ Completed orders deleted.")
    st.rerun()

# Show Orders
orders = load_orders()
if not orders:
    st.info("No orders yet.")
else:
    for order in orders[::-1]:  # Show latest first
        status_color = {
            "Pending": "orange",
            "Preparing": "blue",
            "Completed": "green",
            "Cancelled": "red"
        }.get(order["status"], "black")

        with st.container():
            st.markdown(f"### 🧾 Order ID: {order['id']}")
            st.markdown(f"**Table:** {order['table']} | **Status:** :{status_color}[{order['status']}]")
            st.markdown(f"_Placed at: {datetime.fromtimestamp(order['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}_")

            if order["status"] == "Cancelled":
                st.markdown("~~This order was cancelled.~~")
            else:
                for name, item in order["items"].items():
                    st.markdown(f"- {name} x {item['quantity']} = ₹{item['price'] * item['quantity']}")

            st.markdown(f"**Total: ₹{order['total']}**")

            # Buttons for status update
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🔄 Preparing", key=f"prep_{order['id']}"):
                    update_order_status(order["id"], "Preparing")
                    st.rerun()
            with col2:
                if st.button("✅ Complete", key=f"done_{order['id']}"):
                    update_order_status(order["id"], "Completed")
                    st.rerun()
            with col3:
                if st.button("❌ Cancel", key=f"cancel_{order['id']}"):
                    cancel_order(order["id"])
                    st.rerun()
            st.markdown("---")