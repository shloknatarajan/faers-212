"""
Download FAERS data from the FDA website.
Must be run from the root directory of the project.
"""

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
from bs4 import BeautifulSoup
from urllib.request import urlopen
from loguru import logger
from typing import List
import argparse
from pathlib import Path
from loguru import logger
from src.utils.supported_quarters import get_available_online_quarters, get_available_raw_quarters, get_available_processed_quarters
from src.download_data.parse_quarters import ParseQuarters


def flatten_directory(directory_path: str, debug: bool = False):
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
            if debug:
                logger.debug(f"Moved: {source_path} -> {dest_path}")

    # Remove all subdirectories (bottom-up to ensure they're empty)
    for root, dirs, files in os.walk(directory_path, topdown=False):
        if root != directory_path:  # Don't remove the top-level directory
            try:
                os.rmdir(root)
                if debug:
                    logger.debug(f"Removed directory: {root}")
            except OSError as e:
                logger.error(f"Error removing directory {root}: {e}")


class FAERSDownloader:
    """
    Class for downloading FAERS data from the FDA website.
    Used by methods below to download the raw data
    """
    def __init__(self, save_dir: str = "data", debug: bool = False):
        self.debug = debug
        self.save_dir = Path(save_dir).joinpath("raw_faers")
        self.available_online_quarters = get_available_online_quarters()
    
    def help(self):
        """
        List all available online quarters and print example message
        """
        print(f"Available online quarters: {self.available_online_quarters.keys()}")
        print(f"Available local unprocessed quarters: {get_available_raw_quarters()}")
        print(f"Available local processed quarters: {get_available_processed_quarters()}")
        print(f"Example usage: ")
        print(f"downloader = FAERSDownloader()")
        print(f"downloader.download_quarters(start_year=2023, end_year=2023, start_quarter=1, end_quarter=4) # Download all quarters for 2023")
        print(f"downloader.download_quarter(quarter='2023Q1') # Download a single quarter")

    def validate_quarters(self, parsed_quarters: List[str]):
        """
        Make sure the quarters are available online
        """
        missing_quarters = []
        for quarter in parsed_quarters:
            if quarter not in self.available_online_quarters:
                missing_quarters.append(quarter)
        if missing_quarters:
            logger.error(f"Quarters {missing_quarters} not found on FAERS Download Page (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)")
            raise ValueError(f"Quarters {missing_quarters} not found in {self.available_online_quarters.keys()}")
        if self.debug:
            logger.debug(f"Quarters {parsed_quarters} found in {self.available_online_quarters.keys()}. All quarters validated.")
        return None
    
    def download_quarters(self, start_year: int = None, end_year: int = None, start_quarter: int = 1, end_quarter: int = 4, overwrite: bool = False, remove_pdfs: bool = True):
        """
        Download a range of quarters of FAERS data
        Args:
            start_year: int = None
            end_year: int = None
            start_quarter: int = 1
            end_quarter: int = 4
            overwrite: bool = False
            remove_pdfs: bool = True
        """
        parsed_quarters = ParseQuarters(start_year, end_year, start_quarter, end_quarter, debug=self.debug).get_quarters()
        self.validate_quarters(parsed_quarters)

        for quarter in tqdm(parsed_quarters):
            logger.info(f"Downloading {quarter}")
            self.download_quarter(quarter, overwrite=overwrite, remove_pdfs=remove_pdfs)

    def download_quarter(self, quarter: str, overwrite: bool = False, remove_pdfs: bool = True):
        """
        Download a single quarter of FAERS data
        Args:
            quarter: the quarter of the FAERS data to download
            overwrite: whether to overwrite the existing data
            remove_pdfs: whether to remove pdf files (READMEs)
        """
        # Check if the quarter is available online
        if quarter not in self.available_online_quarters:
            logger.error(f"Quarter {quarter} not found in {self.available_online_quarters.keys()}")
            return
        
        # Check if the quarter has already been downloaded
        if os.path.exists(os.path.join(self.save_dir, quarter)):
            if not overwrite:
                logger.warning(f"Skipping {quarter} because it already exists")
                return
            else:
                logger.warning(f"Overwriting {quarter}")

        # Create the quarter folder if it doesn't exist
        os.makedirs(os.path.join(self.save_dir, quarter), exist_ok=True)

        # Download the zip file
        download_folder_path = os.path.join(self.save_dir, quarter)
        url = self.available_online_quarters[quarter]
        r = requests.get(url, timeout=200)

        # Unzip
        logger.info(f"Unzipping files")
        z = ZipFile(BytesIO(r.content))
        z.extractall(download_folder_path)
        r.close()
        logger.info(f"{quarter} downloaded to {download_folder_path}")
        self.clean_files(quarter, remove_pdfs=remove_pdfs)

    def clean_files(self, quarter: str, remove_pdfs: bool = True):
        """
        Move files from ascii up a level and remove non-FAERS data files.
        Args:
            quarter: the quarter of the FAERS data to clean
            remove_pdfs: whether to remove pdf files (READMEs)
        """
        logger.info(f"Cleaning {quarter} files")
        quarter_dir = os.path.join(self.save_dir, quarter)
        flatten_directory(quarter_dir)

        # Remove pdf files
        if remove_pdfs:
            files = os.listdir(quarter_dir)
            for file in files:
                if file.endswith(".pdf"):
                    os.remove(os.path.join(quarter_dir, file))
            logger.info(f"Removed all pdf files")

def download_quarter(quarter: str, save_dir: str = "data", overwrite: bool = False, remove_pdfs: bool = True, debug: bool = False):
    """
    Download a single quarter of FAERS data
    """
    # Convert quarter to start year, start quarter, end year, end quarter
    start_year = int(quarter[:2])
    start_quarter = int(quarter[2])
    end_year = int(quarter[:2])
    end_quarter = int(quarter[2])

    downloader = FAERSDownloader(save_dir=save_dir, debug=debug)
    downloader.download_quarters(start_year, end_year, start_quarter, end_quarter, overwrite, remove_pdfs)


    
    