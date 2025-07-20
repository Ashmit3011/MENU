import streamlit as st
import json
import os
import time

# Correct full path to orders.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDER_FILE = os.path.join(BASE_DIR, "orders.json")

# Load and save helpers
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

# UI
st.set_page_config(page_title="Admin Panel - Smart Orders", layout="wide")
st.title("🛠️ Admin Panel - Live Order Manager")

# State tracking
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = 0

# Status colors
STATUS_COLORS = {
    "Pending": "#FFF3CD",
    "Preparing": "#D1ECF1",
    "Served": "#D4EDDA",
    "Completed": "#F8F9FA"
}

# Top bar
colA, colB = st.columns([4, 1])
with colA:
    st.info("Live orders below. Use buttons to update status.")
with colB:
    if st.button("🗑️ Delete Completed Orders"):
        delete_completed_orders()
        st.rerun()

orders = load_orders()
order_count = len(orders)

# Debug info
st.write("Loading from:", ORDER_FILE)
st.write("Loaded Orders:", orders)

# New order sound
if order_count > st.session_state.last_order_count:
    st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg", autoplay=True)
    st.toast("🔔 New order received!")

st.session_state.last_order_count = order_count

if not orders:
    st.info("No orders found.")
else:
    for order in reversed(orders):
        color = STATUS_COLORS.get(order["status"], "#FFFFFF")
        with st.container(border=True):
            st.markdown(
                f"""<div style="background-color:{color}; padding:1em; border-radius:10px">""",
                unsafe_allow_html=True
            )
            st.subheader(f"🧾 Order #{order['id']} - Table {order['table']}")
            st.markdown(f"**Status:** `{order['status']}`  \n⏱️ *Placed at:* `{order['timestamp']}`")

            for item in order["cart"]:
                st.write(f"- {item['name']} x {item['qty']}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🔄 Set to Pending", key=f"pending_{order['id']}"):
                    update_order_status(order["id"], "Pending")
                    st.rerun()
            with col2:
                if st.button("👨‍🍳 Set to Preparing", key=f"preparing_{order['id']}"):
                    update_order_status(order["id"], "Preparing")
                    st.rerun()
            with col3:
                if st.button("✅ Set to Served", key=f"served_{order['id']}"):
                    update_order_status(order["id"], "Served")
                    st.rerun()
            with col4:
                if st.button("✔️ Set to Completed", key=f"completed_{order['id']}"):
                    update_order_status(order["id"], "Completed")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
