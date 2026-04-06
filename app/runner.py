from app.services import (
    ScraperService,
    SummarizerService,
    CuratorService,
    EmailDigestService
)
from app.config import MAX_AGE_HOURS

def run_all():
    print(f"\n--- Unified AI News Aggregator (Last {MAX_AGE_HOURS} hours) ---")
    
    # 1. Scraper Service (YouTube, OpenAI, Anthropic)
    scraper_service = ScraperService()
    try:
        scraper_service.run_all()
    finally:
        scraper_service.close()

    # 2. Summarizer Service
    summarizer_service = SummarizerService()
    try:
        summarizer_service.run()
    finally:
        summarizer_service.close()

    # 3. Curator Service
    curator_service = CuratorService()
    try:
        curator_service.run()
    finally:
        curator_service.close()

    # 4. Email Digest Service
    email_service = EmailDigestService()
    try:
        email_service.run()
    finally:
        email_service.close()

    print("\n--- Aggregation Complete ---")

if __name__ == "__main__":
    run_all()
