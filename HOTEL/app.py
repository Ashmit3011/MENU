import streamlit as st
import json
import uuid
import time
from pathlib import Path
from datetime import datetime

# --- File paths ---
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# --- Load/Save JSON ---
def load_json(path):
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

# --- Hide Sidebar ---
st.set_page_config(page_title="Smart Restaurant Ordering", layout="wide")
hide_st_style = """
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- Load Menu ---
menu = load_json(MENU_FILE)
categories = sorted(set(item['category'] for item in menu))

# --- Session State Init ---
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "table_number" not in st.session_state:
    st.session_state.table_number = ""
if "order_status" not in st.session_state:
    st.session_state.order_status = None

# --- Add/Remove Cart Items ---
def add_to_cart(item_id):
    st.session_state.cart[item_id] = st.session_state.cart.get(item_id, 0) + 1

def remove_from_cart(item_id):
    if item_id in st.session_state.cart:
        if st.session_state.cart[item_id] > 1:
            st.session_state.cart[item_id] -= 1
        else:
            del st.session_state.cart[item_id]

# --- UI Styling ---
st.markdown("""
    <style>
    .cart-card {
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        padding: 1rem;
        margin-bottom: 1rem;
        color: #000;
    }
    .cart-title {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .emoji {
        font-size: 1.2rem;
    }
    .button-row button {
        margin-right: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Menu Display ---
st.title("🍽️ Welcome to Smart Restaurant")
tab1, tab2 = st.tabs(["📋 Menu", "🛒 Your Cart"])

with tab1:
    selected_category = st.selectbox("Choose a category", categories)
    for item in [i for i in menu if i['category'] == selected_category]:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{item['name']}")
            st.write(f"₹{item['price']} | {'🌶️' if item['spicy'] else ''} {'🥬' if item['veg'] else '🍗'}")
        with col2:
            st.button("Add ➕", key=f"add_{item['id']}", on_click=add_to_cart, args=(item['id'],))

# --- Cart Display ---
with tab2:
    st.subheader("🛒 Your Cart")
    total = 0
    for item_id, qty in st.session_state.cart.items():
        item = next((i for i in menu if i['id'] == item_id), None)
        if item:
            price = item['price'] * qty
            total += price
            with st.container():
                st.markdown(f"""<div class='cart-card'>
                    <div class='cart-title'>{item['name']}</div>
                    <div class='emoji'>💰 ₹{item['price']} x {qty} = ₹{price}</div>
                    <div class='button-row'>
                        <button onclick="document.getElementById('plus_{item_id}').click()">➕</button>
                        <button onclick="document.getElementById('minus_{item_id}').click()">➖</button>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.button("➕", key=f"plus_{item_id}", on_click=add_to_cart, args=(item_id,), help="Increase Quantity")
                st.button("➖", key=f"minus_{item_id}", on_click=remove_from_cart, args=(item_id,), help="Decrease Quantity")

    st.markdown(f"### 💳 Total: ₹{total}")

    st.text_input("Enter Table Number", key="table_number")
    if st.button("Place Order"):
        if st.session_state.table_number.strip() == "":
            st.warning("Please enter a table number.")
        elif not st.session_state.cart:
            st.warning("Cart is empty!")
        else:
            order = {
                "id": str(uuid.uuid4()),
                "table": st.session_state.table_number,
                "items": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().isoformat()
            }
            orders = load_json(ORDERS_FILE)
            orders.append(order)
            save_json(ORDERS_FILE, orders)
            st.session_state.order_id = order["id"]
            st.session_state.cart = {}
            st.success("✅ Order Placed!")
            st.balloons()
            st.stop()

# --- Order Tracking ---
if st.session_state.order_id:
    st.markdown("## 🧾 Order Status")
    orders = load_json(ORDERS_FILE)
    my_order = next((o for o in orders if o["id"] == st.session_state.order_id), None)
    if my_order:
        st.info(f"📍 Table: {my_order['table']} | Status: **{my_order['status']}**")
        if my_order["status"] == "Completed":
            with st.form("feedback_form"):
                st.markdown("### 🙋 Leave Feedback")
                name = st.text_input("Your Name")
                rating = st.slider("Rating", 1, 5, 4)
                comments = st.text_area("Comments")
                if st.form_submit_button("Submit"):
                    feedback = load_json(FEEDBACK_FILE)
                    feedback.append({
                        "name": name,
                        "rating": rating,
                        "comments": comments,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_json(FEEDBACK_FILE, feedback)
                    st.success("Thank you for your feedback! 💖")
    else:
        st.warning("Order not found.")
