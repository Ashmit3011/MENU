import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import uuid
import time

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
if "order_id" not in st.session_state:
    st.session_state.order_id = None

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
    order_id = str(uuid.uuid4())[:8]
    order = {
        "id": order_id,
        "table": table_num,
        "items": [
            {"id": item["id"], "name": item["name"], "qty": st.session_state.cart[item["id"]], "price": item["price"]} for item in get_cart_items()
        ],
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
    st.session_state.order_id = order_id
    return order_id

def submit_feedback(order_id, text):
    if not FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "w") as f: json.dump([], f)
    with open(FEEDBACK_FILE, "r") as f:
        feedbacks = json.load(f)
    feedbacks.append({"order_id": order_id, "feedback": text, "time": datetime.now().isoformat()})
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedbacks, f, indent=2)

def get_order_status(order_id):
    if not ORDERS_FILE.exists(): return None
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
    for o in orders:
        if o["id"] == order_id:
            return o["status"]
    return None

# === Mobile-friendly UI CSS ===
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
    }
    .stButton>button {
        width: 100%;
        padding: 10px;
        border-radius: 8px;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# === UI ===
st.title("📱 Smart Table Order")

# Table Number
table = st.text_input("Enter Table Number", max_chars=5)

# Menu UI
selected_category = st.selectbox("Choose Category", ["All"] + categories)
for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue
    st.markdown(f"**{item['name']}** — ₹{item['price']}")
    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        st.button("➖", key=f"{item['id']}_minus", on_click=remove_from_cart, args=(item['id'],))
    with col2:
        st.write(st.session_state.cart.get(item['id'], 0))
    with col3:
        st.button("➕", key=f"{item['id']}_plus", on_click=add_to_cart, args=(item['id'],))
    st.markdown("---")

# Cart Summary
st.subheader("🛒 Your Cart")
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
        st.experimental_rerun()

# Order Tracking
if st.session_state.order_id:
    st.subheader("📦 Track Your Order")
    current_status = get_order_status(st.session_state.order_id)
    if current_status:
        st.success(f"Order ID `{st.session_state.order_id}` is **{current_status}**")
        status_progress = {"Pending": 25, "Preparing": 50, "Ready": 75, "Served": 100}
        st.progress(status_progress.get(current_status, 0))
    else:
        st.warning("Order not found.")
    time.sleep(5)
    st.experimental_rerun()

# Feedback
if st.session_state.order_id:
    st.subheader("💬 Feedback")
    with st.form("feedback_form"):
        feedback_text = st.text_area("Write your feedback")
        submitted = st.form_submit_button("Send Feedback")
        if submitted and feedback_text:
            submit_feedback(st.session_state.order_id, feedback_text)
            st.toast("Feedback sent!", icon="💌")
