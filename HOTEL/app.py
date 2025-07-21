import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.resolve()
MENU_FILE = BASE_DIR / "menu.json"
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# Hide sidebar for customers
st.set_page_config(page_title="Smart Restaurant Ordering", layout="wide")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Load or init JSON
def load_json(path, default=[]):
    if not path.exists():
        path.write_text(json.dumps(default), encoding="utf-8")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Load menu
menu = load_json(MENU_FILE)

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table_number" not in st.session_state:
    st.session_state.table_number = ""
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False

st.title("🍽️ Welcome to Smart Restaurant")
st.markdown("Order your favorite items below.")

# Table number
st.session_state.table_number = st.text_input("Enter your table number", st.session_state.table_number)

# Categories
categories = sorted(set(item["category"] for item in menu))
selected_category = st.selectbox("Select Category", ["All"] + categories)

# Show menu
st.subheader("Menu")
for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(item["image"], width=100)
    with col2:
        st.markdown(f"**{item['name']}** - ₹{item['price']}")
        st.caption(f"{'🌶️' if item['spicy'] else ''} {'🌱' if item['veg'] else '🍖'} {item['category']}")
        qty = st.number_input(f"Qty for {item['name']}", min_value=0, max_value=10, step=1, key=item["name"])
        if qty > 0:
            found = False
            for c in st.session_state.cart:
                if c["name"] == item["name"]:
                    c["qty"] = qty
                    found = True
            if not found:
                st.session_state.cart.append({
                    "name": item["name"],
                    "price": item["price"],
                    "qty": qty
                })

# Cart display
st.subheader("🛒 Your Cart")
total = 0
if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']
    st.markdown(f"**Total: ₹{total}**")
else:
    st.info("Cart is empty.")

# Place order
if st.button("✅ Place Order"):
    if not st.session_state.table_number.strip():
        st.error("Please enter your table number.")
    elif not st.session_state.cart:
        st.warning("Cart is empty.")
    else:
        orders = load_json(ORDER_FILE)
        order_id = len(orders) + 1
        orders.append({
            "id": order_id,
            "table": st.session_state.table_number.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cart": st.session_state.cart,
            "status": "Pending"
        })
        save_json(ORDER_FILE, orders)
        st.success(f"🎉 Order #{order_id} placed successfully!")
        st.balloons()
        st.info("🎁 You've received a free dessert!")
        st.session_state.order_placed = True
        st.session_state.cart = []

# Show feedback after order placed
if st.session_state.order_placed:
    st.markdown("---")
    st.subheader("💬 We'd love your feedback!")
    rating = st.slider("Rate your experience (1-5)", 1, 5, 4)
    comment = st.text_area("Any comments?")
    if st.button("Submit Feedback"):
        feedbacks = load_json(FEEDBACK_FILE)
        feedbacks.append({
            "table": st.session_state.table_number,
            "rating": rating,
            "comments": comment,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(FEEDBACK_FILE, feedbacks)
        st.success("Thank you for your feedback!")
