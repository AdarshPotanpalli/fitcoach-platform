from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from sqlalchemy.orm import Session
from . import orm_models, database
import requests
from datetime import datetime, date, timedelta
import json
from . import utils

def call_update_plans():
    # Call your FastAPI update endpoint (assuming it’s authenticated with a token)
    db: Session = next(database.get_db())
    users = db.query(orm_models.Users).all()

    for user in users:
        preferences = db.query(orm_models.Preferences).filter_by(owner_email=user.email).first()
        if not preferences:
            continue # If no preferences, skip to the next user

        plan_query = db.query(orm_models.Plans).filter_by(owner_email=user.email)
        if not plan_query.first():
            continue # If no plan exists, skip to the next user

        # Modify preferred_timings as you do in your existing endpoint
        preferred_timings_list = preferences.preferred_timings
        preferred_timings_list.insert(0, f"Hard constraint (even if the next elements in this list conflicts with this constraint, you must obey hard this constraint) : The suggested plan must take place after {datetime.now().strftime("%H hrs %M mins")}")
        preferences.preferred_timings = preferred_timings_list


        # the feedback history is also a context, which tells which kind of activities the user succeeded in doing and which they failed
        end_date = date.today()
        start_date = end_date - timedelta(days=4) # last 5 days feedback window is also given as input for plan update
        list_of_task_failures = []
        list_of_task_successes = []
        
        feedback_history = db.query(orm_models.Feedback).filter(
            orm_models.Feedback.owner_email == user.email,
            orm_models.Feedback.date >= start_date,
            orm_models.Feedback.date <= end_date,
            ).all()
        
        for feedback in feedback_history:
            list_of_task_failures.extend(feedback.list_of_task_failures)
            list_of_task_successes.extend(feedback.list_of_task_successes)


        generated_plan = utils.get_todays_plan(preferences,
                                           list_of_task_failures= list_of_task_failures,
                                           list_of_task_successes= list_of_task_successes)
        
        generated_plan["task1_content"] = json.dumps(generated_plan["task1_content"])
        generated_plan["task2_content"] = json.dumps(generated_plan["task2_content"])
        generated_plan["task3_content"] = json.dumps(generated_plan["task3_content"])

        plan_query.update(generated_plan, synchronize_session=False)
        db.commit()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(call_update_plans, 
                      CronTrigger(hour=6, minute=0, timezone=pytz.timezone("Europe/Berlin")),
                      id="daily_plan_generation")  # Every day at 6 AM update plans
    scheduler.start()

