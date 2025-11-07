import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os 


# Set screen width and inject custom CSS for styling
st.set_page_config(layout="wide")

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    /* 1. Document Background Color (Light Grey) */
    .stApp {
        background-color: #F0F0F0; /* Light Grey */
    }

    /* 2. Chart Container Styling (Round Border) */
    /* This targets the Streamlit wrapper around each Plotly chart to make it look like a card */
    div.stPlotlyChart {
        border: 1px solid #CCCCCC; 
        border-radius: 10px; 
        padding: 10px;
        background-color: white; /* Internal container background */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    }
    
    /* 3. Main title styling is now handled by the inline st.markdown below */
    
    /* Ensuring sidebar background is visible against the light grey app background */
    .css-1d391kg {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define the custom color sequence (Netflix theme: Red, Black, White)
NETFLIX_COLORS = ["#E50914", "#000000", "#FFFFFF"]
RED_COLORS = ["#E50914", "#9A1717", "#3E0000", "#230101"]


# Set the title of the Streamlit app (MODIFIED for color, alignment, and size)
st.markdown(
    "<h1 style='color: #E50914; text-align: center; font-size: 3em;'>Movie Releases Over Time</h1>", 
    unsafe_allow_html=True
)


# Define a standard theme update function, adjusting for the white container background
def update_chart_theme(fig, title):
    fig.update_layout(
        title={
            'text': title, 
            'font': {'color': 'black'} # Title text is black against white card background
        },
        plot_bgcolor='white', # FIX: Changed to white plot background
        paper_bgcolor='rgba(0,0,0,0)', # Transparent paper background shows the white CSS card
        font=dict(color="black"), # Default font color for outer elements
        margin=dict(t=50, b=50, l=50, r=50),
    )
    # Axis labels/ticks must be black and grid lines must be light grey against the white plot background
    fig.update_xaxes(
        showgrid=True, 
        gridcolor='#DDDDDD', # Lighter grid lines
        tickfont=dict(color="black"), 
        title_font=dict(color="black")
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor='#DDDDDD', # Lighter grid lines
        tickfont=dict(color="black"), 
        title_font=dict(color="black")
    )
    # Hover label text should also be black against a light background
    fig.update_layout(
        title_font_color='black',
        legend_font_color='black',
        hoverlabel_font_color='black'
    )
    return fig


# --- DATA LOADING (Initial Load) ---
csv_file_path = r'Plotting data\USA_release_oveYears.csv'
df_main = None
if not os.path.exists(csv_file_path):
    st.error(f"Error: The file '{csv_file_path}' was not found.")
    st.warning("Please make sure the CSV file is in the same directory as this Streamlit script.")
else:
    try:
        df_main = pd.read_csv(csv_file_path)
    except Exception as e:
        st.error(f"An error occurred while loading the main file: {e}")

col1, col2 = st.columns(2)

# --- LINE CHART (Section 1) ---
if df_main is not None:
    try:
        # --- 3. Create the Line Graph ---
        fig_line = px.line(
            df_main,
            x='release_year',
            y='united', # Using original column name
            title=' Movie Releases USA Over Time',
            labels={'release_year': 'Year', 'united': 'Number of Releases'},
            markers=True, 
            color_discrete_sequence=NETFLIX_COLORS, 
        )
        
        fig_line = update_chart_theme(fig_line, 'Movie Releases USA Over Time')
        fig_line.update_layout(hovermode="x unified")
        fig_line.update_xaxes(dtick=1) 

        # --- 4. Display the plot using Streamlit ---
        with col1:
           st.plotly_chart(fig_line, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while creating the Line Chart: {e}")



# --- PIE CHART AND SLIDER (Section 2) ---
if df_main is not None:
    try:
        df_pie = df_main.copy()
        df_pie['release_year'] = df_pie['release_year'].astype(int)

        # --- 3. Add a Slider for Year Filtering ---
        min_year = df_pie['release_year'].min()
        max_year = df_pie['release_year'].max()

        # The sidebar is shared across all widgets
        st.sidebar.header("Filter Data")
        year_range = st.sidebar.slider(
            "Select Year Range:",
            min_value=min_year,
            max_value=max_year,
            value=(max_year - 10, max_year),
            key='pie_slider' # Added key to prevent widget collision
        )

        filtered_df_pie = df_pie[
            (df_pie['release_year'] >= year_range[0]) & 
            (df_pie['release_year'] <= year_range[1])
        ]
        
        if filtered_df_pie.empty:
            with col2:
                 st.warning(f"No data available for the selected range: {year_range[0]} - {year_range[1]}.")
        else:
            # --- 4. Create the Pie Chart using Plotly Express ---
            fig_pie = px.pie(
                filtered_df_pie,
                names='release_year', 
                values='united',      # Using original column name
                title=f' Percentage of Movie Releases USA ({year_range[0]} - {year_range[1]})',
                color_discrete_sequence=RED_COLORS, 
                hole=0.3, 
            )

            fig_pie = update_chart_theme(
                fig_pie, 
                f'Percentage of Movie Releases USA ({year_range[0]} - {year_range[1]})'
            )

            fig_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                marker=dict(
                    line=dict(
                        color='white', 
                        width=2.5      
                    )
                ),
                hoverinfo='label+percent+value',
            )
            
            with col2:
              st.plotly_chart(fig_pie, use_container_width=True)


    except Exception as e:
        st.error(f"An unexpected error occurred in Pie Chart section: {e}")



# --- BAR CHART (Section 3) ---
if df_main is not None:
    try:
        df_bar = df_main.copy()
        df_bar['release_year'] = df_bar['release_year'].astype(int)

        min_year = df_bar['release_year'].min()
        max_year = df_bar['release_year'].max()

        st.markdown("---")
        st.subheader("Bar Chart Data Filter")
        bar_year_range = st.slider(
            "Select Year Range:",
            min_value=min_year,
            max_value=max_year,
            value=(max_year - 10, max_year),
            key='bar_slider'
        )

        filtered_df_bar = df_bar[
            (df_bar['release_year'] >= bar_year_range[0]) & 
            (df_bar['release_year'] <= bar_year_range[1])
        ].sort_values(by='release_year')
        
        if filtered_df_bar.empty:
            st.warning(f"No data available for the selected range: {bar_year_range[0]} - {bar_year_range[1]}.")
        else:
            # --- 4. Create the Bar Chart using Plotly Express ---
            fig_bar = px.bar(
                filtered_df_bar,
                x='release_year',
                y='united', # Using original column name
                title=f'Number of Movie Releases in the USA ({bar_year_range[0]} - {bar_year_range[1]})',
                labels={'release_year': 'Year', 'united': 'Number of Releases'},
                color_discrete_sequence=["#E50914"]
            )

            fig_bar = update_chart_theme(
                fig_bar, 
                f'Number of Movie Releases in the USA ({bar_year_range[0]} - {bar_year_range[1]})'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
    except Exception as e:
        st.error(f"An unexpected error occurred in Bar Chart section: {e}")



# --- MOCK CHART SECTION (Section 4: Advanced Analysis Charts) ---

st.markdown("---")
st.subheader("Advanced Analysis Charts")

# --- DATA PREPARATION FOR ADVANCED CHARTS (FIXED KEYERROR HERE) ---
# We create a new df for the advanced charts and ensure the renaming happens reliably.
df_adv = None
if os.path.exists(csv_file_path):
    try:
        df_adv = pd.read_csv(csv_file_path)
        df_adv['release_year'] = df_adv['release_year'].astype(int)
        
        # --- FIX: Rename column to 'Releases' consistently for this section ---
        df_adv.rename(columns={'united': 'Releases'}, inplace=True)
        
        # Mock function for Box Plots and Heatmaps 
        def create_mock_monthly_data(df):
            data = []
            for year in df['release_year'].unique():
                # Added try-except in case a year has no data, though iloc[0] assumes it exists
                try:
                    total_releases = df[df['release_year'] == year]['Releases'].iloc[0]
                except IndexError:
                    continue # Skip year if no release data found
                
                monthly_counts = np.random.dirichlet(np.ones(12) * 5, size=1)[0] 
                monthly_releases = (monthly_counts * total_releases).astype(int)
                
                diff = total_releases - monthly_releases.sum()
                if diff != 0:
                    monthly_releases[np.random.randint(0, 12)] += diff
                    
                for i, count in enumerate(monthly_releases):
                    data.append({
                        'Year': year, 
                        'Month': i + 1, 
                        'Releases': count
                    })
            return pd.DataFrame(data)

        # Data for Treemap (Hierarchical grouping)
        df_adv['Decade'] = (df_adv['release_year'] // 10 * 10).astype(str) + 's'

        # Data for Scatter Plot (Year vs. Count vs. Trend)
        df_adv['Avg_Releases'] = df_adv['Releases'].rolling(window=5, center=True).mean()
        df_adv['Above_Avg'] = df_adv['Releases'] > df_adv['Avg_Releases']

        # Data for Box Plot/Heatmap
        monthly_df = create_mock_monthly_data(df_adv)
        
    except Exception as e:
        st.error(f"An error occurred during data preparation for advanced charts: {e}")
        df_adv = None


if df_adv is not None and not monthly_df.empty: # Check if monthly_df was created
    col1_adv, col2_adv = st.columns(2) 

    # 1. Heatmaps: Two-dimensional patterns (Mocked Year vs. Month) - COL 1
    with col1_adv:
        fig_heatmap = px.density_heatmap(
            monthly_df, 
            x="Year", 
            y="Month", 
            z="Releases", 
            histfunc="sum",
            color_continuous_scale="Reds",
            title=("Year vs Montly release Heatmap"),
            labels={"Releases": "Total Releases"},
        )
        fig_heatmap.update_traces(xgap=1, ygap=1)
        
        fig_heatmap = update_chart_theme(fig_heatmap, "Year vs Montly release Heatmap")
        
        # Heatmap custom axes settings (to remove standard grid lines that look odd)
        fig_heatmap.update_xaxes(showgrid=False, tickfont=dict(color="black"), title_font=dict(color="black"))
        fig_heatmap.update_yaxes(showgrid=False, tickfont=dict(color="black"), title_font=dict(color="black"))

        st.plotly_chart(fig_heatmap, use_container_width=True)

    # 2. Treemaps: Hierarchical data (Decade > Year) - COL 2
    with col2_adv:
        # Calculate the total releases per Decade and Year for the Treemap
        treemap_df = df_adv.groupby(['Decade', 'release_year'])['Releases'].sum().reset_index()
        treemap_df['Year_Label'] = treemap_df['release_year'].astype(str)
        
        fig_treemap = px.treemap(
            treemap_df, 
            path=['Decade', 'Year_Label'], 
            values='Releases',
            title=("Treemap (Decade and Year Hierarchy)"),
            color_discrete_sequence=NETFLIX_COLORS, 
        )
        
        fig_treemap = update_chart_theme(fig_treemap, "Treemap (Decade and Year Hierarchy)")
        fig_treemap.data[0].textinfo = 'label+value'
        
        # Treemaps do not use conventional axes, so we clear the axis settings to avoid errors/warnings
        fig_treemap.update_xaxes(showgrid=False, zeroline=False, visible=False)
        fig_treemap.update_yaxes(showgrid=False, zeroline=False, visible=False)
        
        st.plotly_chart(fig_treemap, use_container_width=True)

    # Box plot - COL 1
    with col1_adv:
        fig_box = px.box(
            monthly_df, 
            x="Year", 
            y="Releases", 
            color="Year",
            title=(" Box Plot (Monthly Release Distribution Comparison)"),
            color_discrete_sequence=NETFLIX_COLORS, 
            labels={"Releases": "Monthly Releases"}
        )
        
        fig_box = update_chart_theme(fig_box, "Box Plot (Monthly Release Distribution Comparison)")

        st.plotly_chart(fig_box, use_container_width=True)

    # Scatter plots: Relationships between variables - COL 2
    with col2_adv:
        fig_scatter = px.scatter(
            df_adv, 
            x='release_year', 
            y='Releases',
            size='Releases',
            color='Above_Avg', 
            color_discrete_sequence=NETFLIX_COLORS, 
            title='Yearly Releases with 5-Year Average Trend',
            labels={'release_year': 'Year', 'Releases': 'Number of Releases', 'Above_Avg': 'Above 5Y Avg'},
        )
        
        fig_scatter = update_chart_theme(fig_scatter, 'Yearly Releases with 5-Year Average Trend')

        st.plotly_chart(fig_scatter, use_container_width=True)
elif df_adv is None:
    pass # Error already shown during data prep
else:
    st.warning("Could not generate advanced analysis charts due to empty mock data.")

    #netflix colors
netflix_red = "#E50914"
netflix_dark = "#141414"
netflix_gray = "#B3B3B3"
netflix_white = "#FFFFFF"



df = st.session_state['netflix_df'].copy()
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

# --- STEP 2: CLEANING ---

st.title("Top 5 Niche vs Mainstream Genres — IMDb Ratings")

# --- LOAD + CLEAN ---

df = df.dropna(subset=['genres', 'averageRating']).copy()

def clean_genres(x):
    if isinstance(x, list):
        return [g.strip() for g in x]
    return [g.strip() for g in str(x).split(',')]

df['genres'] = df['genres'].apply(clean_genres)

# --- GENRE RATING ANALYSIS ---
genre_df = df.explode('genres')
genre_rating = (
    genre_df.groupby('genres')['averageRating']
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

top_threshold = genre_rating['averageRating'].quantile(0.75)
bottom_threshold = genre_rating['averageRating'].quantile(0.25)

genre_rating['category'] = genre_rating['averageRating'].apply(
    lambda x: 'Niche' if x >= top_threshold else
              ('Mainstream' if x <= bottom_threshold else 'Balanced')
)

niche_top5 = genre_rating[genre_rating['category'] == 'Niche'].nlargest(5, 'averageRating')
mainstream_top5 = genre_rating[genre_rating['category'] == 'Mainstream'].nsmallest(5, 'averageRating')
top5_combined = pd.concat([niche_top5, mainstream_top5])

# --- PLOTLY PLOT (WHITE THEME) ---
fig = px.bar(
    top5_combined,
    x='averageRating',
    y='genres',
    color='averageRating',
    orientation='h',
    color_continuous_scale=['#FFB3B3', '#FF6F61', '#FF3B30', '#B00610'],  # Red gradient (light → dark)
    title='Top 5 Niche vs Mainstream Genres — IMDb Ratings',
    text='averageRating'
)

fig.update_layout(
    title=dict(font=dict(color='black', size=18)),
    xaxis=dict(
        title=dict(text='Average IMDb Rating', font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=True,
        gridcolor='rgba(0,0,0,0.08)'
    ),
    yaxis=dict(
        title=dict(text='Genre', font=dict(color='black')),
        tickfont=dict(color='black'),
        showgrid=False
    ),
    font=dict(family="Times New Roman", color='black', size=13),
    plot_bgcolor='white',
    paper_bgcolor='white',
    coloraxis_colorbar=dict(
    title=dict(text="Rating", font=dict(color='black')),
    tickfont=dict(color='black')
)

)

fig.update_traces(
    texttemplate='%{text:.2f}',
    textposition='outside',
    marker_line_color='black',
    marker_line_width=1.1
)

st.plotly_chart(fig, width="stretch")