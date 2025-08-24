# tracking.py
import streamlit as st
import pandas as pd

def tracking_page():
    st.title("Request Tracking")
    st.markdown("Track the status of your material purchase requests")
    
    # Display the tracking table
    df = pd.read_csv('tracking.csv')
    
    # Reorder columns to have status information together
    columns_order = ["Request ID", "Manufacturer", "Current Status"] + [
        "Requested", "Approved", "PO Issued", "Delivered", "Completed"
    ]
    
    df = df[columns_order]
    
    # Display the main table
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Add some visual indicators - FIXED VERSION
    st.markdown("### Status Legend")
    cols = st.columns(6)
    status_legends = [
        ("🟦", "Requested", "Purchase request submitted"),
        ("🟪", "Approved", "Request approved by manager"),
        ("🟨", "PO Issued", "Purchase order issued to Manufacturer"),
        ("🟩", "Delivered", "Materials delivered to site"),
        ("✅", "Completed", "Process completed")
    ]
    
    for i, (icon, status, help_text) in enumerate(status_legends):
        cols[i].markdown(f"{icon} **{status}**  \n{help_text}")