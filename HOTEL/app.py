import streamlit as st
import json
import os
import uuid
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Smart Menu", page_icon="🍽️", layout="wide")

# ---------- File Paths ----------
BASE_DIR = os.getcwd()
MENU_PATH = os.path.join(BASE_DIR, "menu.json")
ORDERS_PATH = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_PATH = os.path.join(BASE_DIR, "feedback.json")

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
    if not os.path.exists(MENU_PATH):
        st.error("❌ menu.json not found at path: " + MENU_PATH)
        return []
    try:
        with open(MENU_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load menu.json: {e}")
        return []

# ---------- Session Init ----------
if "cart" not in st.session_state:
    st.session_state.cart = []

if "order_id" not in st.session_state:
    st.session_state.order_id = None

# ---------- Menu Display ----------
def render_menu():
    st.title("📋 Smart Restaurant Menu")
    st.subheader("Select items to add to your cart")
    menu = load_menu()

    if not menu:
        st.warning("⚠️ No menu items available.")
        return

    categories = sorted(set(item["category"] for item in menu))
    for cat in categories:
        st.markdown(f"### 🍴 {cat}")
        col1, col2 = st.columns(2)
        with col1:
            for item in [m for m in menu if m["category"] == cat][:len(menu)//2]:
                st.markdown(f"**{item['name']}** - ${item['price']:.2f}")
                if st.button(f"Add {item['name']}", key=f"add_{item['id']}"):
                    st.session_state.cart.append(item)
                    st.toast(f"🛒 {item['name']} added to cart", icon="✅")
        with col2:
            for item in [m for m in menu if m["category"] == cat][len(menu)//2:]:
                st.markdown(f"**{item['name']}** - ${item['price']:.2f}")
                if st.button(f"Add {item['name']}", key=f"add_{item['id']}"):
                    st.session_state.cart.append(item)
                    st.toast(f"🛒 {item['name']} added to cart", icon="✅")

# ---------- Cart Display ----------
def render_cart():
    st.sidebar.title("🛒 Your Cart")
    cart = st.session_state.cart
    if not cart:
        st.sidebar.info("Your cart is empty.")
        return

    total = sum(item["price"] for item in cart)
    for item in cart:
        st.sidebar.markdown(f"- {item['name']} (${item['price']:.2f})")

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
        orders = load_json(ORDERS_PATH)
        orders.append(order)
        save_json(ORDERS_PATH, orders)

        st.toast("🎉 Order placed successfully", icon="✅")
        st.session_state.order_id = order["order_id"]
        st.session_state.cart = []
        st.rerun()

# ---------- Order Tracking ----------
def render_tracking():
    if not st.session_state.order_id:
        return

    st.divider()
    st.subheader("📡 Order Tracking")
    orders = load_json(ORDERS_PATH)
    current = next((o for o in orders if o["order_id"] == st.session_state.order_id), None)

    if not current:
        st.warning("Your order could not be found.")
        return

    status = current["status"]
    st.info(f"Order ID: {current['order_id']} | Table: {current['table']}")

    progress_map = {
        "Pending": 0.25,
        "Preparing": 0.5,
        "Ready": 0.75,
        "Served": 1.0
    }

    st.progress(progress_map.get(status, 0.0), text=f"Status: {status}")
    
    if status == "Served":
        st.success("✅ Your food has been served! Enjoy your meal 🍽️")

        # Optional feedback form
        with st.expander("💬 Leave Feedback"):
            rating = st.slider("Rate your experience (1-5)", 1, 5, 5)
            comment = st.text_area("Comments")
            if st.button("Submit Feedback"):
                feedback = load_json(FEEDBACK_PATH)
                feedback.append({
                    "order_id": current["order_id"],
                    "table": current["table"],
                    "rating": rating,
                    "comment": comment
                })
                save_json(FEEDBACK_PATH, feedback)
                st.toast("✅ Feedback submitted", icon="💬")

# ---------- Main App ----------
def main():
    render_menu()
    render_cart()
    render_tracking()

    # Auto-refresh every 10 seconds
    st_autorefresh(interval=10 * 1000, key="track_refresh")

if __name__ == "__main__":
    main()
