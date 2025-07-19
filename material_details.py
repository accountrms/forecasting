import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from data import load_additional_data, load_leadtime_data
from datetime import date, timedelta, datetime

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
    st.subheader("Forecast Data (in days)")
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
        
        st.divider()
        
        # Prepare data for plotting
        additional_data['year'] = additional_data['year'].astype(int)
        additional_data = additional_data.sort_values('year')

        additional_data=additional_data[['year','cons_wip', 'buffer_stock','net_req','present_stock']]
        # Create the plot
        st.subheader("Inventory Trends Over Time (Plotly Express)")

        # To plot multiple lines easily with Plotly Express, it's often best to "melt" your DataFrame
        # into a "long" format. This stacks your 'cons_wip', 'buffer_stock', etc., into a single 'Quantity' column
        # with a new 'Metric' column to distinguish them.
        df_long = additional_data.melt(id_vars=['year'],
                                       var_name='Metric',
                                       value_name='Quantity')

        fig = px.line(df_long,
                      x='year',
                      y='Quantity',
                      color='Metric',  # This tells Plotly to draw a separate line for each 'Metric'
                      markers=True,  # Show markers at each data point
                      labels={'year': 'Year', 'Quantity': 'Quantity'})  # Customize axis labels

        # Enhance interactivity with hover templates or unified hovers
        fig.update_layout(hovermode="x unified")  # Shows all series values when hovering over a specific year

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)  # use_container_width makes it fill the Streamlit column

        st.divider()

        # Load data
        @st.cache_data
        def load_data():
            return pd.read_csv('files/forecasted.csv')

        forecasted = load_data()
        forecasted['Material No'] = forecasted['Material No'].astype(str)

        def makedaywiseForecast(df_yearly,mat,oem,end_date=date.today()+timedelta(days=365*5),initial_stock=10):
            daywiseForecast = pd.DataFrame(columns=['Material No','Desc','leadtime','date','daily_cons','anticipated_consum','buffer_stock','present_stock','stock_after'])
            df=df_yearly.copy()
            df=df[(df['Material No']==mat)&(df['oem']==oem)].reset_index(drop=True)
            consider_pre_order = False
            start_date = date.today()
            days = (end_date-start_date).days
            initial_stock = df.at[0,'cons_wip']*2
            daywiseForecast.at[0,'present_stock'] = initial_stock if df.at[0,'buffer_stock'] < initial_stock else df.at[0,'buffer_stock']*1.2
            daywiseForecast.at[0,'stock_after']=daywiseForecast.at[0,'present_stock']
            reorder_point=end_date+timedelta(days=2)
            reorder_qty,updated_reorder_qty=0,0
            first_reorder=False
            leadtime = df['leadtime'].iloc[0]
            arrival={}
            for i in range(days):
                daywiseForecast.at[i,'date']=start_date+timedelta(days=i)
                daywiseForecast.at[i,'anticipated_consum']=df.loc[df['year']==date.today().year,'cons_woip'].iloc[0]*leadtime/365
                daywiseForecast.at[i,'buffer_stock']=df.loc[df['year']==date.today().year,'buffer_stock'].iloc[0]
                daywiseForecast.at[i,'daily_cons']=df.loc[df['year']==date.today().year,'cons_wip'].iloc[0]/365
                if i>0:
                    if i in arrival.keys():
                        arrived_qty = arrival[i]
                    else:
                        arrived_qty=0
                    daywiseForecast.at[i,'present_stock']=max(daywiseForecast.at[i-1,'present_stock']-daywiseForecast.at[i-1,'daily_cons'],0)
                    daywiseForecast.at[i,'stock_after']=max(daywiseForecast.at[i-1,'stock_after']-daywiseForecast.at[i-1,'daily_cons'],0)+arrived_qty
                    if not first_reorder:
                        if daywiseForecast.at[i,'present_stock']< daywiseForecast.at[i,'buffer_stock']:
                            reorder_point = daywiseForecast.at[i,'date']
                            first_reorder = True
                            current_year=daywiseForecast.at[i,'date'].year
                            reorder_qty = df.loc[df['year']==date.today().year,'cons_wip'].iloc[0] + daywiseForecast.at[i,'anticipated_consum'] +  daywiseForecast.at[i,'buffer_stock'] - daywiseForecast.at[i, 'present_stock']
                            arrival[i+leadtime]=reorder_qty
            daywiseForecast['Material No']=mat
            daywiseForecast['Desc']=df.at[0,'Desc']
            daywiseForecast['leadtime']=df['leadtime'].iloc[0]
            date_for_stock_check = reorder_point+timedelta(days=(365+int(leadtime)))
            if date_for_stock_check < end_date:
                if daywiseForecast[daywiseForecast['date']==date_for_stock_check]['present_stock'].iloc[0] == 0:
                    consider_pre_order = True
                    updated_period = daywiseForecast[daywiseForecast['date'].between(date.today(),reorder_point)]
                    updated_reorder_qty = reorder_qty - updated_period['daily_cons'].values.sum()
            return daywiseForecast.reset_index(drop=True),{
                'reorder_point':reorder_point,
                'reorder_qty': np.ceil(reorder_qty),
                'updated_reorder_qty':np.ceil(updated_reorder_qty),
                'consider_pre_order':consider_pre_order,
                'leadtime':leadtime
            }

        st.subheader("Inventory Forecast Dashboard")

        # User inputs
        # oem = st.text_input("OEM", "atlas")
        # initial_stock = st.number_input("Initial Stock", value=10)
        oem = "atlas"
        initial_stock = 10

        # Run forecast
        try:
            ordering_required = {}
            ordering_required[material_id]={}
            df, ordering_required[material_id] = makedaywiseForecast(forecasted, material_id, 'atlas')
            leadtime = ordering_required[material_id]['leadtime']
            reorder_point = ordering_required[material_id]['reorder_point']
            delivery_date = reorder_point + pd.DateOffset(days=leadtime)  # Proper date addition
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Reorder Point", reorder_point.strftime('%Y-%m-%d'))
            col2.metric("Reorder Quantity", ordering_required[material_id]['reorder_qty'])
            col3.metric("Delivery Date", delivery_date.strftime('%Y-%m-%d'))
            col4.metric("Present Stock", additional_data['present_stock'].iloc[0])
            col5.metric("Safety Stock", additional_data['buffer_stock'].iloc[0])

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
        
        # Show raw data in an expandable section
        with st.expander("View Raw Data"):
            st.dataframe(df, hide_index=True)
            
    else:
        st.warning("No additional forecast data available for this material")
    
    st.divider()
    if st.button("Back to Search"):
        st.session_state.show_details = False
        st.session_state.current_page = "Material Search"
        st.rerun()