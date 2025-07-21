import streamlit as st
import json
import os
from datetime import datetime
from uuid import uuid4

st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# Hide sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .st-emotion-cache-1avcm0n { padding: 1rem; }
        .item-card {
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            padding: 16px;
            background: #ffffffcc;
            margin-bottom: 16px;
        }
        .cart-card {
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            padding: 16px;
            background: #f9fafb;
        }
        .stButton > button {
            background-color: #2563eb;
            color: white;
            border-radius: 6px;
            padding: 0.5rem 1rem;
        }
    </style>
""", unsafe_allow_html=True)

menu_file = "menu.json"
orders_file = "orders.json"
feedback_file = "feedback.json"

# Load Menu
if os.path.exists(menu_file):
    with open(menu_file, "r") as f:
        menu = json.load(f)
else:
    st.error("Menu file not found.")
    st.stop()

# Initialize session state
if "cart" not in st.session_state:
    st.session_state.cart = []

if "table" not in st.session_state:
    st.session_state.table = ""

st.title("🍽️ Welcome to Smart Table Ordering")
st.subheader("Browse Menu and Order")

st.text_input("Enter Table Number", key="table")

# Category Filter
categories = list(set([item["category"] for item in menu]))
selected_category = st.selectbox("Filter by Category", ["All"] + categories)

# Search
search_query = st.text_input("Search Menu")

# Display Menu
for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue
    if search_query and search_query.lower() not in item["name"].lower():
        continue

    with st.container():
        st.markdown(f"""
        <div class='item-card'>
        <h4>{item['name']} - ₹{item['price']}</h4>
        <p style='color: gray;'>{item['category']} | {'🌶️' if item.get('spicy') else ''} {'🥗' if item.get('veg') else '🍗'}</p>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(item.get("description", ""))
        with col2:
            qty_key = f"qty_{item['id']}"
            if qty_key not in st.session_state:
                st.session_state[qty_key] = 1
            st.number_input("Qty", min_value=1, step=1, key=qty_key)
            if st.button("Add to Cart", key=f"add_{item['id']}"):
                found = False
                for i in st.session_state.cart:
                    if i["id"] == item["id"]:
                        i["quantity"] += st.session_state[qty_key]
                        found = True
                        break
                if not found:
                    st.session_state.cart.append({
                        "id": item["id"],
                        "name": item["name"],
                        "price": item["price"],
                        "quantity": st.session_state[qty_key]
                    })
                st.success(f"✅ {item['name']} added to cart")

        st.markdown("</div>", unsafe_allow_html=True)

# Show Cart
st.markdown("---")
st.subheader("🛒 Cart")

if st.session_state.cart:
    with st.container():
        st.markdown("<div class='cart-card'>", unsafe_allow_html=True)
        total = 0
        for item in st.session_state.cart:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            col1.markdown(f"**{item['name']}**")
            if col2.button("➖", key=f"minus_{item['id']}"):
                item['quantity'] -= 1
                if item['quantity'] <= 0:
                    st.session_state.cart.remove(item)
            col3.markdown(f"Qty: {item['quantity']}")
            if col4.button("➕", key=f"plus_{item['id']}"):
                item['quantity'] += 1
            col5.markdown(f"₹{item['price'] * item['quantity']}")

        total = sum([item['price'] * item['quantity'] for item in st.session_state.cart])
        st.markdown(f"**Total: ₹{total}**")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✅ Place Order"):
            if not st.session_state.table:
                st.error("Please enter a table number.")
            else:
                order = {
                    "id": str(uuid4()),
                    "table": st.session_state.table,
                    "cart": st.session_state.cart,
                    "status": "Pending",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if os.path.exists(orders_file):
                    with open(orders_file, "r") as f:
                        orders = json.load(f)
                else:
                    orders = []

                orders.append(order)
                with open(orders_file, "w") as f:
                    json.dump(orders, f, indent=2)

                st.session_state.cart = []
                st.success("✅ Order Placed!")

else:
    st.info("Your cart is empty.")

st.markdown("---")
st.subheader("💬 Feedback")
feedback = st.text_area("Leave your message here")
if st.button("Send Feedback"):
    if not st.session_state.table:
        st.error("Enter table number to send feedback.")
    elif not feedback:
        st.warning("Message can't be empty.")
    else:
        entry = {
            "table": st.session_state.table,
            "message": feedback,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                feedbacks = json.load(f)
        else:
            feedbacks = []
        fee
