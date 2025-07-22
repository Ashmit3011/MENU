import streamlit as st
import json
import uuid
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------- INIT ----------
st.set_page_config(page_title="Smart Menu", page_icon="🍽️", layout="centered")

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'order_id' not in st.session_state:
    st.session_state.order_id = None
if 'table_number' not in st.session_state:
    st.session_state.table_number = None

# ---------- LOAD DATA ----------
def load_menu():
    with open('menu.json', 'r') as f:
        return json.load(f)

def load_orders():
    if not os.path.exists('orders.json'):
        with open('orders.json', 'w') as f:
            json.dump([], f)
    with open('orders.json', 'r') as f:
        return json.load(f)

def save_order(order_data):
    orders = load_orders()
    orders.append(order_data)
    with open('orders.json', 'w') as f:
        json.dump(orders, f, indent=2)

def get_order_status(order_id):
    orders = load_orders()
    for order in orders:
        if order["order_id"] == order_id:
            return order["status"]
    return "Not Found"

# ---------- UI FUNCTIONS ----------
def add_to_cart(item):
    st.session_state.cart.append(item)
    st.toast(f"✅ Added {item['name']} to cart", icon="🛒")

def render_menu():
    menu = load_menu()
    categories = sorted(set(item["category"] for item in menu))
    st.header("📋 Menu")
    for cat in categories:
        st.subheader(f"🍽️ {cat}")
        for item in filter(lambda x: x['category'] == cat, menu):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.text(f"{item['name']} - ${item['price']:.2f}")
            with col2:
                if st.button("Add", key=item["id"]):
                    add_to_cart(item)

def render_cart():
    st.header("🛒 Your Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        return

    total = 0
    for idx, item in enumerate(st.session_state.cart):
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
        with col1:
            st.write(item["name"])
        with col2:
            st.write(f"${item['price']:.2f}")
        with col3:
            if st.button("❌ Remove", key=f"remove_{idx}"):
                st.session_state.cart.pop(idx)
                st.experimental_rerun()
        total += item["price"]

    st.markdown(f"### Total: ${total:.2f}")
    
    st.session_state.table_number = st.number_input("Enter Table Number", min_value=1, max_value=50, step=1, key="table_input")
    if st.button("✅ Place Order"):
        if not st.session_state.table_number:
            st.warning("Please enter a table number.")
        else:
            order_id = str(uuid.uuid4())[:8].upper()
            order = {
                "order_id": order_id,
                "table": st.session_state.table_number,
                "items": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_order(order)
            st.session_state.order_id = order_id
            st.session_state.cart = []
            st.success(f"🎉 Order placed successfully! Order ID: {order_id}")
            st.balloons()
            st.experimental_rerun()

def render_status_tracker():
    st.header("📡 Track Your Order")
    if not st.session_state.order_id:
        st.info("No active order to track.")
        return
    
    st_autorefresh(interval=5000, limit=None, key="status_refresh")
    status = get_order_status(st.session_state.order_id)
    
    st.write(f"Order ID: `{st.session_state.order_id}`")
    with st.spinner("Checking order status..."):
        st.success(f"📦 Order Status: **{status}**")
        status_stages = ["Pending", "Preparing", "Ready", "Served"]
        current_stage = status_stages.index(status) if status in status_stages else -1

        for i, stage in enumerate(status_stages):
            if i <= current_stage:
                st.markdown(f"✅ {stage}")
            else:
                st.markdown(f"🔲 {stage}")
    
    if status == "Served":
        if st.button("Give Feedback"):
            st.session_state.order_id = None
            st.experimental_rerun()

# ---------- MAIN ----------
st.title("🍽️ Smart Menu System")

page = st.sidebar.radio("Navigate", ["Menu", "Cart", "Order Status"])

if page == "Menu":
    render_menu()

elif page == "Cart":
    render_cart()

elif page == "Order Status":
    render_status_tracker()
