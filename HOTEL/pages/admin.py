import streamlit as st
import json
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 🚀 Custom toast
def custom_toast(message: str, duration: int = 3000):
    st.markdown(f"""
        <script>
        const toast = document.createElement("div");
        toast.textContent = "{message}";
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1f1f1f;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            font-size: 14px;
            z-index: 9999;
            animation: fadein 0.5s, fadeout 0.5s ${(duration / 1000) - 0.5}s;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), {duration});
        </script>
    """, unsafe_allow_html=True)

# 📁 File paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")

# Load menu and orders
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error("Menu file not found.")
    st.stop()

if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# Auto-refresh
st_autorefresh(interval=5000, key="autorefresh")

# 💅 Streamlit-safe CSS
st.markdown("""
    <style>
    .order-box {
        background: #181818;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }
    .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 16px;
    }
    .status-pill {
        background-color: #3a3a3a;
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        text-transform: lowercase;
        font-weight: 600;
        box-shadow: inset 0 0 4px rgba(255,255,255,0.1);
    }
    .order-time {
        font-size: 13px;
        color: #aaa;
        margin-top: 4px;
    }
    .order-item {
        padding-left: 12px;
        font-size: 14px;
        margin: 6px 0;
    }
    .stButton button {
        background: transparent;
        border: 1px solid #555;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        padding: 6px 16px;
        margin: 4px 0;
        transition: 0.2s ease;
    }
    .stButton button:hover {
        background-color: #ef4444;
        color: white;
        border: 1px solid #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# 🕐 Time ago formatter
def time_ago(ts):
    try:
        t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - t
        if delta < timedelta(minutes=1):
            return "Just now"
        elif delta < timedelta(hours=1):
            return f"{int(delta.total_seconds() // 60)} min ago"
        elif delta < timedelta(days=1):
            return f"{int(delta.total_seconds() // 3600)} hr ago"
        else:
            return t.strftime("%d %b %Y %I:%M %p")
    except:
        return ts

# 🔃 Sort orders
priority = {"Pending": 0, "Preparing": 1, "Completed": 2, "Cancelled": 3}
orders = sorted(orders, key=lambda x: (priority.get(x["status"], 99), x["timestamp"]), reverse=True)

# 🛠️ Panel UI
st.markdown("### 🛠️ Admin Panel - Order Management")
st.subheader("📦 All Orders")

changed = False

if not orders:
    st.info("No orders yet.")
else:
    for idx, order in enumerate(orders):
        st.markdown(f"""
            <div class="order-box">
                <div class="order-header">
                    <strong>🍽️ Table {order['table']}</strong>
                    <div class="status-pill">{order['status'].lower()}</div>
                </div>
                <div class="order-time">⏱️ {time_ago(order['timestamp'])}</div>
                <hr style="border: none; border-top: 1px solid #333; margin: 8px 0;">
        """, unsafe_allow_html=True)

        for name, item in order["items"].items():
            st.markdown(f"""
                <div class="order-item">🍴 <b>{name}</b> x {item['quantity']} = ₹{item['price'] * item['quantity']}</div>
            """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)

        # Status change buttons
        with col1:
            if order["status"] == "Pending":
                if st.button("👨‍🍳 Preparing", key=f"prep-{idx}"):
                    orders[idx]["status"] = "Preparing"
                    changed = True
                    custom_toast(f"🍳 Table {order['table']} is now Preparing")

            elif order["status"] == "Preparing":
                if st.button("✅ Complete", key=f"comp-{idx}"):
                    orders[idx]["status"] = "Completed"
                    changed = True
                    custom_toast(f"✅ Table {order['table']} Completed")

        with col2:
            if order["status"] in ["Pending", "Preparing"]:
                if st.button("❌ Cancel", key=f"cancel-{idx}"):
                    orders[idx]["status"] = "Cancelled"
                    changed = True
                    custom_toast(f"❌ Table {order['table']} Cancelled")

        with col3:
            if order["status"] in ["Completed", "Cancelled"]:
                if st.button("🗑️ Delete", key=f"delete-{idx}"):
                    del orders[idx]
                    with open(ORDERS_FILE, "w") as f:
                        json.dump(orders, f, indent=2)
                    custom_toast(f"🗑️ Deleted order for Table {order['table']}")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# 💾 Save
if changed:
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.success("✅ Order status updated.")
