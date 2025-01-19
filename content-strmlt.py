import streamlit as st
import google.generativeai as genai
import json
from content_finder import ContentFinder
import os

# Configure API keys directly in code
API_KEYS = {
    'REDDIT_CLIENT_ID': 'IW7JQMSzU-uCbp-0Gmi2lA',
    'REDDIT_CLIENT_SECRET': 'xxahjdPKNwpOtCjD1pWBahtx0pC67Q',
    'REDDIT_USER_AGENT': 'ContentFinder/1.0',
    'NEWS_API_KEY': '6829434b7662434e992ed2d0613b8d9d',
    'GEMINI_API_KEY': 'AIzaSyAkkgoutn9SEYg939Pb21Zi19rBwD93_5M'
}

# Set environment variables
for key, value in API_KEYS.items():
    os.environ[key] = value

# Custom CSS for better styling
st.set_page_config(page_title="Content Discovery Platform", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .stTitle {
        color: #1E88E5;
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        text-align: center;
    }
    
    /* Card styling */
    .css-1r6slb0 {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1565C0;
        transform: translateY(-2px);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Results card styling */
    .result-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Platform icons */
    .platform-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    /* Metrics styling */
    .metrics-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: #ffffff;
        border-radius: 5px;
        color: #1E88E5;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def main():
    # Header with gradient background
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1E88E5 0%, #64B5F6 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; text-align: center; font-size: 3rem; margin: 0;'>🔍 Content Discovery Platform</h1>
            <p style='color: white; text-align: center; font-size: 1.2rem; margin-top: 1rem;'>
                Discover relevant content across multiple platforms powered by AI
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Create tabs with custom styling
    tab1, tab2 = st.tabs(["📝 Input Business Insights", "🎯 Discovered Content"])

    with tab1:
        st.markdown("""
            <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
                <h2 style='color: #1E88E5; margin-bottom: 1rem;'>Business Insights</h2>
                <p style='color: #666;'>Fill in your business details to discover relevant content</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("business_insights_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            
            with col1:
                audience = st.text_area(
                    "🎯 Target Audience",
                    placeholder="e.g., Small business owners aged 30-50, primarily in urban areas",
                    help="Describe your target audience demographics, location, and characteristics",
                    height=150
                )
                
                pain_points = st.text_area(
                    "💡 Pain Points Addressed",
                    placeholder="e.g.,\nDifficulty in accessing analytics\nHigh costs of solutions",
                    help="List the main problems your product/service solves",
                    height=150
                )
            
            with col2:
                competitors = st.text_area(
                    "🏢 Competitors",
                    placeholder="e.g.,\nCompetitor A\nCompetitor B",
                    help="List your main competitors",
                    height=150
                )
                
                market_position = st.text_area(
                    "🎯 Market Position",
                    placeholder="e.g., Affordable and user-friendly platform for small businesses",
                    help="Describe your unique market position and value proposition",
                    height=150
                )

            submit_button = st.form_submit_button("🔎 Find Content", use_container_width=True)

            if submit_button:
                if not audience or not market_position:
                    st.error("⚠️ Please fill in at least the Audience and Market Position fields.")
                    return

                media_insights = {
                    "primaryAudienceDemographics": audience,
                    "painPointsAddressed": [p.strip() for p in pain_points.split('\n') if p.strip()],
                    "competitors": [c.strip() for c in competitors.split('\n') if c.strip()],
                    "marketPosition": market_position
                }

                st.session_state['media_insights'] = media_insights
                st.session_state['search_completed'] = False

    with tab2:
        if 'media_insights' in st.session_state and not st.session_state.get('search_completed', False):
            try:
                with st.spinner('🔍 Discovering relevant content across platforms...'):
                    finder = ContentFinder()
                    results = finder.find_targeted_content(
                        st.session_state['media_insights'],
                        max_results_per_query=3,
                        max_total_results=20,
                        max_queries_per_category=3
                    )
                    st.session_state['results'] = results
                    st.session_state['search_completed'] = True
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")
                return

        if 'results' in st.session_state:
            results = st.session_state['results']
            
            # Display statistics in a metrics container
            st.markdown("""
                <div class='metrics-container'>
                    <h3 style='color: #1E88E5; margin-bottom: 1rem;'>📊 Search Results Overview</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Results", results['stats'].get('total_results_found', 0))
            with col2:
                st.metric("YouTube Videos", len(results['youtube_videos']))
            with col3:
                st.metric("News Articles", len(results['news_articles']))
            with col4:
                st.metric("Reddit Posts", len(results['reddit_posts']))
            
            # Display results in columns
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("📺 YouTube Videos", expanded=True):
                    if not results['youtube_videos']:
                        st.info("No YouTube videos found")
                    for video in results['youtube_videos']:
                        with st.container():
                            st.markdown("""
                                <div class='result-card'>
                                    <h3 style='color: #1E88E5;'>{}</h3>
                                    <p><strong>Channel:</strong> {}</p>
                                    <a href="{}" target="_blank" style='color: #1E88E5;'>Watch Video →</a>
                                </div>
                            """.format(
                                video.get('title', 'No Title'),
                                video.get('channel', 'Unknown Channel'),
                                video.get('url', '#')
                            ), unsafe_allow_html=True)
                            if video.get('thumbnail'):
                                st.image(video['thumbnail'], use_column_width=True)

            with col2:
                with st.expander("📰 News & Articles", expanded=True):
                    if not results['news_articles']:
                        st.info("No news articles found")
                    for article in results['news_articles']:
                        st.markdown("""
                            <div class='result-card'>
                                <h3 style='color: #1E88E5;'>{}</h3>
                                <p><strong>Source:</strong> {} | <strong>Published:</strong> {}</p>
                                <a href="{}" target="_blank" style='color: #1E88E5;'>Read Article →</a>
                            </div>
                        """.format(
                            article.get('title', 'No Title'),
                            article.get('source', 'Unknown Source'),
                            article.get('published', 'No Date'),
                            article.get('link', '#')
                        ), unsafe_allow_html=True)

            # Add refresh button
            st.button("🔄 Start New Search", use_container_width=True)

if __name__ == "__main__":
    main()
