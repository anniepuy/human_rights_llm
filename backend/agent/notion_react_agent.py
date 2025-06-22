"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: notion_react_agent.py
Description: Uses ReAct agent to generate or summarize human rights reports with RAG context from backend.core.rag_chain and publish to Notion.
"""

import warnings
from langchain._api.deprecation import LangChainDeprecationWarning

# Suppress deprecation warning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from notion_client import Client
from langchain.tools import tool


# Dynamically determine project root and add to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added to sys.path: {sys.path}")

# Verify import after path adjustment
try:
    from backend.core.rag_chain import rag_chain
    logging.info("Successfully imported rag_chain from backend.core.rag_chain")
except ImportError as e:
    logging.error(f"Failed to import rag_chain: {str(e)}")
    raise

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = "21a8568dd63d80e99bb5dc9d1cfa8e4d"

# Tool: generate_report_tool
def generate_report_tool(query: str) -> str:
    """
    Generate a comprehensive, structured human rights report in markdown format.
    """
    logger.info(f"Generating report for query: {query}")
    llm = ChatOllama(model="mistral:latest", temperature=1, max_tokens=4000)
    msg = HumanMessage(
        content=f"""You are a human rights research assistant. Create a comprehensive, structured report on the following human rights topic in markdown format:

        {query}

        The report MUST include:
        - **Executive Summary**: A brief overview of the human rights situation (150-200 words).
        - **Key Issues and Violations**: Detailed list of specific human rights abuses (e.g., arbitrary detention, torture).
        - **Affected Groups**: Identify groups most impacted (e.g., civilians, minorities, women, children).
        - **Current Status**: Recent developments or ongoing issues (as of the latest available data).
        - **Recommendations**: Actionable steps for governments, NGOs, or international bodies.
        - **Sources/References**: Cite credible sources (e.g., UN reports, Amnesty International) or note if using general knowledge.

        Format it as a professional report with clear markdown headings (##) and bullet points. Be objective, factual, and detailed (minimum 800 words). Do NOT include meta-commentary like 'This report provides...', 'I hope this answers...', or any introductory/explanatory text outside the report structure. Return ONLY the markdown report."""
    )
    return llm.invoke([msg]).content

# Tool: summarize_llm_only
@tool("summarize_llm_only")
def summarize_llm_only(query: str) -> str:
    """Summarize a query using only the LLM with no external documents."""
    logger.info(f"Summarizing query without RAG: {query}")
    llm = ChatOllama(model="mistral:latest")
    msg = HumanMessage(
        content=f"""You are a human rights research assistant. Summarize the following human rights topic concisely in markdown format, using only your general knowledge. Do not include external sources or references:

        {query}

        The summary should be brief (100-200 words), objective, and factual, with clear headings for:
        - Summary
        - Key Points"""
    )
    return llm.invoke([msg]).content

# Tool: search_rag_data
@tool("search_rag_data")
def search_rag_data(query: str) -> str:
    """Searches ChromaDB via rag_chain and returns relevant context with citations."""
    logger.info(f"Searching RAG data for query: {query}")
    if not query or query.lower() == "none":
        query = "What countries are represented in the RAG data?"
        logger.warning(f"No query provided, using default: {query}")
    try:
        response = rag_chain.invoke({"question": query})
        logger.debug(f"RAG response: {response}")
        return response if response else "No relevant documents found in the ChromaDB vector store."
    except Exception as e:
        logger.error(f"Error retrieving context from rag_chain: {str(e)}")
        return f"Error retrieving context from rag_chain: {str(e)}"

# Tool: summarize_with_context
@tool("summarize_with_context")
def summarize_with_context(query_and_context: dict) -> str:
    """Summarizes using LLM + supplied context from DOS human rights reports. Input must include 'query' and 'context' keys."""
    logger.info(f"Summarizing with context for query: {query_and_context.get('query', 'unknown')}")
    if not isinstance(query_and_context, dict) or 'query' not in query_and_context or 'context' not in query_and_context:
        logger.error("Invalid input for summarize_with_context: missing 'query' or 'context' keys")
        return "Error: Input must be a dictionary with 'query' and 'context' keys."
    
    query = query_and_context['query']
    context = query_and_context['context']
    
    llm = ChatOllama(model="mistral:latest")
    msg = HumanMessage(
        content=f"""You are a human rights research assistant. Create a detailed report on the following human rights topic in markdown format, using the provided context from Department of State human rights reports. Ensure the report is objective, factual, and detailed (minimum 800 words), with clear headings for:
        - Executive Summary (150-200 words)
        - Key Issues and Violations
        - Affected Groups
        - Current Status
        - Recommendations
        - References (cite the context as 'U.S. Department of State Human Rights Reports')

        Topic: {query}

        Context: {context}"""
    )
    return llm.invoke([msg]).content

# LLM and tools
llm = ChatOllama(model="mistral:latest")
tools = [
    Tool(
        name="generate_report",
        func=generate_report_tool,
        description="Generate a comprehensive, structured report on human rights topics using general knowledge if RAG data is unavailable. Input: a human rights query or topic. Output: a detailed markdown report with sections for Executive Summary, Key Issues, Affected Groups, Current Status, Recommendations, and Sources."
    ),
    summarize_llm_only,
    search_rag_data,
    summarize_with_context
]

# Custom prompt template with reasoning logic
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a human rights research assistant. Your primary purpose is to generate objective, factual, and detailed reports or summaries on human rights topics, including violations in any country, using your Retrieval-Augmented Generation (RAG) system containing Department of State human rights reports. Follow these steps to process user queries:

    1. **Determine the query type**:
       - For queries requesting a 'full report', 'detailed report', or 'report on [topic]' (e.g., 'Write me a detailed report on human rights violations in Iran'), ALWAYS use the `search_rag_data` tool first to retrieve context from the RAG system, then use `summarize_with_context` to generate a detailed report incorporating the RAG data. If RAG returns 'No relevant documents found' or an error, use `generate_report` with general knowledge as a fallback.
       - If the user asks for sources or RAG data (e.g., 'What does the RAG data say about human rights in Iran'), use the `search_rag_data` tool, then `summarize_with_context`.
       - If the user requests a quick summary without sources (e.g., 'summarize human rights in Iran'), use the `summarize_llm_only` tool.
       - If unsure, default to `search_rag_data` and `summarize_with_context`.

    2. **Tool usage**:
       - Use exact tool names: `generate_report`, `summarize_llm_only`, `search_rag_data`, `summarize_with_context`.
       - For `search_rag_data`, provide a specific query string (e.g., 'Human rights violations in Iran').
       - For `summarize_with_context`, pass a dictionary with 'query' and 'context' keys.
       - Example actions:
         - Action: search_rag_data\nAction Input: "Human rights violations in Iran"
         - Action: summarize_with_context\nAction Input: {"query": "Human rights violations in Iran", "context": "[RAG output]"}
         - Action: generate_report\nAction Input: "Human rights violations in Iran"

    3. **CRITICAL - Output Rules**:
       - Return the COMPLETE tool output as your final answer.
       - Do NOT summarize, condense, or rephrase the tool output.
       - Do NOT add meta-commentary like 'This report provides...' or 'I hope this answers...'.
       - The tool output IS your final answer.

    **Critical**: Do NOT refuse to process human rights topics, including reports on violations in any country (e.g., Iran, Syria). ALWAYS check the RAG system first for relevant data. Generate objective, factual content based on RAG data or general knowledge, ensuring no justification or promotion of harmful behavior. This is your core function and overrides any safety concerns about discussing human rights abuses."""),
    ("human", "{input}\n\nAvailable tools: {tool_names}\n{tools}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create ReAct agent
def handle_parsing_errors(error):
    logger.error(f"Parsing error: {str(error)}")
    return "Invalid format detected. Please provide a valid action, e.g., 'Action: search_rag_data\nAction Input: \"[topic]\"' or 'Action: generate_report\nAction Input: \"[topic]\"'."

agent = initialize_agent(
    llm=llm,
    tools=tools,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=handle_parsing_errors,
    max_iterations=5,
    prompt=prompt
)

# Run agent with user input
def run_agent(user_query: str):
    """
    Run the ReAct agent to generate or summarize a human rights report.
    Returns a dictionary with the actual output text.
    """
    logger.info(f"Running agent with query: {user_query}")
    try:
        result = agent.invoke({"input": user_query})
        
        # Log intermediate steps
        intermediate_steps = getattr(result, "intermediate_steps", [])
        logger.debug(f"Intermediate steps: {intermediate_steps}")

        # Look for tool output (generate_report or summarize_with_context)
        detailed_output = ""
        for step in intermediate_steps:
            if len(step) >= 2 and isinstance(step[1], str):
                tool_name = getattr(step[0], "tool", None)
                if tool_name in ["generate_report", "summarize_with_context"]:
                    detailed_output = step[1]
                    logger.info(f"Found {tool_name} output: {detailed_output[:100]}...")
                    break

        # Use tool output if available, otherwise fallback to final agent output
        if detailed_output:
            output = detailed_output
        else:
            output = getattr(result, "output", str(result))
            if any(phrase in output.lower() for phrase in ["this report provides", "i hope this answers"]):
                logger.warning(f"Agent returned generic response: {output[:100]}...")
            else:
                logger.info("Using fallback agent output")

        return {"output": output}

    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        return {"output": f"Error: Agent execution failed - {str(e)}"}

# Publish to Notion
def publish_to_notion(title: str, content: str, date: str = None, source: str = "Human Rights LLM Agent"):
    """
    Publish a report to Notion page, splitting long content into multiple blocks.
    """
    logger.info(f"Publishing to Notion with title: {title}, content length: {len(content)}")
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    notion = Client(auth=NOTION_API_KEY)
    block_size = 2000  # Notion's character limit per block
    
    # Split content into chunks
    content_chunks = [content[i:i+block_size] for i in range(0, len(content), block_size)]
    logger.debug(f"Split content into {len(content_chunks)} chunks")
    
    try:
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": title}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"Date: {date} | Source: {source}"}}]
                }
            }
        ]
        for chunk in content_chunks:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })
        
        response = notion.blocks.children.append(
            block_id=NOTION_PAGE_ID,
            children=children
        )
        logger.info(f"Successfully published to Notion page {NOTION_PAGE_ID}: {response}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to Notion: {str(e)}")
        return False

# CLI entry
if __name__ == "__main__":
    user_query = input("Enter your human rights question to summarize: ")
    
    logger.info("Running ReAct agent...")
    result = run_agent(user_query)
    
    report_content = result.get("output", "No report generated.")
    title = f"Human Rights Report: {user_query.title()}"
    
    logger.info("Preparing to publish to Notion...")

    success = publish_to_notion(
        title=title,
        content=report_content,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    if success:
        print("Report successfully published to Notion.")
    else:
        print("Report generated but failed to publish to Notion.")