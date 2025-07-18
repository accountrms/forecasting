import streamlit as st
from data import load_main_data

# Notification Page (unchanged from your original)
def notification_page():
    st.title("📊 Notifications")
    st.write("User Notifications")
    
    data = load_main_data()
    if data is not None:
        st.subheader("Quick Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Materials", len(data))
        
        if 'Manufacturer Name' in data.columns:
            col2.metric("Unique Manufacturers", data['Manufacturer Name'].nunique())
        
        if 'Plant Code' in data.columns:
            col3.metric("Unique Plants", data['Plant Code'].nunique())