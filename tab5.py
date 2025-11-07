import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os 

import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Assuming original_df is your Netflix dataset loaded previously
try:
    df = st.session_state['netflix_df'].copy()
except KeyError:
    st.error("Error: Netflix DataFrame not found in session state. Please ensure 'netflix_df' is loaded into st.session_state.")
    st.stop()
df = df[['title', 'listed_in', 'country', 'rating']].dropna(subset=['listed_in', 'country', 'rating']).copy()

# Split multiple countries/genres
df['country'] = df['country'].str.split(', ')
df['listed_in'] = df['listed_in'].str.split(', ')

# Explode both
df = df.explode('country').explode('listed_in')
df.rename(columns={'listed_in': 'Genre', 'country': 'Country'}, inplace=True)

# Group by Country & Genre to find the most common one
genre_counts = df.groupby(['Country', 'Genre']).size().reset_index(name='Count')

# For each country, find top genre
top_genre = genre_counts.loc[genre_counts.groupby('Country')['Count'].idxmax()]

# Merge back with rating info
rating_mode = df.groupby(['Country', 'Genre'])['rating'].agg(lambda x: x.mode()[0] if not x.mode().empty else None).reset_index()
insight_df = pd.merge(top_genre, rating_mode, on=['Country', 'Genre'], how='left')

insight_df = insight_df.sort_values(by='Count', ascending=False).reset_index(drop=True)
insight_df.head(10)

top15 = insight_df.sort_values('Count', ascending=False).head(15)

st.title("Top Genre per Country and Their Dominant Rating")

# Create combined label
insight_df['Country_Genre'] = insight_df['Country'] + ' - ' + insight_df['Genre']

# Sort by count to keep top 15 overall
top15 = insight_df.sort_values('Count', ascending=False).head(15)

# Define red color shades (light → dark)
red_palette = ['#FFB3B3', '#FF6666', '#B22222', '#800000']

# Create interactive bar plot
fig = px.bar(
    top15,
    x='Country_Genre',
    y='Count',
    color='rating',
    title='Top Genre per Country and Their Dominant Rating',
    color_discrete_sequence=red_palette
)

# Layout styling
fig.update_layout(
    title=dict(text='Top Genre per Country and Their Dominant Rating', font=dict(color='black')),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Times New Roman', color='black', size=14),
    title_x=0.5,
    xaxis=dict(
        title=dict(text='Country - Genre', font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True,
        gridcolor='lightgray',
        linecolor='black',
        tickangle=75
    ),
    yaxis=dict(
        title=dict(text='No. of Titles in Top Genre', font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True,
        gridcolor='lightgray',
        linecolor='black'
    ),
    legend=dict(
        title=dict(text='Dominant Rating', font=dict(color='black')),
        font=dict(color='black')
    )
)

# Bar outline
fig.update_traces(marker_line_color='black', marker_line_width=1.2)

st.plotly_chart(fig, width="stretch")

try:
    df = st.session_state['netflix_df'].copy()
except KeyError:
    st.error("Error: Netflix DataFrame not found in session state. Please ensure 'netflix_df' is loaded into st.session_state.")
    st.stop()

TOP_N = 5
CSV_FALLBACK = "netflix_titles.csv"
RED_SHADES = ['#B00610', '#E50914', '#FF6F61', '#FF8A80', '#FFB3B3']
FONT_FAMILY = "Times New Roman"

st.title(f"Titles Added per Year — Top {TOP_N} Genres")

# Ensure column exists
if 'date_added' not in df.columns:
    raise ValueError("'date_added' column not found in dataframe")

# Convert to string first, strip spaces, then convert
df['date_added'] = df['date_added'].astype(str).str.strip()
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

# Drop rows where conversion failed
df = df[df['date_added'].notna()].copy()

# Extract year
df['year_added'] = df['date_added'].dt.year.astype(int)


# require genres
if 'listed_in' not in df.columns:
    st.error("❌ Expected 'listed_in' column in dataset")
    st.stop()

# explode genres
df_exp = df.dropna(subset=['listed_in']).copy()
df_exp['listed_in'] = df_exp['listed_in'].astype(str)
df_exp = df_exp.assign(genre=df_exp['listed_in'].str.split(',')).explode('genre')
df_exp['genre'] = df_exp['genre'].str.strip()

# id column for unique counting
id_col = next((c for c in ['show_id','id','title_id','title'] if c in df_exp.columns), df_exp.columns[0])

# totals to pick top genres
genre_totals = df_exp.groupby('genre')[id_col].nunique().sort_values(ascending=False)
top_genres = genre_totals.head(TOP_N).index.tolist()

# compute counts per year per genre
year_genre = (
    df_exp[df_exp['genre'].isin(top_genres)]
    .groupby(['year_added','genre'])[id_col]
    .nunique()
    .reset_index(name='count')
)

if year_genre.empty:
    st.warning("⚠️ No data found for the selected genres.")
    st.stop()

# build complete year index
min_year = int(year_genre['year_added'].min())
max_year = int(year_genre['year_added'].max())
years = np.arange(min_year, max_year + 1)

pivot = year_genre.pivot(index='year_added', columns='genre', values='count')
pivot = pivot.reindex(index=years, columns=top_genres, fill_value=0)
pivot = pivot.apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

plot_df = pivot.reset_index().melt(id_vars='year_added', var_name='genre', value_name='count')

# ---------- Plot ----------
fig = go.Figure()
for i, g in enumerate(top_genres):
    series = plot_df[plot_df['genre'] == g]
    fig.add_trace(go.Scatter(
        x=series['year_added'],
        y=series['count'],
        mode='lines+markers',
        name=g,
        line=dict(width=2.5, color=RED_SHADES[i % len(RED_SHADES)]),
        marker=dict(size=6),
        hovertemplate="<b>%{text}</b><br>Year: %{x}<br>Titles added: %{y:,}<extra></extra>",
        text=[g]*len(series)
    ))

fig.update_layout(
    title=dict(text=f"Titles Added per Year — Top {TOP_N} Genres", font=dict(color="black")),
    xaxis=dict(
        title=dict(text='Year Added', font=dict(color="black")),
        tickfont=dict(color="black"),
        tickmode='linear',
        dtick=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.06)',
        linecolor='black'
    ),
    yaxis=dict(
        title=dict(text='Number of Titles Added', font=dict(color="black")),
        tickfont=dict(color="black"),
        showgrid=True,
        gridcolor='rgba(0,0,0,0.06)',
        linecolor='black'
    ),
    paper_bgcolor='white',
    plot_bgcolor='white',
    font=dict(family=FONT_FAMILY, color="black", size=12),
    title_font=dict(family=FONT_FAMILY, color="black", size=18),
    legend=dict(
        title=dict(text='Genre', font=dict(color="black")),
        font=dict(color="black"),
        bgcolor='white',
        bordercolor='black',
        borderwidth=1
    ),
    margin=dict(t=90, b=60, l=80, r=40),
    width=900,
    height=520
)

st.plotly_chart(fig, width="stretch")

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load Data
df = st.session_state['netflix_df'].copy()

df['listed_in'] = df['listed_in'].fillna('Unknown')

genre_df = df.assign(genre=df['listed_in'].str.split(', ')).explode('genre')

st.title("Genre vs Rating Spread")

# Genre vs Rating Boxplot (shades of red)
fig = px.box(genre_df, x='genre', y='rating', color='genre', color_discrete_sequence=px.colors.sequential.Reds)
st.plotly_chart(fig, use_container_width=True)


