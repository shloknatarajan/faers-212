import pandas as pd
import numpy as np

from loguru import logger
from src.aggregations import aggregate_faers_table

def preprocess(df: pd.DataFrame, type: str) -> pd.DataFrame:
    """
    Factory function to preprocess the dataframe for the given type.

    Args:
        df: pd.DataFrame
        type: str
    Returns:
        pd.DataFrame (with preprocessed data)
    """
    if type == "reac":
        return preprocess_reac_df(df)
    elif type == "drug":
        return preprocess_drug_df(df)
    elif type == "demo":
        return preprocess_demo_df(df)
    elif type == "outc":
        return preprocess_outc_df(df)
    elif type == "ther":
        return preprocess_ther_df(df)
    elif type == "indi":
        return preprocess_indi_df(df)
    elif type == "rpsr":
        return preprocess_rpsr_df(df)
    else:
        logger.error(
            f"Invalid type: {type}. Must be one of {['reac', 'drug', 'demo', 'outc', 'ther', 'indi', 'rpsr']}"
        )
        raise ValueError(
            f"Invalid type: {type}. Must be one of {['reac', 'drug', 'demo', 'outc', 'ther', 'indi', 'rpsr']}"
        )


def load_rxnorm_mapping(mapping_path, drug_df):

    # Load full mapping
    logger.info(f"Loading RxNorm mapping from: {mapping_path}")
    mapping = pd.read_csv(mapping_path)

    # Get unique drugnames from FAERS drug table for given time frame
    faers_drugnames = drug_df["drugname"].dropna().unique()

    # Only keep relevant names to minimize merge time
    mapping = mapping[mapping["drugname"].isin(faers_drugnames)]

    return mapping


def preprocess_drug_df(drug):
    drug = drug[
        [
            "primaryid",
            "caseid",
            "role_cod",
            "drugname",
            "prod_ai",
            "drug_seq",
            "dechal",
            "rechal",
        ]
    ]

    logger.info(f"Starting number of reports in 'drug' file: {drug.shape[0]}")

    drug = drug[drug["role_cod"] == "PS"]
    logger.info(
        f"Number of reports in the 'drug' file where drug is the primary suspect: {drug.shape[0]}"
    )

    drug = drug[pd.notnull(drug["drugname"])]  # Drops Nulls
    drug = drug[~drug["drugname"].isin(["unknown"])]  # Drops unknowns

    logger.info(
        f"Number of reports in the 'drug' file after unknown/null drugs are removed: {drug.shape[0]}"
    )

    # Clean drug names BEFORE loading mapping
    drug["drugname"] = (
        drug["drugname"].str.strip().str.lower()
    )  # Strips whitespace, Transforms to lowercase
    drug["drugname"] = drug["drugname"].str.replace(
        "\\", "/"
    )  # Standardizes slashes to '/'
    drug["drugname"] = drug["drugname"].map(
        lambda x: x[:-1] if str(x).endswith(".") else x
    )  # Removes periods at the end of drug names

    # Now load mapping after cleaning drug names
    name_mapping = load_rxnorm_mapping("data/rxnorm_map.csv", drug)

    # Add in rxnorm mapping results
    drug = drug.merge(
        name_mapping[["drugname", "best_match_name", "rxnorm_name"]],
        how="left",
        on="drugname",
    )

    drug["prod_ai"] = drug["prod_ai"].str.lower()
    drug = drug.drop_duplicates(subset=["primaryid"], keep="first")

    logger.info(f"Number of reports in the 'drug' file after rxnorm mapping: {drug.shape[0]}")

    return drug


def preprocess_reac_df(reac: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    if debug:
        logger.debug(f"Starting number of reports in 'reac' file: {reac.shape[0]}")

    reac = reac[pd.notnull(reac["pt"])]  # Drops Nulls
    reac = reac[~reac["pt"].isin(["unknown"])]  # Drops unknowns

    if debug:
        logger.debug(
            f"Number of reports in the 'reac' file after unknown/null reacs are removed: {reac.shape[0]}"
        )

    reac["pt"] = reac["pt"].str.strip().str.lower()  # Transforms to lowercase
    reac["pt"] = reac["pt"].map(
        lambda x: x[:-1] if str(x).endswith(".") else x
    )  # Removes periods at the end of drug names

    return reac


def preprocess_demo_df(demo: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    if debug:
        logger.debug(f"Starting number of reports in 'demo' file: {demo.shape[0]}")

    demo = demo[
        [
            "primaryid",
            "caseid",
            "caseversion",
            "age_cod",
            "age",
            "sex",
            "wt",
            "fda_dt",
            "event_dt",
        ]
    ]

    # If multiple reports have the same primary id and case id, keep the most recent one
    demo = demo.sort_values(
        by=["caseid", "fda_dt", "primaryid"], ascending=[True, False, False]
    )
    demo = demo.drop_duplicates(subset=["caseid"], keep="first")

    if debug:
        logger.debug(
            f"Number of reports in the 'demo' file after duplicate primary/case id combos are removed: {demo.shape[0]}"
        )

    demo = demo[pd.notnull(demo["age"])]
    demo = demo[demo.age_cod != "dec"].reset_index(drop=True)
    demo["age"] = demo["age"].apply(pd.to_numeric, errors="coerce")
    demo["age"] = np.where(
        demo["age_cod"] == "MON", demo["age"] * 1 / 12, demo["age"]
    )  # mounth
    demo["age"] = np.where(
        demo["age_cod"] == "WK", demo["age"] * 1 / 52, demo["age"]
    )  # week
    demo["age"] = np.where(
        demo["age_cod"] == "DY", demo["age"] * 1 / 365, demo["age"]
    )  # day
    demo["age"] = np.where(
        demo["age_cod"] == "HR", demo["age"] * 1 / 8760, demo["age"]
    )  # hour
    demo = demo.drop(["age_cod"], axis=1)

    if debug:
        logger.debug(
            f"Number of reports in the 'demo' file after unknown/invalid ages are removed: {demo.shape[0]}"
        )

    return demo


def preprocess_outc_df(outc: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    if debug:
        logger.debug(f"Starting number of reports in 'outc' file: {outc.shape[0]}")

    outcomes_agg = aggregate_faers_table(outc, 'outc', debug)

    # Map to human-readable outcomes
    outcome_labels = {
        'DE': 'Death',
        'LT': 'Life-Threatening',
        'HO': 'Hospitalization',
        'DS': 'Disability',
        'CA': 'Congenital Anomaly',
        'RI': 'Required Intervention',
        'OT': 'Other Serious'
    }

    # Map each code in the list to its human-readable label
    outcomes_agg['outc_label'] = outcomes_agg['outc_cod'].apply(lambda codes: [outcome_labels[code] for code in codes])

    return outcomes_agg


def preprocess_ther_df(ther: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    if debug:
        logger.debug(f"Starting number of reports in 'ther' file: {ther.shape[0]}")

    ther = ther[['primaryid', 'caseid', 'start_dt', 'dsg_drug_seq']] 

    ther = ther.rename(columns={'dsg_drug_seq': 'drug_seq'})

    return ther

def preprocess_indi_df(indi: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    if debug:
        logger.debug(f"Starting number of reports in 'indi' file: {indi.shape[0]}")

    indi = indi.rename(columns={"indi_drug_seq": "drug_seq"})

    return indi

def preprocess_rpsr_df(rpsr: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    if debug:
        logger.debug(f"Starting number of reports in 'rpsr' file: {rpsr.shape[0]}")

    rpsr_processed = rpsr.copy()

    # map to human-readable reporter codes
    rpsr_processed['rpsr_label'] = rpsr_processed['rpsr_cod'].map({
        'CSM': 'Consumer',
        'HP': 'Health Professional',
        'OT': 'Other'
    })

    return rpsr_processed
