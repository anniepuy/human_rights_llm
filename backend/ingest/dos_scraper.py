"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-05-2025
File: dos_scraper.py
Description: This file is used to scrape the Dept of State's Human Rights Reports on the top 20 aslyum seeking countries.
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
BASE_URL = "https://www.state.gov"
INDEX_URL = f"{BASE_URL}/reports/2023-country-reports-on-human-rights-practices/"
PDF_DIR = "data/pdf/dos"

# Add headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

#Countries whose reports we want to scrape
TARGET_COUNTRIES = [
    "afghanistan", "venezuela", "el-salvador", "honduras", "iran", "iraq",
    "guatemala", "syria", "somalia", "eritrea", "yemen", "cuba", "nicaragua",
    "democratic-republic-of-the-congo", "sudan", "south-sudan", "burundi",
    "pakistan", "bangladesh", "ethiopia"
]

#Ouput directory
os.makedirs(PDF_DIR, exist_ok=True)

def get_country_links():
    try:
        response = requests.get(INDEX_URL, headers=HEADERS)
        response.raise_for_status()
        print(f"Response status: {response.status_code}")
        print(f"Response content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        country_links = []
        
        print(f"Searching for country links on: {INDEX_URL}")
        print(f"Looking for countries: {TARGET_COUNTRIES}")
        
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            print(f"Found link: {href}")
            
            # Check if this is a country report link for our target countries
            if "2023-country-reports-on-human-rights-practices" in href and href.endswith("/"):
                for country in TARGET_COUNTRIES:
                    if f"/{country}/" in href:
                        # Convert to full URL if it's relative
                        full_url = urljoin(BASE_URL, href) if href.startswith("/") else href
                        country_links.append(full_url)
                        print(f"✓ Matched country: {country} -> {full_url}")
                        break
        
        print(f"Total country links found: {len(country_links)}")
        return country_links
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the website: {e}")
        return []

def download_pdfs_from_country_page(country_url):
    try:
        response = requests.get(country_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".pdf"):
                pdf_url = urljoin(BASE_URL, href)
                filename = Path(pdf_url).name
                local_path = os.path.join(PDF_DIR, filename)
                if not os.path.exists(local_path):
                    print(f"Downloading {filename}...")
                    pdf_response = requests.get(pdf_url, headers=HEADERS)
                    pdf_response.raise_for_status()
                    with open(local_path, "wb") as f:
                        f.write(pdf_response.content)
                else:
                    print(f"{filename} already exists, skipping.")
    except requests.exceptions.RequestException as e:
        print(f"Error accessing {country_url}: {e}")

def main():
    country_links = get_country_links()
    print(f"Found {len(country_links)} target country links.")
    for country_url in country_links:
        download_pdfs_from_country_page(country_url)

if __name__ == "__main__":
    main()