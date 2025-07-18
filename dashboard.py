import streamlit as st
from data import load_stock_value
import pandas as pd
import plotly.express as px

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
    
    stock_2024, stock_2025 = load_stock_value("files/stock_value_2024.csv")
    
    if stock_2024 is not None and stock_2025 is not None:

        # Create two columns
        col1, col2 = st.columns(2)

        # First column content
        with col1:
            st.subheader("Total Stock Value 2025")
            st.header(f"₹ {format_indian_units(stock_2025)}")

        # Second column content
        with col2:
            st.subheader('Inventory Present Trend')
            
            # Create dataframe
            data = {'Year': [2023, 2024, 2025],
                    'Amount (crore)': [50, 60, 110.73]}
            df = pd.DataFrame(data)

            # Calculate percentage increase (2024 to 2025)
            prev_amount = df.loc[df['Year'] == 2024, 'Amount (crore)'].values[0]
            current_amount = df.loc[df['Year'] == 2025, 'Amount (crore)'].values[0]
            percentage_increase = ((current_amount - prev_amount) / prev_amount) * 100

            # Display the trend metric
            st.metric(
                label="2024 → 2025",
                value=f"{percentage_increase:.1f}% increase",
            )

        # Create plot
        fig = px.line(df, x='Year', y='Amount (crore)', 
                    title='Amount Growth Over Years',
                    markers=True,
                    text='Amount (crore)')

        # Customize plot
        fig.update_traces(textposition='top center')
        fig.update_layout(
            yaxis_title='Amount (in crores)',
            xaxis=dict(tickmode='linear', dtick=1),
            hovermode='x unified'
        )

        # Display plot in Streamlit
        st.plotly_chart(fig)