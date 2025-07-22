import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

# ------------------ Setup ------------------
st.set_page_config(page_title="Admin Panel", layout="wide", page_icon="🛠️")
BASE_DIR = os.getcwd()
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# ------------------ JSON Helpers ------------------
def load_json(path, fallback=[]):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {path}: {e}")
        return fallback

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ------------------ Admin Panel ------------------
def admin_panel():
    password = st.text_input("Enter admin password", type="password")
    if password != "admin123":
        st.warning("Unauthorized access")
        st.stop()

    st.title("🛠️ Admin Dashboard")

    # Orders Section
    st.header("📦 Manage Orders")
    orders = load_json(ORDERS_FILE)
    updated = False

    for order in orders:
        with st.expander(f"🧾 Order {order.get('order_id')} | Table: {order.get('table')} | Status: {order.get('status')}"):
            for item in order.get("items", []):
                st.markdown(f"- {item.get('name')} (${item.get('price'):.2f})")

            status = st.selectbox(
                "Update Status",
                ["Pending", "Preparing", "Ready", "Served"],
                index=["Pending", "Preparing", "Ready", "Served"].index(order.get("status", "Pending")),
                key=f"status_{order.get('order_id')}"
            )

            if status != order.get("status"):
                order["status"] = status
                updated = True
                st.toast(f"Status updated to {status}", icon="🔄")

            if status == "Served":
                if st.button("🗑️ Delete Order", key=f"delete_{order.get('order_id')}"):
                    orders.remove(order)
                    updated = True
                    st.toast("🗑️ Order deleted", icon="⚠️")
                    st.rerun()

    if updated:
        save_json(ORDERS_FILE, orders)

    # Feedback Section
    st.header("💬 Customer Feedback")
    feedback = load_json(FEEDBACK_FILE)
    if not feedback:
        st.info("No feedback available.")
    else:
        for entry in feedback:
            with st.container():
                st.markdown(f"**Order ID**: {entry.get('order_id')} | **Table**: {entry.get('table')} | ⭐ {entry.get('rating', 0)}/5")
                st.markdown(f"_Comment_: {entry.get('comment', '')}")
                st.markdown("---")

    st_autorefresh(interval=10 * 1000, key="admin_refresh")

# ------------------ Run ------------------
admin_panel()
