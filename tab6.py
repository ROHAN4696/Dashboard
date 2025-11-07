import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os 

# --- 1. Configuration (MUST be the first command) ---
st.set_page_config(layout="wide") 

# Assuming 'netflix_df' is correctly populated in st.session_state
if 'netflix_df' not in st.session_state:
    st.error("Error: DataFrame 'netflix_df' not found in session state.")
    st.stop()

df = st.session_state['netflix_df'].copy()

# --- 2. Custom CSS for Light Theme Aesthetics and DataFrames ---
st.markdown("""
    <style>
        /* Global App Background - Light Theme */
        .stApp {
            background-color: #F8F8F8; /* Very subtle light grey */
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
            color: #E50914; /* Netflix Red */
            text-align: center;
            font-size: 2.8rem; /* Slightly larger */
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #EEEEEE;
            margin-bottom: 2rem;
            font-weight: 700;
        }
        h2 {
            color: #E50914; /* Red for secondary headers (like "Cast Search") */
            text-align: left;
            font-size: 2rem;
            margin-top: 2rem;
            margin-bottom: 1.5rem;
            border-left: 5px solid #E50914;
            padding-left: 15px;
        }
        
        /* --- Styled Selectbox Container --- */
        div[data-testid="stSelectbox"] {
            margin-bottom: 1.5rem;
            /* Wider selectbox for wide layout */
            max-width: 600px;
        }

        /* --- Styled DataFrame Container (Card Look) --- */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E0E0E0; /* Lighter border */
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05); /* Softer, wider shadow */
            background-color: white;
            margin-bottom: 3rem;
            transition: box-shadow 0.3s;
        }
        div[data-testid="stDataFrame"]:hover {
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }
        /* Style for the table headers inside the dataframe */
        div[data-testid="stDataFrame"] .col-header {
            background-color: #F5F5F5; /* Very light grey header */
            color: #333333;
            font-weight: 600;
        }
        /* Style for the table cells (alternating row color for readability) */
        div[data-testid="stDataFrame"] table tbody tr:nth-child(even) {
            background-color: #FAFAFA;
        }

        /* --- Custom Info Card (for quick stats) --- */
        .info-card {
            background-color: #FFFFFF;
            border: 1px solid #E50914; /* Red outline */
            border-radius: 10px; 
            padding: 15px 25px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            text-align: center;
            height: 100px; /* Uniform height for better alignment */
        }
        /* FIX: Ensure h4 text is smaller and centered for cleaner look */
        .info-card h4 {
            color: #333333;
            font-size: 1.1rem;
            margin-bottom: 0.2rem;
            text-align: center;
        }
        .info-card p {
            color: #E50914; /* Red color for the count */
            font-size: 2.5rem; /* Larger count */
            font-weight: bold;
        }
        
    </style>
""", unsafe_allow_html=True)

# --- 3. Director Search Section ---
st.title("Director Search")

directors = df['director'].dropna().unique()
directors = sorted(directors)

# Center the selectbox using columns
col_s1, col_sc, col_s2 = st.columns([1, 4, 1])
with col_sc:
    selected_director = st.selectbox("Select a Director", directors, key="dir_select")

filtered_df = df[df['director'] == selected_director]

# Display Summary Card (Use columns to place it neatly below the selectbox)
col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
with col_c2:
    total_titles = len(filtered_df)
    

# Display Dataframe (NO explicit subheader here)
st.dataframe(
    filtered_df[['title', 'type', 'release_year', 'country', 'listed_in']].reset_index(drop=True),
    use_container_width=True
)

# --- Horizontal Separator ---
st.markdown("---")


# --- 4. Cast Search Section ---
st.title("Cast Search")

# Prepare unique list of actors
actors = (
    df['cast']
    .dropna()
    .apply(lambda x: [a.strip() for a in x.split(',')])
    .explode()
    .unique()
)
cast = sorted(actors)

# Center the selectbox using columns
col_s3, col_sc2, col_s4 = st.columns([1, 4, 1])
with col_sc2:
    selected_cast = st.selectbox("Select a Cast Member", cast, key="cast_select")

# Filter logic
filtered_cast_df = df[df['cast'].fillna("").str.contains(selected_cast, case=False)]

# Display Summary Card
col_c4, col_c5, col_c6 = st.columns([1, 2, 1])
with col_c5:
    total_titles_cast = len(filtered_cast_df)
    
 

# Display Dataframe (NO explicit subheader here)
st.dataframe(
    filtered_cast_df[['title', 'type', 'release_year', 'country', 'listed_in']].reset_index(drop=True),
    use_container_width=True
)

