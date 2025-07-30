import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# File paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
QR_IMAGE = os.path.join(BASE_DIR, "qr.png")  # Optional QR code image

# Load menu
with open(MENU_FILE, "r", encoding="utf-8") as f:
    menu = json.load(f)

# Load existing orders
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        orders = json.load(f)
else:
    orders = []

st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.markdown("<h1 style='text-align: center;'>🍽️ Smart Table Ordering</h1>", unsafe_allow_html=True)

# Select table
table_number = st.selectbox("Select your Table Number", [1, 2, 3, 4, 5], index=0)

# Create categories
categories = sorted(set(item["category"] for item in menu))
selected_category = st.selectbox("Choose a Category", categories)

# Show menu items for selected category
st.subheader(f"Menu - {selected_category}")
cart = {}

for item in menu:
    if item["category"] == selected_category:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item['name']}**  \nRs. {item['price']}")
        with col2:
            qty = st.number_input(f"{item['name']}", min_value=0, max_value=10, step=1, key=item["name"])
            if qty > 0:
                cart[item["name"]] = {"price": item["price"], "quantity": qty}

# Place order
if st.button("🛒 Place Order"):
    if not cart:
        st.warning("Please add at least one item to cart.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_order = {
            "table": table_number,
            "items": cart,
            "status": "Pending",
            "timestamp": timestamp
        }

        orders.append(new_order)

        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2)

        st.success("✅ Order placed successfully!")

# View order history for current table
st.markdown("## 📦 Your Orders")
for idx, order in enumerate(orders):
    if order["table"] == table_number:
        status = order["status"]
        st.markdown(f"**Order #{idx+1}** - `{status}` - `{order['timestamp']}`")
        df = pd.DataFrame([
            {
                "Item": name,
                "Quantity": item["quantity"],
                "Price": item["price"],
                "Subtotal": item["price"] * item["quantity"]
            }
            for name, item in order["items"].items()
        ])
        st.dataframe(df, use_container_width=True)

        if status == "Completed":
            if "invoice_path" not in order or not os.path.exists(order["invoice_path"]):
                invoice_path = os.path.join(BASE_DIR, f"invoice_table_{order['table']}_{order['timestamp'].replace(':','-').replace(' ', '_')}.pdf")
                order["invoice_path"] = generate_invoice(order, invoice_path)
                with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                    json.dump(orders, f, indent=2)
            else:
                invoice_path = order["invoice_path"]

            st.success("✅ Order Completed! Download your invoice below:")
            with open(invoice_path, "rb") as f:
                st.download_button("📄 Download Invoice", data=f.read(), file_name=os.path.basename(invoice_path), mime="application/pdf")

# --- Invoice PDF Generation ---
def generate_invoice(order, save_path):
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

    pdf.output(save_path)
    return save_path