import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ====== File paths ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback.json")

# ====== Utility functions ======
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ====== Page config ======
st.set_page_config(page_title="Smart Table Menu", layout="wide")
st.markdown("<style>footer {visibility: hidden;} .block-container {padding-top: 2rem;} .st-emotion-cache-1avcm0n {padding-top: 1rem;} </style>", unsafe_allow_html=True)

# ====== Hide sidebar ======
st.markdown("""<style>.css-18e3th9 {visibility: hidden;}</style>""", unsafe_allow_html=True)

# ====== Load data ======
menu_data = load_json(MENU_FILE, {})
orders = load_json(ORDERS_FILE, [])
feedbacks = load_json(FEEDBACK_FILE, [])

# ====== Table input ======
table_number = st.text_input("Enter your table number", placeholder="e.g. 1, 2, 5")

# ====== Autorefresh ======
st_autorefresh(interval=3000, limit=None, key="autorefresh")

# ====== Category selection ======
categories = list(menu_data.keys())
query_params = st.query_params
selected_category = query_params.get("category", categories[0] if categories else "")

st.markdown("## 🍽️ Select Category")

# Scrollable horizontal category selector
scroll_style = """
<style>
.scroll-container {
    display: flex;
    overflow-x: auto;
    padding: 10px;
    background: #f9f9f9;
    border-radius: 10px;
    margin-bottom: 20px;
}
.scroll-container::-webkit-scrollbar {
    height: 8px;
}
.scroll-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}
.scroll-container button {
    margin-right: 10px;
    border: none;
    padding: 8px 16px;
    background-color: #3b82f6;
    color: white;
    border-radius: 20px;
    cursor: pointer;
}
.scroll-container button.selected {
    background-color: #1e40af;
}
</style>
<div class="scroll-container">
"""

category_buttons = ""
for cat in categories:
    is_selected = "selected" if cat == selected_category else ""
    category_buttons += f"<form method='get'><input type='hidden' name='category' value='{cat}'><button class='{is_selected}' type='submit'>{cat}</button></form>"

scroll_style += category_buttons + "</div>"
st.markdown(scroll_style, unsafe_allow_html=True)

# ====== Display menu items ======
if selected_category and selected_category in menu_data:
    st.markdown(f"### 🧾 Menu - {selected_category}")
    cols = st.columns(2)
    for idx, item in enumerate(menu_data[selected_category]):
        with cols[idx % 2]:
            st.markdown(f"""
                <div style='border:1px solid #e5e7eb; border-radius:10px; padding:15px; margin-bottom:10px; background:#ffffff'>
                    <h4 style='margin:0;'>{item['name']} - ₹{item['price']}</h4>
                    <form action="" method="POST">
                        <input type="hidden" name="item" value="{item['name']}">
                        <input type="hidden" name="price" value="{item['price']}">
                        <input type="number" name="qty" min="1" value="1" style="width: 50px; margin-top:10px;" />
                        <button type="submit" name="order" style="margin-left:10px;">Add</button>
                    </form>
                </div>
            """, unsafe_allow_html=True)

# ====== Add to Order ======
if "item" in st.session_state:
    name = st.session_state["item"]
    price = float(st.session_state["price"])
    qty = int(st.session_state["qty"])

    orders.append({
        "table": table_number,
        "item": name,
        "price": price,
        "qty": qty,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Pending"
    })
    save_json(ORDERS_FILE, orders)
    st.success(f"✅ Added {qty} x {name} to your order")

# ====== View Current Orders ======
st.markdown("---")
st.subheader("🧾 Your Current Orders")
table_orders = [o for o in orders if o.get("table") == table_number and o.get("status") != "Completed"]

if table_orders:
    for order in table_orders:
        st.markdown(f"- {order['qty']} x **{order['item']}** – ₹{order['price'] * order['qty']} ({order['status']})")
else:
    st.info("No orders yet.")

# ====== Feedback Section ======
completed_orders = [o for o in orders if o.get("table") == table_number and o.get("status") == "Completed"]

if completed_orders:
    st.markdown("---")
    st.subheader("📝 Leave Feedback")

    with st.form("feedback_form"):
        msg = st.text_area("Your feedback", placeholder="Type your feedback...")
        submit = st.form_submit_button("Submit Feedback")

        if submit and msg.strip():
            feedbacks.append({
                "table": table_number,
                "message": msg.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_json(FEEDBACK_FILE, feedbacks)
            st.success("✅ Feedback submitted successfully!")