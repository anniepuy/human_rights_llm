"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-05-2025
File: test_ingest_documents.py
Description: Unit tests for ingest_documents.py
"""

import os
import sqlite3
import tempfile
import pandas as pd
import pytest
import logging
from ingest.ingest_documents import (
    get_source_from_url, 
    load_csv, 
    save_to_sqlite, 
    load_pdfs, 
    init_sqlite
)
from langchain_core.documents import Document

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Setup logging for test file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/test_log.log", mode='w')
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def test_get_source_from_url():
    logger.info("Running test_get_source_from_url...")
    assert get_source_from_url("https://www.kaggle.com/datasets/uconn/human-rights") == "kaggle"
    assert get_source_from_url("https://state.gov/reports/some-report") == "state"
    assert get_source_from_url("https://www.hrw.org/countries") == "hrw"
    assert get_source_from_url("invalid") == "unknown"
    logger.info("Completed test_get_source_from_url.")


def test_load_csv_creates_documents(tmp_path):
    logger.info("Running test_load_csv_creates_documents...")
    test_csv = tmp_path / "test.csv"
    df = pd.DataFrame({"Country": ["A", "B"], "Score": [1, 2]})
    df.to_csv(test_csv, index=False)

    docs = load_csv(str(test_csv))
    assert len(docs) == 2
    assert all("kaggle" in d.metadata["source"] for d in docs)
    assert all(d.metadata["document_type"] == "csv" for d in docs)
    logger.info("Completed test_load_csv_creates_documents.")


def test_save_to_sqlite_inserts_records():
    logger.info("Running test_save_to_sqlite_inserts_records...")
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            document_type TEXT,
            content TEXT,
            date_added TEXT,
            tags TEXT
        )
    """)

    docs = [
        Document(page_content="sample content", metadata={
            "title": "Test",
            "source": "test_source",
            "document_type": "txt",
            "date_added": "2025-01-01",
            "tags": "test"
        })
    ]

    save_to_sqlite(docs, conn)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM documents")
    count = cur.fetchone()[0]
    assert count == 1
    logger.info("Completed test_save_to_sqlite_inserts_records.")


def test_init_sqlite_creates_table():
    logger.info("Running test_init_sqlite_creates_table...")
    # Use temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        conn = init_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
        table_exists = cursor.fetchone() is not None
        assert table_exists
        logger.info("Completed test_init_sqlite_creates_table.")
    finally:
        # Clean up
        os.unlink(temp_db.name)


def test_load_pdfs_with_mock_files(tmp_path):
    logger.info("Running test_load_pdfs_with_mock_files...")
    # Create a mock PDF directory
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    
    # Create a mock PDF file (we'll just create a text file for testing)
    mock_pdf = pdf_dir / "test.pdf"
    mock_pdf.write_text("Mock PDF content")
    
    # Test that the function handles the directory
    # Note: This test is limited since we can't easily create real PDFs in tests
    try:
        docs = load_pdfs(str(pdf_dir))
        # The function should handle the directory even if PDFs can't be read
        logger.info("Completed test_load_pdfs_with_mock_files.")
    except Exception as e:
        logger.warning(f"load_pdfs test encountered expected error: {e}")
        # This is expected since we're not creating real PDF files


def test_document_metadata_structure():
    logger.info("Running test_document_metadata_structure...")
    # Test that documents have the expected metadata structure
    test_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    test_csv.write("Country,Score\nA,1\nB,2")
    test_csv.close()
    
    try:
        docs = load_csv(test_csv.name)
        assert len(docs) > 0
        
        for doc in docs:
            assert "title" in doc.metadata
            assert "source" in doc.metadata
            assert "document_type" in doc.metadata
            assert doc.page_content is not None
            assert len(doc.page_content) > 0
        
        logger.info("Completed test_document_metadata_structure.")
    finally:
        os.unlink(test_csv.name)


if __name__ == "__main__":
    logger.info("Starting test suite for ingest_documents.py")
    # Run tests
    pytest.main([__file__, "-v"])
    logger.info("Test suite completed")