import streamlit as st
from data import load_stock_value
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def format_indian_units(number):

    if pd.isna(number):  # Handle NaN/None safely
        return "N/A"
    
    number = float(number)
    crore = number / 10000000
    lakh = number / 100000
    
    if crore >= 1:
        return f"{crore:.0f} crore" if crore.is_integer() else f"{crore:.2f} crore"
    elif lakh >= 1:
        return f"{lakh:.0f} lakh" if lakh.is_integer() else f"{lakh:.2f} lakh"
    else:
        return f"{number:,.0f}"  # Default formatting for small numbers

# Dashboard Page (unchanged from your original)
def dashboard_page():
    st.title("📊 Dashboard")

    st.title("Plant Inventory Monitoring")

    k1, k2, k3, k4 = st.columns([2, 1, 1, 1])
    with k1:
        st.subheader("Total Purchase Done (Quarter-wise)")
        x = ['Q1 FY25-26', 'Q4 FY24-25', 'Q3 FY24-25', 'Q2 FY24-25', 'Q1 FY24-25', 'Q4 FY23-24',
             'Q3 FY23-24', 'Q2 FY23-24', 'Q1 FY23-24']
        y = [7681630.84, 12968215.3, 32258856.39, 17267796.14, 25834122.68, 104923920.5, 90889918.55, 44488211.24,
             27807649.7]
        fig_q = go.Figure(data=[go.Bar(x=x, y=y)])
        fig_q.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=300, xaxis_title='Quarter',
                            yaxis_title='Inventory')
        st.plotly_chart(fig_q, use_container_width=True)

    with k2:
        from data import load_stock_value
        stock_2024, stock_2025 = load_stock_value("files/stock_value_2024.csv")
        st.metric("Present Inventory Value", f"  \n  ₹ {format_indian_units(stock_2025)}")
        percentage_increase = ((stock_2025 - stock_2024) / stock_2024) * 100

        # Display the trend metric
        st.metric(
            label="",
            value=f"{percentage_increase:.1f}% increase",
            delta="2024 → 2025",
            delta_color="inverse"
        )

    with k3:
        st.metric("Present No. of PRs In Process", 9)

    with k4:
        st.metric("Present Stockout Ratio", 5.5)

    # ---------------------- Middle: Trends and breakdowns ----------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Present Inventory Trend")
        fig_inv = go.Figure(data=go.Scatter(x=[2023, 2024, 2025], y=[50, 60, 110.73], mode='lines+markers'))
        fig_inv.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_inv, use_container_width=True)

    with c2:
        st.subheader("Stockout Trend")
        fig_so = go.Figure(data=go.Scatter(x=[2023, 2024, 2025], y=[4.8, 4.5, 5.5], mode='lines+markers'))
        fig_so.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_so, use_container_width=True)

    with c3:
        non_moving = 242
        slow_moving = 97
        st.subheader("Non-moving and Slow-moving Items")
        st.metric("Non-moving items", int(non_moving))
        st.metric("Slow-moving items", int(slow_moving))
        # small pie
        fig_p = go.Figure(data=[go.Pie(labels=['Non-moving', 'Slow-moving'], values=[non_moving, slow_moving])])
        fig_p.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
        st.plotly_chart(fig_p, use_container_width=True)