# app.py (Enhanced Customer Interface)
import streamlit as st
import json
import os
import time
import uuid
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Table Ordering", layout="wide")
st_autorefresh(interval=5000, limit=None, key="customer_refresh")

# ---------------- FILE PATHS ---------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")

# ---------------- LOADERS ----------------
def load_menu():
    with open(MENU_FILE, 'r') as f:
        return json.load(f)

def save_order(order):
    try:
        with open(ORDERS_FILE, 'r') as f:
            orders = json.load(f)
    except:
        orders = []
    orders.append(order)
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

# ---------------- STYLE ----------------
st.markdown("""
    <style>
    body {
        color: #fff;
    }
    .card {
        background-color: #ffffff;
        color: #111 !important;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: 0.3s ease;
        margin-bottom: 1rem;
    }
    .card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }
    .food-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.25rem;
    }
    .price {
        font-weight: 500;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .emoji {
        font-size: 1.2rem;
    }
    .add-btn {
        background-color: #10b981;
        border: none;
        color: white;
        padding: 0.3rem 0.8rem;
        font-weight: bold;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    .add-btn:hover {
        background-color: #059669;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- CART STATE ----------------
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# ---------------- MENU DISPLAY ----------------
st.title("🍽️ Smart Table Ordering")
menu = load_menu()

# Category Tabs
categories = list(menu.keys())
selected_category = st.selectbox("Choose Category", categories)

st.subheader(f"{selected_category} Menu")
col1, col2 = st.columns(2)

for idx, item in enumerate(menu[selected_category]):
    with [col1, col2][idx % 2]:
        with st.container():
            st.markdown(f"""
            <div class='card'>
                <h5>{item['name']}</h5>
                <p>₹{item['price']} | {'🌶️' if item.get('spicy') else ''} {'🌱' if item.get('veg') else '🍗'}</p>
                <form action="#" method="post">
                    <input type="hidden" name="item_id" value="{item['id']}">
                    <input type="number" min="1" value="1" id="qty_{item['id']}" style="width:60px;"> 
                    <button type="button" class="btn-add" onclick="sendAdd('{item['id']}', {item['price']}, '{item['name']}')">Add</button>
                </form>
            </div>
            """, unsafe_allow_html=True)

# ---------------- CART SECTION ----------------
st.sidebar.title("🛒 Your Cart")
total = 0
for key, item in st.session_state.cart.items():
    st.sidebar.write(f"{item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
    total += item['qty'] * item['price']

if total > 0:
    st.sidebar.success(f"Total: ₹{total}")
    table_no = st.sidebar.text_input("Enter Table Number")
    if st.sidebar.button("Place Order"):
        if table_no.strip() == "":
            st.sidebar.warning("Please enter table number.")
        else:
            order = {
                "id": str(uuid.uuid4())[:8],
                "table": table_no,
                "items": st.session_state.cart,
                "total": total,
                "status": "Pending",
                "timestamp": int(time.time())
            }
            save_order(order)
            st.session_state.cart = {}
            st.success("✅ Order placed successfully!")
            st.balloons()
else:
    st.sidebar.info("Your cart is empty")

# ---------------- JS TO ADD ITEM ----------------
st.markdown("""
<script>
    function sendAdd(id, price, name) {
        const qty = parseInt(document.getElementById('qty_' + id).value);
        if (qty > 0) {
            const pyCmd = `add_item("${id}", ${price}, "${name}", ${qty})`;
            const el = window.parent.document.querySelector('[data-testid="stActionButton"]');
            if (el) el.click();
            fetch("_stcore/_custom_component", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({name: "add_item", args: [id, price, name, qty]})
            });
        }
    }
</script>
""", unsafe_allow_html=True)

# ---------------- FUNCTION TO ADD ITEM ----------------
def add_item(id, price, name, qty):
    cart = st.session_state.cart
    if id in cart:
        cart[id]['qty'] += qty
    else:
        cart[id] = {"name": name, "price": price, "qty": qty}
    st.session_state.cart = cart

st.button("_trigger", key="internal_trigger")
