import sys
from pathlib import Path
# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.scrapers.youtube import YouTubeScraper
from app.scrapers.openai import OpenAIScraper
from app.scrapers.anthropic import AnthropicScraper
from app.services.config import YOUTUBE_CHANNELS, MAX_AGE_HOURS

def run_all():
    print(f"\n--- Unified AI News Aggregator (Last {MAX_AGE_HOURS} hours) ---")
    
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

    # 2. OpenAI Scraper
    print("\n[OpenAI Blog]")
    oa_scraper = OpenAIScraper()
    oa_posts = oa_scraper.get_latest_posts(MAX_AGE_HOURS)
    if not oa_posts:
        print("  -> No recent OpenAI blog posts found.")
    else:
        for p in oa_posts:
            print(f"  -> Blog: {p.title} ({p.published_at})")

    # 3. Anthropic Scraper
    print("\n[Anthropic Blog]")
    ant_scraper = AnthropicScraper()
    ant_posts = ant_scraper.get_latest_posts(MAX_AGE_HOURS)
    if not ant_posts:
        print("  -> No recent Anthropic posts found.")
    else:
        for p in ant_posts:
            print(f"  -> [{p.category}] {p.title} ({p.published_at})")

    print("\n--- Aggregation Complete ---")

if __name__ == "__main__":
    run_all()
