import streamlit as st
import json
import os
import time
from datetime import datetime

# === File paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Load helpers ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)import streamlit as st
import json
import os
import time
from datetime import datetime

# === File paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Load helpers ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)

def save_orders(data):
    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_feedback(data):
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([], f)
    with open(FEEDBACK_FILE, "r") as f:
        feedbacks = json.load(f)
    feedbacks.append(data)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedbacks, f, indent=2)

# === UI config ===
st.set_page_config(page_title="📋 Smart Table Ordering", layout="centered")
st.markdown("""
    <style>
    .food-card {
        background-color: #ffffff0c;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #333;
    }
    .cart-card {
        background-color: #111111cc;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 2rem;
        border: 1px solid #444;
    }
    .plus-btn {
        background-color: #0a84ff;
        color: white;
        font-size: 20px;
        border-radius: 5px;
        width: 40px;
        height: 40px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Welcome to Our Restaurant")

menu = load_menu()
categories = list(menu.keys())

# === Session State Setup ===
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
if "order_id" not in st.session_state:
    st.session_state.order_id = None

# === Table number input ===
st.session_state.table = st.text_input("Enter your Table Number", st.session_state.table)

# === Menu Display ===
st.markdown("## 📜 Menu")
tabs = st.tabs(categories)

for i, category in enumerate(categories):
    with tabs[i]:
        for item in menu[category]:
            with st.container():
                st.markdown(f"""
                    <div class='food-card'>
                        <strong>{item['name']}</strong><br>
                        ₹{item['price']} {'🌶️' if item['spicy'] else ''} {'🌱' if item['veg'] else '🍖'}<br>
                        <small>Category: {category}</small><br><br>
                        <form action="" method="post">
                            <button class="plus-btn" type="submit" name="add_{item['id']}">+</button>
                        </form>
                    </div>
                """, unsafe_allow_html=True)

                if st.button("Add", key=f"add_{item['id']}_{time.time()}"):
                    found = False
                    for c in st.session_state.cart:
                        if c['id'] == item['id']:
                            c['qty'] += 1
                            found = True
                            break
                    if not found:
                        st.session_state.cart.append({"id": item['id'], "name": item['name'], "price": item['price'], "qty": 1})
                    st.toast(f"Added {item['name']}", icon="✅")

# === Cart Summary ===
if st.session_state.cart:
    st.markdown("<div class='cart-card'>", unsafe_allow_html=True)
    st.subheader("🛒 Your Cart")
    total = 0
    for item in st.session_state.cart:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
        with col2:
            qty = st.number_input("Qty", value=item['qty'], min_value=1, key=f"qty_{item['id']}")
            item['qty'] = qty
        with col3:
            if st.button("❌", key=f"remove_{item['id']}"):
                st.session_state.cart = [c for c in st.session_state.cart if c['id'] != item['id']]
                st.rerun()
        total += item['qty'] * item['price']

    st.markdown(f"### Total: ₹{total}")
    if st.button("✅ Place Order"):
        order = {
            "id": f"order{int(time.time())}",
            "table": st.session_state.table,
            "items": st.session_state.cart,
            "total": total,
            "status": "Pending",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        st.success("🎉 Order placed successfully!")
        st.session_state.order_placed = True
        st.session_state.order_id = order['id']
        st.session_state.cart = []
    st.markdown("</div>", unsafe_allow_html=True)

# === Order Status Tracking ===
if st.session_state.order_placed and st.session_state.order_id:
    st.markdown("---")
    st.subheader("📦 Order Status")
    orders = load_orders()
    current = next((o for o in orders if o['id'] == st.session_state.order_id), None)
    if current:
        status = current['status']
        st.markdown(f"**Current Status: `{status}`**")
        st.progress(["Pending", "Preparing", "Ready", "Served"].index(status) / 3)

        if status == "Served":
            st.markdown("---")
            st.subheader("📝 Feedback")
            rating = st.slider("How was your experience?", 1, 5, 4)
            comment = st.text_area("Leave a comment")
            if st.button("Submit Feedback"):
                save_feedback({
                    "table": st.session_state.table,
                    "rating": rating,
                    "comment": comment,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Thanks for your feedback!")

# === Real-time Refresh ===
time.sleep(5)
st.rerun()


def save_feedback(data):
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([], f)
    with open(FEEDBACK_FILE, "r") as f:
        feedbacks = json.load(f)
    feedbacks.append(data)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedbacks, f, indent=2)

# === UI config ===
st.set_page_config(page_title="📋 Smart Table Ordering", layout="centered")
st.title("🍽️ Welcome to Our Restaurant")

menu = load_menu()
categories = list(menu.keys())

# === Session State Setup ===
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
if "order_id" not in st.session_state:
    st.session_state.order_id = None

# === Table number input ===
st.session_state.table = st.text_input("Enter your Table Number", st.session_state.table)

# === Category-wise Tabs ===
st.subheader("📜 Menu")
tabs = st.tabs(categories)
for i, category in enumerate(categories):
    with tabs[i]:
        for item in menu[category]:
            with st.container():
                st.markdown(
                    f"""
                    <div style='background-color:#fff; border-radius:12px; padding:12px 16px; margin:8px 0; box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <div style='font-weight:600; font-size:18px;'>{item['name']}</div>
                                <div style='color:#888; font-size:13px;'>Category: {category}</div>
                            </div>
                            <div style='text-align:right;'>
                                <div style='font-size:18px; font-weight:bold;'>₹{item['price']}</div>
                                <form action="" method="post">
                                    <button type="submit" name="add_{item['id']}" style='background:#0d6efd; color:white; border:none; border-radius:8px; padding:4px 12px; font-size:18px;'>+</button>
                                </form>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button("Add", key=f"add_{item['id']}_{time.time()}"):
                    found = False
                    for c in st.session_state.cart:
                        if c['id'] == item['id']:
                            c['qty'] += 1
                            found = True
                            break
                    if not found:
                        st.session_state.cart.append({"id": item['id'], "name": item['name'], "price": item['price'], "qty": 1})
                    st.toast(f"✅ Added {item['name']}")

# === Cart Summary ===
if st.session_state.cart:
    st.markdown("---")
    st.subheader("🛒 Your Cart")
    total = 0
    for item in st.session_state.cart:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
        with col2:
            qty = st.number_input("Qty", min_value=1, value=item['qty'], key=item['id'])
            item['qty'] = qty
        with col3:
            if st.button("❌", key=f"remove_{item['id']}"):
                st.session_state.cart = [c for c in st.session_state.cart if c['id'] != item['id']]
        total += item['qty'] * item['price']

    st.markdown(f"### 💵 Total: ₹{total}")
    if st.button("✅ Place Order"):
        order = {
            "id": f"order{int(time.time())}",
            "table": st.session_state.table,
            "items": st.session_state.cart,
            "total": total,
            "status": "Pending",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        st.success("🎉 Order placed successfully!")
        st.session_state.order_placed = True
        st.session_state.order_id = order['id']
        st.session_state.cart = []

# === Order Status Tracking ===
if st.session_state.order_placed and st.session_state.order_id:
    st.markdown("---")
    st.subheader("📦 Order Status")
    orders = load_orders()
    current = next((o for o in orders if o['id'] == st.session_state.order_id), None)
    if current:
        status = current['status']
        st.markdown(f"**Current Status: `{status}`**")
        st.progress(["Pending", "Preparing", "Ready", "Served"].index(status) / 3)

        # Show feedback form when served
        if status == "Served":
            st.markdown("---")
            st.subheader("📝 Feedback")
            rating = st.slider("How was your experience?", 1, 5, 4)
            comment = st.text_area("Leave a comment")
            if st.button("Submit Feedback"):
                save_feedback({
                    "table": st.session_state.table,
                    "rating": rating,
                    "comment": comment,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Thanks for your feedback!")

# === Real-time Refresh ===
time.sleep(5)
st.rerun()
