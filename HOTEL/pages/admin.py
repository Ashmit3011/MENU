import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import time

# ---- Paths ----
BASE_DIR = Path(__file__).resolve().parent.parent
ORDER_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# ---- Page Config ----
st.set_page_config(page_title="Admin Panel", layout="wide", initial_sidebar_state="collapsed")

# ---- Utility Functions ----
def load_json(file_path):
    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ---- Load Orders ----
orders = load_json(ORDER_FILE)
feedback_data = load_json(FEEDBACK_FILE)

# ---- Title ----
st.title("🧾 Admin Dashboard")
st.markdown("### Live Orders")

# ---- New Order Sound Effect ----
if "last_order_count" not in st.session_state:
    st.session_state.last_order_count = len(orders)

if len(orders) > st.session_state.last_order_count:
    st.audio("https://www.soundjay.com/buttons/sounds/button-3.mp3", autoplay=True)
    st.toast("New order received!", icon="✅")

st.session_state.last_order_count = len(orders)

# ---- Display Orders ----
if not orders:
    st.info("No orders yet.")
else:
    for i, order in enumerate(orders):
        with st.container():
            status = order.get("status", "placed").capitalize()
            status_color = {
                "Placed": "gray",
                "Preparing": "orange",
                "Ready": "green",
                "Cancelled": "red"
            }.get(status, "gray")

            st.markdown(f"""
            <div style='padding: 1rem; border-radius: 12px; background-color: #f9f9f9; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 1rem;'>
                <strong>🪑 Table:</strong> {order.get("table")} &nbsp;|&nbsp; 
                <strong>Status:</strong> <span style='color:{status_color};'>{status}</span><br>
                <strong>🕒 Placed:</strong> {order.get("timestamp")}
            </div>
            """, unsafe_allow_html=True)

            for item in order.get("cart", []):
                name = item.get("name", "Unknown")
                qty = item.get("quantity", 1)
                price = item.get("price", 0)
                st.write(f"- {name} × {qty} = ₹{price * qty}")

            # Status buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("👨‍🍳 Start Preparing", key=f"prep_{i}"):
                    order["status"] = "preparing"
                    save_json(ORDER_FILE, orders)
                    st.experimental_rerun()
            with col2:
                if st.button("✅ Mark Ready", key=f"ready_{i}"):
                    order["status"] = "ready"
                    save_json(ORDER_FILE, orders)
                    st.experimental_rerun()
            with col3:
                if st.button("❌ Cancel", key=f"cancel_{i}"):
                    order["status"] = "cancelled"
                    save_json(ORDER_FILE, orders)
                    st.experimental_rerun()
            with col4:
                if st.button("🗑 Delete", key=f"del_{i}"):
                    orders.pop(i)
                    save_json(ORDER_FILE, orders)
                    st.experimental_rerun()

# ---- Feedback Section ----
st.markdown("---")
st.subheader("📝 Customer Feedback")

if not feedback_data:
    st.info("No feedback submitted yet.")
else:
    for fb in reversed(feedback_data):
        st.markdown(f"""
        <div style='background-color:#fffbe6;padding:1rem;border-left:5px solid #ffc107;margin-bottom:1rem;border-radius:6px;'>
            <strong>Table {fb.get("table", "N/A")}</strong> said:<br>
            <em>“{fb.get("message", "No message")}”</em><br>
            <small>{fb.get("timestamp")}</small>
        </div>
        """, unsafe_allow_html=True)

# ---- Auto Refresh ----
st.markdown(
    """
    <script>
    setTimeout(function() { window.location.reload(); }, 10000);
    </script>
    """,
    unsafe_allow_html=True
)
