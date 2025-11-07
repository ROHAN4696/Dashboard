import streamlit as st
import plotly.express as px
import pandas as pd


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import CountVectorizer

st.set_page_config(layout="wide")

# ================== GLOBAL CSS ==================
st.markdown("""
    <style>
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 2rem;
            max-width: 90%;
            margin-top:0rem;
        }
        .info-box {
            border: 1px solid #ccc;
            padding: 14px;
            border-radius: 8px;
            background-color: #f9f9f9;
            width: 75%;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)


st.title("Netflix Dashboard")


# =========================================================
# ✅ SECTION 1 — Pie Chart (Top-10 + Others)
# =========================================================

dfn = pd.read_csv(r'netflix_titles_with_imdb_ratings.csv')

all_count1 = dfn['country'].value_counts()
mcpctrs1 = all_count1.head(10).copy()
mcpctrs1['Others'] = all_count1.iloc[10:].sum()

netflix_colors = [
    '#E50914', '#B20710', '#831010', '#666666', '#555555',
    '#444444', '#333333', '#222222', '#111111', '#0F0F0F', '#AAAAAA'
]

row1_col1, row1_col2 = st.columns([2, 3])

with row1_col1:
    fig1, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        mcpctrs1,
        labels=mcpctrs1.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=netflix_colors,
        wedgeprops={'edgecolor': '#000000', 'linewidth': 1}
    )
    ax.set_title(
        'Content Distribution (Top 10 + Others)',
        fontsize=12,
        pad=8
    )
    ax.axis('equal')
    st.pyplot(fig1)

with row1_col2:
    st.markdown("""
    <div class="info-box">
    <b>Insights:</b><br>
    • Shows leading content-producing countries.<br>
    • "Others" represents smaller contributors.<br>
    • Indicates geographic concentration.<br>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# ✅ SECTION 2 — Avg Lag Movies vs TV
# =========================================================

df = pd.read_csv(r'C:\\Users\\krdhi\\Downloads\\archive\\KPI\\netflix_titles.csv')
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['release_date'] = pd.to_datetime(df['release_year'], format='%Y', errors='coerce')

df['lag_days'] = (df['date_added'] - df['release_date']).dt.days
df = df[df['lag_days'].between(0, 5000)]
df['year_added'] = df['date_added'].dt.year

avg_lag_yearly = (
    df.groupby(['year_added', 'type'])['lag_days']
    .mean()
    .reset_index()
    .sort_values('year_added')
)

row2_col1, row2_col2 = st.columns([2, 3])

with row2_col1:
    fig2 = px.line(
        avg_lag_yearly,
        x='year_added',
        y='lag_days',
        color='type',
        markers=True,
        title='Avg Lag: Release → Netflix Add (Movies vs TV)',
        color_discrete_sequence=['#FF4C4C', '#B22222']
    )
    fig2.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Times New Roman', color='black', size=14),
        title_x=0.5,
        xaxis=dict(title='Year Added', showgrid=True, linecolor='black', dtick=1),
        yaxis=dict(title='Avg Lag (Days)', showgrid=True, linecolor='black'),
    )
    fig2.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(fig2, use_container_width=True)

with row2_col2:
    st.markdown("""
    <div class="info-box">
    <b>Insights:</b><br>
    • Shows fluctuations in time-to-add trends.<br>
    • TV shows generally added quicker than movies.<br>
    • Possible shift based on acquisition strategy.<br>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# ✅ SECTION 3 — YoY Growth Movies vs TV
# =========================================================

df = pd.read_csv(r'C:\\Users\\krdhi\\Downloads\\archive\\KPI\\netflix_titles.csv')
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')

yearly_counts = (
    df.groupby(['release_year', 'type'])
    .size()
    .reset_index(name='count')
    .pivot(index='release_year', columns='type', values='count')
    .fillna(0)
)

yearly_growth = yearly_counts.diff().fillna(0).reset_index()
yearly_growth = yearly_growth[yearly_growth['release_year'] >= 2005]

COLOR_MOVIE = '#FF6666'
COLOR_TVSHOW = '#800000'
COLOR_FILL = 'rgba(128, 0, 0, 0.25)'

row3_col1, row3_col2 = st.columns([2, 3])

with row3_col1:
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=yearly_growth['release_year'],
        y=yearly_growth.get('Movie', 0),
        mode='lines+markers',
        name='Movie',
        line=dict(color=COLOR_MOVIE, width=2),
        marker=dict(size=6)
    ))

    fig3.add_trace(go.Scatter(
        x=yearly_growth['release_year'],
        y=yearly_growth.get('TV Show', 0),
        mode='lines+markers',
        name='TV Show',
        line=dict(color=COLOR_TVSHOW, width=2.5),
        marker=dict(size=6)
    ))

    x_fill = yearly_growth['release_year']
    y_upper = yearly_growth['TV Show']
    y_lower = yearly_growth['Movie']

    fig3.add_trace(go.Scatter(
        x=pd.concat([x_fill, x_fill[::-1]]),
        y=pd.concat([pd.Series(np.maximum(y_upper, y_lower)), pd.Series(y_lower[::-1])]),
        fill='toself',
        fillcolor=COLOR_FILL,
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        showlegend=True,
        name='TV Shows > Movies'
    ))

    fig3.update_layout(
        title='YoY Growth: Movies vs TV Shows',
        xaxis_title='Release Year',
        yaxis_title='YoY Growth',
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig3, use_container_width=True)

with row3_col2:
    st.markdown("""
    <div class="info-box">
    <b>Insights:</b><br>
    • TV shows show stronger yearly growth compared to movies.<br>
    • Indicates Netflix’s increasing focus on episodic content.<br>
    </div>
    """, unsafe_allow_html=True)

