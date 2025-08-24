import streamlit as st
import pandas as pd
from data import makedaywiseForecast
from datetime import datetime

def prepr_process_page(material_no=None):
    st.subheader("Material Requisition Process")
    
    if material_no:
        # Initialize session state variables if they don't exist
        if 'override_reasons' not in st.session_state:
            st.session_state.override_reasons = {}
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
            st.session_state.forecasted_data = None
            st.session_state.all_material_nos = None
            st.session_state.oem = None
        if 'show_data' not in st.session_state:
            st.session_state.show_data = False

        # Load data only if not already loaded
        if not st.session_state.data_loaded:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            forecasted_data = pd.read_csv("files/forecasted.csv")
            forecasted_data['Material No'] = forecasted_data['Material No'].astype(str)
            oem = forecasted_data[forecasted_data["Material No"] == material_no].iloc[0]['oem']
            all_material_nos = forecasted_data[forecasted_data["oem"] == oem].drop_duplicates(subset=["Material No"], keep='first')
            st.write(f"Displaying forecast of material codes of Manufacturer related to Material No: {material_no} of OEM {oem}")
            data = {
                "Sl No": [],  # Changed from "Material No" to "Sl No"
                "Material No": [],
                "Description": [],
                "VED": [],
                'One off Requirement (forecasted)': [],
                'One off Requirement (override)': [],
                'Regular Requirement': [],
                'Overhaul Qty': [],
                'Anticipated Qty': [],
                'Plant Stock': [],
                'On order Stock': [],
                'In process Stock': [],
                'Net Requirement (forecasted)': [],
                "Final Requirement (override)": [],
                "Justification for manual override": []
            }

            rows = len(all_material_nos)
            n = 100/rows if rows > 0 else 0
            i = 1
            
            for index, row in all_material_nos.iterrows():
                material_no = row['Material No']
                description = row['Desc']

                df, result = makedaywiseForecast(forecasted_data, material_no, oem)
                df = df.fillna(0)
                one_off_requirement = result["One-off_req"]
                one_off_requirement_override = result["One-off_req"]
                regular_requirement = result["Regular_req"]
                overhaul_quantity = 0
                anticipated_qty = result["anticipated_consum"]
                plant_stock = 0
                on_order_stock = df.iloc[0]["on_order_stock"]
                in_process_stock = 0
                updated_reorder_qty = result['updated_reorder_qty']
                net_requirement = updated_reorder_qty
                final_requirement = updated_reorder_qty
                st.session_state.override_reasons[material_no] = ""

                new_row = {
                    "Sl No": i,  # Adding serial number starting from 1
                    "Material No": material_no,
                    "Description": description,
                    "VED": "",
                    'One off Requirement (forecasted)': one_off_requirement,
                    'One off Requirement (override)': one_off_requirement_override,
                    'Regular Requirement': regular_requirement,
                    'Overhaul Qty': overhaul_quantity,
                    'Anticipated Qty': anticipated_qty,
                    'Plant Stock': plant_stock,
                    'On order Stock': on_order_stock,
                    'In process Stock': in_process_stock,
                    'Net Requirement (forecasted)': net_requirement,
                    "Final Requirement (override)": final_requirement,
                    "Justification for manual override": st.session_state.override_reasons[material_no]
                }

                for key in data:
                    data[key].append(new_row[key])

                # Update progress
                progress_percent = round(n*i)
                progress_bar.progress(progress_percent)
                status_text.text(f"Processing: {progress_percent}%")
                i = i+1

            st.session_state.data = pd.DataFrame(data)
            st.session_state.data_loaded = True
            st.session_state.forecasted_data = forecasted_data
            st.session_state.all_material_nos = all_material_nos
            st.session_state.oem = oem
            
            progress_bar.empty()
            status_text.empty()

        # Display the form
        with st.form("override_form"):
            edited_df = st.data_editor(
                st.session_state.data,
                hide_index=True,
                column_config={
                    "Sl No": st.column_config.NumberColumn(disabled=True),  # Added Sl No column config
                    "Material No": st.column_config.TextColumn(disabled=True),
                    "Description": st.column_config.TextColumn(disabled=True),
                    "VED": st.column_config.SelectboxColumn(
                        options=["Vital", "Essential", "Desirable"],
                        required=True
                    ),
                    'One off Requirement (forecasted)': st.column_config.NumberColumn(disabled=True),
                    'Regular Requirement': st.column_config.NumberColumn(disabled=True),
                    'Overhaul Qty': st.column_config.NumberColumn(disabled=True),
                    'Anticipated Qty': st.column_config.NumberColumn(disabled=True),
                    'Plant Stock': st.column_config.NumberColumn(disabled=True),
                    'On order Stock': st.column_config.NumberColumn(disabled=True),
                    'In process Stock': st.column_config.NumberColumn(disabled=True),
                    'Net Requirement (forecasted)': st.column_config.NumberColumn(disabled=True),
                    'Final Requirement (override)': st.column_config.NumberColumn(disabled=True),
                },
                key="data_editor"
            )

            st.write("Enter the quantity in Override Qty to override the reorder quantity")

            # Submit button - only runs when clicked
            submitted = st.form_submit_button("Apply Overrides")

            if submitted:
                # Update the session state with the edited values
                for index, row in edited_df.iterrows():
                    material_no = row['Material No']
                    d_net_requirement = row['Net Requirement (forecasted)']
                    d_one_off_requirement = row['One off Requirement (forecasted)']
                    d_one_off_requirement_override = row['One off Requirement (override)']
                    d_final_requirement = d_net_requirement - d_one_off_requirement + d_one_off_requirement_override
                    edited_df.loc[index, 'Final Requirement (override)'] = d_final_requirement
                    st.session_state.override_reasons[material_no] = row['Justification for manual override']

                # Update the displayed data
                st.session_state.data = edited_df
                st.session_state.show_data = True
                st.success("Overrides applied!")
                
                # Prevent rerun by using st.experimental_rerun() only when necessary
                st.rerun()

        # Display the current state of the data only after Apply Overrides is clicked
        if st.session_state.show_data:
            st.write("Current Requirements:")
            st.dataframe(st.session_state.data)
            
            # Add a submit button to update tracking.csv
            if st.button("Submit Requirements"):
                try:
                    # Load existing tracking data or create new if it doesn't exist
                    try:
                        tracking_df = pd.read_csv("files/tracking.csv")
                    except FileNotFoundError:
                        tracking_df = pd.DataFrame(columns=[
                            "Timestamp", "User", "Material No", "VED", 
                            "Final Requirement", "Justification"
                        ])
                    
                    # Get current user (you might want to replace this with actual user authentication)
                    user = "Current User"  # Replace with actual user identification
                    
                    # Add new entries to tracking dataframe
                    for index, row in st.session_state.data.iterrows():
                        new_entry = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "User": user,
                            "Material No": row["Material No"],
                            "VED": row["VED"],
                            "Final Requirement": row["Final Requirement (override)"],
                            "Justification": row["Justification for manual override"]
                        }
                        tracking_df = pd.concat([tracking_df, pd.DataFrame([new_entry])], ignore_index=True)
                    
                    # Save the updated tracking dataframe
                    tracking_df.to_csv("files/tracking.csv", index=False)
                    st.success("Requirements submitted successfully! You can track the status on REQ Tracking")
                    
                except Exception as e:
                    st.error(f"Error updating tracking file: {str(e)}")

    else:
        st.warning("No material selected")