"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: app.py
Description: Streamlit app for the LLM
"""
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
from backend.tools.rag_chain import retrieve_documents
#from backend.memory.chat_memory import chat_history
from backend.memory import sql_chat_memory as chat_history
from langchain_core.messages import HumanMessage, AIMessage
import requests

#ensure the database exists
chat_history.init_chat_table()

st.set_page_config(page_title="Human Rights RAG Chatbot", layout="wide")
st.title("🕊️ Human Rights RAG Chatbot")

#Sidebar to retain chat history
st.sidebar.title("Chat History")
if st.sidebar.button("Clear history"):
    chat_history.clear_chat_history()
    st.rerun()

messages = chat_history.load_messages()

for i, msg in enumerate(messages):
    role = "User" if isinstance(msg, HumanMessage) else "AI"
    st.sidebar.markdown(f"**{role}** {msg.content[:100]}...")

#Main chat interface
user_input = st.text_input("Ask a question about human rights:", key="user_input")

if user_input:
    chat_history.save_message("user", user_input)
    try:
        response = requests.post(
            "http://localhost:5000/api/agent", 
            json={"query": user_input},
            timeout=60
        )
        response_data = response.json()
        response = response_data.get("result", "Error: No response from agent")
    except Exception as e:
        response = f"Error: {str(e)}"
    chat_history.save_message("ai", response)

#display convo
for msg in chat_history.load_messages():
    if isinstance(msg, HumanMessage):
        st.markdown(f"**User:** {msg.content}")
    elif isinstance(msg, AIMessage):
        st.markdown(f"**AI:** {msg.content}")
    st.markdown("---")