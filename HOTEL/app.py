import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
menu_file = os.path.join(BASE_DIR, "menu.json")
orders_file = os.path.join(BASE_DIR, "orders.json")

# Page config
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# Hide sidebar and Streamlit elements
hide_sidebar = """
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarNav"] ul li a[href*="pages/_admin"] { display: none; }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center;'>🍽️ Smart Table Ordering System</h1>", unsafe_allow_html=True)

# ⌨️ Input table number at the top of the page
table_number = st.text_input("Enter your Table Number:", max_chars=10)

if not table_number:
    st.warning("Please enter your Table Number to continue.")
    st.stop()

# Load menu
if os.path.exists(menu_file):
    with open(menu_file, "r") as f:
        menu = json.load(f)
else:
    st.error("Menu file not found.")
    st.stop()

# Load orders
if os.path.exists(orders_file):
    with open(orders_file, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Auto-clean old completed/cancelled orders (> 5 mins)
now = datetime.now()
filtered_orders = []
for order in orders:
    order_time = datetime.strptime(order["timestamp"], "%Y-%m-%d %H:%M:%S")
    if order["status"] in ["Completed", "Cancelled"]:
        if now - order_time < timedelta(minutes=5):
            filtered_orders.append(order)
    else:
        filtered_orders.append(order)

# Save cleaned orders
with open(orders_file, "w") as f:
    json.dump(filtered_orders, f, indent=4)

# Select items
st.markdown("## 🧾 Menu")
selected_items = {}
for category, items in menu.items():
    st.subheader(category)
    for item in items:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{item['name']}** - ₹{item['price']}")
        with col2:
            qty = st.number_input(f"{item['name']}", key=item['name'], min_value=0, step=1)
            if qty > 0:
                selected_items[item['name']] = {"price": item['price'], "quantity": qty}

# Place order
if st.button("🛎️ Place Order"):
    if selected_items:
        new_order = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "table": table_number,
            "items": selected_items,
            "status": "Pending"
        }
        filtered_orders.append(new_order)
        with open(orders_file, "w") as f:
            json.dump(filtered_orders, f, indent=4)
        st.success("✅ Your order has been placed!")
        st.rerun()
    else:
        st.warning("Please select at least one item.")

# Show current table's orders
st.markdown("## 📦 Your Orders")

has_orders = False
for order in reversed(filtered_orders):
    if order.get("table") != table_number:
        continue

    has_orders = True
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

if not has_orders:
    st.info("You have not placed any orders yet.")

# Refresh to update live
st.experimental_set_query_params(t=str(datetime.now().timestamp()))