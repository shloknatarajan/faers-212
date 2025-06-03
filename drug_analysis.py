#!/usr/bin/env python3
import argparse
import pandas as pd
import sys
from pathlib import Path


def load_data(csv_path):
    try:
        return pd.read_csv(csv_path, low_memory=False)
    except Exception as e:
        print(f"Error loading CSV file: {e}", file=sys.stderr)
        sys.exit(1)


#Find and filter drug reports based on the query drug name
def filter_drug_reports(drug_df, query_drug):
    
    query_drug_df = drug_df[
        drug_df['drugname'].str.contains(query_drug, na=False) |
        drug_df['prod_ai'].str.contains(query_drug, na=False) |
        drug_df['best_match_name'].str.contains(query_drug, na=False) |
        drug_df['rxnorm_name'].str.contains(query_drug, na=False)
    ]
    
    print(f"Number of reports for {query_drug} in 'drug' file: {query_drug_df.shape[0]}")
    print(f"Number of reports with same 'primaryid': {query_drug_df.duplicated(subset=['primaryid']).sum()}")
    
    return query_drug_df

# Merge drug reports with demographics data
def merge_with_demographics(query_drug_df, demo_df):
    
    required_cols = ['primaryid', 'caseid']
    for df_name, df in [('drug', query_drug_df), ('demo', demo_df)]:
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Error: Missing required columns in {df_name} file: {missing_cols}")
            return None
    
    merged_df = pd.merge(demo_df, query_drug_df, on=['primaryid', 'caseid'], how='inner')
    print(f"Number of reports after merging with demographics: {merged_df.shape[0]}")
    print(f"Number of reports with same 'primaryid': {merged_df.duplicated(subset=['primaryid']).sum()}")
    
    return merged_df

#merge with outcomes
def merge_with_outcomes(merged_df, outc_df):

    merged_df = pd.merge(merged_df, outc_df, on=['primaryid', 'caseid'], how='left')
    print(f"Number of reports after merging with outcomes: {merged_df.shape[0]}")
    
    return merged_df


#merge with indications
def merge_with_indications(merged_df, indi_df):

    # Check if drug_seq exists in merged_df
    if 'drug_seq' not in merged_df.columns:
        print("Warning: 'drug_seq' column not found in merged data, skipping indications merge")
        return merged_df
    
    merged_df = pd.merge(merged_df, indi_df, on=['primaryid', 'caseid', 'drug_seq'], how='left')
    print(f"Number of reports after merging with indications: {merged_df.shape[0]}")
    
    return merged_df

#age filtering
def filter_by_age(merged_df, min_age_yrs, max_age_yrs):

    filtered_df = merged_df[
        (merged_df['age'] >= min_age_yrs) & 
        (merged_df['age'] <= max_age_yrs)
    ]
    
    print(f"Number of reports that meet age range ({min_age_yrs}-{max_age_yrs}): {filtered_df.shape[0]}")
    print(f"Number of reports with same 'primaryid': {filtered_df.duplicated(subset=['primaryid']).sum()}")
    
    return filtered_df

#top indications 
def extract_top_indications(merged_df, top_n=10):
    if 'indi_pt' not in merged_df.columns:
        print("Warning: 'indi_pt' column not found, cannot extract top indications")
        return None
    
    # Extract top indications
    top_indi = merged_df['indi_pt'].value_counts().head(top_n)
    
    print(f"Top {top_n} indications:")
    print(top_indi)
    
    # Filter to only include reports with top indications
    filtered_df = merged_df[merged_df['indi_pt'].isin(top_indi.index)]
    filtered_df = filtered_df[filtered_df['indi_pt'] != 'Product used for unknown indication']
    
    print(f"\nNumber of reports matching top indications: {filtered_df.shape[0]}")
    return filtered_df

def run_full_analysis(data_dir, query_drug, min_age_yrs=0, max_age_yrs=100, top_n=10):

    print(f"Starting analysis for drug: {query_drug}")
    print(f"Age range: {min_age_yrs}-{max_age_yrs} years")
    print(f"Data directory: {data_dir}")
    print("-" * 50)
    
    # Load required files from directory
    drug_file = Path(data_dir) / "drug.csv"
    demo_file = Path(data_dir) / "demo.csv"
    outc_file = Path(data_dir) / "outc.csv"
    indi_file = Path(data_dir) / "indi.csv"
    
  
    drug_df = load_data(drug_file)
    demo_df = load_data(demo_file)
    
    outc_df = None
    indi_df = None
    
    if outc_file.exists():
        outc_df = load_data(outc_file)
        print(f"Loaded outcomes file: {outc_file}")
    else:
        print(f"Outcomes file not found: {outc_file} (skipping)")
    
    if indi_file.exists():
        indi_df = load_data(indi_file)
        print(f"Loaded indications file: {indi_file}")
    else:
        print(f"Indications file not found: {indi_file} (skipping)")
    
    # Filter drug reports
    query_drug_df = filter_drug_reports(drug_df, query_drug)
    if query_drug_df is None or query_drug_df.empty:
        print(f"No reports found for drug: {query_drug}")
        return
    
    # Merge with demogograh
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
        query_indications_df = extract_top_indications(merged_df, top_n)
    
    print(f"\nFinal dataset shape: {merged_df.shape}")
    print("Analysis complete")


def main():
    parser = argparse.ArgumentParser(description='Analyze pharmaceutical drug adverse event data')
    parser.add_argument('data_dir', help='Directory containing the CSV files (drug.csv, demo.csv, outc.csv, indi.csv)')
    parser.add_argument('query_drug', help='Drug name to search for')
    parser.add_argument('--min-age', type=int, default=0, help='Minimum age (default: 0)')
    parser.add_argument('--max-age', type=int, default=100, help='Maximum age (default: 100)')
    parser.add_argument('--top-indications', type=int, default=10, 
                       help='Number of top indications to analyze (default: 10)')
    
    args = parser.parse_args()
    
    # Run the analysis
    run_full_analysis(
        data_dir=args.data_dir,
        query_drug=args.query_drug,
        min_age_yrs=args.min_age,
        max_age_yrs=args.max_age,
        top_n=args.top_indications
    )


if __name__ == '__main__':
    main()