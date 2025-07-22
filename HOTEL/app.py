import streamlit as st
import json
import os
import time
from datetime import datetime
from fpdf import FPDF

# --- Page config ---
st.set_page_config(page_title="Smart Table Order", layout="centered")

# --- Calm UI Styling ---
st.markdown("""
    <style>
    body {
        background-color: #F6F6F6;
        color: #2E3B4E;
    }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu, footer {visibility: hidden;}
    .stButton > button {
        padding: 0.5rem 1.2rem !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        background-color: #A7D7C5 !important;
        color: #1C2B2D;
        border: none;
    }
    .stButton > button:hover {
        background-color: #92C9B1 !important;
    }
    .invoice {
        background: #e0f2f1;
        padding: 1rem;
        border-radius: 10px;
    }
    .block-container {
        background-color: #F6F6F6;
    }
    </style>
""", unsafe_allow_html=True)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# --- Load Menu & Orders ---
menu = json.load(open(MENU_FILE)) if os.path.exists(MENU_FILE) else {}
orders = json.load(open(ORDERS_FILE)) if os.path.exists(ORDERS_FILE) else []

# --- Session State Init ---
if "table_number" not in st.session_state:
    st.title("🍽️ Smart Table Ordering System")
    table_number = st.text_input("🔢 Enter your Table Number")
    if table_number:
        st.session_state.table_number = table_number
        st.session_state.cart = {}
        st.rerun()
    st.stop()

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "last_status" not in st.session_state:
    st.session_state.last_status = None

# --- UI Header ---
st.title(f"🪑 Table {st.session_state.table_number}")

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
                    name, price = item["name"], item["price"]
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
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.markdown(f"{name} x {item['quantity']} = ₹{subtotal}")
        with col2:
            if st.button("➖", key=f"decrease-{name}"):
                item["quantity"] -= 1
                if item["quantity"] <= 0:
                    del st.session_state.cart[name]
                st.rerun()
        with col3:
            if st.button("❌", key=f"remove-{name}"):
                del st.session_state.cart[name]
                st.rerun()

    st.markdown(f"### 🧾 Total: ₹{total}")
    if st.button("✅ Place Order"):
        orders = [o for o in orders if o["table"] != st.session_state.table_number]
        new_order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        json.dump(orders, open(ORDERS_FILE, "w"), indent=2)
        st.success("✅ Order Placed!")
        del st.session_state.cart
        st.rerun()
else:
    st.info("🛍️ Your cart is empty.")

# --- Order Status & Invoice ---
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
            with st.expander("🧾 Download Invoice"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(190, 10, f"Invoice - Table {order['table']}", ln=True)
                pdf.set_font("Arial", "", 12)
                pdf.cell(190, 10, f"Time: {order['timestamp']}", ln=True)
                pdf.cell(190, 10, f"Status: {status}", ln=True)
                pdf.ln(5)
                total = 0
                for name, item in order["items"].items():
                    qty, price = item["quantity"], item["price"]
                    subtotal = qty * price
                    total += subtotal
                    pdf.cell(190, 10, f"{name} x {qty} = ₹{subtotal}", ln=True)
                pdf.ln(5)
                pdf.set_font("Arial", "B", 12)
                pdf.cell(190, 10, f"Total: ₹{total}", ln=True)
                invoice_path = os.path.join(BASE_DIR, "invoice.pdf")
                pdf.output(invoice_path)
                with open(invoice_path, "rb") as f:
                    st.download_button("📥 Download Invoice", f, file_name="invoice.pdf")

        if status == "Preparing" and st.session_state.last_status != "Preparing":
            st.markdown("""
                <script>
                const audio = new Audio("https://www.myinstants.com/media/sounds/bell.mp3");
                audio.play();
                </script>
            """, unsafe_allow_html=True)

        if status not in ["Completed", "Cancelled"]:
            if st.button("❌ Cancel Order", key=order["timestamp"]):
                order["status"] = "Cancelled"
                json.dump(orders, open(ORDERS_FILE, "w"), indent=2)
                st.warning("Order cancelled.")
                st.rerun()
        st.markdown("---")
        st.session_state.last_status = status
        break

if not found:
    st.info("📭 No current orders found.")

# --- Auto Refresh ---
time.sleep(10)
st.rerun()
