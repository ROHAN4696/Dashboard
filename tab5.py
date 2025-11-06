import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os # Import os for better path handling



#set screen width
st.set_page_config(layout="wide")

# Define the custom color sequence (Netflix theme: Red, Black, White)
NETFLIX_COLORS = ["#E50914", "#000000", "#FFFFFF"]


# Set the title of the Streamlit app
st.title("Movie Releases Over Time")

# --- 1. Define the file path ---
# Use the full path or ensure 'yearly_united_counts.csv' is in the same folder as this script
csv_file_path = r'Plotting data\USA_release_oveYears.csv'

# --- 2. Read the CSV file into a DataFrame ---
if not os.path.exists(csv_file_path):
    st.error(f"Error: The file '{csv_file_path}' was not found.")
    st.warning("Please make sure the CSV file is in the same directory as this Streamlit script.")
else:
    try:
        df = pd.read_csv(csv_file_path)
        
        # --- 3. Create the Line Graph ---
        fig = px.line(
            df,
            x='release_year',
            y='united',
            title=' Movie Releases USA Over Time',
            labels={'release_year': 'Year', 'united': 'Number of Releases'},
            markers=True, # Optional: Add markers for better visibility of data points
            color_discrete_sequence=NETFLIX_COLORS, # Apply the requested color sequence
        )
        
        # Make the chart more readable/interactive
        fig.update_layout(hovermode="x unified")
                   # Customize layout for better appearance and visibility of white slices
        fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="white"),
                margin=dict(t=50, b=0, l=0, r=0),
            )
        fig.update_xaxes(dtick=1) # Ensure every year is labeled on the x-axis

        # --- 4. Display the plot using Streamlit ---
        col1, col2 = st.columns(2)
        with col1:
         st.plotly_chart(fig, use_container_width=True)


    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")





# --- 1. Define the file path ---
# Path remains the same as requested
csv_file_path = r'Plotting data\USA_release_oveYears.csv'



# --- 2. Read the CSV file into a DataFrame ---
if not os.path.exists(csv_file_path):
    st.error(f"Error: The file '{csv_file_path}' was not found.")
    st.warning("Please make sure the CSV file is in the correct path relative to this script.")
else:
    try:
        df = pd.read_csv(csv_file_path)

        # Convert release_year to int for filter compatibility
        df['release_year'] = df['release_year'].astype(int)

        # --- 3. Add a Slider for Year Filtering ---
        # A pie chart works best on a subset of data rather than an entire time series.
        min_year = df['release_year'].min()
        max_year = df['release_year'].max()

        st.sidebar.header("Filter Data")
        year_range = st.sidebar.slider(
            "Select Year Range:",
            min_value=min_year,
            max_value=max_year,
            value=(max_year - 10, max_year) # Default to last 10 years
        )

        # Filter the DataFrame based on the selection
        filtered_df = df[
            (df['release_year'] >= year_range[0]) & 
            (df['release_year'] <= year_range[1])
        ]
        
        if filtered_df.empty:
            st.warning(f"No data available for the selected range: {year_range[0]} - {year_range[1]}.")
        else:
            # --- 4. Create the Pie Chart using Plotly Express ---
            fig = px.pie(
                filtered_df,
                names='release_year', # The years become the slices/categories
                values='united',      # The number of releases determines slice size
                title=f' Percentage of Movie Releases USA ({year_range[0]} - {year_range[1]})',
                color_discrete_sequence=NETFLIX_COLORS, # Apply the requested color sequence
                hole=0.4,
            )

            # Customize layout for better appearance and visibility of white slices
            fig.update_layout(
                plot_bgcolor='#111111', # Dark plot background to contrast white slices/text
                paper_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="white"),
                margin=dict(t=50, b=0, l=0, r=0),
            )

            # Customize the appearance of the slices (text and outline)
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                marker=dict(line=dict(color='#333333', width=1.5)), # Add a dark border to slices
                hoverinfo='label+percent+value',
            )

            # Display the Pie Chart
            with col2:
             st.plotly_chart(fig, use_container_width=True)
            

    except pd.errors.EmptyDataError:
        st.error("Error: The CSV file is empty.")
    except pd.errors.ParserError:
        st.error("Error: Could not parse the CSV file. Check the file format.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")



# Bar Chart

# --- 1. Define the file path ---
csv_file_path = r'Plotting data\USA_release_oveYears.csv'

# --- 2. Read the CSV file into a DataFrame ---
if not os.path.exists(csv_file_path):
    st.error(f"Error: The file '{csv_file_path}' was not found.")
    st.warning("Please make sure the CSV file is in the correct path relative to this script.")
else:
    try:
        df = pd.read_csv(csv_file_path)

        # Convert release_year to int for filter compatibility
        df['release_year'] = df['release_year'].astype(int)

        # --- 3. Add a Slider for Year Filtering ---
        min_year = df['release_year'].min()
        max_year = df['release_year'].max()

        year_range = st.slider(
            "Select Year Range:",
            min_value=min_year,
            max_value=max_year,
            value=(max_year - 10, max_year) # Default to last 10 years
        )

        # Filter the DataFrame based on the selection
        filtered_df = df[
            (df['release_year'] >= year_range[0]) & 
            (df['release_year'] <= year_range[1])
        ].sort_values(by='release_year') # Ensure years are sorted for time series visualization
        
        if filtered_df.empty:
            st.warning(f"No data available for the selected range: {year_range[0]} - {year_range[1]}.")
        else:
            # --- 4. Create the Bar Chart using Plotly Express ---
            fig = px.bar(
                filtered_df,
                x='release_year',
                y='united',
                title=f'Number of Movie Releases in the USA ({year_range[0]} - {year_range[1]})',
                labels={'release_year': 'Year', 'united': 'Number of Releases'},
                color_discrete_sequence=["#E50914"] # Apply the requested Netflix Red color
            )

            # Customize layout for Netflix dark theme
            fig.update_layout(
                font=dict(color="white"),
                margin=dict(t=50, b=50, l=50, r=50),
            )
            
            # Customize axes appearance for clarity
            fig.update_xaxes(
                type='category', # Treat x-axis as discrete categories (years)
        
                showgrid=False,
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
            fig.update_yaxes(
                showgrid=True,
                gridcolor='#333333',
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )

            # Display the Bar Chart
            with col1:
             st.plotly_chart(fig, use_container_width=True)
            
    except pd.errors.EmptyDataError:
        st.error("Error: The CSV file is empty.")
    except pd.errors.ParserError:
        st.error("Error: Could not parse the CSV file. Check the file format.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


NETFLIX_COLOR = "#E50914" 
COLORS = px.colors.sequential.Plotly3 # Use a sequential palette for variety

# --- 2. Data Loading and Base Preparation ---
if not os.path.exists(csv_file_path):
    st.error(f"Error: The file '{csv_file_path}' was not found.")
    st.stop()
    
try:
    df = pd.read_csv(csv_file_path)
    df['release_year'] = df['release_year'].astype(int)
    # Rename for consistency
    df.rename(columns={'united': 'Releases'}, inplace=True)
except Exception as e:
    st.error(f"An error occurred during data loading: {e}")
    st.stop()

# --- 3. Mock Data Generation for Complex Charts ---

# Mock function for Box Plots and Heatmaps (creates synthetic monthly distribution)
def create_mock_monthly_data(df):
    data = []
    for year in df['release_year'].unique():
        # Get the actual total release count for that year
        total_releases = df[df['release_year'] == year]['Releases'].iloc[0]
        
        # Generate 12 random numbers that sum up roughly to the total releases
        # Using a Dirichlet distribution for a weighted, randomized split
        monthly_counts = np.random.dirichlet(np.ones(12) * 5, size=1)[0] 
        monthly_releases = (monthly_counts * total_releases).astype(int)
        
        # Adjust the sum precisely
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
df['Decade'] = (df['release_year'] // 10 * 10).astype(str) + 's'

# Data for Scatter Plot (Year vs. Count vs. Trend)
df['Avg_Releases'] = df['Releases'].rolling(window=5, center=True).mean()
df['Above_Avg'] = df['Releases'] > df['Avg_Releases']

# Data for Box Plot/Heatmap
monthly_df = create_mock_monthly_data(df)

# Mock data for Sankey/Network/Word Cloud Replacements (for visual variety)
# Using a dummy DataFrame for funnels/flows (as proxy for Sankey/Network)
funnel_df = pd.DataFrame({
    'Stage': ['Idea', 'Screenplay', 'Production', 'Release'],
    'Count': [1000, 750, 500, 450],
    'Color': [NETFLIX_COLOR, '#FF5C5C', '#FFA3A3', '#FFDADA']
})


# --- 4. Dashboard Layout and Chart Generation ---
col1, col2 = st.columns(2)

# Define a standard dark theme update for Plotly figures
def update_dark_theme(fig, title):
    fig.update_layout(
        title=title,
        plot_bgcolor='#111111', 
        paper_bgcolor='#000000', 
        font=dict(color="white"),
        margin=dict(t=50, b=50, l=50, r=50),
    )
    fig.update_xaxes(showgrid=True, gridcolor='#333333', tickfont=dict(color="white"), title_font=dict(color="white"))
    fig.update_yaxes(showgrid=True, gridcolor='#333333', tickfont=dict(color="white"), title_font=dict(color="white"))
    return fig

# --- Chart Definitions (8 Total, Alternating Columns) ---

# 1. Heatmaps: Two-dimensional patterns (Mocked Year vs. Month) - COL 1
with col1:
    fig = px.density_heatmap(
        monthly_df, 
        x="Year", 
        y="Month", 
        z="Releases", 
        histfunc="sum",
        color_continuous_scale="Reds",
        title=("Year vs Montly release Heatmap"),
        labels={"Releases": "Total Releases"},
    )
    fig.update_traces(xgap=1, ygap=1,
                      )
 # Customize axes appearance for clarity
    fig.update_xaxes(
                type='category', # Treat x-axis as discrete categories (years)
                showgrid=False,
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
    fig.update_yaxes(
                showgrid=True,
                gridcolor='#333333',
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
    st.plotly_chart(fig, use_container_width=True)

# 2. Treemaps: Hierarchical data (Decade > Year) - COL 2
with col2:
    # Calculate the total releases per Decade and Year for the Treemap
    treemap_df = df.groupby(['Decade', 'release_year'])['Releases'].sum().reset_index()
    treemap_df['Year_Label'] = treemap_df['release_year'].astype(str)
    
    fig = px.treemap(
        treemap_df, 
        path=['Decade', 'Year_Label'], 
        values='Releases',
        title=("Treemap (Decade and Year Hierarchy)"),
      color_discrete_sequence=NETFLIX_COLORS, # Apply the requested color sequence
    )
    fig.update_xaxes(
                type='category', # Treat x-axis as discrete categories (years)
                showgrid=False,
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
    fig.update_yaxes(
                showgrid=True,
                gridcolor='#333333',
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
    fig.data[0].textinfo = 'label+value'
   
    st.plotly_chart(fig, use_container_width=True)
# Box plot
with col1:
    fig = px.box(
        monthly_df, 
        x="Year", 
        y="Releases", 
        color="Year",
        title=(" Box Plot (Monthly Release Distribution Comparison)"),
        color_discrete_sequence=NETFLIX_COLORS, # Apply the requested color sequence
        labels={"Releases": "Monthly Releases"}
    )
  # Customize axes appearance for clarity
    fig.update_xaxes(
                type='category', # Treat x-axis as discrete categories (years)
                showgrid=False,
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
    fig.update_yaxes(
                showgrid=True,
                gridcolor='#333333',
                tickfont=dict(color="black"),
                title_font=dict(color="black")
            )
    st.plotly_chart(fig, use_container_width=True)

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

