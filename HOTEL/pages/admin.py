import streamlit as st
import json
import os
import time
from datetime import datetime
from pathlib import Path

# === File Paths ===
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
MENU_FILE = BASE_DIR / "menu.json"

# === Streamlit Page Config ===
st.set_page_config(page_title="🛎️ Admin Panel", layout="centered")

# === Style ===
st.markdown("""
    <style>
        .order-box {
            background: #111111dd;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .status-pending { color: orange; font-weight: bold; }
        .status-preparing { color: deepskyblue; font-weight: bold; }
        .status-ready { color: yellowgreen; font-weight: bold; }
        .status-served { color: lightgreen; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# === Load Data ===
def load_orders():
    if not ORDERS_FILE.exists():
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f)
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === State ===
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0
if "played_sound" not in st.session_state:
    st.session_state.played_sound = False

# === Header ===
st.title("🛎️ Admin Dashboard")

# === Load and Show Orders ===
orders = load_orders()
orders.sort(key=lambda x: x["time"], reverse=True)

# === Alert New Order ===
if len(orders) > st.session_state.last_order_count:
    st.toast("🔔 New order received!", icon="🍽️")
    st.audio("https://www.soundjay.com/buttons/beep-07.wav", autoplay=True)
    st.session_state.last_order_count = len(orders)

if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        with st.container():
            status_class = f"status-{order['status'].lower()}"
            st.markdown(f"""
                <div class="order-box">
                    <strong>🆔 Order ID:</strong> {order['id']}<br>
                    <strong>🪑 Table:</strong> {order['table']}<br>
                    <strong>📅 Time:</strong> {order['time']}<br>
                    <strong>📦 Status:</strong> <span class="{status_class}">{order['status']}</span><br><br>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🧾 Items")
            for item in order["items"]:
                st.markdown(f"- {item['name']} x {item['qty']} (₹{item['price'] * item['qty']})")

            st.markdown(f"**💰 Total: ₹{order['total']}**")

            # === Status Buttons ===
            col1, col2, col3, col4 = st.columns(4)
            statuses = ["Pending", "Preparing", "Ready", "Served"]
            current_idx = statuses.index(order["status"])

            if current_idx < 3:
                with col2:
                    if st.button(f"➡️ Mark as {statuses[current_idx + 1]}", key=f"{order['id']}_next"):
                        order["status"] = statuses[current_idx + 1]
                        save_orders(orders)
                        st.experimental_rerun()
            else:
                with col2:
                    st.success("✅ Completed")

            st.markdown("---")

# === Auto Refresh ===
time.sleep(5)
st.rerun()
