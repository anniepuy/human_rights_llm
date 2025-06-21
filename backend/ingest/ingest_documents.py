"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-05-2025
File: ingest_documents.py
Description: This file is used to ingest documents & scraped websites into the database.
"""

import os
import sqlite3
import pandas as pd
import fitz
from urllib.parse import urlparse
import logging
from datetime import datetime
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from pathlib import Path
import shutil

# Path definitions - use backend structure
BACKEND_ROOT = Path(__file__).parent.parent
DATA_DIR = BACKEND_ROOT / "data"
CSV_DIR = DATA_DIR / "csv"
PDF_DIR = DATA_DIR / "pdf" / "dos"
DB_PATH = BACKEND_ROOT / "db" / "documents.db"
CHROMA_DB_PATH = BACKEND_ROOT / "embeddings" / "chroma_db"

#logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

#Create folders 
os.makedirs(DB_PATH.parent, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

#SqlLite Connection
def init_sqlite():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            title TEXT,
            source TEXT,
            document_type TEXT,
            content TEXT,
            date_added TEXT,
            tags TEXT
        )
    """)
    conn.commit()
    return conn

#Extract source from URL
def get_source_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or "unknown"
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname.split(".")[0]

#Helder function to load and clean documents
def load_pdfs(pdf_dir):
    """
    Loads and cleans PDF documents from a directory.
    """
    docs = []
    for fname in os.listdir(pdf_dir):
        if fname.endswith(".pdf"):
            path = os.path.join(pdf_dir, fname)
            text = ""
            with fitz.open(path) as doc:
                for page in doc:
                    text += page.get_text()
            source = get_source_from_url("https://www.state.gov/reports/2023-country-reports-on-human-rights-practices/")
            docs.append(Document(page_content=text, metadata={
                "title": fname,
                "source": source,
                "document_type": "pdf",
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "tags": "human_rights,state_department"
            }))
    return docs

#Load CSV Data from Kaggle
def load_csv(csv_path):
    """
    Loads and cleans CSV data from a file.
    """
    df = pd.read_csv(csv_path)
    docs = []
    for index, row in df.iterrows():
        content = " ".join([str(v) for v in row.values])
        source = get_source_from_url("https://www.kaggle.com/datasets/uconn/human-rights")
        docs.append(Document(page_content=content, metadata={
            "title": f"Row {index}",
            "source": source,
            "document_type": "csv",
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "tags": "human_rights,kaggle"
        }))
    return docs

#Save to SQLite
def save_to_sqlite(docs, conn):
    c = conn.cursor()
    for doc in docs:
        c.execute("""
                  INSERT INTO documents (title, source, document_type, content, date_added, tags)
                  VALUES (?, ?, ?, ?, ?, ?)
                  """, (
                      doc.metadata["title"], 
                      doc.metadata["source"], 
                      doc.metadata["document_type"], 
                      doc.page_content, 
                      doc.metadata["date_added"], 
                      doc.metadata["tags"]))
    conn.commit()

#Main ingest routine
if __name__ == "__main__":
    conn = init_sqlite()

    print("Loading PDFs...")
    pdf_docs = load_pdfs(PDF_DIR)
    print(f"Loaded {len(pdf_docs)} PDFs")

    print("Loading CSV...")
    csv_docs = load_csv(CSV_DIR / "human_rights.csv")
    print(f"Loaded {len(csv_docs)} CSV rows")

    all_docs = pdf_docs + csv_docs
    save_to_sqlite(all_docs, conn)

    print("Splitting and embedding documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(all_docs)

    embedding_fn = OllamaEmbeddings(model="nomic-embed-text")
    Chroma.from_documents(documents=chunks, embedding=embedding_fn, persist_directory=str(CHROMA_DB_PATH))

    logger.info(f"Loaded {len(pdf_docs)} PDFs")
    logger.info(f"Loaded {len(csv_docs)} CSV rows")
    
    logger.info(f"Ingest complete with {len(chunks)} chunks!")

    print("Downloaded files:")
    for item in DATA_DIR.iterdir():
        # If moving the 'pdf' directory, move it to backend/data/pdf
        if item.name == "pdf":
            dest = DATA_DIR / "pdf"
        elif item.name == "csv":
            dest = DATA_DIR / "csv"
        else:
            dest = DATA_DIR / item.name
        logger.info(f"Moving {item} to {dest}")
        print(f"Moving {item} to {dest}")
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(item), str(dest))
        else:
            shutil.move(str(item), str(dest))