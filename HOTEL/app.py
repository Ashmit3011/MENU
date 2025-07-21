import streamlit as st
import json
import uuid
from datetime import datetime

# Load menu
def load_menu():
    try:
        with open("menu.json", "r") as f:
            return json.load(f)
    except:
        return []

# Save orders
def save_order(order):
    try:
        with open("orders.json", "r") as f:
            orders = json.load(f)
    except:
        orders = []

    orders.append(order)
    with open("orders.json", "w") as f:
        json.dump(orders, f, indent=2)

# Save feedback
def save_feedback(feedback):
    try:
        with open("feedback.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(feedback)
    with open("feedback.json", "w") as f:
        json.dump(data, f, indent=2)

# App UI setup
st.set_page_config(page_title="Smart Ordering", layout="wide")
st.markdown("""
    <style>
    body { background-color: #111; }
    .stButton>button { background-color: #4CAF50; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Smart Ordering")
st.subheader("Browse Menu and Order")

table_number = st.text_input("Enter Table Number", "")

menu_data = load_menu()
categories = sorted(set([item["category"] for item in menu_data]))
selected_category = st.selectbox("Filter by Category", ["All"] + categories)

if "cart" not in st.session_state:
    st.session_state.cart = []

# Show menu without images
st.markdown("### 📋 Menu")
for item in menu_data:
    if selected_category != "All" and item["category"] != selected_category:
        continue
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"**{item['name']}** - ₹{item['price']} ({item['category']})")
        tags = []
        if item.get("veg"): tags.append("🌱 Veg")
        else: tags.append("🍗 Non-Veg")
        if item.get("spicy"): tags.append("🌶️ Spicy")
        if item.get("popular"): tags.append("⭐ Popular")
        st.caption(", ".join(tags))
    with col2:
        if st.button("Add", key=item['id']):
            st.session_state.cart.append({**item, "quantity": 1})
            st.success(f"Added {item['name']}")

# Cart section
st.markdown("## 🛒 Cart")
if st.session_state.cart:
    total = 0
    for item in st.session_state.cart:
        item_total = item["price"] * item["quantity"]
        total += item_total
        st.write(f"- {item['name']} × {item['quantity']} = ₹{item_total}")
    st.markdown(f"**Total: ₹{total}**")
    
    if st.button("✅ Place Order"):
        if not table_number.strip():
            st.warning("Please enter a table number.")
        else:
            order = {
                "id": str(uuid.uuid4()),
                "table": table_number,
                "cart": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().isoformat()
            }
            save_order(order)
            st.session_state.cart = []
            st.success("✅ Order placed successfully!")

# Feedback section
st.markdown("## 💬 Feedback")
feedback_text = st.text_area("Leave your message here")
if st.button("Submit Feedback"):
    if feedback_text.strip():
        save_feedback({
            "table": table_number,
            "message": feedback_text,
            "timestamp": datetime.now().isoformat()
        })
        st.success("Thanks for your feedback!")
    else:
        st.warning("Please type a message first.")

# Order tracking
st.markdown("## 🔄 Order Status")
try:
    with open("orders.json", "r") as f:
        all_orders = json.load(f)
    your_orders = [o for o in all_orders if o["table"] == table_number.strip()]
    if your_orders:
        latest = your_orders[-1]
        st.write(f"🕒 Last Order ID: `{latest['id']}`")
        st.write(f"📋 Status: **{latest['status']}**")
    else:
        st.info("No orders found for this table.")
except:
    st.warning("Order data not available.")
