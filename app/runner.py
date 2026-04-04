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

def run_all():
    print(f"\n--- Unified AI News Aggregator (Last {MAX_AGE_HOURS} hours) ---")
    
    # Initialize DB session and repository
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 0. Truncate posts table (one-time operation)
        print("\n[Maintenance] Truncating posts table...")
        repo.truncate_posts()
        
        # 1. YouTube Scraper
        print("\n[YouTube]")
        yt_scraper = YouTubeScraper()
        for channel_id in YOUTUBE_CHANNELS:
            print(f"Fetching updates for {channel_id}...")
            yt_data = yt_scraper.get_latest_videos(channel_id, MAX_AGE_HOURS)
            if not yt_data.videos:
                print(f"  -> No recent videos found for {channel_id}")
            else:
                for v in yt_data.videos:
                    print(f"  -> Video: {v.title} ({v.published_at})")
                    repo.upsert_video(v)
                    print(f"     [STRECH] Saved to DB")

        # 2. OpenAI Scraper
        print("\n[OpenAI Blog]")
        oa_scraper = OpenAIScraper()
        oa_posts = oa_scraper.get_latest_posts(MAX_AGE_HOURS, fetch_content=True)
        if not oa_posts:
            print("  -> No recent OpenAI blog posts found.")
        else:
            for p in oa_posts:
                print(f"  -> Blog: {p.title} ({p.published_at})")
                repo.upsert_post(p, source="OpenAI")
                print(f"     [STRECH] Saved to DB")

        # 3. Anthropic Scraper
        print("\n[Anthropic Blog]")
        ant_scraper = AnthropicScraper()
        ant_posts = ant_scraper.get_latest_posts(MAX_AGE_HOURS, fetch_content=True)
        if not ant_posts:
            print("  -> No recent Anthropic posts found.")
        else:
            for p in ant_posts:
                print(f"  -> [{p.category}] {p.title} ({p.published_at})")
                repo.upsert_post(p, source="Anthropic")
                print(f"     [STRECH] Saved to DB")

    finally:
        db.close()

    print("\n--- Aggregation Complete ---")

if __name__ == "__main__":
    run_all()
