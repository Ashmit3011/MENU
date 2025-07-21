import streamlit as st
import json
import uuid
import time
from datetime import datetime
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# ---------- FILE PATHS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ---------- DATA FUNCTIONS ----------
def load_menu():
    try:
        with open(MENU_FILE, "r") as f:
            menu = json.load(f)
            assert isinstance(menu, list)
            return menu
    except:
        return []

def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def save_order(order):
    orders = load_orders()
    orders.append(order)
    save_orders(orders)

def delete_served_orders():
    orders = load_orders()
    remaining = [o for o in orders if o.get("status") != "Served"]
    save_orders(remaining)

# ---------- TOAST CSS ----------
st.markdown("""
    <style>
        .toast {
            position: fixed;
            bottom: 70px;
            right: 20px;
            background-color: #333;
            color: white;
            padding: 16px;
            border-radius: 10px;
            z-index: 10000;
            animation: slideIn 0.5s ease-out;
        }
        @keyframes slideIn {
            0% {opacity: 0; transform: translateY(20px);}
            100% {opacity: 1; transform: translateY(0);}
        }

        /* Hide sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Hide hamburger menu */
        [data-testid="stToolbar"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

def toast(msg):
    st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)

# ---------- SESSION STATE ----------
st.session_state.setdefault("cart", {})
st.session_state.setdefault("table_number", "")

# ---------- LOAD MENU ----------
menu = load_menu()
st.title("🍽️ Smart Table Ordering System")

if not menu:
    st.error("❌ Menu is empty or not loaded properly.")
    st.stop()

# ---------- UI TABS ----------
tab_menu, tab_cart, tab_track, tab_admin = st.tabs(["📋 Menu", "🛒 Cart", "📦 Track Order", "🧑‍🍳 Admin"])

# ---------- MENU TAB ----------
with tab_menu:
    selected_category = st.selectbox("Select a category", sorted(set(i["category"] for i in menu)))
    filtered_menu = [item for item in menu if item["category"] == selected_category]

    for item in filtered_menu:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
            st.caption(f"₹{item['price']} | {'🌶️' if item['spicy'] else ''} {'🟢' if item['veg'] else '🔴'}")
        with col2:
            qty = st.number_input(f"Qty - {item['id']}", min_value=0, step=1, key=f"qty_{item['id']}")
            if qty > 0:
                st.session_state.cart[item['id']] = {"name": item['name'], "qty": qty, "price": item['price']}
            elif item['id'] in st.session_state.cart:
                del st.session_state.cart[item['id']]

# ---------- CART TAB ----------
with tab_cart:
    st.subheader("🛒 Your Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        total = 0
        for item in st.session_state.cart.values():
            st.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            total += item['qty'] * item['price']
        st.success(f"Total: ₹{total}")

        st.text_input("Enter your table number", key="table_number")
        if st.button("✅ Place Order"):
            if not st.session_state.table_number:
                st.warning("Please enter a table number.")
            else:
                order = {
                    "id": str(uuid.uuid4())[:8],
                    "table": st.session_state.table_number,
                    "items": st.session_state.cart,
                    "total": total,
                    "status": "Pending",
                    "timestamp": time.time()
                }
                save_order(order)
                st.session_state.cart = {}
                toast("✅ Order placed successfully!")

# ---------- ORDER TRACKING TAB ----------
with tab_track:
    st.subheader("📦 Track Your Order")

    if not st.session_state.table_number:
        st.info("Enter your table number in the cart to track your order.")
    else:
        user_orders = [o for o in load_orders() if o['table'] == st.session_state.table_number]
        user_orders = sorted(user_orders, key=lambda x: x['timestamp'], reverse=True)

        if not user_orders:
            st.info("No orders found for your table.")
        else:
            latest = user_orders[0]
            status = latest['status']
            status_steps = ["Pending", "Preparing", "Ready", "Served"]
            status_index = status_steps.index(status)

            st.write(f"🧾 **Order ID**: `{latest['id']}`")
            st.write(f"🪑 **Table**: `{latest['table']}`")
            st.caption(f"⏰ Placed at: {datetime.fromtimestamp(latest['timestamp']).strftime('%I:%M %p')}")

            with st.expander("📋 View Ordered Items"):
                for item in latest["items"].values():
                    st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                st.success(f"Total: ₹{latest['total']}")

            st.progress(status_index / 3)

            st.markdown("### 🚦 Order Status")
            for i, step in enumerate(status_steps):
                if i < status_index:
                    st.markdown(f"✅ **{step}**")
                elif i == status_index:
                    st.markdown(f"🟡 **{step} (Current)**")
                else:
                    st.markdown(f"⏳ {step}")

# ---------- ADMIN TAB ----------
with tab_admin:
    st.subheader("🧑‍🍳 Admin - Live Orders")
    orders = load_orders()
    orders = sorted(orders, key=lambda x: float(x.get("timestamp", 0)), reverse=True)
    status_options = ["Pending", "Preparing", "Ready", "Served"]
    updated = False

    if not orders:
        st.info("No orders available.")
    else:
        for idx, order in enumerate(orders):
            order_id = order.get("id", "N/A")
            table = order.get("table", "N/A")
            current_status = order.get("status", "Pending")
            readable_time = datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')

            with st.container():
                st.markdown(f"""
                <div style='
                    border: 2px solid #444; 
                    border-radius: 12px; 
                    padding: 16px; 
                    margin-bottom: 10px;
                    background-color: #1e1e1e;
                    color: white;
                '>
                    <strong>🧾 Order ID:</strong> {order_id}<br>
                    <strong>🪑 Table:</strong> {table}<br>
                    <strong>⏰ Time:</strong> {readable_time}<br>
                    <strong>Items:</strong>
                </div>
                """, unsafe_allow_html=True)

                for item in order["items"].values():
                    st.markdown(f"<span style='color:white'>- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}</span>", unsafe_allow_html=True)

                new_status = st.selectbox(
                    f"Update Status for Order {order_id}",
                    status_options,
                    index=status_options.index(current_status),
                    key=f"status_{order_id}"
                )

                if new_status != current_status:
                    orders[idx]["status"] = new_status
                    updated = True

                st.progress(status_options.index(orders[idx]["status"]) / 3)
                st.markdown("---")

        # Delete Button
        if st.button("🗑️ Delete Orders Marked as Served"):
            delete_served_orders()
            toast("🗑️ Deleted all served orders.")
            st.experimental_rerun()

    if updated:
        save_orders(orders)
        toast("✅ Order status updated.")

# ---------- AUTO REFRESH ----------
st.markdown("""
<script>
    setTimeout(() => window.location.reload(), 7000);
</script>
""", unsafe_allow_html=True)