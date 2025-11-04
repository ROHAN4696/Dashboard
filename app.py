import streamlit as st
import pandas as pd
import kagglehub

@st.cache_data
def load_data():
    path = kagglehub.dataset_download("shivamb/netflix-shows")
    df = pd.read_csv(f"{path}/netflix_titles.csv")
    return df

df = load_data()

st.session_state["netflix_df"] = df

pages = [
   st.Page("./tab1.py", title="Executive Overview"),
   st.Page("./tab2.py", title="Content Explorer"),
   st.Page("./tab3.py", title="Trend Intelligence"),
   st.Page("./tab4.py", title="Geographic Insights"),
   st.Page("./tab5.py", title="Genre and Category Intelligence"),
   st.Page("./tab6.py", title="Creator & Talent Hub"),
   st.Page("./tab7.py", title="Strategic Recommendations"),
]

nav = st.navigation(pages, position="sidebar", expanded=True)
nav.run()
