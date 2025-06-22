import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = "21a8568dd63d80e99bb5dc9d1cfa8e4d"  # Replace with your actual Notion page ID

notion = Client(auth=NOTION_API_KEY)

try:
    response = notion.blocks.children.append(
        block_id=NOTION_PAGE_ID,
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Test from script"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "If you see this, Notion API works!"}}]
                }
            }
        ]
    )
    print("Successfully appended blocks to the page!")
except Exception as e:
    print(f"Failed to append blocks: {e}") 