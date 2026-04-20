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
from app.schemas.youtube import YouTubeVideo
from app.database.models import VideoModel

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
        count = 0
        for channel_id in YOUTUBE_CHANNELS:
            print(f"Fetching updates for {channel_id}...")
            raw_videos = self.yt_scraper.get_latest_videos(channel_id, MAX_AGE_HOURS)
            
            if not raw_videos:
                print(f"  -> No recent videos found for {channel_id}")
            else:
                for v in raw_videos:
                    print(f"Processing: {v['title']} ({v['video_id']})")
                    
                    # 1. OPTIMIZATION: Check if we already have this video BEFORE fetching transcript
                    existing = self.db.query(VideoModel).filter(VideoModel.video_id == v['video_id']).first()
                    
                    if not existing:
                        # 2. Only fetch transcript for truly new videos
                        transcript = self.yt_scraper.get_transcript(v['video_id'])
                        
                        video_obj = YouTubeVideo(
                            title=v['title'],
                            video_id=v['video_id'],
                            url=f"https://www.youtube.com/watch?v={v['video_id']}",
                            published_at=v['published_at'],
                            author=v.get('author', 'Unknown'),
                            transcript=transcript
                        )
                        
                        _, created = self.repo.add_video(video_obj)
                        if created:
                            count += 1
                            print(f"     [STRETCH] Truly NEW item saved to DB")
                    else:
                        print(f"     [SKIP] Already in database.")
        return count

    def run_openai(self):
        """Runs the OpenAI blog scraper."""
        print("\n[OpenAI Blog Scraper Service]")
        count = 0
        oa_posts = self.oa_scraper.get_latest_posts(MAX_AGE_HOURS, fetch_content=True)
        if not oa_posts:
            print("  -> No recent OpenAI blog posts found.")
        else:
            for p in oa_posts:
                print(f"  -> Blog: {p.title} ({p.published_at})")
                _, created = self.repo.add_post(p, source="OpenAI")
                if created:
                    count += 1
                    print(f"     [STRETCH] Saved to DB")
        return count

    def run_anthropic(self):
        """Runs the Anthropic blog scraper."""
        print("\n[Anthropic Blog Scraper Service]")
        count = 0
        ant_posts = self.ant_scraper.get_latest_posts(MAX_AGE_HOURS, fetch_content=True)
        if not ant_posts:
            print("  -> No recent Anthropic posts found.")
        else:
            for p in ant_posts:
                print(f"  -> [{p.category}] {p.title} ({p.published_at})")
                _, created = self.repo.add_post(p, source="Anthropic")
                if created:
                    count += 1
                    print(f"     [STRETCH] Saved to DB")
        return count

    def run_all(self):
        """Runs all scrapers in sequence and returns a status string."""
        yt_count = self.run_youtube()
        oa_count = self.run_openai()
        ant_count = self.run_anthropic()
        total = yt_count + oa_count + ant_count
        return f"Scraped {total} new items ({yt_count} YouTube, {oa_count} OpenAI, {ant_count} Anthropic)."

    def close(self):
        self.db.close()

if __name__ == "__main__":
    service = ScraperService()
    try:
        service.run_all()
    finally:
        service.close()
