import streamlit as st
from datetime import datetime, date
import requests

API_URL = "http://localhost:8000"


def add_update_tab():
    st.markdown("### 📅 Select Date & Log Expenses")
    
    # --- Date Selector Header Card ---
    col_d1, col_d2 = st.columns([2, 1])
    with col_d1:
        selected_date = st.date_input("Expense Date", datetime(2024, 8, 1), key="selected_expense_date")
    with col_d2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📅 Today", use_container_width=True):
            st.session_state.selected_expense_date = date.today()
            st.rerun()

    formatted_date = selected_date.strftime("%Y-%m-%d")

    # GET existing expenses from API
    try:
        response = requests.get(f"{API_URL}/expenses/{formatted_date}", timeout=2.0)
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.error(f"Failed to retrieve expenses (Status Code: {response.status_code})")
            existing_expenses = []
    except Exception as e:
        st.error(f"Unable to connect to backend server: {e}")
        existing_expenses = []

    categories = ["Shopping", "Food", "Rent", "Entertainment", "Transport", "Utilities", "Other"]

    # Calculate existing total for date
    total_existing = sum(float(item.get("amount", 0)) for item in existing_expenses)

    st.markdown(f"""
    <div style="background: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 16px; margin: 16px 0 24px 0; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="color: #94A3B8; font-size: 13px; font-weight: 600;">LOGGED EXPENSES FOR DATE</span>
            <h3 style="color: #F8FAFC; margin: 2px 0 0 0;">{formatted_date}</h3>
        </div>
        <div style="text-align: right;">
            <span style="color: #94A3B8; font-size: 13px; font-weight: 600;">TOTAL AMOUNT</span>
            <h2 style="color: #10B981; margin: 2px 0 0 0;">${total_existing:,.2f}</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Form Container ---
    with st.form(key="expense_form"):
        st.markdown("##### 📝 Expense Line Items")
        
        # Grid Headers
        header_col1, header_col2, header_col3 = st.columns([1.5, 1.5, 2])
        with header_col1:
            st.caption("💵 Amount ($)")
        with header_col2:
            st.caption("🏷️ Category")
        with header_col3:
            st.caption("📌 Notes / Description")

        expenses = []
        for i in range(5):
            if i < len(existing_expenses):
                amount = float(existing_expenses[i].get('amount', 0.0))
                cat_val = existing_expenses[i].get("category", "Shopping")
                category = cat_val if cat_val in categories else "Other"
                notes = existing_expenses[i].get("notes", "")
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            col1, col2, col3 = st.columns([1.5, 1.5, 2])
            with col1:
                amount_input = st.number_input(
                    label=f"Amount {i+1}", 
                    min_value=0.0, 
                    step=10.0, 
                    value=amount, 
                    key=f"amount_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                category_input = st.selectbox(
                    label=f"Category {i+1}", 
                    options=categories, 
                    index=categories.index(category),
                    key=f"category_{i}", 
                    label_visibility="collapsed"
                )
            with col3:
                notes_input = st.text_input(
                    label=f"Notes {i+1}", 
                    value=notes, 
                    key=f"notes_{i}", 
                    placeholder="Optional notes...",
                    label_visibility="collapsed"
                )

            expenses.append({
                'amount': amount_input,
                'category': category_input,
                'notes': notes_input
            })

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("💾 Save & Update Expenses for Date", use_container_width=True)

        if submit_button:
            filtered_expenses = [expense for expense in expenses if expense['amount'] > 0]

            try:
                response = requests.post(f"{API_URL}/expenses/{formatted_date}", json=filtered_expenses)
                if response.status_code == 200:
                    st.success(f"✅ Successfully updated {len(filtered_expenses)} expense entry(ies) for {formatted_date}!")
                    st.rerun()
                else:
                    st.error(f"Failed to update expenses. Server status: {response.status_code}")
            except Exception as e:
                st.error(f"Error connecting to server: {e}")
