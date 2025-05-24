import streamlit as st

# Initialize the authentication state if it doesn't exist
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Toggle button
if st.session_state.authenticated:
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.switch_page("pages/user_guide.py")
else:
    if st.button("🔐 Login"):
        st.session_state.authenticated = True
        st.switch_page("pages/dashboard.py")

