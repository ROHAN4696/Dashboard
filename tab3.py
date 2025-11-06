#importing required libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# data reading
import pandas as pd

# Read the dataset
df = st.session_state['netflix_df']

# Convert date_added to datetime and drop missing dates
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df = df.dropna(subset=['date_added']).copy()

# ✅ Exclude all titles added in 2021
df = df[df['date_added'].dt.year != 2021].copy()
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. Data Processing and Preparation ---

# Read the dataset from session state
try:
    df = st.session_state['netflix_df'].copy()
except KeyError:
    st.error("Error: Netflix DataFrame not found in session state.")
    st.stop()

# Convert date_added to datetime and drop missing dates
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df = df.dropna(subset=['date_added']).copy()

# Exclude all titles added in 2021
df = df[df['date_added'].dt.year != 2021].copy()

# Extract month for season mapping
df['month'] = df['date_added'].dt.month

# Function to convert months to seasons
def month_to_season(month):
    if month in (1, 2, 3): return 'JFM'     # Winter
    if month in (4, 5, 6): return 'AMJ'     # Spring
    if month in (7, 8, 9): return 'JAS'     # Summer
    if month in (10, 11, 12): return 'OND'  # Autumn

# Apply the season mapping
df['season'] = df['month'].apply(month_to_season)

# Define season order and colors
season_order = ['JFM', 'AMJ', 'JAS', 'OND']
netflix_red = '#E50914'
netflix_light_red = '#404040' 

# Seasonal counts by content type (Movie vs TV Show)
by_type = (
    df.groupby(['season','type']).size()
      .unstack(fill_value=0)
      .reindex(index=season_order)
      .reset_index()
      .melt(id_vars='season', var_name='type', value_name='count')
)


# --- 2. Plotly Chart Generation ---

fig2 = px.bar(
    by_type, 
    x='season', 
    y='count', 
    color='type',
    category_orders={'season': season_order},
    title='Titles Added per Season — Movies vs TV Shows',
    labels={'season':'Season','count':'Titles Added','type':'Type'},
    # Use color_discrete_map for initial legend/color mapping
    color_discrete_map={'Movie': netflix_red, 'TV Show': netflix_light_red} 
)

# Apply text and hover styling
fig2.update_traces(
    texttemplate='%{y:,}',
    textposition='outside',
    hovertemplate="<b>%{x}</b><br>Titles Added: %{y:,}<extra></extra>"
)

# Assign colors for each trace (ensuring consistency)
fig2.for_each_trace(
    lambda t: t.update(marker_color=netflix_red if t.name == 'Movie' else netflix_light_red)
)

# Update layout with white backgrounds and styling
fig2.update_layout(
    paper_bgcolor='white',      # overall background
    plot_bgcolor='white',       # plot area background
    title_font=dict(size=22, color='black', family='Times New Roman'),
    font=dict(color='black', size=13, family='Times New Roman'),
    yaxis=dict(title='Number of Titles', showgrid=True, gridcolor='rgba(0,0,0,0.1)', color='black'),
    xaxis=dict(title='Season', color='black'),
    legend=dict(
        bgcolor='white',
        bordercolor='black',
        borderwidth=1,
        title_font=dict(color='black'),
        font=dict(color='black')
    ),
    margin=dict(t=20, b=60, l=60, r=40),
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)


# --- 3. Streamlit Layout and Display ---

# Divide the page into two columns
col1, col2 = st.columns(2)

# Place the chart in the first column
with col1:
    st.plotly_chart(fig2, use_container_width=True)
    
# The second column is left empty
with col2:
    pass
# Extract month and year
df['month'] = df['date_added'].dt.month
df['year'] = df['date_added'].dt.year

# Function to convert months to seasons
def month_to_season(month, hemisphere='NH'):
    if month in (1, 2, 3): return 'JFM'   # Winter
    if month in (4, 5, 6): return 'AMJ'   # Spring
    if month in (7, 8, 9): return 'JAS'   # Summer
    if month in (10, 11, 12): return 'OND' # Autumn

# Apply the season mapping
df['season'] = df['month'].apply(lambda m: month_to_season(m, hemisphere='NH'))

# Seasonal counts
season_order = ['JFM', 'AMJ', 'JAS', 'OND']
season_counts = (
    df.groupby('season')
      .size()
      .reindex(season_order)
      .fillna(0)
      .astype(int)
      .reset_index()
)
season_counts.columns = ['season', 'count']

# Add percentage of total and deviation from mean
total_titles = season_counts['count'].sum()
season_counts['pct_of_total'] = season_counts['count'] / total_titles * 100
mean_count = season_counts['count'].mean()
season_counts['pct_vs_mean'] = (season_counts['count'] - mean_count) / mean_count * 100

season_counts
# Define Netflix color shades
# Define Netflix color palette
netflix_red = '#E50914'
netflix_light_red = '#FF4C4C'  # lighter red for contrast

#PLOT 2: bar with tv shows vs movies
by_type = (
    df.groupby(['season','type']).size()
      .unstack(fill_value=0)
      .reindex(index=season_order)
      .reset_index()
      .melt(id_vars='season', var_name='type', value_name='count')
)

fig2 = px.bar(
    by_type, 
    x='season', 
    y='count', 
    color='type',
    category_orders={'season': season_order},
    title='Titles Added per Season — Movies vs TV Shows',
    labels={'season':'Season','count':'Titles Added','type':'Type'},
    color_discrete_map={'Movie': netflix_red, 'TV Show': '#404040'}  # dark gray for TV Shows
)
by_type
# Apply text and hover styling
fig2.update_traces(
    texttemplate='%{y:,}',
    textposition='outside',
    hovertemplate="<b>%{x}</b><br>Titles Added: %{y:,}<extra></extra>"
)

# Assign colors for each trace
fig2.for_each_trace(
    lambda t: t.update(marker_color=netflix_red if t.name == 'Movie' else netflix_light_red)
)

# Update layout with white backgrounds
fig2.update_layout(
    paper_bgcolor='white',       # overall background
    plot_bgcolor='white',        # plot area background
    title='',
    title_font=dict(size=22, color='black', family='Times New Roman'),
    font=dict(color='black', size=13, family='Times New Roman'),
    yaxis=dict(title='Number of Titles', showgrid=True, gridcolor='rgba(0,0,0,0.1)', color='black'),
    xaxis=dict(title='Season', color='black'),
    legend=dict(
        bgcolor='white',
        bordercolor='black',
        borderwidth=1,
        title_font=dict(color='black'),
        font=dict(color='black')
    ),
    margin=dict(t=20, b=60, l=60, r=40),
    uniformtext_minsize=8,
    uniformtext_mode='hide'
)

# Final show
fig2.show()
st.plotly_chart(fig2, use_container_width=True)