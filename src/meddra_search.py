"""
Search for MedDRA terms in a FAERS report
"""

import pandas as pd
import pickle
from typing import List
from loguru import logger


def filter_by_any_pt_terms(df: pd.DataFrame, terms: List[str]) -> pd.DataFrame:
    """
    Filter DataFrame to only include rows that contain ANY of the specified terms.

    Args:
        df: DataFrame containing the data
        terms: List of terms to search for (all must be present)

    Returns:
        DataFrame containing only rows that have all specified terms
    """
    terms_set = set(terms)
    return df[df["pt"].apply(lambda term_list: any(t in terms_set for t in term_list))]


def filter_by_all_pt_terms(df: pd.DataFrame, terms: List[str]) -> pd.DataFrame:
    """
    Filter DataFrame to only include rows that contain ALL of the specified terms.

    Args:
        df: DataFrame containing the data
        terms: List of terms to search for (all must be present)

    Returns:
        DataFrame containing only rows that have all specified terms
    """
    # Filter rows where all terms are present
    mask = df["pt"].apply(lambda x: all(term in x for term in terms))

    return df[mask]

def filter_by_preferred_terms(report: pd.DataFrame, preferred_terms: List[str]) -> pd.DataFrame:
    """
    Filter for MedDRA Preferred Terms in a FAERS report. PTs are contained in REAC
    """
    # Get all rows where the column 'pt' contains any of the preferred terms
    logger.info(f"Searching for {preferred_terms} in {report.shape[0]} rows")
    starting_rows = report.shape[0]
    matching_rows = filter_by_all_pt_terms(report, preferred_terms)
    logger.info(f"Number of rows after filtering by preferred terms: {matching_rows.shape[0]}")
    logger.info(f"Number of rows removed: {starting_rows - matching_rows.shape[0]}")
    ending_rows = matching_rows.shape[0]
    return matching_rows, starting_rows, ending_rows


def get_system_organ_classes(meddra_terms: List[str]) -> List[str]:
    """
    TODO: Maybe change this from code to term
    Get the system organ class for MedDRA LLT codes. List allows for batches of term processing.
    Args:
        meddra_terms: List of MedDRA LLT codes
    Returns:
        List of system organ classes
    """
    with open("llt_to_soc.pkl", "rb") as f:
        llt_to_soc = pickle.load(f)
    return [llt_to_soc[term] for term in meddra_terms]


# def filter_by_soc(
#     report: pd.DataFrame, system_organ_classes: List[str]
# ) -> pd.DataFrame:
#     """
#     Filter for MedDRA System Organ Classes in a FAERS report
#     Args:
#         report: FAERS report
#         system_organ_classes: List of system organ classes by
#     Returns:
#         DataFrame of rows where the system organ class is in the list
#     """
#     logger.error("Not implemented")
#     pass

