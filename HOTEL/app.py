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
        with open(MENU_FILE, "r") as f:
            return json.load(f)
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

# ---------- UI ----------
st.title("🧾 Smart Table Ordering System")

table_num = st.text_input("Enter your Table Number", key="table_input")

if table_num:
    order = {}
    total = 0

    st.header("🍽 Menu")
    for category, items in menu.items():
        st.subheader(category)
        for item_id, item in items.items():
            qty = st.number_input(
                f"{item['name']} - ₹{item['price']}", min_value=0, step=1, key=item_id
            )
            if qty > 0:
                order[item_id] = {
                    "name": item["name"],
                    "qty": qty,
                    "price": item["price"]
                }
                total += qty * item["price"]

    if st.button("✅ Place Order"):
        if order:
            new_order = {
                "id": str(uuid.uuid4()),
                "table": table_num,
                "items": order,
                "total": total,
                "status": "Pending",
                "timestamp": datetime.now().timestamp()
            }
            save_order(new_order)
            st.success("🟢 Order Placed Successfully!")
        else:
            st.warning("⚠️ Please select at least one item.")

# ---------- Auto Refresh every 5 seconds ----------
st_autorefresh(interval=5000, key="app_refresh")