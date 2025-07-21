import streamlit as st
import json
import uuid
from pathlib import Path
from datetime import datetime
import os

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# ---------- Utility Functions ----------
def load_json(file_path):
    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---------- Hide Sidebar ----------
st.set_page_config(page_title="Smart Café", layout="wide")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ---------- Load Menu ----------
menu = load_json(MENU_FILE)

# ---------- Cart State ----------
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_id" not in st.session_state:
    st.session_state.order_id = None

# ---------- Category Tabs ----------
categories = sorted(list(set(item["category"] for item in menu)))
tab_objs = st.tabs(categories)

for cat, tab in zip(categories, tab_objs):
    with tab:
        for item in [i for i in menu if i["category"] == cat]:
            st.markdown(
                f"""
                <div style='border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); padding: 1rem; margin: 0.5rem 0; background: white;'>
                    <h4>{item['name']} {'🌶️' if item.get('spicy') else ''} {'🥦' if item.get('veg') else '🍗'}</h4>
                    <p>₹{item['price']}</p>
                    <form action='' method='post'>
                        <button type="submit" name="add_{item['id']}" style="background-color:#eee;">➕</button>
                    </form>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("➕", key=f"add_{item['id']}_cart"):
                st.session_state.cart[item["id"]] = st.session_state.cart.get(item["id"], 0) + 1
                st.success(f"Added {item['name']} to cart")

# ---------- Your Cart ----------
st.markdown("### 🛒 Your Cart")
cart = st.session_state.cart
if not cart:
    st.info("Your cart is empty.")
else:
    total = 0
    for item_id, qty in cart.items():
        item = next((i for i in menu if i["id"] == item_id), None)
        if not item:
            continue
        item_total = item["price"] * qty
        total += item_total
        with st.container():
            st.markdown(
                f"""
                <div style='border-radius: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); background: #fff; padding: 1rem; margin-bottom: 1rem;'>
                    <b>{item['name']}</b><br>
                    💰 ₹{item['price']} x {qty} = ₹{item_total}
                </div>
                """,
                unsafe_allow_html=True
            )
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("➕", key=f"inc_{item_id}"):
                    cart[item_id] += 1
            with col2:
                if st.button("➖", key=f"dec_{item_id}"):
                    cart[item_id] -= 1
                    if cart[item_id] <= 0:
                        del cart[item_id]

    st.markdown(f"### 🧾 Total: ₹{total}")
    table_number = st.text_input("Enter Table Number")
    if st.button("🛎️ Place Order", use_container_width=True):
        if not table_number:
            st.error("Please enter table number")
        elif not cart:
            st.warning("Your cart is empty.")
        else:
            order = {
                "id": str(uuid.uuid4())[:8],
                "table": table_number,
                "items": [{"id": k, "qty": v} for k, v in cart.items()],
                "timestamp": datetime.now().isoformat(),
                "status": "Received",
                "feedback": ""
            }
            orders = load_json(ORDER_FILE)
            orders.append(order)
            save_json(ORDER_FILE, orders)
            st.session_state.order_id = order["id"]
            st.session_state.cart = {}
            st.success("Order Placed Successfully!")
            st.balloons()

# ---------- Order Tracking ----------
if st.session_state.order_id:
    st.markdown("## 🧭 Order Tracking")
    orders = load_json(ORDER_FILE)
    order = next((o for o in orders if o["id"] == st.session_state.order_id), None)
    if order:
        st.markdown(f"🆔 Order ID: `{order['id']}`  |  Table: `{order['table']}`")
        st.progress(["Received", "Preparing", "Served"].index(order["status"]) / 2.0)

        if order["status"] == "Received":
            if st.button("❌ Cancel Order"):
                orders = [o for o in orders if o["id"] != order["id"]]
                save_json(ORDER_FILE, orders)
                st.session_state.order_id = None
                st.warning("Order Cancelled")
        elif order["status"] == "Served" and not order.get("feedback_submitted"):
            st.markdown("### 🗣️ Give Feedback")
            feedback = st.text_area("How was the food and service?")
            if st.button("✅ Submit Feedback"):
                all_feedback = load_json(FEEDBACK_FILE)
                all_feedback.append({
                    "order_id": order["id"],
                    "table": order["table"],
                    "feedback": feedback,
                    "timestamp": datetime.now().isoformat()
                })
                save_json(FEEDBACK_FILE, all_feedback)
                for o in orders:
                    if o["id"] == order["id"]:
                        o["feedback_submitted"] = True
                save_json(ORDER_FILE, orders)
                st.success("Thanks for your feedback!")
