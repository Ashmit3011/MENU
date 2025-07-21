import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 sec
st_autorefresh(interval=5000, key="admin_refresh")
st.set_page_config(page_title="Admin Panel", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"

if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

def load_orders():
    if ORDERS_FILE.exists():
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Toast and audio
st.markdown("""
    <style>
    .toast { position: fixed; bottom: 70px; right: 20px; background: #111; color: white; padding: 12px;
             border-radius: 8px; z-index: 9999; animation: fadeIn 0.5s ease-in-out;}
    @keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }
    </style>
""", unsafe_allow_html=True)
def toast(msg): st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)
def play_sound():
    st.markdown("""
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)

# Load & check orders
orders = sorted(load_orders(), key=lambda x: x["timestamp"], reverse=True)
if len(orders) > st.session_state.last_order_count:
    play_sound()
    toast("🔔 New order received!")
    st.session_state.last_order_count = len(orders)

st.title("📋 Admin Panel - Orders")
if not orders:
    st.info("No orders found.")
else:
    for order in orders:
        with st.container():
            st.markdown(f"### 🧾 Order `{order['id']}` | Table: {order['table']}")
            st.caption(datetime.fromtimestamp(order["timestamp"]).strftime("%b %d, %I:%M %p"))
            for item in order["items"].values():
                st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            st.success(f"Total: ₹{order['total']}")

            col1, col2 = st.columns([3, 1])
            status_list = ["Pending", "Preparing", "Ready", "Served"]
            with col1:
                new_status = st.selectbox("Status", status_list, index=status_list.index(order["status"]), key=f"status_{order['id']}")
            with col2:
                if st.button("Update", key=f"update_{order['id']}"):
                    order["status"] = new_status
                    save_orders(orders)
                    st.success("✅ Status updated.")
                    st.rerun()

            if order["status"] == "Served":
                if st.button("🗑️ Delete", key=f"delete_{order['id']}"):
                    orders = [o for o in orders if o["id"] != order["id"]]
                    save_orders(orders)
                    st.success("🗑️ Order deleted.")
                    st.rerun()