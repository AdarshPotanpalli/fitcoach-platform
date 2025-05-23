import streamlit as st

st.title("🤖 Your AI Coach Chatbot")

# Chat message input
user_input = st.chat_input("Ask me anything about your health or workout...")

if user_input:
    # Placeholder for AI response (replace with your AI logic)
    response = f"Received: {user_input}"
    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(response)
