import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000/analytics/summary"

def analytics_tab():
    st.header("💡 Expense Analytics Dashboard")
    st.markdown("Track your expenses in a visually appealing professional dashboard.")

    # --- Date Filter ---
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 0.5])
        with col1:
            start_date = st.date_input("Start Date", datetime(2024, 8, 1))
        with col2:
            end_date = st.date_input("End Date", datetime(2024, 8, 5))
        with col3:
            st.write("")

    if st.button("Get Analytics"):
        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        try:
            response = requests.post(API_URL, json=payload).json()
        except Exception as e:
            st.error(f"Failed to fetch analytics: {e}")
            return

        if "detail" in response:
            st.error(f"Backend error: {response['detail']}")
            return

        # --- Prepare DataFrame ---
        data = {
            "Category": list(response.keys()),
            "Total": [response[cat]["total"] for cat in response],
            "Percentage": [response[cat]["percentage"] for cat in response]
        }
        df = pd.DataFrame(data).sort_values(by="Percentage", ascending=False)

        # --- Total Expense Card ---
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            total_expense = df["Total"].sum()
            st.metric(label="💰 Total Expense", value=f"${total_expense:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        # --- Pie Chart ---
        st.subheader("📌 Expense Distribution by Category")
        fig = px.pie(df, names='Category', values='Total',
                     color_discrete_sequence=px.colors.qualitative.Prism,
                     hole=0.4)
        fig.update_traces(textinfo='percent+label', hoverinfo='label+value')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)

        # --- Bar Chart ---
        st.subheader("📊 Percentage Breakdown by Category")
        fig2 = px.bar(df, x='Category', y='Percentage',
                      text=df['Percentage'].map(lambda x: f"{x:.2f}%"),
                      color='Percentage', color_continuous_scale=px.colors.sequential.Teal)
        fig2.update_layout(yaxis_title="Percentage", xaxis_title="Category",
                           paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(color='white'))
        st.plotly_chart(fig2, use_container_width=True)

        # --- Detailed Table ---
        st.subheader("📝 Detailed Expense Table")
        df_display = df.copy()
        df_display["Total"] = df_display["Total"].map("${:,.2f}".format)
        df_display["Percentage"] = df_display["Percentage"].map("{:.2f}%".format)
        st.dataframe(df_display.reset_index(drop=True), use_container_width=True)
