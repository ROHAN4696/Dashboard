import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os 



# # Input data files are available in the read-only "../input/" directory
# # For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory



# # Input data files are available in the read-only "../input/" directory
# # For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

# st.set_page_config(page_title="Netflix Actor Ratings Dashboard", layout="wide")

# csv_file_path = r'Plotting data\netflix_titles_with_imdb_ratings_2.csv'
# df2 = None
# if not os.path.exists(csv_file_path):
#     st.error(f"Error: The file '{csv_file_path}' was not found.")
#     st.warning("Please make sure the CSV file is in the same directory as this Streamlit script.")
# else:
#     try:
#         df2 = pd.read_csv(csv_file_path)
#     except Exception as e:
#         st.error(f"An error occurred while loading the main file: {e}")

# df2['genre']=df2['listed_in']
# df2.head()

# df2['genre'] = df2['genre'].str.split(',')

# # Remove extra spaces
# df2['genre'] = df2['genre'].apply(lambda x: [i.strip() for i in x])

# # Explode the list into separate rows
# df_exploded = df2.explode('genre', ignore_index=True)





# df_exploded['cast'] = df_exploded['cast'].str.split(',\s*')   # split on comma and optional spaces
# df1 = df_exploded.explode('cast')




# df1 = df1[df1['cast'].notna()]                  
# df1 = df1[df1['cast'].str.strip() != '']



# netflix_reds = ["#F28C8C", "#D82E2F", "#B01717", "#800000", "#400000"]






# top5_genres = df1['genre'].value_counts().nlargest(5).index
# top5_cast_genre = (
#     df1[df1['genre'].isin(top5_genres)]
#     .groupby(['genre', 'cast']).size()
#     .reset_index(name='count')
# )

# top5_cast_genre = top5_cast_genre.groupby('genre', group_keys=False).apply(lambda x: x.nlargest(5, 'count'))

# fig = px.bar(
#     top5_cast_genre,
#     x='cast', y='count', color='genre',
#     barmode='group',
#     color_discrete_sequence=netflix_reds,
#     title="Top 5 Cast Members in Each of the Top 5 Genres"
# )

# fig.update_layout(
#     plot_bgcolor='white', paper_bgcolor='white', title_x=0.5,
#     xaxis_title="Cast", yaxis_title="Count of Titles"
# )
# fig.update_xaxes(tickangle=45)
# st.plotly_chart(fig, use_container_width=True)



# top5_countries = df1['country'].value_counts().nlargest(5).index
# top3_cast_country = (
#     df1[df1['country'].isin(top5_countries)]
#     .groupby(['country', 'cast']).size()
#     .reset_index(name='count')
# )

# top3_cast_country = top3_cast_country.groupby('country', group_keys=False).apply(lambda x: x.nlargest(3, 'count'))

# fig = px.bar(
#     top3_cast_country,
#     x='cast', y='count', color='country',
#     barmode='group',
#     color_discrete_sequence=netflix_reds,
#     title="Top 3 Cast Members in Each of the Top 5 Content-Producing Countries"
# )

# fig.update_layout(
#     plot_bgcolor='white', paper_bgcolor='white', title_x=0.5,
#     xaxis_title="Cast", yaxis_title="Count of Titles"
# )
# fig.update_xaxes(tickangle=45)
# st.plotly_chart(fig, use_container_width=True)



# # Find out top 10 content producing countries' genre
# top10_countries = df_exploded['country'].value_counts().head(10).index
# df_top = df_exploded[df_exploded['country'].isin(top10_countries)]
# df_top



# top5_countries = top10_countries[:4]

# # Netflix-inspired gradient palette for genres (expandable if more genres exist)
# netflix_gradient = [
#     "#7A0000",  # Dark crimson
#     "#9B0000",
#     "#B00000",
#     "#C61C0A",
#     "#E50914",  # Netflix red
#     "#F45B4D",
#     "#F97C6C",
#     "#FCA08A",
#     "#FEC8B0"
# ]

# # Create faceted histogram: separate columns for each country
# fig = px.histogram(
#     df_top[df_top['country'].isin(top5_countries)],
#     y='genre',
#     color='genre',                    # color by genre, not country
#     facet_col='country',              # one column per country
#     category_orders={'country': top5_countries},
#     color_discrete_sequence=netflix_gradient
# )

# # Layout styling
# fig.update_layout(
#     plot_bgcolor='white',
#     paper_bgcolor='white',
#     title="Genre Distribution Across Top 4 Content-Producing Countries (Netflix)",
#     title_x=0.5,
#     yaxis_title="Genre",
#     font=dict(size=14, color='black'),
#     legend_title="Genre",
#     bargap=0.2
# )

# # Improve readability
# fig.update_yaxes(autorange="reversed")
# fig.update_xaxes(showgrid=True)
# st.plotly_chart(fig, use_container_width=True)










# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Netflix Actor Ratings Dashboard", layout="wide")

csv_file_path = r'Plotting data\netflix_titles_with_imdb_ratings_2.csv'
df = None
if not os.path.exists(csv_file_path):
    st.error(f"Error: The file '{csv_file_path}' was not found.")
    st.warning("Please make sure the CSV file is in the same directory as this Streamlit script.")
else:
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        st.error(f"An error occurred while loading the main file: {e}")

# ---------------- LOAD DATA ----------------


# ---------------- DATA PROCESSING ----------------
df['cast'] = df['cast'].astype(str).str.split(', ')
df1 = df.explode('cast')
netflix = df1.dropna(subset=['cast', 'averageRating', 'country'])

# Split multiple actors into separate rows
cast_country_rating = (
    netflix.assign(actor=netflix['cast'].str.split(','))
    .explode('actor')
    .dropna(subset=['actor'])
)
cast_country_rating['actor'] = cast_country_rating['actor'].str.strip()

# Compute average rating of each actor per country
actor_country_rating = (
    cast_country_rating
    .groupby(['country', 'actor'], as_index=False)['averageRating']
    .mean()
)

# Keep top 15 actors by overall average rating
top_actors = (
    actor_country_rating.groupby('actor')['averageRating']
    .mean()
    .nlargest(15)
    .index
)
filtered_data = actor_country_rating[actor_country_rating['actor'].isin(top_actors)]




# ---------------- PLOT ----------------
fig = px.bar(
    filtered_data,
    x='actor',
    y='averageRating',
    color='country',
    title='IMDb Rating by Actor and Country',
    color_discrete_sequence=['#330000', '#660000', '#990000', '#cc0000', '#ff1a1a']  # Netflix palette
)

fig.update_layout(
    xaxis_title='Actor',
    yaxis_title='Average IMDb Rating',
    xaxis_tickangle=-45,
    template='plotly_white',
    font=dict(color='#221f1f', size=14),
    title_font=dict(size=22, color='#e50914', family='Arial Black'),
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend_title_text='Country',
)
fig.update_yaxes(range=[9, 10])
fig.update_traces(marker_line_color='#221f1f', marker_line_width=0.8)

st.plotly_chart(fig, use_container_width=True)


st.markdown("---")



# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Netflix Actor Distribution Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------


# ---------------- DATA PROCESSING ----------------
df['cast'] = df['cast'].astype(str).str.split(', ')
df1 = df.explode('cast')

# Drop rows with missing country or cast info
netflix = df1.dropna(subset=['country', 'cast'])

df = (
    netflix.assign(actor=netflix['cast'].str.split(','))
    .explode('actor')
    .dropna(subset=['actor'])
)
df['actor'] = df['actor'].str.strip()

# Remove duplicates — each (actor, country) counted once
df_unique = df.drop_duplicates(subset=['country', 'actor'])

# Find top 5 countries by number of *unique* actors
top_countries = df_unique['country'].value_counts().nlargest(5).index

# Filter to top 5 countries
df_top = df_unique[df_unique['country'].isin(top_countries)]

# Count unique actors per country
country_counts = df_top['country'].value_counts().reset_index()
country_counts.columns = ['country', 'unique_actor_count']

# ---------------- STREAMLIT UI ----------------
st.title("Netflix Actor Distribution Across Top 5 Countries")
st.markdown("### Explore which countries have the largest number of unique actors in Netflix titles")

# ---------------- PLOT ----------------
fig = px.bar(
    country_counts,
    x='country',
    y='unique_actor_count',
    color='unique_actor_count',
    color_continuous_scale=['#330000', '#660000', '#990000', '#cc0000', '#ff1a1a'],
    title='Cast Actors in Top 5 Countries'
)

fig.update_layout(
    xaxis_title='Country',
    yaxis_title='Number of Unique Actors',
    template='plotly_white',
    font=dict(color='#221f1f', size=14),
    title_font=dict(size=22, color='#e50914', family='Arial Black'),
    plot_bgcolor='white',
    paper_bgcolor='white',
    coloraxis_colorbar=dict(
        title='Actor Count',
        tickcolor='#221f1f',
        tickfont=dict(color='#221f1f')
    )
)

# Display Plotly figure
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

