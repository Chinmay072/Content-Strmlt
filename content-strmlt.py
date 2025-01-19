import streamlit as st
import google.generativeai as genai
import json
from content_finder import ContentFinder
import os

# Configure API keys
GEMINI_API_KEY = 'AIzaSyAkkgoutn9SEYg939Pb21Zi19rBwD93_5M'
REDDIT_CLIENT_ID = 'IW7JQMSzU-uCbp-0Gmi2lA'
REDDIT_CLIENT_SECRET = 'xxahjdPKNwpOtCjD1pWBahtx0pC67Q'
NEWS_API_KEY = '6829434b7662434e992ed2d0613b8d9d'

# Set environment variables
os.environ['REDDIT_CLIENT_ID'] = REDDIT_CLIENT_ID
os.environ['REDDIT_CLIENT_SECRET'] = REDDIT_CLIENT_SECRET
os.environ['REDDIT_USER_AGENT'] = 'ContentFinder/1.0'

def main():
    st.set_page_config(
        page_title="Content Discovery Platform",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Content Discovery Platform")
    st.markdown("""
    This platform helps you discover relevant content across multiple platforms based on your business insights.
    """)

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Input Business Insights", "Discovered Content"])

    with tab1:
        st.header("Business Insights")
        
        # Create form for business insights
        with st.form("business_insights_form"):
            audience = st.text_area(
                "Primary Audience Demographics",
                placeholder="e.g., Small business owners aged 30-50, primarily in urban areas"
            )
            
            pain_points = st.text_area(
                "Pain Points Addressed (one per line)",
                placeholder="e.g.,\nDifficulty in accessing analytics\nHigh costs of solutions"
            )
            
            competitors = st.text_area(
                "Competitors (one per line)",
                placeholder="e.g.,\nCompetitor A\nCompetitor B"
            )
            
            market_position = st.text_area(
                "Market Position",
                placeholder="e.g., Affordable and user-friendly platform for small businesses"
            )

            submit_button = st.form_submit_button("Find Content")

            if submit_button:
                # Process the inputs
                media_insights = {
                    "primaryAudienceDemographics": audience,
                    "painPointsAddressed": [p.strip() for p in pain_points.split('\n') if p.strip()],
                    "competitors": [c.strip() for c in competitors.split('\n') if c.strip()],
                    "marketPosition": market_position
                }

                # Store in session state
                st.session_state['media_insights'] = media_insights
                st.session_state['search_completed'] = False

    with tab2:
        if 'media_insights' in st.session_state and not st.session_state.get('search_completed', False):
            try:
                with st.spinner('Searching for relevant content...'):
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
                st.error(f"An error occurred during the search: {str(e)}")
                return

        if 'results' in st.session_state:
            results = st.session_state['results']
            
            # Display results in expandable sections
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("📺 YouTube Videos", expanded=True):
                    if not results['youtube_videos']:
                        st.info("No YouTube videos found")
                    for video in results['youtube_videos']:
                        st.markdown(f"### {video.get('title', 'No Title')}")
                        if video.get('channel'):
                            st.markdown(f"**Channel:** {video.get('channel')}")
                        st.markdown(f"[Watch Video]({video.get('url', '#')})")
                        if video.get('thumbnail'):
                            st.image(video['thumbnail'], use_column_width=True)
                        st.markdown("---")

                with st.expander("📰 News Articles", expanded=True):
                    if not results['news_articles']:
                        st.info("No news articles found")
                    for article in results['news_articles']:
                        st.markdown(f"### {article.get('title', 'No Title')}")
                        st.markdown(f"**Source:** {article.get('source', 'Unknown Source')}")
                        st.markdown(f"**Published:** {article.get('published', 'No Date')}")
                        st.markdown(f"[Read Article]({article.get('link', '#')})")
                        st.markdown("---")

            with col2:
                with st.expander("💬 Reddit Discussions", expanded=True):
                    if not results['reddit_posts']:
                        st.info("No Reddit discussions found")
                    for post in results['reddit_posts']:
                        st.markdown(f"### {post.get('title', 'No Title')}")
                        st.markdown(f"**Subreddit:** r/{post.get('subreddit', 'unknown')}")
                        st.markdown(f"**Author:** u/{post.get('author', 'unknown')}")
                        st.markdown(f"[View Discussion]({post.get('url', '#')})")
                        st.markdown("---")

                with st.expander("📝 Medium Articles", expanded=True):
                    if not results['medium_articles']:
                        st.info("No Medium articles found")
                    for article in results['medium_articles']:
                        st.markdown(f"### {article.get('title', 'No Title')}")
                        st.markdown(f"**Author:** {article.get('author', 'Unknown Author')}")
                        st.markdown(f"[Read Article]({article.get('url', '#')})")
                        st.markdown("---")

            # Display statistics in sidebar
            st.sidebar.header("Search Statistics")
            stats = results.get('stats', {})
            st.sidebar.metric("Total Results", stats.get('total_results_found', 0))
            st.sidebar.metric("Queries Generated", stats.get('queries_generated', 0))
            st.sidebar.metric("Queries Used", stats.get('queries_used', 0))

            # Add refresh button
            if st.button("Start New Search"):
                st.session_state.clear()
                st.experimental_rerun()

if __name__ == "__main__":
    main()