import os
import json
from pathlib import Path
from dotenv import load_dotenv

def bootstrap_auth():
    """
    Bootstraps authentication and environment variables.
    Ensures .env is loaded from the absolute path of the project root.
    Provides diagnostic information for Google Cloud credentials.
    """
    # 1. Standardize .env loading
    # project_root/app/utils/auth_utils.py -> project_root/app/.env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    
    # 2. Check for GCP Credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not creds_path:
        print("[Auth Utils] WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set.")
        return

    creds_file = Path(creds_path)
    if not creds_file.exists():
        print(f"[Auth Utils] ERROR: Credentials file not found at {creds_path}")
        return

    # 3. Diagnostic Check (User vs Service Account)
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
            
        cred_type = creds_data.get("type")
        
        if cred_type == "service_account":
            print(f"[Auth Utils] SUCCESS: Using Service Account credentials ({creds_data.get('client_email')})")
        elif cred_type == "authorized_user" or "refresh_token" in creds_data:
            print("[Auth Utils] WARNING: Using 'User' credentials (ADC).")
            print("[Auth Utils] NOTE: In cloud environments like Render, User credentials frequently require re-authentication.")
            print("[Auth Utils] If you see 'Reauthentication is needed', please update the secret file on Render with a fresh local key.")
        else:
            print(f"[Auth Utils] INFO: Detected credential type: {cred_type or 'unknown'}")
            
    except Exception as e:
        print(f"[Auth Utils] WARNING: Could not parse credentials file for diagnostics: {e}")

def list_available_models(client):
    """Utility to list available Vertex AI models for diagnostics."""
    try:
        print("[Auth Utils] Fetching available models...")
        models = client.models.list()
        print("[Auth Utils] Available Models:")
        for m in models:
            print(f"  - {m.name}")
    except Exception as e:
        print(f"[Auth Utils] ERROR: Could not list models: {e}")

def get_model_name(default="gemini-2.5-flash"):
    """Returns the model name from env or default."""
    model = os.getenv("VERTEX_MODEL") or default
    print(f"[Auth Utils] Using model: {model}")
    return model
