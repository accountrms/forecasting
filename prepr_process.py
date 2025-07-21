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

        i = 0
        progress_bar = st.progress(0)
        status_text = st.empty()
        today = datetime.now().date().strftime("%d/%m/%Y")
        data = {
                "Material No": [],
                "Reorder Point": [],
                "Reorder Qty": [],
                "Updated Reorder Point":[],
                "Updated Reorder Qty": []
        }

        for index, row in all_material_nos.iterrows():
            material_no = row['Material No'] 

            ordering_required = {}
            ordering_required[material_no]={}
            df, ordering_required[material_no] = makedaywiseForecast(forecasted_data, material_no, 'atlas')
            leadtime = ordering_required[material_no]['leadtime']
            reorder_point = ordering_required[material_no]['reorder_point']
            reorder_qty = ordering_required[material_no]['reorder_qty']
            updated_reorder_qty = ordering_required[material_no]['updated_reorder_qty']
            delivery_date = reorder_point + pd.DateOffset(days=leadtime)

            # print(material_no, reorder_point, reorder_qty, updated_reorder_qty)
            new_row = {
                "Material No": material_no,
                "Reorder Point": reorder_point.strftime("%d/%m/%Y"),
                "Reorder Qty": reorder_qty,
                "Updated Reorder Point": today,
                "Updated Reorder Qty": updated_reorder_qty
            }

            for key in data:
                data[key].append(new_row[key])

                # Update progress
            progress_percent = i*10
            progress_bar.progress(progress_percent)
            status_text.text(f"Processing: {progress_percent}%")
            i = i+1

        df = pd.DataFrame(data)
        st.table(df)

        st.divider()


        st.write("Enter the quantity below in case you want to override")

        if 'override_values' not in st.session_state:
            st.session_state.override_values = {}

        with st.form("override_form"):
            for index, row in df.iterrows():
                material_no = row['Material No']
                current_qty = float(row['Updated Reorder Qty'])

                # Use material_no as key to avoid duplicate widget keys
                override_qty = st.number_input(
                    f"Override for {material_no} (Forecasted Qty: {current_qty})",
                    key=f"override_{material_no}"  # Unique key for each widget
                )
                st.session_state.override_values[material_no] = override_qty

            # Submit button - only runs when clicked
            submitted = st.form_submit_button("Apply Overrides")

        if submitted:
            st.success("Overrides applied!")
            df['Override Qty'] = df['Material No'].map(st.session_state.override_values)
            st.dataframe(df)


    else:
        st.warning("No material selected")
