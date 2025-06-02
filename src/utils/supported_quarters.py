import os
from pathlib import Path
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from typing import List
faers_download_page = [
    "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html"
]

def get_available_downloaded_quarters(save_dir: str = "data") -> List[str]:
    """
    Checks the quarters in data/faers_reports and returns a list of the supported quarters.
    """
    supported_quarters = []
    for folder in Path(save_dir).joinpath("faers_reports").iterdir():
        if folder.is_dir():
            supported_quarters.append(folder.name)
    # Sort the quarters
    supported_quarters.sort()
    return supported_quarters


def get_available_processed_quarters(save_dir: str = "data") -> List[str]:
    """
    Checks the quarters in data/processed_faers and returns a list of the supported quarters.
    """
    supported_quarters = []
    for folder in Path(save_dir).joinpath("processed_faers").iterdir():
        if folder.is_dir():
            supported_quarters.append(folder.name)
    return supported_quarters


def convert_quarter_file_str(quarter_string: str) -> str:
    """
    Convert a quarter string from format 'YYYYQN' to 'YYQN'

    Args:
        quarter_string (str): A string in the format 'YYYYQN' (e.g. '2025Q1')

    Returns:
        str: The converted string in format 'YYQN' (e.g. '25Q1')
    """
    # Check if input follows expected format
    if (
        len(quarter_string) == 6
        and quarter_string[4] == "Q"
        and quarter_string[5] in "1234"
    ):
        # Extract the last two digits of the year and append the quarter part
        return quarter_string[2:]
    else:
        # Return original string or raise an error if format doesn't match
        raise ValueError(
            f"Input '{quarter_string}' is not in the expected format 'YYYYQN'"
        )

def get_available_online_quarters() -> dict[str, str]:
    """
    find all web urls in the FAERS download page
    :return: dict files = {"YYYYQN":"url"}
    """
    files = {}
    for page_url in faers_download_page:
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
                t_url = url.get("href")
                # Extract year and quarter from the URL
                match = re.search(r"ascii_(\d{4})([qQ]\d)", t_url)
                if match:
                    year = match.group(1)
                    quarter = match.group(2).upper()  # Convert to uppercase
                    key = f"{year}{quarter}"
                    files[key] = t_url
    return files