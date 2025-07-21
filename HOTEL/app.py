import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Set page config
st.set_page_config(page_title="Smart Menu", layout="wide")

# File paths
BASE_DIR = Path("/mnt/data")
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# Load menu
def load_menu():
    if MENU_FILE.exists():
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save order
def save_order(order):
    orders = []
    if ORDERS_FILE.exists():
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                orders = json.load(f)
        except json.JSONDecodeError:
            orders = []
    order["id"] = len(orders) + 1
    order["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order["status"] = "Pending"
    orders.append(order)
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

# Save feedback
def save_feedback(feedback):
    feedbacks = []
    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)
        except json.JSONDecodeError:
            feedbacks = []
    feedback["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedbacks.append(feedback)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

# UI
st.title("🍽️ Smart Restaurant Ordering")
menu_data = load_menu()

# Filter categories
categories = sorted(list(set(item["category"] for item in menu_data)))
selected_category = st.selectbox("Select Category", categories)

# Table number
table_number = st.text_input("Enter Your Table Number", "")

# Cart management
cart = []
st.subheader("Menu Items")

for item in menu_data:
    if item["category"] != selected_category:
        continue
    cols = st.columns([3, 1, 1])
    with cols[0]:
        st.write(f"**{item['name']}** - ₹{item['price']}")
        st.caption(f"{item.get('description', '')}")
    with cols[1]:
        qty = st.number_input(
            f"Qty for {item['name']}", min_value=0, max_value=10, step=1, key=f"qty_{item['name']}"
        )
    with cols[2]:
        if qty > 0:
            cart.append({
                "name": item["name"],
                "price": item["price"],
                "qty": qty
            })

# Show cart
st.markdown("---")
st.subheader("🛒 Your Cart")
if cart:
    total = sum(item["price"] * item["qty"] for item in cart)
    for item in cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['price'] * item['qty']}")
    st.write(f"**Total: ₹{total}**")

    if table_number.strip() == "":
        st.warning("Please enter your table number before placing the order.")
    elif st.button("✅ Place Order"):
        save_order({
            "table": table_number,
            "cart": cart,
        })
        st.success("🎉 Order placed successfully!")
        st.experimental_rerun()
else:
    st.info("No items in cart yet.")

# Feedback section
st.markdown("---")
st.subheader("💬 Give Feedback")
with st.form("feedback_form"):
    rating = st.slider("Rate your experience (1 to 5)", 1, 5, 4)
    comments = st.text_area("Additional comments")
    if st.form_submit_button("Submit Feedback"):
        if table_number.strip() == "":
            st.warning("Enter table number to submit feedback.")
        else:
            save_feedback({
                "table": table_number,
                "rating": rating,
                "comments": comments
            })
            st.success("🙏 Thanks for your feedback!")
