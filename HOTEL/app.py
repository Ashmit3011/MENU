import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
menu_file = os.path.join(BASE_DIR, "menu.json")
orders_file = os.path.join(BASE_DIR, "orders.json")

# Title
st.set_page_config(page_title="Smart Menu", layout="wide")
st.markdown("<h1 style='text-align: center;'>📋 Smart Table Ordering</h1>", unsafe_allow_html=True)

# Load Menu
if os.path.exists(menu_file):
    with open(menu_file, "r") as f:
        menu = json.load(f)
else:
    st.error("Menu file not found.")
    st.stop()

# Load Orders
if os.path.exists(orders_file):
    with open(orders_file, "r") as f:
        orders = json.load(f)
else:
    orders = []

# 🔄 Auto-delete completed/cancelled orders older than 5 minutes
now = datetime.now()
cleaned_orders = []
for order in orders:
    order_time = datetime.strptime(order["timestamp"], "%Y-%m-%d %H:%M:%S")
    if order["status"] in ["Completed", "Cancelled"]:
        if now - order_time < timedelta(minutes=5):
            cleaned_orders.append(order)
    else:
        cleaned_orders.append(order)

# Save cleaned orders
with open(orders_file, "w") as f:
    json.dump(cleaned_orders, f, indent=4)

# Sidebar Menu Selection
st.sidebar.header("Menu")
selected_items = {}
for category, items in menu.items():
    st.sidebar.subheader(category)
    for item in items:
        qty = st.sidebar.number_input(f"{item['name']} (₹{item['price']})", min_value=0, step=1)
        if qty > 0:
            selected_items[item['name']] = {"price": item['price'], "quantity": qty}

# Submit Order
if st.sidebar.button("Place Order"):
    if selected_items:
        new_order = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": selected_items,
            "status": "Pending"
        }
        cleaned_orders.append(new_order)
        with open(orders_file, "w") as f:
            json.dump(cleaned_orders, f, indent=4)
        st.success("✅ Order placed successfully!")
        st.rerun()
    else:
        st.warning("Please select at least one item to place an order.")

# Display Live Orders
st.markdown("## 📦 Your Orders")
for order in reversed(cleaned_orders):
    timestamp = order["timestamp"]
    status = order["status"]
    items = order["items"]

    status_color = {
        "Pending": "orange",
        "Preparing": "blue",
        "Completed": "green",
        "Cancelled": "red"
    }.get(status, "gray")

    st.markdown(f"""
    <div style="border:1px solid #444;padding:10px;border-radius:10px;margin:10px 0;">
        <p>🕒 <span style="color:lightgreen;">{timestamp}</span> — 
        <b>Status:</b> <span style="color:{status_color};">{status}</span></p>
    """, unsafe_allow_html=True)

    for name, detail in items.items():
        text = f"{name} x {detail['quantity']} = ₹{detail['price'] * detail['quantity']}"
        if status == "Cancelled":
            st.markdown(f"<p style='text-decoration: line-through; color: gray;'>{text}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"- {text}")

    st.markdown("</div>", unsafe_allow_html=True)

# Hide "admin" from sidebar (Option 2)
hide_sidebar_style = """
    <style>
    section[data-testid="stSidebarNav"] ul li a[href*="pages/_admin"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# Force refresh to show updates
st.experimental_set_query_params(t=str(datetime.now().timestamp()))