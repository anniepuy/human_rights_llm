#!/bin/bash

echo "Setting up Notion environment variables..."
echo ""

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file..."
    touch .env
fi

echo "Please enter your Notion API Key (from https://www.notion.so/my-integrations):"
read -s NOTION_API_KEY

echo "Please enter your Notion Database ID (from the URL of your database):"
read NOTION_DATABASE_ID

# Add to .env file
echo "NOTION_API_KEY=$NOTION_API_KEY" >> .env
echo "NOTION_DATABASE_ID=$NOTION_DATABASE_ID" >> .env

# Also export for current session
export NOTION_API_KEY=$NOTION_API_KEY
export NOTION_DATABASE_ID=$NOTION_DATABASE_ID

echo ""
echo "✅ Environment variables set!"
echo "NOTION_API_KEY: ${NOTION_API_KEY:0:10}..."
echo "NOTION_DATABASE_ID: $NOTION_DATABASE_ID"
echo ""
echo "To make these permanent, add to your shell profile (.zshrc, .bashrc, etc.):"
echo "source .env"
echo ""
echo "Testing connection..."
python backend/agent/test_notion.py 