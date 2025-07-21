import streamlit as st
import json
import os
import time
from datetime import datetime

# === Paths ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Page Config ===
st.set_page_config(page_title="🍽️ Smart Table Ordering", layout="centered")

# === Session State ===
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "table" not in st.session_state:
    st.session_state.table = ""

# === Load Menu ===
with open(MENU_FILE, "r") as f:
    menu = json.load(f)

categories = sorted(set([item["category"] for item in menu]))

# === Header ===
st.title("🍴 Welcome to Smart Restaurant")

# === Table Input ===
st.session_state.table = st.text_input("Enter your Table Number", value=st.session_state.table)

# === Show Menu ===
st.markdown("---")
st.markdown("## 🧾 Menu")

tabs = st.tabs(categories)
for idx, cat in enumerate(categories):
    with tabs[idx]:
        for item in menu:
            if item["category"] == cat:
                col1, col2 = st.columns([6, 2])
                with col1:
                    st.markdown(f"**{item['name']}**  ")
                    st.markdown(f"₹{item['price']} | {'🌶️' if item['spicy'] else ''} {'🟢' if item['veg'] else '🔴'}")
                with col2:
                    qty = st.session_state.cart.get(item["id"], 0)
                    col_a, col_b, col_c = st.columns([1, 1, 1])
                    with col_a:
                        if st.button("➖", key=f"dec_{item['id']}"):
                            if qty > 0:
                                st.session_state.cart[item["id"]] = qty - 1
                    with col_b:
                        st.markdown(f"<div style='text-align:center;'>{qty}</div>", unsafe_allow_html=True)
                    with col_c:
                        if st.button("➕", key=f"inc_{item['id']}"):
                            st.session_state.cart[item["id"]] = qty + 1

# === Cart Summary ===
st.markdown("---")
st.markdown("## 🛒 Cart Summary")

cart_items = []
total = 0
for item in menu:
    qty = st.session_state.cart.get(item["id"], 0)
    if qty > 0:
        subtotal = qty * item["price"]
        cart_items.append({"id": item["id"], "name": item["name"], "price": item["price"], "qty": qty})
        total += subtotal
        st.markdown(f"- {item['name']} x {qty} = ₹{subtotal}")

st.markdown(f"### 💰 Total: ₹{total}")

# === Place Order ===
if st.button("✅ Place Order") and cart_items and st.session_state.table:
    order_data = {
        "id": int(time.time()),
        "table": st.session_state.table,
        "items": cart_items,
        "total": total,
        "status": "Pending",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w") as f:
            json.dump([], f)
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
    orders.append(order_data)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.session_state.cart = {}
    st.toast("🍽️ Order placed successfully!")
    st.session_state.auto_refresh = True
    st.rerun()

# === Order Status Tracker ===
st.markdown("---")
st.markdown("## 🔍 Track Your Order Status")

if st.session_state.table:
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            all_orders = json.load(f)
        table_orders = [o for o in all_orders if o["table"] == st.session_state.table]
        if table_orders:
            latest_order = sorted(table_orders, key=lambda x: x["time"], reverse=True)[0]
            st.markdown(f"### 🧾 Order #{latest_order['id']} - Status: `{latest_order['status']}`")
            with st.expander("Order Details"):
                for item in latest_order["items"]:
                    st.markdown(f"- {item['name']} x {item['qty']} (₹{item['price'] * item['qty']})")
                st.markdown(f"**Total: ₹{latest_order['total']}**")
                st.markdown(f"**Placed At:** {latest_order['time']}")
            progress_map = {"Pending": 0, "Preparing": 33, "Ready": 66, "Served": 100}
            st.progress(progress_map.get(latest_order["status"], 0))

            if latest_order["status"] == "Served":
                st.markdown("### 🙋‍♂️ Leave Feedback")
                feedback_text = st.text_input("How was your meal?")
                if st.button("Submit Feedback"):
                    if not os.path.exists(FEEDBACK_FILE):
                        with open(FEEDBACK_FILE, "w") as f:
                            json.dump([], f)
                    with open(FEEDBACK_FILE, "r") as f:
                        feedback_data = json.load(f)
                    feedback_data.append({
                        "table": st.session_state.table,
                        "feedback": feedback_text,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    with open(FEEDBACK_FILE, "w") as f:
                        json.dump(feedback_data, f, indent=2)
                    st.success("Thanks for your feedback!")

# === Auto Refresh ===
time.sleep(5)
st.rerun()
