import streamlit as st
import pandas as pd
import plotly.express as px

df = st.session_state['netflix_df']


country_counts = (
    df['country']
    .dropna()
    .str.split(',')
    .explode()
    .str.strip()
    .value_counts()
    .reset_index()
)
country_counts.columns = ['country', 'count']

fig = px.choropleth(
    country_counts,
    locations='country',
    locationmode='country names',
    color='count',
    hover_name='country',
    color_continuous_scale='Reds',
    title='Netflix Titles by Country'
)

st.plotly_chart(fig, use_container_width=True)

selected_country = st.selectbox("Filter by Country", sorted(country_counts['country'].unique()))

filtered_df = df[df['country'].fillna("").str.contains(selected_country, case=False)]

st.subheader(f"Titles from {selected_country}")
st.dataframe(filtered_df[['title', 'type', 'director', 'release_year', 'listed_in']])
