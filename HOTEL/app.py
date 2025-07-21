import streamlit as st
import json
import os
from datetime import datetime

# === File Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# === Utility Functions ===
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

def save_order(order):
    orders = []
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_feedback(feedback):
    all_feedback = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            all_feedback = json.load(f)
    all_feedback.append(feedback)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(all_feedback, f, indent=2)

def get_latest_order(table_no, orders):
    for order in reversed(orders):
        if order["table"] == table_no:
            return order
    return None

# === Streamlit Setup ===
st.set_page_config(page_title="Smart Table Ordering", layout="centered")
st.title("🍽️ Smart Table Ordering")

menu = load_menu()

# === Session Init ===
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
    st.session_state.table_no = ""

# === Order Not Yet Placed ===
if not st.session_state.order_placed:
    st.markdown("#### Select your dishes")

    # Show menu as mobile-friendly cards
    for category, items in menu.items():
        st.markdown(f"### 🔸 {category}")
        for item in items:
            with st.container():
                veg_icon = "🥦" if item["veg"] else "🍗"
                spicy_icon = "🌶️" if item["spicy"] else ""
                popular_icon = "⭐" if item["popular"] else ""
                st.markdown(f"**{item['name']}** {veg_icon}{spicy_icon}{popular_icon}")
                st.markdown(f"💰 ₹{item['price']}")

                qty = st.number_input(f"Qty for {item['name']}", min_value=0, max_value=10, value=0, key=f"qty_{item['id']}")
                if qty > 0:
                    st.session_state.cart[item["id"]] = {"item": item, "qty": qty}
                elif item["id"] in st.session_state.cart:
                    del st.session_state.cart[item["id"]]

    # Sticky cart bar
    total = sum(entry["item"]["price"] * entry["qty"] for entry in st.session_state.cart.values())
    if total > 0:
        st.markdown("---")
        st.markdown(f"### 🛒 Cart Total: ₹{total}")
        for entry in st.session_state.cart.values():
            item = entry["item"]
            qty = entry["qty"]
            st.markdown(f"- {item['name']} x {qty} = ₹{item['price'] * qty}")

        st.markdown("---")
        table_no = st.text_input("Enter your Table Number", key="input_table")

        if st.button("✅ Place Order"):
            if not table_no:
                st.warning("Enter a valid table number.")
            else:
                order = {
                    "table": table_no,
                    "items": [
                        {"name": e["item"]["name"], "qty": e["qty"], "price": e["item"]["price"]}
                        for e in st.session_state.cart.values()
                    ],
                    "total": total,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Pending"
                }
                save_order(order)
                st.session_state.order_placed = True
                st.session_state.table_no = table_no
                st.session_state.cart = {}
                st.success("🎉 Order placed successfully!")

# === Order Placed: Show Status and Feedback ===
if st.session_state.order_placed:
    st.markdown("---")
    st.subheader("📦 Track Your Order")

    orders = load_orders()
    latest = get_latest_order(st.session_state.table_no, orders)

    if latest:
        st.markdown(f"**Table:** {latest['table']}  \n⏰ **Time:** {latest['time']}")
        st.markdown("### 🔄 Status Progress:")

        status_steps = ["Pending", "Preparing", "Ready", "Served"]
        current_idx = status_steps.index(latest["status"])
        for i, step in enumerate(status_steps):
            if i < current_idx:
                st.success(f"✅ {step}")
            elif i == current_idx:
                st.warning(f"🔄 {step}")
            else:
                st.info(f"⏳ {step}")

        # Feedback when order is Served
        if latest["status"] == "Served":
            st.markdown("---")
            st.subheader("📝 Share Your Feedback")
            rating = st.slider("Rating (1–5)", 1, 5, 5)
            comment = st.text_area("Your comments")
            if st.button("Submit Feedback"):
                save_feedback({
                    "table": latest["table"],
                    "rating": rating,
                    "comment": comment,
                    "time": latest["time"]
                })
                st.success("🙏 Thank you! Feedback submitted.")
                st.session_state.order_placed = False
                st.session_state.table_no = ""

    else:
        st.error("No order found.")

    # Auto-refresh every 5 seconds
    st.markdown("<script>setTimeout(() => location.reload(), 5000);</script>", unsafe_allow_html=True)
