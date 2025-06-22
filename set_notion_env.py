#!/usr/bin/env python3
"""
Set up Notion environment variables
"""
import os

# Your Notion API key
NOTION_API_KEY = "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"

print("Setting up Notion environment variables...")
print(f"API Key: {NOTION_API_KEY[:10]}...")

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
try:
    from notion_client import Client
    notion = Client(auth=NOTION_API_KEY)
    
    # Try to list databases to test the connection
    response = notion.search(filter={"property": "object", "value": "database"})
    print(f"✅ API key is valid! Found {len(response['results'])} databases")
    
except Exception as e:
    print(f"❌ Error testing API key: {str(e)}") 