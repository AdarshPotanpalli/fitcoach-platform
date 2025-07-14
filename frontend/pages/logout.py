import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend import utils

headers = {
            "Authorization": f"Bearer {utils.get_token()}"
        }

def show_logout():
    # st.set_page_config(page_title="Logout", page_icon="🚪")
    st.title("🚪 Logout")

    st.markdown("Thank you for using FitCoach! I'd love to hear your views before you go.")

    st.subheader("🗣️ How was your experience?")
    feedback = st.feedback("faces")

    # Optional Feedback Text
    comments = st.text_area("💬 Additional Comments (optional):", placeholder="Tell us what you liked or what could be improved...")

    # Button to submit user experience feedback

    if st.button("Submit your app experience", use_container_width=True):
        user_experience_json = {}
        if feedback is not None:
            user_experience_json["experience_rating"] = feedback + 1
            if comments:
                user_experience_json["experience_comments"] = comments
            try:
                response_user_experience = requests.post(url=(API_URL+"/user_ratings_comments"),
                                                            json = user_experience_json,
                                                            headers=headers)
                if response_user_experience.status_code == 201:
                    st.toast("Thank you for your app experience feedback! 🙏")
            except requests.exceptions.RequestException:
                st.toast("Something went wrong, please try again later.")
        else:
            st.toast("Please select a face to rate your app experience.")
    
    # Logout Button
    if st.button("Logout", use_container_width=True):
        # Perform logout logic here (API call + cookies cleanup)
        try:
            
            logout_response = requests.post(url=(API_URL+"/auth/logout"), headers=headers)
            if logout_response.status_code == 200: 
                st.success("✅ You’ve been logged out successfully!")
                st.rerun()
            else:
                error_detail = logout_response.json().get("detail", "Something wrong happened!")
                st.error(error_detail)
        except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the server: {e}")

if __name__ == "__main__":
    show_logout()
