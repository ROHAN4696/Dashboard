# --- Importing required libraries ---
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page config for wide layout
st.set_page_config( layout="wide")


# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    /* 1. Document Background Color (Light Grey) */
    .stApp {
        background-color: #F0F0F0; /* Light Grey */
    }

    /* 2. Chart Container Styling (Round Border) */
    /* This targets the Streamlit wrapper around each Plotly chart to make it look like a card */
    div.stPlotlyChart {
        border: 1px solid #CCCCCC; 
        border-radius: 10px; 
        padding: 10px;
        background-color: white; /* Internal container background */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    }
    
    /* 3. Main title styling is now handled by the inline st.markdown below */
    
    /* Ensuring sidebar background is visible against the light grey app background */
    .css-1d391kg {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Data Reading and Preprocessing ---
# Read the dataset from session state
try:
    df = st.session_state['netflix_df'].copy()
except KeyError:
    st.error("Error: Netflix DataFrame not found in session state. Please ensure 'netflix_df' is loaded into st.session_state.")
    st.stop()

# Convert date_added to datetime and drop missing dates
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df = df.dropna(subset=['date_added']).copy()

# Exclude all titles added in 2021
df = df[df['date_added'].dt.year != 2021].copy()

# Extract month for season mapping
df['month'] = df['date_added'].dt.month

# --- Function to map month → season (Used for Fig 2 and 3 Data) ---
def month_to_season(month, hemisphere='NH'):
    if month in (1, 2, 3): return 'JFM'     # Winter
    if month in (4, 5, 6): return 'AMJ'     # Spring
    if month in (7, 8, 9): return 'JAS'     # Summer
    if month in (10, 11, 12): return 'OND'  # Autumn

# Apply the season mapping
df['season'] = df['month'].apply(lambda m: month_to_season(m, hemisphere='NH'))

# Define season order and colors
season_order = ['JFM', 'AMJ', 'JAS', 'OND']
netflix_red = '#E50914' # Dark Red for Movie
# NEW COLOR: Light Red/Orangish for TV Show
netflix_light_red_for_tv_show = "#F6602E" 



#  PLOT 1: Titles Added per Season — Movies vs TV Shows

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
    labels={'season':'Season','count':'Titles Added','type':'Type'},
    # APPLY NEW COLOR HERE
    color_discrete_map={'Movie': netflix_red, 'TV Show': netflix_light_red_for_tv_show} 
)

fig2.update_traces(
    texttemplate='%{y:,}',
    textposition='outside',
    hovertemplate="<b>%{x}</b><br>Titles Added: %{y:,}<extra></extra>"
)

# This loop ensures the colors are correctly assigned to each trace based on 'type'
fig2.for_each_trace(
    lambda t: t.update(marker_color=netflix_red if t.name == 'Movie' else netflix_light_red_for_tv_show)
)

# AXIS FIX and Consistent Height
fig2.update_layout(
    paper_bgcolor='white',
    plot_bgcolor='white',
    title=dict(text="Titles Added per Season — Movies vs TV Shows", font=dict(color="red")),
    font=dict(color='black', size=13, family='Times New Roman'),
    yaxis=dict(title='Number of Titles', showgrid=True, gridcolor='rgba(0,0,0,0.1)', color='black', showline=True, linecolor='black', linewidth=1), 
    xaxis=dict(title='Season', color='black', showline=True, linecolor='black', linewidth=1), 
    legend=dict(
        bgcolor='white',
        bordercolor='black',
        borderwidth=1,
        title_font=dict(color='black'),
        font=dict(color='black')
    ),
    margin=dict(t=80, b=60, l=60, r=40),
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    height=450 # Consistent height
)



#  PLOT 2: Seasonal Additions by Top Genres (Grouped Bar)

if 'listed_in' in df.columns:
    df_genres = df.assign(genre=df['listed_in'].str.split(',')).explode('genre')
    df_genres['genre'] = df_genres['genre'].str.strip().fillna('Unknown')
    top_genres = df_genres['genre'].value_counts().nlargest(6).index.tolist()
    genre_season = (
        df_genres[df_genres['genre'].isin(top_genres)]
        .groupby(['season','genre']).size()
        .unstack(fill_value=0)
        .reindex(index=season_order)
        .reset_index()
    )

    display_genres = list(top_genres)[:6]
    red_shades = ['#E50914', '#B00610', '#8B0000', '#FF5C5C', '#FF7F7F', '#FF9999']

    fig3 = go.Figure()

    for i, g in enumerate(display_genres):
        fig3.add_trace(go.Bar(
            name=g,
            x=genre_season['season'],
            y=genre_season[g],
            marker_color=red_shades[i % len(red_shades)],
            width=0.12,
            hovertemplate=f"<b>{g}</b><br>%{{x}}: %{{y:,}} titles<extra></extra>"
        ))

    # AXIS FIX and Consistent Height
    fig3.update_layout(
        barmode='group',
        bargap=0.22,
        bargroupgap=0.08,
        title=dict(text="Seasonal Additions by Top Genres", font=dict(color="red")),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black', size=13, family='Times New Roman'),
        xaxis=dict(
            title='Season',
            color='black',
            categoryorder='array',
            categoryarray=['JFM', 'AMJ', 'JAS', 'OND'],
            showline=True, linecolor='black', linewidth=1 
        ),
        yaxis=dict(
            title='Number of Titles',
            color='black',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            showline=True, linecolor='black', linewidth=1 
        ),
        legend=dict(bgcolor='white', bordercolor='black', borderwidth=1),
        margin=dict(t=90, b=60, l=80, r=40),
        height=450 # Consistent height
    )
else:
    fig3 = go.Figure().add_annotation(text="Genre data (listed_in) not available in DataFrame.", showarrow=False)
    fig3.update_layout(height=450, title="Seasonal Additions by Top Genres")



#  PLOT 3: Netflix Content Growth Over Years (Release Year)

yearly = df.groupby('release_year').size().reset_index(name='count')
yearly = yearly[yearly['release_year'] >= 2008]

fig_growth = px.line(
    yearly,
    x='release_year',
    y='count',
    title='Netflix Content Growth Over Years',
    markers=True,
    line_shape='linear'
)
fig_growth.update_traces(line_color='red')

# AXIS FIX and Consistent Height
fig_growth.update_layout(
    title=dict(text="Netflix Content Growth Over Years", font=dict(color="red")),
    xaxis_title='Release Year',
    yaxis_title='Number of Titles Released',
    template='plotly_white',
    plot_bgcolor='white', 
    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', showline=True, linecolor='black', linewidth=1), 
    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', showline=True, linecolor='black', linewidth=1), 
    margin=dict(t=80, b=60, l=60, r=40),
    height=450 # Consistent height
)



#  PLOT 4: Growth in Content-Producing Countries

country_growth = df.groupby('release_year')['country'].nunique().reset_index(name='unique_countries')
country_growth = country_growth[country_growth['release_year'] >= 2008]

fig_countries = go.Figure()

fig_countries.add_trace(go.Scatter(
    x=country_growth['release_year'],
    y=country_growth['unique_countries'],
    mode='lines+markers',
    line=dict(color='red', width=4, shape='linear'),
    marker=dict(size=8, color='red', line=dict(width=1, color='white')),
    name='Unique Countries'
))

# AXIS FIX and Consistent Height
fig_countries.update_layout(
      title=dict(text="Growth in Content-Producing Countries (Netflix Global Expansion)", font=dict(color="red")),
    xaxis_title="Release Year",
    yaxis_title="Number of Unique Countries",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black', size=14),
    hovermode="x unified",
    showlegend=False,
    xaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False, showline=True, linecolor='black', linewidth=1), 
    yaxis=dict(showgrid=True, gridcolor='lightgrey', zeroline=False, showline=True, linecolor='black', linewidth=1),
    height=450 # Consistent height
)



#  PLOT 5: Average Lag Between Release and Netflix Addition

# Ensure date columns are datetime
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['release_date'] = pd.to_datetime(df['release_year'], format='%Y', errors='coerce')

# Calculate lag (in days)
df['lag_days'] = (df['date_added'] - df['release_date']).dt.days
df_lag = df[df['lag_days'].between(0, 5000)].copy()

# Extract year only
df_lag['year_added'] = df_lag['date_added'].dt.year

# Average lag per type per **year**
avg_lag_yearly = (
    df_lag.groupby(['year_added', 'type'])['lag_days']
    .mean()
    .reset_index()
    .sort_values('year_added')
)

red_shades_lag = ['#FF4C4C', '#B22222'] 

fig_lag = px.line(
    avg_lag_yearly,
    x='year_added',
    y='lag_days',
    color='type',
    markers=True,
    color_discrete_sequence=red_shades_lag
)

# AXIS FIX and Consistent Height
fig_lag.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(
        family='Times New Roman',
        color='black',
        size=14
    ),
    title=dict(text="Average Lag Between Release and Netflix Addition (Movies vs TV Shows)", font=dict(color="red")),
    xaxis=dict(
        title='Year Added',
        showgrid=True,
        gridcolor='lightgray',
        linecolor='black',
        dtick=1,
        showline=True, linewidth=1 
    ),
    yaxis=dict(
        title='Average Lag (Days)',
        showgrid=True,
        gridcolor='lightgray',
        linecolor='black',
        showline=True, linewidth=1 
    ),
    legend=dict(
        title='Type',
        font=dict(family='Times New Roman', color='black')
    ),
    height=450 # Consistent height
)

fig_lag.update_traces(
    line=dict(width=3),
    marker=dict(size=8, symbol='circle')
)



#  PLOT 6: Movie Percentage vs TV Show Percentage Over Time

df_orig = st.session_state['netflix_df'].copy()
KPI_1 = pd.crosstab(columns=df_orig['type'], index=df_orig['release_year'])
KPI_1['Movie %'] = KPI_1['Movie'] * 100 / (KPI_1['Movie'] + KPI_1['TV Show'])
KPI_1['TV Show %'] = KPI_1['TV Show'] * 100 / (KPI_1['Movie'] + KPI_1['TV Show'])

df_temp_pct = KPI_1[KPI_1.index >= 1997].copy()

fig_pct = go.Figure()

fig_pct.add_trace(go.Scatter(
    x=df_temp_pct.index,
    y=df_temp_pct['Movie %'],
    mode='lines+markers',
    name='Movie %',
    marker=dict(color='red', size=6),
    line=dict(color='red', width=2)
))

fig_pct.add_trace(go.Scatter(
    x=df_temp_pct.index,
    y=df_temp_pct['TV Show %'],
    mode='lines+markers',
    name='TV Show %',
    marker=dict(color='black', size=6),
    line=dict(color='black', width=2)
))

# AXIS FIX and Consistent Height
fig_pct.update_layout(
    title=dict(text="Movie Percentage vs TV Show Percentage Over Time", font=dict(color="red")),
    xaxis=dict(
        title=dict(text="Year", font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=False,
        zeroline=False,
        color="black",
        showline=True, linecolor='black', linewidth=1 
    ),
    yaxis=dict(
        title=dict(text="Percentage", font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=False,
        zeroline=False,
        color="black",
        showline=True, linecolor='black', linewidth=1 
    ),
    legend=dict(
        title=dict(text="Category", font=dict(color="black")),
        font=dict(color="black")
    ),
    font=dict(family="Times New Roman", size=14, color="black"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=450 # Consistent height
)


# PLOT 7: Movie vs TV Show Growth Over Time (Percent Change)

KPI_2 = pd.crosstab(columns = df_orig['type'], index = df_orig['release_year'])
KPI_2 = KPI_2.sort_index()

KPI_2['Movie growth'] = KPI_2['Movie'].pct_change() * 100
KPI_2['TV Show growth'] = KPI_2['TV Show'].pct_change() * 100

df_growth_pct = KPI_2[KPI_2.index >= 2000].copy()

fig_growth_pct = go.Figure()

fig_growth_pct.add_trace(go.Scatter(
    x=df_growth_pct.index,
    y=df_growth_pct['Movie growth'],
    mode='lines',
    name='Movie growth',
    line=dict(color='red', width=2)
))

fig_growth_pct.add_trace(go.Scatter(
    x=df_growth_pct.index,
    y=df_growth_pct['TV Show growth'],
    mode='lines',
    name='TV Show growth',
    line=dict(color='black', width=2)
))

# AXIS FIX and Consistent Height
fig_growth_pct.update_layout(
    title=dict(text="Movie vs TV Show Growth Over Time", font=dict(color="red")),
    xaxis=dict(
        title=dict(text="Year", font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=False,
        zeroline=False,
        showline=True, linecolor='black', linewidth=1 
    ),
    yaxis=dict(
        title=dict(text="Growth", font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=False,
        zeroline=False,
        showline=True, linecolor='black', linewidth=1 
    ),
    legend=dict(
        title=dict(text="Category", font=dict(color="black")),
        font=dict(color="black")
    ),
    font=dict(family="Times New Roman", size=14, color="black"),
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=450, # Consistent height
    
    # Zero baseline
    shapes=[
        dict(
            type="line",
            x0=df_growth_pct.index.min(),
            x1=df_growth_pct.index.max(),
            y0=0,
            y1=0,
            line=dict(color="black", width=2)
        )
    ]
)



#  PLOT 8: Yearly Release Volume: Movies vs TV Seasons (Overlay Bar)

# Ensure df_orig is used for these calculations to prevent issues with df being modified
df_seasons = df_orig[df_orig['type'] == 'TV Show']['duration'].str[0].astype(int)
df_release_year = df_orig[df_orig['type'] == 'TV Show']['release_year'].value_counts()

# Adjusted logic for TV Show seasons to correctly increment subsequent years
# Create a series to hold adjusted TV show counts for each year
tv_show_adjusted_counts = pd.Series(0, index=range(df_orig['release_year'].min(), df_orig['release_year'].max() + 1))

for idx, num_seasons in df_seasons.items():
    release_yr = df_orig.loc[idx, 'release_year']
    for j in range(num_seasons):
        if (release_yr + j) in tv_show_adjusted_counts.index:
            tv_show_adjusted_counts[release_yr + j] += 1

df_rel_yr = pd.DataFrame(tv_show_adjusted_counts).reset_index()
df_rel_yr.columns = ['release_year', 'TV Show']
df_rel_yr.set_index('release_year', inplace=True)


df_movie = df_orig[df_orig['type'] == 'Movie']['release_year'].value_counts()
df_movie = pd.DataFrame(df_movie)
df_movie.columns.values[0] = 'Movie'

# Concatenate and handle missing years
full_years = pd.Series(0, index=range(df_orig['release_year'].min(), df_orig['release_year'].max() + 1))
df_sn_type = pd.concat([df_movie, df_rel_yr, full_years], axis=1).fillna(0).astype(int)
df_sn_type = df_sn_type.iloc[:, :2] # Keep only 'Movie' and 'TV Show' columns
df_sn_type.sort_index(inplace = True)


df_temp_volume = df_sn_type[df_sn_type.index >= 2000].copy()
df_temp_volume = df_temp_volume.reset_index()
df_temp_volume.rename(columns={'index': 'release_year'}, inplace=True)


movie_norm = (df_temp_volume['Movie'] - df_temp_volume['Movie'].min()) / (df_temp_volume['Movie'].max() - df_temp_volume['Movie'].min() + 1e-6)
tv_norm = (df_temp_volume['TV Show'] - df_temp_volume['TV Show'].min()) / (df_temp_volume['TV Show'].max() - df_temp_volume['TV Show'].min() + 1e-6)

movie_colors = [f"rgba(255, {int(220 - 200*m)}, {int(220 - 200*m)}, 1)" for m in movie_norm]
tv_colors    = [f"rgba({int(180 - 150*t)}, {int(180 - 150*t)}, {int(180 - 150*t)}, 1)" for t in tv_norm]

fig_volume = go.Figure()

fig_volume.add_trace(go.Bar(
    x=df_temp_volume['release_year'],
    y=df_temp_volume['TV Show'],
    name='TV Show',
    marker=dict(color=tv_colors),
    opacity=0.85,
))

fig_volume.add_trace(go.Bar(
    x=df_temp_volume['release_year'],
    y=df_temp_volume['Movie'],
    name='Movie',
    marker=dict(color=movie_colors),
    opacity=0.85
))

# AXIS FIX and Consistent Height
fig_volume.update_layout(
         title=dict(text="Yearly Release Volume: Movies vs TV Seasons", font=dict(color="red")),
    xaxis=dict(
        title=dict(text="Release Year", font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=False,
        zeroline=False,
        showline=True, linecolor='black', linewidth=1 
    ),
    yaxis=dict(
        title=dict(text="Count", font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=False,
        zeroline=False,
        showline=True, linecolor='black', linewidth=1 
    ),
    legend=dict(
        title=dict(text="Category", font=dict(color="black")),
        font=dict(color="black")
    ),
    font=dict(family="Times New Roman", size=14, color="black"),
    barmode='overlay',
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=450 # Consistent height
)






plots = [fig2, fig3, fig_growth, fig_countries, fig_lag, fig_pct, fig_growth_pct, fig_volume]

# Create 4 rows of 2 columns each
for i in range(0, len(plots), 2):
    col1, col2 = st.columns(2)
    
    # Plot 1 (Left Column)
    with col1:
        st.plotly_chart(plots[i], use_container_width=True)

    # Plot 2 (Right Column)
    if i + 1 < len(plots):
        with col2:
            st.plotly_chart(plots[i+1], use_container_width=True)

    # Add a main separator between rows of plots
