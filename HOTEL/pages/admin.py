import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Admin Panel", page_icon="🛠️", layout="wide")

# ---------- Paths ----------
BASE_DIR = os.getcwd()
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# ---------- JSON Helpers ----------
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

# ---------- Manage Orders ----------
def manage_orders():
    st.header("📦 Manage Orders")
    orders = load_json(ORDERS_FILE)
    updated = False
    status_options = ["Pending", "Preparing", "Ready", "Served"]

    updated_orders = []

    for order in orders:
        with st.expander(f"🧾 Order {order.get('order_id', 'N/A')} - Table {order.get('table', 'N/A')} - Status: {order.get('status', 'Pending')}"):
            for item in order.get("items", []):
                st.markdown(f"- {item.get('name', 'Unnamed')} (${item.get('price', 0.0):.2f})")

            status = st.selectbox(
                "Update Status",
                status_options,
                index=status_options.index(order.get("status", "Pending")),
                key=f"status_{order.get('order_id')}"
            )

            if status != order.get("status"):
                order["status"] = status
                order["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = True
                st.toast(f"Status updated to {status}", icon="🔄")

            if status == "Served":
                if st.button("🗑️ Delete Order", key=f"delete_{order.get('order_id')}"):
                    st.toast("🗑️ Order deleted", icon="⚠️")
                    continue  # Skip saving this order
            updated_orders.append(order)

    if updated:
        save_json(ORDERS_FILE, updated_orders)

# ---------- View Feedback ----------
def view_feedback():
    st.header("💬 Customer Feedback")
    feedback = load_json(FEEDBACK_FILE)

    if not feedback:
        st.info("No feedback available.")
        return

    for entry in reversed(feedback):
        with st.container():
            st.markdown(f"**Order ID**: `{entry.get('order_id', 'N/A')}` | **Table**: `{entry.get('table', 'N/A')}`")
            st.markdown(f"⭐ **Rating**: {entry.get('rating', 0)}/5")
            comment = entry.get("comment", "").strip()
            if comment:
                st.markdown(f"💬 _{comment}_")
            st.markdown("---")

# ---------- Main ----------
def main():
    st.title("🛠️ Admin Dashboard")
    manage_orders()
    view_feedback()
    st_autorefresh(interval=10 * 1000, key="admin_refresh")

if __name__ == "__main__":
    main()
