# app.py
import streamlit as st
import json
import os
import time
from uuid import uuid4
from streamlit_autorefresh import st_autorefresh

# ------------ SETUP ------------
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ------------ AUTO REFRESH ------------
st_autorefresh(interval=5000, key="app_refresh")

# ------------ LOAD MENU ------------
def load_menu():
    try:
        with open(MENU_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

menu = load_menu()
if not menu:
    st.error("Menu could not be loaded.")
    st.stop()

# ------------ SESSION STATE ------------
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "table" not in st.session_state:
    st.session_state.table = ""

# ------------ UI ------------
st.title("🍽️ Smart Table Ordering")

st.text_input("Enter Table Number", key="table")

st.header("📋 Menu")

for category, items in menu.items():
    st.subheader(category)
    for item in items:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item['name']}** - ₹{item['price']}")
        with col2:
            qty = st.number_input(
                f"Qty_{item['id']}", min_value=0, step=1, label_visibility="collapsed", key=f"{item['id']}_qty")
            if qty > 0:
                st.session_state.cart[item['id']] = {
                    "name": item['name'],
                    "price": item['price'],
                    "qty": qty
                }

# ------------ PLACE ORDER ------------
if st.button("🛒 Place Order"):
    if not st.session_state.table:
        st.warning("Please enter your table number.")
    elif not st.session_state.cart:
        st.warning("Please add some items.")
    else:
        order = {
            "id": str(uuid4())[:8],
            "table": st.session_state.table,
            "items": st.session_state.cart,
            "total": sum(item["price"] * item["qty"] for item in st.session_state.cart.values()),
            "status": "Pending",
            "timestamp": int(time.time())
        }

        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r") as f:
                orders = json.load(f)
        else:
            orders = []

        orders.append(order)

        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)

        st.success("✅ Order placed successfully!")
        st.session_state.cart = {}
