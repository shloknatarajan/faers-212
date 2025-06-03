from src.data_loader import FAERSData
from src.utils import aggregate_faers_table
from loguru import logger

def merge_data(data: FAERSData):
    """
    Merge the data for the given start and end years and quarters.
    """
    # === Load Data ===
    logger.info(f"Merging dataframes")

    # === Start with drug_data ===
    merged_df = data.drug_data.copy()

    # === Merge with demo_data ===
    logger.debug(f"Merging with demo_data")
    merged_df = merged_df.merge(data.demo_data, on=["primaryid", "caseid"], how="left")
    
    # === Merge and aggregate reaction_data ===
    logger.debug(f"Merging with reaction_data")
    reac_agg = aggregate_faers_table(data.reac_data, 'reac', debug=False)
    merged_df = merged_df.merge(reac_agg, on=["primaryid", "caseid"], how="left")
    
    # === Merge outcome_data ===
    logger.debug(f"Merging with outcome_data")
    merged_df = merged_df.merge(data.outc_data, on=["primaryid", "caseid"], how="left")
    
    # === Merge and aggregate rpsr_data ===
    logger.debug(f"Merging with rpsr_data")
    rpsr_agg = aggregate_faers_table(data.rpsr_data, 'rpsr', debug=False)
    merged_df = merged_df.merge(rpsr_agg, on=["primaryid", "caseid"], how="left")
    
    # === Merge and aggregate therapy_data ===
    logger.debug(f"Merging with therapy_data")
    ther_agg = aggregate_faers_table(data.ther_data, 'ther', debug=False)
    merged_df = merged_df.merge(ther_agg, on=["primaryid", "caseid"], how="left")
    
    # === Final Output ===
    logger.info(f"Final merged shape: {merged_df.shape}")
    return merged_df
    