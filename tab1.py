import streamlit as st
import plotly.express as px

st.title("Netflix Dataset Viewer")

df = st.session_state['netflix_df']
type_counts = df['type'].value_counts().reset_index()
type_counts.columns = ['Type', 'Count']

fig = px.pie(
    type_counts,
    names='Type',
    values='Count',
    color='Type',
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4, 
    title='Distribution of Movies vs TV Shows'
)

fig.update_traces(textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)