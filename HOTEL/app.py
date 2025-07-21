import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import time

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent
MENU_FILE = BASE_DIR / "menu.json"
ORDERS_FILE = BASE_DIR / "orders.json"
FEEDBACK_FILE = BASE_DIR / "feedback.json"

# === Streamlit Setup ===
st.set_page_config(page_title="🍽️ Order Menu", layout="centered")
hide_sidebar_style = "<style>div[data-testid='stSidebar'] { display: none; }</style>"
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# === Loaders ===
def load_json(file, default):
    if not file.exists():
        with open(file, "w") as f:
            json.dump(default, f)
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

menu = load_json(MENU_FILE, [])
orders = load_json(ORDERS_FILE, [])
feedbacks = load_json(FEEDBACK_FILE, [])

# === Session State Init ===
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "order_status" not in st.session_state:
    st.session_state.order_status = None

# === Title & Table Entry ===
st.title("🍽️ Smart Menu")

if st.session_state.order_id:
    # === Order Status Tracking ===
    orders = load_json(ORDERS_FILE, [])
    current_order = next((o for o in orders if o["id"] == st.session_state.order_id), None)

    if current_order:
        st.subheader("📦 Your Order Status")
        status = current_order["status"]
        st.success(f"Status: **{status}**")

        if status == "Served":
            st.markdown("---")
            st.subheader("💬 Leave Feedback")
            with st.form("feedback_form"):
                rating = st.slider("Rate your experience", 1, 5, 5)
                text = st.text_area("Comments")
                if st.form_submit_button("Submit"):
                    feedbacks.append({
                        "order_id": st.session_state.order_id,
                        "rating": rating,
                        "text": text
                    })
                    save_json(FEEDBACK_FILE, feedbacks)
                    st.success("Thanks for your feedback!")
                    st.session_state.order_id = None
                    st.session_state.order_status = None
                    st.session_state.cart = {}
                    st.stop()
        time.sleep(5)
        st.rerun()
    else:
        st.warning("Waiting for your order to be registered...")
        time.sleep(5)
        st.rerun()
else:
    # === Table Entry ===
    table = st.text_input("Enter your table number")
    st.markdown("---")

    # === Filter Menu by Category ===
    categories = sorted(set([item["category"] for item in menu]))
    selected_cat = st.selectbox("Select Category", categories)

    filtered_menu = [m for m in menu if m["category"] == selected_cat]
    for item in filtered_menu:
        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown(f"**{item['name']}**")
            st.markdown(f"₹{item['price']}")
        with col2:
            item_id = str(item["id"])
            qty = st.session_state.cart.get(item_id, {}).get("qty", 0)

            colA, colB, colC = st.columns([1, 1, 1])
            with colA:
                if st.button("-", key=f"minus_{item_id}") and qty > 0:
                    st.session_state.cart[item_id]["qty"] -= 1
                    if st.session_state.cart[item_id]["qty"] <= 0:
                        del st.session_state.cart[item_id]
            with colB:
                st.markdown(f"<center>{qty}</center>", unsafe_allow_html=True)
            with colC:
                if st.button("+", key=f"plus_{item_id}"):
                    if item_id not in st.session_state.cart:
                        st.session_state.cart[item_id] = {"name": item["name"], "price": item["price"], "qty": 1}
                    else:
                        st.session_state.cart[item_id]["qty"] += 1

        st.markdown("---")

    # === Cart Display ===
    if st.session_state.cart:
        st.subheader("🛒 Your Cart")
        total = 0
        for item_id, data in st.session_state.cart.items():
            line_total = data["qty"] * data["price"]
            total += line_total
            st.markdown(f"- {data['name']} x {data['qty']} = ₹{line_total}")
        st.markdown(f"**💰 Total: ₹{total}**")

        if table and st.button("✅ Place Order"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_order = {
                "id": f"O{int(time.time())}",
                "table": table,
                "items": list(st.session_state.cart.values()),
                "total": total,
                "status": "Pending",
                "time": now
            }
            orders.append(new_order)
            save_json(ORDERS_FILE, orders)
            st.success("Order placed successfully! 🥳")
            st.balloons()
            st.session_state.order_id = new_order["id"]
            st.session_state.order_status = "Pending"
            st.rerun()
    else:
        st.info("Add items to your cart to proceed.")
