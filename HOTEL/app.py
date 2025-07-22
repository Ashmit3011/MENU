import streamlit as st
import json
import os
import uuid
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Smart Menu", page_icon="🍽️", layout="wide")

# ---------- Paths ----------
BASE_DIR = os.getcwd()
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
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

# ---------- Menu Load ----------
def load_menu():
    try:
        if not os.path.exists(MENU_FILE):
            st.error(f"❌ menu.json not found at {MENU_FILE}")
            return []

        with open(MENU_FILE, "r") as f:
            menu_data = json.load(f)

        if not isinstance(menu_data, list):
            st.error("⚠️ menu.json format is incorrect. Expected a list.")
            return []

        return menu_data

    except Exception as e:
        st.error(f"Failed to load menu.json: {e}")
        return []

# ---------- Session Init ----------
if "cart" not in st.session_state:
    st.session_state.cart = []

if "order_id" not in st.session_state:
    st.session_state.order_id = None

if "category_filter" not in st.session_state:
    st.session_state.category_filter = "All"

# ---------- Menu Display ----------
def render_menu():
    st.title("📋 Smart Restaurant Menu")
    menu = load_menu()

    if not menu:
        st.warning("No menu items available.")
        return

    # --- Category Filter ---
    categories = sorted(set(item.get("category", "Uncategorized") for item in menu))
    st.subheader("🍽️ Select Category")
    selected_category = st.selectbox("Filter by Category", ["All"] + categories, index=0)
    st.session_state.category_filter = selected_category

    # --- Menu Items ---
    st.subheader("📟 Menu Items")
    filtered_menu = [item for item in menu if selected_category == "All" or item.get("category") == selected_category]

    for item in filtered_menu:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item.get('name', 'Unnamed')}**")
                st.caption(f"Category: {item.get('category', 'Uncategorized')}")
                st.markdown(f"💵 ${item.get('price', 0.0):.2f}")
            with col2:
                if st.button(f"Add", key=f"add_{item.get('id')}"):
                    st.session_state.cart.append(item)
                    st.toast(f"✅ {item.get('name')} added to cart")
        st.markdown("---")

# ---------- Cart Display ----------
def render_cart():
    st.sidebar.title("🛒 Your Cart")
    cart = st.session_state.cart
    if not cart:
        st.sidebar.info("Your cart is empty.")
        return

    total = sum(item.get("price", 0.0) for item in cart)
    for item in cart:
        st.sidebar.markdown(f"- {item.get('name')} (${item.get('price', 0.0):.2f})")

    st.sidebar.markdown(f"**Total: ${total:.2f}**")
    table_number = st.sidebar.number_input("Enter Table Number", min_value=1, step=1)

    if st.sidebar.button("✅ Place Order"):
        order = {
            "order_id": str(uuid.uuid4())[:8],
            "table": int(table_number),
            "items": cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders = load_json(ORDERS_FILE)
        orders.append(order)
        save_json(ORDERS_FILE, orders)

        st.toast("🎉 Order placed successfully", icon="✅")
        st.session_state.order_id = order["order_id"]
        st.session_state.cart = []
        st.rerun()

# ---------- Order Tracking ----------
def render_tracking():
    if not st.session_state.order_id:
        return

    st.divider()
    st.subheader("📱 Order Tracking")
    orders = load_json(ORDERS_FILE)
    current = next((o for o in orders if o.get("order_id") == st.session_state.order_id), None)

    if not current:
        st.warning("Your order could not be found.")
        return

    status = current.get("status", "Pending")
    st.info(f"Order ID: {current.get('order_id')} | Table: {current.get('table')}")

    progress_map = {
        "Pending": 0.25,
        "Preparing": 0.5,
        "Ready": 0.75,
        "Served": 1.0
    }

    st.progress(progress_map.get(status, 0.0), text=f"Status: {status}")

    if status == "Served":
        st.success("✅ Your food has been served! Enjoy your meal 🍽️")

        with st.expander("💬 Leave Feedback"):
            rating = st.slider("Rate your experience (1-5)", 1, 5, 5)
            comment = st.text_area("Comments")
            if st.button("Submit Feedback"):
                feedback = load_json(FEEDBACK_FILE)
                feedback.append({
                    "order_id": current.get("order_id"),
                    "table": current.get("table"),
                    "rating": rating,
                    "comment": comment
                })
                save_json(FEEDBACK_FILE, feedback)
                st.toast("✅ Feedback submitted", icon="💬")

# ---------- Main App ----------
def main():
    render_menu()
    render_cart()
    render_tracking()
    st_autorefresh(interval=10 * 1000, key="track_refresh")

if __name__ == "__main__":
    main()
