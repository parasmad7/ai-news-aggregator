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
from app.config import USER_INTERESTS

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class RankingResponse(BaseModel):
    score: float = Field(description="Relevance score from 0.0 to 1.0")
    reason: str = Field(description="A brief explanation for the score")

class CuratorAgent:
    def __init__(self, model_name="gemini-3-flash-preview"):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def rank_digest(self, title: str, summary: str) -> RankingResponse:
        """Scores a digest based on user interests using Gemini 3 Flash."""
        interests_str = ", ".join(USER_INTERESTS)
        prompt = f"""
        User Interests: {interests_str}
        
        News Item:
        Title: {title}
        Summary: {summary}
        
        Evaluate how relevant this news item is to the user's interests. 
        Provide a score from 0.0 (not relevant) to 1.0 (highly relevant) and a brief reason.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert news curator specializing in AI and technology. Your goal is to accurately rank news items based on a user's specific interests, providing objective scores and concise justifications.",
                    response_mime_type="application/json",
                    response_schema=RankingResponse,
                ),
            )
            return response.parsed
        except Exception as e:
            print(f"Error ranking '{title}': {e}")
            return None

    def run(self):
        """Processes all unranked digests in the database."""
        print("\n[Curator Agent]")
        digests = self.repo.get_unranked_digests()
        print(f"Ranking {len(digests)} unranked digests...")
        
        for d in digests:
            print(f"  -> Ranking: {d.title}")
            ranking = self.rank_digest(d.title, d.summary)
            if ranking:
                self.repo.update_digest_relevance(d.id, ranking.score, ranking.reason)
                print(f"     [STRECH] Score: {ranking.score}")
        
        print("Curation complete.")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    # The user specifically requested Gemini 3 Flash.
    model_to_use = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
    agent = CuratorAgent(model_name=model_to_use)
    try:
        agent.run()
    finally:
        agent.close()
