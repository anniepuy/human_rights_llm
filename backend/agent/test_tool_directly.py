#!/usr/bin/env python3
"""
Test the publish_to_notion_tool directly to verify it works
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from notion_client import Client

# Load environment variables
load_dotenv()

# Notion API set up
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = "21a8568dd63d80e99bb5dc9d1cfa8e4d"

notion = Client(auth=NOTION_API_KEY)

class PublishToNotionInput(BaseModel):
    title: str = Field(..., description="The title of the report.")
    content: str = Field(..., description="The full report to publish.")
    date: str = Field(..., description="The date of the report.")
    source: str = Field(..., description="The source of the report.")

@tool("publish_to_notion", args_schema=PublishToNotionInput)
def publish_to_notion_tool(input: PublishToNotionInput) -> str:
    """
    Publishes a report to a Notion page as a set of blocks (heading, metadata, content).
    """
    print("[DEBUG] publish_to_notion_tool called!")
    print(f"[DEBUG] Title: {input.title}")
    print(f"[DEBUG] Date: {input.date}")
    print(f"[DEBUG] Source: {input.source}")
    print(f"[DEBUG] Content preview: {input.content[:100]}...")
    
    # Convert Pydantic model to plain text for Notion
    title_text = str(input.title)
    content_text = str(input.content)
    date_text = str(input.date) if input.date else "2025-01-27"
    source_text = str(input.source) if input.source else "Human Rights LLM Report"
    
    try:
        response = notion.blocks.children.append(
            block_id=NOTION_PAGE_ID,
            children=[
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": title_text}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": f"Date: {date_text} | Source: {source_text}"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content_text}}]
                    }
                }
            ]
        )
        resp = notion.blocks.children.append(...)
        print("[Notion Response]:", resp)
        print("[DEBUG] Successfully published to Notion!")
        return f"Report successfully published to Notion page {NOTION_PAGE_ID}"
    except Exception as e:
        print(f"[DEBUG] Failed to publish to Notion: {str(e)}")
        return f"Failed to publish to Notion: {str(e)}"

# Test the tool directly
if __name__ == "__main__":
    print("Testing publish_to_notion_tool directly...")
    
    test_input = PublishToNotionInput(
        title="Test Report - Direct Tool Call",
        content="This is a test report to verify the tool works correctly when called directly.",
        date="2025-01-27",
        source="Direct Tool Test"
    )
    
    result = publish_to_notion_tool.invoke(test_input.dict())
    print(f"Tool result: {result}") 