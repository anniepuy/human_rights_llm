"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: notion_react_agent.py
Description: ReACT agent that takes a user query, drafts a report, and publishes it to Notion
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from notion_client import Client

# Load environment variables
load_dotenv()

#Notion API set up
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Check if environment variables are set
if not NOTION_API_KEY or not NOTION_DATABASE_ID:
    raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID must be set in environment variables or .env file")

notion = Client(auth=NOTION_API_KEY)

#Tool function
def publish_to_notion(title: str, content: str, date: str = "2025-01-27", source: str = "Human Rights LLM Report") -> str:
    try:
        print("Publishing report to Notion...")
        print(f"Title: {title}")
        print(f"Date: {date}")
        print(f"Source: {source}")
        print(f"Content preview: {content[:100]}...")

        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": date
                    }
                },
                "Source": {
                    "rich_text": [
                        {
                            "text": {
                                "content": source
                            }
                        }
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]
        )

        print(f"Report published to Notion. Page ID: {response['id']}")
        return f"Report published to Notion. Page ID: {response['id']}"

    except Exception as e:
        print(f"Failed to publish to Notion: {str(e)}")
        return f"Failed to publish to Notion: {str(e)}"

#Tools# 1 LangChain tool decorator
@tool("publish_to_notion")
def publish_to_notion_tool(title: str, content: str, date: str = "2025-01-27", source: str = "Human Rights LLM Report") -> str:
    """
    Tool that publishes a summary report to Notion. 
    Provide title and content as separate arguments. Date and source have default values.
    """
    return publish_to_notion(title, content, date, source)

#Tool# 2 Summarize
@tool("summarize_query")
def summarize_query(query: str) -> str:
    """
    Use the LLM to generate a summary of the human rights topic in markdown format
    """
    llm = ChatOllama(model="llama3:8b")
    messages = [
        HumanMessage(content=f"Summarize the following human rights topic in markdown format:\n\n{query}")
    ]
    return llm.invoke(messages).content

#The ReACT agent
llm = ChatOllama(model="llama3:8b")
tools = [summarize_query, publish_to_notion_tool]

# Create a simple prompt for the ReACT agent
prompt = PromptTemplate.from_template(
    """You are a human rights expert and researcher that can summarize human rights topics and publish reports to Notion.

        Follow these steps exactly:
        1. Use the 'summarize_query' tool to create a summary of the topic.
        2. Use the 'publish_to_notion' tool to publish the summary in JSON format.

        For the 'publish_to_notion' tool, use this format:
        {{
            "title": "<short report title>",
            "content": "<full markdown summary>",
            "date": "<YYYY-MM-DD>",
            "source": "<name of source or report>"
        }}

        3. After both tools are used successfully, provide a Final Answer.

        IMPORTANT: Once you have used both tools successfully, you MUST provide a Final Answer.
        Do not continue using tools after the report is published.

        Tools: {tools}

        Question: {input}
        Thought: I should think about what steps to take to answer this question.
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer.
        Final Answer: Successfully created and published a report on [topic]. The report has been saved to Notion.

        {agent_scratchpad}
    """
)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    handle_parsing_errors=True, 
    verbose=True,
    max_iterations=5  # Prevent infinite loops
)

#Entry point
def run_agent(user_query: str):
    """
    Execute the ReACT agent pipeline: summarize and publish
    """
    return agent_executor.invoke({"input": user_query})

#Direct testing block
if __name__ == "__main__":
    user_query = "Summarize the current human rights violations in Iraq and publish the findings."
    result = run_agent(user_query)
    print(result)