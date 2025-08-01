import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from streamlit_autorefresh import st_autorefresh

# === Session State Setup for Refresh Control ===
if "order_just_placed" not in st.session_state:
    st.session_state.order_just_placed = False

# Refresh only if order not just placed
if not st.session_state.order_just_placed:
    st_autorefresh(interval=5000, key="customer_refresh")

# === File paths ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")
os.makedirs(INVOICE_DIR, exist_ok=True)

# === Utility Functions ===
def load_json(file_path, default=[]):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to parse {file_path}")
    return default

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Load Data ===
menu = load_json(MENU_FILE)
orders = load_json(ORDERS_FILE)
feedbacks = load_json(FEEDBACK_FILE)

# === UI Setup ===
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.title("\U0001F37D️ Smart Table Ordering System")

# --- Table Selection ---
ALL_TABLES = ["1", "2", "3", "4", "5"]
occupied_tables = set(str(o["table"]) for o in orders if o["status"] != "Completed")
available_tables = [t for t in ALL_TABLES if t not in occupied_tables]

if available_tables:
    table_number = st.selectbox("Select your Table Number:", available_tables, index=0)
else:
    st.error("\U0001F6AB All tables are currently in use. Please wait.")
    st.stop()

# --- Menu Display ---
st.header("\U0001F4CB Menu")

if not menu:
    st.warning("\U0001F6AB No menu items available.")
    st.stop()

categories = sorted(set(item['category'] for item in menu if 'category' in item))
selected_category = st.selectbox("Select Category", categories)

cart = {}

for item in menu:
    if item.get("category") == selected_category:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{item['name']}**  \n\U0001FA75 Rs. {item['price']}")
        with col2:
            qty = st.number_input(f"Qty - {item['name']}", min_value=0, step=1, key=f"qty_{item['id']}")
            if qty > 0:
                cart[item['id']] = qty

# --- Cart Section ---
if cart:
    st.markdown("---")
    st.subheader("\U0001F6D2 Your Cart")
    item_data = []
    total_amt = 0
    for item_id, qty in cart.items():
        item = next((i for i in menu if i["id"] == item_id), {"name": "Unknown", "price": 0})
        total = item["price"] * qty
        total_amt += total
        item_data.append({
            "Item": item["name"],
            "Quantity": qty,
            "Price": item["price"],
            "Total": total
        })
    st.dataframe(pd.DataFrame(item_data), use_container_width=True)
    st.markdown(f"### \U0001F9BE Total Amount: Rs. {total_amt}")

# --- Payment Selection ---
payment_method = st.selectbox("\U0001F4B3 Choose Payment Method", ["Cash", "Card", "Online"])

# --- Place Order ---
if st.button("✅ Place Order"):
    if not cart:
        st.warning("Please select at least one item.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_order = {
            "table": str(table_number),
            "items": cart,
            "status": "Preparing",
            "timestamp": timestamp,
            "payment_method": payment_method
        }

        orders = load_json(ORDERS_FILE)
        orders.append(new_order)
        save_json(ORDERS_FILE, orders)

        st.session_state.order_just_placed = True
        st.success("✅ Order placed successfully!")

# --- Your Orders ---
st.header("\U0001F4E6 Your Orders")
orders = load_json(ORDERS_FILE)
user_orders = [o for o in orders if str(o["table"]) == str(table_number)]

if not user_orders:
    st.info("You haven't placed any orders yet.")
else:
    for idx, order in enumerate(reversed(user_orders)):
        st.markdown("---")
        st.markdown(f"### \U0001FA91 Table: {order['table']} | ⏰ {order['timestamp']}")
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

        st.dataframe(pd.DataFrame(item_data), use_container_width=True)

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
                    label="\U0001F4C4 Download Invoice",
                    data=f.read(),
                    file_name=invoice_name,
                    mime="application/pdf"
                )

# --- Feedback Section ---
st.markdown("---")
st.header("\U0001F4AC Submit Feedback")
feedback_text = st.text_area("Your feedback:")
if st.button("\U0001F4DD Submit Feedback"):
    if not feedback_text.strip():
        st.warning("Feedback cannot be empty.")
    else:
        feedbacks = load_json(FEEDBACK_FILE)
        feedbacks.append({
            "table": str(table_number),
            "feedback": feedback_text.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_json(FEEDBACK_FILE, feedbacks)
        st.success("\U0001F64F Thanks for your feedback!")
        st.rerun()
