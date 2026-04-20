import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime

# Add project root to sys.path for absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.database.session import SessionLocal
from app.database.repository import NewsRepository
from app.services import (
    ScraperService,
    SummarizerService,
    CuratorService,
    EmailDigestService
)
from app.utils import bootstrap_auth, get_model_name

# Bootstrap authentication and env vars
bootstrap_auth()

class SupervisorDecision(BaseModel):
    action: str = Field(description="The next action to take: 'SCRAPE', 'SUMMARIZE', 'CURATE', 'SEND_EMAIL', or 'FINISH'.")
    reasoning: str = Field(description="The logic behind choosing this action.")

from app.agent.tools.search_tool import search_the_web

class SupervisorAgent:
    def __init__(self, model_name=None):
        self.db = SessionLocal()
        self.repo = NewsRepository(self.db)
        
        project_id = os.getenv("VERTEX_PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION")
        
        if not project_id or not location:
            raise ValueError("Vertex AI configuration (PROJECT_ID/LOCATION) not found in .env file.")
        
        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
        self.model_name = model_name or get_model_name()
        self.max_turns = 10
        self.history = []

    # --- Tool Definitions ---

    def scrape_news(self) -> str:
        """Fetches new news from YouTube and blogs. Returns a summary of findings."""
        service = ScraperService()
        try:
            return service.run_all()
        finally:
            service.close()

    def summarize_pending_news(self) -> str:
        """Summarizes raw news items waiting in the database. Returns a status string."""
        service = SummarizerService()
        try:
            return service.run()
        finally:
            service.close()

    def curate_pending_news(self) -> str:
        """Ranks news summaries by relevance to the user. Returns a status string."""
        service = CuratorService()
        try:
            return service.run()
        finally:
            service.close()

    def send_email_digest(self) -> str:
        """Generates and sends the email digest. Respects the 24h rule."""
        service = EmailDigestService()
        try:
            return service.run()
        finally:
            service.close()

    def get_system_state_manual(self) -> str:
        """Returns the current snapshot of the news pipeline (counts and headlines)."""
        state = self.repo.get_detailed_state()
        return str(state)

    # --- Execution Loop ---

    def run(self):
        """Main execution loop using formal Function Calling."""
        print("\n--- [Supervisor Agent: STARTING (Tool-Mode)] ---")
        
        # Define the tools available to the model
        tools = [
            self.scrape_news,
            self.summarize_pending_news,
            self.curate_pending_news,
            self.send_email_digest,
            search_the_web
        ]
        
        # Build the initial system instruction
        system_instruction = f"""
        You are the autonomous Manager of an AI News Aggregator. 
        Your goal is to move news items through the pipeline: Scrape -> Summarize -> Curate -> Email.
        
        Rules:
        1. 24-HOUR RULE: Ideally, wait at least 24 hours between emails. 
        2. BREAKING NEWS: Override the 24h rule only for news with Relevance > 0.9.
        3. REDUNDANCY: If you scrape and find 0 new items, and everything else is empty, stop.
        4. ANALYSIS: Use the 'search_the_web' tool if you see a vague news item and need more context to rank it.
        
        Process:
        - Check current state (you will be provided with a snapshot initially).
        - Call tools to progress the pipeline.
        - When all work is done or you hit the 24h rule, explain your reasoning and say "FINISH" or simply stop calling tools.
        """
        
        state = self.repo.get_detailed_state()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools,
            )
        )
        
        initial_prompt = f"""
        Current Time: {current_time}
        Initial System State: {state}
        
        Please manage the pipeline. Start by evaluating if a SCRAPE is needed or if there is pending work to summarize/curate.
        """
        
        response = chat.send_message(initial_prompt)
        
        # The SDK handles the tool execution loop if we use the right config, 
        # but manual control gives us better visibility in logs.
        
        turn = 1
        while turn <= self.max_turns:
            # Look for tool calls in the response
            tool_calls = [part.function_call for part in response.candidates[0].content.parts if part.function_call]
            
            if not tool_calls:
                print(f"\n[Agent Thought]: {response.text}")
                if "FINISH" in response.text.upper():
                    break
                # If no tool calls and no FINISH, the agent might be done or just chatting
                break

            for call in tool_calls:
                fname = call.name
                fargs = call.args
                print(f"\n[Turn {turn}] Agent calls: {fname}({fargs})")
                
                # Execute the corresponding local function
                if fname == "scrape_news": result = self.scrape_news()
                elif fname == "summarize_pending_news": result = self.summarize_pending_news()
                elif fname == "curate_pending_news": result = self.curate_pending_news()
                elif fname == "send_email_digest": result = self.send_email_digest()
                elif fname == "search_the_web": result = search_the_web(**fargs)
                else: result = f"Error: Tool '{fname}' not found."
                
                print(f"Tool Result: {result}")
                
                # Send the tool result back to the model
                # The SDK usually expects a list of parts for the next turn
                response = chat.send_message(
                    types.Part.from_function_response(
                        name=fname,
                        response={"result": result}
                    )
                )
            
            turn += 1

        print("\n--- [Supervisor Agent: COMPLETE] ---")

    def close(self):
        self.db.close()

if __name__ == "__main__":
    agent = SupervisorAgent()
    try:
        agent.run()
    finally:
        agent.close()
