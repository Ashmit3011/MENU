import streamlit as st
import json, uuid, time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"

st.set_page_config(page_title="📋 Menu", layout="centered")

# --- Load Menu ---
with open(MENU_FILE, "r") as f:
    menu = json.load(f)
categories = sorted(set([item["category"] for item in menu]))

# --- Session State ---
if "cart" not in st.session_state: st.session_state.cart = []
if "table" not in st.session_state: st.session_state.table = ""

def get_cart_item(item_id):
    for item in st.session_state.cart:
        if item["id"] == item_id:
            return item
    return None

def add_to_cart(product):
    existing = get_cart_item(product["id"])
    if existing:
        existing["qty"] += 1
    else:
        st.session_state.cart.append({**product, "qty": 1})

def remove_from_cart(item_id):
    item = get_cart_item(item_id)
    if item:
        item["qty"] -= 1
        if item["qty"] <= 0:
            st.session_state.cart.remove(item)

def place_order():
    if not st.session_state.table.strip():
        st.warning("Please enter table number")
        return

    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)

    order = {
        "id": str(uuid.uuid4())[:8],
        "table": st.session_state.table,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": st.session_state.cart,
        "total": sum(item['qty'] * item['price'] for item in st.session_state.cart),
        "status": "Pending"
    }
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.success("✅ Order placed!")
    st.session_state.cart = []

# --- UI ---
st.title("🍽️ Smart Menu")
st.text_input("🪑 Enter Table Number", key="table")

for category in categories:
    with st.expander(f"📂 {category}", expanded=True):
        items = [i for i in menu if i["category"] == category]
        for item in items:
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{item['name']}**  ₹{item['price']}")
            with col2:
                qty_item = get_cart_item(item["id"])
                col2.button("➖", on_click=remove_from_cart, args=(item["id"],), key=f"rm{item['id']}")
                col2.write(qty_item["qty"] if qty_item else 0)
                col2.button("➕", on_click=add_to_cart, args=(item,), key=f"add{item['id']}")

st.markdown("---")

if st.session_state.cart:
    st.subheader("🛒 Your Cart")
    total = sum(item['qty'] * item['price'] for item in st.session_state.cart)
    for item in st.session_state.cart:
        st.markdown(f"{item['name']} x {item['qty']} = ₹{item['qty']*item['price']}")
    st.markdown(f"**Total: ₹{total}**")
    if st.button("✅ Confirm Order"):
        place_order()

# --- Auto Refresh ---
time.sleep(5)
st.rerun()
