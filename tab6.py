import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import kagglehub

# --- 1. Configuration (MUST be the first command) ---
st.set_page_config(layout="wide", page_title="Netflix Comprehensive Dashboard")

# Define colors for consistent styling where applicable
NETFLIX_REDS = ["#F28C8C", "#D82E2F", "#B01717", "#800000", "#400000"]
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
    '#800000'  # Maroon
]

# ------------------------------------------------------------
# 2. Data Loading and Preparation Functions
# ------------------------------------------------------------

@st.cache_data
def load_main_data():
    """Downloads and loads the Netflix dataset (used for search and plots A, B, C)."""
    # Assuming 'netflix_df' is populated by the navigation script
    if 'netflix_df' in st.session_state:
        return st.session_state['netflix_df'].copy()
    
    # Fallback/First time load logic (same as original code)
    try:
        data_path = "netflix_titles.csv"
        if not os.path.exists(data_path):
            with st.spinner("Downloading Netflix dataset via KaggleHub..."):
                path = kagglehub.dataset_download("shivamb/netflix-shows")
                data_path = f"{path}/netflix_titles.csv"
        return pd.read_csv(data_path)
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
    df_exploded['genre'] = df_exploded['listed_in'].str.split(',')
    df_exploded['genre'] = df_exploded['genre'].apply(lambda x: [i.strip() for i in x])
    df_exploded = df_exploded.explode('genre', ignore_index=True)
    
    df1 = df_exploded.copy()
    df1['cast'] = df1['cast'].str.split(',\\s*')
    df1 = df1.explode('cast')
    
    df1 = df1[df1['cast'].notna()]
    df1 = df1[df1['cast'].str.strip() != '']
    
    return df_exploded, df1

# ------------------------------------------------------------
# 3. Plotting Functions (A, B, C)
# ------------------------------------------------------------

def plot_top_cast_by_genre(df1):
    """Plot A: Top 5 Cast in Top 5 Genres Grouped Bar Chart."""
    top5_genres = df1['genre'].value_counts().nlargest(5).index
    top5_cast_genre = (
        df1[df1['genre'].isin(top5_genres)]
        .groupby(['genre', 'cast']).size()
        .reset_index(name='count')
    )
    top5_cast_genre = top5_cast_genre.groupby('genre').apply(lambda x: x.nlargest(5, 'count')).reset_index(drop=True)
    
    fig = px.bar(
        top5_cast_genre, 
        x='cast', 
        y='count', 
        color='genre', 
        barmode='group',
        color_discrete_sequence=NETFLIX_REDS,
        labels={'count': 'Count of Titles', 'cast': 'Cast Member'},
        title="Top 5 Cast Members in Each of the Top 5 Genres"
    )
    fig.update_layout(xaxis_tickangle=-45, height=600, plot_bgcolor='white')
    return fig

def plot_top_cast_by_country(df1):
    """Plot B: Top 3 Cast in Top 5 Countries Grouped Bar Chart."""
    df1['country'] = df1['country'].fillna('Missing')
    top5_countries = df1['country'].value_counts().nlargest(5).index
    top3_cast_country = (
        df1[df1['country'].isin(top5_countries)]
        .groupby(['country', 'cast']).size()
        .reset_index(name='count')
    )
    top3_cast_country = top3_cast_country.groupby('country').apply(lambda x: x.nlargest(3, 'count')).reset_index(drop=True)

    fig = px.bar(
        top3_cast_country, 
        x='cast', 
        y='count', 
        color='country', 
        barmode='group',
        color_discrete_sequence=NETFLIX_REDS,
        labels={'count': 'Count of Titles', 'cast': 'Cast Member'},
        title="Top 3 Cast Members in Each of the Top 5 Content-Producing Countries"
    )
    fig.update_layout(xaxis_tickangle=-45, height=600, plot_bgcolor='white')
    return fig

def plot_genre_distribution_by_country(df_exploded):
    """Plot C: Genre Distribution by Top 4 Countries Stacked Horizontal Bar Chart (Custom Colors)."""
    top4_countries_genre = df_exploded['country'].value_counts().nlargest(4).index
    df_country_genre = df_exploded[df_exploded['country'].isin(top4_countries_genre)].dropna(subset=['country'])
    
    genre_country_df = df_country_genre.groupby(['country', 'genre']).size().reset_index(name='count')
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
        title="Genre Distribution Across Top 4 Content-Producing Countries (Netflix)",
        xaxis_title="Count of Titles (Genre)",
        yaxis_title="Country",
        legend_title="Genre",
        height=600,
        plot_bgcolor='white'
    )
    return fig

# ------------------------------------------------------------
# 4. Data Loading and Processing for IMDb Plots (D, E)
# ------------------------------------------------------------

csv_file_path = 'Plotting data/netflix_titles_with_imdb_ratings_2.csv'
df_imdb = None
filtered_data = pd.DataFrame() # Data for Plot D
country_counts = pd.DataFrame() # Data for Plot E

try:
    if os.path.exists(csv_file_path):
        df_imdb = pd.read_csv(csv_file_path)
    else:
        st.error(f"Error: The file '{csv_file_path}' was not found. Plots 4 and 5 cannot be generated.")
        
    if df_imdb is not None and not df_imdb.empty:
        # --- Processing for Plot D (IMDb Rating by Actor and Country) ---
        df_imdb['cast'] = df_imdb['cast'].astype(str).str.split(', ')
        df1_imdb = df_imdb.explode('cast')
        netflix_imdb = df1_imdb.dropna(subset=['cast', 'averageRating', 'country'])

        cast_country_rating = (
            netflix_imdb.assign(actor=netflix_imdb['cast'].str.split(','))
            .explode('actor')
            .dropna(subset=['actor'])
        )
        cast_country_rating['actor'] = cast_country_rating['actor'].str.strip()

        actor_country_rating = (
            cast_country_rating
            .groupby(['country', 'actor'], as_index=False)['averageRating']
            .mean()
        )
        top_actors = (
            actor_country_rating.groupby('actor')['averageRating']
            .mean()
            .nlargest(15)
            .index
        )
        filtered_data = actor_country_rating[actor_country_rating['actor'].isin(top_actors)]
        
        # --- Processing for Plot E (Actor Distribution) ---
        df_imdb_dist = df_imdb.copy()
        df_imdb_dist['cast'] = df_imdb_dist['cast'].astype(str).str.split(', ')
        df1_dist = df_imdb_dist.explode('cast')
        
        netflix_dist = df1_dist.dropna(subset=['country', 'cast'])

        df_dist = (
            netflix_dist.assign(actor=netflix_dist['cast'].str.split(','))
            .explode('actor')
            .dropna(subset=['actor'])
        )
        df_dist['actor'] = df_dist['actor'].str.strip()

        df_unique = df_dist.drop_duplicates(subset=['country', 'actor'])
        top_countries = df_unique['country'].value_counts().nlargest(5).index
        df_top = df_unique[df_unique['country'].isin(top_countries)]
        
        country_counts = df_top['country'].value_counts().reset_index()
        country_counts.columns = ['country', 'unique_actor_count']

except Exception as e:
    st.error(f"An error occurred during IMDb file processing: {e}")


# ------------------------------------------------------------
# 5. MAIN APP LAYOUT
# ------------------------------------------------------------

# Load the main dataset for the Search & Plots A, B, C
df = load_main_data()
if df.empty:
    st.stop()

# Prepare data for Plots A, B, C
df_exploded, df1 = prepare_genre_cast_data(df)


# --- Apply Custom CSS (Ensures ALL headers are RED) ---
st.markdown("""
    <style>
        /* Global App Background - Light Theme */
        .stApp {
            background-color: #F8F8F8;
        }
        
        /* Ensures the wide layout is used effectively */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }

        /* --- Custom Title/Header Styling (Prominent Red) --- */
        h1 {
            color: #E50914; /* Netflix Red: Used by st.title() */
            text-align: center;
            font-size: 2.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #EEEEEE;
            margin-bottom: 2rem;
            font-weight: 700;
        }
        
        /* Ensures h2 (st.header) and h3 (st.subheader) are also red */
        h2 { 
            color: #E50914; /* Netflix Red: Used by st.header() */
            text-align: left;
            font-size: 2rem;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            border-left: 5px solid #E50914;
            padding-left: 15px;
        }
        h3 {
            color: #E50914; /* Netflix Red: Used by st.subheader() */
            font-size: 1.5rem;
            text-align: center; /* Center h3 for plot titles */
            border-left: none;
            padding-left: 0;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* --- Styled Selectbox Container --- */
        div[data-testid="stSelectbox"] {
            margin-bottom: 1.5rem;
            max-width: 600px;
        }

        /* --- Styled DataFrame Container (Card Look) --- */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E0E0E0; 
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
            background-color: white;
            margin-bottom: 3rem;
            transition: box-shadow 0.3s;
        }
        div[data-testid="stDataFrame"] .col-header {
            background-color: #F5F5F5;
            color: #333333;
            font-weight: 600;
        }
        div[data-testid="stDataFrame"] table tbody tr:nth-child(even) {
            background-color: #FAFAFA;
        }

        /* --- Custom Info Card (for quick stats) --- */
        .info-card {
            background-color: #FFFFFF;
            border: 1px solid #E50914; 
            border-radius: 10px; 
            padding: 15px 25px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            text-align: center;
            height: 100px;
        }
        .info-card h4 {
            color: #333333;
            font-size: 1.1rem;
            margin-bottom: 0.2rem;
            text-align: center;
        }
        .info-card p {
            color: #E50914; 
            font-size: 2.5rem; 
            font-weight: bold;
        }
        
    </style>
""", unsafe_allow_html=True)


st.title("Director and Cast Content Search")

# ----------------------------------------------
# Director Search Section
# ----------------------------------------------
st.header("Director Search")

directors = df['director'].dropna().unique()
directors = sorted(directors)

col_s1, col_sc, col_s2 = st.columns([1, 4, 1])
with col_sc:
    selected_director = st.selectbox("Select a Director", directors, key="dir_select")

filtered_df = df[df['director'] == selected_director]

col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
with col_c2:
    total_titles = len(filtered_df)


st.dataframe(
    filtered_df[['title', 'type', 'release_year', 'country', 'listed_in']].reset_index(drop=True),
    use_container_width=True
)

st.markdown("---")

# ----------------------------------------------
# Cast Search Section
# ----------------------------------------------
st.header("Cast Search")

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

filtered_cast_df = df[df['cast'].fillna("").str.contains(selected_cast, case=False)]

col_c4, col_c5, col_c6 = st.columns([1, 2, 1])
with col_c5:
    total_titles_cast = len(filtered_cast_df)
   

st.dataframe(
    filtered_cast_df[['title', 'type', 'release_year', 'country', 'listed_in']].reset_index(drop=True),
    use_container_width=True
)

st.markdown("---")

# ----------------------------------------------
# PLOT SECTION: 2x2 Grid (A, B, D, E) + 1 Full Width (C)
# ----------------------------------------------

st.title("Content and Talent Analysis")

# --- ROW 1: Plots A and B ---
col_A, col_B = st.columns(2)

# Plot A: Top 5 Cast by Top 5 Genres
with col_A:
    st.subheader("Top 5 Cast by Top 5 Genres")
    if not df1.empty:
        fig1 = plot_top_cast_by_genre(df1)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Data unavailable to generate Plot A.")

# Plot B: Top 3 Cast by Top 5 Content-Producing Countries
with col_B:
    st.subheader("Top 3 Cast by Top 5 Content Countries")
    if not df1.empty:
        fig2 = plot_top_cast_by_country(df1)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Data unavailable to generate Plot B.")

st.markdown("---")

# --- ROW 2: Plots D and E ---
# Plot D: IMDb Rating by Actor and Country
# Plot E: Cast Actors in Top 5 Countries (Actor Distribution)
col_D, col_E = st.columns(2)

with col_D:
    st.subheader("IMDb Rating by Actor and Country")
    if not filtered_data.empty:
        fig4 = px.bar(
            filtered_data,
            x='actor',
            y='averageRating',
            color='country',
            title='IMDb Rating by Actor and Country',
            color_discrete_sequence=['#330000', '#660000', '#990000', '#cc0000', '#ff1a1a']
        )
        fig4.update_layout(
            xaxis_title='Actor',
            yaxis_title='Average IMDb Rating',
            xaxis_tickangle=-45,
            template='plotly_white',
            font=dict(color='#221f1f', size=14),
            title_font=dict(size=20, color='#e50914', family='Arial Black'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend_title_text='Country',
        )
        fig4.update_yaxes(range=[9, 10])
        fig4.update_traces(marker_line_color='#221f1f', marker_line_width=0.8)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("IMDb rating data is missing or failed to load. Cannot generate IMDb Rating Plot.")


with col_E:
    st.subheader("Actor Distribution Across Top 5 Countries")
    if not country_counts.empty:
        fig5 = px.bar(
            country_counts,
            x='country',
            y='unique_actor_count',
            color='unique_actor_count',
            color_continuous_scale=['#330000', '#660000', '#990000', '#cc0000', '#ff1a1a'],
            title='Cast Actors in Top 5 Countries'
        )

        fig5.update_layout(
            xaxis_title='Country',
            yaxis_title='Number of Unique Actors',
            template='plotly_white',
            font=dict(color='#221f1f', size=14),
            title_font=dict(size=20, color='#e50914', family='Arial Black'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_colorbar=dict(
                title='Actor Count',
                tickcolor='#221f1f',
                tickfont=dict(color='#221f1f')
            )
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Actor distribution data is missing or failed to load. Cannot generate Actor Distribution Plot.")

st.markdown("---")

# --- ROW 3: Plot C (Full Width) ---

st.header("Comprehensive Content Analysis")
st.subheader("Genre Distribution Across Top 4 Content-Producing Countries (Custom Colors)")

# Plot C: Genre Distribution Across Top 4 Countries (Custom Colors)
if not df_exploded.empty:
    fig3 = plot_genre_distribution_by_country(df_exploded)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Data unavailable to generate the Genre Distribution Plot.")