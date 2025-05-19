# coding: utf-8
# author: Jing Li
# date: 2019/04/01

import os
import re
import lxml
import time
import shutil
import warnings
import requests
from tqdm import tqdm
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
from loguru import logger

# this script will find target in this list pages.
target_page = ["https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html"]

# local directory to save files.
data_dir = "data/raw_faers"

# ignore warnings
warnings.filterwarnings('ignore')
def flatten_directory(directory_path):
    """
    Flattens all subdirectories in the given directory by moving all files to the top level
    and removing all folders.
    
    Args:
        directory_path (str): Path to the directory to flatten
    """
    # Get the absolute path
    directory_path = os.path.abspath(directory_path)
    
    # Collect all files (including those in subdirectories)
    all_files = []
    for root, dirs, files in os.walk(directory_path):
        # Skip the top-level directory
        if root != directory_path:
            for file in files:
                source_path = os.path.join(root, file)
                all_files.append(source_path)
    
    # Move all files to the top level
    for source_path in all_files:
        # Get the filename only
        filename = os.path.basename(source_path)
        
        # Create destination path at top level
        dest_path = os.path.join(directory_path, filename)
        
        # Handle filename conflicts by adding a suffix
        if os.path.exists(dest_path) and source_path != dest_path:
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest_path):
                new_filename = f"{base}_{counter}{ext}"
                dest_path = os.path.join(directory_path, new_filename)
                counter += 1
        
        # Move the file
        if source_path != dest_path:  # Don't try to move a file to itself
            shutil.move(source_path, dest_path)
            print(f"Moved: {source_path} -> {dest_path}")
    
    # Remove all subdirectories (bottom-up to ensure they're empty)
    for root, dirs, files in os.walk(directory_path, topdown=False):
        if root != directory_path:  # Don't remove the top-level directory
            try:
                os.rmdir(root)
                print(f"Removed directory: {root}")
            except OSError as e:
                print(f"Error removing directory {root}: {e}")
                
class FAERSDownloader:
    def __init__(self, data_dir: str = "data/raw_faers"):
        self.data_dir = data_dir
        self.file_urls = self.get_file_urls()

    def get_file_urls(self) -> dict[str, str]:
        """
        find all web urls in the FAERS download page
        :return: dict files = {"YYYYQN":"url"}  
        """
        logger.info("Fetching web urls")
        files = {}
        for page_url in target_page:
            try:
                request = urlopen(page_url)
                page_bs = BeautifulSoup(request, "lxml")
                request.close()
            except:
                request = urlopen(page_url)
                page_bs = BeautifulSoup(request)
            for url in page_bs.find_all("a"):
                a_string = str(url)
                if "ASCII" in a_string.upper():
                    t_url = url.get('href')
                    # Extract year and quarter from the URL
                    match = re.search(r'ascii_(\d{4})([qQ]\d)', t_url)
                    if match:
                        year = match.group(1)
                        quarter = match.group(2).upper()  # Convert to uppercase
                        key = f"{year}{quarter}"
                        files[key] = t_url

            logger.info("Got all quarterly zip file urls")
            return files
        
    def download_quarter(self, quarter: str, overwrite: bool = False):
        """
        Download a single quarter of FAERS data
        """
        # Check if the quarter folder exists
        logger.info(f"Downloading {quarter} from {self.file_urls[quarter]}")
        if os.path.exists(os.path.join(self.data_dir, quarter)):
            if not overwrite:
                logger.info(f"Skipping {quarter} because it already exists")
                return
            else:
                logger.info(f"Overwriting {quarter}")
        
        # Create the quarter folder if it doesn't exist
        os.makedirs(os.path.join(self.data_dir, quarter), exist_ok=True)

        # Download the zip file
        download_folder_path = os.path.join(self.data_dir, quarter)
        if quarter not in self.file_urls:
            logger.error(f"Quarter {quarter} not found in {self.file_urls.keys()}")
            return
        url = self.file_urls[quarter]
        r = requests.get(url, timeout=200)

        # Unzip
        logger.info(f"Unzipping files")
        z = ZipFile(BytesIO(r.content))
        z.extractall(download_folder_path)
        r.close()
        # self.remove_meta_files(self.data_dir)
        logger.info(f"{quarter} downloaded to {download_folder_path}")

    def download_files(self, faers_files):
        """
        download faers data files.
        :param faers_files: dict faers_files = {"name":"url"}
        :param data_dir: data/raw_faers
        :return: none
        """
        for file_name in tqdm(faers_files):
            try:
                logger.info(f"Downloading {file_name}")
                r = requests.get(faers_files[file_name], timeout=200)
                z = ZipFile(BytesIO(r.content))
                z.extractall(self.data_dir)
                r.close()

                # delete and copy files to data/raw_faers.
                self.remove_meta_files(self.data_dir)
                logger.info(f"Downloaded {file_name}")
            except Exception as e:
                logger.error(f"Download failed! Error: {str(e)}")
            logger.info("Sleeping 30 seconds before starting download a new file.")
            time.sleep(30)


    def clean_files(self, quarter: str, remove_pdfs: bool = True):
        """
        Move files from ascii up a level and remove non-FAERS data files.
        Args:
            quarter: the quarter of the FAERS data to clean
            remove_pdfs: whether to remove pdf files (READMEs)
        """
        logger.info(f"Cleaning {quarter}")
        quarter_dir = os.path.join(self.data_dir, quarter)
        flatten_directory(quarter_dir)

        # Remove pdf files
        if remove_pdfs:
            files = os.listdir(quarter_dir)
            for file in files:
                if file.endswith('.pdf'):
                    os.remove(os.path.join(quarter_dir, file))
            logger.debug(f"Removed all pdf files")
        logger.info(f"Cleaning {quarter} complete")

def main():
    # get faers data file's url and download them.
    downloader = FAERSDownloader('data/raw_faers')
    downloader.download_quarter('2023Q1', overwrite=False)
    downloader.clean_files('2023Q1', remove_pdfs=True)
    

if __name__ == '__main__':
    main()
