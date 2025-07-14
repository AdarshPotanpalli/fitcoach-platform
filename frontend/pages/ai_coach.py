import streamlit as st
import random
import time
import requests
from frontend.streamlit_app import API_URL
from frontend import utils

headers = {
    "Authorization": f"Bearer {utils.get_token()}"
}

def stream_from_api(user_input: str):
    
    """Generator to stream messages from the API."""
    
    response = requests.post(
        f"{API_URL}/coach",
        json={"user_query": user_input},
        stream=True,
        headers=headers
    )
    
    if response.status_code !=200:
        yield "⚠️ Error from server."
    else:
        for chunk in response.iter_lines(decode_unicode=True):
            if chunk:
                yield chunk + " "

# get the username ------>
response_user = requests.get(API_URL + "/me", headers=headers)
if response_user.status_code == 200:
    user_data = response_user.json()
    username = user_data.get("username", "User")

st.title(f"🦾💬 {username}'s coach")

plans_response = requests.get(API_URL + "/plans", headers = headers)
if plans_response.status_code == 404:
    # if no plan exists, then display a button to redirect to the onboarding page
    
    st.error("To use the AI Coach, you need to set your preferences first.")
    if st.button("Set your preferences"):
        st.switch_page("pages/onboarding_form.py")
else:
    # Initialize session state for chat history
    if "history" not in st.session_state:
        st.session_state.history = {} 
        
    # different session state history for different users as a dictionary
    current_user_response = requests.get(API_URL + "/me", headers=headers)
    if current_user_response.status_code != 200:
        st.error("Error fetching user data.")
    else:
        current_user_data = current_user_response.json()
        st.session_state.user_email = current_user_data.get("email", "unknown_user")
        if st.session_state.user_email not in st.session_state.history:
            st.session_state.history[st.session_state.user_email] = []

    # Display chat history
    for message in st.session_state.history[st.session_state.user_email]:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])



    # Input field for user query
    user_input = st.chat_input("Ask anything related to your plans, nutrition, fitness, etc...")

    if user_input:
        # Placeholder for AI response (replace with your AI logic)
        st.chat_message("user").write(user_input)
        st.session_state.history[st.session_state.user_email].append({"role": "user", "content": user_input})
        
        with st.chat_message("assistant"):
            markdown_placeholder = st.empty()  # Placeholder for streaming markdown
            full_response = ""
            for chunk in stream_from_api(user_input):
                full_response += "\n" + chunk
                markdown_placeholder.markdown(full_response)  # Re-render as markdown each step

        st.session_state.history[st.session_state.user_email].append({"role": "assistant", "content": full_response})
