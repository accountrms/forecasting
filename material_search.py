import streamlit as st
from data import load_main_data
from material_details import show_material_details

# Material Search Page (unchanged from your original)
def material_search_page():
    if 'show_details' not in st.session_state:
        st.session_state.show_details = False
    if 'selected_material' not in st.session_state:
        st.session_state.selected_material = None

    if st.session_state.show_details and st.session_state.selected_material:
        data = load_main_data()
        if data is not None:
            show_material_details(st.session_state.selected_material, data)
        return

    st.title("🏭 Demand Forecast")
    
    data = load_main_data()
    
    if data is not None:
        st.success("Data loaded successfully!")
        
        if st.checkbox("Show raw data"):
            st.write(data)
        
        st.divider()
        st.subheader("Search Materials")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Manufacturer Name' in data.columns:
                manufacturers = ['All'] + sorted(data['Manufacturer Name'].dropna().unique().tolist())
                selected_manf = st.selectbox("Filter by Manufacturer", manufacturers)
        
        with col2:
            if 'Plant Code' in data.columns:
                plants = ['All'] + sorted(data['Plant Code'].dropna().unique().tolist())
                selected_plant = st.selectbox("Filter by Plant Code", plants)
            
            if 'Material Type' in data.columns:
                material_types = ['All'] + sorted(data['Material Type'].dropna().unique().tolist())
                selected_type = st.selectbox("Filter by Material Type", material_types)

        with col3:
            search_term = st.text_input("Search by Material No")
        
        filtered_data = data.copy()
        
        if search_term:
            if 'Material No' in filtered_data.columns:
                filtered_data = filtered_data[
                    filtered_data['Material No'].astype(str).str.contains(search_term, case=False, na=False)
                ]
        
        if 'Manufacturer Name' in data.columns and selected_manf != 'All':
            filtered_data = filtered_data[filtered_data['Manufacturer Name'] == selected_manf]

        if 'Plant Code' in data.columns and selected_plant != 'All':
            filtered_data = filtered_data[filtered_data['Plant Code'] == selected_plant]
        
        if 'Material Type' in data.columns and selected_type != 'All':
            filtered_data = filtered_data[filtered_data['Material Type'] == selected_type]
        
        st.write(f"Found {len(filtered_data)} materials (showing first 100)")
        
        if not filtered_data.empty:
            for _, row in filtered_data.head(100).iterrows():
                with st.expander(f"{row['Material No']} - {row.get('Description', '')} - MPN {row.get('Mfr Part No', '')}"):
                    cols = st.columns(2)
                    for i, (key, value) in enumerate(row.items()):
                        cols[i%2].write(f"**{key}:** {value}")
                    
                    if st.button(f"View Details for {row['Material No']}", key=f"btn_{row['Material No']}"):
                        st.session_state.selected_material = row['Material No']
                        st.session_state.show_details = True
                        st.rerun()
            
        else:
            st.warning("No materials match your search criteria")