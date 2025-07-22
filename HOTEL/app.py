import streamlit as st
import json
import os
from datetime import datetime
import time

# ----------- Helper Functions -----------

def load_json(filepath, default):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# ----------- File Paths -----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "../menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "../orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "../feedback.json")

# ----------- Page Config -----------

st.set_page_config(page_title="Smart Menu", layout="wide")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ----------- Session State Init -----------

if "cart" not in st.session_state:
    st.session_state.cart = {}
if "table_number" not in st.session_state:
    st.session_state.table_number = None
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "All"

# ----------- Ask Table Number Once -----------

if st.session_state.table_number is None:
    table = st.text_input("🔢 Enter Your Table Number")
    if st.button("Submit") and table:
        st.session_state.table_number = table
    st.stop()

# ----------- Load Menu -----------

menu_data = load_json(MENU_FILE, {})
categories = list(set(item["category"] for item in menu_data)) if menu_data else []
categories.sort()
categories.insert(0, "All")  # Add "All" at top

# ----------- Category Selector -----------

st.markdown("## 🍽️ Welcome to Smart Menu")
st.markdown(f"### 🪑 Table {st.session_state.table_number}")

st.markdown("""
    <style>
        .scrolling-category {
            display: flex;
            overflow-x: auto;
            padding: 10px 0;
            margin-bottom: 20px;
        }
        .cat-btn {
            padding: 10px 20px;
            margin: 0 10px 0 0;
            border-radius: 25px;
            border: 2px solid #ccc;
            background-color: white;
            cursor: pointer;
            transition: 0.3s;
            white-space: nowrap;
        }
        .cat-btn:hover {
            background-color: #f3f4f6;
        }
        .cat-btn.active {
            background-color: #2563eb;
            color: white;
            border-color: #2563eb;
        }
    </style>
""", unsafe_allow_html=True)

category_bar = '<div class="scrolling-category">'
for cat in categories:
    is_active = 'active' if cat == st.session_state.selected_category else ''
    category_bar += f"""
        <form method="get" style="display:inline;">
            <button class="cat-btn {is_active}" name="category" value="{cat}">{cat}</button>
        </form>
    """
category_bar += "</div>"
st.markdown(category_bar, unsafe_allow_html=True)

query_params = st.query_params
selected_category = query_params.get("category", [st.session_state.selected_category])[0]
st.session_state.selected_category = selected_category

# ----------- Display Menu -----------

filtered_menu = [item for item in menu_data if selected_category == "All" or item["category"] == selected_category]

cols = st.columns(2)
for idx, item in enumerate(filtered_menu):
    col = cols[idx % 2]
    with col:
        with st.container():
            st.markdown(f"#### {item['name']}")
            st.markdown(f"💰 ₹{item['price']}")
            if st.button(f"Add to Cart - {item['name']}", key=item['name']):
                if item['name'] not in st.session_state.cart:
                    st.session_state.cart[item['name']] = {"price": item['price'], "qty": 1}
                else:
                    st.session_state.cart[item['name']]["qty"] += 1

# ----------- Cart -----------

st.markdown("---")
st.subheader("🛒 Cart")
if st.session_state.cart:
    total = 0
    for name, item in st.session_state.cart.items():
        qty = item["qty"]
        price = item["price"]
        subtotal = qty * price
        total += subtotal
        st.write(f"**{name}** - {qty} x ₹{price} = ₹{subtotal}")
    st.markdown(f"### 💵 Total: ₹{total}")

    if st.button("✅ Place Order"):
        orders = load_json(ORDERS_FILE, [])
        orders.append({
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "total": total,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Pending"
        })
        save_json(ORDERS_FILE, orders)
        st.success("✅ Order Placed Successfully!")
        st.session_state.cart = {}

        # Show feedback after placing order
        feedback = st.text_area("📝 Leave Feedback (optional)")
        if st.button("Submit Feedback") and feedback:
            feedbacks = load_json(FEEDBACK_FILE, [])
            feedbacks.append({
                "table": st.session_state.table_number,
                "message": feedback,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, feedbacks)
            st.success("✅ Thank you for your feedback!")

else:
    st.info("Your cart is empty.")