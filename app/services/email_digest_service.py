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
from app.utils import bootstrap_auth

# Bootstrap authentication and env vars
bootstrap_auth()

class EmailDigestService:
    def __init__(self, model_name=None):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        self.agent = EmailAgent(model_name=model_name) if model_name else EmailAgent()
        self.email_service = EmailService()

    def run(self):
        """Orchestrates the fetching, generation, and sending of the daily digest."""
        print("\n[Email Digest Service]")
        
        # 1. Fetch top 10 digests that haven't been sent yet
        # Expanded window to 72 hours for safety.
        print("Fetching top 10 unsent ranked digests from the last 72 hours...")
        top_digests = self.repo.get_top_digests(limit=10, hours=72, unsent_only=True)
        
        if not top_digests:
            print("  -> No recent unsent digests found. Email generation skipped.")
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
            recipient = os.getenv("RECIPIENT_EMAIL") or os.getenv("MY_EMAIL") or "paras@example.com"
            
            if self.email_service.send_email(email_data.subject, email_data.body, recipient):
                # 5. Update the sent status in the DB
                self.repo.update_email_sent_status(db_email.id)
                
                # 6. Mark included digests as sent to avoid duplicates in next run
                digest_ids = [d.id for d in top_digests]
                self.repo.mark_digests_as_sent(digest_ids)
                
                print(f"     [STRETCH] Email successfully sent to {recipient}")
                print(f"     [STRETCH] Marked {len(digest_ids)} digests as sent.")
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
