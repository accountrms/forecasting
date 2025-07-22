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
                "Description": [],
                'One off Requirement': [],
                'Regular Requirement': [],
                'Overhaul Qty': [],
                'Anticipated Qty': [],
                'Plant Stock': [],
                'On order Stock': [],
                'In process Stock': [],
                'Net Requirement': [],
                "Final Requirement": [],
                "Justification for manual override": []
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
            description = row['Desc']

            ordering_required = {}
            ordering_required[material_no]={}
            df, ordering_required[material_no] = makedaywiseForecast(forecasted_data, material_no, 'atlas')
            df = df.fillna(0)
            leadtime = ordering_required[material_no]['leadtime']
            reorder_point = ordering_required[material_no]['reorder_point']
            reorder_qty = ordering_required[material_no]['reorder_qty']
            one_off_requirement = round(df.iloc[0]["One-off_req"])
            regular_requirement = round(df.iloc[0]["Regular_req"])
            overhaul_quantity = 0
            anticipated_qty = round(df.iloc[0]["anticipated_consum"])
            plant_stock = 0
            on_order_stock = round(df.iloc[0]["on_order_stock"])
            in_process_stock = 0
            net_requirement = one_off_requirement + regular_requirement + overhaul_quantity + anticipated_qty - (plant_stock + on_order_stock + in_process_stock)
            updated_reorder_qty = ordering_required[material_no]['updated_reorder_qty']
            st.session_state.override_quantities[material_no] = updated_reorder_qty
            st.session_state.override_reasons[material_no] = ""
        
            print(df)

            new_row = {
                "Material No": material_no,
                "Description": description,
                'One off Requirement': one_off_requirement,
                'Regular Requirement': regular_requirement,
                'Overhaul Qty': overhaul_quantity,
                'Anticipated Qty': anticipated_qty,
                'Plant Stock': plant_stock,
                'On order Stock': on_order_stock,
                'In process Stock': in_process_stock,
                'Net Requirement': net_requirement,
                "Final Requirement": st.session_state.override_quantities[material_no],
                "Justification for manual override": st.session_state.override_reasons[material_no]
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
                        "Description": st.column_config.TextColumn(disabled=True),
                        'One off Requirement': st.column_config.TextColumn(disabled=True),
                        'Regular Requirement': st.column_config.TextColumn(disabled=True),
                        'Overhaul Qty': st.column_config.TextColumn(disabled=True),
                        'Anticipated Qty': st.column_config.TextColumn(disabled=True),
                        'Plant Stock': st.column_config.TextColumn(disabled=True),
                        'On order Stock': st.column_config.TextColumn(disabled=True),
                        'In process Stock': st.column_config.TextColumn(disabled=True),
                        'Net Requirement': st.column_config.TextColumn(disabled=True),
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
