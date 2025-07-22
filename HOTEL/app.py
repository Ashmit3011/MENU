import streamlit as st
import json
import uuid
from pathlib import Path
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------- Setup ----------
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"
MENU_FILE = BASE_DIR / "menu.json"

# ---------- Load Menu ----------
def load_menu():
    if MENU_FILE.exists():
        try:
            with open(MENU_FILE, "r") as f:
                return json.load(f)
        except:
            st.error("❌ menu.json is invalid.")
            return {}
    else:
        st.warning("⚠️ menu.json not found.")
        return {}

menu = load_menu()

# ---------- Save Order ----------
def save_order(order):
    try:
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    except:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)

# ---------- Session Init ----------
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

# ---------- UI ----------
st.title("🍽 Smart Table Ordering System")

table_num = st.text_input("Enter your Table Number", key="table_input")

if table_num:

    # ---------- Category Navigation ----------
    st.sidebar.title("📂 Categories")
    for category in menu.keys():
        if st.sidebar.button(category):
            st.session_state.selected_category = category

    selected_category = st.session_state.selected_category or next(iter(menu))

    st.subheader(f"📦 Browse: {selected_category}")

    for item_id, item in menu[selected_category].items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{item['name']}** - ₹{item['price']}")
        with col2:
            qty = st.number_input(
                f"Qty for {item['name']}",
                min_value=0,
                max_value=20,
                step=1,
                key=f"qty_{item_id}"
            )
            if qty > 0:
                st.session_state.cart[item_id] = {
                    "name": item["name"],
                    "qty": qty,
                    "price": item["price"]
                }
            elif item_id in st.session_state.cart:
                del st.session_state.cart[item_id]

    # ---------- Cart System ----------
    st.markdown("## 🛒 Your Cart")
    if st.session_state.cart:
        total = 0
        for item_id, item in st.session_state.cart.items():
            st.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
            total += item['qty'] * item['price']
        st.success(f"**Total: ₹{total}**")
    else:
        st.info("Your cart is empty.")

    # ---------- Feedback ----------
    feedback = st.text_area("💬 Any feedback or special instructions?", placeholder="E.g. Less spicy, extra plates, etc.")

    # ---------- Place Order ----------
    if st.button("✅ Place Order"):
        if st.session_state.cart:
            new_order = {
                "id": str(uuid.uuid4()),
                "table": table_num,
                "items": st.session_state.cart,
                "total": total,
                "status": "Pending",
                "feedback": feedback.strip(),
                "timestamp": datetime.now().timestamp()
            }
            save_order(new_order)
            st.success("🟢 Order Placed Successfully!")
            st.session_state.cart = {}
        else:
            st.warning("⚠️ Please add items to your cart.")

# ---------- Auto Refresh ----------
st_autorefresh(interval=7000, key="app_refresh")