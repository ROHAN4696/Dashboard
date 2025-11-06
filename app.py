import streamlit as st
import pandas as pd
import kagglehub
import os

# --- 1. Custom CSS for Collapsible Sidebar (Removed Icons, Enhanced Hiding) ---
st.markdown(
    """
    <style>
    /* 1. Base Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6; 
        transition: width 0.3s ease;
        overflow-x: hidden;
    }

    /* 2. Narrow sidebar by default */
    [data-testid="stSidebar"] {
        width: 70px !important;
        /* CRITICAL: Ensure no padding forces text to peek out */
        padding-left: 0 !important; 
        padding-right: 0 !important;
    }

    /* 3. Expand sidebar on hover */
    [data-testid="stSidebar"]:hover {
        width: 250px !important;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }

    /* 4. Target the text container (p) and hide it */
    .st-emotion-cache-p2p2k0 a p {
        /* CRITICAL: Use clip-path to physically cut off the text area */
        clip-path: polygon(0 0, 0 0, 0 100%, 0% 100%); 
        opacity: 0;
        transition: clip-path 0.3s ease, opacity 0.3s ease, margin 0.3s ease;
        margin-left: -50px !important; /* Force shift left */
        white-space: nowrap; 
    }

    /* 5. Target the icon container (span or svg) to center it in the narrow bar */
    .st-emotion-cache-p2p2k0 a span, 
    .st-emotion-cache-p2p2k0 a svg {
        min-width: 20px; 
        margin-right: 15px; /* Space between icon and edge */
    }
    
    /* 6. Show text on sidebar hover */
    [data-testid="stSidebar"]:hover .st-emotion-cache-p2p2k0 a p {
        clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%); /* Expand clipping */
        opacity: 1;
        margin-left: 10px !important; /* Move text to the right of the icon */
    }

    /* 7. Align link content for proper centered/left alignment */
    .st-emotion-cache-p2p2k0 a { 
        display: flex;
        align-items: center;
        padding: 10px 0px 10px 15px !important; 
        justify-content: flex-start; /* Keep icons aligned left even when narrow */
        overflow: hidden; /* Ensure nothing leaks out */
    }

    /* Remove the default scrollbar when collapsed */
    [data-testid="stSidebar"]::before {
        content: "";
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    """Loads Netflix data from KaggleHub."""
    # NOTE: This function requires 'kagglehub' and a working Kaggle token setup 
    # if running outside of a compatible environment.
    try:
        path = kagglehub.dataset_download("shivamb/netflix-shows")
        df = pd.read_csv(f"{path}/netflix_titles.csv")
        return df
    except Exception as e:
        st.error(f"Could not load data from KaggleHub: {e}. Returning empty DataFrame.")
        # Create a dummy DataFrame if loading fails to prevent further errors
        return pd.DataFrame({'show_id': [], 'title': [], 'type': []})

df = load_data()

# Store data in session state for access across pages
st.session_state["netflix_df"] = df

# --- 2. Define Pages (ICONS REMOVED AS REQUESTED) ---
# NOTE: The custom CSS will still display a default icon if none is provided, 
# but the text will remain hidden until hover.
pages = [
    st.Page("./tab1.py", title="Executive Overview"),
    st.Page("./tab2.py", title="Content Explorer"),
    st.Page("./tab3.py", title="Trend Intelligence"),
    st.Page("./tab4.py", title="Geographic Insights"),
    st.Page("./tab5.py", title="Genre and Category Intelligence"),
    st.Page("./tab6.py", title="Creator & Talent Hub"),
    st.Page("./tab7.py", title="Strategic Recommendations"),
]

# --- 3. Run Navigation ---
nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()