import streamlit as st
import pandas as pd
from data import makedaywiseForecast
from datetime import datetime

def prepr_process_page(material_no=None):
    st.title("Pre PR Process")
    
    if material_no:
        st.write(f"Displaying forecast of material codes of Manufacturer related to Material No: {material_no}")
        forecasted_data = pd.read_csv("files/forecasted.csv")
        forecasted_data['Material No'] = forecasted_data['Material No'].astype(str)
        oem = forecasted_data[forecasted_data["Material No"] == material_no].iloc[0]['oem']
        all_material_nos = forecasted_data[forecasted_data["oem"] == oem].drop_duplicates(subset=["Material No"], keep='first')

        progress_bar = st.progress(0)
        status_text = st.empty()
        today = datetime.now().date().strftime("%d/%m/%Y")
        data = {
                "Material No": [],
                "Reorder Point": [],
                "Reorder Qty": [],
                "Updated Reorder Point":[],
                "Updated Reorder Qty": [],
                "Override Qty": [],
                "Reason for Override": []
        }


        if 'override_quantities' not in st.session_state:
            st.session_state.override_quantities = {}
        if 'override_reasons' not in st.session_state:
            st.session_state.override_reasons = {}

        
        rows = len(all_material_nos)
        n = 100/rows
        i=1
        for index, row in all_material_nos.iterrows():
            material_no = row['Material No'] 

            ordering_required = {}
            ordering_required[material_no]={}
            df, ordering_required[material_no] = makedaywiseForecast(forecasted_data, material_no, 'atlas')
            leadtime = ordering_required[material_no]['leadtime']
            reorder_point = ordering_required[material_no]['reorder_point']
            reorder_qty = ordering_required[material_no]['reorder_qty']
            updated_reorder_qty = ordering_required[material_no]['updated_reorder_qty']
            st.session_state.override_quantities[material_no] = updated_reorder_qty
            st.session_state.override_reasons[material_no] = ""

            # print(material_no, reorder_point, reorder_qty, updated_reorder_qty)
            new_row = {
                "Material No": material_no,
                "Reorder Point": reorder_point.strftime("%d/%m/%Y"),
                "Reorder Qty": reorder_qty,
                "Updated Reorder Point": today,
                "Updated Reorder Qty": updated_reorder_qty,
                "Override Qty": st.session_state.override_quantities[material_no],
                "Reason for Override": st.session_state.override_reasons[material_no]
            }

            for key in data:
                data[key].append(new_row[key])

            # Update progress
            progress_percent = round(n*i)
            progress_bar.progress(progress_percent)
            status_text.text(f"Processing: {progress_percent}%")
            i = i+1

        with st.form("override_form"):
            df = pd.DataFrame(data)
            edited_df = st.data_editor(
                df,
                    column_config={
                        "Material No": st.column_config.TextColumn(disabled=True),
                        "Reorder Point": st.column_config.TextColumn(disabled=True),
                        "Reorder Qty": st.column_config.TextColumn(disabled=True),
                        "Updated Reorder Point": st.column_config.TextColumn(disabled=True),
                        "Updated Reorder Qty": st.column_config.TextColumn(disabled=True)
                    },
            )

            st.write("Enter the quantity in Override Qty to override the reorder quantity")

            # Submit button - only runs when clicked
            submitted = st.form_submit_button("Apply Overrides")

            if submitted:
                print(st.session_state.override_quantities)
                st.success("Overrides applied!")
                st.write(edited_df)

    else:
        st.warning("No material selected")
