import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# REMOVED: from sklearn.feature_extraction.text import CountVectorizer

st.set_page_config(layout="wide", page_title="Netflix Insights Dashboard")

# ---------------------------------------------------------
# METAMORPHIC NEON GLOW CSS (APPLIED)
# ---------------------------------------------------------
st.markdown("""
<style>

/* Main App background */
.stApp {
	background-color: #000000 !important;
}

:root {
	--netflix-red: #E50914;
	--netflix-red-soft: rgba(229, 9, 20, 0.45);
	--netflix-red-glow: rgba(229, 9, 20, 0.75);
	--card-bg: #111111;
	--card-border: #1f1f1f;
}

/* --- TITLES & HEADERS NEON GLOW --- */
h1, h2, h3, h4, h5, .st-emotion-cache-10trblm { /* .st-emotion-cache-10trblm targets titles in Streamlit */
	color: var(--netflix-red) !important;
	text-shadow:
		0 0 8px var(--netflix-red-soft),
		0 0 14px var(--netflix-red-glow),
		0 0 22px var(--netflix-red-glow);
	font-weight: 700 !important;
}

/* --- METAMORPHIC GLOW CARD --- */
.glow-card {
	background: var(--card-bg);
			
	padding: 30px 35px;
	border-radius: 16px;
	border: 1px solid var(--card-border);
	margin-top: 25px;
	margin-bottom: 35px;
	box-shadow:
		inset 0 0 25px rgba(255, 255, 255, 0.05),
		0 0 20px rgba(229, 9, 20, 0.25),
		0 0 35px rgba(229, 9, 20, 0.35),
		0 0 55px rgba(229, 9, 20, 0.45);
	transition: all 0.35s ease-in-out;
}

.glow-card:hover {
	transform: translateY(-5px);
	box-shadow:
		inset 0 0 35px rgba(255, 255, 255, 0.08),
		0 0 35px rgba(229, 9, 20, 0.55),
		0 0 55px rgba(229, 9, 20, 0.75),
		0 0 85px rgba(229, 9, 20, 0.9);
}

/* Chart container glow */
.chart-wrap {
	background: #0c0c0c;
	padding: 18px;
	border-radius: 12px;
	box-shadow: 0 0 22px rgba(229, 9, 20, 0.4);
}

/* KPI Box adjustments for dark theme */
.info-box {
	border: 1px solid var(--card-border);
	padding: 14px;
	border-radius: 8px;
	background-color: var(--card-bg);
	width: 100% !important; /* Adjusted width */
	margin-left: auto;
	margin-right: auto;
	color: white; /* Text color */
}
/* Ensure text inside info-box's b tags is also white */
.info-box b {
	color: white !important;
}

</style>
""", unsafe_allow_html=True)

# Centering the main title using HTML markdown and increasing font size to approx 1.5x of default H1
st.markdown("<h1 style='text-align: center; font-size: 3.75rem;'>Netflix Analysis Dashboard</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARD WRAPPERS
# ---------------------------------------------------------
def glow_card(title: str):
	st.markdown(f"<div class='glow-card' 	;><h2 >{title}</h2>", unsafe_allow_html=True)

def end_card():
	st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PLOTLY THEME HELPER
# ---------------------------------------------------------
def update_fig_style(fig, title):
	fig.update_layout(
		plot_bgcolor='black',
		paper_bgcolor='black',
		font=dict(family='Times New Roman', color='white', size=14),
		title=dict(text=title, x=0.5, font=dict(color="#E50914")),
		xaxis=dict(showgrid=True, gridcolor='#333333', linecolor='white'),
		yaxis=dict(showgrid=True, gridcolor='#333333', linecolor='white'),
	)
	return fig


# =========================================================
# ✅ SECTION 1 — Pie Chart (Top-10 + Others) - PLOTLY
# =========================================================

glow_card("Top Country Content Distribution")

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
			hole=0.3,
			textfont=dict(color='white')
		)
		
		# Apply dark theme style
		fig1.update_layout(
			plot_bgcolor='black',
			paper_bgcolor='black',
			title=dict(text='Content Distribution (Top 10 + Others)', x=0.5, font=dict(color="#E50914")),
			font=dict(color='white'),
			margin=dict(t=30, b=0, l=0, r=0),
			legend=dict(font=dict(color='white'))
		)

		st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
		st.plotly_chart(fig1, use_container_width=True)
		st.markdown("</div>", unsafe_allow_html=True)

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
end_card()

# =========================================================
# ✅ SECTION 2 & 3 — Lag & Growth (Applying Theme)
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
		.reset_index(name='lag_days')
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
	glow_card("Average Lag: Release to Netflix Add Date")
	
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
		
		# Apply dark theme style
		fig2 = update_fig_style(fig2, 'Avg Lag: Release → Netflix Add (Movies vs TV)')
		fig2.update_traces(line=dict(width=3), marker=dict(size=8))
		
		st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
		st.plotly_chart(fig2, use_container_width=True)
		st.markdown("</div>", unsafe_allow_html=True)

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
	end_card()


	# =========================================================
	# ✅ SECTION 3 — YoY Growth Movies vs TV
	# =========================================================
	st.divider()
	glow_card("Year-over-Year Content Growth")

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

		# Apply dark theme style
		fig3 = update_fig_style(fig3, 'YoY Growth: Movies vs TV Shows (Since 2005)')
		fig3.update_layout(
			xaxis_title='Release Year',
			yaxis_title='YoY Growth',
			hovermode='x unified',
			height=500
		)

		st.markdown("<div class='chart-wrap'>", unsafe_allow_html=True)
		st.plotly_chart(fig3, use_container_width=True)
		st.markdown("</div>", unsafe_allow_html=True)

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
	end_card()


except KeyError:
	st.error("Please ensure the DataFrame is loaded into st.session_state['netflix_df'].")
except Exception as e:
	st.error(f"An error occurred loading or processing data for Plots 2 & 3: {e}")
