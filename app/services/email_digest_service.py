import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.agent.email_agent import EmailAgent
from app.services.email_service import EmailService
from app.database.session import SessionLocal
from app.database.repository import NewsRepository

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class EmailDigestService:
    def __init__(self, model_name=None):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        self.agent = EmailAgent(model_name=model_name) if model_name else EmailAgent()
        self.email_service = EmailService()

    def run(self):
        """Orchestrates the fetching, generation, and sending of the daily digest."""
        print("\n[Email Digest Service]")
        
        # 1. Fetch top 10 digests from the last 24 hours
        print("Fetching top 10 ranked digests from the last 24 hours...")
        top_digests = self.repo.get_top_digests(limit=10, hours=24)
        
        if not top_digests:
            print("  -> No recent ranked digests found. Email generation skipped.")
            return

        print(f"  -> Found {len(top_digests)} items. Generating email content...")
        
        # 2. Generate email content via the Agent
        email_data = self.agent.generate_email(top_digests)
        
        if email_data:
            # 3. Store the record in the database
            db_email = self.repo.create_email(email_data.subject, email_data.body)
            print(f"     [STRETCH] Email template saved to 'emails' table (ID: {db_email.id})")
            
            # 4. Send the email via the EmailService
            print("  -> Sending email...")
            recipient = os.getenv("RECIPIENT_EMAIL", "paras@example.com")
            
            if self.email_service.send_email(email_data.subject, email_data.body, recipient):
                # 5. Update the sent status in the DB
                self.repo.update_email_sent_status(db_email.id)
                print(f"     [STRETCH] Email successfully sent to {recipient}")
            else:
                print(f"     [WARNING] Email was stored but not sent. Check SMTP configuration.")
        else:
            print("  -> Failed to generate email content.")

    def close(self):
        """Closes the database connections."""
        self.db.close()
        self.agent.close()

if __name__ == "__main__":
    model_to_use = os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
    service = EmailDigestService(model_name=model_to_use)
    try:
        service.run()
    finally:
        service.close()
