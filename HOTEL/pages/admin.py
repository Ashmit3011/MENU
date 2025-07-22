import streamlit as st
import json
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 🚀 Custom toast using HTML
def custom_toast(message: str, duration: int = 3000):
    st.markdown(
        f"""
        <script>
        const toast = document.createElement("div");
        toast.textContent = "{message}";
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #323232;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-size: 14px;
            z-index: 9999;
            animation: fadein 0.5s, fadeout 0.5s {duration / 1000 - 0.5}s;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), {duration});
        </script>
        """,
        unsafe_allow_html=True
    )

# 📁 File paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")

# 📦 Load menu
if os.path.exists(MENU_FILE):
    with open(MENU_FILE, "r") as f:
        menu = json.load(f)
else:
    st.error(f"❌ Menu file not found at {MENU_FILE}")
    st.stop()

# 📄 Load orders
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# 🔁 Auto-refresh
st_autorefresh(interval=5000, key="admin_autorefresh")

# 🧠 CSS styles for dark theme
st.markdown("""
    <style>
    .order-card {
        border: 1px solid #444;
        padding: 16px;
        border-radius: 12px;
        background-color: #1e1e1e;
        margin-bottom: 20px;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.05);
        animation: fadeIn 0.5s ease-in-out;
    }
    .status-badge {
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: bold;
        font-size: 12px;
        color: white;
        text-transform: capitalize;
    }
    .stButton button {
        padding: 0.4rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        margin: 6px 0;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
""", unsafe_allow_html=True)

# 💬 Human-readable time
def time_ago(timestamp_str):
    try:
        t = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - t
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            return f"{int(diff.total_seconds() // 60)} min ago"
        elif diff < timedelta(days=1):
            return f"{int(diff.total_seconds() // 3600)} hr ago"
        else:
            return t.strftime("%d %b %Y %I:%M %p")
    except:
        return timestamp_str

# 🎨 Status color mapping
def get_status_color(status):
    return {
        "Pending": "#f59e0b",      # amber
        "Preparing": "#3b82f6",    # blue
        "Completed": "#22c55e",    # green
        "Cancelled": "#ef4444",    # red
    }.get(status, "#888")

# 🔃 Sort orders: Pending > Preparing > Others
status_priority = {"Pending": 0, "Preparing": 1, "Completed": 2, "Cancelled": 3}
orders = sorted(orders, key=lambda x: (status_priority.get(x["status"], 99), x["timestamp"]), reverse=True)

# 🧠 Panel Header
st.markdown("### 🛠️ Admin Panel - Order Management")
st.subheader("📦 All Orders")

changed = False

if not orders:
    st.info("No orders yet.")
else:
    for idx, order in enumerate(orders):
        status = order["status"]
        color = get_status_color(status)

        st.markdown(f"""
        <div class="order-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div><strong>🍽️ Table {order['table']}</strong></div>
                <div class="status-badge" style="background-color:{color};">{status}</div>
            </div>
            <div style="font-size: 13px; color: #aaa;">⏱️ {time_ago(order['timestamp'])}</div>
            <hr style="border: none; border-top: 1px solid #333; margin: 10px 0;">
        """, unsafe_allow_html=True)

        for name, item in order["items"].items():
            st.markdown(f"""
                <div style="padding-left: 10px; margin-bottom: 5px;">
                    🍴 <b>{name}</b> x {item['quantity']} = ₹{item['price'] * item['quantity']}
                </div>
            """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if status == "Pending" and st.button("👨‍🍳 Preparing", key=f"prep-{idx}"):
                orders[idx]["status"] = "Preparing"
                changed = True
                custom_toast(f"🍳 Table {order['table']} is now Preparing")

        with col2:
            if status == "Preparing" and st.button("✅ Complete", key=f"comp-{idx}"):
                orders[idx]["status"] = "Completed"
                changed = True
                custom_toast(f"✅ Table {order['table']} marked as Completed")

        with col3:
            if status not in ["Completed", "Cancelled"] and st.button("❌ Cancel", key=f"cancel-{idx}"):
                orders[idx]["status"] = "Cancelled"
                changed = True
                custom_toast(f"❌ Table {order['table']} Cancelled")

        with col4:
            if status == "Completed" and st.button("🗑️ Delete", key=f"delete-{idx}"):
                del orders[idx]
                with open(ORDERS_FILE, "w") as f:
                    json.dump(orders, f, indent=2)
                custom_toast(f"🗑️ Deleted completed order for Table {order['table']}")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)  # close order-card div

# 💾 Save updates
if changed:
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.success("✅ Order status updated.")
