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
from app.services.email_service import EmailService

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

    def run(self):
        """Fetches top digests, generates the email, saves it, and sends it."""
        print("\n[Email Agent]")
        
        # 1. Fetch top 10 digests
        print("Fetching top 10 ranked digests...")
        top_digests = self.repo.get_top_digests(limit=10)
        
        if not top_digests:
            print("  -> No ranked digests found. Email generation skipped.")
            return

        print(f"  -> Found {len(top_digests)} items. Generating email content...")
        
        # 2. Generate email content
        email_data = self.generate_email(top_digests)
        
        if email_data:
            # 3. Store in the database
            db_email = self.repo.create_email(email_data.subject, email_data.body)
            print(f"     [STRECH] Email template saved to 'emails' table (ID: {db_email.id})")
            
            # 4. Attempt to send the email
            print("  -> Sending email...")
            email_service = EmailService()
            recipient = os.getenv("RECIPIENT_EMAIL", "paras@example.com") # Default if not in .env
            
            if email_service.send_email(email_data.subject, email_data.body, recipient):
                # 5. Mark as sent in DB
                self.repo.update_email_sent_status(db_email.id)
                print(f"     [STRECH] Email successfully sent to {recipient}")
            else:
                print(f"     [WARNING] Email was stored but not sent. Check SMTP configuration.")
        else:
            print("  -> Failed to generate email content.")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    # Use Vertex AI configuration
    agent = EmailAgent()
    try:
        agent.run()
    finally:
        agent.close()
