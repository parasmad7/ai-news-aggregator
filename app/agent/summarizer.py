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
    def __init__(self, model_name=None):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        
        project_id = os.getenv("VERTEX_PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION")
        
        if not project_id or not location:
            raise ValueError("Vertex AI configuration (PROJECT_ID/LOCATION) not found in .env file.")
        
        # Initialize the new Google GenAI client for Vertex AI
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        self.model_name = model_name or os.getenv("VERTEX_MODEL", "gemini-2.5-flash")

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
                self.repo.create_digest(
                    url=video.url,
                    title=video.title,
                    summary=summary,
                    source_type="video",
                    published_at=video.published_at
                )
                print(f"     [STRETCH] Summary saved")
        
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
                self.repo.create_digest(
                    url=post.url,
                    title=post.title,
                    summary=summary,
                    source_type="post",
                    published_at=post.published_at
                )
                print(f"     [STRETCH] Summary saved")
        
        print("Summarization complete.")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    # Use Vertex AI configuration
    agent = SummarizerAgent()
    try:
        agent.run()
    finally:
        agent.close()
