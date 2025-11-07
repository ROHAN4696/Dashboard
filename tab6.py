import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import kagglehub

# --- 1. Configuration (MUST be the first command) ---
# Set theme to 'dark' for Streamlit native dark elements (sidebar, widgets)
st.set_page_config(layout="wide", page_title="Netflix Comprehensive Dashboard", initial_sidebar_state="expanded")

# Define colors for consistent styling where applicable
NETFLIX_RED = "#E50914" # Primary Netflix Red
NETFLIX_REDS = ["#FF4500", "#D82E2F", "#B01717", "#800000", "#400000"] # Color sequence for plots

# Dark Theme Colors
DARK_BACKGROUND = "#141414" # Almost black
DARK_CARD = "#222222" # Darker gray for cards/containers
DARK_TEXT = "#E0E0E0" # Light gray for text
DARK_BORDER = "#303030" # Dark border lines

# Custom color scheme for Plot C, focusing on red/brown/orange/yellow
CUSTOM_PLOT3_COLORS = [
    '#B01717',  # Dark Red
    '#D82E2F',  # Bright Red
    '#FF4500',  # Orange-Red
    '#FFA500',  # Orange
    '#FFD700',  # Gold/Yellow
    '#A52A2A',  # Brown
    '#8B4513',  # SaddleBrown
    '#C04000',  # Cinnabar/Rust
    '#E97451',  # Light Salmon
    '#800000' # Maroon
]

# ------------------------------------------------------------
# 2. Data Loading and Preparation Functions
# ------------------------------------------------------------

@st.cache_data
def load_main_data():
    """Downloads and loads the Netflix dataset (used for search and plots A, B, C)."""
    try:
        data_path = "netflix_titles.csv"
        # Using KaggleHub download logic as the primary way to ensure data availability.
        with st.spinner("Downloading Netflix dataset via KaggleHub..."):
            path = kagglehub.dataset_download("shivamb/netflix-shows")
            data_path = f"{path}/netflix_titles.csv"
            
        df = pd.read_csv(data_path)
        # Normalize columns for consistency
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        return df
    except Exception as e:
        st.error(f"Could not load main dataset: {e}")
        return pd.DataFrame()

@st.cache_data
def prepare_genre_cast_data(df):
    """Performs genre and cast explosion and cleaning for Plots A, B, C."""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_exploded = df.copy()
    df_exploded['country'] = df_exploded['country'].fillna('Missing') 
    # Explode genres
    df_exploded['genre'] = df_exploded['listed_in'].str.split(',')
    df_exploded['genre'] = df_exploded['genre'].apply(lambda x: [i.strip() for i in x])
    df_exploded = df_exploded.explode('genre', ignore_index=True)
    
    # Explode cast
    df1 = df_exploded.copy()
    # Handles comma space and comma splits
    df1['cast'] = df1['cast'].astype(str).str.split(',\\s*') 
    df1 = df1.explode('cast')
    
    df1 = df1[df1['cast'].notna()]
    df1 = df1[df1['cast'].str.strip() != '']
    
    return df_exploded, df1

# ------------------------------------------------------------
# 3. Plotting Functions (A, B, C) - Updated for Dark Theme
# ------------------------------------------------------------

def update_plot_layout_dark(fig, title_text):
    """Helper function to apply consistent dark theme styling to Plotly figures."""
    fig.update_layout(
        title={'text': title_text, 'x': 0.5, 'xanchor': 'center', 'font': {'color': NETFLIX_RED, 'size': 20}},
        height=600,
        plot_bgcolor=DARK_CARD,  # Dark background for the plotting area
        paper_bgcolor=DARK_BACKGROUND,  # Dark background for the entire figure
        font={'color': DARK_TEXT},  # Light text color
        xaxis={'tickangle': -45, 'gridcolor': DARK_BORDER, 'zerolinecolor': DARK_BORDER},
        yaxis={'gridcolor': DARK_BORDER, 'zerolinecolor': DARK_BORDER},
        legend_bgcolor=DARK_CARD,
        margin=dict(t=50)
    )
    return fig

def plot_top_cast_by_genre(df1):
    """Plot A: Top 5 Cast in Top 5 Genres Grouped Bar Chart."""
    if df1.empty or 'genre' not in df1.columns or 'cast' not in df1.columns:
        return go.Figure().add_annotation(text="Insufficient data for Plot A", showarrow=False, font={'color': DARK_TEXT})
        
    top5_genres = df1['genre'].value_counts().nlargest(5).index
    if top5_genres.empty:
        return go.Figure().add_annotation(text="Insufficient genre data for Plot A", showarrow=False, font={'color': DARK_TEXT})

    top5_cast_genre = (
        df1[df1['genre'].isin(top5_genres)]
        .groupby(['genre', 'cast']).size()
        .reset_index(name='count')
    )
    if top5_cast_genre.empty:
        return go.Figure().add_annotation(text="Insufficient cast/genre data for Plot A", showarrow=False, font={'color': DARK_TEXT})
        
    top5_cast_genre = top5_cast_genre.groupby('genre').apply(lambda x: x.nlargest(5, 'count')).reset_index(drop=True)
    
    fig = px.bar(
        top5_cast_genre, 
        x='cast', 
        y='count', 
        color='genre', 
        barmode='group',
        color_discrete_sequence=NETFLIX_REDS,
        labels={'count': 'Count of Titles', 'cast': 'Cast Member'},
    )
    return update_plot_layout_dark(fig, "Top 5 Cast Members in Each of the Top 5 Genres")

def plot_top_cast_by_country(df1):
    """Plot B: Top 3 Cast in Top 5 Countries Grouped Bar Chart."""
    if df1.empty or 'country' not in df1.columns or 'cast' not in df1.columns:
        return go.Figure().add_annotation(text="Insufficient data for Plot B", showarrow=False, font={'color': DARK_TEXT})
        
    df1['country'] = df1['country'].fillna('Missing')
    top5_countries = df1['country'].value_counts().nlargest(5).index
    
    if top5_countries.empty:
        return go.Figure().add_annotation(text="Insufficient country data for Plot B", showarrow=False, font={'color': DARK_TEXT})

    top3_cast_country = (
        df1[df1['country'].isin(top5_countries)]
        .groupby(['country', 'cast']).size()
        .reset_index(name='count')
    )
    
    if top3_cast_country.empty:
        return go.Figure().add_annotation(text="Insufficient cast/country data for Plot B", showarrow=False, font={'color': DARK_TEXT})
        
    top3_cast_country = top3_cast_country.groupby('country').apply(lambda x: x.nlargest(3, 'count')).reset_index(drop=True)

    fig = px.bar(
        top3_cast_country, 
        x='cast', 
        y='count', 
        color='country', 
        barmode='group',
        color_discrete_sequence=NETFLIX_REDS,
        labels={'count': 'Count of Titles', 'cast': 'Cast Member'},
    )
    return update_plot_layout_dark(fig, "Top 3 Cast Members in Each of the Top 5 Content-Producing Countries")

def plot_genre_distribution_by_country(df_exploded):
    """Plot C: Genre Distribution by Top 4 Countries Stacked Horizontal Bar Chart (Custom Colors)."""
    if df_exploded.empty or 'country' not in df_exploded.columns or 'genre' not in df_exploded.columns:
        return go.Figure().add_annotation(text="Insufficient data for Plot C", showarrow=False, font={'color': DARK_TEXT})

    top4_countries_genre = df_exploded['country'].value_counts().nlargest(4).index
    df_country_genre = df_exploded[df_exploded['country'].isin(top4_countries_genre)].dropna(subset=['country'])
    
    if df_country_genre.empty:
        return go.Figure().add_annotation(text="Insufficient filtered data for Plot C", showarrow=False, font={'color': DARK_TEXT})
        
    genre_country_df = df_country_genre.groupby(['country', 'genre']).size().reset_index(name='count')
    
    if genre_country_df.empty:
        return go.Figure().add_annotation(text="No genre counts available for Plot C", showarrow=False, font={'color': DARK_TEXT})

    genre_pivot = genre_country_df.pivot(index='country', columns='genre', values='count').fillna(0)
    
    total_counts = genre_pivot.sum(axis=1).sort_values(ascending=False).index
    genre_pivot = genre_pivot.loc[total_counts]

    fig = go.Figure()
    colors = CUSTOM_PLOT3_COLORS
    
    for i, genre in enumerate(genre_pivot.columns):
        fig.add_trace(go.Bar(
            y=genre_pivot.index,
            x=genre_pivot[genre],
            name=genre,
            orientation='h',
            marker_color=colors[i % len(colors)]
        ))

    fig.update_layout(
        barmode='stack',
        xaxis_title="Count of Titles (Genre)",
        yaxis_title="Country",
        legend_title="Genre",
    )
    return update_plot_layout_dark(fig, "Genre Distribution Across Top 4 Content-Producing Countries (Netflix)")

# ------------------------------------------------------------
# 4. Data Loading and Processing for IMDb Plots (D, E)
# ------------------------------------------------------------
# (IMDb data loading logic remains the same for functionality, 
# but warnings are updated for clarity in a dark theme context.)

csv_file_path = 'Plotting data/netflix_titles_with_imdb_ratings_2.csv' 
df_imdb = None
filtered_data = pd.DataFrame() # Data for Plot D
country_counts = pd.DataFrame() # Data for Plot E
imdb_data_available = False

try:
    if os.path.exists(csv_file_path):
        df_imdb = pd.read_csv(csv_file_path)
        df_imdb.columns = df_imdb.columns.str.strip().str.lower().str.replace(' ', '_')
        imdb_data_available = True
    
    if df_imdb is not None and not df_imdb.empty:
        if all(col in df_imdb.columns for col in ['cast', 'averagerating', 'country']):
            # --- Processing for Plot D and E ---
            df_imdb['cast'] = df_imdb['cast'].astype(str).str.split(', ')
            df1_imdb = df_imdb.explode('cast')
            netflix_imdb = df1_imdb.dropna(subset=['cast', 'averagerating', 'country'])

            # Plot D Logic
            cast_country_rating = (netflix_imdb.assign(actor=netflix_imdb['cast'].str.split(',')).explode('actor').dropna(subset=['actor']))
            cast_country_rating['actor'] = cast_country_rating['actor'].str.strip()
            actor_country_rating = (cast_country_rating.groupby(['country', 'actor'], as_index=False)['averagerating'].mean())
            top_actors = (actor_country_rating.groupby('actor')['averagerating'].mean().nlargest(15).index)
            filtered_data = actor_country_rating[actor_country_rating['actor'].isin(top_actors)]
            
            # Plot E Logic
            df_imdb_dist = df_imdb.copy()
            df_imdb_dist['cast'] = df_imdb_dist['cast'].astype(str).str.split(', ')
            df1_dist = df_imdb_dist.explode('cast')
            netflix_dist = df1_dist.dropna(subset=['country', 'cast'])
            df_dist = (netflix_dist.assign(actor=netflix_dist['cast'].str.split(',')).explode('actor').dropna(subset=['actor']))
            df_dist['actor'] = df_dist['actor'].str.strip()
            df_unique = df_dist.drop_duplicates(subset=['country', 'actor'])
            top_countries = df_unique['country'].value_counts().nlargest(5).index
            df_top = df_unique[df_unique['country'].isin(top_countries)]
            country_counts = df_top['country'].value_counts().reset_index()
            country_counts.columns = ['country', 'unique_actor_count']
        else:
            st.warning("IMDb file loaded, but missing one or more required columns ('cast', 'averagerating', 'country') for Plots D and E.")
            imdb_data_available = False
            
    if not imdb_data_available and not os.path.exists(csv_file_path):
        st.warning(f"⚠️ **IMDb Data Missing:** The file '{csv_file_path}' was not found. Plots D and E cannot be generated. Please place the required data file in the specified path.")
        
except Exception as e:
    st.error(f"An error occurred during IMDb file processing: {e}")
    imdb_data_available = False


# ------------------------------------------------------------
# 5. MAIN APP LAYOUT
# ------------------------------------------------------------

# Load the main dataset for the Search & Plots A, B, C
df = load_main_data()
if df.empty:
    st.error("Cannot proceed without the main Netflix dataset.")
    st.stop()

# Prepare data for Plots A, B, C
df_exploded, df1 = prepare_genre_cast_data(df)


# --- Apply Custom CSS (Updated for Dark Theme) ---
st.markdown(f"""
    <style>
   
        /* Global App Background - Dark Theme */
        .stApp {{
            background-color: {DARK_BACKGROUND};
        }}
        
        /* Ensures the wide layout is used effectively */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 5rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }}
        /* General text color for all standard markdown/text */
        * {{
            color: {DARK_TEXT};
        }}

        /* --- Custom Title/Header Styling (Prominent Red) --- */
        h1 {{
            color: {NETFLIX_RED}; 
            text-align: center;
            font-size: 2.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {DARK_BORDER};
            margin-bottom: 2rem;
            font-weight: 700;
        }}
        
        h2 {{ 
            color: {NETFLIX_RED}; 
            text-align: left;
            font-size: 2rem;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            border-left: 5px solid {NETFLIX_RED};
            padding-left: 15px;
        }}
        h3 {{
            color: {NETFLIX_RED}; 
            font-size: 1.5rem;
            text-align: center;
            border-left: none;
            padding-left: 0;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        /* --- Styled DataFrame Container (Dark Card Look) --- */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {DARK_BORDER}; 
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
            background-color: {DARK_CARD};
            margin-bottom: 3rem;
            transition: box-shadow 0.3s;
        }}
        /* Dataframe cell/text colors */
        div[data-testid="stDataFrame"] .row-header-content,
        div[data-testid="stDataFrame"] .col-header-content {{
            color: {DARK_TEXT} !important;
        }}
        div[data-testid="stDataFrame"] table tbody tr td:nth-child(even) {{
            background-color: {DARK_CARD}; /* Keep even rows dark */
        }}
        
        /* --- Custom Info Card (Dark style for metrics) --- */
        .info-card {{
            background-color: {DARK_CARD};
            border: 1px solid {NETFLIX_RED}; 
            border-radius: 10px; 
            padding: 15px 25px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            margin-bottom: 1.5rem;
            text-align: center;
            height: 100px;
        }}
        .info-card h4 {{
            color: {DARK_TEXT};
            font-size: 1.1rem;
            margin-bottom: 0.2rem;
            text-align: center;
        }}
        .info-card p {{
            color: {NETFLIX_RED}; 
            font-size: 2.5rem; 
            font-weight: bold;
        }}
        
        /* Styling for st.info and st.warning to stand out on dark background */
        .stAlert {{
            background-color: #333333;
            border-left: 5px solid {NETFLIX_RED};
            color: {DARK_TEXT};
        }}
        
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: red;'>Director and Cast Content Search</h1>", unsafe_allow_html=True)

# ----------------------------------------------
# Director Search Section
# ----------------------------------------------
st.header(" Director Search")


directors = df['director'].dropna().unique()
directors = sorted(directors)

col_s1, col_sc, col_s2 = st.columns([1, 4, 1])
with col_sc:
    # Streamlit's selectbox will automatically adapt to the dark theme setting
    selected_director = st.selectbox("Select a Director", directors, key="dir_select")

filtered_df = df[df['director'] == selected_director]

# Display simple metric for director's work



st.dataframe(
    filtered_df[['title', 'type', 'release_year', 'country', 'listed_in']].reset_index(drop=True),
    use_container_width=True
)

st.markdown("---")

# ----------------------------------------------
# Cast Search Section
# ----------------------------------------------

st.header(" Cast Search")

actors = (
    df['cast']
    .dropna()
    .apply(lambda x: [a.strip() for a in x.split(',')])
    .explode()
    .unique()
)
cast = sorted(actors)

col_s3, col_sc2, col_s4 = st.columns([1, 4, 1])
with col_sc2:
    selected_cast = st.selectbox("Select a Cast Member", cast, key="cast_select")

filtered_cast_df = df[df['cast'].fillna("").str.contains(selected_cast, case=False, na=False)]

# Display simple metric for cast member's work


st.dataframe(
    filtered_cast_df[['title', 'type', 'release_year', 'country', 'listed_in']].reset_index(drop=True),
    use_container_width=True
)

st.markdown("---")

# ----------------------------------------------
# Content and Talent Analysis
# ----------------------------------------------
st.markdown("<h1 style='text-align: center; color: red;'>Content and Talent Analysis</h1>", unsafe_allow_html=True)

# --- ROW 1: Plots A and B ---
col_A, col_B = st.columns(2)

# Plot A: Top 5 Cast by Top 5 Genres
with col_A:
    
    if not df1.empty and 'genre' in df1.columns:
        fig1 = plot_top_cast_by_genre(df1)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Data unavailable to generate Plot A.")

# Plot B: Top 3 Cast by Top 5 Content-Producing Countries
with col_B:
    
    if not df1.empty and 'country' in df1.columns:
        fig2 = plot_top_cast_by_country(df1)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Data unavailable to generate Plot B.")

st.markdown("---")

# ----------------------------------------------
# IMDb-Based Insights (Plots D and E)
# ----------------------------------------------
st.header("IMDb-Based Insights ")

# Plot D: IMDb Rating by Actor and Country
col_D, col_E = st.columns(2)

with col_D:
   
    if imdb_data_available and not filtered_data.empty:
        fig4 = px.bar(
            filtered_data,
            x='actor',
            y='averagerating', 
            color='country',
            color_discrete_sequence=['#FF4500', '#B01717', '#800000', '#FFD700', '#A52A2A'], # Use a subset of dark-friendly reds/browns
        )
        fig4 = update_plot_layout_dark(fig4, 'IMDb Rating by Actor and Country')

        # Adjust y-axis range if data is valid
        if pd.api.types.is_numeric_dtype(filtered_data['averagerating']) and filtered_data['averagerating'].any():
            fig4.update_yaxes(range=[
                filtered_data['averagerating'].min() * 0.95, 
                filtered_data['averagerating'].max() * 1.05 
            ])
        fig4.update_traces(marker_line_color=DARK_TEXT, marker_line_width=0.8)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("IMDb rating data is missing or failed to load. Cannot generate IMDb Rating Plot.")


with col_E:
    
    if imdb_data_available and not country_counts.empty:
        fig5 = px.bar(
            country_counts,
            x='country',
            y='unique_actor_count',
            color='unique_actor_count',
            color_continuous_scale=['#FFD700', '#FFA500', '#FF4500', NETFLIX_RED, '#B01717'], # Dark-friendly color scale
        )

        fig5 = update_plot_layout_dark(fig5, 'Unique Cast Actors in Top 5 Countries')
        fig5.update_layout(coloraxis_colorbar=dict(
            title='Actor Count',
            tickcolor=DARK_TEXT,
            tickfont=dict(color=DARK_TEXT)
        ))

        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Actor distribution data is missing or failed to load. Cannot generate Actor Distribution Plot.")

st.markdown("---")

# ----------------------------------------------
# Genre Distribution (Plot C - Full Width)
# ----------------------------------------------

st.header("Comprehensive Content Analysis: Genre Distribution")

# Plot C: Genre Distribution Across Top 4 Countries (Custom Colors)
if not df_exploded.empty and 'genre' in df_exploded.columns:
    fig3 = plot_genre_distribution_by_country(df_exploded)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Data unavailable to generate the Genre Distribution Plot.")
