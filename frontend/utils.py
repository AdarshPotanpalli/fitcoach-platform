import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv
import os

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

# --- Usage Example ---

def login_user(token):
    cookies["access_token"] = token
    cookies["authenticated"] = "true"
    cookies.save()

def logout_user():
    cookies["access_token"] = ""
    cookies["authenticated"] = "false"
    cookies.save()

def is_user_authenticated():
    return cookies.get("authenticated") == "true"

def get_token():
    return cookies.get("access_token")
