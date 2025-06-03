from .drug_search import filter_by_drug_name, filter_by_age
from .meddra_search import filter_by_preferred_terms
from typing import List, Tuple
import pandas as pd
from .data_loader import FAERSData

def filter_by(df: pd.DataFrame | FAERSData, filter_type: str, filter_value: str | List[str] | Tuple[int, int]) -> pd.DataFrame:
    if filter_type == "drug":
        return filter_by_drug_name(df, filter_value)
    elif filter_type == "age":
        return filter_by_age(df, filter_value[0], filter_value[1])
    elif filter_type == "preferred_terms":
        return filter_by_preferred_terms(df, filter_value)
    else:
        raise ValueError(f"Invalid filter type: {filter_type}")