import os
import sys
from pathlib import Path
from google import genai

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.utils import bootstrap_auth, list_available_models

def main():
    bootstrap_auth()
    
    project_id = os.getenv("VERTEX_PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION")
    
    if not project_id or not location:
        print("Error: VERTEX_PROJECT_ID or VERTEX_LOCATION not set.")
        return

    print(f"Connecting to Project: {project_id}, Location: {location}")
    
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    
    list_available_models(client)

if __name__ == "__main__":
    main()
