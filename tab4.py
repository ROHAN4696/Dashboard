import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# 🎨 Custom CSS for Styling
# -----------------------------
# Set page background to light grey and apply card-like styling to containers
# Streamlit's light theme secondary background is a good target for charts/widgets.

custom_css = """
<style>
/* 1. Page Background to Light Grey (Streamlit's secondary background color is a good light grey) */
/* This targets the main app container */
.stApp {
    background-color: #F0F2F6; 
}

/* 2. Rounded Borders and Card-like styling for Plot Containers */
/* Target Streamlit's main block containers (st.container, st.columns) which hold the charts */
/* We target the div that contains the plotly charts in a column/block */
[data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"] {
    /* Apply styles to blocks that are likely containing the charts */
    padding: 15px;
    border: 1px solid #e6e6e6; /* Light border */
    border-radius: 10px; /* Rounded corners */
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
    margin-bottom: 20px; 
    background-color: white; /* Keep the interior white for contrast */
}
    div.stPlotlyChart {
        border: 1px solid #CCCCCC; 
        border-radius: 10px; 
        padding: 10px;
        background-color: white; /* Internal container background */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    }
/* Add padding to the column parent to ensure space between cards in a row */
[data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
    padding: 0 10px;
}

/* Fix for the very first top-level chart containers */
.stApp > header {
    background-color: #F0F2F6; 
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# -----------------------------
# Set Streamlit page to wide and define helper
# -----------------------------
st.set_page_config(layout="wide")

# --- Assumed: df is loaded and available via st.session_state ---
try:
    # Use a copy to avoid SettingWithCopyWarning during modifications
    df = st.session_state['netflix_df'].copy() 
except KeyError:
    st.error("Please ensure 'netflix_df' is loaded into st.session_state.")
    st.stop()
except AttributeError:
    # This block handles the case where st.session_state is not available or df is not a proper DataFrame
    st.error("DataFrame not found or improperly structured. Cannot proceed.")
    st.stop()


# -----------------------------
# Plot Function Helper
# -----------------------------
def update_fig_style(fig, title):
    """Applies common style updates including red title, Times New Roman font, and grid."""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Times New Roman', color='black', size=14),
    
        title=dict(
            text=title,
             font=dict(color="red"),
        ),
        xaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='black'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='black'),
    )
    return fig


# -----------------------------
# Preprocessing: Ensure all data required for the charts is ready
# -----------------------------

# Prep for Choropleth (Graph 1)
country_counts = (
    df['country'].dropna().str.split(',').explode().str.strip().value_counts().reset_index()
)
country_counts.columns = ['country', 'count']

# Prep for Scatter Geo (Graphs 2 & 3)
df_geo = df.copy().dropna(subset=['country', 'type'])
df_geo = df_geo.assign(country=df_geo['country'].str.split(', ')).explode('country')
df_geo['country'] = df_geo['country'].str.strip()
movies_df = df_geo[df_geo['type'] == 'Movie']
tv_df = df_geo[df_geo['type'] == 'TV Show']
movies_pct = movies_df['country'].value_counts(normalize=True).reset_index()
movies_pct.columns = ['country', 'percentage']
movies_pct['percentage'] *= 100
tv_pct = tv_df['country'].value_counts(normalize=True).reset_index()
tv_pct.columns = ['country', 'percentage']
tv_pct['percentage'] *= 100

# Prep for Top 10 Non-US (Graphs 4 & 5) and Origin plots (Graphs 6, 7)
df_pre_origin = df.copy() # Use a clean copy for origin calcs
df_pre_origin['country'] = df_pre_origin['country'].astype(str)
df_pre_origin = df_pre_origin[df_pre_origin['country'].notna()]
df_pre_origin = df_pre_origin[df_pre_origin['country'].str.lower() != 'unknown']

# Prep for Lag/Origin/Rating plots (Graphs 6 & 7)
df_pre_origin['date_added'] = pd.to_datetime(df_pre_origin['date_added'], errors='coerce')
df_pre_origin['year_added'] = df_pre_origin['date_added'].dt.year
df_pre_origin['primary_country'] = df_pre_origin['country'].str.split(',').str[0].str.strip()

def get_origin(country):
    if country == 'United States':
        return 'Domestic'
    elif pd.isna(country) or country == '':
        return pd.NA
    else:
        return 'International'

df_pre_origin['content_origin'] = df_pre_origin['primary_country'].apply(get_origin)
df_pre_origin = df_pre_origin.dropna(subset=['content_origin']) # Drop titles with no clear origin



# -----------------------------
#   Graph 1: Netflix Titles by Country (Choropleth)
# -----------------------------
fig1 = px.choropleth(
    country_counts,
    locations='country',
    locationmode='country names',
    color='count',
    hover_name='country',
    color_continuous_scale='Reds',
)
# fig1.update_layout(margin=dict(l=0,r=0,t=50,b=0), height=500, title_x=0.5) 
# fig1 = update_fig_style(fig1, 'Netflix Titles by Country')
# st.plotly_chart(fig1, use_container_width=True)

# # Country Filter UI (Part of the first section)
# st.markdown("---")
# selected_country = st.selectbox("Filter by Country", sorted(country_counts['country'].unique()))
# # Use the main df for filtering here to maintain original data integrity for the filter output
# filtered_df = df[df['country'].fillna("").str.contains(selected_country, case=False)] 
# st.subheader(f"Titles from {selected_country}")
# st.dataframe(filtered_df[['title', 'type', 'director', 'release_year', 'listed_in']])
# st.markdown("---")

# -----------------------------
#   Graphs 2 & 3: Scatter Geo for Movies/TV Shows (Side-by-Side)
# -----------------------------
# --- Title 1: Content Distribution by Type Across the Globe ---
st.markdown(
    """
    <div style='background-color: red; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
    <h2 style='color: white; font-weight: bold; margin: 0;'>
Content Distribution by Type Across the Globe</h2>
    </div>
    """, 
    unsafe_allow_html=True
)

col_a, col_b = st.columns(2)

with col_a:
    fig2 = px.scatter_geo(
        movies_pct,
        locations="country",
        locationmode="country names",
        size="percentage",
        hover_name="country",
        hover_data={"percentage": ":.2f"},
        projection="natural earth",
        color_discrete_sequence=["red"],
        title="Movies: % of Titles per Country"
    )
    # Explicit height set for consistency and center title
    fig2.update_layout(geo=dict(showframe=False, showcoastlines=True), margin=dict(l=0,r=0,t=50,b=0), height=500, title_x=0.5)
    fig2 = update_fig_style(fig2, 'Movies: % of Titles per Country')
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    fig3 = px.scatter_geo(
        tv_pct,
        locations="country",
        locationmode="country names",
        size="percentage",
        hover_name="country",
        hover_data={"percentage": ":.2f"},
        projection="natural earth",
        color_discrete_sequence=["blue"],
        title="TV Shows: % of Titles per Country"
    )
    # Explicit height set for consistency and center title
    fig3.update_layout(geo=dict(showframe=False, showcoastlines=True), margin=dict(l=0,r=0,t=50,b=0), height=500, title_x=0.5)
    fig3 = update_fig_style(fig3, 'TV Shows: % of Titles per Country')
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------
#2nd map
#2nd map

# STREAMLIT PAGE SETTINGS
# st.set_page_config(layout="wide", page_title="Netflix Country & Genre Map") # This line is redundant if page config is set at the top

# --- Title 2: Netflix Content Distribution Map (Movies vs TV Shows + Top Genre) ---
st.markdown(
    """
    <div style='background-color: red; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
    <h2 style='color: white; font-weight: bold; margin: 0;'>
Netflix Content Distribution Map (Movies vs TV Shows + Top Genre)</h2>
    </div>
    """, 
    unsafe_allow_html=True
)

# LOAD DATA (The data loading here is technically redundant if already loaded but kept for context)
df = df.dropna(subset=['country', 'type', 'listed_in'])

# FIX MULTIPLE COUNTRIES
df = df.assign(country=df['country'].str.split(', ')).explode('country')
df['country'] = df['country'].str.strip()


df["genre_list"] = df["listed_in"].str.split(",").apply(lambda x: [i.strip() for i in x])

genre_dummies = (
    df["genre_list"]
    .explode()
    .str.get_dummies()
    .groupby(level=0)
    .sum()
)

df = df.join(genre_dummies)

genre_cols = genre_dummies.columns.tolist()
if len(genre_cols) == 0:
    st.error("⚠ No valid genre columns created — please check data!")
    st.stop()


# SPLIT MOVIES / TV SHOWS
movies_df = df[df['type'] == "Movie"].copy()
tv_df = df[df['type'] == "TV Show"].copy()


# CALCULATE % PER COUNTRY (relative to type total)
movies_pct = movies_df['country'].value_counts(normalize=True).reset_index()
movies_pct.columns = ['country', 'percentage']
movies_pct['percentage'] *= 100

tv_pct = tv_df['country'].value_counts(normalize=True).reset_index()
tv_pct.columns = ['country', 'percentage']
tv_pct['percentage'] *= 100


# FIND COUNTRY → TOP GENRE FOR MOVIES / TV
def get_top_genre(df_):
    grouped = df_.groupby("country")[genre_cols].sum()
    top = grouped.idxmax(axis=1)
    return top.reset_index().rename(columns={0: "top_genre"})


movies_top = get_top_genre(movies_df)
tv_top = get_top_genre(tv_df)

movies_final = movies_pct.merge(movies_top, on="country", how="left")
tv_final = tv_pct.merge(tv_top, on="country", how="left")


# COLOR MAP FOR GENRES
color_map = {
    g: px.colors.qualitative.Bold[i % len(px.colors.qualitative.Bold)]
    for i, g in enumerate(genre_cols)
}


# MOVIE MAP
fig_movies = px.scatter_geo(
    movies_final,
    locations="country",
    locationmode="country names",
    size="percentage",
    color="top_genre",
    hover_name="country",
    hover_data={"percentage": ":.2f", "top_genre": True},
    projection="natural earth",
    title=" Movies: % of Titles & Top Genre by Country",
    color_discrete_map=color_map
)
fig_movies.update_layout(
    margin=dict(l=0, r=0, t=50, b=0),
    geo=dict(showframe=False, showcoastlines=True),
)


# TV SHOW MAP
fig_tv = px.scatter_geo(
    tv_final,
    locations="country",
    locationmode="country names",
    size="percentage",
    color="top_genre",
    hover_name="country",
    hover_data={"percentage": ":.2f", "top_genre": True},
    projection="natural earth",
    title=" TV Shows: % of Titles & Top Genre by Country",
    color_discrete_map=color_map
)
fig_tv.update_layout(
    margin=dict(l=0, r=0, t=50, b=0),
    geo=dict(showframe=False, showcoastlines=True),
)


# DISPLAY SIDE-BY-SIDE
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_movies, use_container_width=True)

with col2:
    st.plotly_chart(fig_tv, use_container_width=True)

# --- Title 3: International vs Domestic content Analysis ---
st.markdown(
    """
    <div style='background-color: red; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
    <h2 style='color: white; font-weight: bold; margin: 0;'>International vs. Domestic Content Analysis</h2>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- Prep for Top 10 Non-US (Graph 4) ---
countries_g4 = (
    df_pre_origin['country']
    .str.split(',')
    .explode()
    .str.strip()
)
# Exclude 'United States' for international focus
countries_g4 = countries_g4[countries_g4.str.lower() != 'united states'] 
top_countries_g4 = countries_g4.value_counts().head(10).reset_index()
top_countries_g4.columns = ['Country', 'Count']

fig4 = px.bar(
    top_countries_g4,
    x='Country',
    y='Count',
    text='Count',
    title='Top 10 Countries (International) on Netflix',
    color_discrete_sequence=['red']
)
fig4.update_traces(textposition='outside', textfont=dict(color='black', ))
fig4.update_xaxes(tickangle=45)
# Set height explicitly to 500
fig4.update_layout(height=500) 
fig4 = update_fig_style(fig4, 'Top 10 Countries (International) on Netflix')
fig4.update_yaxes(title='Number of Titles')


# --- Country vs Content Type (Graph 5) ---
df_non_us_type = df_pre_origin[~df_pre_origin['primary_country'].str.contains('United States', case=False, na=False)]
top_countries_g5 = df_non_us_type['primary_country'].value_counts().head(10).index
df_top_g5 = df_non_us_type[df_non_us_type['primary_country'].isin(top_countries_g5)]
country_type = (
    df_top_g5.groupby(['primary_country', 'type'])
        .size()
        .reset_index(name='count')
)
red_shades_g5 = ['#FF4C4C', '#B22222']

fig5 = px.bar(
    country_type,
    y='primary_country',
    x='count',
    color='type',
    orientation='h',
    title='Country vs Content Type (Top 10 International Countries)',
    color_discrete_sequence=red_shades_g5
)
# Set height explicitly to 500
fig5.update_layout(barmode='group', height=500, legend=dict(title='Content Type'))
fig5 = update_fig_style(fig5, 'Country vs Content Type (Top 10 International Countries)')
fig5.update_yaxes(title='Country')
fig5.update_xaxes(title='Number of Titles')


# --- Growth of International vs Domestic Content (Graph 6) ---
yearly = (
    df_pre_origin.groupby(['year_added', 'content_origin'])
      .size()
      .reset_index(name='count')
)
red_shades_g6 = ['#FF4C4C', '#B22222']

fig6 = px.line(
    yearly,
    x='year_added',
    y='count',
    color='content_origin',
    markers=True,
    title='Growth of International vs Domestic Content Over Time',
    color_discrete_sequence=red_shades_g6
)
fig6.update_traces(line=dict(width=3))
# Set height explicitly to 500
fig6.update_layout(legend=dict(title='Content Origin'), height=500)
fig6 = update_fig_style(fig6, 'Growth of International vs Domestic Content Over Time')
fig6.update_xaxes(title='Year Added')
fig6.update_yaxes(title='Number of Titles')


# --- Content Rating Distribution (Graph 7) ---
rating_counts = (
    df_pre_origin.groupby(['rating', 'content_origin'])
      .size()
      .reset_index(name='count')
)
rating_order = df_pre_origin['rating'].value_counts().index.tolist()
red_shades_g7 = ['#FF4C4C', '#B22222']

fig7 = px.bar(
    rating_counts,
    y='rating',
    x='count',
    color='content_origin',
    orientation='h',
    category_orders={'rating': rating_order},
    color_discrete_sequence=red_shades_g7,
    title='Content Rating Distribution: Domestic vs International'
)
# Set height explicitly to 500
fig7.update_layout(barmode='group', legend=dict(title='Content Origin'), height=500)
fig7 = update_fig_style(fig7, 'Content Rating Distribution: Domestic vs International')
fig7.update_yaxes(title='Rating')
fig7.update_xaxes(title='Number of Titles')


# -----------------------------
# Display the final four graphs in a 2x2 grid
# -----------------------------

# Row 1
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig4, use_container_width=True)
with col2:
    st.plotly_chart(fig5, use_container_width=True)

# Row 2
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig6, use_container_width=True)
with col4:
    st.plotly_chart(fig7, use_container_width=True)




# Set the page title/layout for the Streamlit app
st.set_page_config(layout="wide")

# -----------------------------


# -----------------------------
# Compute top 10 countries + Others
# -----------------------------
# Using dfn, consistent with the initial load step
all_count1 = df['country'].value_counts()

# Ensure we have at least 11 countries to perform the split, otherwise handle gracefully
if len(all_count1) > 10:
    mcpctrs1 = all_count1.head(10).copy()       # top 10
    mcpctrs1['Others'] = all_count1.iloc[10:].sum() # sum of remaining
else:
    mcpctrs1 = all_count1.copy()

# Convert the Series to a DataFrame for Plotly Express
df_pie = mcpctrs1.reset_index()
df_pie.columns = ['Country', 'Count']


# -----------------------------
# Updated Red-to-Brown Color scheme
# -----------------------------
new_colors_red_brown = [
    '#E50914',  # Bright Red
    '#B20710',  # Darker Red
    '#800000',  # Maroon
    '#A52A2A',  # Brown
    '#CD853F',  # Peru (Medium Brown)
    '#D2B48C',  # Tan (Lighter Brown)
    '#F5DEB3',  # Wheat (Lightest Brown)
    '#DEB887',  # BurlyWood
    '#BC8F8F',  # RosyBrown
    '#A9A9A9',  # Dark Gray (for later slices)
    '#696969'   # Dim Gray (for 'Others')
]

# Select only the colors needed, based on the number of slices
colors_for_plot = new_colors_red_brown[:len(df_pie)]


# -----------------------------
# Create Plotly Donut chart (added hole=0.3 and increased height)
# -----------------------------
fig = px.pie(
    df_pie,
    values='Count',
    names='Country',
    title='Content Distribution by Country (Top 10 + Others)',
    color_discrete_sequence=colors_for_plot,
    height=700, # Height remains 450
    hole=0.3    # Added hole for donut chart
)

# Apply Styling (changed border color to white)
fig.update_traces(
    textinfo='percent+label',
    rotation=90,
    # Set the wedge properties (white edge border)
    marker=dict(line=dict(color='#FFFFFF', width=2)),
    # Set the text color and style for better visibility (white, bold)
    textfont=dict(color="#FFFFFF", size=10, family="sans-serif", weight='bold'),
    textposition='inside',
    # **MODIFICATION: Increase the radius of the circle**
    # Domain controls the chart area [xmin, xmax], [ymin, ymax] from 0 to 1.
    # Increasing max values (e.g., to 0.95) makes the chart bigger within the plot area.
    domain={'x': [0.05, 0.95], 'y': [0.05, 0.95]} 
)

fig.update_layout(

    title_font_color="#FF0000",
    title_font_size=20,
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend_title_text='Country',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.05
    )
)

# -----------------------------
# Display in Streamlit
# -----------------------------
st.plotly_chart(fig, use_container_width=True)