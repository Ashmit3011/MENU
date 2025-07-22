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
            animation: fadein 0.5s, fadeout 0.5s ${duration / 1000 - 0.5}s;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), {duration});
        </script>
        """,
        unsafe_allow_html=True
    )

# File paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
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
st_autorefresh(interval=5000, key="admin_refresh")

# Page header
st.markdown("## 🛠️ Admin Panel - Order Management")
st.markdown("### 📦 All Orders")

changed = False

for idx, order in reversed(list(enumerate(orders))):
    with st.container():
        with st.expander(f"🪑 Table {order['table']} — ⏰ {order['timestamp']} — **{order['status']}**", expanded=True):
            # Order items
            for name, item in order["items"].items():
                st.markdown(f"🍴 **{name}** x {item['quantity']} = ₹{item['price'] * item['quantity']}")

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if order["status"] == "Pending":
                    if st.button("👨‍🍳 Preparing", key=f"prep-{idx}"):
                        orders[idx]["status"] = "Preparing"
                        changed = True
                        custom_toast(f"🍳 Order for Table {order['table']} is now Preparing")

                elif order["status"] == "Preparing":
                    if st.button("✅ Complete", key=f"comp-{idx}"):
                        orders[idx]["status"] = "Completed"
                        changed = True
                        custom_toast(f"✅ Order for Table {order['table']} marked as Completed")

            with col2:
                if order["status"] not in ["Completed", "Cancelled"]:
                    if st.button("❌ Cancel", key=f"cancel-{idx}"):
                        orders[idx]["status"] = "Cancelled"
                        changed = True
                        custom_toast(f"❌ Order for Table {order['table']} Cancelled")

            with col3:
                if order["status"] in ["Completed", "Cancelled"]:
                    if st.button("🗑️ Delete", key=f"delete-{idx}"):
                        del orders[idx]
                        with open(ORDERS_FILE, "w") as f:
                            json.dump(orders, f, indent=2)
                        custom_toast(f"🗑️ Deleted order for Table {order['table']}")
                        st.rerun()

        st.markdown("---")

# Save updated order statuses
if changed:
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.success("✅ Order status updated.")
