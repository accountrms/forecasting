import streamlit as st
import pandas as pd
from prepr_process import prepr_process_page

def notification_page():
    # Check if we should show dashboard instead
    if st.session_state.get('show_dashboard'):
        # Add a back button in the dashboard
        if st.button("← Back to Notifications"):
            # Reset the dashboard state
            st.session_state['show_dashboard'] = False
            st.session_state['selected_material_no'] = None
            st.session_state['data_loaded'] = False
            st.rerun()
        # Pass the selected material number to the prepr_process_page
        prepr_process_page(st.session_state.get('selected_material_no'))
        return  # This exits the function early, showing only the dashboard

    st.subheader("📝 Notifications")

    # Sample data
    stock_data = pd.DataFrame({
        "Date": ["20-07-2025 00:23", "21-07-2025 10:15", "22-07-2025 14:30"],
        "Material No": ["220003196", "220026696", "220003198"],
        "Present Stock": [30, 80, 55],
        "Safety Stock": [39, 100, 50]
    })

    # Iterate through notifications
    for index, notification in stock_data.iterrows():
        if notification['Present Stock'] < notification['Safety Stock']:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.error(f"⚠️ [{notification['Date']}] Stock below Safety level - **Material No:** {notification['Material No']}")
            with col2:
                if st.button("Create Requisition", key=f"btn_{notification['Material No']}"):
                    # Store the selected material number and show dashboard
                    st.session_state['selected_material_no'] = notification['Material No']
                    st.session_state['show_dashboard'] = True
                    st.rerun()