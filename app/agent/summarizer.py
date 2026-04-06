import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.database.session import SessionLocal
from app.database.repository import NewsRepository

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Define schema for structured output
class DigestSummary(BaseModel):
    summary: str = Field(description="A 2-3 line summary of the content.")

class SummarizerAgent:
    def __init__(self, model_name="gemini-3-flash-preview"):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file.")
        
        # Initialize the new Google GenAI client
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def summarize(self, text: str, title: str) -> str:
        """Sends content to Gemini and returns a 2-3 line summary using structured output."""
        prompt = f"""
        Provide a concise 2-3 line summary of the following content.
        
        Title: {title}
        Content: {text}
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a professional news summarizer. Your goal is to provide 2-3 line summaries that are clear, concise, and highlight the most important takeaways from AI and technology news.",
                    response_mime_type="application/json",
                    response_schema=DigestSummary,
                ),
            )
            
            # The new SDK provides a .parsed attribute for Pydantic models
            if response.parsed:
                return response.parsed.summary
            return None
            
        except Exception as e:
            print(f"Error summarizing '{title}': {e}")
            return None

    def run(self):
        """Processes all videos and posts in the database."""
        print("\n[Summarizer Agent]")
        
        # Process Videos
        videos = self.repo.get_all_videos()
        print(f"Checking {len(videos)} videos...")
        for video in videos:
            if self.repo.get_digest_by_url(video.url):
                continue
            
            content = video.transcript or video.title
            print(f"  -> Summarizing video: {video.title}")
            summary = self.summarize(content, video.title)
            if summary:
                self.repo.create_digest(video.url, video.title, summary, "video")
                print(f"     [STRECH] Summary saved")
        
        # Process Posts
        posts = self.repo.get_all_posts()
        print(f"Checking {len(posts)} posts...")
        for post in posts:
            if self.repo.get_digest_by_url(post.url):
                continue
            
            content = post.content or post.description or post.title
            print(f"  -> Summarizing post: {post.title}")
            summary = self.summarize(content, post.title)
            if summary:
                self.repo.create_digest(post.url, post.title, summary, "post")
                print(f"     [STRECH] Summary saved")
        
        print("Summarization complete.")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    # The user specifically requested Gemini 3 Flash.
    model_to_use = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    agent = SummarizerAgent(model_name=model_to_use)
    try:
        agent.run()
    finally:
        agent.close()
