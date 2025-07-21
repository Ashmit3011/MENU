import streamlit as st
import json
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# Load menu
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

# Save order
def save_order(order):
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    else:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# Save feedback
def save_feedback(feedback):
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            all_feedback = json.load(f)
    else:
        all_feedback = []
    all_feedback.append(feedback)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(all_feedback, f, indent=2)

# Load orders
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

# Get last order for a table
def get_latest_order(table_no, orders):
    for order in reversed(orders):
        if order["table"] == table_no:
            return order
    return None

# Streamlit setup
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.title("📋 Smart Table Ordering System")

menu = load_menu()
if "cart" not in st.session_state:
    st.session_state.cart = {}

if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
    st.session_state.table_no = ""
    st.session_state.order_id = None

# Show menu
if not st.session_state.order_placed:
    st.markdown("### 🍽️ Browse the Menu")
    tabs = st.tabs(list(menu.keys()))

    for category in menu:
        with tabs[list(menu.keys()).index(category)]:
            for item in menu[category]:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                with col1:
                    flags = ""
                    if item.get("veg"): flags += "🥦"
                    else: flags += "🍗"
                    if item.get("spicy"): flags += " 🌶️"
                    if item.get("popular"): flags += " ⭐"
                    st.markdown(f"**{item['name']}** {flags}")
                with col2:
                    st.markdown(f"₹{item['price']}")
                with col3:
                    qty = st.number_input(
                        f"Qty ({item['id']})", min_value=0, max_value=10, value=0, key=f"qty_{item['id']}"
                    )
                with col4:
                    if qty > 0:
                        st.session_state.cart[item["id"]] = {"item": item, "qty": qty}
                    elif item["id"] in st.session_state.cart:
                        del st.session_state.cart[item["id"]]

    # Cart Summary
    st.markdown("---")
    st.markdown("### 🛒 Cart Summary")

    if st.session_state.cart:
        total = 0
        for entry in st.session_state.cart.values():
            item = entry["item"]
            qty = entry["qty"]
            subtotal = item["price"] * qty
            total += subtotal
            st.write(f"{item['name']} x {qty} = ₹{subtotal}")
        st.markdown(f"### 💰 Total: ₹{total}")
    else:
        st.info("Cart is empty.")

    # Place Order
    st.markdown("---")
    table_no = st.text_input("Enter Table Number", max_chars=5)

    if st.button("✅ Place Order"):
        if not table_no:
            st.warning("Please enter a table number.")
        elif not st.session_state.cart:
            st.warning("Your cart is empty.")
        else:
            order = {
                "table": table_no,
                "items": [
                    {"name": entry["item"]["name"], "qty": entry["qty"], "price": entry["item"]["price"]}
                    for entry in st.session_state.cart.values()
                ],
                "total": sum(entry["item"]["price"] * entry["qty"] for entry in st.session_state.cart.values()),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Pending"
            }
            save_order(order)
            st.session_state.cart = {}
            st.session_state.order_placed = True
            st.session_state.table_no = table_no
            st.success("🎉 Order placed successfully! You can now track it below.")

# Order Tracking & Feedback
if st.session_state.order_placed:
    st.markdown("---")
    st.subheader("📦 Track Your Order")

    orders = load_orders()
    latest = get_latest_order(st.session_state.table_no, orders)

    if latest:
        st.markdown(f"**Table:** {latest['table']}  \n**Time:** {latest['time']}  \n**Total:** ₹{latest['total']}")

        status_levels = ["Pending", "Preparing", "Ready", "Served"]
        current_idx = status_levels.index(latest["status"])

        st.markdown("### 🔄 Order Status:")
        for i, stage in enumerate(status_levels):
            if i < current_idx:
                st.success(f"✅ {stage}")
            elif i == current_idx:
                st.warning(f"🔄 {stage}")
            else:
                st.info(f"⏳ {stage}")

        # Feedback section (only if Served)
        if latest["status"] == "Served":
            st.markdown("---")
            st.subheader("📝 Share Your Feedback")

            rating = st.slider("How would you rate your experience?", 1, 5, 4)
            comment = st.text_area("Any comments?")

            if st.button("Submit Feedback"):
                feedback = {
                    "table": latest["table"],
                    "time": latest["time"],
                    "rating": rating,
                    "comment": comment
                }
                save_feedback(feedback)
                st.success("🙏 Thank you for your feedback!")
                st.session_state.order_placed = False
                st.session_state.table_no = ""

    else:
        st.error("❌ No active order found.")

# Auto-refresh every 5s if tracking
if st.session_state.order_placed:
    st.markdown("<script>setTimeout(() => location.reload(), 5000);</script>", unsafe_allow_html=True)
