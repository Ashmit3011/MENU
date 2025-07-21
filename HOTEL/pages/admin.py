import streamlit as st
import json
import os
import time
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="🛎️ Admin Panel", layout="wide")

# --- FILE PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "..", "orders.json")

# --- LOAD / SAVE ---
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# --- INIT SESSION ---
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

# --- LOAD ORDERS ---
orders = load_orders()
orders = sorted(orders, key=lambda x: x["timestamp"], reverse=True)
current_order_count = len(orders)
now = time.time()

# --- TITLE ---
st.title("🛎️ Orders")

# --- TOAST + SOUND on new order ---
if current_order_count > st.session_state.last_order_count:
    st.session_state.last_order_count = current_order_count

    st.markdown("""
        <div id="toast" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #4BB543;
            color: white;
            padding: 16px 24px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            font-size: 18px;
            z-index: 10000;
            animation: slideIn 0.5s ease-out;
        ">
            🔔 New order received!
        </div>
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/sounds/button-10.mp3" type="audio/mpeg">
        </audio>
        <script>
            setTimeout(() => {
                const toast = document.getElementById("toast");
                if (toast) toast.style.display = "none";
            }, 3000);
        </script>
        <style>
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
    """, unsafe_allow_html=True)

# --- DISPLAY ORDERS ---
any_orders = False

for i, order in enumerate(orders):
    is_recent = (now - order["timestamp"]) < 120
    bg_color = "#fff4d2" if is_recent else "#f4f4f4"
    text_color = "#000000"

    with st.container():
        st.markdown(
            f"""
            <div style='background-color:{bg_color}; color:{text_color}; padding:20px; 
                         border-radius:12px; margin-bottom:16px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);'>
                <h4 style='margin:0;'>🧾 Order ID: {order['id']} | Table: {order['table']}</h4>
                <p style='margin-top:8px;'>Status: <b>{order['status']}</b> &nbsp;|&nbsp; 
                Placed: {datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')}</p>
            """,
            unsafe_allow_html=True
        )

        for item in order["items"].values():
            st.markdown(f"- **{item['name']}** x {item['qty']} = ₹{item['qty'] * item['price']}")

        status = st.selectbox(
            "Update Status",
            ["Pending", "Preparing", "Ready", "Served"],
            index=["Pending", "Preparing", "Ready", "Served"].index(order["status"]),
            key=f"status_{i}"
        )

        if status != order["status"]:
            order["status"] = status
            save_orders(orders)
            st.rerun()

        if order["status"] == "Served":
            if st.button(f"🗑️ Delete Order {order['id']}", key=f"delete_{i}"):
                orders.pop(i)
                save_orders(orders)
                st.success(f"Deleted Order {order['id']}")
                st.rerun()

        st.markdown("---")
        any_orders = True

if not any_orders:
    st.info("No orders yet.")

# --- AUTO REFRESH ---
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 10000);
</script>
""", unsafe_allow_html=True)
