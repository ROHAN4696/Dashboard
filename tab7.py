import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="Strategic Recommendations Dashboard"
)

# --- Netflix Theme CSS (Metamorphic Update) ---
# UPDATES:
# 1. Page background set to deep black (#181818) for classic Netflix feel.
# 2. Strategy and Corporate cards are given a unified, slightly lighter background (#212121) to appear "extruded."
# 3. Metamorphic/Neumorphic box shadows are applied to the cards for a smooth, three-dimensional look on the dark surface.
# 4. Hover effects are added to make the cards subtly lift up, enhancing the interaction.
#
netflix_theme_css = f"""
<style>
/* 1. Page Background: Deep Netflix Black */
html, body, [data-testid="stAppViewContainer"], .main {{
    background-color: #181818 !important; 
}}

/* Main Title (Netflix Red with a SIGNIFICANT White Glow) */
h1 {{
    color: #E50914; /* Netflix Red */
    # text-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 0 0 5px #E50914; /* White glow + subtle red core */
    text-align: center;
    font-weight: 900;
    padding-bottom: 25px;
    padding-top: 25px;
    letter-spacing: 2px;
}}

/* Sub-headers for sections (Pure White with SIGNIFICANT glow) */
h2 {{
    color: #FFFFFF; /* Pure White */
    # text-shadow: 0 0 15px rgba(255, 255, 255, 0.6); /* Significant white glow */
    font-weight: 700;
    border-bottom: 1px solid #333333; /* Darker border */
    padding-bottom: 15px;
    margin-top: 40px;
}}

/* --- Metamorphic Strategy Card Style --- */
.strategy-card {{
    background-color: #212121; /* Card background, slightly lighter than page */
    /* Metamorphic shadows: top/left for highlight, bottom/right for depth */
    # box-shadow: 
    #     -5px -5px 10px rgba(40, 40, 40, 0.9), /* Darker top/left shadow (simulating recess) */
    #     5px 5px 10px rgba(0, 0, 0, 0.7); /* Deep black bottom/right shadow (simulating extrusion) */
    border-radius: 12px; /* Slightly more rounded corners */
    padding: 24px;
    height: 380px; /* Fixed height maintained */
    display: flex;
    flex-direction: column;
    transition: all 0.2s ease-in-out;
}}

.strategy-card:hover {{
    transform: translateY(-3px); /* Subtle lift on hover */
    # box-shadow: 
    #     -8px -8px 15px rgba(45, 45, 45, 0.9),
    #     8px 8px 15px rgba(0, 0, 0, 0.8);
}}

/* Strategy Title (inside the card - Kept Red) */
.strategy-card h3 {{
    color: #E50914; /* Red Title */
    font-weight: bold;
    font-size: 1.4rem; 
    border-bottom: none; 
    padding-bottom: 0;
    margin-bottom: 15px; 
    margin-top: 0;
}}

/* Strategy Text (inside the card) */
.strategy-card p {{
    color: #CCCCCC; /* Lighter grey for body text */
    font-size: 1.05rem;
    flex-grow: 1; 
    text-align: justify; 
}}

/* --- Prominent Corporate Card Style (Metamorphic + Accent) --- */
.corporate-card {{
    background-color: #212121; /* Card background, same as strategy card */
    border: 1px solid none; /* Red border maintained */
    # box-shadow: 
    #     -5px -5px 15px rgba(229, 9, 20, 0.1), /* Subtle Red Highlight */
    #     5px 5px 15px rgba(0, 0, 0, 0.8); /* Deep Black Shadow */
    border-radius: 12px;
    padding: 24px;
    height: 300px; /* Fixed height maintained */
    display: flex;
    flex-direction: column;
    transition: all 0.2s ease-in-out;
}}

.corporate-card:hover {{
    transform: translateY(-5px); /* Stronger lift for corporate focus */
    # box-shadow: 
    #     0 0 30px rgba(229, 9, 20, 0.4), /* Intense Red Glow on hover */
    #     0 0 20px rgba(0, 0, 0, 1);
}}

/* Corporate Title (inside the card - Kept Red) */
.corporate-card h3 {{
    color: #E50914; 
    font-weight: 900; /* Extra bold */
    font-size: 1.5rem; 
    margin-top: 0;
    margin-bottom: 20px; 
}}

/* Corporate Text (inside the card) */
.corporate-card p {{
    color: #FFFFFF; /* Bright White */
    font-size: 1.1rem;
    flex-grow: 1;
    text-align: justify; 
}}
</style>
"""

# Inject the custom CSS
st.markdown(netflix_theme_css, unsafe_allow_html=True)

# --- Dashboard Content ---

# 1. Main Title
st.markdown("<h1 style='color:#E50914; font-weight:900; text-align:center; padding-top:20px; padding-bottom:20px;'>Strategic Recommendations</h1>", unsafe_allow_html=True)

# --- SECTION 1: Market & Retention Strategies (4 Cards) ---
st.markdown("<h2 style='color:white; font-weight:900; margin-top:40px;'>Market & Retention Strategies</h2>", unsafe_allow_html=True)

# Define the data for this section
strategies_market = [
    {
        "title": "Prioritize Family/General Audience Content",
        "text": "Implement a content strategy that actively diversifies the catalog by investing in family and general audience content to achieve balanced viewership and expand the total addressable market."
    },
    {
        "title": "Target High-Priority Country-Genre Combinations",
        "text": "Utilize the priority score formula (based on growth and representation) to guide content commissioning, focusing on underrepresented catalogs in specific countries/genres that demonstrate high growth potential."
    },
    {
        "title": "Sustain Investment in Series",
        "text": "Continue the strategic focus on TV shows, as the rising Content Focus Ratio (CFR) indicates this is a key driver for long-term user retention."
    },
    {
        "title": "Leverage High-Rated Niche Content",
        "text": "Increase focus on genres with a High-Rating Title Ratio (HRTR), such as Classic & Cult TV and Classic Movies. High-quality niche content can be a strong differentiator."
    }
]

# Create the 1x4 Grid
cols_market = st.columns(4, gap="medium")
for i, col in enumerate(cols_market):
    with col:
        st.markdown(f"""
        <div class="strategy-card">
            <h3>{strategies_market[i]['title']}</h3>
            <p>{strategies_market[i]['text']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- SECTION 2: High-Value Acquisition Targets (3 Cards) ---
st.markdown("<h2 style='color:white; font-weight:900; margin-top:40px;'>High-Value Acquisition Targets</h2>", unsafe_allow_html=True)

# Define the data for this section
strategies_acquisition = [
    {
        "title": "Invest in High-Satisfaction Genres",
        "text": "Aggressively invest in high-quality acquisitions and originals within the Classic Movies, Classic & Cult TV, and Anime Series genres. These genres show the highest average ratings (Avg. Rating > 7.0), indicating a highly satisfied and engaged niche audience."
    },
    {
        "title": "Focus on Globally Stable Content",
        "text": "Classic movies maintain a high average rating consistently across the United States, India, and the United Kingdom. This global stability makes it a low-risk, high-satisfaction content category that appeals strongly across diverse markets."
    },
    {
        "title": "Secure Premium Documentary Content",
        "text": "Secure premium documentary and factual content, specifically within the science and nature TV category. This genre shows robust average ratings, particularly in the UK and India, attracting audiences seeking educational content."
    }
]

# Create the 1x3 Grid
cols_acq = st.columns(3, gap="medium")
for i, col in enumerate(cols_acq):
    with col:
        st.markdown(f"""
        <div class="strategy-card">
            <h3>{strategies_acquisition[i]['title']}</h3>
            <p>{strategies_acquisition[i]['text']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- SECTION 3: Core Corporate & Financial Directives (2 Cards) ---
st.markdown("<h2 style='color:white; font-weight:900; margin-top:40px;'>Core Corporate & Financial Directives</h2>", unsafe_allow_html=True)

# Define the data for this section
strategies_corporate = [
    {
        "title": "Content & Creator Allocation Strategy",
        "text": "The highest priority is allocating capital to create and expand ownable Intellectual Property (IP), such as Stranger Things & Squid Game. This creates permanent assets that build a competitive 'moat' and can be monetized across sequels, games, and merchandise."
    },
    {
        "title": "Financial & Competitive Strategy", 
        "text": "The company is now highly profitable. After funding all content and operations, its excess free cash flow is allocated to retiring debt and executing a large-scale stock buyback program to return capital to shareholders."
    }
]

# Create the 1x2 Grid using the new .corporate-card style
cols_corp = st.columns(2, gap="medium")
for i, col in enumerate(cols_corp):netflix_theme_css = """
<style>

/* --- GLOBAL PAGE BACKGROUND (True Netflix Black) --- */
html, body, [data-testid="stAppViewContainer"], .main {
    background-color: #0D0D0D !important;
}

/* --- MAIN TITLE (Cinematic Netflix Glow) --- */
h1 {
    color: #FFFFFF;
    font-weight: 900;
    text-align: center;
    letter-spacing: 2px;
    padding-top: 25px;
    padding-bottom: 25px;

    text-shadow:
        0 0 25px rgba(229, 9, 20, 0.9),
        0 0 10px rgba(229, 9, 20, 0.8),
        0 0 5px rgba(255, 255, 255, 0.5);
}

/* --- SECTION HEADERS (Clean Netflix White) --- */
h2 {
    color: #FFFFFF;
    font-weight: 700;
    margin-top: 40px;
    padding-bottom: 10px;

    text-shadow:
        0 0 12px rgba(255, 255, 255, 0.35);

    border-bottom: 2px solid #E50914;
}

/* --- UNIVERSAL CARD STYLE (Premium Netflix Look) --- */
.strategy-card, .corporate-card {
    background: linear-gradient(145deg, #1A1A1A, #111111);
    border-radius: 14px;

    padding: 24px;
    height: 380px;

    box-shadow:
        0 0 25px rgba(0, 0, 0, 0.8),
        inset 0 0 10px rgba(255, 255, 255, 0.03),
        inset 0 0 25px rgba(0, 0, 0, 0.7);

    transition: all 0.25s ease-in-out;
    display: flex;
    flex-direction: column;
}

/* --- HOVER EFFECT (Smooth Elevation) --- */
.strategy-card:hover, .corporate-card:hover {
    transform: scale(1.02);
    box-shadow:
        0 0 45px rgba(229, 9, 20, 0.45),
        0 0 25px rgba(255, 255, 255, 0.1);
}

/* --- CARD TITLE (Netflix Red, Elegant) --- */
.strategy-card h3, .corporate-card h3 {
    color: #E50914;
    font-size: 1.45rem;
    margin-top: 0;
    margin-bottom: 15px;

    text-shadow:
        0 0 12px rgba(229, 9, 20, 0.65),
        0 0 5px rgba(229, 9, 20, 0.4);
}

/* --- CARD BODY TEXT (Clean Grey) --- */
.strategy-card p, .corporate-card p {
    color: #D4D4D4;
    font-size: 1.07rem;
    text-align: justify;
    flex-grow: 1;
    line-height: 1.55;
}

/* --- SPECIAL CORPORATE CARD OVERRIDES (Highlight Tier) --- */
.corporate-card {
    border: 1px solid rgba(229, 9, 20, 0.85);
    height: 320px;

    box-shadow:
        0 0 20px rgba(229, 9, 20, 0.25),
        0 0 10px rgba(0, 0, 0, 0.9),
        inset 0 0 20px rgba(229, 9, 20, 0.15);
}

.corporate-card:hover {
    transform: scale(1.03);
    box-shadow:
        0 0 45px rgba(229, 9, 20, 0.75),
        0 0 30px rgba(255, 255, 255, 0.15);
}
</style>
"""

# Define the data for this section
strategies_corporate = [
    {
        "title": "Content & Creator Allocation Strategy",
        "text": "The highest priority is allocating capital to create and expand ownable Intellectual Property (IP), such as Stranger Things & Squid Game. This creates permanent assets that build a competitive 'moat' and can be monetized across sequels, games, and merchandise."
    },
    {
        "title": "Financial & Competitive Strategy", 
        "text": "The company is now highly profitable. After funding all content and operations, its excess free cash flow is allocated to retiring debt and executing a large-scale stock buyback program to return capital to shareholders."
    }
]

# Create the 1x2 Grid using the new .corporate-card style
cols_corp = st.columns(2, gap="medium")
for i, col in enumerate(cols_corp):
    with col:
        st.markdown(f"""
        <div class="corporate-card">
            <h3>{strategies_corporate[i]['title']}</h3>
            <p>{strategies_corporate[i]['text']}</p>
        </div>
        """, unsafe_allow_html=True)
