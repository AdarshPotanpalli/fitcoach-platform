import streamlit as st
import requests
from frontend.utils import get_token, logout_user
# backend url
API_URL = "http://127.0.0.1:8000"

# if "token" not in st.session_state:
#     st.session_state.token = "" # default jwt token

# if "authenticated" not in st.session_state:
#     st.session_state.authenticated = False  # Default state

if "login_form_key" not in st.session_state:
    st.session_state.login_form_key = "login_form"

# this is used to track if the user is registering a new account
if "new_register" not in st.session_state:
    st.session_state.new_register = False  # Default state for new registration

def is_user_authenticated():
    # return cookies.get("authenticated") == "true"
    """Checks if the user is authenticated by verifying the presence of an access token."""
    headers = {
                "Authorization": f"Bearer {get_token()}"
            }
    response = requests.get(API_URL + "/me", headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False


# Conditional pages
try:
    if is_user_authenticated():
        if st.session_state["new_register"]: # this means the user ahs just registered
            st.session_state["new_register"] = False
            pages = {
                "📚 Resources": [
                    st.Page("pages/user_guide.py", title="ℹ️ Getting Started Guide"),
                    st.Page("pages/dashboard.py", title="🏠 Dashboard"),
                    st.Page("pages/ai_coach.py", title="🤖 Your AI Coach"),
                    st.Page("pages/detailed_plan.py", title="📝 Your detailed daily plan")
                ],
                "👤 Your Account": [
                    st.Page("pages/logout.py", title="🚪Logout"),
                    st.Page("pages/onboarding_form.py", title="🔧 Personalization", default= True)
                ]
            }
        else: # the user is authenticated but not registering a new account
            pages = {
                "📚 Resources": [
                    st.Page("pages/user_guide.py", title="ℹ️ Getting Started Guide"),
                    st.Page("pages/dashboard.py", title="🏠 Dashboard", default= True),
                    st.Page("pages/ai_coach.py", title="🤖 Your AI Coach"),
                    st.Page("pages/detailed_plan.py", title="📝 Your detailed daily plan")
                ],
                "👤 Your Account": [
                    st.Page("pages/logout.py", title="🚪Logout"),
                    st.Page("pages/onboarding_form.py", title="🔧 Personalization")
                ]
            }
            
    else:
        pages = {
            "📚 Resources": [
                st.Page("pages/user_guide.py", title="ℹ️ Getting Started Guide", default=True),
            ],
            "👤 Your Account": [
                st.Page("pages/login.py", title="🔐 Login"),
                st.Page("pages/register.py", title ="🧾 Sign Up")
            ]
        }

    pg = st.navigation(pages)
    pg.run()

except Exception as e:
    print(f"Oops! something went wrong: {e}")
