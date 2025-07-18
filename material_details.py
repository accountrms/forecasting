import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from data import load_main_data
from data import load_additional_data
from data import load_leadtime_data

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

        def makedaywiseForecast(df_yearly, mat, oem, end_date=date.today()+timedelta(days=365*5), initial_stock=10):
            daywiseForecast = pd.DataFrame(columns=['Material No','Desc','leadtime','date','daily_cons','anticipated_consum','buffer_stock','present_stock','stock_after'])
            df = df_yearly.copy()
            df = df[(df['Material No']==mat) & (df['oem']==oem)].reset_index(drop=True)
            
            start_date = date.today()
            days = (end_date-start_date).days
            daywiseForecast.at[0,'present_stock'] = initial_stock if df.at[0,'buffer_stock'] < initial_stock else df.at[0,'buffer_stock']*1.2
            daywiseForecast.at[0,'stock_after'] = daywiseForecast.at[0,'present_stock']
            
            reorder_point = 0
            reorder_qty = 0
            first_reorder = False
            leadtime = int(df['leadtime'].iloc[0])  # Convert to Python int
            arrival = {}
            
            for i in range(days):
                daywiseForecast.at[i,'date'] = start_date + timedelta(days=i)
                daywiseForecast.at[i,'anticipated_consum'] = df.loc[df['year']==date.today().year,'cons_woip'].iloc[0]*leadtime/365
                daywiseForecast.at[i,'buffer_stock'] = df.loc[df['year']==date.today().year,'buffer_stock'].iloc[0]
                daywiseForecast.at[i,'daily_cons'] = df.loc[df['year']==date.today().year,'cons_wip'].iloc[0]/365
                
                if i > 0:
                    if i in arrival.keys():
                        arrived_qty = arrival[i]
                    else:
                        arrived_qty = 0
                        
                    daywiseForecast.at[i,'present_stock'] = max(daywiseForecast.at[i-1,'present_stock'] - daywiseForecast.at[i-1,'daily_cons'], 0)
                    daywiseForecast.at[i,'stock_after'] = max(daywiseForecast.at[i-1,'stock_after'] - daywiseForecast.at[i-1,'daily_cons'], 0) + arrived_qty
                    
                    if not first_reorder:
                        if daywiseForecast.at[i,'present_stock'] < daywiseForecast.at[i,'buffer_stock']:
                            reorder_point = daywiseForecast.at[i,'date']
                            first_reorder = True
                            current_year = daywiseForecast.at[i,'date'].year
                            reorder_qty = df.loc[df['year']==date.today().year,'cons_wip'].iloc[0] + daywiseForecast.at[i,'anticipated_consum'] + daywiseForecast.at[i,'buffer_stock'] - daywiseForecast.at[i, 'present_stock']
                            arrival[i+leadtime] = reorder_qty
            
            daywiseForecast['Material No'] = mat
            daywiseForecast['Desc'] = df.at[0,'Desc']
            daywiseForecast['leadtime'] = leadtime
            
            return daywiseForecast, reorder_point, reorder_qty, leadtime

        def plot_req2(dff, tagw, mat, ro_p, leadtime):
            result = dff.copy()
            fig, ax = plt.subplots(figsize=(12, 4))
            
            for t in tagw:
                t1 = result[t].to_list()
                y1 = result['date'].to_list()
                ax.plot(y1, t1, label=t, marker='o', linestyle='-')
            
            ax.axvline(x=ro_p, color='red', linestyle='--', label=f"reorder point at {ro_p.strftime('%d-%m-%Y')}")
            ax.axvline(x=ro_p+timedelta(days=int(leadtime)), color='red', linestyle='--', label=f"delivery point at {(ro_p+timedelta(days=int(leadtime))).strftime('%d-%m-%Y')}")
            ax.hlines(50, ro_p, ro_p+timedelta(days=int(leadtime)), colors='k', linestyles='--', label='leadtime')
            
            ax.set_xticks(y1)
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in y1], rotation=45)
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
            ax.legend()
            ax.set_title(f"Forecast - {mat}")
            plt.tight_layout()
            
            return fig


        st.subheader("Inventory Forecast Dashboard")

        # User inputs
        # oem = st.text_input("OEM", "atlas")
        # initial_stock = st.number_input("Initial Stock", value=10)
        oem = "atlas"
        initial_stock = 10

        # Run forecast
        try:
            df, reorder_point, reorder_qty, leadtime = makedaywiseForecast(forecasted, material_id, oem, initial_stock=initial_stock)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Reorder Point", reorder_point.strftime('%Y-%m-%d'))
            col2.metric("Reorder Quantity", round(reorder_qty, 1))
            col3.metric("Lead Time", f"{leadtime} days")
            
            # Plot
            fig = plot_req2(df, ['buffer_stock', 'stock_after', 'present_stock'], material_id, reorder_point, leadtime)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

        st.divider()
        
        # Show raw data in an expandable section
        with st.expander("View Raw Data"):
            st.dataframe(additional_data, hide_index=True)

        with st.expander("View Leadtime Data"):
            st.dataframe(leadtime_data, hide_index=True)
            
    else:
        st.warning("No additional forecast data available for this material")
    
    st.divider()
    if st.button("Back to Search"):
        st.session_state.show_details = False
        st.session_state.current_page = "Material Search"
        st.rerun()