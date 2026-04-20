import sys
from pathlib import Path

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.agent.summarizer import SummarizerAgent

class SummarizerService:
    def __init__(self, model_name=None):
        self.agent = SummarizerAgent(model_name=model_name) if model_name else SummarizerAgent()

    def run(self):
        """Runs the summarization agent and returns a status string."""
        print("\n[Summarizer Service]")
        count = self.agent.run()
        return f"Summarized {count} new items."

    def close(self):
        self.agent.close()

if __name__ == "__main__":
    import os
    model_to_use = os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
    service = SummarizerService(model_name=model_to_use)
    try:
        service.run()
    finally:
        service.close()
