from app.agent.supervisor import SupervisorAgent
from app.config import MAX_AGE_HOURS

def run_all():
    print(f"\n--- AI News Aggregator: Agentic Mode (Window: {MAX_AGE_HOURS}h) ---")
    
    supervisor = SupervisorAgent()
    try:
        supervisor.run()
    finally:
        supervisor.close()

    print("\n--- Process Complete ---")

if __name__ == "__main__":
    run_all()
