import streamlit as st
import pandas as pd

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