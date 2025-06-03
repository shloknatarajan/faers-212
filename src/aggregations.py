"""Functions for aggregating FAERS data."""

import pandas as pd
from loguru import logger
from typing import Dict, Callable, Any

def aggregate_outcomes(outc: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Aggregate outcome data by primaryid and caseid."""
    if debug:
        logger.debug(f"Aggregating outcomes for {outc.shape[0]} rows")
    
    outcomes_agg = (
        outc.groupby(["primaryid", "caseid"])["outc_cod"]
        .apply(lambda x: list(x.dropna().unique()))
        .reset_index()
    )
    return outcomes_agg

def aggregate_reactions(reac: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Aggregate reaction data by primaryid and caseid."""
    if debug:
        logger.debug(f"Aggregating reactions for {reac.shape[0]} rows")
        
    reactions_agg = (
        reac.groupby(["primaryid", "caseid"])["pt"]
        .apply(lambda x: list(x.dropna().unique()))
        .reset_index()
    )
    return reactions_agg

def aggregate_therapy(ther: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Aggregate therapy data by primaryid and caseid."""
    if debug:
        logger.debug(f"Aggregating therapy data for {ther.shape[0]} rows")
        
    therapy_agg = (
        ther.groupby(["primaryid", "caseid"])[
            ["start_dt", "end_dt", "dur", "dur_cod"]
        ]
        .apply(lambda x: list(x.dropna().unique()))
        .reset_index()
    )
    return therapy_agg

def aggregate_reporter(rpsr: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    """Aggregate reporter data by primaryid and caseid."""
    if debug:
        logger.debug(f"Aggregating reporter data for {rpsr.shape[0]} rows")
        
    rpsr_agg = (
        rpsr.groupby(["primaryid", "caseid"])["rpsr_cod"]
        .apply(lambda x: list(x.dropna().unique()))
        .reset_index()
    )
    return rpsr_agg

# Factory method setup similar to preprocessing.py
AGGREGATION_FUNCTIONS: Dict[str, Callable[[pd.DataFrame, bool], pd.DataFrame]] = {
    "reac": aggregate_reactions,
    "ther": aggregate_therapy,
    "rpsr": aggregate_reporter,
    "outc": aggregate_outcomes,
}

def aggregate_faers_table(data: pd.DataFrame, data_type: str, debug: bool = False) -> pd.DataFrame:
    """
    Aggregate FAERS data based on data type.
    
    Args:
        data: DataFrame to aggregate
        data_type: Type of data ('reac', 'ther', 'rpsr')
        debug: Whether to print debug information
        
    Returns:
        Aggregated DataFrame
    """
    if data_type not in AGGREGATION_FUNCTIONS:
        raise ValueError(f"Unknown data type: {data_type}")
        
    return AGGREGATION_FUNCTIONS[data_type](data, debug)
