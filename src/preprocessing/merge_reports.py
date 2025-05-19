import os
from loguru import logger
import pandas as pd
import argparse

def get_supported_quarters():
    """
    Checks the quarters in data/raw_faers and returns a list of the supported quarters.
    """
    supported_quarters = []
    for folder in os.listdir("data/raw_faers"):
        if os.path.isdir(os.path.join("data/raw_faers", folder)):
            supported_quarters.append(folder)
    return supported_quarters

def get_processed_quarters():
    """
    Checks the quarters in data/processed_faers and returns a list of the supported quarters.
    """
    supported_quarters = []
    for folder in os.listdir("data/processed_faers"):
        if os.path.isdir(os.path.join("data/processed_faers", folder)):
            supported_quarters.append(folder)
    return supported_quarters

def format_quarter(quarter_string):
    """
    Convert a quarter string from format 'YYYYQN' to 'YYQN'
    
    Args:
        quarter_string (str): A string in the format 'YYYYQN' (e.g. '2025Q1')
        
    Returns:
        str: The converted string in format 'YYQN' (e.g. '25Q1')
    """
    # Check if input follows expected format
    if len(quarter_string) == 6 and quarter_string[4] == 'Q' and quarter_string[5] in '1234':
        # Extract the last two digits of the year and append the quarter part
        return quarter_string[2:]
    else:
        # Return original string or raise an error if format doesn't match
        raise ValueError(f"Input '{quarter_string}' is not in the expected format 'YYYYQN'")

def merge_reports(report_quarter, overwrite=False):
    if report_quarter not in get_supported_quarters():
        raise ValueError(f"Report quarter {report_quarter} is not supported. Supported report quarters are: {get_supported_quarters()}")
    if report_quarter in get_processed_quarters() and not overwrite:
        logger.info(f"Report quarter {report_quarter} already processed. Skipping...")
        return

    # Load the report data
    # DEMO
    demo_file = f"data/raw_faers/{report_quarter}/DEMO{format_quarter(report_quarter)}.txt"

    # DRUG
    drug_file = f"data/raw_faers/{report_quarter}/DRUG{format_quarter(report_quarter)}.txt"

    # OUTCOME
    outcome_file = f"data/raw_faers/{report_quarter}/OUTC{format_quarter(report_quarter)}.txt"

    # REACTION
    reaction_file = f"data/raw_faers/{report_quarter}/REAC{format_quarter(report_quarter)}.txt"

    # RPSR
    rpsr_file = f"data/raw_faers/{report_quarter}/RPSR{format_quarter(report_quarter)}.txt"

    # THERAPY
    therapy_file = f"data/raw_faers/{report_quarter}/THER{format_quarter(report_quarter)}.txt"

    logger.info(f"Loading data from {report_quarter}")
    # === Load Data ===
    try:
        demo_data = pd.read_csv(demo_file, sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"DEMO{report_quarter}.txt not found")
        raise e
    try:    
        drug_data = pd.read_csv(drug_file, sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"DRUG{report_quarter}.txt not found")
        raise e
    try:
        reaction_data = pd.read_csv(reaction_file, sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"REAC{report_quarter}.txt not found")
        raise e
    try:
        outcome_data = pd.read_csv(outcome_file, sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"OUTC{report_quarter}.txt not found")
        raise e
    try:
        rpsr_data = pd.read_csv(rpsr_file, sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"RPSR{report_quarter}.txt not found")
        raise e
    try:
        therapy_data = pd.read_csv(therapy_file, sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"THER{report_quarter}.txt not found")
        raise e
    
    logger.info(f"Merging dataframes")
    
    # === Start with drug_data ===
    merged = drug_data.copy()

    # === Merge with demo_data ===
    logger.debug(f"Merging with demo_data")
    merged = merged.merge(demo_data, on=['primaryid', 'caseid'], how='left')

    # === Merge reaction_data (aggregate PT terms) ===
    logger.debug(f"Merging with reaction_data")
    reactions_agg = reaction_data.groupby(['primaryid', 'caseid'])['pt'] \
        .apply(lambda x: '; '.join(x.dropna().unique())).reset_index()
    merged = merged.merge(reactions_agg, on=['primaryid', 'caseid'], how='left')

    # === Merge outcome_data (aggregate outcome codes) ===
    logger.debug(f"Merging with outcome_data")
    outcomes_agg = outcome_data.groupby(['primaryid', 'caseid'])['outc_cod'] \
        .apply(lambda x: '; '.join(x.dropna().unique())).reset_index()
    merged = merged.merge(outcomes_agg, on=['primaryid', 'caseid'], how='left')

    # === Merge rpsr_data (aggregate reporter occupation codes) ===
    logger.debug(f"Merging with rpsr_data")
    rpsr_agg = rpsr_data.groupby(['primaryid', 'caseid'])['rpsr_cod'] \
        .apply(lambda x: '; '.join(x.dropna().unique())).reset_index()
    merged = merged.merge(rpsr_agg, on=['primaryid', 'caseid'], how='left')

    # === Merge therapy_data (aggregate therapy info) ===
    logger.debug(f"Merging with therapy_data")
    therapy_agg = therapy_data.groupby(['primaryid', 'caseid'])[['start_dt', 'end_dt', 'dur', 'dur_cod']] \
        .agg(lambda col: '; '.join(col.dropna().astype(str).unique())).reset_index()
    merged = merged.merge(therapy_agg, on=['primaryid', 'caseid'], how='left')

    # === Final Output ===
    logger.info(f"Final merged shape: {merged.shape}")

    # Write merged dataframe to csv
    output_dir = f"data/processed_faers/{report_quarter}"
    os.makedirs(output_dir, exist_ok=True)
    merged.to_csv(f"{output_dir}/MERGED{format_quarter(report_quarter)}.csv", index=False)
    return merged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge FAERS reports.')
    parser.add_argument('--quarter', type=str, help='The quarter to merge (e.g. 2024Q1)')
    args = parser.parse_args()

    merge_reports(args.quarter)