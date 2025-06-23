# Notion Setup Guide

This guide will help you set up Notion integration for the Human Rights LLM project.

## Prerequisites

1. A Notion account
2. A Notion database where you want to store reports

## Step 1: Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "Human Rights LLM")
4. Select the workspace where your database is located
5. Click "Submit"
6. Copy the **Internal Integration Token** (this is your API key)

## Step 2: Get Your Database ID

1. Open your Notion database in the browser
2. Copy the URL - it will look like: `https://www.notion.so/your-workspace/DATABASE_ID=...`
3. The database ID is the part after the last `/` and before the `?v=`

## Step 3: Set Up Environment Variables

### Option A: Using the Template Script

1. Copy the template file:

   ```bash
   cp setup_notion_env_template.py set_notion_env.py
   ```

2. Edit `set_notion_env.py` and replace `your_notion_api_key_here` with your actual API key

3. Run the script:

   ```bash
   python set_notion_env.py
   ```

4. Edit the `.env` file and add your database ID:
   ```
   NOTION_API_KEY=your_actual_api_key
   NOTION_DATABASE_ID=your_database_id
   ```

### Option B: Using the Shell Script

1. Run the interactive setup:

   ```bash
   chmod +x setup_notion_env.sh
   ./setup_notion_env.sh
   ```

2. Enter your API key and database ID when prompted

### Option C: Manual Setup

1. Create a `.env` file in the project root:
   ```
   NOTION_API_KEY=your_actual_api_key
   NOTION_DATABASE_ID=your_database_id
   ```

## Step 4: Share Database with Integration

1. Open your Notion database
2. Click the "Share" button in the top right
3. Click "Invite"
4. Search for your integration name (e.g., "Human Rights LLM")
5. Select it and click "Invite"

## Step 5: Test the Setup

Run the test script to verify everything is working:

```bash
python backend/tests/test_notion.py
```
