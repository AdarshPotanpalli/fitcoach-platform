import streamlit as st

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
                st.Page("pages/auth.py", title="🚪Logout"),
                st.Page("pages/onboarding_form.py", title="🔧 Personalization")
            ]
        }
    else:
        pages = {
            "📚 Resources": [
                st.Page("pages/user_guide.py", title="ℹ️ Getting Started Guide", default=True),
            ],
            "👤 Your Account": [
                st.Page("pages/auth.py", title="🔐 Login/Register")
            ]
        }

    pg = st.navigation(pages)
    pg.run()

except Exception as e:
    print(f"Oops! something went wrong: {e}")
