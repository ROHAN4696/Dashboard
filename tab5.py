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

# Scatter plots: Relationships between variables (Year vs. Count, colored by trend) - COL 2
with col2:
    fig = px.scatter(
        df, 
        x='release_year', 
        y='Releases',
        size='Releases',
        color='Above_Avg', # Color based on whether releases were above 5-year average
        color_discrete_sequence=NETFLIX_COLORS, # Apply the requested color sequence
        title='Yearly Releases with 5-Year Average Trend',
        labels={'release_year': 'Year', 'Releases': 'Number of Releases', 'Above_Avg': 'Above 5Y Avg'},
    )
    st.plotly_chart(fig, use_container_width=True)

