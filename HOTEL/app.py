import streamlit as st
import json
import os
import time
from datetime import datetime

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Smart Table Order", layout="wide")

# --- Custom Dark Theme CSS Styling ---
st.markdown("""
    <style>
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }
        [data-testid="stSidebar"] { display: none; }
        #MainMenu, footer {visibility: hidden;}

        h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2 {
            color: #80CBC4;
        }

        .stButton > button {
            background-color: #37474F !important;
            color: white !important;
            border-radius: 8px;
            font-size: 0.9rem;
            padding: 0.5rem 1rem;
        }

        .stExpanderHeader {
            color: #E0E0E0 !important;
        }

        .stMarkdown {
            font-size: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# --- Load menu ---
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error(f"❌ Menu file not found at {MENU_FILE}")
    st.stop()

# --- Load orders ---
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# --- Ask for table number ---
if "table_number" not in st.session_state or not st.session_state.table_number:
    st.title("🍽️ Smart Table Ordering System")
    table_number = st.text_input("🔢 Enter your Table Number")
    if table_number:
        st.session_state.table_number = table_number
        st.session_state.cart = {}
        st.rerun()
    st.stop()

st.title(f"🪑 Table {st.session_state.table_number}")

# --- Init cart ---
if "cart" not in st.session_state:
    st.session_state.cart = {}

# --- Show Menu ---
st.subheader("📋 Menu")
for category, items in menu.items():
    with st.expander(category):
        for item in items:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{item['name']}** — ₹{item['price']}")
            with col2:
                if st.button("➕", key=f"{category}-{item['name']}"):
                    name = item["name"]
                    price = item["price"]
                    if name not in st.session_state.cart:
                        st.session_state.cart[name] = {"price": price, "quantity": 1}
                    else:
                        st.session_state.cart[name]["quantity"] += 1
                    st.rerun()

# --- Show Cart ---
st.subheader("🛒 Your Cart")
if st.session_state.cart:
    total = 0
    for name, item in list(st.session_state.cart.items()):
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        item_col, btn1_col, btn2_col = st.columns([6, 1, 1])

        with item_col:
            st.markdown(f"**{name}** x {item['quantity']} = ₹{subtotal}")

        with btn1_col:
            if st.button("➖", key=f"decrease-{name}"):
                st.session_state.cart[name]["quantity"] -= 1
                if st.session_state.cart[name]["quantity"] <= 0:
                    del st.session_state.cart[name]
                st.rerun()

        with btn2_col:
            if st.button("❌", key=f"remove-{name}"):
                del st.session_state.cart[name]
                st.rerun()

    st.markdown(f"### 🧾 Total: ₹{total}")

    if st.button("✅ Place Order"):
        orders = [o for o in orders if o["table"] != st.session_state.table_number]
        order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(order)
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)
        st.success("✅ Order Placed!")
        del st.session_state.cart
        st.rerun()
else:
    st.info("🔒 Your cart is empty.")

# --- Order History / Status ---
st.subheader("📦 Order Status")
found = False
for order in reversed(orders):
    if order["table"] == st.session_state.table_number:
        found = True
        status = order["status"]
        st.markdown(f"🕒 *{order['timestamp']}* — **Status:** `{status}`")
        for name, item in order["items"].items():
            line = f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}"
            if status == "Cancelled":
                st.markdown(f"<s>{line}</s>", unsafe_allow_html=True)
            else:
                st.markdown(line)

        if status == "Completed":
            st.success("🎉 Order Completed! Here's your invoice:")
            total_amt = sum(i['price'] * i['quantity'] for i in order['items'].values())
            st.download_button(
                label="📄 Download Invoice",
                file_name=f"invoice_table_{order['table']}.txt",
                mime="text/plain",
                data=f"Table {order['table']}\n\n" + "\n".join(
                    [f"{k} x {v['quantity']} = ₹{v['price'] * v['quantity']}" for k, v in order['items'].items()]
                ) + f"\n\nTotal: ₹{total_amt}\nTime: {order['timestamp']}"
            )

        if status == "preparing" and not st.session_state.get("notified_preparing"):
            st.audio("https://www.soundjay.com/buttons/beep-07.wav", format="audio/wav")
            st.toast("🍳 Your order is being prepared!", icon="🍳")
            st.session_state.notified_preparing = True

        if status not in ["Completed", "Cancelled"]:
            if st.button(f"❌ Cancel Order ({order['timestamp']})", key=order["timestamp"]):
                order["status"] = "Cancelled"
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                st.warning("Order cancelled.")
                st.rerun()

        st.markdown("---")

if not found:
    st.info("🧾 No current orders found.")

# --- Auto-refresh every 10 seconds ---
with st.empty():
    time.sleep(10)
    st.rerun()
