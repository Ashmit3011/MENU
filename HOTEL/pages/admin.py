import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ------------------ Setup ------------------
st.set_page_config(page_title="Smart Café", layout="wide")
BASE_DIR = os.getcwd()
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
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

    # Orders
    st.header("📦 Manage Orders")
    orders = load_json(ORDERS_FILE)
    updated = False

    for order in orders:
        with st.expander(f"🧾 Order {order.get('order_id', 'N/A')} - Table {order.get('table', 'N/A')} - Status: {order.get('status', 'N/A')}"):
            for item in order.get("items", []):
                st.markdown(f"- {item.get('name', 'Unnamed')} (${item.get('price', 0.0):.2f})")

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

    # Feedback
    st.header("💬 Customer Feedback")
    feedback = load_json(FEEDBACK_FILE)
    if not feedback:
        st.info("No feedback available.")
    else:
        for entry in feedback:
            with st.container():
                st.markdown(f"**Order ID**: {entry.get('order_id', 'N/A')} | **Table**: {entry.get('table', 'N/A')} | ⭐ {entry.get('rating', 0)}/5")
                st.markdown(f"_Comment_: {entry.get('comment', '')}")
                st.markdown("---")

    st_autorefresh(interval=10 * 1000, key="admin_refresh")

# ------------------ Customer Panel ------------------
def customer_panel():
    st.title("🍽️ Welcome to Smart Café")

    menu = load_json(MENU_FILE)
    if not menu:
        st.error("Menu is empty or failed to load.")
        return

    cart = []
    category_filter = st.selectbox("Select Category", sorted(set(item['category'] for item in menu)))

    for item in menu:
        if item['category'] != category_filter:
            continue
        with st.container():
            cols = st.columns([4, 1, 1])
            cols[0].markdown(f"**{item['name']}**")
            cols[1].markdown(f"${item['price']:.2f}")
            if cols[2].button("Add", key=item['id']):
                cart.append(item)
                st.toast(f"Added {item['name']} to cart", icon="🛒")

    if 'cart' not in st.session_state:
        st.session_state.cart = []

    st.session_state.cart += cart

    if st.session_state.cart:
        st.subheader("🛒 Cart")
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.markdown(f"- {item['name']} (${item['price']:.2f})")
        st.markdown(f"**Total: ${total:.2f}**")

        table = st.text_input("Table Number")
        if st.button("Place Order") and table:
            orders = load_json(ORDERS_FILE)
            order = {
                "order_id": str(len(orders) + 1),
                "table": table,
                "items": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().isoformat()
            }
            orders.append(order)
            save_json(ORDERS_FILE, orders)
            st.success("✅ Order Placed!")
            st.session_state.cart = []

    st.markdown("---")
    st.subheader("💬 Leave Feedback")
    order_id = st.text_input("Order ID")
    rating = st.slider("Rating", 1, 5, 3)
    comment = st.text_area("Comment")
    if st.button("Submit Feedback"):
        feedback = load_json(FEEDBACK_FILE)
        feedback.append({
            "order_id": order_id,
            "table": table if 'table' in locals() else "N/A",
            "rating": rating,
            "comment": comment
        })
        save_json(FEEDBACK_FILE, feedback)
        st.success("✅ Feedback submitted")

# ------------------ Main ------------------
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["customer"])[0]

if page == "admin":
    admin_panel()
else:
    customer_panel()
