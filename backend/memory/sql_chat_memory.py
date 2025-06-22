"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: sql_chat_memory.py
Description: Retains chat history in a SQL table with session management
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
        # Create sessions table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Check if chat_history table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create new table with session_id
            conn.execute("""
            CREATE TABLE chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
        else:
            # Check if session_id column exists
            cursor = conn.execute("PRAGMA table_info(chat_history)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'session_id' not in columns:
                # Drop and recreate table with session_id (SQLite limitation)
                print("Updating chat_history table schema...")
                conn.execute("DROP TABLE chat_history")
                conn.execute("""
                CREATE TABLE chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
        
        conn.commit()

def create_new_session(title: str = None) -> int:
    """Create a new chat session and return the session ID"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
        INSERT INTO chat_sessions (title) VALUES (?)
        """, (title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",))
        session_id = cursor.lastrowid
        conn.commit()
        return session_id

def save_message(role: str, content: str, session_id: int = None):
    """Save a message to a specific session"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)
        """, (session_id, role, content))
        conn.commit()

def load_messages(session_id: int = None):
    """Load messages for a specific session or all messages if no session_id"""
    with sqlite3.connect(DB_PATH) as conn:
        if session_id:
            rows = conn.execute("""
                SELECT role, content FROM chat_history 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            """, (session_id,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT role, content FROM chat_history 
                ORDER BY timestamp ASC
            """).fetchall()
        
        return [
            HumanMessage(content=row[1]) if row[0] == "user" else AIMessage(content=row[1])
            for row in rows
        ]

def get_chat_sessions():
    """Get all chat sessions with their titles"""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT id, title FROM chat_sessions 
            ORDER BY created_at DESC
        """).fetchall()
        return rows

def clear_chat_history():
    """Clear all chat history and sessions"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM chat_history")
        conn.execute("DELETE FROM chat_sessions")
        conn.commit()

