# app.py (Customer Interface)
import streamlit as st
import json
import uuid
import time
from datetime import datetime
import os
from streamlit_autorefresh import st_autorefresh

# -------------- CONFIG --------------
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# -------------- FILE PATHS --------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# -------------- DATA FUNCTIONS --------------
def load_menu():
    try:
        with open(MENU_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_order(order):
    try:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# -------------- TOAST + STYLE --------------
st.markdown("""
    <style>
        .toast {
            position: fixed;
            bottom: 70px;
            right: 20px;
            background-color: #444;
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
        [data-testid="stSidebar"], [data-testid="stToolbar"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

def toast(msg):
    st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)
    st.audio("https://www.soundjay.com/buttons/sounds/button-3.mp3", autoplay=True)

# -------------- SESSION STATE --------------
st.session_state.setdefault("cart", {})
st.session_state.setdefault("table_number", "")

# -------------- AUTO REFRESH --------------
st_autorefresh(interval=5000, limit=None, key="auto_refresh")

# -------------- LOAD MENU --------------
menu = load_menu()
st.title("🍽️ Smart Table Ordering")

if not menu:
    st.error("❌ Menu is empty or not loaded properly.")
    st.stop()

# -------------- TABS --------------
tab_menu, tab_cart, tab_track = st.tabs(["📋 Menu", "🛒 Cart", "📦 Track Order"])

# -------------- MENU TAB --------------
with tab_menu:
    for category, items in menu.items():
        st.markdown(f"### 🍽️ {category}")
        for item in items:
            col1, col2 = st.columns([4, 1])
            with col1:
                veg_icon = "🟢" if item.get("veg") else "🔴"
                spice_icon = "🌶️" if item.get("spicy") else ""
                st.markdown(f"**{item['name']}**")
                st.caption(f"₹{item['price']} {veg_icon} {spice_icon}")
            with col2:
                qty = st.number_input(f"Qty - {item['id']}", min_value=0, step=1, key=f"qty_{item['id']}")
                if qty > 0:
                    st.session_state.cart[item['id']] = {
                        "name": item['name'],
                        "qty": qty,
                        "price": item['price']
                    }
                elif item['id'] in st.session_state.cart:
                    del st.session_state.cart[item['id']]

# -------------- CART TAB --------------
with tab_cart:
    st.subheader("🛒 Your Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        total = 0
        for item in st.session_state.cart.values():
            st.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            total += item['qty'] * item['price']
        st.success(f"Total: ₹{total}")

        table_input = st.text_input("Enter your table number", key="table_input")
        if table_input:
            st.session_state.table_number = table_input

        if st.button("✅ Place Order"):
            if not st.session_state.table_number:
                st.warning("Please enter a table number.")
            else:
                order = {
                    "id": str(uuid.uuid4())[:8],
                    "table": st.session_state.table_number,
                    "items": st.session_state.cart,
                    "total": total,
                    "status": "Pending",
                    "timestamp": time.time()
                }
                save_order(order)
                st.session_state.cart = {}
                toast("✅ Order placed successfully!")

# -------------- TRACKING TAB --------------
with tab_track:
    st.subheader("📦 Track Your Order")
    if not st.session_state.table_number:
        st.info("Please enter your table number in the Cart tab.")
    else:
        orders = load_orders()
        user_orders = [o for o in orders if o["table"] == st.session_state.table_number]
        user_orders = sorted(user_orders, key=lambda x: x['timestamp'], reverse=True)

        if not user_orders:
            st.info("No orders found for your table.")
        else:
            latest = user_orders[0]
            st.write(f"🧾 Order ID: `{latest['id']}` | Status: **{latest['status']}**")
            order_time = datetime.fromtimestamp(latest['timestamp']).strftime("%I:%M %p")
            st.caption(f"🕒 Placed at {order_time}")
            status_index = ["Pending", "Preparing", "Ready", "Served"].index(latest['status'])
            st.progress(status_index / 3)
