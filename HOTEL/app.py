import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid

# Set page config
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# File paths
BASE_DIR = Path(__file__).parent.resolve()
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# Load JSON safely
def load_json(path):
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Load menu
menu = load_json(MENU_FILE)

# Title
st.title("🍽️ Smart Table Ordering System")

# Get table number
table_number = st.text_input("Enter your Table Number:", key="table_input")
if not table_number:
    st.warning("Please enter your table number to start ordering.")
    st.stop()

# Initialize cart
if "cart" not in st.session_state:
    st.session_state.cart = []

# Food categories
categories = sorted(set(item.get("category", "Others") for item in menu))
selected_category = st.selectbox("Choose Category", ["All"] + categories)

# Search bar
search_query = st.text_input("🔍 Search Menu")

# Filter menu
filtered_menu = [
    item for item in menu
    if (selected_category == "All" or item.get("category") == selected_category)
    and (search_query.lower() in item.get("name", "").lower())
]

# Display menu items
st.subheader("🍔 Menu")
if not filtered_menu:
    st.info("No items match your filter.")
else:
    for item in filtered_menu:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item['name']}**  — ₹{item['price']}")
            labels = []
            if item.get("is_veg"):
                labels.append("🥦 Veg")
            else:
                labels.append("🍗 Non-Veg")
            if item.get("spicy"):
                labels.append("🌶 Spicy")
            if item.get("popular"):
                labels.append("🔥 Popular")
            st.caption(" • ".join(labels))
        with col2:
            qty = st.number_input(f"Qty for {item['name']}", min_value=0, max_value=10, value=0, key=item['name'])
            if qty > 0:
                st.session_state.cart.append({
                    "name": item["name"],
                    "price": item["price"],
                    "qty": qty
                })

# Cart Summary
st.markdown("---")
st.subheader("🛒 Your Cart")

if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        st.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']
    st.write(f"**Total: ₹{total}**")

    if st.button("✅ Place Order"):
        new_order = {
            "id": str(uuid.uuid4())[:8],
            "table": table_number,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cart": st.session_state.cart,
            "status": "Pending"
        }
        existing_orders = load_json(ORDERS_FILE)
        existing_orders.append(new_order)
        save_json(ORDERS_FILE, existing_orders)
        st.success("✅ Order Placed Successfully!")
        st.session_state.cart = []

        # Optionally ask for feedback
        st.markdown("---")
        st.header("💬 Leave Feedback")
        rating = st.slider("Rate your experience", 1, 5, 4)
        comments = st.text_area("Comments (optional)")
        if st.button("Submit Feedback"):
            feedbacks = load_json(FEEDBACK_FILE)
            feedbacks.append({
                "table": table_number,
                "rating": rating,
                "comments": comments,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, feedbacks)
            st.success("🙌 Thank you for your feedback!")
else:
    st.info("Your cart is empty.")
