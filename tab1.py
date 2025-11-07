import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        /* Global App Background - Light Theme */
        .stApp {
            background-color: #F8F8F8;
        }
        
        /* Ensures the wide layout is used effectively and respects user's max-width request */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 2rem;
            max-width: 100%;
            margin-top:0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Netflix Dataset Viewer")

df = st.session_state['netflix_df']
type_counts = df['type'].value_counts().reset_index()
type_counts.columns = ['Type', 'Count']

fig_pie = px.pie(
    type_counts,
    names='Type',
    values='Count',
    color='Type',
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4, 
    title='Distribution of Movies vs TV Shows'
)

fig_pie.update_traces(textinfo='percent+label')

df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')

# Group by year and type
yearly_counts = (
    df.groupby(['release_year', 'type'])
    .size()
    .reset_index(name='count')
    .sort_values('release_year')
)
fig_bar = px.bar(
    yearly_counts,
    x='release_year',
    y='count',
    color='type',
    barmode='group',  # side-by-side bars; use 'stack' for stacked view
    title=' Year-on-Year Content Production (Movies vs TV Shows)',
    labels={'release_year': 'Release Year', 'count': 'Number of Releases', 'type': 'Type'},
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_bar.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    yaxis_title='Number of Titles',
    xaxis_title='Year'
)

col1, col2 = st.columns([3,4])

with col1:
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.plotly_chart(fig_bar, use_container_width=True)

