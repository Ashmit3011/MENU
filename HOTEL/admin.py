import streamlit as st
import json
import os
import time

# Absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDER_FILE = os.path.join(BASE_DIR, "orders.json")

def load_orders():
    if not os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(ORDER_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDER_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

def update_order_status(order_id, new_status):
    orders = load_orders()
    for o in orders:
        if o["id"] == order_id:
            if o["status"] != new_status:
                o["status"] = new_status
                save_orders(orders)
                st.toast(f"📢 Order #{order_id} status changed to {new_status}")
            break

def delete_completed_orders():
    orders = load_orders()
    remaining = [o for o in orders if o["status"] != "Completed"]
    save_orders(remaining)
    st.toast("🗑️ All completed orders deleted.")

# UI config
st.set_page_config(page_title="Admin Panel", layout="wide")

# CSS for mobile responsiveness
st.markdown("""
    <style>
    @media screen and (max-width: 768px) {
        .order-card {
            font-size: 14px !important;
        }
        .order-controls {
            flex-direction: column !important;
            gap: 0.5rem !important;
        }
    }
    .order-card {
        background-color: #f9f9f9;
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 1em;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛠️ Admin Panel")

# Top controls
top_left, top_right = st.columns([4, 1])
with top_left:
    st.info("Live orders below. Tap a button to update status.")
with top_right:
    if st.button("🗑️ Delete Completed"):
        delete_completed_orders()
        st.rerun()

# State tracking
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

orders = load_orders()
order_count = len(orders)

# Sound + toast on new order
if order_count > st.session_state.last_order_count:
    st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg", autoplay=True)
    st.toast("🔔 New order received!")

st.session_state.last_order_count = order_count

# Status colors
STATUS_COLORS = {
    "Pending": "#FFF3CD",
    "Preparing": "#D1ECF1",
    "Served": "#D4EDDA",
    "Completed": "#F8F9FA"
}

if not orders:
    st.info("No orders yet.")
else:
    for order in reversed(orders):
        bg_color = STATUS_COLORS.get(order["status"], "#FFFFFF")

        with st.container():
            st.markdown(f'<div class="order-card" style="background-color:{bg_color}">', unsafe_allow_html=True)

            st.subheader(f"🧾 Order #{order['id']} - Table {order['table']}")
            st.markdown(f"**Status:** `{order['status']}`  \n⏱️ *{order['timestamp']}*")

            st.markdown("**Items:**")
            for item in order["cart"]:
                st.write(f"- {item['name']} x {item['qty']}")

            # Responsive button group
            st.markdown('<div class="order-controls" style="display:flex; gap: 1rem; flex-wrap: wrap;">', unsafe_allow_html=True)

            st.button("🔄 Pending", key=f"pending_{order['id']}", on_click=update_order_status, args=(order["id"], "Pending"))
            st.button("👨‍🍳 Preparing", key=f"preparing_{order['id']}", on_click=update_order_status, args=(order["id"], "Preparing"))
            st.button("✅ Served", key=f"served_{order['id']}", on_click=update_order_status, args=(order["id"], "Served"))
            st.button("✔️ Completed", key=f"completed_{order['id']}", on_click=update_order_status, args=(order["id"], "Completed"))

            st.markdown("</div></div>", unsafe_allow_html=True)

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
