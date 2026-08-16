import streamlit as st
import requests
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000/analytics/summary"


def analytics_tab():
    st.markdown("### 💡 Expense Analytics & Insights")
    st.markdown("Analyze spending trends, category distributions, and percentage breakdowns across custom date ranges.")

    # --- Date Range Selector ---
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            start_date = st.date_input("Start Date", datetime(2024, 8, 1), key="analytics_start_date")
        with col2:
            end_date = st.date_input("End Date", datetime(2024, 8, 5), key="analytics_end_date")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_analytics = st.button("⚡ Generate Analytics", use_container_width=True)

    if fetch_analytics or True:  # Auto fetch on load
        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=2.5).json()
        except Exception as e:
            st.error(f"Failed to connect to Analytics API: {e}")
            return

        if "detail" in response:
            st.error(f"Backend error: {response['detail']}")
            return

        if not response:
            st.warning("⚠️ No expense records found for the selected date range. Try logging expenses in the 'Add / Manage Expenses' tab.")
            return

        # --- Prepare DataFrame ---
        data = {
            "Category": list(response.keys()),
            "Total": [response[cat]["total"] for cat in response],
            "Percentage": [response[cat]["percentage"] for cat in response]
        }
        df = pd.DataFrame(data).sort_values(by="Total", ascending=False)

        total_expense = df["Total"].sum()
        top_category = df.iloc[0]["Category"] if not df.empty else "N/A"
        top_cat_amount = df.iloc[0]["Total"] if not df.empty else 0.0
        num_days = max((end_date - start_date).days + 1, 1)
        daily_avg = total_expense / num_days

        st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)

        # --- Key Metric Cards Row ---
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">💰 Total Expense</div>
                <div class="metric-value" style="color: #10B981;">${total_expense:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🏷️ Top Category</div>
                <div class="metric-value" style="color: #38BDF8;">{top_category}</div>
                <div style="font-size: 12px; color: #94A3B8;">${top_cat_amount:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📊 Daily Average</div>
                <div class="metric-value" style="color: #F59E0B;">${daily_avg:,.2f}</div>
                <div style="font-size: 12px; color: #94A3B8;">Over {num_days} Day(s)</div>
            </div>
            """, unsafe_allow_html=True)

        with m_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🔢 Categories Active</div>
                <div class="metric-value" style="color: #A855F7;">{len(df)}</div>
                <div style="font-size: 12px; color: #94A3B8;">Active Categories</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Visual Charts Section ---
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("##### 🍩 Expense Distribution by Category")
            fig = px.pie(
                df, 
                names='Category', 
                values='Total',
                color_discrete_sequence=px.colors.qualitative.Bold,
                hole=0.45
            )
            fig.update_traces(
                textinfo='percent+label', 
                hoverinfo='label+value',
                marker=dict(line=dict(color='#0F172A', width=2))
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8FAFC', family="Plus Jakarta Sans"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            st.markdown("##### 📊 Category Spending Comparison ($)")
            fig2 = px.bar(
                df, 
                x='Category', 
                y='Total',
                text=df['Total'].map(lambda x: f"${x:,.2f}"),
                color='Total', 
                color_continuous_scale=px.colors.sequential.Teal
            )
            fig2.update_traces(
                textposition='outside',
                marker_line_color='#0F172A',
                marker_line_width=1.5
            )
            fig2.update_layout(
                yaxis_title="Total ($)", 
                xaxis_title="Category",
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8FAFC', family="Plus Jakarta Sans"),
                coloraxis_showscale=False,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        # --- Detailed Data Table ---
        st.markdown("##### 📝 Category Breakdown Table")
        df_display = df.copy()
        df_display["Total Amount ($)"] = df_display["Total"].map("${:,.2f}".format)
        df_display["Share (%)"] = df_display["Percentage"].map("{:.2f}%".format)
        df_display = df_display[["Category", "Total Amount ($)", "Share (%)"]]
        
        st.dataframe(df_display.reset_index(drop=True), use_container_width=True)
