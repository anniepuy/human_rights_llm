"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-05-2025
File: dos_scraper.py
Description: This file is used to scrape the Dept of State's Human Rights Reports.
"""
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import logging

#Logging set up
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/dos_scraper.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

#Constants
BASE_URL = "https://www.state.gov/"
INDEX_URL = "https://www.state.gov/reports/2023-country-reports-on-human-rights-practices/"
PDF_DIR = "data/pdf/dos"

#Ouput directory
os.makedirs(PDF_DIR, exist_ok=True)

#Scrap the page and get the PDFS
def scrap_dos_reports(url=INDEX_URL):
    """
    Scrape the DOS reports page and get the PDFS
    """
    logger.info(f"Scraping DOS reports from {url}")
    try:
        response = requests.get(INDEX_URL)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error scraping DOS reports: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "2023-country-reports-on-human-rights-practices" in href and href.endswith(".pdf"):
            full_url = urljoin(INDEX_URL, href)
            pdf_links.append(full_url)
    
    logger.info(f"Found {len(pdf_links)} PDF links")


    for link in pdf_links:
        filename = Path(link).name
        local_path = os.path.join(PDF_DIR, filename)
        if not os.path.exists(local_path):
            try:
                logger.info(f"Downloading {filename}...")
                pdf_response = requests.get(link)
                pdf_response.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(pdf_response.content)
                logger.info(f"Saved to {local_path}")
            except Exception as e:
                logger.error(f"Failed to download {filename}: {e}")
        else:
            logger.info(f"Already downloaded {filename}, skipping download.")

if __name__ == "__main__":
    scrap_dos_reports()