import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# ---------- AUTO REFRESH ----------
st_autorefresh(interval=5000, key="adminrefresh")

# ---------- CONFIG ----------
st.set_page_config(page_title="Admin Panel", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"

# ---------- STATE ----------
if "last_count" not in st.session_state:
    st.session_state.last_count = 0

# ---------- LOAD DATA ----------
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

orders = load_orders()
orders = sorted(orders, key=lambda x: x['timestamp'], reverse=True)

# ---------- STYLE ----------
st.markdown("""
    <style>
        .toast {
            position: fixed;
            bottom: 60px;
            right: 20px;
            background-color: #222;
            color: white;
            padding: 14px;
            border-radius: 8px;
            z-index: 9999;
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(10px);}
            to {opacity: 1; transform: translateY(0);}
        }
    </style>
""", unsafe_allow_html=True)

def toast(msg):
    st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)

def play_sound():
    st.markdown("""
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/sounds/button-16.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)

# ---------- ALERT ON NEW ----------
if len(orders) > st.session_state.last_count:
    toast("🔔 New Order!")
    play_sound()
    st.session_state.last_count = len(orders)

# ---------- UI ----------
st.title("📋 Admin Panel")
if not orders:
    st.info("No orders yet.")
else:
    for order in orders:
        st.markdown(f"### 🧾 Order ID: `{order['id']}` | Table: {order['table']}")
        st.caption("Placed: " + datetime.fromtimestamp(order["timestamp"]).strftime("%b %d, %I:%M %p"))

        for item in order["items"].values():
            st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")

        st.success(f"Total: ₹{order['total']}")
        col1, col2 = st.columns([2, 1])

        with col1:
            new_status = st.selectbox("Update Status", ["Pending", "Preparing", "Ready", "Served"],
                                      index=["Pending", "Preparing", "Ready", "Served"].index(order["status"]),
                                      key=order["id"])
        with col2:
            if st.button("Update", key=f"update_{order['id']}"):
                order["status"] = new_status
                save_orders(orders)
                st.success("Status updated.")

        if order["status"] == "Served":
            if st.button("🗑 Delete", key=f"del_{order['id']}"):
                orders = [o for o in orders if o["id"] != order["id"]]
                save_orders(orders)
                st.success("Order deleted.")
                st.rerun()
