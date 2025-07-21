import streamlit as st
import json
import os
import uuid
from datetime import datetime
from collections import defaultdict
from streamlit_autorefresh import st_autorefresh

# File paths (absolute or relative as per your deployment)
menu_file = os.path.abspath("menu.json")
orders_file = os.path.abspath("orders.json")

# Auto-refresh every 3 seconds
st_autorefresh(interval=3000, key="autorefresh")

# Page config
st.set_page_config(page_title="Smart Restaurant Ordering", layout="wide")

# Hide sidebar
st.markdown('<style>div[data-testid="stSidebar"]{display: none;}</style>', unsafe_allow_html=True)

# Inject custom CSS for better mobile layout
st.markdown("""
    <style>
    body { font-size: 16px; }
    .element-container { margin-bottom: 10px !important; }
    @media screen and (max-width: 768px) {
        .stButton > button { width: 100%; font-size: 16px; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Smart Table Ordering")

# Load menu from JSON
try:
    with open(menu_file, "r") as f:
        menu = json.load(f)
        if not isinstance(menu, list):
            st.error("Invalid menu format. Expected a list of items.")
            st.stop()
except Exception as e:
    st.error(f"Failed to load menu: {e}")
    st.stop()

# Group menu by category
categorized_menu = defaultdict(list)
for item in menu:
    categorized_menu[item["category"]].append(item)

# Initialize session state for cart
if "cart" not in st.session_state:
    st.session_state.cart = []

if "order_id" not in st.session_state:
    st.session_state.order_id = None

# Add item to cart
def add_to_cart(item):
    for existing in st.session_state.cart:
        if existing["id"] == item["id"]:
            existing["quantity"] += 1
            return
    st.session_state.cart.append({"id": item["id"], "name": item["name"], "price": item["price"], "quantity": 1})

# Display menu by category
for category, items in categorized_menu.items():
    st.markdown(f"### 🍱 {category}")
    for item in items:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"₹{item['price']}")
                st.caption(item["description"])
            with col2:
                if st.button("➕", key=f"add_{item['id']}"):
                    add_to_cart(item)
                    st.toast(f"Added {item['name']} to cart", icon="🛒")

# Cart display
st.markdown("---")
st.markdown("## 🛒 Your Cart")

if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        st.write(f"- {item['name']} × {item['quantity']} = ₹{item['price'] * item['quantity']}")
        total += item['price'] * item['quantity']
    st.write(f"**Total: ₹{total}**")
    table = st.text_input("Enter your table number:")
    if st.button("✅ Place Order"):
        if not table:
            st.warning("Please enter your table number.")
        else:
            order = {
                "id": str(uuid.uuid4()),
                "items": st.session_state.cart,
                "total": total,
                "table": table,
                "status": "Preparing",
                "timestamp": datetime.now().isoformat()
            }
            try:
                if os.path.exists(orders_file):
                    with open(orders_file, "r") as f:
                        orders = json.load(f)
                else:
                    orders = []
                orders.append(order)
                with open(orders_file, "w") as f:
                    json.dump(orders, f, indent=2)
                st.session_state.order_id = order["id"]
                st.session_state.cart = []
                st.success("✅ Order placed successfully!")
                st.toast("Order Placed!", icon="🚀")
            except Exception as e:
                st.error(f"Failed to save order: {e}")
else:
    st.info("Your cart is empty.")

# Track order
st.markdown("---")
st.markdown("## 📦 Track Your Order")
if st.session_state.order_id:
    try:
        with open(orders_file, "r") as f:
            orders = json.load(f)
        order = next((o for o in orders if o["id"] == st.session_state.order_id), None)
        if order:
            st.info(f"Your order status: **{order['status']}**")
            if order["status"] == "Served":
                st.success("✅ Your food has been served!")
                st.balloons()
    except Exception as e:
        st.error(f"Failed to read order status: {e}")
else:
    st.caption("Place an order to begin tracking.")
