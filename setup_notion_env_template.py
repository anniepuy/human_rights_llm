#!/usr/bin/env python3
"""
Template for setting up Notion environment variables
Copy this file to set_notion_env.py and fill in your actual API key
"""
import os

# TODO: Replace with your actual Notion API key from https://www.notion.so/my-integrations
NOTION_API_KEY = "your_notion_api_key_here"

print("Setting up Notion environment variables...")
print(f"API Key: {NOTION_API_KEY[:10] if NOTION_API_KEY != 'your_notion_api_key_here' else 'NOT SET'}...")

# Create .env file
with open('.env', 'w') as f:
    f.write(f"NOTION_API_KEY={NOTION_API_KEY}\n")
    f.write("NOTION_DATABASE_ID=your_database_id_here\n")

# Set environment variables for current session
os.environ['NOTION_API_KEY'] = NOTION_API_KEY

print("✅ Environment variables set in .env file!")
print("⚠️  You still need to:")
print("1. Get your Notion Database ID from your database URL")
print("2. Update the .env file with your database ID")
print("3. Make sure your Notion integration has access to the database")

# Test the API key
if NOTION_API_KEY != "your_notion_api_key_here":
    try:
        from notion_client import Client
        notion = Client(auth=NOTION_API_KEY)
        
        # Try to list databases to test the connection
        response = notion.search(filter={"property": "object", "value": "database"})
        print(f"✅ API key is valid! Found {len(response['results'])} databases")
        
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
else:
    print("❌ Please set your actual Notion API key in this file") 