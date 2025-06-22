#!/usr/bin/env python3
"""
Update .env file with database ID
"""
import os

# Update .env file with the database ID
NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "21a8568d-d63d-80b6-89e6-c44f58708137"  # Untitled database

print("Updating .env file with database ID...")

# Update .env file
with open('.env', 'w') as f:
    f.write(f"NOTION_API_KEY={NOTION_API_KEY}\n")
    f.write(f"NOTION_DATABASE_ID={NOTION_DATABASE_ID}\n")

# Set environment variables for current session
os.environ['NOTION_API_KEY'] = NOTION_API_KEY
os.environ['NOTION_DATABASE_ID'] = NOTION_DATABASE_ID

print("✅ .env file updated!")
print(f"Database ID: {NOTION_DATABASE_ID}")

# Test the complete setup
print("\nTesting complete setup...")
try:
    from notion_client import Client
    notion = Client(auth=NOTION_API_KEY)
    
    # Try to get database info
    database = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
    title = database['title'][0]['plain_text'] if database['title'] else "Untitled"
    print(f"✅ Successfully connected to database: {title}")
    
    # Test creating a simple page
    print("Testing page creation...")
    response = notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Test Page - Human Rights LLM"
                        }
                    }
                ]
            }
        }
    )
    print(f"✅ Successfully created test page: {response['id']}")
    
    # Clean up - delete the test page
    notion.pages.update(page_id=response['id'], archived=True)
    print("✅ Test page deleted")
    
    print("\n🎉 Everything is working! You can now run your agent.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("You may need to:")
    print("1. Share the database with your integration")
    print("2. Check if the database has the required properties (Name, Date, Source)") 