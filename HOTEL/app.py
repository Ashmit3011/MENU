import streamlit as st
import json
import os
import time
from datetime import datetime
from fpdf import FPDF

# -------------- Streamlit Config & Styling --------------
st.set_page_config(page_title="Smart Table Order", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        #MainMenu, footer {visibility: hidden;}
        .stButton > button {
            padding: 0.4rem 0.8rem;
            font-size: 0.85rem;
            border-radius: 8px;
            background-color: #a8dadc !important;
            color: #1d3557 !important;
        }
        .stDownloadButton>button {
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
        pdf.image(QR_IMAGE, x=pdf.get_x(), y=pdf.get_y(), w=40)

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
st.subheader("📋 Browse Menu")

menu_container = st.container()
with menu_container:
    for category, items in menu.items():
        st.markdown(f"### 🍽️ {category}")
        for item in items:
            with st.container():
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(f"""
                        <div style='padding: 0.5rem 0.75rem; background-color: #f1faee; border-radius: 10px;'>
                            <strong style='font-size: 1rem; color: #1d3557;'>{item['name']}</strong><br>
                            <span style='color: #6c757d; font-size: 0.85rem;'>{item.get('description', '')}</span>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div style='margin-top: 0.75rem;'><strong>₹{item['price']}</strong></div>", unsafe_allow_html=True)
                with col3:
                    if st.button("➕", key=f"{category}-{item['name']}"):
                        name, price = item["name"], item["price"]
                        st.session_state.cart[name] = st.session_state.cart.get(name, {"price": price, "quantity": 0})
                        st.session_state.cart[name]["quantity"] += 1
                        st.rerun()
            st.markdown("---")

# -------------- Display Cart --------------
st.subheader("🛒 Cart")
if st.session_state.cart:
    total = 0
    for name, item in list(st.session_state.cart.items()):
        subtotal = item["price"] * item["quantity"]
        total += subtotal

        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.markdown(f"**{name}** x {item['quantity']} = ₹{subtotal}")
        with col2:
            if st.button("➖", key=f"dec-{name}"):
                st.session_state.cart[name]["quantity"] -= 1
                if st.session_state.cart[name]["quantity"] <= 0:
                    del st.session_state.cart[name]
                st.rerun()
        with col3:
            if st.button("❌", key=f"rem-{name}"):
                del st.session_state.cart[name]
                st.rerun()

    st.markdown(f"### 🧾 Total: ₹{total}")

    if st.button("✅ Place Order"):
        # Remove previous order for same table
        orders = [o for o in orders if o["table"] != st.session_state.table_number]
        new_order = {
            "table": st.session_state.table_number,
            "items": st.session_state.cart,
            "status": "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        orders.append(new_order)
        json.dump(orders, open(ORDERS_FILE, "w"), indent=2)
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

        if status not in ["Completed", "Cancelled"]:
            if st.button(f"❌ Cancel Order ({order['timestamp']})", key=order["timestamp"]):
                order["status"] = "Cancelled"
                json.dump(orders, open(ORDERS_FILE, "w"), indent=2)
                st.warning("Order cancelled.")
                st.rerun()
        elif status == "Completed":
            invoice_path = generate_invoice(order)
            st.success("✅ Order Completed! Download your invoice below:")
            with open(invoice_path, "rb") as f:
                st.download_button("📄 Download Invoice", data=f, file_name=os.path.basename(invoice_path))

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
        json.dump(feedback, open(FEEDBACK_FILE, "w"), indent=2)
        st.success("🎉 Thank you for your feedback!")
    else:
        st.warning("Please enter both name and feedback.")

# -------------- Auto-refresh every 10 seconds --------------
with st.empty():
    time.sleep(10)
    st.rerun()