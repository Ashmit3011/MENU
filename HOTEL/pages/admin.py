import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Admin Dashboard", layout="centered")

# Inject auto-refresh every 3 seconds
st.markdown("""
    <meta http-equiv="refresh" content="3">
""", unsafe_allow_html=True)

orders_file = os.path.join("..", "orders.json")
feedback_file = os.path.join("..", "feedback.json")

st.title("📋 Live Orders")

if os.path.exists(orders_file):
    with open(orders_file, "r") as f:
        orders = json.load(f)
else:
    orders = []

status_colors = {
    "Pending": "orange",
    "Preparing": "gold",
    "Ready": "limegreen",
    "Cancelled": "red"
}

updated_orders = []

for order in orders:
    status = order.get("status", "Pending")
    status_color = status_colors.get(status, "white")

    with st.container():
        st.markdown(
            f"""
            <div style="background-color: #2a2a2a; padding: 1rem; border-radius: 1rem; 
                        box-shadow: 0 0 10px rgba(255,255,255,0.05); margin-bottom: 1rem;">
                <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">
                    🧾 <strong>Order #{order['order_id']}</strong> —
                    <span style="color: {status_color};">{status}</span><br>
                    ⏰ {order.get('timestamp', '')}
                </p>
            </div>
            """, unsafe_allow_html=True
        )

        for item in order.get("cart", []):
            st.write(f"- {item['name']} × {item['quantity']} = ₹{item['price'] * item['quantity']}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🍳 Start Preparing", key=f"prepare_{order['order_id']}"):
                order["status"] = "Preparing"
        with col2:
            if st.button("✅ Mark Ready", key=f"ready_{order['order_id']}"):
                order["status"] = "Ready"
        with col3:
            if st.button("❌ Cancel", key=f"cancel_{order['order_id']}"):
                order["status"] = "Cancelled"
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{order['order_id']}"):
                continue  # Skip adding to updated list

    updated_orders.append(order)

# Save updated order status
with open(orders_file, "w") as f:
    json.dump(updated_orders, f, indent=4)

st.markdown("---")
st.subheader("📝 Customer Feedback")

if os.path.exists(feedback_file):
    with open(feedback_file, "r") as f:
        feedback_list = json.load(f)
else:
    feedback_list = []

if not feedback_list:
    st.info("No feedback yet.")

for entry in reversed(feedback_list):
    st.markdown(
        f"""
        <div style="background-color: #fef3c7; color: #111827; padding: 1rem; margin-bottom: 1rem;
                    border-radius: 1rem; box-shadow: 0 0 5px rgba(0,0,0,0.1);">
            <p><strong>Table {entry['table']}</strong> said:</p>
            <p>“{entry['message']}”</p>
            <small>{entry['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True
    )
