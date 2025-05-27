import os
from loguru import logger
import pandas as pd
import argparse
from pathlib import Path

"""
Merging the dataframes from raw_faers/{quarter} into a single dataframe.

This will eventually need to be moved into a class / preprocessing pipeline 
as the number of prepreocessing steps grows.

Need to add:
- deduplicatin
- drug normalization
"""
from src.utils import get_raw_quarters, get_processed_quarters, format_quarter

def load_raw_data(report_quarter: str) -> pd.DataFrame:
    """
    Load the raw data from the raw_faers/{quarter} directory
    """
    if report_quarter not in get_raw_quarters():
        raise ValueError(
            f"Report quarter {report_quarter} is not supported. Supported report quarters are: {get_raw_quarters()}"
        )
    # Load the report data
    # DEMO
    demo_file = (
        Path("data/raw_faers")
        / report_quarter
        / f"DEMO{format_quarter(report_quarter)}.txt"
    )

    # DRUG
    drug_file = (
        Path("data/raw_faers")
        / report_quarter
        / f"DRUG{format_quarter(report_quarter)}.txt"
    )

    # OUTCOME
    outcome_file = (
        Path("data/raw_faers")
        / report_quarter
        / f"OUTC{format_quarter(report_quarter)}.txt"
    )

    # REACTION
    reaction_file = (
        Path("data/raw_faers")
        / report_quarter
        / f"REAC{format_quarter(report_quarter)}.txt"
    )

    # RPSR
    rpsr_file = (
        Path("data/raw_faers")
        / report_quarter
        / f"RPSR{format_quarter(report_quarter)}.txt"
    )

    # THERAPY
    therapy_file = (
        Path("data/raw_faers")
        / report_quarter
        / f"THER{format_quarter(report_quarter)}.txt"
    )

    logger.info(f"Loading data from {report_quarter}")
    # === Load Data ===
    try:
        demo_data = pd.read_csv(demo_file, sep="$", low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"DEMO{report_quarter}.txt not found")
        raise e
    try:
        drug_data = pd.read_csv(drug_file, sep="$", low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"DRUG{report_quarter}.txt not found")
        raise e
    try:
        reaction_data = pd.read_csv(reaction_file, sep="$", low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"REAC{report_quarter}.txt not found")
        raise e
    try:
        outcome_data = pd.read_csv(outcome_file, sep="$", low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"OUTC{report_quarter}.txt not found")
        raise e
    try:
        rpsr_data = pd.read_csv(rpsr_file, sep="$", low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"RPSR{report_quarter}.txt not found")
        raise e
    try:
        therapy_data = pd.read_csv(therapy_file, sep="$", low_memory=False)
    except FileNotFoundError as e:
        logger.error(f"THER{report_quarter}.txt not found")
        raise e

def merge_reports(report_quarter: str, overwrite: bool = False) -> pd.DataFrame:
    """
    Merge the raw dataframes into a single dataframe
    """
    if report_quarter not in get_raw_quarters():
        raise ValueError(
            f"Report quarter {report_quarter} is not supported. Supported report quarters are: {get_raw_quarters()}"
        )
    if report_quarter in get_processed_quarters() and not overwrite:
        logger.info(f"Report quarter {report_quarter} already processed. Skipping...")
        return

    demo_data, drug_data, reaction_data, outcome_data, rpsr_data, therapy_data = load_raw_data(report_quarter)
    # === Load Data ===
    logger.info(f"Merging dataframes")

    # === Start with drug_data ===
    merged = drug_data.copy()

    # === Merge with demo_data ===
    logger.debug(f"Merging with demo_data")
    merged = merged.merge(demo_data, on=["primaryid", "caseid"], how="left")

    # === Merge reaction_data (aggregate PT terms) ===
    logger.debug(f"Merging with reaction_data")
    reactions_agg = (
        reaction_data.groupby(["primaryid", "caseid"])["pt"]
        .apply(lambda x: "; ".join(x.dropna().unique()))
        .reset_index()
    )
    merged = merged.merge(reactions_agg, on=["primaryid", "caseid"], how="left")

    # === Merge outcome_data (aggregate outcome codes) ===
    logger.debug(f"Merging with outcome_data")
    outcomes_agg = (
        outcome_data.groupby(["primaryid", "caseid"])["outc_cod"]
        .apply(lambda x: "; ".join(x.dropna().unique()))
        .reset_index()
    )
    merged = merged.merge(outcomes_agg, on=["primaryid", "caseid"], how="left")

    # === Merge rpsr_data (aggregate reporter occupation codes) ===
    logger.debug(f"Merging with rpsr_data")
    rpsr_agg = (
        rpsr_data.groupby(["primaryid", "caseid"])["rpsr_cod"]
        .apply(lambda x: "; ".join(x.dropna().unique()))
        .reset_index()
    )
    merged = merged.merge(rpsr_agg, on=["primaryid", "caseid"], how="left")

    # === Merge therapy_data (aggregate therapy info) ===
    logger.debug(f"Merging with therapy_data")
    therapy_agg = (
        therapy_data.groupby(["primaryid", "caseid"])[
            ["start_dt", "end_dt", "dur", "dur_cod"]
        ]
        .agg(lambda col: "; ".join(col.dropna().astype(str).unique()))
        .reset_index()
    )
    merged = merged.merge(therapy_agg, on=["primaryid", "caseid"], how="left")

    # === Final Output ===
    logger.info(f"Final merged shape: {merged.shape}")

    # Write merged dataframe to csv
    output_dir = f"data/processed_faers/{report_quarter}"
    os.makedirs(output_dir, exist_ok=True)
    merged.to_csv(
        f"{output_dir}/MERGED{format_quarter(report_quarter)}.csv", index=False
    )
    return merged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge FAERS reports.")
    parser.add_argument(
        "--quarters", nargs="+", type=str, help="The quarters to merge (e.g. 2024Q1)"
    )
    args = parser.parse_args()

    if args.quarters == "all":
        for quarter in get_raw_quarters():
            merge_reports(quarter)
    else:
        for quarter in args.quarters:
            merge_reports(quarter)
