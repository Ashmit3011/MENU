import streamlit as st
import json
import os
from datetime import datetime

# === Paths ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")

# === Config ===
st.set_page_config(page_title="Smart Restaurant", layout="centered")

# === Load Menu ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

# === Save Order ===
def save_order(order):
    try:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# === State Init ===
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "table" not in st.session_state:
    st.session_state.table = ""
if "just_ordered" not in st.session_state:
    st.session_state.just_ordered = False

# === Confirmation Screen ===
if st.session_state.just_ordered:
    st.success("✅ Thank you! Your order has been placed and is being processed.")
    st.balloons()
    if st.button("🛒 Start New Order"):
        st.session_state.just_ordered = False
        st.session_state.table = ""
    st.stop()

# === UI ===
st.title("🍴 Welcome to Smart Restaurant")

menu = load_menu()
categories = sorted(set([item["category"] for item in menu]))

# === Table Entry ===
st.session_state.table = st.text_input("Enter Table Number", st.session_state.table)

# === Menu Display ===
for cat in categories:
    st.subheader(f"📂 {cat}")
    for item in [i for i in menu if i["category"] == cat]:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"**{item['name']}**")
            st.caption(f"₹{item['price']}")
        with col2:
            qty = st.session_state.cart.get(item['id'], 0)
            if st.button("➖", key=f"dec_{item['id']}"):
                if qty > 0:
                    st.session_state.cart[item['id']] = qty - 1
            st.markdown(f"**{qty}**")
            if st.button("➕", key=f"inc_{item['id']}"):
                st.session_state.cart[item['id']] = qty + 1

# === Cart Summary ===
cart = st.session_state.cart
if cart:
    st.markdown("---")
    st.header("🛒 Your Cart")
    total = 0
    items = []
    for id, qty in cart.items():
        if qty == 0:
            continue
        item = next((x for x in menu if x["id"] == id), None)
        if not item:
            continue
        amount = qty * item["price"]
        total += amount
        items.append({"id": id, "name": item["name"], "qty": qty, "price": item["price"]})
        st.write(f"{item['name']} x {qty} = ₹{amount}")

    st.markdown(f"**Total: ₹{total}**")

    if st.button("✅ Place Order"):
        if not st.session_state.table:
            st.warning("Please enter your table number first.")
        else:
            order = {
                "id": f"ORD{datetime.now().strftime('%H%M%S')}",
                "table": st.session_state.table,
                "items": items,
                "total": total,
                "status": "Pending",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_order(order)
            st.session_state.cart = {}
            st.session_state.just_ordered = True
            st.rerun()
else:
    st.info("Your cart is empty.")
