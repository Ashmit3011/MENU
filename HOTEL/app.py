# ---------- app.py (Customer Panel) ----------

import streamlit as st
import json
import os
from datetime import datetime
import uuid
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Smart Menu", page_icon="🍽️", layout="wide")

BASE_DIR = os.getcwd()
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

def load_json(path, fallback=[]):
    if not os.path.exists(path):
        return fallback
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

menu = load_json(MENU_FILE)

if "cart" not in st.session_state:
    st.session_state.cart = []

st.title("🍽️ Welcome to the Smart Café")

# Group menu items
grouped = {}
for item in menu:
    grouped.setdefault(item["category"], []).append(item)

st.subheader("📟️ Browse Menu")
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
        st.session_state.last_order_id = new_order["order_id"]

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

# Real-Time Order Tracking
if "last_order_id" in st.session_state:
    st.markdown("---")
    st.subheader("⏱️ Track Your Order in Real-Time")
    st_autorefresh(interval=10 * 1000, key="order_status_refresh")

    orders = load_json(ORDERS_FILE)
    current_order = next((o for o in orders if o["order_id"] == st.session_state.last_order_id), None)

    if current_order:
        st.markdown(f"**Order ID:** `{current_order['order_id']}`")
        st.markdown(f"**Table:** `{current_order['table']}`")
        st.markdown(f"**Status:** 🟢 `{current_order['status']}`")
        st.markdown(f"**Placed At:** {current_order['timestamp']}")
        st.markdown("**Items:**")
        for item in current_order["items"]:
            st.markdown(f"- {item['name']} (${item['price']:.2f})")
        if current_order["status"] == "Served":
            st.success("✅ Your order has been served! Enjoy your meal!")
    else:
        st.warning("❗ Could not find your order.")


# ---------- admin.py (Admin Panel) ----------

import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Admin Panel", page_icon="🛠️", layout="wide")

BASE_DIR = os.getcwd()
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

def load_json(path, fallback=[]):
    if not os.path.exists(path):
        return fallback
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def manage_orders():
    st.header("📦 Manage Orders")
    orders = load_json(ORDERS_FILE)
    updated = False
    new_orders = []
    statuses = ["Pending", "Preparing", "Ready", "Served"]

    for order in orders:
        with st.expander(f"Order {order['order_id']} (Table {order['table']}) – {order['status']}"):
            for it in order["items"]:
                st.markdown(f"- {it['name']} (${it['price']:.2f})")
            status = st.selectbox("Update status", statuses, index=statuses.index(order["status"]), key=f"stat_{order['order_id']}")
            if status != order["status"]:
                order["status"] = status
                order["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = True
                st.toast(f"Status: {status}", icon="🔄")
            if status == "Served" and st.button("🗑️ Delete", key=f"del_{order['order_id']}"):
                st.toast("Order deleted", icon="⚠️")
                continue
            new_orders.append(order)

    if updated:
        save_json(ORDERS_FILE, new_orders)

def view_feedback():
    st.header("💬 Customer Feedback")
    fb = load_json(FEEDBACK_FILE)
    if not fb:
        st.info("No feedback yet.")
        return
    for e in reversed(fb):
        st.markdown(f"**Order ID**: `{e['order_id']}` | Table: `{e['table']}`")
        st.markdown(f"⭐ Rating: {e['rating']}/5")
        if e.get("comment"):
            st.markdown(f"💬 {e['comment']}")
        st.markdown("---")

def main():
    st.title("🛠️ Admin Dashboard")
    manage_orders()
    view_feedback()
    st_autorefresh(interval=10000, key="refresh")

if __name__ == "__main__":
    main()
