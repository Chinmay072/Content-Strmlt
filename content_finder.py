import requests
import json
from typing import Dict, List, Union
import time
import random
import feedparser
from datetime import datetime, timedelta
import urllib.parse
from bs4 import BeautifulSoup
import os
import praw

class ContentFinder:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay_range = (1, 2)
        self.news_api_key = '6829434b7662434e992ed2d0613b8d9d'
        
        # Initialize Reddit client
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'ContentFinder/1.0'),
                check_for_async=False,
                read_only=True
            )
        except Exception as e:
            print(f"Error initializing Reddit client: {str(e)}")

    def _delay(self):
        """Add random delay between requests"""
        time.sleep(random.uniform(*self.delay_range))

    def search_youtube(self, query: str, max_results: int = 3) -> List[Dict]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return []
                
            content = response.text
            videos = []
            start = 0
            
            while len(videos) < max_results:
                vid_index = content.find('"videoId":"', start)
                if vid_index == -1:
                    break
                    
                vid_start = vid_index + 11
                vid_end = content.find('"', vid_start)
                video_id = content[vid_start:vid_end]
                
                title_index = content.find('"title":{"runs":[{"text":"', vid_end)
                if title_index == -1:
                    title_index = content.find('"title":{"simpleText":"', vid_end)
                    if title_index == -1:
                        start = vid_end
                        continue
                    title_start = title_index + 23
                else:
                    title_start = title_index + 26
                title_end = content.find('"', title_start)
                title = content[title_start:title_end]
                
                if video_id and title:
                    video_info = {
                        'title': urllib.parse.unquote(title),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'thumbnail': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    }
                    videos.append(video_info)
                
                start = title_end
            
            return videos
            
        except Exception as e:
            print(f"Error in YouTube search: {str(e)}")
            return []

    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        try:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': max_results,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for article in data.get('articles', [])[:max_results]:
                    result = {
                        'title': article.get('title', ''),
                        'link': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published': article.get('publishedAt', '')
                    }
                    results.append(result)
                
                return results
            return []
            
        except Exception as e:
            print(f"Error in news search: {str(e)}")
            return []

    def search_reddit(self, query: str, max_results: int = 5) -> List[Dict]:
        try:
            results = []
            for submission in self.reddit.subreddit('all').search(query, limit=max_results):
                try:
                    result = {
                        'title': submission.title,
                        'url': f"https://reddit.com{submission.permalink}",
                        'subreddit': str(submission.subreddit),
                        'author': str(submission.author) if submission.author else '[deleted]'
                    }
                    results.append(result)
                except Exception as post_error:
                    continue
            return results
            
        except Exception as e:
            print(f"Error in Reddit search: {str(e)}")
            return []

    def search_medium(self, query: str, max_results: int = 5) -> List[Dict]:
        try:
            search_url = f"https://medium.com/search?q={urllib.parse.quote(query)}"
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            articles = soup.find_all('article', limit=max_results)
            for article in articles:
                title_elem = article.find(['h2', 'h3'])
                link_elem = article.find('a', href=True)
                
                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    url = link_elem['href']
                    if not url.startswith('http'):
                        url = f"https://medium.com{url}"
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'author': 'Unknown Author'
                    })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Error searching Medium: {str(e)}")
            return []

    def find_targeted_content(self, media_insights: Dict, max_results_per_query: int = 3,
                            max_total_results: int = 50, max_queries_per_category: int = 5) -> Dict:
        results = {
            'youtube_videos': [],
            'news_articles': [],
            'reddit_posts': [],
            'medium_articles': [],
            'stats': {
                'queries_generated': 0,
                'queries_used': 0,
                'total_results_found': 0
            }
        }

        # Generate search queries based on media insights
        queries = []
        if media_insights.get('marketPosition'):
            queries.append(media_insights['marketPosition'])
        if media_insights.get('primaryAudienceDemographics'):
            queries.append(media_insights['primaryAudienceDemographics'])
        for pain_point in media_insights.get('painPointsAddressed', []):
            queries.append(pain_point)
        for competitor in media_insights.get('competitors', []):
            queries.append(competitor)

        results['stats']['queries_generated'] = len(queries)
        queries = queries[:max_queries_per_category]
        results['stats']['queries_used'] = len(queries)

        # Search across platforms
        for query in queries:
            # YouTube
            videos = self.search_youtube(query, max_results_per_query)
            results['youtube_videos'].extend(videos)

            # News
            news = self.search_news(query, max_results_per_query)
            results['news_articles'].extend(news)

            # Reddit
            reddit_posts = self.search_reddit(query, max_results_per_query)
            results['reddit_posts'].extend(reddit_posts)

            # Medium
            medium_articles = self.search_medium(query, max_results_per_query)
            results['medium_articles'].extend(medium_articles)

            self._delay()

        # Calculate total results
        results['stats']['total_results_found'] = (
            len(results['youtube_videos']) +
            len(results['news_articles']) +
            len(results['reddit_posts']) +
            len(results['medium_articles'])
        )

        return results