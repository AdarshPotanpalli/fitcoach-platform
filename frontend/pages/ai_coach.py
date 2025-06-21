import streamlit as st
import random
import time
import requests
from frontend.streamlit_app import API_URL
from frontend import utils

st.title("🤖 Your AI Coach Chatbot")

headers = {
    "Authorization": f"Bearer {utils.get_token()}"
}

# Initialize session state for chat history
if "history" not in st.session_state:
    st.session_state.history = [] 

# Display chat history
for message in st.session_state.history:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

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
    

# Chat message input
user_input = st.chat_input("Ask me anything about your health or workout...")

if user_input:
    # Placeholder for AI response (replace with your AI logic)
    st.chat_message("user").write(user_input)
    st.session_state.history.append({"role": "user", "content": user_input})
    
    
    with st.chat_message("assistant"):
        response = st.write_stream(stream_from_api(user_input))
    st.session_state.history.append({"role": "assistant", "content": response})
