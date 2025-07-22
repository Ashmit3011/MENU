import streamlit as st
import os
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------- File Paths ----------
BASE_DIR = os.getcwd()
MENU_PATH = os.path.join(BASE_DIR, "menu.json")
ORDERS_PATH = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_PATH = os.path.join(BASE_DIR, "feedback.json")

st.set_page_config(page_title="Admin Panel", page_icon="🛠️", layout="wide")
st.title("🛠️ Admin Dashboard")

# ---------- JSON Helpers ----------
def load_json(path, fallback=[]):
    if not os.path.exists(path):
        return fallback
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return fallback

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ---------- Orders Management ----------
def manage_orders():
    st.subheader("📦 Manage Orders")
    orders = load_json(ORDERS_PATH)
    status_options = ["Pending", "Preparing", "Ready", "Served"]

    if not orders:
        st.info("No orders found.")
        return

    updated = False
    for index, order in enumerate(orders):
        order_id = order.get("order_id", "Unknown")
        table = order.get("table", "N/A")
        status = order.get("status", "Pending")

        with st.expander(f"🧾 Order {order_id} - Table {table} - Status: {status}"):
            for item in order.get('items', []):
                st.markdown(f"- **{item.get('name', 'Unnamed')}** (${item.get('price', 0.0):.2f})")

            new_status = st.selectbox("Update Status", status_options, index=status_options.index(status), key=order_id)
            if new_status != status:
                order['status'] = new_status
                order['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated = True
                st.toast(f"✅ Status updated to {new_status}", icon="🔄")

            if status == "Served" and st.button("🗑️ Delete Order", key=f"delete_{order_id}"):
                del orders[index]
                save_json(ORDERS_PATH, orders)
                st.toast("🗑️ Order deleted", icon="❌")
                st.rerun()

    if updated:
        save_json(ORDERS_PATH, orders)

# ---------- Menu Management ----------
def manage_menu():
    st.subheader("📋 Manage Menu")
    menu = load_json(MENU_PATH)

    for item in menu:
        with st.expander(f"{item['name']} (${item['price']:.2f}) - {item['category']}"):
            item['name'] = st.text_input("Name", item['name'], key=f"name_{item['id']}")
            item['price'] = st.number_input("Price", value=float(item['price']), key=f"price_{item['id']}")
            item['category'] = st.text_input("Category", item['category'], key=f"cat_{item['id']}")

    if st.button("💾 Save Menu Changes"):
        save_json(MENU_PATH, menu)
        st.toast("✅ Menu updated", icon="🍽️")
        st.rerun()

# ---------- Feedback Viewer ----------
def view_feedback():
    st.subheader("💬 Customer Feedback")
    feedback = load_json(FEEDBACK_PATH)

    if not feedback:
        st.info("No feedback submitted yet.")
        return

    for fb in feedback:
        with st.expander(f"📝 Table {fb['table']} | Order {fb['order_id']} | ⭐ {fb['rating']}"):
            st.write(fb['comment'])

# ---------- Render Everything ----------
def main():
    st_autorefresh(interval=10 * 1000, key="admin_refresh")
    manage_orders()
    st.divider()
    manage_menu()
    st.divider()
    view_feedback()

main()
