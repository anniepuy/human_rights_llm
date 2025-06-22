"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: app.py
Description: Streamlit app for the LLM
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1])) 

import streamlit as st
from backend.core.rag_chain import run_rag_chain
from backend.memory import sql_chat_memory as chat_history
from langchain_core.messages import HumanMessage, AIMessage
import requests
import logging

# Add project root to path
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
logger.debug(f"Calculated PROJECT_ROOT: {PROJECT_ROOT}")
logger.debug(f"sys.path before append: {sys.path}")
sys.path.insert(0, str(PROJECT_ROOT))
logger.debug(f"sys.path after append: {sys.path}")

# Verify backend module
try:
    import backend
    logger.debug("Successfully imported backend module")
except ImportError as e:
    logger.error(f"Failed to import backend module: {str(e)}")
    raise

# Initialize the chat database tables
chat_history.init_chat_table()

st.set_page_config(page_title="Human Rights RAG Chatbot", layout="wide")
st.title("🕊️ Human Rights RAG Chatbot")

# Initialize session state for current chat
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'current_messages' not in st.session_state:
    st.session_state.current_messages = []
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Sidebar for chat history
st.sidebar.title("Chat History")

# Ingest Pipeline button
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Management:**")

if st.sidebar.button("Run Ingest Pipeline"):
    with st.spinner("Running ingest pipeline... This may take a few minutes."):
        try:
            response = requests.post(
                "http://localhost:5001/api/ingest",
                timeout=300  # 5 minute timeout
            )
            response_data = response.json()
            
            if response_data.get("status") == "success":
                st.sidebar.success("Ingest pipeline completed!")
                st.sidebar.info("New data has been processed and is ready for queries.")
            else:
                st.sidebar.error(f"Ingest failed: {response_data.get('message', 'Unknown error')}")
                
        except requests.exceptions.Timeout:
            st.sidebar.error("Ingest pipeline timed out (5 minutes)")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")

# New Chat button
st.sidebar.markdown("---")
st.sidebar.markdown("**Chat Management:**")

if st.sidebar.button("New Chat"):
    st.session_state.current_chat_id = None
    st.session_state.current_messages = []
    st.session_state.input_key += 1
    st.rerun()

# Clear all history button
if st.sidebar.button("🗑️ Clear All History"):
    chat_history.clear_chat_history()
    st.session_state.current_chat_id = None
    st.session_state.current_messages = []
    st.session_state.input_key += 1
    st.rerun()

# Load and display chat history
st.sidebar.markdown("---")
st.sidebar.markdown("**Previous Chats:**")

# Get all chat sessions
chat_sessions = chat_history.get_chat_sessions()

for session_id, session_info in chat_sessions:
    if st.sidebar.button(f"{session_info[:50]}...", key=f"session_{session_id}"):
        st.session_state.current_chat_id = session_id
        st.session_state.current_messages = chat_history.load_messages(session_id)
        st.session_state.input_key += 1
        st.rerun()

# Main chat interface
st.markdown("---")

# Display current chat messages in a growing container
chat_container = st.container()

with chat_container:
    for msg in st.session_state.current_messages:
        if isinstance(msg, HumanMessage):
            st.markdown(f"**👤 You:** {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"**🤖 AI:** {msg.content}")
        st.markdown("---")

# Input area at the bottom
st.markdown("---")
user_input = st.text_input(
    "Ask a question about human rights:", 
    key=f"user_input_{st.session_state.input_key}",
    placeholder="Enter your human rights query here..."
)

# Process user input
if user_input and user_input.strip():
    # Save user message to current session
    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = chat_history.create_new_session()
    
    chat_history.save_message("user", user_input, st.session_state.current_chat_id)
    
    # Add to current display
    st.session_state.current_messages.append(HumanMessage(content=user_input))
    
    # Get AI response
    try:
        with st.spinner("🤖 Thinking..."):
            response = requests.post(
                "http://localhost:5001/api/agent", 
                json={"query": user_input},
                timeout=120  
            )
            response_data = response.json()
            ai_response = response_data.get("result", "Error: No response from agent")
            notion_success = response_data.get("notion_success", False)
    except requests.exceptions.Timeout:
        ai_response = "Error: Request timed out. The query may be too complex or the server is slow."
        notion_success = False
    except requests.RequestException as e:
        ai_response = f"Error: {str(e)}"
        notion_success = False
    
    # Save AI response
    chat_history.save_message("ai", ai_response, st.session_state.current_chat_id)
    st.session_state.current_messages.append(AIMessage(content=ai_response))
    
    # Display Notion publishing status
    if notion_success:
        st.success("Report published to Notion.")
    else:
        st.error("Failed to publish to Notion.")
    
    # Clear input and refresh
    st.session_state.input_key += 1
    st.rerun()