import streamlit as st
import json
import os
import time
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Admin Panel", layout="wide")

# ---------- FILE PATHS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "../orders.json")

# ---------- LOAD ORDERS ----------
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# ---------- SAVE ORDERS ----------
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# ---------- STYLE ----------
st.markdown("""
    <style>
        .order-card {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 0 8px rgba(0,0,0,0.4);
        }
        .order-header {
            font-weight: bold;
            font-size: 18px;
        }
        .completed {
            opacity: 0.4;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #222;
            color: white;
            padding: 16px;
            border-radius: 10px;
            z-index: 10000;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            0% {opacity: 0; transform: translateY(20px);}
            100% {opacity: 1; transform: translateY(0);}
        }
    </style>
""", unsafe_allow_html=True)

def toast(msg):
    st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)

# ---------- SOUND FOR NEW ORDER ----------
new_order_sound = """
<audio autoplay>
  <source src="https://www.soundjay.com/buttons/sounds/button-29.mp3" type="audio/mpeg">
</audio>
"""

def play_sound():
    st.markdown(new_order_sound, unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

# ---------- DISPLAY ORDERS ----------
st.title("📋 Orders")

orders = load_orders()
orders = sorted(orders, key=lambda x: x['timestamp'], reverse=True)

if len(orders) > st.session_state.last_order_count:
    play_sound()
    toast("🔔 New order received!")
    st.session_state.last_order_count = len(orders)

if not orders:
    st.info("No orders found.")

for i, order in enumerate(orders):
    card_class = "order-card"
    if order["status"] == "Served":
        card_class += " completed"

    with st.container():
        st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
        st.markdown(f"<div class='order-header'>🧾 Order ID: {order['id']} | Table: {order['table']}</div>", unsafe_allow_html=True)
        status_time = datetime.fromtimestamp(order['timestamp']).strftime("%I:%M %p")
        st.caption(f"Status: {order['status']} | Placed at {status_time}")

        for item in order["items"].values():
            st.markdown(f"- **{item['name']}** x {item['qty']} = ₹{item['qty'] * item['price']}")

        col1, col2 = st.columns([4, 1])
        with col1:
            new_status = st.selectbox("Update Status", ["Pending", "Preparing", "Ready", "Served"], index=["Pending", "Preparing", "Ready", "Served"].index(order["status"]), key=f"status_{i}")
            if new_status != order["status"]:
                orders[i]["status"] = new_status
                save_orders(orders)
                st.experimental_rerun()

        with col2:
            if order["status"] == "Served"]:
                if st.button("🗑️ Delete", key=f"del_{i}"):
                    orders.pop(i)
                    save_orders(orders)
                    toast("✅ Order deleted")
                    st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- AUTO REFRESH ----------
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 3000);
</script>
""", unsafe_allow_html=True)
