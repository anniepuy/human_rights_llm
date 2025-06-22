"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: rag_chain.py
Description: Retrieves top-k similar documents from ChromaDB and injects them into a prompt for the LLM to answer.
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import time
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from .retriever import retrieve_documents
from langchain_core.output_parsers import StrOutputParser

## Instantiate the LLM
llm = ChatOllama(model="mistral:latest")

#Prompt template with citation template
RAG_PROMPT = ChatPromptTemplate.from_template("""
You are an expert in human rights, international law, and United States homeland security policies. Using the provided context, answer the user's question.
Be concise and cite your sources using inline citations from [source].
                                              
Question: {question}
                                              
Context: {context}
                                              
Answer:
""")

#Document formatter to merge sources
format_docs = lambda docs: "\n\n".join(
    f"Source [{doc.metadata.get('source', 'Unknown')}]:\n{doc.page_content[:800]}..."
    for doc in docs
    )


#main RAG chain
rag_chain = (
    RunnableMap({
        "context": lambda x: format_docs(retrieve_documents(x["question"])),
        "question": lambda x: x["question"]})
        | RAG_PROMPT
        | llm
        | StrOutputParser()
)

def run_rag_chain(query: str):
    """
    Run the RAG chain with a user question.
    """
    start_time = time.time()
    response = rag_chain.invoke({"question": query})
    latency = round(time.time() - start_time, 2)
    print(f"Time taken: (Latency: {latency}s):\n\n{response}")
    return response

# Example usage
if __name__ == "__main__":
    q = "What human rights issues were reported in Syria in 2023?"
    run_rag_chain(q)