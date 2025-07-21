import streamlit as st
import json
import os
import time
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="🛎️ Admin Panel", layout="wide")

# ---------- FILE PATH ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ---------- LOAD/SAVE ----------
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# ---------- STYLING + SOUND ----------
st.markdown("""
    <style>
        .toast {
            position: fixed;
            bottom: 70px;
            right: 20px;
            background-color: #008000;
            color: white;
            padding: 16px;
            border-radius: 10px;
            z-index: 10000;
            animation: slideIn 0.5s ease-out;
            font-size: 18px;
        }
        @keyframes slideIn {
            0% {opacity: 0; transform: translateY(20px);}
            100% {opacity: 1; transform: translateY(0);}
        }
    </style>

    <script>
        const newOrderSound = new Audio("https://www.soundjay.com/buttons/beep-07.wav");
        if (!window.prevOrderCount) window.prevOrderCount = 0;

        const checkOrders = async () => {
            const response = await fetch(window.location.href);
            const text = await response.text();
            const count = (text.match(/🧾 Order ID/g) || []).length;

            if (count > window.prevOrderCount) {
                newOrderSound.play();
            }
            window.prevOrderCount = count;
        };

        setInterval(checkOrders, 4000);
    </script>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.title("🛎️ Admin Panel – Live Orders")

orders = load_orders()
orders = sorted(orders, key=lambda x: x["timestamp"], reverse=True)
now = time.time()

if not orders:
    st.info("No orders yet.")
else:
    for i, order in enumerate(orders):
        is_recent = (now - order["timestamp"]) < 120  # 2 mins
        color = "#ffeeba" if is_recent else "#f8f9fa"

        with st.container():
            st.markdown(
                f"""
                <div style='background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px'>
                    <h4>🧾 Order ID: {order['id']} | Table: {order['table']}</h4>
                    <p>Status: <b>{order['status']}</b> &nbsp;&nbsp; | &nbsp;&nbsp; 
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

# ---------- AUTO REFRESH ----------
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 10000);
</script>
""", unsafe_allow_html=True)
