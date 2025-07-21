import streamlit as st
import json
import os
from datetime import datetime

# Auto refresh every 3 seconds
st.set_page_config(layout="wide", page_title="Admin Panel")
st.experimental_set_query_params()  # for smooth refresh workaround

# Hide sidebar and padding
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .st-emotion-cache-1avcm0n { padding: 1rem; }
        .order-card {
            background-color: #f3f4f6;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }
        .feedback {
            background-color: #fefce8;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        }
        h1, h3, .stButton > button {
            color: #1f2937;
        }
    </style>
""", unsafe_allow_html=True)

# Auto-refresh workaround
st.markdown("""
<script>
    setTimeout(function() {
        window.location.reload();
    }, 3000);
</script>
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

# Display Orders
for order in orders:
    with st.container():
        with st.container():
            st.markdown(f"""
            <div class="order-card">
                <h4>🪑 Table {order.get('table', '?')} — <em>{order.get('status', 'Unknown')}</em></h4>
                <p style='font-size: 0.85rem; color: gray;'>⏰ {order.get('timestamp', '')}</p>
            </div>
            """, unsafe_allow_html=True)

        for item in order.get("cart", []):
            try:
                name = item.get('name', '')
                qty = item.get('quantity', 0)
                price = item.get('price', 0)
                st.markdown(f"- **{name}** × {qty} = ₹{price * qty}")
            except Exception:
                continue

        col1, col2, col3, col4 = st.columns(4)

        if order.get("status") == "Pending":
            if col1.button("🍳 Start Preparing", key=f"prep_{order['timestamp']}"):
                order["status"] = "Preparing"
        if order.get("status") == "Preparing":
            if col2.button("✅ Mark Ready", key=f"ready_{order['timestamp']}"):
                order["status"] = "Ready"
        if order.get("status") in ["Pending", "Preparing"]:
            if col3.button("❌ Cancel", key=f"cancel_{order['timestamp']}"):
                order["status"] = "Cancelled"
        if col4.button("🗑️ Delete", key=f"delete_{order['timestamp']}"):
            orders.remove(order)
            break

# Save updates
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

for fb in reversed(feedbacks):
    with st.container():
        st.markdown(f"""
        <div class="feedback">
            <strong>🪑 Table {fb.get('table', '?')} said:</strong>
            <p>{fb.get('message', '')}</p>
            <p style='font-size: 0.8rem; color: gray;'>{fb.get('timestamp', '')}</p>
        </div>
        """, unsafe_allow_html=True)
