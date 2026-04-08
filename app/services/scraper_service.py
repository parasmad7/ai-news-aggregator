import os
import sys
from pathlib import Path

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.scrapers.youtube import YouTubeScraper
from app.scrapers.openai import OpenAIScraper
from app.scrapers.anthropic import AnthropicScraper
from app.config import YOUTUBE_CHANNELS, MAX_AGE_HOURS
from app.database.session import SessionLocal
from app.database.repository import NewsRepository

class ScraperService:
    def __init__(self):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        self.yt_scraper = YouTubeScraper()
        self.oa_scraper = OpenAIScraper()
        self.ant_scraper = AnthropicScraper()

    def run_youtube(self):
        """Runs the YouTube RSS scraper for all configured channels."""
        print("\n[YouTube Scraper Service]")
        for channel_id in YOUTUBE_CHANNELS:
            print(f"Fetching updates for {channel_id}...")
            yt_data = self.yt_scraper.get_latest_videos(channel_id, MAX_AGE_HOURS)
            if not yt_data.videos:
                print(f"  -> No recent videos found for {channel_id}")
            else:
                for v in yt_data.videos:
                    print(f"  -> Video: {v.title} ({v.published_at})")
                    self.repo.add_video(v)
                    print(f"     [STRETCH] Saved to DB")

    def run_openai(self):
        """Runs the OpenAI blog scraper."""
        print("\n[OpenAI Blog Scraper Service]")
        oa_posts = self.oa_scraper.get_latest_posts(MAX_AGE_HOURS, fetch_content=True)
        if not oa_posts:
            print("  -> No recent OpenAI blog posts found.")
        else:
            for p in oa_posts:
                print(f"  -> Blog: {p.title} ({p.published_at})")
                self.repo.add_post(p, source="OpenAI")
                print(f"     [STRETCH] Saved to DB")

    def run_anthropic(self):
        """Runs the Anthropic blog scraper."""
        print("\n[Anthropic Blog Scraper Service]")
        ant_posts = self.ant_scraper.get_latest_posts(MAX_AGE_HOURS, fetch_content=True)
        if not ant_posts:
            print("  -> No recent Anthropic posts found.")
        else:
            for p in ant_posts:
                print(f"  -> [{p.category}] {p.title} ({p.published_at})")
                self.repo.add_post(p, source="Anthropic")
                print(f"     [STRETCH] Saved to DB")

    def run_all(self):
        """Runs all scrapers in sequence."""
        self.run_youtube()
        self.run_openai()
        self.run_anthropic()

    def close(self):
        self.db.close()

if __name__ == "__main__":
    service = ScraperService()
    try:
        service.run_all()
    finally:
        service.close()
