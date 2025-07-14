import streamlit as st
import requests
from frontend.streamlit_app import API_URL
from frontend import utils

def show_logout():
    # st.set_page_config(page_title="Logout", page_icon="🚪")
    st.title("🚪 Logout")

    st.markdown("Thank you for using FitCoach! I'd love to hear your views before you go.")

    st.subheader("🗣️ How was your experience?")
    # sentiment_mapping = [
    #     "Loved it! Everything worked smoothly.",
    #     "It was good, but there's room for improvement.",
    #     "It was okay, but I expected more.",
    #     "I ran into a few issues.",
    #     "Not satisfied. Needs major improvements."
    # ]
    feedback = st.feedback("faces")
    # if feedback is not None:
    #     st.markdown(f"You selected {feedback+1} star(s).")

    # Optional Feedback Text
    comments = st.text_area("💬 Additional Comments (optional):", placeholder="Tell us what you liked or what could be improved...")

    # Logout Button
    if st.button("Logout", use_container_width=True):
        # Perform logout logic here (API call + cookies cleanup)
        try:
            headers = {
                "Authorization": f"Bearer {utils.get_token()}"
            }
            logout_response = requests.post(url=(API_URL+"/auth/logout"), headers=headers)
            if logout_response.status_code == 200: 
                st.success("✅ You’ve been logged out successfully!")
                # # Optionally print or log feedback
                # st.toast(f"Feedback: {feedback} stars")
                # if comments:
                #     st.info(f"Comments: {comments}")

                # Clear cookies
                # utils.logout_user()

                st.rerun()
            else:
                error_detail = logout_response.json().get("detail", "Something wrong happened!")
                st.error(error_detail)
        except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the server: {e}")

if __name__ == "__main__":
    show_logout()
