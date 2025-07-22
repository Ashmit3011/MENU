# Save this as app.py
import json
import os
import uuid
import time
from datetime import datetime
import streamlit as st

# Setup
st.set_page_config(page_title="🍽️ Smart Table Ordering", layout="wide")
st.title("🍽️ Smart Table Ordering System")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# Load Menu
def load_menu():
    try:
        with open(MENU_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save Order
def save_order(order):
    orders = load_orders()
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Load Orders
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save Updated Orders
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Initialize
menu = load_menu()
st.session_state.setdefault("cart", {})
st.session_state.setdefault("table_number", "")
st.session_state.setdefault("last_status", "")

# Menu
if not menu:
    st.error("⚠️ Menu is empty!")
    st.stop()

selected_category = st.selectbox("Choose Category", sorted(set([item["category"] for item in menu])))
filtered = [item for item in menu if item["category"] == selected_category]

st.subheader("📋 Menu")
for item in filtered:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{item['name']}** - ₹{item['price']} {'🟢' if item['veg'] else '🔴'} {'🌶️' if item['spicy'] else ''}")
    with col2:
        qty = st.number_input(f"{item['name']}", min_value=0, step=1, key=item["id"])
        if qty > 0:
            st.session_state.cart[item['id']] = {"name": item['name'], "qty": qty, "price": item['price']}
        elif item['id'] in st.session_state.cart:
            del st.session_state.cart[item['id']]

# Cart
st.markdown("---")
st.subheader("🛒 Your Cart")
if st.session_state.cart:
    total = sum(i["qty"] * i["price"] for i in st.session_state.cart.values())
    for i in st.session_state.cart.values():
        st.write(f"{i['name']} x {i['qty']} = ₹{i['qty'] * i['price']}")
    st.success(f"Total: ₹{total}")
    st.text_input("Enter Table Number", key="table_number")
    if st.button("✅ Place Order"):
        if not st.session_state.table_number:
            st.warning("Please enter table number.")
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
            st.experimental_rerun()
else:
    st.info("Your cart is empty.")

# Track Order
st.markdown("---")
st.subheader("📦 Order Tracking")
if st.session_state.table_number:
    orders = [o for o in load_orders() if o['table'] == st.session_state.table_number]
    if not orders:
        st.info("No orders found.")
    else:
        latest = sorted(orders, key=lambda x: x['timestamp'], reverse=True)[0]
        st.write(f"🧾 Order ID: `{latest['id']}` | Status: **{latest['status']}**")
        status_index = ["Pending", "Preparing", "Ready", "Served"].index(latest["status"])
        st.progress((status_index + 1) / 4)
        st.caption(f"Placed at {datetime.fromtimestamp(latest['timestamp']).strftime('%I:%M %p')}")

        if st.session_state.last_status != latest["status"]:
            st.session_state.last_status = latest["status"]
            if os.path.exists("notification.wav"):
                st.audio("notification.wav", autoplay=True)
else:
    st.info("Enter table number to track your order.")

# Auto-refresh every 5 seconds
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 5000);
</script>
""", unsafe_allow_html=True)