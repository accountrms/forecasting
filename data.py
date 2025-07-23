import streamlit as st
import pandas as pd
from datetime import date, timedelta
import numpy as np

# Function to load main data from CSV
@st.cache_data
def load_main_data():
    try:
        data = pd.read_csv("files/spare_items_master_file_truncated.csv")
        if 'Material No' in data.columns:
            data['Material No'] = data['Material No'].astype(str)
        return data
    except Exception as e:
        st.error(f"Error loading main file: {e}")
        return None
    
# Function to load additional data from different CSV
@st.cache_data
def load_additional_data(material_id):
    try:
        additional_data = pd.read_csv("files/forecasted.csv")  # Replace with your actual filename
        if 'Material No' in additional_data.columns:
            additional_data['Material No'] = additional_data['Material No'].astype(str)
        return additional_data[additional_data['Material No'] == material_id]
    except Exception as e:
        st.warning(f"Could not load additional details for material {material_id}: {e}")
        return None
    
# Function to load leadtime from different CSV
@st.cache_data
def load_leadtime_data(material_id):
    try:
        leadtime_data = pd.read_csv("files/leadtime.csv")  # Replace with your actual filename
        if 'Material No' in leadtime_data.columns:
            leadtime_data['Material No'] = leadtime_data['Material No'].astype(str)
        return leadtime_data[leadtime_data['Material No'] == material_id]
    except Exception as e:
        st.warning(f"Could not load leadtime details for material {material_id}: {e}")
        return None
    
# Function to load stock data from CSV
@st.cache_data
def load_stock_value(filepath):
    try:
        # Try reading the CSV with different encodings if needed
        df = pd.read_csv(filepath, encoding='latin1')  # or 'utf-8', 'cp1252'
        
        # Convert to numeric (handling commas, currency symbols, etc.)
        df['ValStckVal'] = pd.to_numeric(
            df['ValStckVal'].astype(str).str.replace('[^\d.]', '', regex=True), 
            errors='coerce'
        )
        
        df['Val.Stock in May 2025'] = pd.to_numeric(
            df['Val.Stock in May 2025'].astype(str).str.replace('[^\d.]', '', regex=True),
            errors='coerce'
        )
        
        # Sum columns, ignoring NaN values
        sum_2024 = df['ValStckVal'].sum(skipna=True)
        sum_2025 = df['Val.Stock in May 2025'].sum(skipna=True)
        
        return sum_2024, sum_2025
        
    except Exception as e:
        st.error(f"Error loading {filepath}: {str(e)}")
        return None, None
    
# Function to load reliability factor from different CSV
@st.cache_data
def load_reliability_data(material_id):
    try:
        reliability_data = pd.read_csv("files/reliability.csv")  # Replace with your actual filename
        if 'Material No' in reliability_data.columns:
            reliability_data['Material No'] = reliability_data['Material No'].astype(str)
        return reliability_data[reliability_data['Material No'] == material_id]
    except Exception as e:
        st.warning(f"Could not load leadtime details for material {material_id}: {e}")
        return None
    
def makedaywiseForecast(df_yearly,mat,oem,end_date=date.today()+timedelta(days=365*5),initial_stock=10):
    daywiseForecast = pd.DataFrame(columns=['Material No','Desc','leadtime','date','daily_cons','Regular_req', 'One-off_req','anticipated_consum','buffer_stock','on_order_stock','present_stock','stock_after'])
    df=df_yearly.copy()
    df=df[(df['Material No']==mat)&(df['oem']==oem)].reset_index(drop=True)
    consider_pre_order = False
    start_date = date.today()
    days = (end_date-start_date).days
    initial_stock = df.at[0,'forecasted_consum']*2
    daywiseForecast.at[0,'present_stock'] = initial_stock if df.at[0,'buffer_stock'] < initial_stock else df.at[0,'buffer_stock']*1.4
    daywiseForecast.at[0,'stock_after']=daywiseForecast.at[0,'present_stock']
    reorder_point=end_date+timedelta(days=2)
    reorder_index,present_stock_correction=days-1,0
    reorder_qty,updated_reorder_qty=0,0
    first_reorder=False
    leadtime = df['leadtime'].iloc[0]
    arrival={}
    for i in range(days):
        daywiseForecast.at[i,'date']=start_date+timedelta(days=i)
        daywiseForecast.at[i,'anticipated_consum']=df.loc[df['year']==date.today().year,'anticipated_consum'].iloc[0]
        daywiseForecast.at[i,'Regular_req']=df.loc[df['year']==date.today().year,'Regular_req'].iloc[0]
        daywiseForecast.at[i,'One-off_req']=df.loc[df['year']==date.today().year,'One-off_req'].iloc[0]
        daywiseForecast.at[i,'buffer_stock']=df.loc[df['year']==date.today().year,'buffer_stock'].iloc[0]
        daywiseForecast.at[i,'daily_cons']=df.loc[df['year']==date.today().year,'forecasted_consum'].iloc[0]/365
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
                    reorder_index=i
                    first_reorder = True
                    current_year=daywiseForecast.at[i,'date'].year
                    reorder_qty = daywiseForecast.at[i,'One-off_req']+ daywiseForecast.at[i,'Regular_req'] + daywiseForecast.at[i,'anticipated_consum'] +  daywiseForecast.at[i,'buffer_stock'] - daywiseForecast.at[i, 'present_stock']
                    arrival[i+leadtime]=reorder_qty
    daywiseForecast['Material No']=mat
    daywiseForecast['Desc']=df.at[0,'Desc']
    daywiseForecast['leadtime']=df['leadtime'].iloc[0]
    date_for_stock_check = reorder_point+timedelta(days=(365+int(leadtime)))
    if date_for_stock_check < end_date:
        if daywiseForecast[daywiseForecast['date']==date_for_stock_check]['present_stock'].iloc[0] == 0:
            consider_pre_order = True
            present_stock_correction = daywiseForecast[daywiseForecast['date'].between(date.today(),reorder_point)]['daily_cons'].values.sum()
            updated_reorder_qty = reorder_qty - present_stock_correction
    result = {'reorder_point':reorder_point,
              'reorder_qty': np.ceil(reorder_qty),
              'updated_reorder_qty':np.ceil(updated_reorder_qty),
              'consider_pre_order':consider_pre_order,
              'One-off_req':np.ceil(daywiseForecast.at[reorder_index,'One-off_req']),
              'Regular_req':np.ceil(daywiseForecast.at[reorder_index,'Regular_req']),
              'anticipated_consum':np.ceil(daywiseForecast.at[reorder_index,'anticipated_consum']),
              'buffer_stock':np.ceil(daywiseForecast.at[reorder_index,'buffer_stock']),
              'present_stock':np.ceil(daywiseForecast.at[reorder_index, 'present_stock']+present_stock_correction),
              'leadtime': leadtime
             }
    return daywiseForecast.reset_index(drop=True), result