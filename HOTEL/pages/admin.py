import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# Paths
MENU_FILE = os.path.join(os.path.dirname(__file__), "..", "menu.json")
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "..", "orders.json")

# Load orders
def load_orders():
    if Path(ORDERS_FILE).exists():
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

# Save orders
def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Emoji icons
status_colors = {
    "pending": "gray",
    "preparing": "orange",
    "completed": "green",
    "cancelled": "red"
}

st.markdown("### 🛠️ Admin Panel - Order Management")
st.markdown("## 📦 All Orders")

orders = load_orders()

if not orders:
    st.info("No orders yet.")
else:
    for i, order in enumerate(orders):
        with st.container():
            st.markdown(
                f"""
                <div style='border:1px solid #444; border-radius:10px; padding:10px; margin-bottom:10px; background-color:#1f1f1f;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <span>🍽️ <strong>Table {order['table']}</strong></span>
                        <span style='background-color:{status_colors[order["status"]]}; color:white; padding:2px 10px; border-radius:10px; font-size:12px;'>
                            {order["status"].capitalize()}
                        </span>
                    </div>
                    <div style='color:gray; font-size:13px; margin-top:2px;'>🕒 {order["timestamp"]}</div>
                    <hr style='border-top:1px solid #333;'/>
            """,
                unsafe_allow_html=True
            )

            for item in order["items"]:
                st.markdown(f"🍴 <b>{item['name']}</b> x {item['quantity']} = ₹{item['price'] * item['quantity']}", unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🧑‍🍳 Preparing", key=f"prepare_{i}"):
                    orders[i]["status"] = "preparing"
                    save_orders(orders)
                    st.experimental_rerun()
            with col2:
                if st.button("✅ Complete", key=f"complete_{i}"):
                    orders[i]["status"] = "completed"
                    save_orders(orders)
                    st.experimental_rerun()
            with col3:
                if st.button("❌ Cancel", key=f"cancel_{i}"):
                    orders[i]["status"] = "cancelled"
                    save_orders(orders)
                    st.experimental_rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    orders.pop(i)
                    save_orders(orders)
                    st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)
