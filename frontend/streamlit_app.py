import streamlit as st

# backend url
API_URL = "http://127.0.0.1:8000"

if "token" not in st.session_state:
    st.session_state.token = "" # default jwt token

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False  # Default state

# Conditional pages
try:
    if st.session_state.authenticated:
        pages = {
            "📚 Resources": [
                st.Page("pages/user_guide.py", title="ℹ️ Getting Started Guide"),
                st.Page("pages/dashboard.py", title="🏠 Dashboard", default=True),
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
