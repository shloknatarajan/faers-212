"""
Add a column with the normalized drug name
"""
import pandas as pd

def normalize_drug_name(drug_name: str) -> str:
    """
    Normalize the drug name
    """
    pass

def normalize_drug_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the drug names in the dataframe
    """
    df["RX_NORM_DRUG_NAME"] = df["DRUG_NAME"].apply(normalize_drug_name)
    return df