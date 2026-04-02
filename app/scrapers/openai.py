import sys
from pathlib import Path
# Add the project root to sys.path for absolute imports to work
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import feedparser
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.schemas.openai import OpenAIPost
from docling.document_converter import DocumentConverter

class OpenAIScraper:
    def __init__(self):
        self.rss_url = "https://openai.com/news/rss.xml"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.converter = DocumentConverter()

    def get_post_content(self, url: str) -> Optional[str]:
        """Converts a given URL to Markdown using docling."""
        try:
            print(f"  -> Converting URL to Markdown: {url}")
            result = self.converter.convert(url)
            return result.document.export_to_markdown()
        except Exception as e:
            print(f"  -> Failed to convert {url}: {e}")
            return None

    def get_latest_posts(self, max_age_hours: int = 24, fetch_content: bool = False) -> List[OpenAIPost]:
        """Fetches the latest OpenAI blog posts and filters by age."""
        try:
            resp = self.session.get(self.rss_url, timeout=10)
            if resp.status_code != 200:
                print(f"Failed to fetch OpenAI RSS: {resp.status_code}")
                return []
            
            feed = feedparser.parse(resp.text)
            threshold = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            
            posts = []
            for entry in feed.entries:
                # Convert the time to a UTC datetime object
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                
                if published_at >= threshold:
                    posts.append(OpenAIPost(
                        title=entry.get('title', 'No Title'),
                        url=entry.get('link', ''),
                        description=entry.get('description', ''),
                        published_at=published_at,
                        category=entry.get('category'),
                        content=self.get_post_content(entry.get('link')) if fetch_content else None
                    ))
            return posts

        except Exception as e:
            print(f"Error scraping OpenAI: {e}")
            return []

if __name__ == "__main__":
    # Quick test
    scraper = OpenAIScraper()
    # Using 48 hours and fetching content for the test
    recent_posts = scraper.get_latest_posts(48, fetch_content=True)
    print(f"\nFetched {len(recent_posts)} posts in the last 48 hours:")
    for post in recent_posts:
        print(f"\n--- {post.title} ---\nDate: {post.published_at}\nContent Snippet: {post.content[:200] if post.content else 'None'}...")
