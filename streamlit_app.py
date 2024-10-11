import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="Electrolyzer Data Analysis", page_icon=":bar_chart:", layout="wide")

image = Image.open('NitroVolt_Default(2).png')

st.image(image, width=500)

Title = st.title("Electrolyzer Data Analysis")

# When using excel
#file_path = 'Book1.xlsx'
#df = pd.read_excel(file_path, header=7)

sheet_url='https://docs.google.com/spreadsheets/d/e/2PACX-1vRRBGdnCxVwSG6HoCNVI1inzyAFjEYtccE-0OJojOUOwSqa2V82cpTZ4lhWYszI3kqYNRxs5xa4TO7O/pub?output=csv'

df = pd.read_csv(sheet_url, header=7)

# Convert columns to numeric just in case
df['net/nominal production rate max'] = pd.to_numeric(df['net/nominal production rate max'], errors='coerce')
df['average power consumption by stack min'] = pd.to_numeric(df['average power consumption by stack min'], errors='coerce')
df['average power consumption by stack max'] = pd.to_numeric(df['average power consumption by stack max'], errors='coerce')
df['average power consumption by system'] = pd.to_numeric(df['average power consumption by system'], errors='coerce')

# combine min  and max for the satck
df['average power consumption by stack combined'] = df['average power consumption by stack min'].combine_first(df['average power consumption by stack max'])

df_filtered = df.dropna(subset=['net/nominal production rate max'])

# Filter by 'net/nominal production rate max' <= 1200
df_filtered = df_filtered[df_filtered['net/nominal production rate max'] <= 1200]

st.sidebar.header("Filter Options")

# Filtrar by manufacturer
companies = sorted(df_filtered['manufacturer'].unique())
selected_companies = st.sidebar.multiselect("Select Companies", companies, default=companies)

# Filtrar by Location
locations = sorted(df_filtered['Location'].unique())
selected_locations = st.sidebar.multiselect("Select Locations", locations, default=locations)

# Apply the filters
df_filtered = df_filtered[(df_filtered['manufacturer'].isin(selected_companies)) & 
                          (df_filtered['Location'].isin(selected_locations))]

# Net porduction slider
net_prod_min, net_prod_max = st.sidebar.slider(
    'Net/Nominal Production Rate Max (Nm³/h)',
    int(df_filtered['net/nominal production rate max'].min()),
    int(df_filtered['net/nominal production rate max'].max()),
    (int(df_filtered['net/nominal production rate max'].min()), int(df_filtered['net/nominal production rate max'].max()))
)

df_filtered = df_filtered[(df_filtered['net/nominal production rate max'] >= net_prod_min) & 
                          (df_filtered['net/nominal production rate max'] <= net_prod_max)]

# Slider for power consumption (changes stack and system at same time)
power_min, power_max = st.sidebar.slider(
    'Average Power Consumption (kWh/Nm³)',
    float(min(df_filtered['average power consumption by stack combined'].min(), df_filtered['average power consumption by system'].min())),
    float(max(df_filtered['average power consumption by stack combined'].max(), df_filtered['average power consumption by system'].max())),
    (float(min(df_filtered['average power consumption by stack combined'].min(), df_filtered['average power consumption by system'].min())),
     float(max(df_filtered['average power consumption by stack combined'].max(), df_filtered['average power consumption by system'].max())))
)

df_filtered_stack = df_filtered[(df_filtered['average power consumption by stack combined'] >= power_min) & 
                                (df_filtered['average power consumption by stack combined'] <= power_max)]

df_filtered_system = df_filtered[(df_filtered['average power consumption by system'] >= power_min) & 
                                 (df_filtered['average power consumption by system'] <= power_max)]

# Scatter plot for stack
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
    template='plotly_white',
    height=1050,  
    width=1050    
)

fig_stack.update_layout(
    xaxis=dict(range=[-10, net_prod_max]),  
    yaxis=dict(range=[2.9, power_max])    
)

fig_stack.update_layout(
    xaxis=dict(range=[-10, net_prod_max], title_font=dict(size=20), tickfont=dict(size=16)),  # Font size for x-axis
    yaxis=dict(range=[2.9, power_max], title_font=dict(size=20), tickfont=dict(size=16)),    # Font size for y-axis
    legend=dict(title="Technology",title_font=dict(size=22), font=dict(size=22)),  # Title and font size for the legend
    title_font=dict(size=25) )

# Scatter plot for System
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
    template='plotly_white',
    height=1050, 
    width=1050
)


fig_system.update_layout(
    xaxis=dict(range=[-10, net_prod_max]), 
    yaxis=dict(range=[2.9, power_max])
)

fig_system.update_layout(
    xaxis=dict(range=[-10, net_prod_max], title_font=dict(size=20), tickfont=dict(size=16)),  # Font size for x-axis
    yaxis=dict(range=[2.9, power_max], title_font=dict(size=20), tickfont=dict(size=16)),    # Font size for y-axis
    legend=dict(title="Technology", title_font=dict(size=22), font=dict(size=22)),  # Title and font size for the legend
    title_font=dict(size=22)  # Font size for the title
)

st.plotly_chart(fig_stack, use_container_width=True)
st.plotly_chart(fig_system, use_container_width=True)

st.header("Suggestions for new electrolyzers")

st.markdown("https://docs.google.com/spreadsheets/d/1X9WFXng7z1fJmlgLHs0YCmQAzgnc_U9PseOId34QzHk/edit?usp=sharing")

st.title(":mailbox: Get in Touch with Us!")

contact_form = """
<form action="https://formsubmit.co/tcm@nitrovolt.com" method="POST">
     <input type="hidden" name="captcha" value="false">
     <input type="text" name = "name" placeholder="Your name" required>
     <input type="email" name = "email" placeholder="Your email" required>
     <textarea name="message" placeholder="You message here"></textarea>
     <button type = "submit">Send</button>
</form>
"""
st.markdown(contact_form, unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)

local_css("style.css")
