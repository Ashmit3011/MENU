import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="admin_autorefresh")

# File paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
MENU_FILE = os.path.join(BASE_DIR, "menu.json")

# Load data
orders = json.load(open(ORDERS_FILE)) if os.path.exists(ORDERS_FILE) else []
menu = json.load(open(MENU_FILE)) if os.path.exists(MENU_FILE) else {}

st.title("🛠️ Admin Panel")
st.caption("Real-time order tracking and management")

# Color status map
status_colors = {
    "Preparing": "orange",
    "Ready": "green",
    "Completed": "gray"
}

# Sort orders by timestamp (latest first)
orders = sorted(orders, key=lambda x: x["timestamp"], reverse=True)

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

            # Status label
            st.markdown(
                f"<span style='color:{status_colors.get(status, 'black')}; font-weight:bold;'>Status: {status}</span>",
                unsafe_allow_html=True
            )

            # Display items in a table
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

            # Change status options
            if status != "Completed":
                new_status = st.selectbox(
                    f"Change status for Table {table}",
                    ["Preparing", "Ready", "Completed"],
                    index=["Preparing", "Ready", "Completed"].index(status),
                    key=f"status_{idx}"
                )
                if new_status != status:
                    order["status"] = new_status
                    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(orders, f, indent=2)
                    st.success(f"✅ Status updated to '{new_status}'")
                    st.rerun()

            # Invoice download section
            if status == "Completed":
                invoice_path = order.get("invoice_path")
                if invoice_path and os.path.exists(invoice_path):
                    with open(invoice_path, "rb") as f:
                        st.download_button(
                            label="📄 Download Invoice",
                            data=f.read(),
                            file_name=os.path.basename(invoice_path),
                            mime="application/pdf",
                            key=f"download_{idx}"
                        )
                else:
                    st.info("📄 Invoice not found or not generated yet.")

            # Delete completed order
            if status == "Completed":
                if st.button(f"🗑️ Delete Order (Table {table})", key=f"delete_{idx}"):
                    orders.pop(idx)
                    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                        json.dump(orders, f, indent=2)
                    st.success(f"🗑️ Order for Table {table} deleted.")
                    st.rerun()
# Feedback Viewer
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")
st.markdown("---")
st.subheader("💬 Customer Feedback")

if os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedback_data = json.load(f)

    if feedback_data:
        for entry in reversed(feedback_data):  # Show latest feedback first
            table = entry.get("table", "Unknown")
            message = entry.get("message", "")
            timestamp = entry.get("timestamp", "Unknown")
            st.info(f"🪑 Table {table} | 🕒 {timestamp}\n\n📩 {message}")
    else:
        st.write("No feedback submitted yet.")
else:
    st.write("Feedback file not found.")