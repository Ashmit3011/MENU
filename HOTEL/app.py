import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Smart Table Ordering", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    </style>
""", unsafe_allow_html=True)

MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"
FEEDBACK_FILE = "feedback.json"

def load_menu():
    if not os.path.exists(MENU_FILE):
        return []
    with open(MENU_FILE, 'r') as f:
        return json.load(f)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, 'r') as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

def save_feedback(feedback):
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            existing = json.load(f)
    else:
        existing = []
    existing.append(feedback)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(existing, f, indent=4)

st.title("🍽️ Smart Table Ordering")
table_number = st.text_input("Enter Table Number")

menu = load_menu()
orders = load_orders()

tracking = st.toggle("Track My Order")

if not tracking:
    st.subheader("Browse Menu and Order")
    category = st.selectbox("Filter by Category", ["All"] + sorted(set(item["category"] for item in menu)))
    cart = []

    for item in menu:
        if category != "All" and item["category"] != category:
            continue
        with st.container():
            st.markdown(f"**{item['name']}** - ₹{item['price']}")
            qty = st.number_input(f"Qty for {item['name']}", min_value=0, step=1, key=item['name'])
            if qty > 0:
                cart.append({"name": item['name'], "qty": qty, "price": item['price']})

    if cart and st.button("Place Order"):
        order_id = f"ORD{int(datetime.now().timestamp())}"
        new_order = {
            "id": order_id,
            "table": table_number,
            "items": cart,
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        }
        orders.append(new_order)
        save_orders(orders)
        st.success(f"Order placed! Your ID: {order_id}")

    st.subheader("🛒 Cart")
    if cart:
        total = 0
        for item in cart:
            subtotal = item['qty'] * item['price']
            total += subtotal
            st.write(f"- {item['name']} × {item['qty']} = ₹{subtotal}")
        st.write(f"**Total: ₹{total}**")
    else:
        st.info("Your cart is empty.")

    st.subheader("💬 Feedback")
    feedback_msg = st.text_area("Leave your message here")
    if st.button("Submit Feedback"):
        save_feedback({
            "table": table_number,
            "message": feedback_msg,
            "timestamp": datetime.now().isoformat()
        })
        st.success("Thank you for your feedback!")

else:
    # Auto-refresh every 5 seconds using HTML meta tag
    st.markdown("""
        <meta http-equiv="refresh" content="5">
    """, unsafe_allow_html=True)

    st.subheader("Track Your Order")
    found = False

    for order in orders:
        if order["table"] == table_number:
            found = True
            st.write(f"🧾 **Order ID**: {order['id']}")
            st.write("🍽 **Items:**")
            for item in order["items"]:
                st.write(f"- {item['name']} × {item['qty']}")
            st.write(f"📦 **Status**: `{order['status']}`")
            st.caption(f"🕒 Placed at: {order['timestamp']}")
            break

    if not found:
        st.warning("No order found for this table.")

    st.caption(f"⏱️ Auto-refreshed at {datetime.now().strftime('%H:%M:%S')}")
