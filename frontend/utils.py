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


