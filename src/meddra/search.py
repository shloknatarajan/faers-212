"""
Search for MedDRA terms in a FAERS report
"""
import pandas as pd
from typing import List
from src.load_data.load_report import load_report
from loguru import logger

def filter_by_any_terms(df: pd.DataFrame, terms: List[str]) -> pd.DataFrame:
    """
    Filter DataFrame to only include rows that contain ANY of the specified terms.
    
    Args:
        df: DataFrame containing the data
        terms: List of terms to search for (all must be present)
        
    Returns:
        DataFrame containing only rows that have all specified terms
    """
    terms_set = set(terms)
    return df[df['pt'].apply(lambda term_list: any(t in terms_set for t in term_list))]

def filter_by_all_terms(df: pd.DataFrame, terms: List[str]) -> pd.DataFrame:
    """
    Filter DataFrame to only include rows that contain ALL of the specified terms.
    
    Args:
        df: DataFrame containing the data
        terms: List of terms to search for (all must be present)
        
    Returns:
        DataFrame containing only rows that have all specified terms
    """
    # Filter rows where all terms are present
    mask = df['pt'].apply(lambda x: all(term in x for term in terms))
    
    return df[mask]

def search_meddra(report: pd.DataFrame, preferred_terms: List[str]) -> pd.DataFrame:
    """
    Search for MedDRA terms in a FAERS report
    """
    # Get all rows where the column 'pt' contains any of the preferred terms
    matching_rows = filter_by_all_terms(report, preferred_terms)

    return matching_rows


def get_system_organ_class(meddra_term: str) -> str:
    """
    Get the system organ class for a MedDRA term
    """
    pass

if __name__ == "__main__":
    report_quarter = "25Q1"
    preferred_terms = ["Palmar-plantar erythrodysaesthesia syndrome"]
    report = load_report(report_quarter)
    matching_rows = search_meddra(report, preferred_terms)
    print(matching_rows)
