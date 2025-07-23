import streamlit as st
import json
import os
import time
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# -------------- Streamlit Config & Styling --------------
st.set_page_config(page_title="Smart Table Order", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        #MainMenu, footer {visibility: hidden;}
        .css-1aumxhk {padding-top: 1rem;}
        .stButton > button {
            padding: 0.1rem 0.35rem !important;
            font-size: 0.65rem !important;
            height: 1.5rem !important;
            line-height: 1rem !important;
            border-radius: 4px !important;
            background-color: #a8dadc !important;
            color: #1d3557 !important;
        }
        .stDownloadButton > button {
            padding: 0.2rem 0.5rem !important;
            font-size: 0.7rem !important;
            height: 1.8rem !important;
            border-radius: 4px !important;
            background-color: #457b9d !important;
            color: white !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# -------------- Paths --------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")
QR_IMAGE = os.path.join(BASE_DIR, "qr.jpg")

# -------------- Helper: Generate Invoice --------------
def generate_invoice(order):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Smart Café Invoice", ln=True, align="C")
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Table: {order['table']}", ln=True)
    pdf.cell(0, 10, f"Date: {order['timestamp']}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Item", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(30, 10, "Price", 1)
    pdf.cell(40, 10, "Subtotal", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    total = 0
    for name, item in order["items"].items():
        qty = item["quantity"]
        price = item["price"]
        subtotal = qty * price
        total += subtotal

        pdf.cell(80, 10, name, 1)
        pdf.cell(30, 10, str(qty), 1)
        pdf.cell(30, 10, f"Rs. {price}", 1)
        pdf.cell(40, 10, f"Rs. {subtotal}", 1)
        pdf.ln()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "Total", 1)
    pdf.cell(40, 10, f"Rs. {total}", 1)
    pdf.ln(20)

    if os.path.exists(QR_IMAGE):
        pdf.image(QR_IMAGE, x=10, y=pdf.get_y(), w=40)

    invoice_path = os.path.join(BASE_DIR, f"invoice_table_{order['table']}.pdf")
    pdf.output(invoice_path)
    return invoice_path

# -------------- Load Data --------------
menu = json.load(open(MENU_FILE)) if os.path.exists(MENU_FILE) else {}
orders = json.load(open(ORDERS_FILE)) if os.path.exists(ORDERS_FILE) else []
feedback = json.load(open(FEEDBACK_FILE)) if os.path.exists(FEEDBACK_FILE) else []

# -------------- Table Number Session --------------
if "table_number" not in st.session_state:
    st.title("🍽️ Smart Table Ordering System")
    table_number = st.text_input("🔢 Enter your Table Number")
    if table_number:
        st.session_state.table_number = table_number
        st.session_state.cart = {}
        st.rerun()
    st.stop()

st.title(f"🍽️ Smart Ordering — Table {st.session_state.table_number}")
if "cart" not in st.session_state:
    st.session_state.cart = {}

# -------------- Display Menu --------------
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
                    st.session_state.cart[name] = st.session_state.cart.get(name, {"price": price, "quantity": 0})
                    st.session_state.cart[name]["quantity"] += 1
                    st.rerun()

st.subheader("🛒 Your Cart")

if st.session_state.cart:
    total = 0
    for name, item in list(st.session_state.cart.items()):
        price = item["price"]
        qty = item["quantity"]
        subtotal = price * qty
        total += subtotal

        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            st.markdown(f"""
                <div style="
                    background-color: #e0f7fa;
                    padding: 0.8rem;
                    border-radius: 10px;
                    border: 1px solid #b2ebf2;
                    box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
                ">
                    <b>🍽️ {name}</b><br>
                    <span style="font-size: 0.85rem; color: #555;">₹{price} × {qty}</span><br>
                    <b>Subtotal: ₹{subtotal}</b>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("➖", key=f"dec_{name}", help="Decrease quantity"):
                st.session_state.cart[name]["quantity"] -= 1
                if st.session_state.cart[name]["quantity"] <= 0:
                    del st.session_state.cart[name]
                st.rerun()

        with col3:
            st.empty()  # filler for spacing

    st.markdown(f"""
        <div style='text-align: right; font-size: 1.2rem; margin-top: 1rem;'>
            <b>🧾 Total: ₹{total}</b>
        </div>
    """, unsafe_allow_html=True)

    col = st.columns([2, 1, 2])[1]
    with col:
        if st.button("✅ Place Order"):
            orders = [o for o in orders if o["table"] != st.session_state.table_number]
            new_order = {
                "table": st.session_state.table_number,
                "items": st.session_state.cart,
                "status": "pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders.append(new_order)
            with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(orders, f, indent=2)
            st.success("✅ Order Placed!")
            del st.session_state.cart
            st.rerun()
else:
    st.info("🛍️ Your cart is empty.")

# -------------- Order History --------------
st.subheader("📦 Your Orders")
found = False
for order in reversed(orders):
    if order["table"] == st.session_state.table_number:
        found = True
        status = order["status"]
        st.markdown(f"🕒 *{order['timestamp']}* — **Status:** `{status}`")

        for name, item in order["items"].items():
            st.markdown(f"{name} x {item['quantity']} = ₹{item['price'] * item['quantity']}")

        if status == "Completed":
            invoice_path = generate_invoice(order)
            st.success("✅ Order Completed! Download your invoice below:")
            with open(invoice_path, "rb") as f:
                st.download_button("📄 Download Invoice", data=f.read(), file_name=os.path.basename(invoice_path))

        if status == "Preparing" and "alerted" not in st.session_state:
            st.session_state.alerted = True
            st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg")

        st.markdown("---")

if not found:
    st.info("📭 No orders found.")

# -------------- Feedback Form --------------
st.subheader("💬 Feedback")
name = st.text_input("Your Name")
rating = st.slider("How was your experience?", 1, 5, 3)
message = st.text_area("Any comments or suggestions?")
if st.button("📩 Submit Feedback"):
    if name and message:
        feedback.append({
            "table": st.session_state.table_number,
            "name": name,
            "rating": rating,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedback, f, indent=2)
        st.success("🎉 Thank you for your feedback!")
    else:
        st.warning("Please enter both name and feedback.")

# -------------- Auto-refresh every 10 seconds --------------
with st.empty():
    time.sleep(10)
    st.rerun()