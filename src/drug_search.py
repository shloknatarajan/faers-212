#!/usr/bin/env python3
import argparse
import pandas as pd
import sys
from pathlib import Path
from src.data_loader import FAERSData
from loguru import logger

def filter_by_drug_name(drug_df: pd.DataFrame | FAERSData, drug_name: str):
    if isinstance(drug_df, FAERSData):
        return filter_by_drug_name_faersdata(drug_df, drug_name)
    else:
        return filter_by_drug_name_drug_df(drug_df, drug_name)

def filter_by_drug_name_drug_df(drug_df: pd.DataFrame, drug_name: str):
    """
    Find and filter drug reports based on the query drug name
    """
    just_drugs = drug_df
    
    query_drug_df = just_drugs[
        just_drugs['drugname'].str.contains(drug_name, na=False) |
        just_drugs['prod_ai'].str.contains(drug_name, na=False) |
        just_drugs['best_match_name'].str.contains(drug_name, na=False) |
        just_drugs['rxnorm_name'].str.contains(drug_name, na=False)
    ]
    
    logger.info(f"Number of reports for {drug_name} in 'drug' file: {query_drug_df.shape[0]}")
    logger.info(f"Number of reports with same 'primaryid': {query_drug_df.duplicated(subset=['primaryid']).sum()}")
    
    return query_drug_df

def filter_by_drug_name_faersdata(drug_df: FAERSData, drug_name: str):
    """
    Find and filter drug reports based on the query drug name
    """
    return filter_by_drug_name(drug_df.drug_data, drug_name)

# Merge drug reports with demographics data
def merge_with_demographics(query_drug_df, demo_df):
    
    required_cols = ['primaryid', 'caseid']
    for df_name, df in [('drug', query_drug_df), ('demo', demo_df)]:
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Error: Missing required columns in {df_name} file: {missing_cols}")
            return None
    
    merged_df = pd.merge(demo_df, query_drug_df, on=['primaryid', 'caseid'], how='inner')
    logger.info(f"Number of reports after merging with demographics: {merged_df.shape[0]}")
    logger.info(f"Number of reports with same 'primaryid': {merged_df.duplicated(subset=['primaryid']).sum()}")
    
    return merged_df

#merge with outcomes
def merge_with_outcomes(merged_df, outc_df):

    merged_df = pd.merge(merged_df, outc_df, on=['primaryid', 'caseid'], how='left')
    logger.info(f"Number of reports after merging with outcomes: {merged_df.shape[0]}")
    
    return merged_df



def merge_with_indications(merged_df, indi_df):

    # Check if drug_seq exists in merged_df
    if 'drug_seq' not in merged_df.columns:
        logger.warning("Warning: 'drug_seq' column not found in merged data, skipping indications merge")
        return merged_df
    
    merged_df = pd.merge(merged_df, indi_df, on=['primaryid', 'caseid', 'drug_seq'], how='left')
    logger.info(f"Number of reports after merging with indications: {merged_df.shape[0]}")
    
    return merged_df


def filter_by_age(merged_df, min_age_yrs, max_age_yrs):

    filtered_df = merged_df[
        (merged_df['age'] >= min_age_yrs) & 
        (merged_df['age'] <= max_age_yrs)
    ]
    
    logger.info(f"Number of reports that meet age range ({min_age_yrs}-{max_age_yrs}): {filtered_df.shape[0]}")
    logger.info(f"Number of reports with same 'primaryid': {filtered_df.duplicated(subset=['primaryid']).sum()}")
    
    return filtered_df

def extract_top_indications(merged_df, drug_df, indi_df, top_n=10):
    
    if 'indi_pt' not in merged_df.columns:
        logger.warning("Warning: 'indi_pt' column not found, cannot extract top indications")
        return None
    
    # Extract top indications
    top_indi = merged_df['indi_pt'].value_counts().head(top_n)
    top_indi_values = top_indi.index.tolist()
    
    logger.info(f"Top {top_n} indications:")
    logger.info(top_indi)
    
    # Remove "Product used for unknown indication" if present
    if 'Product used for unknown indication' in top_indi_values:
        top_indi_values.remove('Product used for unknown indication')

    # Find matching rows in indications data
    if indi_df is not None:
        matching_rows = indi_df[indi_df['indi_pt'].isin(top_indi_values)]
        
        # Merge with drug data
        required_cols = ['primaryid', 'caseid', 'drug_seq']
        missing_cols = [col for col in required_cols if col not in drug_df.columns or col not in matching_rows.columns]
        if not missing_cols:
            query_indications_df = pd.merge(drug_df, matching_rows, on=['primaryid', 'caseid', 'drug_seq'], how='inner')
            logger.info(f"\nNumber of reports matching top indications: {query_indications_df.shape[0]}")
            return query_indications_df
    
    return None

def run_indications_analysis(data: FAERSData, query_drug, min_age_yrs=0, max_age_yrs=100, top_n=10):

    print(f"Starting analysis for drug: {query_drug}")
    print(f"Age range: {min_age_yrs}-{max_age_yrs} years")
    print("-" * 50)
    
    # Load tables from FAERSData object
    drug_df = data.drug_data
    demo_df = data.demo_data
    outc_df = data.outc_data
    indi_df = data.indi_data
    
    # Filter drug reports
    query_drug_df = filter_by_drug_name(drug_df, query_drug)
    if query_drug_df is None or query_drug_df.empty:
        print(f"No reports found for drug: {query_drug}")
        return
    
    # Merge with demograph
    merged_df = merge_with_demographics(query_drug_df, demo_df)
    if merged_df is None or merged_df.empty:
        print("No matching reports found after demographic merge")
        return
    
    # outcomes merge (if available)
    if outc_df is not None:
        merged_df = merge_with_outcomes(merged_df, outc_df)
    
    # indications merge (if available)
    if indi_df is not None:
        merged_df = merge_with_indications(merged_df, indi_df)
    
    # Filter by age
    merged_df = filter_by_age(merged_df, min_age_yrs, max_age_yrs)
    
    # top indications
    if indi_df is not None:
        print("\n" + "="*50)
        print("TOP INDICATIONS ANALYSIS")
        print("="*50)
        query_indications_df = extract_top_indications(merged_df, drug_df, indi_df, top_n)
    
    print(f"\nFinal dataset shape: {merged_df.shape}")
    print("Analysis complete")