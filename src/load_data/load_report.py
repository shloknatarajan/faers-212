import pandas as pd
import os
from loguru import logger

SUPPORTED_REPORT_QUARTERS = [
    '2025Q1',
]

def download_reports(report_quarter):
    if report_quarter not in SUPPORTED_REPORT_QUARTERS:
        raise ValueError(f"Report quarter {report_quarter} is not supported. Supported report quarters are: {SUPPORTED_REPORT_QUARTERS}")
    #TODO: Implement a download method
    pass


def merge_reports(report_quarter):
    if report_quarter not in SUPPORTED_REPORT_QUARTERS:
        raise ValueError(f"Report quarter {report_quarter} is not supported. Supported report quarters are: {SUPPORTED_REPORT_QUARTERS}")
    
    # Load the report data
    # DEMO
    demo_file = f"saved_data/{report_quarter}/DEMO{report_quarter}.txt"
    demo_data = pd.read_csv(demo_file, sep='$', low_memory=False)

    # DRUG
    drug_file = f"saved_data/{report_quarter}/DRUG{report_quarter}.txt"
    drug_data = pd.read_csv(drug_file, sep='$', low_memory=False)

    # OUTCOME
    outcome_file = f"saved_data/{report_quarter}/OUTC{report_quarter}.txt"
    outcome_data = pd.read_csv(outcome_file, sep='$', low_memory=False)

    # REACTION
    reaction_file = f"saved_data/{report_quarter}/REAC{report_quarter}.txt"
    reaction_data = pd.read_csv(reaction_file, sep='$', low_memory=False)

    # RPSR
    rpsr_file = f"saved_data/{report_quarter}/RPSR{report_quarter}.txt"
    rpsr_data = pd.read_csv(rpsr_file, sep='$', low_memory=False)

    # === Load Data ===
    try:
        demo_data = pd.read_csv(f'saved_data/{report_quarter}/DEMO{report_quarter}.txt', sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"DEMO{report_quarter}.txt not found")
        raise e
    try:    
        drug_data = pd.read_csv(f'saved_data/{report_quarter}/DRUG{report_quarter}.txt', sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"DRUG{report_quarter}.txt not found")
        raise e
    try:
        reaction_data = pd.read_csv(f'saved_data/{report_quarter}/REAC{report_quarter}.txt', sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"REAC{report_quarter}.txt not found")
        raise e
    try:
        outcome_data = pd.read_csv(f'saved_data/{report_quarter}/OUTC{report_quarter}.txt', sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"OUTC{report_quarter}.txt not found")
        raise e
    try:
        rpsr_data = pd.read_csv(f'saved_data/{report_quarter}/RPSR{report_quarter}.txt', sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"RPSR{report_quarter}.txt not found")
        raise e
    try:
        therapy_data = pd.read_csv(f'saved_data/{report_quarter}/THER{report_quarter}.txt', sep='$', low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"THER{report_quarter}.txt not found")
        raise e
    
    logger.info(f"Merging dataframes")
    
    # === Start with drug_data ===
    merged = drug_data.copy()

    # === Merge with demo_data ===
    merged = merged.merge(demo_data, on=['primaryid', 'caseid'], how='left')

    # === Merge reaction_data (aggregate PT terms) ===
    reactions_agg = reaction_data.groupby(['primaryid', 'caseid'])['pt'] \
        .apply(lambda x: '; '.join(x.dropna().unique())).reset_index()
    merged = merged.merge(reactions_agg, on=['primaryid', 'caseid'], how='left')

    # === Merge outcome_data (aggregate outcome codes) ===
    outcomes_agg = outcome_data.groupby(['primaryid', 'caseid'])['outc_cod'] \
        .apply(lambda x: '; '.join(x.dropna().unique())).reset_index()
    merged = merged.merge(outcomes_agg, on=['primaryid', 'caseid'], how='left')

    # === Merge rpsr_data (aggregate reporter occupation codes) ===
    rpsr_agg = rpsr_data.groupby(['primaryid', 'caseid'])['rpsr_cod'] \
        .apply(lambda x: '; '.join(x.dropna().unique())).reset_index()
    merged = merged.merge(rpsr_agg, on=['primaryid', 'caseid'], how='left')

    # === Merge therapy_data (aggregate therapy info) ===
    therapy_agg = therapy_data.groupby(['primaryid', 'caseid'])[['start_dt', 'end_dt', 'dur', 'dur_cod']] \
        .agg(lambda col: '; '.join(col.dropna().astype(str).unique())).reset_index()
    merged = merged.merge(therapy_agg, on=['primaryid', 'caseid'], how='left')

    # === Final Output ===
    logger.info(f"Final merged shape: {merged.shape}")
    return merged