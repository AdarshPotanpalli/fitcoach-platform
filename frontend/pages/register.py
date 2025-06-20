import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend import utils

def show_register():
    # st.set_page_config(page_title="Register", page_icon="📝")
    

    with st.form("register", clear_on_submit=True):
        st.title("📝 Create an Account")
        st.markdown("Fill in the form below to register.")
        
        email = st.text_input("Email", placeholder="you@example.com")
        username = st.text_input("Username", placeholder="username")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
        submit = st.form_submit_button("Register")

    if submit:
        if not email or not password or not confirm_password:
            st.warning("⚠️ Please fill in all fields.")
        elif "@" not in email or "." not in email:
            st.error("❌ Enter a valid email.")
        elif len(username) < 3:
            st.error("❌ Username must be at least 3 characters long.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            # st.success(f"Account ready to be created for: {email}")
            # Backend registration logic would go here
            payload = {"email": email,
                        "username": username,
                        "password": password}
            # try registering the user
            try:
                response = requests.post(url= (API_URL + "/auth/register"), json= payload)
                if response.status_code == 201:
                    st.success("Account registered successfully!")
                    st.session_state.new_register = True  # Set the new registration state
                    
                    # login the user
                    login_payload = {
                        "username": email, # fastapi OAuth2PasswordRequestForm uses "username"
                        "password": password
                    }
                    login_response = requests.post(url = (API_URL+ "/auth/login"), data= login_payload)
                    if login_response.status_code == 200:
                        st.success("User logged in successfully!")
                        token = login_response.json().get("token")
                        utils.login_user(token) # set the encrypted token cookie
                        st.rerun()
                    else:
                        st.warning("Registration succeeded but login failed. Please log in manually!")
                        
                else:
                    error_detail = response.json().get("detail", "Something wrong happened!")
                    st.error(error_detail)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the server: {e}")
    
    st.markdown("---")
    if st.button("🔐 Already have an account? Log in here"):
        st.switch_page("pages/login.py")


if __name__ == "__main__":
    show_register()