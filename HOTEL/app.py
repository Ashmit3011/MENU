import streamlit as st
import json
import os
from datetime import datetime
from uuid import uuid4

st.set_page_config(page_title="🍽️ Smart Menu", layout="wide")

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
menu_file = os.path.join(BASE_DIR, "menu.json")
orders_file = os.path.join(BASE_DIR, "orders.json")

# === Load Menu ===
if os.path.exists(menu_file):
    with open(menu_file, "r") as f:
        menu = json.load(f)
else:
    st.error("Menu not found!")
    st.stop()

# === Session State ===
if "cart" not in st.session_state:
    st.session_state.cart = []
if "order_id" not in st.session_state:
    st.session_state.order_id = str(uuid4())
if "order_status" not in st.session_state:
    st.session_state.order_status = ""

# === Styling ===
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .menu-card {
            border-radius: 12px;
            background-color: #f8fafc;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 16px;
            margin-bottom: 20px;
        }
        .cart-box {
            border-radius: 12px;
            background-color: #fff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            padding: 16px;
            margin-top: 32px;
        }
        .success-toast {
            color: green;
        }
        .autorefresh {animation: none;}
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Welcome to Our Restaurant")
st.subheader("Select your favorite items below")

# === Cart Logic ===
def add_to_cart(item):
    for i in st.session_state.cart:
        if i["id"] == item["id"]:
            i["quantity"] += 1
            return
    st.session_state.cart.append({**item, "quantity": 1})

def remove_from_cart(item_id):
    for i in st.session_state.cart:
        if i["id"] == item_id:
            if i["quantity"] > 1:
                i["quantity"] -= 1
            else:
                st.session_state.cart.remove(i)
            return

def get_total():
    return sum(item["price"] * item["quantity"] for item in st.session_state.cart)

# === Display Menu ===
if isinstance(menu, dict):
    for category, items in menu.items():
        st.markdown(f"## {category}")
        for item in items:
            with st.container():
                st.markdown("<div class='menu-card'>", unsafe_allow_html=True)
                st.markdown(f"**{item['name']}**  ")
                st.markdown(f"₹{item['price']}  ")
                if st.button(f"➕ Add", key=f"add_{item['id']}"):
                    add_to_cart(item)
                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Invalid menu format. Expected a dictionary.")

# === Cart ===
if st.session_state.cart:
    st.markdown("---")
    st.markdown("## 🛒 Your Cart")
    with st.container():
        st.markdown("<div class='cart-box'>", unsafe_allow_html=True)
        for item in st.session_state.cart:
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            col1.markdown(f"**{item['name']}**")
            col2.markdown(f"₹{item['price']}")
            col3.markdown(f"× {item['quantity']}")
            with col4:
                if st.button("➕", key=f"plus_{item['id']}"):
                    add_to_cart(item)
                if st.button("➖", key=f"minus_{item['id']}"):
                    remove_from_cart(item['id'])
        st.markdown(f"### Total: ₹{get_total()}")
        table_no = st.text_input("Enter Table Number")
        if st.button("✅ Place Order"):
            order_data = {
                "id": st.session_state.order_id,
                "table": table_no,
                "cart": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if os.path.exists(orders_file):
                with open(orders_file, "r") as f:
                    all_orders = json.load(f)
            else:
                all_orders = []
            all_orders.append(order_data)
            with open(orders_file, "w") as f:
                json.dump(all_orders, f, indent=2)
            st.toast("✅ Order Placed!", icon="✅")
            st.session_state.order_status = "Pending"
            st.session_state.cart = []

        st.markdown("</div>", unsafe_allow_html=True)

# === Order Tracking ===
if st.session_state.order_status:
    st.markdown("---")
    st.markdown("## 🚚 Track Your Order")
    if os.path.exists(orders_file):
        with open(orders_file, "r") as f:
            orders = json.load(f)
        for o in orders:
            if o["id"] == st.session_state.order_id:
                st.markdown(f"**Status:** `{o['status']}`")
                if o['status'] == "Served":
                    st.success("✅ Your food is served! Enjoy!")
                    st.session_state.order_status = ""
                break

# Auto-refresh order tracking section without blinking
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 3000);
</script>
""", unsafe_allow_html=True)
