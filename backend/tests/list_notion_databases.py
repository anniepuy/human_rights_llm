#!/usr/bin/env python3
"""
List all available Notion databases
"""
import os
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
notion = Client(auth=NOTION_API_KEY)

print("Available Notion databases:")
print("=" * 50)

try:
    # Search for databases
    response = notion.search(filter={"property": "object", "value": "database"})
    
    for i, database in enumerate(response['results'], 1):
        title = database['title'][0]['plain_text'] if database['title'] else "Untitled"
        db_id = database['id']
        print(f"{i}. {title}")
        print(f"   ID: {db_id}")
        print(f"   URL: https://notion.so/{db_id.replace('-', '')}")
        print()
    
    if response['results']:
        print("To use a database, copy its ID and update your .env file:")
        print("NOTION_DATABASE_ID=your_chosen_database_id")
    else:
        print("No databases found. Make sure your integration has access to databases.")
        
except Exception as e:
    print(f"Error listing databases: {str(e)}") 