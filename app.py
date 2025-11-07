import streamlit as st
import pandas as pd
import kagglehub
import os

st.markdown("""
<style>

/* --- 1. CORE SIDEBAR BEHAVIOR & POSITION (FINAL FIXES) --- */

[data-testid="stSidebar"] {
    position: fixed !important;
    left: 0 !important;
    top: 60px !important; /* FIXED: Starts 60px from the top */
    
    /* Height Fix: Shorter, content-fit height */
    height: fit-content !important; 
    max-height: 80vh; /* ADJUSTED: Reduced max height to 80vh for a shorter look */

    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;

    /* Styling: Red Background, Rounded Corners */
    background-color: #000000 !important;
    border-radius: 15px !important;
    border: none;
    
    /* Hover/Expand Logic */
    transform: translateX(-260px) !important;
    transition: transform 0.65s cubic-bezier(.16, 1, .3, 1), box-shadow 0.5s ease;
    z-index: 9999 !important;
    padding: 0 !important;
    overflow-x: hidden !important;
    overflow-y: hidden; /* Prevents scrollbar inside sidebar */
}

/* Sidebar Hover/Expand (DO NOT TOUCH) */
[data-testid="stSidebar"]:hover {
    transform: translateX(0px) !important;
    box-shadow: 6px 0 20px rgba(0,0,0,0.3);
}

/* Main Page Adjustment */
[data-testid="stAppViewContainer"] {
    margin-left: 20px !important;
}

/* Hide the default hamburger icon and Streamlit header */
.st-emotion-cache-10o5hri, .stApp > header {
    display: none !important;
}

/* --- 2. NAVIGATION FONT & COLOR FIXES --- */

/* Force White Text and Enlarged Size on all elements inside the sidebar */
[data-testid="stSidebar"] * {
    color: white !important; 
    font-size: 18px !important; 
    font-weight: 600 !important; 
}

/* Re-apply opacity transition to the specific text wrapper */
[data-testid="stSidebar"] .st-emotion-cache-1wmy9hl p {
    opacity: 0; 
    transition: opacity 0.45s ease 0.15s, color 0.2s;
    white-space: nowrap;
}

/* When sidebar is hovered, make text visible */
[data-testid="stSidebar"]:hover .st-emotion-cache-1wmy9hl p {
    opacity: 1;
}

/* Navigation Links (Anchor Tag) Styling */
[data-testid="stSidebar"] a { 
    padding: 12px 20px;
    margin: 5px 10px;
    border-radius: 8px;
    transition: background-color 0.2s;
    display: flex; 
    align-items: center;
}

/* Navigation Links: Hover state */
[data-testid="stSidebar"] a:hover {
    background-color: #FF4D4D !important; /* Light red on hover */
}

/* Navigation Links: Active page highlight */
[data-testid="stSidebar"] .st-emotion-cache-1jmpsf6 a { 
    background-color: #CC0000 !important; /* Darker red for active link */
    border-left: 5px solid white; 
    padding-left: 15px;
    margin-left: 0; 
}

/* Adjust padding at the top of the sidebar content */
[data-testid="stSidebar"] > div > div > div:nth-child(1) {
    padding-top: 20px !important; 
    padding-bottom: 10px !important;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# ✅ 2. Load dataset
# ------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        data_path = "netflix_titles.csv"
        if not os.path.exists(data_path):
            path = kagglehub.dataset_download("shivamb/netflix-shows")
            data_path = f"{path}/netflix_titles.csv"
        
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Could not load dataset: {e}")
        return pd.DataFrame({'show_id': [], 'title': [], 'type': []})

df = load_data()
st.session_state["netflix_df"] = df


# ------------------------------------------------------------
# ✅ 3. Page Definitions
# ------------------------------------------------------------
pages = [
    st.Page("./tab1.py", title= "Executive Overview"),
    st.Page("./tab2.py", title="Content Explorer"),
    st.Page("./tab3.py", title="Trend Intelligence"),
    st.Page("./tab4.py", title="Geographic Insights"),
    st.Page("./tab5.py", title="Genre Intelligence"),
    st.Page("./tab6.py", title="Creator & Talent Hub"),
    st.Page("./tab7.py", title="Strategic Recommendations"),
]

# ------------------------------------------------------------
# ✅ 4. Run Navigation
# ------------------------------------------------------------
nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()