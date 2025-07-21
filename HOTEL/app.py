import streamlit as st
import json, uuid, time
from datetime import datetime
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# Paths
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"

# Auto-refresh every 5 sec
st_autorefresh(interval=5000, key="app_refresh")
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# Session
st.session_state.setdefault("cart", {})
st.session_state.setdefault("table_number", "")

# Load menu
def load_menu():
    try:
        with open(MENU_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_order(order):
    try:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Toast style
st.markdown("""
    <style>
    .toast { position: fixed; bottom: 70px; right: 20px; background: #222; color: white; padding: 12px;
             border-radius: 8px; z-index: 9999; animation: fadeIn 0.5s ease-in-out;}
    @keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }
    </style>
""", unsafe_allow_html=True)
def toast(msg): st.markdown(f'<div class="toast">{msg}</div>', unsafe_allow_html=True)

# Load menu
menu = load_menu()
if not menu:
    st.error("Menu not available.")
    st.stop()

st.title("🍽️ Smart Table Ordering")
tab1, tab2, tab3 = st.tabs(["📋 Menu", "🛒 Cart", "📦 Track"])

with tab1:
    categories = sorted(set(i['category'] for i in menu))
    selected = st.selectbox("Select Category", categories)
    for item in [m for m in menu if m['category'] == selected]:
        col1, col2 = st.columns([4,1])
        with col1:
            st.markdown(f"**{item['name']}**")
            st.caption(f"₹{item['price']} {'🟢' if item['veg'] else '🔴'} {'🌶️' if item['spicy'] else ''}")
        with col2:
            qty = st.number_input(f"Qty - {item['id']}", 0, 20, 0, 1, key=f"qty_{item['id']}")
            if qty > 0:
                st.session_state.cart[item['id']] = {"name": item["name"], "qty": qty, "price": item["price"]}
            elif item['id'] in st.session_state.cart:
                del st.session_state.cart[item['id']]

with tab2:
    st.subheader("Your Cart")
    if not st.session_state.cart:
        st.info("No items.")
    else:
        total = 0
        for item in st.session_state.cart.values():
            st.write(f"{item['name']} x {item['qty']} = ₹{item['qty']*item['price']}")
            total += item['qty'] * item['price']
        st.success(f"Total: ₹{total}")
        table_num = st.text_input("Table Number", key="table_number")
        if st.button("Place Order"):
            if not table_num:
                st.warning("Enter table number.")
            else:
                new_order = {
                    "id": str(uuid.uuid4())[:8],
                    "table": table_num,
                    "items": st.session_state.cart,
                    "total": total,
                    "status": "Pending",
                    "timestamp": time.time()
                }
                save_order(new_order)
                st.session_state.cart = {}
                st.session_state.table_number = table_num
                toast("✅ Order placed!")

with tab3:
    st.subheader("Track Order")
    if not st.session_state.table_number:
        st.info("Place an order to begin tracking.")
    else:
        orders = load_orders()
        table_orders = [o for o in orders if o["table"] == st.session_state.table_number]
        if not table_orders:
            st.info("No orders found.")
        else:
            latest = sorted(table_orders, key=lambda x: x["timestamp"], reverse=True)[0]
            st.write(f"🧾 Order ID: `{latest['id']}` | Status: **{latest['status']}**")
            st.caption(datetime.fromtimestamp(latest["timestamp"]).strftime("Placed at %I:%M %p"))
            st.progress(["Pending", "Preparing", "Ready", "Served"].index(latest["status"]) / 3)