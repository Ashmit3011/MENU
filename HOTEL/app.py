import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import uuid

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
MENU_FILE = BASE_DIR / "menu.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# === Config ===
st.set_page_config(page_title="🍽️ Smart Table Order", layout="centered")

# === Load Menu ===
with open(MENU_FILE, "r") as f:
    menu = json.load(f)

# === Categories ===
categories = sorted(set(item["category"] for item in menu))

# === Init Session ===
if "cart" not in st.session_state:
    st.session_state.cart = {}

# === Functions ===
def add_to_cart(item_id):
    st.session_state.cart[item_id] = st.session_state.cart.get(item_id, 0) + 1

def remove_from_cart(item_id):
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id] -= 1
        if st.session_state.cart[item_id] <= 0:
            del st.session_state.cart[item_id]

def get_cart_items():
    return [item for item in menu if item["id"] in st.session_state.cart]

def calculate_total():
    return sum(item["price"] * st.session_state.cart[item["id"]] for item in get_cart_items())

def place_order(table_num):
    order = {
        "id": str(uuid.uuid4())[:8],
        "table": table_num,
        "items": [{"id": item["id"], "name": item["name"], "qty": st.session_state.cart[item["id"]], "price": item["price"]} for item in get_cart_items()],
        "total": calculate_total(),
        "status": "Pending",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if not ORDERS_FILE.exists():
        with open(ORDERS_FILE, "w") as f: json.dump([], f)
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.session_state.cart.clear()
    return order["id"]

def submit_feedback(order_id, text):
    if not FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "w") as f: json.dump([], f)
    with open(FEEDBACK_FILE, "r") as f:
        feedbacks = json.load(f)
    feedbacks.append({"order_id": order_id, "feedback": text, "time": datetime.now().isoformat()})
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedbacks, f, indent=2)

# === UI ===
st.title("🍴 Order Your Meal")

# Table Number
table = st.text_input("Enter Table Number", max_chars=5)

# Menu UI
selected_category = st.selectbox("Select Category", ["All"] + categories)
st.markdown("---")

for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue
    st.markdown(f"""
        <div style="border:1px solid #444; padding:10px; border-radius:8px; margin-bottom:10px;">
            <strong>{item['name']}</strong> — ₹{item['price']}
            <div style="margin-top:5px;">
                <button onclick="document.getElementById('{item['id']}_plus').click()">➕</button>
                <span style="margin:0 8px;">{st.session_state.cart.get(item['id'], 0)}</span>
                <button onclick="document.getElementById('{item['id']}_minus').click()">➖</button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.button("➕", key=f"{item['id']}_plus", on_click=add_to_cart, args=(item["id"],), use_container_width=True)
    st.button("➖", key=f"{item['id']}_minus", on_click=remove_from_cart, args=(item["id"],), use_container_width=True)

# Cart Summary
st.markdown("### 🛒 Cart Summary")
if not st.session_state.cart:
    st.info("Cart is empty.")
else:
    total = calculate_total()
    for item in get_cart_items():
        qty = st.session_state.cart[item["id"]]
        st.markdown(f"- {item['name']} x {qty} — ₹{item['price'] * qty}")
    st.success(f"**Total: ₹{total}**")
    if st.button("✅ Place Order", disabled=not table):
        order_id = place_order(table)
        st.toast(f"🧾 Order placed! ID: {order_id}", icon="✅")
        st.success("Thank you! You can track your order below.")
        st.experimental_rerun()

# Feedback
if st.session_state.get("cart") == {}:
    st.markdown("### 💬 Feedback")
    with st.form("feedback_form"):
        order_id_input = st.text_input("Your Order ID")
        feedback_text = st.text_area("Write your feedback")
        submitted = st.form_submit_button("Send Feedback")
        if submitted and order_id_input and feedback_text:
            submit_feedback(order_id_input, feedback_text)
            st.toast("Feedback sent!", icon="💌")
