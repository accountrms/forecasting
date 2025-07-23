import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from data import load_additional_data, load_leadtime_data, load_reliability_data, makedaywiseForecast
from datetime import datetime
import csv

# Function to display material details with the new requirements
def show_material_details(material_id, main_data):
    material_data = main_data[main_data['Material No'] == material_id].iloc[0]

    st.subheader(f"Material Details: {material_id} - {material_data.iloc[1]}")
    st.divider()
    
    # Display main data
    st.subheader("Basic Information")
    
    cols = st.columns(2)
    for i, (key, value) in enumerate(material_data.items()):
        cols[i%2].write(f"**{key}:** {value}")
    
    st.divider()
    
    # Display additional data
    st.subheader("Inventory Forecast Dashboard")
    additional_data = load_additional_data(material_id)
    leadtime_data = load_leadtime_data(material_id)
    
    if additional_data is not None and leadtime_data is not None and not additional_data.empty and not leadtime_data.empty:

        prpo_forecasted = leadtime_data["prpo_forecasted"]
        pogr_forecasted = leadtime_data["pogr_forecasted"]
        grgi_forecasted = leadtime_data["grgi_forecasted"]
        total_leadtime = prpo_forecasted + pogr_forecasted + grgi_forecasted
        
        # Display lead time information
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("File Processing Time (PR to PO)", prpo_forecasted)
        col2.metric("Manufacturer's Leadtime (PO to GR)", pogr_forecasted)
        col3.metric("Logistics Delay", grgi_forecasted)
        col4.metric("Total Leadtime", total_leadtime)

        # Load data
        @st.cache_data
        def load_data():
            return pd.read_csv('files/forecasted.csv')

        forecasted = load_data()
        forecasted['Material No'] = forecasted['Material No'].astype(str)

        # User inputs
        oem = "atlas"

        # Run forecast
        try:
            df, result = makedaywiseForecast(forecasted, material_id, 'atlas')
            df = df.fillna(0)
            leadtime = result['leadtime']
            reorder_point = result['reorder_point']
            delivery_date = reorder_point + pd.DateOffset(days=leadtime)
            present_stock = result["present_stock"]
            safety_stock = result["buffer_stock"]
            one_off_requirement = result["One-off_req"]
            regular_requirement = result["Regular_req"]
            overhaul_quantity = 0
            anticipated_qty = result["anticipated_consum"]
            plant_stock = 0
            on_order_stock = df.iloc[0]["on_order_stock"]
            in_process_stock = 0
            net_requirement = result["reorder_qty"]

            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Reorder Point", reorder_point.strftime('%d/%m/%y'))
            col2.metric("Reorder Quantity", result['reorder_qty'])
            col3.metric("Delivery Date", delivery_date.strftime('%d/%m/%y'))
            col4.metric("Present Stock", present_stock)
            col5.metric("Safety Stock", safety_stock)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("One off requirement", one_off_requirement)
            col2.metric("Regular requirement", regular_requirement)
            col3.metric("Overhaul quantity", overhaul_quantity)
            col4.metric("Anticipated Quantity", anticipated_qty)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Plant Stock", plant_stock)
            col2.metric("On order Stock", on_order_stock)
            col3.metric("In process Stock", in_process_stock)
            col4.metric("Net Rquirement", net_requirement)


            # Plot
            df['date'] = pd.to_datetime(df['date'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['buffer_stock'],
                mode='lines',
                name='Buffer Stock',
                line=dict(color='red', dash='dash'),
                hoverinfo='y+name'
            ))

            # Present stock (only before delivery)
            present_before_delivery = df[df['date'] < delivery_date]
            fig.add_trace(go.Scatter(
                x=present_before_delivery['date'],
                y=present_before_delivery['present_stock'],
                mode='lines',
                name='Present Stock',
                line=dict(color='orange'),
                hoverinfo='y+name'
            ))

            # Stock after replenishment
            stock_after = df[df['date'] >= delivery_date]
            fig.add_trace(go.Scatter(
                x=stock_after['date'],
                y=stock_after['stock_after'],
                mode='lines',
                name='Stock After Replenishment',
                line=dict(color='green'),
                hoverinfo='y+name'
            ))

            # Customize layout
            fig.update_layout(
                title="Inventory Level",
                xaxis_title="Date",
                yaxis_title="Stock Level",
                hovermode="x unified",
                height=600,
                showlegend=True
            )

            # Display the plot
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        st.divider()

        # Calculating Reliabilty woth Population Input
        reliability_data = load_reliability_data(material_id) 
        st.subheader("Reliability Dashboard")
        population = st.number_input("Total Population (N)")
        reliability_factor = reliability_data["Reliability_365days"].iloc[0]
        reliability_forcasted_qty = round((1-reliability_factor)*population, 2)
        col1, col2 = st.columns(2)
        col1.metric("Reliability Factor (RF)", round(reliability_factor,4))
        col2.metric("Reliability Forecasted Quantity ((1-RF)*N)",reliability_forcasted_qty)


        st.divider()

        present_stock_sim = st.number_input("Present Stock")
        if present_stock_sim < safety_stock:
            st.write("User Notified. Check Notification for further action.")

            filename = "files/notification.csv"
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = [current_date, material_id, present_stock, safety_stock]
            
            with open(filename, 'a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(['Date', 'Material ID', 'Present Stock', 'Safety Stock'])
                writer.writerow(data)
            
    else:
        st.warning("No additional forecast data available for this material")
    
    st.divider()
    if st.button("Back to Search"):
        st.session_state.show_details = False
        st.session_state.current_page = "Material Search"
        st.rerun()