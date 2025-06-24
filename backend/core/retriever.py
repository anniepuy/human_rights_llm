"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: retriever.py
Description: This loads the ChromaDB embeddings and retrieves the top-k similar with metadata based on user query.
"""

import os
from pathlib import Path
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Path definitions - use backend structure
BACKEND_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DB_PATH = BACKEND_ROOT / "embeddings" / "chroma_db"

# Load the embeddings and vector store
embeddings_fn = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma(persist_directory=str(CHROMA_DB_PATH), embedding_function=embeddings_fn)

#Retriever function
def retrieve_documents(query: str, k: int = 5):
    """
    Retrieve top-k similar documents from ChromaDB given a query string.
    Returns a list of Documents with metadata
    """
    results = db.similarity_search(query, k=k)
   
    return results

#test block
if __name__ == "__main__":
    query = "What is the human rights situation in Syria?"
    results = retrieve_documents(query, k=3, csore_threshold=0.5)
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Type: {doc.metadata.get('document_type', 'Unknown')}")
        print(f"Title: {doc.metadata.get('title', 'Unknown')}")
        print(f"Content preview: {doc.page_content[:200]}...")
        print("-" * 40)
      