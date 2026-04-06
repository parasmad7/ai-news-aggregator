import schedule
import time
import logging
from datetime import datetime
from app.runner import run_all

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("daily_runner.log"),
        logging.StreamHandler()
    ]
)

def job():
    """The main aggregation job."""
    logging.info("Starting scheduled daily digest...")
    try:
        run_all()
        logging.info("Daily digest completed successfully.")
    except Exception as e:
        logging.error(f"Error during daily digest: {e}")

def run_scheduler():
    """Sets up and runs the scheduler."""
    # Schedule the job every day at 08:30 AM
    schedule.every().day.at("08:30").do(job)
    
    logging.info("Daily Runner Service started.")
    logging.info(f"Next job scheduled for 08:30 AM local time.")
    
    # Run once at startup to ensure everything is working (optional, but good for feedback)
    # logging.info("Running initial job on startup...")
    # job()

    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute

if __name__ == "__main__":
    run_scheduler()
