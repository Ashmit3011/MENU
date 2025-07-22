import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 🚀 Custom toast using HTML
def custom_toast(message: str, duration: int = 3000):
    st.markdown(
        f"""
        <script>
        const toast = document.createElement("div");
        toast.textContent = "{message}";
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #323232;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-size: 14px;
            z-index: 9999;
            animation: fadein 0.5s, fadeout 0.5s {duration / 1000 - 0.5}s;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), {duration});
        </script>
        """,
        unsafe_allow_html=True
    )

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")

# Load menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error(f"❌ Menu file not found at {MENU_FILE}")
    st.stop()

# Load orders
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="admin_autorefresh")

st.markdown("### 🛠️ Admin Panel - Order Management")
st.subheader("📦 All Orders")

changed = False

for idx, order in reversed(list(enumerate(orders))):
    st.markdown(
        f"### Table {order['table']} — {order['status']} — ⏰ {order['timestamp']}"
    )
    for name, item in order["items"].items():
        st.markdown(f"- {name} x {item['quantity']} = ₹{item['price'] * item['quantity']}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if order["status"] == "Pending" and st.button("👨‍🍳 Mark Preparing", key=f"prep-{idx}"):
            orders[idx]["status"] = "Preparing"
            changed = True
            custom_toast(f"🍳 Order for Table {order['table']} is now Preparing")

    with col2:
        if order["status"] == "Preparing" and st.button("✅ Complete", key=f"comp-{idx}"):
            orders[idx]["status"] = "Completed"
            changed = True
            custom_toast(f"✅ Order for Table {order['table']} marked as Completed")

    with col3:
        if order["status"] not in ["Completed", "Cancelled"] and st.button("❌ Cancel", key=f"cancel-{idx}"):
            orders[idx]["status"] = "Cancelled"
            changed = True
            custom_toast(f"❌ Order for Table {order['table']} Cancelled")

    with col4:
        if order["status"] == "Completed" and st.button("🗑️ Delete", key=f"delete-{idx}"):
            del orders[idx]
            with open(ORDERS_FILE, "w") as f:
                json.dump(orders, f, indent=2)
            custom_toast(f"🗑️ Deleted completed order for Table {order['table']}")
            st.rerun()

    st.markdown("---")

# Save updates
if changed:
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.success("✅ Order status updated.")
