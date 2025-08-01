import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="admin_autorefresh")

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "..", "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "..", "menu.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "..", "feedback.json")

# Load JSON
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

# Save JSON
def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

# PDF Generator
def generate_invoice_pdf(order, save_dir="invoices"):
    os.makedirs(save_dir, exist_ok=True)
    filename = f"Invoice_Table{order['table']}_{order['timestamp'].replace(':','-').replace(' ','_')}.pdf"
    filepath = os.path.join(save_dir, filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, height - 50, "Customer Invoice")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Table No: {order['table']}")
    c.drawString(50, height - 120, f"Date & Time: {order['timestamp']}")
    c.drawString(50, height - 140, f"Payment Method: {order.get('payment', 'N/A')}")

    c.drawString(50, height - 180, "Items Ordered:")
    y = height - 200
    total = 0

    for name, item in order["items"].items():
        qty = item["quantity"]
        price = item["price"]
        subtotal = qty * price
        total += subtotal
        c.drawString(60, y, f"{name} x {qty} = ₹{subtotal}")
        y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, f"Total Amount: ₹{total}")
    c.showPage()
    c.save()
    return filepath

# Toast notification (new orders)
if 'last_order_count' not in st.session_state:
    st.session_state.last_order_count = 0

# App title
st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠️ Admin Panel")

# Load orders and menu
orders = load_json(ORDERS_FILE)
menu = load_json(MENU_FILE)

# Notify on new order
if len(orders) > st.session_state.last_order_count:
    st.toast("📥 New order received!", icon="✅")
st.session_state.last_order_count = len(orders)

# Display current orders
st.subheader("📦 Current Orders")

if not orders:
    st.info("No orders yet.")
else:
    for idx, order in enumerate(reversed(orders)):
        status = order.get("status", "Pending")
        if status != "Completed":
            table = order.get("table", "?")
            timestamp = order.get("timestamp", "N/A")
            items = order.get("items", {})
            payment_method = order.get("payment", "N/A")
            total = sum(details.get("price", 0) * details.get("quantity", 0) for details in items.values())

            with st.container():
                st.markdown(f"### 🪑 Table {table} - ⏳ {status}")
                st.caption(f"🕒 {timestamp}")
                st.markdown(f"💳 Payment Method: **{payment_method}**")
                if payment_method == "Cash":
                    st.markdown(f"<div style='color:yellow; font-weight:bold;'>⚠️ Customer will pay by CASH at Table {table}</div>", unsafe_allow_html=True)

                st.markdown("#### 🍽️ Ordered Items")
                for name, details in items.items():
                    qty = details.get("quantity", 0)
                    price = details.get("price", 0)
                    subtotal = price * qty
                    st.markdown(f"🔸 {name} x {qty} = ₹{subtotal}")

                st.markdown(f"**💰 Total: ₹{total}**")

                # Actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Mark as Completed", key=f"complete_{idx}"):
                        orders[len(orders) - 1 - idx]["status"] = "Completed"
                        save_json(ORDERS_FILE, orders)
                        st.success(f"Order from Table {table} marked as Completed")
                        st.rerun()

                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        orders.pop(len(orders) - 1 - idx)
                        save_json(ORDERS_FILE, orders)
                        st.warning("Order deleted")
                        st.rerun()

# Divider
st.markdown("---")
st.subheader("📜 Order History (Completed Orders)")

# Completed orders
history_orders = [o for o in reversed(orders) if o.get("status") == "Completed"]
if not history_orders:
    st.info("No completed orders yet.")
else:
    for idx, order in enumerate(history_orders):
        table = order.get("table", "?")
        timestamp = order.get("timestamp", "N/A")
        items = order.get("items", {})
        payment_method = order.get("payment", "N/A")
        total = sum(details.get("price", 0) * details.get("quantity", 0) for details in items.values())

        with st.expander(f"🧾 Table {table} | {timestamp} | ₹{total}", expanded=False):
            st.markdown(f"💳 Payment Method: **{payment_method}**")

            for name, details in items.items():
                qty = details.get("quantity", 0)
                price = details.get("price", 0)
                subtotal = qty * price
                st.markdown(f"🔸 {name} x {qty} = ₹{subtotal}")

            st.markdown(f"**💰 Total: ₹{total}**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧾 Generate Invoice", key=f"invoice_{idx}"):
                    filepath = generate_invoice_pdf(order)
                    with open(filepath, "rb") as f:
                        st.download_button("📥 Download Invoice", data=f, file_name=os.path.basename(filepath), mime="application/pdf")

            with col2:
                if st.button("🗑️ Delete", key=f"delete_history_{idx}"):
                    orders.remove(order)
                    save_json(ORDERS_FILE, orders)
                    st.warning("🗑️ Order deleted from history")
                    st.rerun()

# Divider
st.markdown("---")
st.subheader("💬 Customer Feedback")

feedback = load_json(FEEDBACK_FILE)
if not feedback:
    st.info("No feedback received yet.")
else:
    for idx, fb in enumerate(reversed(feedback)):
        actual_index = len(feedback) - 1 - idx  # Index in the original list
        table = fb.get("table", "?")
        message = fb.get("message", "No message")
        rating = fb.get("rating", "N/A")
        time = fb.get("timestamp", "Unknown time")

        with st.chat_message("user"):
            st.markdown(f"**🪑 Table {table}** — 🕒 {time}")
            st.write(f"⭐ Rating: {rating}")
            st.write(f"💬 {message}")

            if st.button("🗑️ Delete Feedback", key=f"delete_feedback_{idx}"):
                feedback.pop(actual_index)
                save_json(FEEDBACK_FILE, feedback)
                st.warning("Feedback deleted.")
                st.rerun()