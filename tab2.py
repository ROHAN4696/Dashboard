import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os # Import os for better path handling

# --- Configuration & Setup ---
st.set_page_config(layout="wide")
st.markdown("""
    <style>
        /* FIX: Ensure titles and headings are red and centered using !important */
        h1, h2, h4, h5, h6 {
            text-align: center;
            color: #FF0000 !important; /* Enforce Red color */
        }

        /* Style for the main block container to maintain layout */
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 2rem;
            max-width: 100%;
            margin-top:0rem;
        }

        /* Style for all headings except Netflix Dataset Viewer */
        h3, h4, h5, h6 {
            width: 100% !important;
            text-align: center !important;
            border-bottom: 1px solid #333333;
            padding-bottom: 15px;
        }

        /* Style specifically for Netflix Dataset Viewer */
        h1 {
            text-align: center !important;
        }
        
        /* Style for plotly charts */
        .js-plotly-plot {
            background-color: black !important;
        }

        /* Style for the Data Preview container (st.dataframe) with rounded corners */
        div[data-testid="stDataFrame"] {
            border: 1px solid #ddd; /* Subtle border */
            border-radius: 10px; /* Rounded corners */
            padding: 10px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); /* Subtle shadow */
        }

        /* BUTTON STYLING: Make all Streamlit buttons (like Reset Filters) red with white text */
        div[data-testid="stButton"] button {
            /* General button size adjustment (from previous version) */
            padding: 0.45rem 0.85rem; 
            
            /* BASE STYLES for Button */
            background-color: #FF0000; /* Red Background */
            color: white !important; /* White Text (using !important for certainty) */
            border-color: #FF0000; /* Red Border */
            transition: background-color 0.3s; /* Smooth transition for hover effect */
        }
        
        /* NEW: Hover effect for Reset Button (Light Red/Orangish) */
        div[data-testid="stButton"] button:hover {
            background-color: #FF7F50; /* Coral/Light Orangish Red */
            border-color: #FF7F50;
            color: white !important;
        }

        /* Optional: Make selectboxes fill the available column width */
        div[data-testid="stSelectbox"] > div {
            width: 100% !important;
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

st.title(" Netflix Dataset Viewer")

# --- Load DataFrame Safely ---
# Use the uploaded file name to load the data if not already in session state
FILE_ID = "netflix_titles.csv"
if 'netflix_df' not in st.session_state:
    try:
        # Load the uploaded CSV file
        df = pd.read_csv(FILE_ID)
        st.session_state['netflix_df'] = df
    except FileNotFoundError:
        st.error(f"Error: Could not find the file '{FILE_ID}'. Please ensure it is uploaded.")
        st.stop() # Stop execution if the file is not found
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()

# Assign the DataFrame from session state for use in the rest of the script
df = st.session_state['netflix_df'].copy() # Use .copy() to avoid SettingWithCopyWarning

# --- Normalize column names ---
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# --- derive year column (prefer release_year else parse date_added) ---
if 'release_year' in df.columns:
    df['year'] = df['release_year']
elif 'date_added' in df.columns:
    # Ensure date_added is treated as a string before using .str.split()
    df['date_added'] = df['date_added'].astype(str)
    # The original code used pd.to_datetime, which is better:
    df['year'] = pd.to_datetime(df['date_added'], errors='coerce').dt.year
else:
    df['year'] = None

# --- Prepare options for widgets ---
show_types = sorted(df['type'].dropna().unique().tolist())
ratings = sorted(df['rating'].dropna().unique().tolist())
# Safely convert years to int and filter out NaNs (which can happen if date_added or release_year is missing/invalid)
years = sorted([int(y) for y in df['year'].dropna().unique().tolist() if not pd.isna(y)], reverse=True)
titles = sorted(df['title'].dropna().unique().tolist())
directors = sorted(df['director'].dropna().unique().tolist())

# split cast into individual names
cast_names = []
if 'cast' in df.columns:
    cast_series = df['cast'].dropna().astype(str).str.split(',')
    cast_flat = [actor.strip() for sub in cast_series for actor in sub if isinstance(sub, list)]
    cast_names = sorted(set([c for c in cast_flat if c]))

# --- WIDGET KEYS & session_state defaults ---
WIDGET_KEYS = {
    "type": "filter_type",
    "rating": "filter_rating",
    "year": "filter_year",
    "title": "filter_title",
    "cast": "filter_cast",
    "director": "filter_director",
}

for k in WIDGET_KEYS.values():
    if k not in st.session_state:
        st.session_state[k] = "All"

# --- Reset callback (safe: modifies session_state via callback) ---
def reset_filters():
    for k in WIDGET_KEYS.values():
        st.session_state[k] = "All"
    # st.experimental_rerun() is often not needed just for changing state values

# --- Layout: two rows, six columns (2 columns per filter) ---
st.markdown("###  Search & Filter")
col1, col2, col3 = st.columns(3)

# Helper: safe index chooser (returns 0 if not found)
def safe_index(options, desired):
    try:
        return options.index(desired)
    except Exception:
        return 0

# making the selectbox to filter
with col1:
    opts = ["All"] + show_types
    st.selectbox(
        "Type",
        options=opts,
        index=safe_index(opts, st.session_state[WIDGET_KEYS["type"]]),
        key=WIDGET_KEYS["type"],
    )
with col2:
    opts = ["All"] + ratings
    st.selectbox(
        "Rating",
        options=opts,
        index=safe_index(opts, st.session_state[WIDGET_KEYS["rating"]]),
        key=WIDGET_KEYS["rating"],
    )
with col3:
    year_opts = ["All"] + [str(y) for y in years]
    st.selectbox(
        "Year Released",
        options=year_opts,
        index=safe_index(year_opts, st.session_state[WIDGET_KEYS["year"]]),
        key=WIDGET_KEYS["year"],
    )

#making selectbox (second row)     
col1b, col2b, col3b= st.columns(3)

with col1b:
    opts = ["All"] + titles
    st.selectbox(
        "Title",
        options=opts,
        index=safe_index(opts, st.session_state[WIDGET_KEYS["title"]]),
        key=WIDGET_KEYS["title"],
    )
with col2b:
    opts = ["All"] + cast_names
    st.selectbox(
        "Cast Member",
        options=opts,
        index=safe_index(opts, st.session_state[WIDGET_KEYS["cast"]]),
        key=WIDGET_KEYS["cast"],
    )
with col3b:
    opts = ["All"] + directors
    st.selectbox(
        "Director",
        options=opts,
        index=safe_index(opts, st.session_state[WIDGET_KEYS["director"]]),
        key=WIDGET_KEYS["director"],
    )

# --- Reset button (safe) ---
st.markdown("---")
st.button(" Reset Filters", on_click=reset_filters)

# --- Apply filters to dataframe ---
filtered_df = df.copy()

if st.session_state[WIDGET_KEYS["type"]] != "All":
    filtered_df = filtered_df[filtered_df['type'] == st.session_state[WIDGET_KEYS["type"]]]

if st.session_state[WIDGET_KEYS["rating"]] != "All":
    filtered_df = filtered_df[filtered_df['rating'] == st.session_state[WIDGET_KEYS["rating"]]]

if st.session_state[WIDGET_KEYS["year"]] != "All":
    try:
        yval = int(st.session_state[WIDGET_KEYS["year"]])
        # Filter where 'year' is not null AND equals the selected year
        filtered_df = filtered_df[filtered_df['year'].notna() & (filtered_df['year'] == yval)]
    except Exception:
        pass

if st.session_state[WIDGET_KEYS["title"]] != "All":
    # Use exact match for titles when a specific title is selected for clarity
    filtered_df = filtered_df[filtered_df['title'].astype(str) == st.session_state[WIDGET_KEYS["title"]]]


if st.session_state[WIDGET_KEYS["cast"]] != "All" and 'cast' in filtered_df.columns:
    # Ensure 'cast' is string type and handle NaNs before using str.contains
    cast_filter = st.session_state[WIDGET_KEYS["cast"]]
    filtered_df = filtered_df[filtered_df['cast'].astype(str).str.contains(cast_filter, case=False, na=False)]


if st.session_state[WIDGET_KEYS["director"]] != "All":
    # Ensure 'director' is string type and handle NaNs before using str.contains
    director_filter = st.session_state[WIDGET_KEYS["director"]]
    filtered_df = filtered_df[filtered_df['director'].astype(str).str.contains(director_filter, case=False, na=False)]

# --- Show results ---
st.markdown(f"###  Results ({len(filtered_df)} records)")
st.dataframe(filtered_df.reset_index(drop=True))