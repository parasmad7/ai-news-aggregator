import sys
from pathlib import Path

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.agent.email_agent import EmailAgent

class EmailDigestService:
    def __init__(self, model_name=None):
        self.agent = EmailAgent(model_name=model_name) if model_name else EmailAgent()

    def run(self):
        """Runs the email digest agent to generate and send the daily digest."""
        print("\n[Email Digest Service]")
        self.agent.run()

    def close(self):
        self.agent.close()

if __name__ == "__main__":
    import os
    model_to_use = os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
    service = EmailDigestService(model_name=model_to_use)
    try:
        service.run()
    finally:
        service.close()
