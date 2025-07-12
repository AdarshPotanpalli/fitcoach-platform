from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, status, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from .. import utils, database, schemas, orm_models, oauth2, config
from typing import Annotated
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from datetime import date
import json
from google.auth.transport.requests import Request as GoogleRequest

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
def start_google_sync(user=Depends(oauth2.get_current_user), token = Depends(oauth2.oauth2_scheme), db: Session = Depends(database.get_db)):
    
    """Directs the user to Google's OAuth 2.0 auth login(consent) page"""
    
    # get plans of the user
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == user.email).first()
    if not user_plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plans found for user {user.username}, please set up your preferences first."
        )
    
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
    
    encrypted_credentials = utils.encrypt_credentials(credentials.to_json())
    user.google_credentials = encrypted_credentials # Store the credentials as json string in the user table
    user.is_google_synced = True  # Mark the user as synced with Google Calendar
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create Google Calendar event
    service = build("calendar", "v3", credentials=credentials)
    
    # Create calendar events based on the user's plans
    google_event_ids = utils.create_calendar_events(user_plans, service)
    
    user.google_event_ids = json.dumps(google_event_ids)  # Store the event IDs as a JSON string in the user table
    db.add(user)
    db.commit()
    db.refresh(user)

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

# Update endpoint will be used mostly, the below post and delete endpoints are for testing purposes

# Flow -> every new day, the events from the previous day should be deleted and new events should be created for the current day
# OR
# Flow -> if the user wants to update their current day's events, they click on the update button, which delets the current day's events and creates new events based
def update_events_for_user(user: orm_models.Users, db: Session) -> JSONResponse:
    
    """Endpoint to update the user's Google Calendar events for the current day.
    Deletes the previous day's events and creates new events based on the user's plans."""
    
    if not user.google_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar is not synced. Please sync your calendar first."
        )
    
    if not user.google_event_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No events found in Google Calendar to update. Please sync your calendar first."
        )
    
    # get plans of the user
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == user.email).first()
    if not user_plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plans found for user {user.username}, please set up your preferences first."
        )
    
    try:
        decrypted_credentials = utils.decrypt_credentials(user.google_credentials)
        credentials = Credentials.from_authorized_user_info(decrypted_credentials, SCOPES)
        
        # refresh the credentials if they are expired
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(GoogleRequest())
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Calendar credentials are invalid or expired. Please re-sync your calendar."
                )
        
        service = build("calendar", "v3", credentials=credentials)
        
        
        # Delete all events in the user's calendar whose IDs are stored in the users table
        event_ids = json.loads(user.google_event_ids)  # Load the event IDs from the user's record
        # print(f"Deleting events with IDs: {event_ids}")
        for event_id in event_ids:
            try:
                service.events().delete(calendarId='primary', eventId=event_id).execute()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"An error occurred while deleting event {event_id} from Google Calendar: {str(e)}"
                )
        
        # Clear the google_event_ids field in the user table
        user.google_event_ids = json.dumps([])  # Clear the event IDs
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create calendar events based on the user's plans + get the corresponding event IDs
        google_event_ids = utils.create_calendar_events(user_plans, service)
        user.google_event_ids = json.dumps(google_event_ids)  # Store the event IDs as a JSON string in the user table
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Events updated to Google Calendar successfully."}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating events from Google Calendar: {str(e)}"
        )

@router.put("/update_events")
def update_events(current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)], 
                 db: Session = Depends(database.get_db)):
    
    return update_events_for_user(current_user, db)
    


## The below endpoints are used only in special scenarios, which can occur only during testing or debugging.

# Post Event to Google Calendar
@router.post("/post_event")
def post_event(current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)], 
               db: Session = Depends(database.get_db)):
    """Endpoint to post an event to the Google Calendar, if the user has already synced their calendar."""
    
    if not current_user.google_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar is not synced. Please sync your calendar first."
        )
    
    if current_user.google_event_ids and current_user.google_event_ids != "[]":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Events already posted to Google Calendar. Please delete existing events before posting new ones."
        )
        
    try:
        decrypted_credentials = utils.decrypt_credentials(current_user.google_credentials)
        credentials = Credentials.from_authorized_user_info(decrypted_credentials, SCOPES)

        # refresh the credentials if they are expired
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(GoogleRequest())
            else:
                # if the credentials are invalid and the refresh token is not available, or if refresh fails
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Calendar credentials are invalid or expired. Please re-sync your calendar."
                )
        
        # get plans of the user
        user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email).first()
        if not user_plans:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No plans found for user {current_user.username}, please set up your preferences first."
            )
            
        # build the service with the refreshed credentials
        service = build("calendar", "v3", credentials=credentials)
        
        # Create calendar events based on the user's plans + get the corresponding event IDs
        google_event_ids = utils.create_calendar_events(user_plans, service)
        current_user.google_event_ids = json.dumps(google_event_ids)  # Store the event IDs as a JSON string in the user table
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Events posted to Google Calendar successfully."}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while posting events to Google Calendar: {str(e)}"
        )
        
# Delete Events from Google Calendar and clear the google credentials and is_google_synced flag      
@router.delete("/unsync_and_delete_events")
def unsync_and_delete_events(current_user: Annotated[schemas.CreateUserResponse, Depends(oauth2.get_current_user)], 
                  db: Session = Depends(database.get_db)):
    """Endpoint to delete all events from the user's Google Calendar."""
    
    # get plans of the user
    user_plans = db.query(orm_models.Plans).filter(orm_models.Plans.owner_email == current_user.email).first()
    if not user_plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No plans found for user {current_user.username}."
        )
    
    if not current_user.google_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Calendar is not synced. Please sync your calendar first."
        )
        
    if not current_user.google_event_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No events found in Google Calendar to delete. Please sync your calendar first."
        )
        
    try:
        decrypted_credentials = utils.decrypt_credentials(current_user.google_credentials)
        credentials = Credentials.from_authorized_user_info(decrypted_credentials, SCOPES)
        
        # refresh the credentials if they are expired
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(GoogleRequest())
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Calendar credentials are invalid or expired. Please re-sync your calendar."
                )
        
        service = build("calendar", "v3", credentials=credentials)
        
        # Delete all events in the user's calendar whose IDs are stored in the users table
        event_ids = json.loads(current_user.google_event_ids)  # Load the event IDs from the user's record
        for event_id in event_ids:
            try:
                service.events().delete(calendarId='primary', eventId=event_id).execute()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"An error occurred while deleting event {event_id} from Google Calendar: {str(e)}"
                )
        
        # Clear the google_event_ids field in the user table
        current_user.google_event_ids = None  # Clear the event IDs
        current_user.google_credentials = None  # Clear the Google credentials
        current_user.is_google_synced = False  # Mark the user as not synced with Google Calendar
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Events deleted from Google Calendar and user unsynced successfully."}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting events from Google Calendar: {str(e)}"
        )