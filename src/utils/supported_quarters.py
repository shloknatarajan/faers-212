import os
from pathlib import Path


def get_raw_quarters():
    """
    Checks the quarters in data/raw_faers and returns a list of the supported quarters.
    """
    supported_quarters = []
    for folder in Path("data/raw_faers").iterdir():
        if folder.is_dir():
            supported_quarters.append(folder.name)
    return supported_quarters


def get_processed_quarters():
    """
    Checks the quarters in data/processed_faers and returns a list of the supported quarters.
    """
    supported_quarters = []
    for folder in Path("data/processed_faers").iterdir():
        if folder.is_dir():
            supported_quarters.append(folder.name)
    return supported_quarters


def format_quarter(quarter_string: str) -> str:
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
