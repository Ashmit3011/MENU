import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# --- File Paths ---
BASE_DIR = Path(__file__).parent.resolve()
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# --- Utility Functions ---
def load_json(path):
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# --- Session Init ---
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""

# --- UI Config ---
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
hide_sidebar = """
<style>
    [data-testid="stSidebar"] {display: none;}
</style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# --- Load Menu & Orders ---
menu = load_json(MENU_FILE)
orders = load_json(ORDERS_FILE)

# --- Table Entry ---
st.title("🍽️ Smart Table Ordering")
table = st.text_input("Enter your Table Number", value=st.session_state.table)
if table:
    st.session_state.table = table

# --- Display Menu ---
st.header("📋 Menu")
categories = sorted(set(item["category"] for item in menu))
selected_category = st.selectbox("Filter by Category", ["All"] + categories)

for item in menu:
    if selected_category != "All" and item["category"] != selected_category:
        continue

    with st.container():
        cols = st.columns([3, 2, 2, 2])
        cols[0].markdown(f"**{item['name']}**")
        cols[1].markdown(f"₹{item['price']}")
        added = False
        if cols[2].button("➕", key=f"add_{item['id']}"):
            for cart_item in st.session_state.cart:
                if cart_item["id"] == item["id"]:
                    cart_item["qty"] += 1
                    added = True
                    break
            if not added:
                st.session_state.cart.append({
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "qty": 1
                })
        if cols[3].button("➖", key=f"minus_{item['id']}"):
            for cart_item in st.session_state.cart:
                if cart_item["id"] == item["id"]:
                    cart_item["qty"] -= 1
                    if cart_item["qty"] <= 0:
                        st.session_state.cart.remove(cart_item)
                    break

# --- Cart ---
if st.session_state.cart:
    st.header("🛒 Your Cart")
    total = 0

    for item in st.session_state.cart:
        item_total = item['qty'] * item['price']
        total += item_total

        with st.container():
            st.markdown(f"""
            <div style="
                background-color:#fefefe;
                border-radius:15px;
                padding:15px;
                margin:10px 0;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                ">
                <h5 style="margin-bottom:5px;">🍽️ {item['name']}</h5>
                <div style="display:flex; justify-content: space-between;">
                    <span>💰 ₹{item['price']} x {item['qty']}</span>
                    <span>🧾 ₹{item_total}</span>
                </div>
                <div style="margin-top:10px;">
                    <form action="" method="post">
                        <button name="add_{item['id']}" type="submit" style="margin-right:8px;">➕</button>
                        <button name="minus_{item['id']}" type="submit">➖</button>
                    </form>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Plus/Minus functionality
        if st.button("➕", key=f"cart_add_{item['id']}"):
            item['qty'] += 1
        if st.button("➖", key=f"cart_minus_{item['id']}"):
            item['qty'] -= 1
            if item['qty'] <= 0:
                st.session_state.cart.remove(item)

    st.markdown(f"<h3 style='text-align:right;'>Grand Total: ₹{total}</h3>", unsafe_allow_html=True)

    if st.button("✅ Place Order"):
        if not st.session_state.table:
            st.error("Please enter your table number!")
        else:
            order = {
                "id": len(orders) + 1,
                "table": st.session_state.table,
                "cart": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders.append(order)
            save_json(ORDERS_FILE, orders)
            st.session_state.cart = []
            st.success("✅ Order placed successfully!")


# --- Order Tracking ---
st.markdown("---")
st.subheader("📦 Track Your Latest Order")
table_orders = [o for o in orders if o["table"] == table]
if table_orders:
    latest_order = table_orders[-1]
    status = latest_order["status"]
    timestamp = latest_order["timestamp"]
    st.write(f"**Order ID:** #{latest_order['id']} | 🕒 Placed at {timestamp}")
    st.write(f"**Current Status:** `{status}`")

    status_progress = {
        "Pending": 0.25,
        "Preparing": 0.5,
        "Served": 0.75,
        "Completed": 1.0
    }
    progress = status_progress.get(status, 0.0)
    st.progress(progress)

    if status == "Pending":
        if st.button("❌ Cancel Order"):
            orders = [o for o in orders if o["id"] != latest_order["id"]]
            save_json(ORDERS_FILE, orders)
            st.warning("🛑 Order cancelled.")
    elif status == "Completed":
        st.success("✅ Your order is completed. Bon appétit!")
    elif status == "Served":
        st.info("🍽️ Your food has been served.")
    elif status == "Preparing":
        st.info("👨‍🍳 Your food is being prepared.")
    else:
        st.warning("⏳ Waiting for kitchen to accept your order.")
else:
    st.info("No recent order found for your table.")

# --- Feedback Form ---
st.markdown("---")
st.header("💬 Leave Feedback")
rating = st.slider("Rate your experience", 1, 5)
comments = st.text_area("Additional comments")
if st.button("📨 Submit Feedback"):
    feedbacks = load_json(FEEDBACK_FILE)
    feedbacks.append({
        "table": table,
        "rating": rating,
        "comments": comments,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(FEEDBACK_FILE, feedbacks)
    st.success("🙏 Thanks for your feedback!")
