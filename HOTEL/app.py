import streamlit as st
import os, json, uuid, time
from datetime import datetime

# ---------- Setup ----------
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ---------- Auto Refresh ----------
if 'last_refresh' not in st.session_state or time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()

# ---------- Load Functions ----------
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r") as f:
            return json.load(f)
    return {}

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# ---------- UI ----------
st.title("🍽️ Smart Table Ordering")

# Input table number
if "table_number" not in st.session_state:
    table_num = st.number_input("Enter your Table Number", min_value=1, max_value=100, step=1)
    if st.button("Start Ordering"):
        st.session_state.table_number = str(table_num)
        st.rerun()
    st.stop()

# Load data
menu = load_menu()
orders = load_orders()
cart = st.session_state.get("cart", {})

# Category UI
st.sidebar.title("📂 Categories")
selected_category = st.sidebar.radio("Choose Category", list(menu.keys()))

# Show items
st.header(f"📋 Menu — {selected_category}")
for item in menu[selected_category]:
    name, price = item["name"], item["price"]
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{name}** — ₹{price}")
    with col2:
        qty = st.number_input(name, min_value=0, max_value=10, step=1, key=name)
        if qty > 0:
            cart[name] = {"qty": qty, "price": price}
        elif name in cart:
            del cart[name]
    st.session_state.cart = cart

# Cart UI
st.markdown("---")
st.header("🛒 Your Cart")
if cart:
    total = sum(info["qty"] * info["price"] for info in cart.values())
    for name, info in cart.items():
        st.write(f"- {name} x {info['qty']} = ₹{info['qty'] * info['price']}")
    st.write(f"**Total: ₹{total}**")
    if st.button("✅ Place Order"):
        new_order = {
            "id": f"{st.session_state.table_number}-{int(time.time())}",
            "table": st.session_state.table_number,
            "items": cart,
            "total": total,
            "status": "Pending",
            "timestamp": time.time()
        }
        orders.append(new_order)
        save_orders(orders)
        st.success("✅ Order placed successfully!")
        st.session_state.cart = {}
        st.rerun()
else:
    st.info("Your cart is empty.")

# Order Tracker
st.markdown("---")
st.header("📦 Track Your Orders")
your_orders = [o for o in orders if o["table"] == st.session_state.table_number]

if your_orders:
    for order in sorted(your_orders, key=lambda x: x["timestamp"], reverse=True):
        st.markdown(f"### Order `{order['id']}` — Placed at {datetime.fromtimestamp(order['timestamp']).strftime('%I:%M %p')}")
        for name, info in order["items"].items():
            st.write(f"- {name} x {info['qty']} = ₹{info['qty'] * info['price']}")
        st.write(f"💵 **Total: ₹{order['total']}**")

        status = order["status"]
        if status == "Cancelled":
            st.markdown("<span style='color:red'><s>❌ Cancelled</s></span>", unsafe_allow_html=True)
        elif status == "Completed":
            st.success("✅ Completed")
        elif status == "Preparing":
            st.info("🍳 Preparing")
        else:
            st.warning("⌛ Pending")

        if status in ["Pending", "Preparing"]:
            if st.button(f"❌ Cancel {order['id']}", key=order["id"]):
                order["status"] = "Cancelled"
                save_orders(orders)
                st.warning(f"⚠️ Order `{order['id']}` cancelled.")
                st.rerun()
        st.markdown("---")
else:
    st.info("No orders yet.")