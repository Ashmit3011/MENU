import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- Paths ---
BASE = os.path.dirname(os.path.abspath(__file__))
menu_file = os.path.join(BASE, "menu.json")
orders_file = os.path.join(BASE, "orders.json")

# --- Load functions ---
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --- Load data ---
menu = load_json(menu_file, {})
orders = load_json(orders_file, [])

# --- Streamlit Setup ---
st.set_page_config(page_title="Smart Table Menu", layout="wide")
st.markdown("<style>footer{visibility:hidden;} .block-container{padding-top:2rem;} .st-emotion-cache-1avcm0n{padding-top:1rem;} .css-18e3th9{visibility:hidden;}</style>", unsafe_allow_html=True)
st_autorefresh(interval=5000, key="refresh")

# --- Table Number Input ---
table = st.text_input("Enter your Table Number", key="table_input")
if not table:
    st.warning("Please enter your table number to continue.")
    st.stop()

# --- Category Navigation ---
categories = list(menu.keys())
query_params = st.query_params

if "category" not in query_params:
    st.query_params.update(category=categories[0])

selected_category = st.query_params.get("category", categories[0])

# --- Scrollable Category Buttons ---
category_html = "<div style='display: flex; overflow-x: auto; padding: 10px;'>"
for cat in categories:
    is_selected = cat == selected_category
    style = "background-color:#2563eb;" if is_selected else "background-color:#3b82f6;"
    category_html += f"""
        <button onclick="window.location.search='?category={cat}&t={int(time.time())}'"
                style="margin-right:10px; padding:10px 20px; border:none; border-radius:20px; color:white; {style}">
            {cat}
        </button>
    """
category_html += "</div>"
st.markdown(category_html, unsafe_allow_html=True)

# --- Show Menu Items ---
if selected_category in menu:
    st.markdown(f"### 🍴 {selected_category}")
    for item in menu[selected_category]:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item['name']}** - ₹{item['price']}")
        with col2:
            qty = st.number_input(f"Qty_{item['name']}", min_value=1, step=1, label_visibility="collapsed")
            if st.button(f"Add {item['name']}", key=item['name']):
                orders.append({
                    "table": table,
                    "item": item["name"],
                    "price": item["price"],
                    "qty": qty,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Pending"
                })
                save_json(orders_file, orders)
                st.success(f"✅ Added {qty} x {item['name']} to your order")

# --- Current Orders for Table ---
st.markdown("---")
st.subheader("🧾 Your Current Orders")

table_orders = [o for o in orders if o["table"] == table]
if table_orders:
    for order in table_orders:
        st.markdown(f"- {order['qty']} x **{order['item']}** – ₹{order['price'] * order['qty']} ({order['status']})")
else:
    st.info("No orders yet.")