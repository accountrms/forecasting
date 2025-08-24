import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plotgraph(df, col, col2):
    fig = go.Figure()
    # Add line plots
    for col in [col]:
        fig.add_trace(go.Scatter(
            x=df["years"],
            y=df[col],
            mode="lines+markers",
            name=col
        ))

    # Add bar plot
    fig.add_trace(go.Bar(
        x=df["years"],
        y=df[col2],
        name="Weighted Leadtime",
        opacity=0.5,  # adjust transparency
        width=0.4  # adjust bar width (smaller = thinner bars)
    ))

    # Layout
    fig.update_layout(
        title=f"{col[:-4]}Leadtime over years with weightages",
        xaxis_title="Year",
        yaxis_title="Leadtime in Days",
        barmode="overlay"  # overlay bars on lines; change to 'group' if you want side-by-side
    )

    st.plotly_chart(fig, use_container_width=False)


def plot2(f):
    variables = ['SVR', 'Linear Regression', 'Exponential Smoothening', 'Arima', 'Sarima']
    values = f.iloc[0].tolist()[1:]

    fig = go.Figure(go.Bar(
        x=values,  # values go to X-axis
        y=variables,  # categories on Y-axis
        orientation="h",  # horizontal bars
        width=0.4  # adjust bar thickness (0.1 = thin, 0.6 = thick)
    ))

    fig.update_layout(
        title="Mean-Squared-Errors for various models",
        xaxis_title="mse",
        yaxis_title="Models"
    )
    st.plotly_chart(fig, use_container_width=True)


def plot3(cons,f):
    x_years_line1 = list(range(2015, 2026))
    y_values_line1 = cons.qty.values
    variables = []
    variables.append(f[1:]['SVR'].to_list())
    variables.append(f[1:]['LR'].to_list())
    variables.append(f[1:]['EXP'].to_list())
    variables.append(f[1:]['ARIMA'].to_list())
    variables.append(f[1:]['SARIMA'].to_list())
    # Lines 2 to 6 for years 2026-2030 (5 data points each)
    x_years_lines2_6 = list(range(2025, 2031))
    y_values_lines2_6 = variables

    # Create a single figure
    fig = go.Figure()

    # Plot Line 1
    fig.add_trace(go.Scatter(
        x=x_years_line1,
        y=y_values_line1,
        mode='lines',
        name='Actuals (2015-2025)',
        line=dict(color='blue', width=2),
    ))

    # Plot lines 2 through 6 (forecasts) in a loop
    colors = ['red', 'green', 'purple', 'orange', 'brown']
    names = ['SVR', 'Linear Regression', 'Exponential Smoothening', 'Arima', 'Sarima']

    for i in range(len(y_values_lines2_6)):
        fig.add_trace(go.Scatter(
            x=x_years_lines2_6,
            y=y_values_lines2_6[i],
            mode='lines',
            name=names[i],
            line=dict(color=colors[i], dash='dash'),
        ))

    # Customize the plot layout
    fig.update_layout(
        title='Quantity Over Time: Actuals and Forecasts',
        xaxis_title='Year',
        yaxis_title='Quantity',
        legend_title='Data Series',
        # Set the x-axis range from 2015 to 2030
        xaxis=dict(range=[2015, 2030]),
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

def tech_analysis():
    lt = pd.read_csv("files/leadtimeMaster.csv")
    f = pd.read_csv("files/forecastedModels.csv")
    cons = pd.read_csv("files/cons.csv")

    st.title("🏭 Technical Analysis")
    st.divider()
    search_term = st.text_input("Analyse by Material No")
    if search_term:
        st.write(f"Analysing {search_term}.......")
        st.subheader("Leadtime Analysis")
        fig = px.bar(lt, x=lt.years, y=["PR-PO days", "PO-GR days", "GR-GI days"],
                     labels={"value": "Days", "variable": "Stage"},
                     title="Leadtime analysis - Historical year-wise data of the material",
                     barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Past Procurement Stage-wise plots")
        col1, col2, col3 = st.columns(3)
        with col1:
            plotgraph(lt,'PR-PO days','prpo_w')
        with col2:
            plotgraph(lt,'PO-GR days','pogr_w')
        with col3:
            plotgraph(lt,'GR-GI days','grgi_w')
        x, y, z = lt.prpo_w.sum(), lt.pogr_w.sum(), lt.grgi_w.sum()
        labels = ['PR-PO days', 'PO-GR days', 'GR-GI days']
        values = [x,y,z]
        newcol1,newcol2 = st.columns(2)
        with newcol1:
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    textinfo='label+value+percent',
                    insidetextorientation='radial',
                    marker=dict(line=dict(color='#000000', width=2)),
                    hole=0.3
                )
            ])
            st.plotly_chart(fig, use_container_width=True)
        with newcol2:
            st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
            st.write(f"Total Forecasted Leadtime = {round(x+y+z,1)} days")
            st.write(f"PR-PO forcasted days = {round(x,1)} days")
            st.write(f"PO-GR forcasted days = {round(y,1)} days")
            st.write(f"GR-GI forcasted days = {round(z,1)} days")
        st.subheader("Material Consumption Analysis")
        st.write(f"Model training and calculations of MSE")
        plot2(f)
        st.write(f"Best model as per cost function is SVR")
        plot3(cons,f)
        st.write(f"Consumption pattern forcasted by best model:")
        st.write(f"2026: {int(f[1:].SVR.iloc[1])} Nos")
        st.write(f"2027: {int(f[1:].SVR.iloc[2])} Nos")
        st.write(f"2028: {int(f[1:].SVR.iloc[3])} Nos")
        st.write(f"2029: {int(f[1:].SVR.iloc[4])} Nos")
        st.write(f"2030: {int(f[1:].SVR.iloc[5])} Nos")