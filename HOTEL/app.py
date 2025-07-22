import streamlit as st
import json
import os
from datetime import datetime

# --- File paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# --- Load menu ---
def load_menu():
    with open(MENU_FILE, "r") as f:
        return json.load(f)

# --- Save orders ---
def save_order(order):
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            orders = json.load(f)
    else:
        orders = []

    orders.append(order)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)

# --- Streamlit App ---
st.set_page_config(page_title="Smart Menu", layout="wide")
st.title("🍽️ Smart Table Ordering")
table_no = st.sidebar.text_input("Enter Table Number", value="1")

if "cart" not in st.session_state:
    st.session_state.cart = []

menu = load_menu()

# Display menu sections
for section, items in menu.items():
    with st.expander(f"🍴 {section}"):
        for item in items:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['name']}** — ₹{item['price']}")
            with col2:
                qty = st.number_input(f"Qty for {item['name']}", min_value=0, step=1, key=item["name"])
                if qty > 0:
                    # Check if item already in cart
                    existing = next((i for i in st.session_state.cart if i["name"] == item["name"]), None)
                    if existing:
                        existing["quantity"] = qty
                    else:
                        st.session_state.cart.append({
                            "name": item["name"],
                            "price": item["price"],
                            "quantity": qty
                        })

# Cart section
st.markdown("## 🛒 Cart")
total = 0
if st.session_state.cart:
    for item in st.session_state.cart:
        try:
            subtotal = item["price"] * item["quantity"]
            total += subtotal
            st.markdown(f"- {item['name']} × {item['quantity']} = ₹{subtotal}")
        except KeyError as e:
            st.error(f"Missing key in item: {e}")

    st.markdown(f"**Total: ₹{total}**")
    if st.button("✅ Place Order"):
        order = {
            "table": table_no,
            "items": st.session_state.cart,
            "total": total,
            "status": "Pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_order(order)
        st.success("Order placed successfully!")
        st.session_state.cart = []
else:
    st.info("No items in cart.")