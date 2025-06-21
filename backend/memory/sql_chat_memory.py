"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: sql_chat_memory.py
Description: Retains chat history in a SQL table
"""

import sqlite3
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from pathlib import Path

# Define the absolute path to the database
DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "db" / "documents.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True) 



def init_chat_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

def save_message(role: str, content: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        INSERT INTO chat_history (role, content) VALUES (?, ?)
        """, (role, content))
        conn.commit()

def load_messages():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT role, content FROM chat_history ORDER BY timestamp ASC").fetchall()
        return [
            HumanMessage(content=row[1]) if row[0] == "user" else AIMessage(content=row[1])
            for row in rows
        ]

def clear_chat_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM chat_history")
        conn.commit()

