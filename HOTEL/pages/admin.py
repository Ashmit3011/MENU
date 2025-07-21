import streamlit as st
import json
import os
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container
from streamlit_autorefresh import st_autorefresh

# Refresh every 3 seconds (3000 milliseconds)
st_autorefresh(interval=3000, key="refresh")

st.set_page_config(layout="wide", page_title="Admin Panel")

# Hide sidebar and default elements
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .st-emotion-cache-1avcm0n { padding: 1rem; }
        .order-card {
            background-color: #f7f7f7;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 0 10px rgba(0,0,0,0.08);
        }
        .feedback {
            background-color: #fff7d9;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📟 Live Orders")

orders_file = "orders.json"
feedback_file = "feedback.json"

# Load orders
if os.path.exists(orders_file):
    with open(orders_file, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Display orders
for order in orders:
    with stylable_container("order-card", key=order["timestamp"]):
        st.markdown(f"🪑 **Table {order['table']}** — *{order['status']}*")
        st.caption(f"⏰ {order['timestamp']}")

        for item in order.get("cart", []):
            try:
                name = item['name']
                qty = item['quantity']
                price = item['price']
                st.write(f"- {name} × {qty} = ₹{price * qty}")
            except KeyError:
                continue

        col1, col2, col3, col4 = st.columns([1,1,1,1])

        if order["status"] == "Pending":
            if col1.button("🍳 Start Preparing", key=f"prep_{order['timestamp']}"):
                order["status"] = "Preparing"
        if order["status"] == "Preparing":
            if col2.button("✅ Mark Ready", key=f"ready_{order['timestamp']}"):
                order["status"] = "Ready"
        if order["status"] in ["Pending", "Preparing"]:
            if col3.button("❌ Cancel", key=f"cancel_{order['timestamp']}"):
                order["status"] = "Cancelled"
        if col4.button("🗑️ Delete", key=f"del_{order['timestamp']}"):
            orders.remove(order)
            break

# Save updated orders
with open(orders_file, "w") as f:
    json.dump(orders, f, indent=2)

st.markdown("---")
st.subheader("📝 Customer Feedback")

# Load feedback
if os.path.exists(feedback_file):
    with open(feedback_file, "r") as f:
        feedbacks = json.load(f)
else:
    feedbacks = []

# Display feedback
for feedback in reversed(feedbacks):
    with stylable_container("feedback", key=feedback['timestamp']):
        st.markdown(f"**Table {feedback['table']} said:**")
        st.write(f"“{feedback['message']}”")
        st.caption(f"{feedback['timestamp']}")
