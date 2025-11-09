import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="Netflix Insights Dashboard")

# ---------------------------------------------------------
# METAMORPHIC NEON GLOW CSS
# ---------------------------------------------------------
st.markdown("""
<style>

:root {
    --netflix-red: #E50914;
    --netflix-red-soft: rgba(229, 9, 20, 0.45);
    --netflix-red-glow: rgba(229, 9, 20, 0.75);
    --card-bg: #111111;
    --card-border: #1f1f1f;
}

# /* --- TITLES & HEADERS NEON GLOW --- */
# h1, h2, h3, h4, h5 {
#     color: var(--netflix-red) !important;
#     text-shadow:
#         0 0 8px var(--netflix-red-soft),
#         0 0 14px var(--netflix-red-glow),
#         0 0 22px var(--netflix-red-glow);
#     font-weight: 700 !important;
# }

/* --- METAMORPHIC GLOW CARD --- */
.glow-card {
    background: var(--card-bg);
    padding: 30px 35px;
    border-radius: 16px;
    border: 1px solid var(--card-border);
    margin-top: 25px;
    margin-bottom: 35px;

    # box-shadow:
    #     inset 0 0 25px rgba(255, 255, 255, 0.05),
    #     0 0 20px rgba(229, 9, 20, 0.25),
    #     0 0 35px rgba(229, 9, 20, 0.35),
    #     0 0 55px rgba(229, 9, 20, 0.45);

    transition: all 0.35s ease-in-out;
}

# .glow-card:hover {
#     transform: translateY(-5px);
#     box-shadow:
#         inset 0 0 35px rgba(255, 255, 255, 0.08),
#         0 0 35px rgba(229, 9, 20, 0.55),
#         0 0 55px rgba(229, 9, 20, 0.75),
#         0 0 85px rgba(229, 9, 20, 0.9);
# }

/* Chart container */
.chart-wrap {
    background: #0c0c0c;
    padding: 18px;
    border-radius: 12px;
}

/* Remove padding from containers */
div[data-testid="stVerticalBlock"] > div {
    padding-left: 0 !important;
}

/* Add styling to all headings */
h1, h2, h3, h4, h5, h6 {
    padding-bottom: 15px;
    margin-bottom: 10px;
    width: 100%;
    margin-left: 0;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARD WRAPPERS
# ---------------------------------------------------------
def glow_card(title: str):
    st.markdown(f"<div class='glow-card'><h2>{title}</h2>", unsafe_allow_html=True)

def end_card():
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
try:
    df = st.session_state['netflix_df'].copy()
except KeyError:
    st.error("Error: Netflix DataFrame not found in session state.")
    st.stop()

# ---------------------------------------------------------
# SECTION 1 — TOP GENRE PER COUNTRY
# ---------------------------------------------------------
df1 = df[['title', 'listed_in', 'country', 'rating']].dropna(subset=['listed_in', 'country', 'rating']).copy()
df1['country'] = df1['country'].str.split(', ')
df1['listed_in'] = df1['listed_in'].str.split(', ')
df1 = df1.explode('country').explode('listed_in')
df1.rename(columns={'listed_in': 'Genre', 'country': 'Country'}, inplace=True)

genre_counts = df1.groupby(['Country', 'Genre']).size().reset_index(name='Count')
top_genre = genre_counts.loc[genre_counts.groupby('Country')['Count'].idxmax()]

rating_mode = df1.groupby(['Country', 'Genre'])['rating'].agg(
    lambda x: x.mode()[0] if not x.mode().empty else None
).reset_index()

insight_df = pd.merge(top_genre, rating_mode, on=['Country', 'Genre'], how='left')
insight_df = insight_df.sort_values(by='Count', ascending=False).reset_index(drop=True)
insight_df['Country_Genre'] = insight_df['Country'] + ' - ' + insight_df['Genre']

top15 = insight_df.sort_values('Count', ascending=False).head(15)
red_palette = ['#FFB3B3', '#FF6666', '#B22222', '#800000']

fig1 = px.bar(
    top15,
    x='Country_Genre',
    y='Count',
    color='rating',

    color_discrete_sequence=red_palette
)

fig1.update_layout(

    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(family='Times New Roman', color='white', size=14),
    xaxis=dict(tickangle=70, color='white'),
    yaxis=dict(color='white')
)

# ---- Render Section 1 ----
glow_card("Top Genre per Country and Their Dominant Rating")
# st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig1, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
end_card()

# ---------------------------------------------------------
# SECTION 2 — TITLES ADDED PER YEAR
# ---------------------------------------------------------
TOP_N = 5
RED_SHADES = ['#B00610', '#E50914', '#FF6F61', '#FF8A80', '#FFB3B3']

df2 = df.copy()
df2['date_added'] = df2['date_added'].astype(str).str.strip()
df2['date_added'] = pd.to_datetime(df2['date_added'], errors='coerce')
df2 = df2[df2['date_added'].notna()]

df2['year_added'] = df2['date_added'].dt.year.astype(int)
df_exp = df2.dropna(subset=['listed_in']).copy()
df_exp['listed_in'] = df_exp['listed_in'].astype(str)
df_exp = df_exp.assign(genre=df_exp['listed_in'].str.split(',')).explode('genre')
df_exp['genre'] = df_exp['genre'].str.strip()

id_col = next((c for c in ['show_id','id','title_id','title'] if c in df_exp.columns), df_exp.columns[0])
genre_totals = df_exp.groupby('genre')[id_col].nunique().sort_values(ascending=False)
top_genres = genre_totals.head(TOP_N).index.tolist()

year_genre = (
    df_exp[df_exp['genre'].isin(top_genres)]
    .groupby(['year_added','genre'])[id_col]
    .nunique()
    .reset_index(name='count')
)

min_year = int(year_genre['year_added'].min())
max_year = int(year_genre['year_added'].max())
years = np.arange(min_year, max_year + 1)

pivot = year_genre.pivot(index='year_added', columns='genre', values='count')
pivot = pivot.reindex(index=years, columns=top_genres, fill_value=0)

plot_df = pivot.reset_index().melt(id_vars='year_added', var_name='genre', value_name='count')

fig2 = go.Figure()
for i, g in enumerate(top_genres):
    series = plot_df[plot_df['genre'] == g]
    fig2.add_trace(go.Scatter(
        x=series['year_added'],
        y=series['count'],
        mode='lines+markers',
        name=g,
        line=dict(width=2.5, color=RED_SHADES[i]),
        marker=dict(size=6)
    ))

fig2.update_layout(

    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(color='white', dtick=1),
    yaxis=dict(color='white'),
)

# ---- Render Section 2 ----
glow_card(f"Titles Added per Year — Top {TOP_N} Genres")
# st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
end_card()

# ---------------------------------------------------------
# SECTION 3 — GENRE VS RATING SPREAD (BOXPLOT)
# ---------------------------------------------------------
genre_df = df.copy()
genre_df['listed_in'] = genre_df['listed_in'].fillna('Unknown')
genre_df = genre_df.assign(genre=genre_df['listed_in'].str.split(', ')).explode('genre')

fig3 = px.box(
    genre_df,
    x='genre',
    y='rating',
    color='genre',

    color_discrete_sequence=px.colors.sequential.Reds
)

fig3.update_layout(
    title_x=0.5,
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(color='white'),
    yaxis=dict(color='white')
)

# ---- Render Section 3 ----
glow_card("Genre vs Rating Spread")
# st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig3, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
end_card()
