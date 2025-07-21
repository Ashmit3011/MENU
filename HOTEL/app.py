import streamlit as st
import json
import uuid
import time
from datetime import datetime
import os

st.set_page_config(page_title="Smart Table Ordering", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# Load menu
def load_menu():
    try:
        with open(MENU_FILE, "r") as f:
            menu = json.load(f)
            assert isinstance(menu, list)
            return menu
    except Exception as e:
        return []

# Save order
def save_order(order):
    try:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Load orders
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Toast notification
st.markdown("""
    <style>
        .toast {
            position: fixed;
            bottom: 70px;
            right: 20px;
            background-color: #333;
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

# --- APP LOGIC ---
menu = load_menu()
st.title("🍽️ Smart Table Ordering")

if not menu:
    st.error("❌ Menu is empty or incorrectly formatted. Please check back later.")
    st.stop()

# --- FILTERED DISPLAY ---
categories = sorted(set(item["category"] for item in menu))
st.subheader("📋 Menu")
tab1, tab2, tab3 = st.columns(3)
st.session_state.setdefault("cart", {})
st.session_state.setdefault("table_number", "")

selected_category = st.selectbox("Select a category", categories)
filtered_menu = [item for item in menu if item["category"] == selected_category]

for item in filtered_menu:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{item['name']}**")
        st.caption(f"₹{item['price']} | {'🌶️' if item['spicy'] else ''} {'🟢' if item['veg'] else '🔴'}")
    with col2:
        qty = st.number_input(f"Qty - {item['id']}", min_value=0, step=1, key=item['id'])
        if qty > 0:
            st.session_state.cart[item['id']] = {"name": item['name'], "qty": qty, "price": item['price']}
        elif item['id'] in st.session_state.cart:
            del st.session_state.cart[item['id']]

# --- CART ---
st.markdown("---")
st.subheader("🛒 Your Cart")
if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for item in st.session_state.cart.values():
        st.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']
    st.success(f"Total: ₹{total}")

    st.text_input("Enter your table number", key="table_number")
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
            

# --- ORDER TRACKING ---
st.markdown("---")
st.subheader("📦 Track Your Order")
user_orders = [o for o in load_orders() if o['table'] == st.session_state.table_number]
user_orders = sorted(user_orders, key=lambda x: x['timestamp'], reverse=True)

if not user_orders:
    st.info("Place an order to begin tracking.")
else:
    latest = user_orders[0]
    st.write(f"🧾 Order ID: {latest['id']} | Status: **{latest['status']}**")
    order_time = datetime.fromtimestamp(latest['timestamp']).strftime("%I:%M %p")
    st.caption(f"Placed at {order_time}")

    st.progress(["Pending", "Preparing", "Ready", "Served"].index(latest['status']) / 3)

# --- SMOOTH REFRESH ---
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)
