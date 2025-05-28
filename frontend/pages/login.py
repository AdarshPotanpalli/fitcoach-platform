import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend.utils import login_user

def show_login():
    # st.set_page_config(page_title="Login", page_icon="🔐")
    
    # login form
    with st.form(st.session_state.login_form_key, clear_on_submit=True):
        st.title("🔐 Login")
        st.markdown("Welcome back! Please log in to continue.")
        
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")

    if submit:
        if not email or not password:
            st.warning("⚠️ Please enter both email and password.")
        elif "@" not in email or "." not in email:
            st.error("❌ Enter a valid email.")
        else:
            # st.success(f"Form submitted with email: {email}")
            # You can trigger the backend login logic here later
            
            try:    
                # login the user
                login_payload = {
                    "username": email, # fastapi OAuth2PasswordRequestForm uses "username"
                    "password": password
                }
                login_response = requests.post(url = (API_URL+ "/auth/login"), data= login_payload)
                if login_response.status_code == 200:
                    st.success("User logged in successfully!")
                    token = login_response.json().get("token")
                    login_user(token)
                    st.rerun()                     
                else:
                    error_detail = login_response.json().get("detail", "Something wrong happened!")
                    st.error(error_detail)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the server: {e}")
        
    st.markdown("---")
    if st.button("📝 Don't have an account? Register here"):
        st.switch_page("pages/register.py")
    
if __name__ == "__main__":
    
    show_login()
