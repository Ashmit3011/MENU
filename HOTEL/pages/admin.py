import streamlit as st
import json
import os
from datetime import datetime

# === FILE PATHS USING BASE_DIR ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")

# === LOAD/SAVE FUNCTIONS ===
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r") as f:
            return json.load(f)
    return {}

# === STREAMLIT SETUP ===
st.set_page_config(page_title="Admin - Kitchen View", layout="wide")
st.title("👨‍🍳 Kitchen Admin Panel")

st.markdown("Real-time order tracking. Page auto-refreshes every 5 seconds.")
st.markdown("---")

orders = load_orders()
menu = load_menu()

status_colors = {
    "Pending": "orange",
    "Preparing": "blue",
    "Ready": "green",
    "Served": "gray"
}

# === ORDER DISPLAY AND STATUS ACTIONS ===
for idx, order in enumerate(reversed(orders)):  # Latest orders first
    with st.container():
        st.markdown(f"### 🧾 Table {order['table']} • `{order['status']}`")
        st.markdown(f"_⏰ Time: {order['time']}_")
        for item in order["items"]:
            st.markdown(f"- {item['name']} x {item['qty']}")
        st.markdown(f"💰 **Total: ₹{order['total']}**")

        col1, col2, col3 = st.columns(3)
        if st.session_state.get(f"status_{idx}") is None:
            st.session_state[f"status_{idx}"] = order["status"]

        with col1:
            if st.button("Preparing", key=f"prep_{idx}"):
                orders[-(idx+1)]["status"] = "Preparing"
                save_orders(orders)
                st.experimental_rerun()
        with col2:
            if st.button("Ready", key=f"ready_{idx}"):
                orders[-(idx+1)]["status"] = "Ready"
                save_orders(orders)
                st.experimental_rerun()
        with col3:
            if st.button("Served", key=f"served_{idx}"):
                orders[-(idx+1)]["status"] = "Served"
                save_orders(orders)
                st.experimental_rerun()

        st.markdown(f"<hr style='border:1px solid {status_colors[order['status']]};'/>", unsafe_allow_html=True)

# === AUTO REFRESH SCRIPT ===
st.markdown("<script>setTimeout(() => location.reload(), 5000);</script>", unsafe_allow_html=True)
