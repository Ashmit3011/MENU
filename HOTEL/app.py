# === app.py ===

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# === File Paths ===
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
MENU_FILE = BASE_DIR / "menu.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# === Streamlit Page Config ===
st.set_page_config(page_title="🍽️ Order Menu", layout="wide")

# === Load Menu ===
with open(MENU_FILE, "r") as f:
    menu = json.load(f)

categories = sorted(set(item["category"] for item in menu))

# === Session State Init ===
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""

# === UI ===
st.title("🍽️ Smart Table Ordering")
st.markdown("""
<style>
.cart-box { background: #f8f8f8; padding: 1rem; border-radius: 10px; }
.food-card { border: 1px solid #ddd; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
.qty-btn { font-size: 1.2rem; margin: 0 0.5rem; }
</style>
""", unsafe_allow_html=True)

# === Table Entry ===
st.session_state.table = st.text_input("Enter Table Number", st.session_state.table)

# === Menu ===
selected_cat = st.selectbox("Select Category", categories)
st.markdown(f"## 🌟 {selected_cat}")

for item in menu:
    if item["category"] != selected_cat:
        continue

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class='food-card'>
        <strong>{item['name']}</strong><br>
        💸 ₹{item['price']}<br>
        🌱 {'Veg' if item['veg'] else 'Non-Veg'} | {'🌶' if item['spicy'] else ''} {'🌟 Popular' if item['popular'] else ''}<br>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        current_qty = next((i['qty'] for i in st.session_state.cart if i['id'] == item['id']), 0)
        st.write("Qty:", current_qty)
        col_inc, col_dec = st.columns(2)
        with col_inc:
            if st.button("+", key=f"inc_{item['id']}"):
                if current_qty == 0:
                    st.session_state.cart.append({**item, "qty": 1})
                else:
                    for i in st.session_state.cart:
                        if i['id'] == item['id']:
                            i['qty'] += 1
                st.toast(f"Added {item['name']}", icon="✅")
        with col_dec:
            if st.button("-", key=f"dec_{item['id']}"):
                for i in st.session_state.cart:
                    if i['id'] == item['id']:
                        i['qty'] -= 1
                        if i['qty'] <= 0:
                            st.session_state.cart.remove(i)
                        st.toast(f"Removed {item['name']}", icon="❌")
                        break

# === Cart ===
st.markdown("## 🛒 Your Cart")
if not st.session_state.cart:
    st.info("Cart is empty!")
else:
    total = sum(i["qty"] * i["price"] for i in st.session_state.cart)
    with st.container():
        for i in st.session_state.cart:
            st.write(f"{i['name']} x {i['qty']} = ₹{i['qty'] * i['price']}")
        st.success(f"Total: ₹{total}")

    if st.button("📨 Place Order"):
        if st.session_state.table == "":
            st.error("Please enter table number")
        else:
            new_order = {
                "id": f"ORD{int(datetime.now().timestamp())}",
                "table": st.session_state.table,
                "items": st.session_state.cart,
                "total": total,
                "status": "Pending",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                if not ORDERS_FILE.exists():
                    with open(ORDERS_FILE, "w") as f:
                        json.dump([], f)
                with open(ORDERS_FILE, "r") as f:
                    orders = json.load(f)
                orders.append(new_order)
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.toast("Order placed!", icon="🍽️")
                st.success("Thanks! Please wait while we prepare your food.")
                st.session_state.cart.clear()
            except Exception as e:
                st.error(f"Error placing order: {e}")

# === Feedback ===
st.markdown("---")
st.subheader("📈 Feedback")
feedback = st.text_area("Leave your feedback")
if st.button("Submit Feedback"):
    fb_data = {
        "table": st.session_state.table,
        "message": feedback,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if not FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([], f)
    with open(FEEDBACK_FILE, "r") as f:
        fb_all = json.load(f)
    fb_all.append(fb_data)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(fb_all, f, indent=2)
    st.success("Thanks for your feedback!")
