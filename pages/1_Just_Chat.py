import streamlit as st
import time
import threading
from common import api_interaction
import os
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="Just Chat",
    page_icon="👋",
)

# Streamlit app title
st.title("AI Chatbot Multi API with Streamlit")
st.markdown("Chat with OpenAI, Claude, or DeepSeek!")

# Sidebar for API selection
st.sidebar.title("Settings")
api_choice = st.sidebar.selectbox("Choose AI API", ["OpenAI", "Claude", "DeepSeek"])

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.creation_time = time.time()

# Function to clear memory
def clear_memory():
    st.session_state.messages = []
    st.session_state.creation_time = time.time()
    
clear_memory()

# Button to clear memory manually
if st.sidebar.button("Clear Memory"):
    clear_memory()

# Function to clear memory after 7 minutes
def auto_clear_memory():
    time.sleep(420)  # 7 minutes
    clear_memory()

# Start the memory clearing thread
threading.Thread(target=auto_clear_memory, daemon=True).start()

# Sort messages by timestamp (assuming each message has a 'timestamp' field)
st.session_state.messages.sort(key=lambda x: x.get('timestamp', 0))

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history with timestamp
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": time.time()})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI response based on selected API
    with st.spinner("Thinking..."):
        # Prepare context from chat history
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        bot_response = api_interaction.getAIResponse(api_choice, context, user_input)

    # Add bot response to chat history with timestamp
    st.session_state.messages.append({"role": "assistant", "content": bot_response, "timestamp": time.time()})
    with st.chat_message("assistant"):
        st.markdown(bot_response)

# Check if 7 minutes have passed and clear memory if necessary
if time.time() - st.session_state.creation_time > 420:
    clear_memory()
