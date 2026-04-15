import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.utils import bootstrap_auth

# Bootstrap authentication and env vars
bootstrap_auth()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = os.getenv("SMTP_PORT", "587")
        self.sender_email = os.getenv("SENDER_EMAIL") or os.getenv("MY_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD") or os.getenv("APP_PASSWORD")
        
        # Validation
        self.is_configured = all([
            self.smtp_server, 
            self.smtp_port, 
            self.sender_email, 
            self.sender_password
        ])

    def send_email(self, subject: str, body: str, recipient_email: str) -> bool:
        """Sends an email using SMTP. Returns True if successful."""
        if not self.is_configured:
            print("[Email Service] WARNING: SMTP is not fully configured in .env. Skipping send.")
            print(f"[Email Service] Subject: {subject}")
            print(f"[Email Service] Body (truncated): {body[:100]}...")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Attach body as HTML
            msg.attach(MIMEText(body, 'html'))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, int(self.smtp_port)) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            print(f"[Email Service] Successfully sent email to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"[Email Service] ERROR: Failed to send email: {e}")
            return False

if __name__ == "__main__":
    # Quick standalone test
    service = EmailService()
    test_recipient = os.getenv("RECIPIENT_EMAIL", "test@example.com")
    service.send_email(
        subject="Test AI Aggregator Email", 
        body="This is a test email from the AI News Aggregator service.", 
        recipient_email=test_recipient
    )
