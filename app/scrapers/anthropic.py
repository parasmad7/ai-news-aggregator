import sys
from pathlib import Path
# Add the project root to sys.path for absolute imports to work
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import feedparser
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import re
from app.schemas.anthropic import AnthropicPost
from docling.document_converter import DocumentConverter

class AnthropicScraper:
    def __init__(self):
        self.urls = {
            "News": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "Engineering": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
            "Research": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml"
        }
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

    def get_latest_posts(self, max_age_hours: int = 24, fetch_content: bool = False) -> List[AnthropicPost]:
        """Fetches latest Anthropic posts from all feeds, merged and sorted."""
        threshold = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        all_posts = []

        for category, url in self.urls.items():
            print(f"Fetching Anthropic {category} feed...")
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200:
                    print(f"  -> Failed to fetch {category}: {resp.status_code}")
                    continue
                
                feed = feedparser.parse(resp.text)
                for entry in feed.entries:
                    # Robust date parsing
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    else:
                        # Try to extract date from title/description (e.g. "Mar 24, 2026...")
                        date_match = re.search(r'([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})', entry.get('title', '') + ' ' + entry.get('description', ''))
                        if date_match:
                            try:
                                published_at = datetime.strptime(date_match.group(1), "%b %d, %Y").replace(tzinfo=timezone.utc)
                            except: pass

                    # If still no date, default to a very old date to avoid accidental inclusion in recent feeds
                    if not published_at:
                        published_at = datetime(1970, 1, 1, tzinfo=timezone.utc)
                    
                    if published_at >= threshold:
                        print(f"  -> Found: {entry.get('title')}")
                        all_posts.append(AnthropicPost(
                            title=entry.get('title', 'No Title'),
                            url=entry.get('link', ''),
                            description=entry.get('description', ''),
                            published_at=published_at,
                            category=category,
                            content=self.get_post_content(entry.get('link')) if fetch_content else None
                        ))
            except Exception as e:
                print(f"  -> Error parsing {category}: {e}")

        # Sort by publication date descending
        all_posts.sort(key=lambda x: x.published_at, reverse=True)
        return all_posts

if __name__ == "__main__":
    # Quick test
    scraper = AnthropicScraper()
    # Using a larger window for testing (e.g., 7 days) as RSS updates might be less frequent
    recent_posts = scraper.get_latest_posts(max_age_hours=240, fetch_content=True)
    print(f"\nFetched {len(recent_posts)} Anthropic posts in the last 7 days:")
    for post in recent_posts:
        print(f"\n--- [{post.category}] {post.title} ---\nDate: {post.published_at}\nContent Snippet: {post.content[:200] if post.content else 'None'}...")
