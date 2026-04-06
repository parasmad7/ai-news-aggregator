import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Add project root to sys.path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    print("Adding columns to digests table...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE digests ADD COLUMN relevance_score FLOAT;"))
            conn.commit()
            print("  -> Added relevance_score")
        except Exception as e:
            # conn.rollback() # Explicit rollback if needed, though session/conn might handle it
            print(f"  -> Skipping relevance_score (likely exists)")

        try:
            conn.execute(text("ALTER TABLE digests ADD COLUMN relevance_reason TEXT;"))
            conn.commit()
            print("  -> Added relevance_reason")
        except Exception as e:
            print(f"  -> Skipping relevance_reason (likely exists)")

    print("Adding columns to emails table...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE emails ADD COLUMN sent_at TIMESTAMP;"))
            conn.commit()
            print("  -> Added sent_at")
        except Exception as e:
            print(f"  -> Skipping sent_at (likely exists)")
            
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
