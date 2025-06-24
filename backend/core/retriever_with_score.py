"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-24-2025
File: retriever_with_score.py
Description: Retrieves top-k similar documents from ChromaDB with similarity scores. Chroma is using distance metric (e.g., Euclidean distance), where lower scores indicate more similar documents.
"""
import os
from pathlib import Path
import logging
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(
    filename="logs/retriever.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Path definitions - use backend structure
BACKEND_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DB_PATH = BACKEND_ROOT / "embeddings" / "chroma_db"

# Load the embeddings and vector store
embeddings_fn = OllamaEmbeddings(model="nomic-embed-text")
try:
    db = Chroma(persist_directory=str(CHROMA_DB_PATH), embedding_function=embeddings_fn)
    logger.info(f"Loaded ChromaDB from {CHROMA_DB_PATH}")
except Exception as e:
    logger.error(f"Failed to load ChromaDB: {str(e)}")
    raise

# Retriever function
def retrieve_documents(query: str, k: int = 5, score_threshold: float = 0.0) -> list[dict]:
    """
    Retrieve top-k similar documents from ChromaDB given a query string.
    Returns a list of dictionaries with Document objects and their similarity scores.
    Filters out documents with scores below score_threshold (0.0 means no filtering).
    """
    if not query.strip():
        logger.warning("Empty query provided")
        return []

    try:
        # Use similarity_search_with_score to get documents and scores
        results = db.similarity_search_with_score(query, k=k)
        logger.info(f"Retrieved {len(results)} documents for query: {query}")

        # Process results into list of dicts with document and score
        formatted_results = []
        for doc, score in results:
            # Assuming cosine similarity (0 to 1, higher is better)
            # If using distance metric, adjust logic (e.g., lower is better)
            if score >= score_threshold:
                formatted_results.append({
                    "document": doc,
                    "score": score
                })
            else:
                logger.debug(f"Filtered out document with score {score} below threshold {score_threshold}")

        logger.info(f"Returning {len(formatted_results)} documents after filtering")
        return formatted_results

    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        return []

# Test block
if __name__ == "__main__":
    query = "What is the human rights situation in Syria?"
    results = retrieve_documents(query, k=3, score_threshold=0.5)
    for i, result in enumerate(results, 1):
        doc = result["document"]
        score = result["score"]
        print(f"\nResult {i}:")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Type: {doc.metadata.get('document_type', 'Unknown')}")
        print(f"Title: {doc.metadata.get('title', 'Unknown')}")
        print(f"Similarity Score: {score:.4f}")
        print(f"Content preview: {doc.page_content[:200]}...")
        print("-" * 40)