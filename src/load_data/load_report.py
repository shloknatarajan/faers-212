import pandas as pd
import os
from loguru import logger
from pathlib import Path
import argparse
from typing import List
from src.utils import available_processed_quarters, format_quarter


def get_report_path(report_quarter: str) -> Path:
    """
    Get the path to a report file in the saved_data directory
    """
    return (
        Path("data/processed_faers")
        / report_quarter
        / f"MERGED{format_quarter(report_quarter)}.csv"
    )

def load_report(report_quarter: str) -> pd.DataFrame:
    """
    Load a report from the given quarter
    """
    if report_quarter not in available_processed_quarters():
        raise ValueError(
            f"Report quarter {report_quarter} is not supported. Supported report quarters are: {available_processed_quarters()}"
        )

    # Get file path to report
    report_file = get_report_path(report_quarter)
    if not report_file.exists():
        raise FileNotFoundError(f"Report file {report_file} not found")

    # Load the report
    report = pd.read_csv(report_file, sep=",", low_memory=False)
    logger.info(f"Loaded report {report_quarter} with shape {report.shape}")

    # Load the ; seperated lists in the pt column
    try:
        report["pt"] = (
            report["pt"]
            .fillna("")
            .apply(lambda x: [term.strip() for term in x.split(";") if term.strip()])
        )
    except Exception as e:
        logger.error(f"Error preprocessing report {report_quarter}: {e}")

    return report


def load_reports(quarters: List[str]) -> pd.DataFrame:
    """
    Load a report from the given quarter
    """
    # Check if all of the quarters are processed
    missing_quarters = [quarter for quarter in quarters if quarter not in available_processed_quarters()]
    if len(missing_quarters) > 0:
        logger.error(f"Missing processed quarters: {missing_quarters}")
        raise ValueError(f"Missing processed quarters: {missing_quarters}")

    # Load all available processed quarters
    if len(quarters) == 1 and quarters[0] == "all":
        logger.info("Loading all processed quarters")
        quarters = available_processed_quarters()
    return pd.concat([load_report(quarter) for quarter in quarters])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quarters", type=str, nargs="+", required=True)
    args = parser.parse_args()
    report = load_reports(args.quarters)
    print(report.head())
