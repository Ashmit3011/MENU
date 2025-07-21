import streamlit as st
import json
import os
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDER_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- Utility functions ---
def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        return json.loads(content) if content else []

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_order_id():
    orders = load_json(ORDER_FILE)
    return len(orders) + 1

# --- Session state ---
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "last_status" not in st.session_state:
    st.session_state.last_status = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

# --- Header ---
st.title("🍽️ Smart Table Ordering")
st.info("🎉 Free Donut with orders above ₹200!")

# --- Table number ---
table_input = st.text_input("Enter Table Number", value=st.session_state.table)
st.session_state.table = table_input.strip()

# --- Load Menu ---
menu = load_json(MENU_FILE)
categories = sorted(set(item.get("category", "Uncategorized") for item in menu))

if categories:
    tabs = st.tabs(categories)
    for i, cat in enumerate(categories):
        with tabs[i]:
            st.subheader(f"{cat} Menu")
            for item in [m for m in menu if m.get("category") == cat]:
                tags = ""
                if item.get("spicy"): tags += " 🌶️"
                if item.get("veg"): tags += " 🥦"
                if item.get("popular"): tags += " ⭐"
                with st.container():
                    st.markdown(f"**{item['name']}** {tags}")
                    st.caption(f"₹{item['price']}")
                    qty = st.number_input(f"Qty - {item['name']}", min_value=0, step=1, key=f"qty_{item['id']}")
                    if qty > 0:
                        existing = next((c for c in st.session_state.cart if c['id'] == item['id']), None)
                        if existing:
                            existing['qty'] = qty
                        else:
                            st.session_state.cart.append({
                                "id": item["id"],
                                "name": item["name"],
                                "price": item["price"],
                                "qty": qty
                            })
else:
    st.warning("No categories found in menu.json.")

# --- Cart Summary ---
st.markdown("## 🛒 Your Cart")
total = 0
if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']
    st.markdown(f"**Total: ₹{total}**")
    if total >= 200:
        st.success("🎉 Free Donut will be added!")

    if st.button("✅ Place Order"):
        if not st.session_state.table:
            st.error("Please enter your table number.")
        else:
            new_order = {
                "id": generate_order_id(),
                "table": st.session_state.table,
                "cart": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders = load_json(ORDER_FILE)
            orders.append(new_order)
            save_json(ORDER_FILE, orders)
            st.success("✅ Order placed successfully!")
            st.session_state.order_id = new_order["id"]
            st.session_state.cart = []
            st.session_state.feedback_given = False
            st.rerun()
else:
    st.info("Your cart is empty.")

# --- Order Tracking ---
if st.session_state.order_id:
    st.markdown("---")
    st.header("🔍 Track Your Order")
    orders = load_json(ORDER_FILE)
    order = next((o for o in orders if o["id"] == st.session_state.order_id), None)
    if order:
        if order["status"] != st.session_state.last_status:
            st.toast(f"📢 Status updated: {order['status']}")
            st.session_state.last_status = order["status"]

        st.success(f"Order #{order['id']} for Table {order['table']}")
        st.markdown(f"**Status:** `{order['status']}`")

        # Progress
        stages = ["Pending", "Preparing", "Served", "Completed"]
        current = stages.index(order["status"]) if order["status"] in stages else 0
        st.progress((current + 1) / len(stages), text=order["status"])

        with st.expander("🧾 View Order"):
            total = 0
            for item in order["cart"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                total += item['qty'] * item['price']
            st.markdown(f"**Total: ₹{total}**")

        # Feedback form
        if order["status"] == "Completed" and not st.session_state.feedback_given:
            st.markdown("### 💬 Leave Feedback")
            rating = st.slider("Rate your experience", 1, 5, 4)
            comments = st.text_area("Comments")
            if st.button("Submit Feedback"):
                feedback = load_json(FEEDBACK_FILE)
                feedback.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "table": order["table"],
                    "rating": rating,
                    "comments": comments
                })
                save_json(FEEDBACK_FILE, feedback)
                st.success("✅ Feedback submitted!")
                st.session_state.feedback_given = True

    # Auto-refresh
    st.markdown("""
        <script>
            setTimeout(() => window.location.reload(), 5000);
        </script>
    """, unsafe_allow_html=True)
