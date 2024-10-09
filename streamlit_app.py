import streamlit as st
import pandas as pd
import plotly.express as px

# Configure Streamlit page
st.set_page_config(page_title="Electrolyzer Data Analysis", page_icon=":bar_chart:", layout="wide")

st.title("Electrolyzer Data Analysis")

# Load the Excel file from the local directory (make sure this is correct)
file_path = 'Book1.xlsx'
df = pd.read_excel(file_path, header=7)

# Convert relevant columns to numeric
df['net/nominal production rate max'] = pd.to_numeric(df['net/nominal production rate max'], errors='coerce')
df['average power consumption by stack min'] = pd.to_numeric(df['average power consumption by stack min'], errors='coerce')
df['average power consumption by stack max'] = pd.to_numeric(df['average power consumption by stack max'], errors='coerce')
df['average power consumption by system'] = pd.to_numeric(df['average power consumption by system'], errors='coerce')

# Combine min and max power consumption columns for stack
df['average power consumption by stack combined'] = df['average power consumption by stack min'].combine_first(df['average power consumption by stack max'])

# Drop rows where 'net/nominal production rate max' is NaN after conversion
df_filtered = df.dropna(subset=['net/nominal production rate max'])

# Filter data where 'net/nominal production rate max' is less than or equal to 1200
df_filtered = df_filtered[df_filtered['net/nominal production rate max'] <= 1200]

# Sidebar for filters
st.sidebar.header("Filter Options")

# Filter by company (alphabetical)
companies = sorted(df_filtered['manufacturer'].unique())
selected_companies = st.sidebar.multiselect("Select Companies", companies, default=companies)

# Filter by location
locations = sorted(df_filtered['Location'].unique())
selected_locations = st.sidebar.multiselect("Select Locations", locations, default=locations)

# Apply company and location filters
df_filtered = df_filtered[(df_filtered['manufacturer'].isin(selected_companies)) & 
                          (df_filtered['Location'].isin(selected_locations))]

# Slider for net production rate
net_prod_min, net_prod_max = st.sidebar.slider(
    'Net/Nominal Production Rate Max (Nm³/h)',
    int(df_filtered['net/nominal production rate max'].min()),
    int(df_filtered['net/nominal production rate max'].max()),
    (int(df_filtered['net/nominal production rate max'].min()), int(df_filtered['net/nominal production rate max'].max()))
)

df_filtered = df_filtered[(df_filtered['net/nominal production rate max'] >= net_prod_min) & 
                          (df_filtered['net/nominal production rate max'] <= net_prod_max)]

# Slider for average power consumption by stack
power_min, power_max = st.sidebar.slider(
    'Average Power Consumption by Stack (kWh/Nm³)',
    float(df_filtered['average power consumption by stack combined'].min()),
    float(df_filtered['average power consumption by stack combined'].max()),
    (float(df_filtered['average power consumption by stack combined'].min()), float(df_filtered['average power consumption by stack combined'].max()))
)

df_filtered_stack = df_filtered[(df_filtered['average power consumption by stack combined'] >= power_min) & 
                                (df_filtered['average power consumption by stack combined'] <= power_max)]

# Slider for average power consumption by system
system_power_min, system_power_max = st.sidebar.slider(
    'Average Power Consumption by System (kWh/Nm³)',
    float(df_filtered['average power consumption by system'].min()),
    float(df_filtered['average power consumption by system'].max()),
    (float(df_filtered['average power consumption by system'].min()), float(df_filtered['average power consumption by system'].max()))
)

df_filtered_system = df_filtered[(df_filtered['average power consumption by system'] >= system_power_min) & 
                                 (df_filtered['average power consumption by system'] <= system_power_max)]

# Scatter plot for stack data
fig_stack = px.scatter(
    df_filtered_stack,
    x='net/nominal production rate max',
    y='average power consumption by stack combined',
    color='technology',
    hover_data=['manufacturer', 'technology', 'Location'],
    title='Net Production Rate vs Avg Power Consumption by Stack',
    labels={
        'net/nominal production rate max': 'Net production rate (Nm³/h)',
        'average power consumption by stack combined': 'Avg Power Consumption by Stack (kWh/Nm³)'
    },
    template='plotly_white'
)

fig_stack.update_layout(
    xaxis=dict(range=[-40, net_prod_max]),  # Ensure the x-axis starts at 0
    yaxis=dict(range=[2.9, power_max])  # Ensure the y-axis starts at 0
)

# Scatter plot for system data
fig_system = px.scatter(
    df_filtered_system,
    x='net/nominal production rate max',
    y='average power consumption by system',
    color='technology',
    hover_data=['manufacturer', 'technology', 'Location'],
    title='Net Production Rate vs Avg Power Consumption by System',
    labels={
        'net/nominal production rate max': 'Net production rate (Nm³/h)',
        'average power consumption by system': 'Avg Power Consumption by System (kWh/Nm³)'
    },
    template='plotly_white'
)

fig_system.update_layout(
    xaxis=dict(range=[-40, net_prod_max]),  # Ensure the x-axis starts at 0
    yaxis=dict(range=[2.91, system_power_max])  # Ensure the y-axis starts at 0
)

# Display both plots
st.plotly_chart(fig_stack, use_container_width=True)
st.plotly_chart(fig_system, use_container_width=True)
