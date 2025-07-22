import streamlit as st
import json
import os
from datetime import datetime
import uuid

# ---------- Config ----------
st.set_page_config(page_title="Smart Menu", page_icon="🍽️", layout="wide")
BASE_DIR = os.getcwd()
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# ---------- Helpers ----------
def load_json(path, fallback=[]):
    if not os.path.exists(path):
        return fallback
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------- UI ----------
st.title("🍽️ Welcome to the Smart Café")

menu = load_json(MENU_FILE)
grouped = {}
for item in menu:
    grouped.setdefault(item["category"], []).append(item)

if "cart" not in st.session_state:
    st.session_state.cart = []

st.subheader("🧾 Browse Menu")
for category, items in grouped.items():
    st.markdown(f"### {category}")
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            st.markdown(f"**{item['name']}**  \n💵 ${item['price']:.2f}")
            if st.button(f"Add {item['name']}", key=f"add_{item['id']}"):
                st.session_state.cart.append(item)
                st.toast(f"{item['name']} added 🛒", icon="✅")

st.markdown("---")
st.subheader("🛒 Your Cart")
total = sum(i["price"] for i in st.session_state.cart)
for item in st.session_state.cart:
    st.markdown(f"- {item['name']} (${item['price']:.2f})")
st.markdown(f"**Total: ${total:.2f}**")

table = st.text_input("Table Number")
if st.button("📤 Place Order"):
    if not st.session_state.cart:
        st.warning("Your cart is empty!")
    elif not table.strip():
        st.warning("Enter a table number.")
    else:
        orders = load_json(ORDERS_FILE)
        new_order = {
            "order_id": str(uuid.uuid4())[:8],
            "table": table.strip(),
            "items": st.session_state.cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        save_json(ORDERS_FILE, orders)
        st.toast("✅ Order Placed!")
        st.success(f"Your order ID is `{new_order['order_id']}`")
        st.session_state.cart = []

        with st.expander("💬 Give Feedback"):
            rating = st.slider("Rating (1–5)", 1, 5)
            comment = st.text_area("Comment (optional)")
            if st.button("Submit Feedback"):
                feedback = load_json(FEEDBACK_FILE)
                feedback.append({
                    "order_id": new_order["order_id"],
                    "table": new_order["table"],
                    "rating": rating,
                    "comment": comment.strip(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                save_json(FEEDBACK_FILE, feedback)
                st.toast("💬 Feedback Submitted")
                st.success("Thank you!")
