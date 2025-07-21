# app.py

import streamlit as st
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

# === File Paths ===
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"

# === Page Config ===
st.set_page_config(page_title="📋 Menu", layout="centered")
hide_menu = """
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .stToast { animation: slideIn 0.3s ease-in-out; }
    </style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# === Load Menu ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

menu = load_menu()
categories = sorted(set(item["category"] for item in menu))

# === Cart Logic ===
if "cart" not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(item):
    if item["id"] in st.session_state.cart:
        st.session_state.cart[item["id"]]["qty"] += 1
    else:
        st.session_state.cart[item["id"]] = {"name": item["name"], "price": item["price"], "qty": 1}

def remove_from_cart(item_id):
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]["qty"] -= 1
        if st.session_state.cart[item_id]["qty"] <= 0:
            del st.session_state.cart[item_id]

# === UI ===
st.title("🍽️ Smart Table Ordering")

selected_cat = st.selectbox("Select Category", categories)
st.markdown("### 🍴 Menu")

for item in menu:
    if item["category"] != selected_cat:
        continue
    col1, col2 = st.columns([6, 2])
    with col1:
        st.markdown(f"**{item['name']}**  \n₹{item['price']}")
    with col2:
        if st.button("+", key=f"add_{item['id']}"):
            add_to_cart(item)
        if item["id"] in st.session_state.cart:
            if st.button("−", key=f"remove_{item['id']}"):
                remove_from_cart(item["id"])

# === Cart Display ===
st.markdown("---")
st.subheader("🛒 Cart Summary")
total = sum(item["price"] * item["qty"] for item in st.session_state.cart.values())

if st.session_state.cart:
    for item_id, item in st.session_state.cart.items():
        st.markdown(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
    st.markdown(f"**Total: ₹{total}**")
else:
    st.info("Your cart is empty.")

# === Place Order ===
with st.form("order_form"):
    table = st.text_input("Enter Table Number", max_chars=5)
    submitted = st.form_submit_button("✅ Place Order")

    if submitted and st.session_state.cart and table:
        new_order = {
            "id": str(uuid.uuid4())[:8],
            "table": table,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": list(st.session_state.cart.values()),
            "total": total,
            "status": "Pending"
        }

        if ORDERS_FILE.exists():
            with open(ORDERS_FILE, "r") as f:
                orders = json.load(f)
        else:
            orders = []

        orders.append(new_order)

        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)

        st.success("✅ Order placed successfully!")
        st.toast("🎉 Thank you! Your order is now being prepared.")
        st.audio("https://www.soundjay.com/button/beep-07.wav", autoplay=True)
        st.session_state.cart.clear()
        st.rerun()
