from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2, config
from typing import Annotated
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from datetime import date
import json

load_dotenv()

router = APIRouter(
    prefix= "/calendar/sync",
    tags = ["Calendar Sync"]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "google_client_secret.json") # Path to your Google client secret JSON file
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # For testing only (allows HTTP redirects during development)


# Start OAuth
@router.get("/start")
def start_google_sync(user=Depends(oauth2.get_current_user), token = Depends(oauth2.oauth2_scheme)):
    
    """Directs the user to Google's OAuth 2.0 auth login(consent) page"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state = token  # Pass the token as state to maintain session 
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true') # The auth_url is the authorization page
    return JSONResponse({"auth_url": auth_url}, status_code=status.HTTP_307_TEMPORARY_REDIRECT)  # Redirects the user to the Google OAuth consent page

# OAuth Callback
@router.get("/callback")
def calendar_sync_callback(request: Request, db: Session = Depends(database.get_db)):
    
    """After the user has authorised the google calendar app, this endpoint is called, with the code in the query parameters,
    The code is used to fetch the access token, which is then used to create a Google Calendar event."""
    
    # Extract the JWT token from the state parameter
    jwt_token = request.query_params.get("state")
    if not jwt_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter. JWT token is missing.")
    else:
        # Verify the JWT token to ensure the user is authenticated
        try:
            token_data = oauth2.verify_access_token(jwt_token, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"))
            user = db.query(orm_models.Users).filter(orm_models.Users.email == token_data.email).first() #Fetch the user from the token
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        except HTTPException as e:
            raise e
    
    # get plans of the user
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == user.email).first()
    if not user_plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plans found for user {user.username}, please set up your preferences first."
        )
    
    code = request.query_params.get("code") # Fetch the code from the query parameters
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code) # Exchange the code for an access token
    credentials = flow.credentials

    # Create Google Calendar event
    service = build("calendar", "v3", credentials=credentials)
    
    # creating events from user's plans -------------------------------->
    todays_date = date.today().isoformat()  # Get today's date in ISO format
    task1_content = ""
    task2_content = "" 
    task3_content = ""
    task1_content_dict = json.loads(user_plans.task1_content)
    for i, (step, task) in enumerate(task1_content_dict.items()):
        task1_content += f"Step {i+1}:   {task}\n\n"
    task2_content_dict = json.loads(user_plans.task2_content)
    for step, task in task2_content_dict.items():
        task2_content += f"Step {i+1}:   {task}\n\n"
    task3_content_dict = json.loads(user_plans.task3_content)
    for step, task in task3_content_dict.items():
        task3_content += f"Step {i+1}:   {task}\n\n"
    event1 = {
        'summary': user_plans.task1_title,
        'description': task1_content,
        'start': {
            'dateTime': todays_date + 'T' + user_plans.task1_timings_start,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': todays_date + 'T' + user_plans.task1_timings_end,
            'timeZone': 'Europe/Berlin',
        },
    }
    event2 = {
        'summary': user_plans.task2_title,
        'description': task2_content,
        'start': {
            'dateTime': todays_date + 'T' + user_plans.task2_timings_start,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': todays_date + 'T' + user_plans.task2_timings_end,
            'timeZone': 'Europe/Berlin',
        },
    }
    event3 = {
        'summary': user_plans.task3_title,
        'description': task3_content,
        'start': {
            'dateTime': todays_date + 'T' + user_plans.task3_timings_start,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            'dateTime': todays_date + 'T' + user_plans.task3_timings_end,
            'timeZone': 'Europe/Berlin',
        },
    }
    # -------------------------------------------------------------------------------
    created_event3 = service.events().insert(calendarId='primary', body=event1).execute()
    created_event2 = service.events().insert(calendarId='primary', body=event2).execute()
    created_event3 = service.events().insert(calendarId='primary', body=event3).execute()

    # Return HTML that closes the tab
    html_content = """
    <html>
        <head>
            <title>Workout Synced</title>
            <script>
                setTimeout(() => {
                    window.close();
                }, 3000);
            </script>
        </head>
        <body>
            <h3>✅ Your workout plan has been synced to Google Calendar!</h3>
            <p>This tab will close automatically...</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
