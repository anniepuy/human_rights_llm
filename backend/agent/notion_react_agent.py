"""
Application: Human Rights LLM
Author: Ann Hagan
Date: 06-21-2025
Description: ReACT agent that summarizes a human rights topic and appends it to your Notion page.
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
from datetime import datetime

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
PAGE_ID = "21a8568dd63d80e99bb5dc9d1cfa8e4d"

if not NOTION_API_KEY:
    raise ValueError("Please set NOTION_API_KEY in .env")

notion = Client(auth=NOTION_API_KEY)

from datetime import date
today = str(date.today())

class PublishToNotionInput(BaseModel):
    title: str = Field(..., description="Report title")
    content: str = Field(..., description="Markdown summary")
    date: str = Field(..., description=today)
    source: str = Field(..., description="Source name")

@tool("publish_to_notion", args_schema=PublishToNotionInput)
def publish_to_notion_tool(input: PublishToNotionInput) -> str:
    """
    Publishes a markdown summary report of human rights to a Notion page.
    """
    print(f"[DEBUG] Publishing to Notion")
    print(f"title: {input.title}, date: {input.date}, source: {input.source}")
    title = input.title.strip()
    metadata = f"Date: {input.date} | Source: {input.source}"
    body = input.content.strip()
    resp =notion.blocks.children.append(
        block_id=PAGE_ID,
        children=[
            {"object": "block", "type": "heading_2",
             "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}]}},
            {"object": "block", "type": "paragraph",
             "paragraph": {"rich_text": [{"type": "text", "text": {"content": metadata}}]}},
            {"object": "block", "type": "paragraph",
             "paragraph": {"rich_text": [{"type": "text", "text": {"content": body}}]}},
        ],
    )
    return "Done"

@tool("summarize_query")
def summarize_query(query: str) -> str:
    """
    Summarizes a given human rights topic into markdown format.
    """
    llm = ChatOllama(model="llama3:8b")
    msg = HumanMessage(content=f"Summarize the following human rights topic in markdown format:\n\n{query}")
    return llm.invoke([msg]).content

llm = ChatOllama(model="llama3:8b")
tools = [summarize_query, publish_to_notion_tool]

prompt = PromptTemplate.from_template(
    """
        You are a helpful human rights expert with access to tools to summarize topics and publish reports.

            Use the following tools:
            {tools}

            When answering, follow this format strictly:

            Question: the input question you must answer
            Thought: think about what to do
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat)
            Thought: I now know the final answer
            Final Answer: your final answer to the question

            Begin!

            Question: {input}


        {agent_scratchpad}
    """
)

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True, max_iterations=5)

def run_agent(user_query: str):
    return agent_executor.invoke({"input": user_query})

if __name__ == "__main__":
    res = run_agent("Summarize the current human rights violations in Iraq and publish them.")
    print(res)