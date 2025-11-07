import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# REMOVED: from sklearn.feature_extraction.text import CountVectorizer

st.set_page_config(layout="wide")

# ================== GLOBAL CSS ==================
# Reverted to your original CSS
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
# ✅ SECTION 1 — Pie Chart (Top-10 + Others) - PLOTLY
# =========================================================

try:
    # Assuming 'netflix_df' is loaded into session_state elsewhere
    dfn = st.session_state['netflix_df'].copy()

    all_count1 = dfn['country'].value_counts()
    mcpctrs1 = all_count1.head(10).copy()
    mcpctrs1['Others'] = all_count1.iloc[10:].sum()

    # --- KPI Calculations for Plot 1 ---
    total_content = mcpctrs1.sum()
    top_country_name = mcpctrs1.index[0]
    top_country_val = mcpctrs1.iloc[0]
    top_country_pct = (top_country_val / total_content) * 100
    others_pct = (mcpctrs1['Others'] / total_content) * 100
    # --- End KPI Calculations ---

    netflix_colors = [
        '#E50914', '#B20710', '#831010', '#666666', '#555555',
        '#444444', '#333333', '#222222', '#111111', '#0F0F0F', '#AAAAAA'
    ]

    # Prepare data for Plotly
    plot1_data = mcpctrs1.reset_index()
    plot1_data.columns = ['Country', 'Count']
    
    row1_col1, row1_col2 = st.columns([2, 3])

    with row1_col1:
        # Using Plotly Express for the Pie Chart
        fig1 = px.pie(
            plot1_data,
            names='Country',
            values='Count',
            title='Content Distribution (Top 10 + Others)',
            color_discrete_sequence=netflix_colors
        )
        fig1.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#000000', width=1)),
            hole=0.3
        )
        fig1.update_layout(
            title_x=0.5,
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with row1_col2:
        # KPI Box
        st.markdown(f"""
        <div class="info-box">
        <b>Key KPIs:</b><br>
        • <b>Top Country ({top_country_name}):</b> {top_country_pct:.1f}% of content.<br>
        • <b>All Other Countries:</b> {others_pct:.1f}% of content.<br>
        </div>
        """, unsafe_allow_html=True)

except KeyError:
    st.error("Please ensure the DataFrame is loaded into st.session_state['netflix_df'].")
except Exception as e:
    st.error(f"An error occurred loading data for Plot 1: {e}")
    dfn = None


# =========================================================
# ✅ SECTION 2 & 3 — Lag & Growth (Already Plotly)
# =========================================================

try:
    # Using the absolute path that fixed the error from before
    df = st.session_state['netflix_df'].copy()
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

    # --- Process for Plot 2 ---
    df_lag = df.copy()
    df_lag['release_date'] = pd.to_datetime(df_lag['release_year'], format='%Y', errors='coerce')
    df_lag['lag_days'] = (df_lag['date_added'] - df_lag['release_date']).dt.days
    df_lag = df_lag[df_lag['lag_days'].between(0, 5000)]
    df_lag['year_added'] = df_lag['date_added'].dt.year

    avg_lag_yearly = (
        df_lag.groupby(['year_added', 'type'])['lag_days']
        .mean()
        .reset_index()
        .sort_values('year_added')
    )
    
    # --- KPI Calculations for Plot 2 ---
    avg_lag_movie = df_lag[df_lag['type'] == 'Movie']['lag_days'].mean()
    avg_lag_tv = df_lag[df_lag['type'] == 'TV Show']['lag_days'].mean()
    lag_diff = avg_lag_movie - avg_lag_tv
    # --- End KPI Calculations ---


    # --- Process for Plot 3 ---
    df_growth = df.copy()
    df_growth['release_year'] = pd.to_numeric(df_growth['release_year'], errors='coerce')
    
    yearly_counts = (
        df_growth.groupby(['release_year', 'type'])
        .size()
        .reset_index(name='count')
        .pivot(index='release_year', columns='type', values='count')
        .fillna(0)
    )

    yearly_growth = yearly_counts.diff().fillna(0).reset_index()
    yearly_growth = yearly_growth[yearly_growth['release_year'] >= 2005]

    # --- KPI Calculations for Plot 3 ---
    avg_growth_movie = yearly_growth.get('Movie', pd.Series(0)).mean()
    avg_growth_tv = yearly_growth.get('TV Show', pd.Series(0)).mean()
    growth_diff = avg_growth_tv - avg_growth_movie
    # --- End KPI Calculations ---


    # =========================================================
    # ✅ SECTION 2 — Avg Lag Movies vs TV
    # =========================================================
    st.divider()
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
        # KPI Box
        st.markdown(f"""
        <div class="info-box">
        <b>Key KPIs (All Years):</b><br>
        • <b>Average Movie Lag:</b> {avg_lag_movie:.0f} days.<br>
        • <b>Average TV Show Lag:</b> {avg_lag_tv:.0f} days.<br>
        • <b>Insight:</b> TV Shows are added, on average, <b>{lag_diff:.0f} days faster</b> than movies.
        </div>
        """, unsafe_allow_html=True)


    # =========================================================
    # ✅ SECTION 3 — YoY Growth Movies vs TV
    # =========================================================
    st.divider()
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
        y_upper = yearly_growth.get('TV Show', pd.Series(0))
        y_lower = yearly_growth.get('Movie', pd.Series(0))

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
            title='YoY Growth: Movies vs TV Shows (Since 2005)',
            xaxis_title='Release Year',
            yaxis_title='YoY Growth',
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig3, use_container_width=True)

    with row3_col2:
        # KPI Box
        st.markdown(f"""
        <div class="info-box">
        <b>Key KPIs (Since 2005):</b><br>
        • <b>Avg. Movie Growth (YoY):</b> {avg_growth_movie:.1f} titles/year.<br>
        • <b>Avg. TV Show Growth (YoY):</b> {avg_growth_tv:.1f} titles/year.<br>
        • <b>Insight:</b> TV Show growth outpaces movies by <b>{growth_diff:.1f} titles</b> per year on average.
        </div>
        """, unsafe_allow_html=True)

except KeyError:
    st.error("Please ensure the DataFrame is loaded into st.session_state['netflix_df'].")
except Exception as e:
    st.error(f"An error occurred loading or processing data for Plots 2 & 3: {e}")
