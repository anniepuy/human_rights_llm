import sqlite3
import pandas as pd
from pathlib import Path

# Path to the database
DB_PATH = Path(__file__).parent.parent / "db" / "documents.db"

def check_database():
    """Check the contents of the SQLite database"""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    print(f"📊 Database found at: {DB_PATH}")
    print(f"📏 Database size: {DB_PATH.stat().st_size / (1024*1024):.2f} MB")
    print("-" * 50)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    # Get table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("📋 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    print("-" * 50)
    
    # Check documents table
    if ('documents',) in tables:
        print("📄 Documents table contents:")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        print(f"  Total documents: {count}")
        
        # Get sample data
        df = pd.read_sql_query("SELECT * FROM documents LIMIT 5", conn)
        print("\n  Sample data (first 5 rows):")
        print(df.to_string(index=False))
        
        # Get document types
        cursor.execute("SELECT document_type, COUNT(*) FROM documents GROUP BY document_type")
        doc_types = cursor.fetchall()
        print(f"\n  Document types:")
        for doc_type, count in doc_types:
            print(f"    {doc_type}: {count}")
        
        # Get sources
        cursor.execute("SELECT source, COUNT(*) FROM documents GROUP BY source")
        sources = cursor.fetchall()
        print(f"\n  Sources:")
        for source, count in sources:
            print(f"    {source}: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 