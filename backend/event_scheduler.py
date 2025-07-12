from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from . import orm_models, database
import requests
import datetime

def call_update_events():
    # Call your FastAPI update endpoint (assuming it’s authenticated with a token)
    token = "YOUR_USER_JWT"  # ideally, generate this dynamically
    response = requests.put(
        "http://localhost:8000/calendar/sync/update_events",
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Update Calendar Response:", response.json())

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(call_update_events, 'cron', hour=7)  # Every day at 7 AM
    scheduler.start()

