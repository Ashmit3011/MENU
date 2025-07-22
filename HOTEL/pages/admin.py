import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- Custom Toast ---
def custom_toast(message, toast_type="info"):
    color_map = {
        "info": "#2b78e4",
        "success": "#3cba54",
        "warning": "#f4c20d",
        "error": "#db3236"
    }
    color = color_map.get(toast_type, "#2b78e4")

    toast_html = f"""
    <div id="custom-toast" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: {color};
        color: white;
        padding: 14px 22px;
        border-radius: 8px;
        font-weight: bold;
        z-index: 9999;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        animation: fadein 0.5s, fadeout 0.5s 2.5s;
    ">
        {message}
    </div>
    <script>
        setTimeout(function() {{
            var toast = document.getElementById("custom-toast");
            if (toast) {{
                toast.style.display = "none";
            }}
        }}, 3000);
    </script>
    <style>
        @keyframes fadein {{
            from {{bottom: 0; opacity: 0;}}
            to {{bottom: 20px; opacity: 1;}}
        }}
        @keyframes fadeout {{
            from {{bottom: 20px; opacity: 1;}}
            to {{bottom: 0; opacity: 0;}}
        }}
    </style>
    """
    st.markdown(toast_html, unsafe_allow_html=True)

# --- File Paths ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_FILE = os.path.join(ROOT_DIR, "menu.json")
ORDERS_FILE = os.path.join(ROOT_DIR, "orders.json")

# --- Load Orders ---
if os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, "r") as f:
        orders = json.load(f)
else:
    orders = []

# --- Auto-Refresh ---
st_autorefresh(interval=5000, key="admin_autorefresh")

# --- Header ---
st.title("🛠️ Admin Panel - Order Management")
st.subheader("📦 Active Orders")

# --- Filter Dropdown ---
status_filter = st.selectbox("🔍 Filter by status", ["All", "Pending", "Preparing", "Completed", "Cancelled"])

def status_badge(status):
    colors = {
        "Pending": "#f39c12",
        "Preparing": "#2980b9",
        "Completed": "#27ae60",
        "Cancelled": "#c0392b"
    }
    color = colors.get(status, "#7f8c8d")
    return f'<span style="background-color:{color}; color:white; padding:4px 10px; border-radius:6px;">{status}</span>'

changed = False

# --- Orders Loop ---
for idx, order in reversed(list(enumerate(orders))):
    if status_filter != "All" and order["status"] != status_filter:
        continue

    st.markdown(f"""
    <div style="padding: 12px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px;">
        <h4>🍽️ Table <strong>{order['table']}</strong> — 🕒 {order['timestamp']} &nbsp;&nbsp; {status_badge(order['status'])}</h4>
    """, unsafe_allow_html=True)

    for name, item in order["items"].items():
        st.markdown(f"<li>{name} × {item['quantity']} = ₹{item['price'] * item['quantity']}</li>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if order["status"] == "Pending" and st.button("👨‍🍳 Mark Preparing", key=f"prep-{idx}"):
            orders[idx]["status"] = "Preparing"
            custom_toast(f"🍳 Table {order['table']} order marked Preparing", "info")
            changed = True

    with col2:
        if order["status"] == "Preparing" and st.button("✅ Complete", key=f"comp-{idx}"):
            orders[idx]["status"] = "Completed"
            custom_toast(f"✅ Table {order['table']} order Completed", "success")
            changed = True

    with col3:
        if order["status"] not in ["Completed", "Cancelled"] and st.button("❌ Cancel", key=f"cancel-{idx}"):
            orders[idx]["status"] = "Cancelled"
            custom_toast(f"❌ Table {order['table']} order Cancelled", "error")
            changed = True

    st.markdown("</div><br>", unsafe_allow_html=True)

# --- Save Changes ---
if changed:
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    st.rerun()
