import streamlit as st

# Initialize states
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "redirect_to_dashboard" not in st.session_state:
    st.session_state.redirect_to_dashboard = False

# Handle redirect after session state updates
if st.session_state.redirect_to_dashboard:
    st.session_state.redirect_to_dashboard = False  # Reset it
    st.switch_page("pages/dashboard.py")

# Toggle logic
if st.session_state.authenticated:
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.switch_page("pages/user_guide.py")
else:
    if st.button("🔐 Login"):
        st.session_state.authenticated = True
        st.session_state.redirect_to_dashboard = True
        st.rerun()  # Let sidebar update before redirect
