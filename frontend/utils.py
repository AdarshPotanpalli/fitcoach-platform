import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()
COOKIE_SECRET = os.getenv("COOKIE_SECRET")
COOKIE_PREFIX = os.getenv("COOKIE_PREFIX")

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix=COOKIE_PREFIX,
    password=COOKIE_SECRET
)

if not cookies.ready():
    st.stop()  # Wait until cookies are ready

def login_user(token):
    cookies["access_token"] = token
    cookies.save()

def logout_user():
    cookies["access_token"] = ""
    cookies.save()   

def get_token():
    return cookies.get("access_token")


def generate_plan(API_URL: str):
    
    """Checks if the user already has a plan,
    if yes, update the plan,
    if not, create a new plan"""
    # check if the user has a plan already in db
    headers = {
        "Authorization": f"Bearer {get_token()}"
    }
    response = requests.get(API_URL+ "/plans", headers = headers)
    if response.status_code == 200:
        # if plan already exists, update the plan
        put_response = requests.put(API_URL + "/plans", headers=headers)

        if put_response.status_code !=200:
            st.error(put_response.json().get("detail", "Error updating plan."))
            
    elif response.status_code == 404:
        # if plan does not exist, create a new plan
        post_response = requests.post(API_URL + "/plans", headers=headers)
        
        if post_response.status_code != 201:
            st.error(post_response.json().get("detail", "Error creating plan."))