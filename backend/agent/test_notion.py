"""
Test script to check Notion API setup
"""
import os
from notion_client import Client

# Check environment variables
print("Checking environment variables...")
notion_api_key = os.getenv("NOTION_API_KEY")
notion_db_id = os.getenv("NOTION_DATABASE_ID")

print(f"NOTION_API_KEY: {'SET' if notion_api_key else 'NOT SET'}")
print(f"NOTION_DATABASE_ID: {'SET' if notion_db_id else 'NOT SET'}")

if not notion_api_key or not notion_db_id:
    print("\n❌ Environment variables are not set!")
    print("Please set the following environment variables:")
    print("export NOTION_API_KEY='your_notion_api_key_here'")
    print("export NOTION_DATABASE_ID='your_notion_database_id_here'")
    exit(1)

# Test Notion connection
try:
    print("\nTesting Notion connection...")
    notion = Client(auth=notion_api_key)
    
    # Try to get database info
    database = notion.databases.retrieve(database_id=notion_db_id)
    print(f"✅ Successfully connected to Notion database: {database['title'][0]['plain_text']}")
    
    # Test creating a simple page
    print("\nTesting page creation...")
    response = notion.pages.create(
        parent={"database_id": notion_db_id},
        properties={
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Test Page from Human Rights LLM"
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
    
except Exception as e:
    print(f"❌ Error connecting to Notion: {str(e)}")
    print("\nPlease check:")
    print("1. Your NOTION_API_KEY is correct")
    print("2. Your NOTION_DATABASE_ID is correct")
    print("3. Your Notion integration has access to the database") 