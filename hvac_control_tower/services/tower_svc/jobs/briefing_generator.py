import schedule
import time
import requests
from datetime import datetime

def generate_daily_briefing():
    """Trigger the daily briefing generation job."""
    print(f"[{datetime.now()}] Generating Daily Executive Briefing...")
    # Calls the local endpoint to generate the briefing (via complex LLM)
    try:
        response = requests.post(
            "http://localhost:8000/copilot/briefing",
            json={"role": "CFO"}
        )
        if response.status_code == 200:
            print("Briefing generated successfully.")
            # In reality, this would be emailed or cached in redis for the frontend
        else:
            print(f"Error generating briefing: {response.status_code}")
    except Exception as e:
        print(f"Failed to connect to API: {e}")

def start_briefing_job():
    """Runs the briefing generator every morning at 06:00 AM."""
    schedule.every().day.at("06:00").do(generate_daily_briefing)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_briefing_job()
