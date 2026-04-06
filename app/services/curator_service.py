import sys
from pathlib import Path

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.agent.curator import CuratorAgent

class CuratorService:
    def __init__(self, model_name=None):
        self.agent = CuratorAgent(model_name=model_name) if model_name else CuratorAgent()

    def run(self):
        """Runs the curation agent."""
        print("\n[Curator Service]")
        self.agent.run()

    def close(self):
        self.agent.close()

if __name__ == "__main__":
    import os
    model_to_use = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    service = CuratorService(model_name=model_to_use)
    try:
        service.run()
    finally:
        service.close()
