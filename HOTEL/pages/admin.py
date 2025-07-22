import streamlit as st
import os, json, time
from datetime import datetime

# ---------- Setup ----------
st.set_page_config(page_title="Admin Panel", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ---------- Auto Refresh ----------
if 'last_refresh' not in st.session_state or time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()

# ---------- Load Functions ----------
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# ---------- UI ----------
st.title("🛠️ Admin Dashboard")
orders = load_orders()

if not orders:
    st.info("No orders yet.")
    st.stop()

for i, order in enumerate(sorted(orders, key=lambda x: x["timestamp"], reverse=True)):
    st.markdown(f"### Order `{order['id']}` | Table {order['table']}")
    for name, info in order["items"].items():
        st.write(f"- {name} x {info['qty']} = ₹{info['qty'] * info['price']}")
    st.write(f"💵 **Total: ₹{order['total']}**")
    st.write(f"🕒 Placed: {datetime.fromtimestamp(order['timestamp']).strftime('%d-%b %I:%M %p')}")

    status = order["status"]
    if status == "Cancelled":
        st.markdown("<span style='color:red'><s>🚫 Cancelled</s></span>", unsafe_allow_html=True)
    elif status == "Completed":
        st.success("✅ Completed")
    elif status == "Preparing":
        st.info("🍳 Preparing")
    else:
        st.warning("⌛ Pending")

    if status not in ["Completed", "Cancelled"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Preparing", key=f"prep_{i}"):
                orders[i]["status"] = "Preparing"
                save_orders(orders)
                st.rerun()
        with col2:
            if st.button("✅ Complete", key=f"comp_{i}"):
                orders[i]["status"] = "Completed"
                save_orders(orders)
                st.rerun()
        with col3:
            if st.button("❌ Cancel", key=f"admin_cancel_{i}"):
                orders[i]["status"] = "Cancelled"
                save_orders(orders)
                st.rerun()
    st.markdown("---")