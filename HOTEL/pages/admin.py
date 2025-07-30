import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="admin_autorefresh")

# File paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")

# Ensure invoice directory exists
os.makedirs(INVOICE_DIR, exist_ok=True)

# Load orders
orders = json.load(open(ORDERS_FILE)) if os.path.exists(ORDERS_FILE) else []

# Load menu and convert to dict
if os.path.exists(MENU_FILE):
    raw_menu = json.load(open(MENU_FILE))
    menu = {item["id"]: item for item in raw_menu}
else:
    menu = {}

# Sort orders by timestamp
orders = sorted(orders, key=lambda x: x["timestamp"], reverse=True)

st.title("🛠️ Admin Panel")
st.caption("Real-time order tracking and management")

status_colors = {
    "Preparing": "orange",
    "Ready": "green",
    "Completed": "gray"
}

# Function to generate invoice PDF
def generate_invoice(order, items_data, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"🧾 Invoice - Table {order['table']}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Timestamp: {order['timestamp']}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 10, "Item", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(40, 10, "Price", 1)
    pdf.cell(60, 10, "Total", 1)
    pdf.ln()

    total_amount = 0
    for row in items_data:
        pdf.set_font("Arial", "", 12)
        pdf.cell(60, 10, row["Item"], 1)
        pdf.cell(30, 10, str(row["Quantity"]), 1)
        pdf.cell(40, 10, f"{row['Price']:.2f}", 1)
        total = row["Quantity"] * row["Price"]
        total_amount += total
        pdf.cell(60, 10, f"{total:.2f}", 1)
        pdf.ln()
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(130, 10, "Grand Total", 1)
    pdf.cell(60, 10, f"{total_amount:.2f}", 1)
    
    pdf.output(file_path)

# Admin order management
if not orders:
    st.info("No orders found.")
else:
    for idx, order in enumerate(orders):
        with st.container():
            st.markdown("---")
            status = order["status"]
            table = order["table"]
            items = order["items"]
            timestamp = order["timestamp"]

            st.markdown(
                f"<h4>🪑 Table: {table} | 🕒 {timestamp}</h4>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<span style='color:{status_colors.get(status, 'black')}; font-weight:bold;'>Status: {status}</span>",
                unsafe_allow_html=True
            )

            # Item breakdown
            item_data = []
            for item_id, quantity in items.items():
                item = menu.get(item_id, {"name": "Unknown", "price": 0})
                item_data.append({
                    "Item": item["name"],
                    "Quantity": quantity,
                    "Price": item["price"],
                    "Total": quantity * item["price"]
                })

            st.dataframe(pd.DataFrame(item_data), use_container_width=True)

            # Status change
            if status != "Completed":
                new_status = st.selectbox(
                    f"Change status for Table {table}",
                    ["Preparing", "Ready", "Completed"],
                    index=["Preparing", "Ready", "Completed"].index(status),
                    key=f"status_{idx}"
                )
                if new_status != status:
                    order["status"] = new_status

                    # Generate invoice if moved to Completed
                    if new_status == "Completed":
                        invoice_file = os.path.join(
                            INVOICE_DIR, f"invoice_table{table}_{timestamp.replace(':', '-')}.pdf"
                        )
                        generate_invoice(order, item_data, invoice_file)
                        order["invoice_path"] = invoice_file

                    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(orders, f, indent=2)
                    st.success(f"✅ Status updated to '{new_status}'")
                    st.rerun()

            # Invoice download for completed orders
            if status == "Completed":
                invoice_path = order.get("invoice_path")
                if invoice_path and os.path.exists(invoice_path):
                    with open(invoice_path, "rb") as f:
                        st.download_button(
                            label="📄 Download Invoice",
                            data=f.read(),
                            file_name=os.path.basename(invoice_path),
                            mime="application/pdf",
                            key=f"invoice_{idx}"
                        )
                else:
                    st.info("📄 Invoice not found or not generated yet.")

                if st.button(f"🗑️ Delete Order (Table {table})", key=f"delete_{idx}"):
                    orders.pop(idx)
                    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(orders, f, indent=2)
                    st.success(f"🗑️ Order for Table {table} deleted.")
                    st.rerun()

# Feedback section
st.markdown("---")
st.subheader("💬 Customer Feedback")

if os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedback_data = json.load(f)

    if feedback_data:
        for entry in reversed(feedback_data):
            table = entry.get("table", "Unknown")
            message = entry.get("message", "")
            timestamp = entry.get("timestamp", "Unknown")
            st.info(f"🪑 Table {table} | 🕒 {timestamp}\n\n📩 {message}")
    else:
        st.write("No feedback submitted yet.")
else:
    st.write("Feedback file not found.")