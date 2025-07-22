import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ✅ Custom Toast using HTML
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

# ✅ File Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")

# ✅ Load Menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error("❌ menu.json not found.")
    st.stop()

# ✅ Load Orders
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# ✅ Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="autorefresh_admin")

# ✅ Header
st.markdown("## 🛠️ <span style='color:white;'>Admin Panel - Order Management</span>", unsafe_allow_html=True)
st.markdown("### 📦 <span style='color:white;'>All Orders</span>", unsafe_allow_html=True)

changed = False

# ✅ Display Orders
for idx, order in reversed(list(enumerate(orders))):
    with st.container():
        st.markdown(
            f"""
            <div style="border: 1px solid #444; border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #222;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>🪑 Table {order['table']}</strong>
                    <span style="background-color: #444; color: white; padding: 2px 8px; border-radius: 12px;">{order['status'].capitalize()}</span>
                </div>
                <div style="font-size: 12px; color: #ccc;">⏰ {order['timestamp']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ✅ Display items in order
        for item in order["items"]:
            try:
                price = int(item["price"])
                qty = int(item["quantity"])
                total = price * qty
                st.markdown(f"🍴 <b>{item['name']}</b> x {qty} = ₹{total}", unsafe_allow_html=True)
            except (ValueError, KeyError, TypeError):
                st.warning("⚠️ Invalid item data.")

        # ✅ Status control buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if order["status"] == "Pending" and st.button("👨‍🍳 Preparing", key=f"prep-{idx}"):
                orders[idx]["status"] = "Preparing"
                changed = True
                custom_toast(f"🍳 Order for Table {order['table']} is now Preparing")

        with col2:
            if order["status"] == "Preparing" and st.button("✅ Complete", key=f"complete-{idx}"):
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
                custom_toast(f"🗑️ Deleted order for Table {order['table']}")
                st.rerun()

        st.markdown("---")

# ✅ Save updated orders
if changed:
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.success("✅ Order status updated.")
