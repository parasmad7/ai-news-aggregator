import sys
from pathlib import Path

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.agent.summarizer import SummarizerAgent

class SummarizerService:
    def __init__(self, model_name=None):
        self.agent = SummarizerAgent(model_name=model_name) if model_name else SummarizerAgent()

    def run(self):
        """Runs the summarization agent."""
        print("\n[Summarizer Service]")
        self.agent.run()

    def close(self):
        self.agent.close()

if __name__ == "__main__":
    import os
    model_to_use = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    service = SummarizerService(model_name=model_to_use)
    try:
        service.run()
    finally:
        service.close()
