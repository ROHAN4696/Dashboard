import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# 🎨 CUSTOM DARK METAMORPHIC GLOW CSS (APPLIED)
# -----------------------------
custom_css = """
<style>

/* Dark Netflix Background */
.stApp {
    background-color: #000000 !important;
}

/* Glowing Chart Containers */
.chart-wrap {
    background: #0c0c0c;
    padding: 18px;
    border-radius: 12px;
    box-shadow:
        inset 0 0 15px rgba(255,255,255,0.05),
        0 0 20px rgba(229, 9, 20, 0.25),
        0 0 35px rgba(229, 9, 20, 0.35),
        0 0 55px rgba(229, 9, 20, 0.45);
}

/* Glow containers for whole section */
.glow-card {
    background: #111111;
    padding: 30px 35px;
    border-radius: 16px;
    border: 1px solid #1f1f1f;
    margin-top: 25px;
    margin-bottom: 35px;
    box-shadow:
        inset 0 0 25px rgba(255,255,255,0.05),
        0 0 20px rgba(229, 9, 20, 0.25),
        0 0 35px rgba(229, 9, 20, 0.35),
        0 0 55px rgba(229, 9, 20, 0.45);
    transition: all 0.3s ease-in-out;
}

.glow-card:hover {
    transform: translateY(-4px);
    box-shadow:
        inset 0 0 32px rgba(255,255,255,0.09),
        0 0 38px rgba(229, 9, 20, 0.55),
        0 0 55px rgba(229, 9, 20, 0.75),
        0 0 85px rgba(229, 9, 20, 0.9);
}

/* Glowing red headers */
h1, h2, h3 {
    color: #E50914 !important;
    text-shadow:
        0 0 6px rgba(229, 9, 20, 0.45),
        0 0 12px rgba(229, 9, 20, 0.75),
        0 0 18px rgba(229, 9, 20, 0.9);
    font-weight: 800 !important;
}

/* Remove white bg from plotly wrapper (ensures chart-wrap background shows) */
.plot-container > div {
    background-color: #111111 !important;
}

/* Custom Red Header styling inside the special red div */
.red-header-div h2 {
    color: white !important; /* Make text white inside the red box */
    text-shadow: none !important; /* Remove text glow for better contrast */
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------
# Set Streamlit page to wide 
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# glow_card wrappers
# -----------------------------
def glow_card(title: str):
    st.markdown(f"<div class='glow-card'><h2>{title}</h2>", unsafe_allow_html=True)

def end_card():
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Load dataframe
# -----------------------------
try:
    # Assuming 'netflix_df' is loaded into session_state elsewhere
    df = st.session_state['netflix_df'].copy()
except:
    st.error("DataFrame not found.")
    st.stop()

# -----------------------------
# Helper for figure styling
# -----------------------------
def update_fig_style(fig, title):
    fig.update_layout(
        plot_bgcolor='#111111',
        paper_bgcolor='#111111',
        font=dict(family='Times New Roman', color='white', size=14),
        title=dict(text=title, font=dict(color="#E50914")),
        xaxis=dict(showgrid=True, gridcolor='grey', linecolor='white', tickfont=dict(color='white')),
        yaxis=dict(showgrid=True, gridcolor='grey', linecolor='white', tickfont=dict(color='white')),
        legend=dict(font=dict(color='white'), bgcolor='#111111', bordercolor='#333333'),
        geo_bgcolor='#111111',
        margin=dict(t=50, b=50)
    )
    return fig


# -----------------------------
# PREPROCESSING
# -----------------------------
# Preprocessing for all sections
country_counts = (
    df['country'].dropna().str.split(',').explode().str.strip().value_counts().reset_index()
)
country_counts.columns = ['country', 'count']

df_geo = df.copy().dropna(subset=['country', 'type'])
df_geo = df_geo.assign(country=df_geo['country'].str.split(', ')).explode('country')
df_geo['country'] = df_geo['country'].str.strip()

movies_df = df_geo[df_geo['type'] == 'Movie']
tv_df = df_geo[df_geo['type'] == 'TV Show']

movies_pct = movies_df['country'].value_counts(normalize=True).reset_index()
movies_pct.columns = ['country', 'percentage']
movies_pct['percentage'] *= 100

tv_pct = tv_df['country'].value_counts(normalize=True).reset_index()
tv_pct.columns = ['country', 'percentage']
tv_pct['percentage'] *= 100

df_pre_origin = df.copy()
df_pre_origin['country'] = df_pre_origin['country'].astype(str)
df_pre_origin = df_pre_origin[df_pre_origin['country'].notna()]
df_pre_origin = df_pre_origin[df_pre_origin['country'].str.lower() != 'unknown']

df_pre_origin['date_added'] = pd.to_datetime(df_pre_origin['date_added'], errors='coerce')
df_pre_origin['year_added'] = df_pre_origin['date_added'].dt.year
df_pre_origin['primary_country'] = df_pre_origin['country'].str.split(',').str[0].str.strip()

def get_origin(country):
    if country == 'United States':
        return 'Domestic'
    elif pd.isna(country) or country == '':
        return pd.NA
    else:
        return 'International'

df_pre_origin['content_origin'] = df_pre_origin['primary_country'].apply(get_origin)
df_pre_origin = df_pre_origin.dropna(subset=['content_origin'])

# -----------------------------
# GRAPH 2 & 3 SECTION: Movies vs TV Shows Scatter Map
# -----------------------------
st.markdown(
    """
    <div class='red-header-div' style='background-color: #E50914; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
        <h2>Content Distribution by Type Across the Globe</h2>
    </div>
    """,
    unsafe_allow_html=True
)

glow_card("Content Distribution by Movies vs TV Shows")

col_a, col_b = st.columns(2)

with col_a:
    fig2 = px.scatter_geo(
        movies_pct, locations="country", locationmode="country names", size="percentage",
        hover_name="country", hover_data={"percentage": ":.2f"}, projection="natural earth",
        color_discrete_sequence=["#FF4C4C"] # Lighter red for visibility
    )
    fig2 = update_fig_style(fig2, 'Movies: % of Titles per Country')

    st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    fig3 = px.scatter_geo(
        tv_pct, locations="country", locationmode="country names", size="percentage",
        hover_name="country", hover_data={"percentage": ":.2f"}, projection="natural earth",
        color_discrete_sequence=["#B22222"] # Darker red/maroon for TV
    )
    fig3 = update_fig_style(fig3, 'TV Shows: % of Titles per Country')

    st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

end_card()

st.markdown("---")

# -----------------------------
# SECOND MAP SECTION: Top Genre Scatter Map
# -----------------------------
st.markdown(
    """
    <div class='red-header-div' style='background-color: #E50914; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
        <h2>Netflix Content Distribution Map (Movies vs TV Shows + Top Genre)</h2>
    </div>
    """,
    unsafe_allow_html=True
)

glow_card("Movies vs TV Shows + Top Genre (Country-wise)")

df = df.dropna(subset=['country', 'type', 'listed_in'])
df = df.assign(country=df['country'].str.split(', ')).explode('country')
df['country'] = df['country'].str.strip()

df["genre_list"] = df["listed_in"].str.split(",").apply(lambda x: [i.strip() for i in x])
genre_dummies = df["genre_list"].explode().str.get_dummies().groupby(level=0).sum()
df = df.join(genre_dummies)
genre_cols = genre_dummies.columns.tolist()

movies_df = df[df['type'] == "Movie"]
tv_df = df[df['type'] == "TV Show"]

movies_pct = movies_df['country'].value_counts(normalize=True).reset_index()
movies_pct.columns = ['country', 'percentage']
movies_pct['percentage'] *= 100

tv_pct = tv_df['country'].value_counts(normalize=True).reset_index()
tv_pct.columns = ['country', 'percentage']
tv_pct['percentage'] *= 100

def get_top_genre(df_):
    grouped = df_.groupby("country")[genre_cols].sum()
    top = grouped.idxmax(axis=1)
    return top.reset_index().rename(columns={0: "top_genre"})

movies_top = get_top_genre(movies_df)
tv_top = get_top_genre(tv_df)

movies_final = movies_pct.merge(movies_top, on="country", how="left")
tv_final = tv_pct.merge(tv_top, on="country", how="left")

# Use a set of diverse colors for genres
color_map = {
    g: px.colors.qualitative.Bold[i % len(px.colors.qualitative.Bold)]
    for i, g in enumerate(genre_cols)
}

col1, col2 = st.columns(2)

with col1:
    fig_movies = px.scatter_geo(
        movies_final, locations="country", locationmode="country names", size="percentage",
        color="top_genre", hover_name="country", projection="natural earth",
        color_discrete_map=color_map
    )
    fig_movies = update_fig_style(fig_movies, "Movies: % of Titles & Top Genre")

    st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
    st.plotly_chart(fig_movies, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    fig_tv = px.scatter_geo(
        tv_final, locations="country", locationmode="country names", size="percentage",
        color="top_genre", hover_name="country", projection="natural earth",
        color_discrete_map=color_map
    )
    fig_tv = update_fig_style(fig_tv, "TV Shows: % of Titles & Top Genre")

    st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
    st.plotly_chart(fig_tv, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

end_card()

st.markdown("---")

# -----------------------------
# THIRD SECTION: International vs. Domestic Content Analysis
# -----------------------------
st.markdown(
    """
    <div class='red-header-div' style='background-color: #E50914; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
        <h2>International vs. Domestic Content Analysis</h2>
    </div>
    """,
    unsafe_allow_html=True
)

glow_card("International vs Domestic Analysis")

# TOP 10 COUNTRIES
countries_g4 = (
    df_pre_origin['country']
    .str.split(',').explode().str.strip()
)
countries_g4 = countries_g4[countries_g4.str.lower() != 'united states']
top_countries_g4 = countries_g4.value_counts().head(10).reset_index()
top_countries_g4.columns = ['Country', 'Count']

fig4 = px.bar(
    top_countries_g4, x='Country', y='Count', text='Count',
    color_discrete_sequence=['#FF4C4C']
)
fig4 = update_fig_style(fig4, 'Top 10 International Countries')

st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig4, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# COUNTRY VS CONTENT TYPE
df_non_us_type = df_pre_origin[~df_pre_origin['primary_country'].str.contains('United States', case=False, na=False)]
top_countries_g5 = df_non_us_type['primary_country'].value_counts().head(10).index
df_top_g5 = df_non_us_type[df_non_us_type['primary_country'].isin(top_countries_g5)]

country_type = df_top_g5.groupby(['primary_country', 'type']).size().reset_index(name='count')

fig5 = px.bar(
    country_type, y='primary_country', x='count', color='type',
    orientation='h', color_discrete_sequence=['#FF4C4C', '#B22222']
)
fig5 = update_fig_style(fig5, 'Country vs Content Type')

st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig5, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# GROWTH TREND
yearly = df_pre_origin.groupby(['year_added', 'content_origin']).size().reset_index(name='count')

fig6 = px.line(
    yearly, x='year_added', y='count', color='content_origin',
    markers=True, color_discrete_sequence=['#FF4C4C', '#B22222']
)
fig6 = update_fig_style(fig6, 'Growth Over Time (Domestic vs International)')

st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig6, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# RATING DISTRIBUTION
rating_counts = df_pre_origin.groupby(['rating', 'content_origin']).size().reset_index(name='count')
rating_order = df_pre_origin['rating'].value_counts().index.tolist()

fig7 = px.bar(
    rating_counts, y='rating', x='count', color='content_origin',
    orientation='h', color_discrete_sequence=['#FF4C4C', '#B22222'],
    category_orders={'rating': rating_order}
)
fig7 = update_fig_style(fig7, 'Rating Distribution by Origin')

st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig7, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

end_card()

st.markdown("---")


# -----------------------------
# PIE CHART SECTION: Country Contribution
# -----------------------------
glow_card("Country Contribution — Pie Chart")

all_count1 = df['country'].value_counts()

if len(all_count1) > 10:
    mcpctrs1 = all_count1.head(10).copy()
    mcpctrs1['Others'] = all_count1.iloc[10:].sum()
else:
    mcpctrs1 = all_count1.copy()

df_pie = mcpctrs1.reset_index()
df_pie.columns = ['Country', 'Count']

# Adjusted color palette for dark theme
new_colors_red_brown = [
    '#E50914', '#B20710', '#800000', '#A52A2A', '#CD853F',
    '#D2B48C', '#F5DEB3', '#DEB887', '#BC8F8F', '#A9A9A9', '#696969'
]
colors_for_plot = new_colors_red_brown[:len(df_pie)]

fig = px.pie(
    df_pie, values='Count', names='Country',
    color_discrete_sequence=colors_for_plot,
    height=700, hole=0.3
)
fig.update_traces(
    textinfo='percent+label',
    marker=dict(line=dict(color='#000000', width=2)), # Darker line for contrast
    textfont=dict(color="#FFFFFF"),
)

# Apply Dark Theme
fig = update_fig_style(fig, 'Top Country Contribution')
fig.update_layout(
    margin=dict(t=50, b=50), # Adjust margins for the pie chart
    showlegend=True
)

st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

end_card()
