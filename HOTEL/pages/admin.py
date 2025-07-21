import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
import os

# ====== File Paths ======
BASE_DIR = Path(__file__).resolve().parent.parent
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# ====== Utility Functions ======
def load_json(path):
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def delete_completed_orders(orders):
    return [o for o in orders if o["status"] != "Completed"]

# ====== UI Setup ======
st.set_page_config(page_title="Admin Panel", layout="wide")
hide_sidebar = """
    <style>
        [data-testid="stSidebar"] { display: none; }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

st.title("👨‍🍳 Smart Restaurant Admin Dashboard")
st.markdown("Monitoring all incoming orders with live updates every 5 seconds.")

# ====== Load Orders and Feedback ======
orders = load_json(ORDER_FILE)
feedback = load_json(FEEDBACK_FILE)

# ====== Order Management ======
latest_order_time = st.session_state.get("latest_order_time", None)
new_order_alert = False

for i, order in enumerate(orders):
    if not isinstance(order.get("cart"), list):
        continue  # skip malformed order

    with st.container(border=True):
        st.subheader(f"🧾 Order #{order['id']} - Table {order['table']}")
        st.markdown(f"**Status:** `{order['status']}`")
        if order["status"] == "Placed":
            new_order_alert = True

        for item in order["cart"]:
            st.write(f"- {item['name']} × {item['quantity']} = ₹{item['price'] * item['quantity']}")

        total = sum(item['price'] * item['quantity'] for item in order["cart"])
        st.markdown(f"### Total: ₹{total}")

        # Status buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🧑‍🍳 Start Preparing", key=f"prep_{i}"):
                order["status"] = "Preparing"
        with col2:
            if st.button("✅ Complete", key=f"done_{i}"):
                order["status"] = "Completed"
        with col3:
            if st.button("🗑️ Cancel", key=f"cancel_{i}"):
                orders.pop(i)
                save_json(ORDER_FILE, orders)
                st.experimental_rerun()

# ====== Show Feedback ======
if feedback:
    st.markdown("---")
    st.header("💬 Customer Feedback")
    for fb in reversed(feedback):
        with st.container(border=True):
            st.write(f"🪑 Table {fb['table']}")
            st.write(f"📝 {fb['feedback']}")
            st.caption(f"Submitted at {fb['time']}")

# ====== Save Updates ======
orders = delete_completed_orders(orders)
save_json(ORDER_FILE, orders)

# ====== Toast & Refresh ======
if new_order_alert:
    st.toast("🛎️ New order received!", icon="✅")

# Auto-refresh every 5 seconds
st.markdown(
    "<script>setTimeout(() => window.location.reload(), 5000);</script>",
    unsafe_allow_html=True,
)
