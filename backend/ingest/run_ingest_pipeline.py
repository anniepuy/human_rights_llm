"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-06-2025
File: run_ingest_pipeline.py
Description: Runs the ingest pipeline for the dos_scraper.py file
"""

import subprocess
import logging
import os
import glob
from pathlib import Path
import shutil

#Path to root of project
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_ROOT = Path(__file__).parent.parent
DATA_DIR = BACKEND_ROOT / "data"
PDF_DIR = DATA_DIR / "pdf" / "dos"
CSV_DIR = DATA_DIR / "csv"

#Kaggle API
os.environ["KAGGLE_CONFIG_DIR"] = os.path.join(os.getcwd(), "kaggle")

#logging set up
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/ingest_pipeline.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def check_pdfs_exist():
    """
    Check if PDF files already exist in the data/pdf/dos directory
    """
    if PDF_DIR.exists():
        pdf_files = list(PDF_DIR.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files in {PDF_DIR}")
        return len(pdf_files) > 0
    print(f"PDF directory {PDF_DIR} does not exist")
    return False

#Kaggle download function
def download_kaggle_dataset():
    """
    Downloads the Kaggle dataset for the Human Rights Reports.
    """
    try:
        import kagglehub
        
        logger.info("Starting Kaggle dataset download...")
        print("Starting Kaggle dataset download...")
        
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        
        # Download to default location (root 'data/')
        path = kagglehub.dataset_download("uconn/human-rights")
        logger.info(f"Kaggle dataset downloaded to {path}")
        print(f"Kaggle dataset downloaded to {path}")

        # Debug: List all files in the downloaded directory
        logger.info("Files in downloaded directory:")
        print("Files in downloaded directory:")
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                logger.info(f"  {file_path}")
                print(f"  {file_path}")

        # Copy CSV directly from Kaggle cache to backend/data/csv
        csv_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.csv'):
                    csv_path = os.path.join(root, file)
                    csv_files.append(csv_path)
                    logger.info(f"Found CSV: {csv_path}")
                    print(f"Found CSV: {csv_path}")
        
        if csv_files:
            # Copy the first CSV file to our expected location
            source_csv = csv_files[0]
            target_csv = CSV_DIR / "human_rights.csv"
            shutil.copy2(source_csv, target_csv)
            logger.info(f"Copied CSV from {source_csv} to {target_csv}")
            print(f"Copied CSV from {source_csv} to {target_csv}")
        else:
            logger.error("No CSV files found in downloaded dataset")
            print("No CSV files found in downloaded dataset")

        # Move files from root data/ to backend/data/ (for any other files)
        root_data_dir = PROJECT_ROOT / "data"

        logger.info(f"Looking for root data directory: {root_data_dir}")
        print(f"Looking for root data directory: {root_data_dir}")

        if root_data_dir.exists():
            logger.info(f"Root data directory exists, moving files to {DATA_DIR}")
            print(f"Root data directory exists, moving files to {DATA_DIR}")
            for item in root_data_dir.iterdir():
                # Move everything to backend/data/ (which is DATA_DIR)
                dest = DATA_DIR / item.name
                logger.info(f"Moving {item} to {dest}")
                print(f"Moving {item} to {dest}")
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.move(str(item), str(dest))
                else:
                    shutil.move(str(item), str(dest))
            # Try to remove the now-empty root data dir
            try:
                root_data_dir.rmdir()
                logger.info("Deleted root data directory after moving files.")
                print("Deleted root data directory after moving files.")
            except Exception as e:
                logger.warning(f"Could not delete root data directory: {e}")
                print(f"Could not delete root data directory: {e}")
        else:
            logger.warning(f"Root data directory {root_data_dir} does not exist")
            print(f"Root data directory {root_data_dir} does not exist")
            
    except Exception as e:
        logger.error(f"Failed to download Kaggle dataset: {e}")
        print(f"Failed to download Kaggle dataset: {e}")
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        PDF_DIR.mkdir(parents=True, exist_ok=True)

#Main function
if __name__ == "__main__":
    print("="*50)
    print("PIPELINE SCRIPT STARTING")
    print("="*50)
    import sys
    sys.stdout.flush()
    
    logger.info("Starting ingest pipeline...")
    print("Starting ingest pipeline...")
    sys.stdout.flush()
    
    # Download Kaggle dataset
    print("About to call download_kaggle_dataset()...")
    sys.stdout.flush()
    try:
        download_kaggle_dataset()
        print("download_kaggle_dataset() completed")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error in download_kaggle_dataset(): {e}")
        logger.error(f"Error in download_kaggle_dataset(): {e}")
        sys.stdout.flush()

    # Check if PDFs already exist
    if check_pdfs_exist():
        logger.info("PDFs already exist, skipping DOS scraper...")
        print("PDFs already exist, skipping DOS scraper...")
        sys.stdout.flush()
    else:
        #Run the dos_scraper.py file
        try: 
            subprocess.run(["python", "ingest/dos_scraper.py"], check=True)
            logger.info("dos_scraper.py completed successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"dos_scraper.py failed: {e}")

    #Run the ingest_documents.py file
    try:
        subprocess.run(["python", "ingest/ingest_documents.py"], check=True)
        logger.info("ingest_documents.py completed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"ingest_documents.py failed: {e}")

    logger.info("Ingest pipeline completed successfully!")  