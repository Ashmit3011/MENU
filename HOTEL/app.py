import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, key="customer_refresh")

# File paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")

# Create invoice directory if not exists
os.makedirs(INVOICE_DIR, exist_ok=True)

# Load menu
menu = json.load(open(MENU_FILE)) if os.path.exists(MENU_FILE) else []

# Load orders
orders = json.load(open(ORDERS_FILE)) if os.path.exists(ORDERS_FILE) else []

# Load feedbacks
feedbacks = json.load(open(FEEDBACK_FILE)) if os.path.exists(FEEDBACK_FILE) else []

# App config
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.title("🍽️ Smart Table Ordering System")

# Select Table Number
table_number = st.selectbox("Select your Table Number:", ["1", "2", "3", "4", "5"], index=0)

# Sidebar Cart
st.sidebar.title("🛒 Cart Summary")
cart = {}

# --- Menu Display ---
st.header("📋 Menu")
categories = sorted(set(item['category'] for item in menu if 'category' in item))
selected_category = st.selectbox("Select Category", categories)

for item in menu:
    if item.get("category") == selected_category:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item['name']}**  \n💵 Rs. {item['price']}")
        with col2:
            qty = st.number_input(f"Qty - {item['name']}", min_value=0, step=1, key=f"qty_{item['id']}")
            if qty > 0:
                cart[item['id']] = qty
                st.sidebar.write(f"{item['name']} x {qty} = Rs. {item['price'] * qty}")

# Show total in cart sidebar
if cart:
    total_amt = sum(next((i['price'] for i in menu if i['id'] == id_), 0) * q for id_, q in cart.items())
    st.sidebar.markdown(f"### Total: Rs. {total_amt}")

# Payment method
payment_method = st.selectbox("💳 Choose Payment Method", ["Cash", "Card", "Online"])

# --- Place Order ---
if st.button("✅ Place Order"):
    if not cart:
        st.warning("Please select at least one item.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_order = {
            "table": table_number,
            "items": cart,
            "status": "Preparing",
            "timestamp": timestamp,
            "payment_method": payment_method
        }

        orders.append(new_order)
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2)

        st.success("✅ Order placed successfully!")
        st.rerun()

# --- Your Orders ---
st.header("📦 Your Orders")
user_orders = [o for o in orders if o["table"] == table_number]

if not user_orders:
    st.info("You haven't placed any orders yet.")
else:
    for idx, order in enumerate(reversed(user_orders)):
        st.markdown("---")
        st.markdown(f"### 🪑 Table: {order['table']} | ⏰ {order['timestamp']}")
        st.markdown(f"**Status:** `{order['status']}`")
        st.markdown(f"**Payment Method:** `{order.get('payment_method', 'N/A')}`")

        item_data = []
        for item_id, qty in order["items"].items():
            item = next((i for i in menu if i["id"] == item_id), {"name": "Unknown", "price": 0})
            item_data.append({
                "Item": item["name"],
                "Quantity": qty,
                "Price": item["price"],
                "Total": qty * item["price"]
            })

        df = pd.DataFrame(item_data)
        st.dataframe(df, use_container_width=True)

        # Invoice download if Completed
        if order["status"] == "Completed":
            invoice_name = f"invoice_table{order['table']}_{idx}.pdf"
            invoice_path = os.path.join(INVOICE_DIR, invoice_name)

            if not os.path.exists(invoice_path):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Smart Table Invoice", ln=True, align="C")
                pdf.cell(200, 10, txt=f"Table: {order['table']} | Time: {order['timestamp']}", ln=True)
                pdf.cell(200, 10, txt=f"Payment Method: {order.get('payment_method', 'N/A')}", ln=True)

                pdf.ln(10)
                total = 0
                for row in item_data:
                    line = f"{row['Item']} x {row['Quantity']} - Rs. {row['Total']}"
                    pdf.cell(200, 10, txt=line, ln=True)
                    total += row['Total']
                pdf.ln(5)
                pdf.cell(200, 10, txt=f"Total Amount: Rs. {total}", ln=True)

                pdf.output(invoice_path)

            with open(invoice_path, "rb") as f:
                st.download_button(
                    label="📄 Download Invoice",
                    data=f.read(),
                    file_name=invoice_name,
                    mime="application/pdf"
                )

# --- Feedback Section ---
st.markdown("---")
st.header("💬 Submit Feedback")

feedback_text = st.text_area("Your feedback:")
if st.button("📝 Submit Feedback"):
    if not feedback_text.strip():
        st.warning("Feedback cannot be empty.")
    else:
        feedbacks.append({
            "table": table_number,
            "feedback": feedback_text.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, indent=2)
        st.success("🙏 Thanks for your feedback!")
        st.rerun()