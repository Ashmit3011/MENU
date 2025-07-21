import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# Page config
st.set_page_config(page_title="Smart Table Ordering", layout="wide", initial_sidebar_state="collapsed")

# Helper functions
def load_json(file):
    if not file.exists():
        file.write_text("[]", encoding="utf-8")
    with open(file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Load menu and orders
menu = load_json(MENU_FILE)
orders = load_json(ORDER_FILE)

# Session state
if "cart" not in st.session_state:
    st.session_state.cart = []
if "order_id" not in st.session_state:
    st.session_state.order_id = len(orders) + 1

# Hide sidebar
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] { display: none !important; }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# --- UI ---
st.title("🍽️ Welcome to Smart Table Ordering")
table_number = st.text_input("Enter your Table Number", max_chars=5)

st.markdown("### 🧾 Menu")
categories = sorted(set(item["category"] for item in menu))
selected_category = st.selectbox("Filter by Category", ["All"] + categories)

# Menu display
for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"{item['name']} {'🌶️' if item.get('spicy') else ''}")
        st.caption(f"₹{item['price']} | {'🥬 Veg' if item.get('veg') else '🍗 Non-Veg'}")
    with col2:
        qty = st.number_input(f"Qty for {item['id']}", min_value=0, step=1, key=item['id'])
        if qty > 0:
            st.session_state.cart.append({**item, "qty": qty})

# Cart
if st.session_state.cart:
    st.markdown("### 🛒 Your Cart")
    total = 0
    for item in st.session_state.cart:
        line_total = item["qty"] * item["price"]
        total += line_total
        st.write(f"- {item['name']} x {item['qty']} = ₹{line_total}")
    st.write(f"**Total: ₹{total}**")

    if total >= 300:
        st.success("🎉 You earned a free dessert!")

    if st.button("✅ Place Order"):
        if not table_number.strip():
            st.warning("Please enter your table number.")
        else:
            orders.append({
                "id": st.session_state.order_id,
                "table": table_number.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cart": st.session_state.cart,
                "status": "Pending"
            })
            save_json(ORDER_FILE, orders)
            st.success("✅ Order placed successfully!")
            st.balloons()
            st.session_state.order_id += 1
            st.session_state.cart = []

# Order tracker
st.markdown("---")
st.header("🔎 Track Your Order")
track_id = st.number_input("Enter your Order ID", min_value=1, step=1)
matching_order = next((o for o in orders if o["id"] == track_id), None)
if matching_order:
    st.info(f"🪑 Table: {matching_order['table']} | 📦 Status: `{matching_order['status']}`")
    st.progress(
        {
            "Pending": 0.25,
            "Preparing": 0.5,
            "Served": 0.75,
            "Completed": 1.0
        }.get(matching_order["status"], 0.0)
    )
else:
    st.caption("Enter your order ID to track status.")

# Feedback
st.markdown("---")
st.header("💬 Leave Feedback")
rating = st.slider("Rate your experience", 1, 5, 4)
comments = st.text_area("Your comments")
feedback_table = st.text_input("Enter your Table Number again")

if st.button("📩 Submit Feedback"):
    feedbacks = load_json(FEEDBACK_FILE)
    feedbacks.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rating": rating,
        "comments": comments,
        "table": feedback_table.strip()
    })
    save_json(FEEDBACK_FILE, feedbacks)
    st.toast("Thanks for your feedback!", icon="💌")
