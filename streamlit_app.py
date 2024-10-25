import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="Electrolyzer Data Analysis", page_icon=":bar_chart:", layout="wide")

image = Image.open('NitroVolt_Default(2).png')

st.image(image, width=500)

Title = st.title("Electrolyzer Database")

st.write("Welcome to the Electrolyzer Database, a comprehensive survey of electrolyzers on the market! You can consume the information via a GoogleSheet [Database](https://docs.google.com/spreadsheets/d/1X9WFXng7z1fJmlgLHs0YCmQAzgnc_U9PseOId34QzHk/edit?usp=sharing) as well as via our summary plots on this page. This online tool is a side project by NitroVolt, a Danish startup dedicated to revolutionizing sustainable ammonia production via a novel electrochemical process. We value your feedback and are committed to continuously improving and expanding our database. If you have any corrections or would like to suggest a new electrolyzer add a comment in our spreadsheet or reach out to us via the contact form at the end of this page. In case you want to suggest the addition of a missing electrolyzer, please provide us with a datasheet and relevant links")

sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRRBGdnCxVwSG6HoCNVI1inzyAFjEYtccE-0OJojOUOwSqa2V82cpTZ4lhWYszI3kqYNRxs5xa4TO7O/pub?output=csv'
df = pd.read_csv(sheet_url, header=1)

# convert columns to numeric just in case
df['net/nominal production rate max'] = pd.to_numeric(df['net/nominal production rate max'], errors='coerce')
df['average power consumption by stack min'] = pd.to_numeric(df['average power consumption by stack min'], errors='coerce')
df['average power consumption by stack max'] = pd.to_numeric(df['average power consumption by stack max'], errors='coerce')
df['average power consumption by system'] = pd.to_numeric(df['average power consumption by system'], errors='coerce')

# round up
df['net/nominal production rate max'] = df['net/nominal production rate max'].round(0)
df['average power consumption by stack min'] = df['average power consumption by stack min'].round(1)
df['average power consumption by stack max'] = df['average power consumption by stack max'].round(1)
df['average power consumption by system'] = df['average power consumption by system'].round(1)

# combine min and max for the stack
df['average power consumption by stack combined'] = df['average power consumption by stack min'].combine_first(df['average power consumption by stack max'])

# remove missing values from production rate
df_filtered = df.dropna(subset=['net/nominal production rate max'])

# Filter by production rate <= 1200
df_filtered = df_filtered[df_filtered['net/nominal production rate max'] <= 1200]

st.sidebar.header("Filter Options")

# Filter by manufacturer
companies = sorted(df_filtered['manufacturer'].unique())
selected_companies = st.sidebar.multiselect("Select Companies", companies, default=companies)

# Filter by Location
locations = sorted(df_filtered['Location'].unique())
selected_locations = st.sidebar.multiselect("Select Locations", locations, default=locations)

# Apply the filters
df_filtered = df_filtered[(df_filtered['manufacturer'].isin(selected_companies)) & 
                          (df_filtered['Location'].isin(selected_locations))]

# Net production slider
net_prod_min, net_prod_max = st.sidebar.slider(
    'Net/Nominal Production Rate Max (Nm³/h)',
    int(df_filtered['net/nominal production rate max'].min()),
    int(df_filtered['net/nominal production rate max'].max()),
    (int(df_filtered['net/nominal production rate max'].min()), int(df_filtered['net/nominal production rate max'].max()))
)

df_filtered = df_filtered[(df_filtered['net/nominal production rate max'] >= net_prod_min) & 
                          (df_filtered['net/nominal production rate max'] <= net_prod_max)]

# Slider for power consumption 
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

# Sidebar options for customization
st.sidebar.header("Customization Options")
marker_size = st.sidebar.slider("Marker Size", 5, 30, 12)
title_font_size = st.sidebar.slider("Title Font Size", 15, 40, 25)
axis_font_size = st.sidebar.slider("Axis Font Size", 10, 25, 16)
legend_font_size = st.sidebar.slider("Legend Font Size", 10, 25, 22)


# Scatter plot for stack 
fig_stack = px.scatter(
    df_filtered,
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
    xaxis=dict(range=[-10, net_prod_max], title_font=dict(size=axis_font_size), tickfont=dict(size=axis_font_size)),
    yaxis=dict(range=[2.9, power_max], title_font=dict(size=axis_font_size), tickfont=dict(size=axis_font_size)),
    legend=dict(title="Technology", title_font=dict(size=legend_font_size), font=dict(size=legend_font_size)),
    title_font=dict(size=title_font_size)
)

# Hoverdata layout
fig_stack.update_traces(marker=dict(size=marker_size), 
    hovertemplate='<b>Electrolyzer technology</b>: %{customdata[1]}<br>' + 
                  '<b>Net production rate</b>: %{x} Nm³/h<br>' + 
                  '<b>System average power consumption</b>: %{y} kWh/Nm³<br>' + 
                  '<b>Manufacturer</b>: %{customdata[0]}<br>' + 
                  '<b>Origin</b>: %{customdata[2]}<extra></extra>')

# Scatter plot for system
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
    xaxis=dict(range=[-10, net_prod_max], title_font=dict(size=axis_font_size), tickfont=dict(size=axis_font_size)),
    yaxis=dict(range=[2.9, power_max], title_font=dict(size=axis_font_size), tickfont=dict(size=axis_font_size)),
    legend=dict(title="Technology", title_font=dict(size=legend_font_size), font=dict(size=legend_font_size)),
    title_font=dict(size=title_font_size)
)
# Hoverdata layout
fig_system.update_traces(marker=dict(size=marker_size), 
    hovertemplate='<b>Electrolyzer technology</b>: %{customdata[1]}<br>' + 
                  '<b>Net production rate</b>: %{x} Nm³/h<br>' + 
                  '<b>System average power consumption</b>: %{y} kWh/Nm³<br>' + 
                  '<b>Manufacturer</b>: %{customdata[0]}<br>' + 
                  '<b>Origin</b>: %{customdata[2]}<extra></extra>')

# Display plots
st.plotly_chart(fig_stack, use_container_width=True)
st.plotly_chart(fig_system, use_container_width=True)

#Contact Form
st.title(":mailbox: Get in Touch with Us!")

contact_form = """
<form action="https://formsubmit.co/ElectrolyzerDatabase@nitrovolt.com" method="POST">
     <input type="hidden" name="captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""
st.markdown(contact_form, unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.write("Copyright 2024 NitroVolt ApS. This tool is licensed under the GNU General Public Licenses v3.0.")
