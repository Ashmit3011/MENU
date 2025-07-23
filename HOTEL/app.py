import streamlit as st
import json
import os
from datetime import datetime

ORDERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.json")

st.subheader("🛒 Your Cart")

if "cart" not in st.session_state:
    st.session_state.cart = {}

if st.session_state.cart:
    total = 0
    for name, item in list(st.session_state.cart.items()):
        price = item["price"]
        qty = item["quantity"]
        subtotal = price * qty
        total += subtotal

        # Unique key for the button
        btn_key = f"dec_{name}"

        # Display item in card-style layout (dark theme)
        st.markdown(f"""
            <div style="
                background-color: #2c2c2c;
                padding: 0.8rem;
                margin-bottom: 0.6rem;
                border-radius: 10px;
                border: 1px solid #444;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #f1f1f1;
            ">
                <div style="flex: 2;">
                    <b>🍽️ {name}</b><br>
                    <span style="font-size: 0.85rem; color: #bbb;">Price: ₹{price} × {qty}</span>
                </div>
                <div style="flex: 1; text-align: center;">
                    <b>₹{subtotal}</b>
                </div>
                <div style="flex: 1; text-align: right;">
                    <form action="#" method="post">
                        <button name="{btn_key}" style="
                            background-color: #dc3545;
                            color: white;
                            border: none;
                            padding: 0.3rem 0.6rem;
                            font-size: 0.8rem;
                            border-radius: 6px;
                            cursor: pointer;
                        ">➖</button>
                    </form>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Decrease quantity detection
        if st.session_state.get(btn_key):
            st.session_state.cart[name]["quantity"] -= 1
            if st.session_state.cart[name]["quantity"] <= 0:
                del st.session_state.cart[name]
            st.rerun()

    # Total section (dark theme, left-aligned)
    st.markdown(f"""
        <div style="
            margin-top: 1.5rem;
            padding: 0.5rem 1rem;
            text-align: left;
            background-color: #1e1e1e;
            border-radius: 8px;
            border: 1px solid #444;
            color: #f1f1f1;
            font-size: 1.2rem;
            width: fit-content;
        ">
            <b>🧾 Total: ₹{total}</b>
        </div>
    """, unsafe_allow_html=True)

    # Place Order button (centered)
    col = st.columns([2, 1, 2])[1]
    with col:
        if st.button("✅ Place Order"):
            if os.path.exists(ORDERS_FILE):
                with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                    orders = json.load(f)
            else:
                orders = []

            # Remove previous order of same table
            orders = [o for o in orders if o["table"] != st.session_state.table_number]

            new_order = {
                "table": st.session_state.table_number,
                "items": st.session_state.cart,
                "status": "pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders.append(new_order)

            with open(ORDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(orders, f, indent=2)

            st.success("✅ Order Placed!")
            del st.session_state.cart
            st.rerun()
else:
    st.info("🛍️ Your cart is empty.")