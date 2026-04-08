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
# from app.services.email_service import EmailService (Moved to run() to avoid circular import)

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class EmailContent(BaseModel):
    subject: str = Field(description="A compelling subject line for the email digest.")
    body: str = Field(description="The full email body in HTML with inline CSS, starting with 'Hey Paras'.")

class EmailAgent:
    def __init__(self, model_name=None): # Updated to match other agents
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

    def generate_email(self, top_digests) -> EmailContent:
        """Generates a personalized HTML email digest using Gemini."""
        if not top_digests:
            return None

        from datetime import datetime
        today_str = datetime.now().strftime("%B %d, %Y")

        digest_items = ""
        for i, d in enumerate(top_digests):
            digest_items += f"<li><strong>{d.title}</strong> ({d.source_type})<br/>"
            digest_items += f"<a href='{d.source_url}' style='color: #007bff; text-decoration: none;'>View Source</a><br/>"
            digest_items += f"{d.summary}</li><br/>"

        prompt = f"""
        Generate a professional and beautifully styled HTML email digest for Paras.
        
        Date: {today_str}
        Today's Top 10 News Items:
        <ul>
        {digest_items}
        </ul>
        
        Requirements:
        1. The body MUST start with "Hey Paras" in an <h1> or <h2> tag.
        2. Incorporate the date ({today_str}) naturally into the introduction (e.g., "Here is your AI Digest for {today_str}").
        3. Provide a brief, high-level summary of today's digest in the introduction.
        4. Use semantic HTML and **inline CSS** for styling:
           - font-family: 'Inter', 'Helvetica', 'Arial', sans-serif;
           - color: #333;
           - line-height: 1.6;
           - max-width: 600px;
           - margin: 0 auto;
        5. Links should be clearly styled and easy to click.
        6. The overall look should feel premium, minimal, and modern.
        7. The subject line should be catchy and relevant to the content.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a personal AI curator for Paras. Your goal is to write a warm, professional, and informative email digest summarizing the most important AI and tech news of the day.",
                    response_mime_type="application/json",
                    response_schema=EmailContent,
                ),
            )
            return response.parsed
        except Exception as e:
            print(f"Error generating email: {e}")
            return None

    def close(self):
        """Closes the database session."""
        self.db.close()

if __name__ == "__main__":
    # Standard standalone check
    from app.config import MAX_AGE_HOURS
    agent = EmailAgent()
    try:
        top_digests = agent.repo.get_top_digests(limit=5, hours=MAX_AGE_HOURS)
        content = agent.generate_email(top_digests)
        if content:
            print(f"--- Subject: {content.subject} ---\n{content.body[:200]}...")
    finally:
        agent.close()
