import streamlit as st
import json
import os
from collections import Counter

# ---------------- AUTH SETUP ----------------
USERNAME = "admin"
PASSWORD = "1234"

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

def login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Incorrect credentials")

# ---------------- LOAD/SAVE DATA ----------------
def load_json(file, default=[]):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump(default, f)
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# ---------------- ORDER MANAGEMENT ----------------
def manage_orders():
    st.subheader("📦 Order Management")
    orders = load_json('orders.json')
    status_options = ["Pending", "Preparing", "Ready", "Served"]

    for order in orders:
        with st.expander(f"🧾 Order {order['order_id']} - Table {order['table']} - Status: {order['status']}"):
            st.write("**Items:**")
            for item in order["items"]:
                st.markdown(f"- **{item['name']}** (${item['price']:.2f})")

            new_status = st.selectbox("Update status", status_options,
                                      index=status_options.index(order["status"]),
                                      key=order["order_id"])
            if st.button("Update", key=f"update_{order['order_id']}"):
                order["status"] = new_status
                save_json('orders.json', orders)
                st.toast("✅ Order status updated", icon="📦")
                st.rerun()

# ---------------- MENU MANAGEMENT ----------------
def manage_menu():
    st.subheader("🍽️ Menu Management")
    menu = load_json('menu.json')

    st.write("### Current Menu")
    for item in menu:
        st.markdown(f"- **{item['name']}** (${item['price']:.2f}) — *{item['category']}*")
        if st.button("🗑️ Delete", key=f"delete_{item['id']}"):
            menu.remove(item)
            save_json('menu.json', menu)
            st.toast("🗑️ Item deleted", icon="⚠️")
            st.rerun()

    st.divider()
    st.write("### ➕ Add New Menu Item")
    name = st.text_input("Item Name")
    category = st.text_input("Category")
    price = st.number_input("Price", min_value=0.0, step=0.1)

    if st.button("Add Item"):
        if name and category and price > 0:
            new_item = {
                "id": max([item["id"] for item in menu], default=0) + 1,
                "name": name,
                "category": category,
                "price": price
            }
            menu.append(new_item)
            save_json('menu.json', menu)
            st.toast("✅ Item added to menu", icon="🍽️")
            st.rerun()
        else:
            st.warning("Please fill all fields.")

# ---------------- FEEDBACK ----------------
def view_feedback():
    st.subheader("💬 Customer Feedback")
    feedback = load_json('feedback.json')
    if not feedback:
        st.info("No feedback received yet.")
        return
    for entry in feedback:
        with st.expander(f"🧾 Order {entry['order_id']} - Table {entry['table']}"):
            st.write(f"**Rating:** ⭐ {entry['rating']} / 5")
            st.write(f"**Comment:** {entry['comment']}")

# ---------------- REPORTS ----------------
def sales_reports():
    st.subheader("📊 Sales & Analytics")
    orders = load_json('orders.json')
    total_revenue = sum(sum(item['price'] for item in order['items']) for order in orders)
    st.metric("💰 Total Revenue", f"${total_revenue:.2f}")

    status_counts = Counter(order['status'] for order in orders)
    st.write("### 📦 Order Status Breakdown")
    for status, count in status_counts.items():
        st.write(f"- **{status}**: {count} orders")

    item_counter = Counter()
    for order in orders:
        for item in order['items']:
            item_counter[item['name']] += 1
    top_items = item_counter.most_common(5)
    st.write("### 🥇 Most Popular Items")
    for item, count in top_items:
        st.write(f"- **{item}**: {count} ordered")

# ---------------- MAIN ----------------
if not st.session_state.admin_logged_in:
    login()
else:
    st.title("👨‍💼 Admin Dashboard")
    page = st.sidebar.radio("Navigate", [
        "📦 Orders", "🍽️ Menu", "💬 Feedback", "📊 Reports", "🚪 Logout"
    ])

    if page == "📦 Orders":
        manage_orders()

    elif page == "🍽️ Menu":
        manage_menu()

    elif page == "💬 Feedback":
        view_feedback()

    elif page == "📊 Reports":
        sales_reports()

    elif page == "🚪 Logout":
        st.session_state.admin_logged_in = False
        st.success("Logged out")
        st.rerun()
