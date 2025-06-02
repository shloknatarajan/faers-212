#!/usr/bin/env python3
import argparse
import pandas as pd
import sys
from pathlib import Path

"""Load CSV data"""
def load_data(csv_path):
    try:
        return pd.read_csv(csv_path, low_memory=False)
    except Exception as e:
        print(f"Error loading CSV file: {e}", file=sys.stderr)
        sys.exit(1)


def describe_age(demo_df):
    if 'age' not in demo_df.columns:
        return None, {'error': 'Age column not found in dataset'}
    
    age_desc = demo_df['age'].describe(percentiles=[0.25, 0.5, 0.75])
    missing = demo_df['age'].isna().sum()
    
    return age_desc.to_frame(name='age'), {'missing_age_count': int(missing)}


def describe_sex(demo_df):
    if 'sex' not in demo_df.columns:
        return {'error': 'Sex column not found in dataset'}
    
    counts = demo_df['sex'].value_counts(dropna=False)
    percentages = demo_df['sex'].value_counts(normalize=True, dropna=False) * 100
    return pd.DataFrame({'count': counts, 'percent': percentages.round(2)})

#return top 10 countries by report count
def describe_country(demo_df):
    if 'occr_country' not in demo_df.columns:
        return {'error': 'occr_country column not found in dataset'}
    
    country_counts = demo_df['occr_country'].value_counts(dropna=False).head(10)
    return country_counts.to_frame(name='report_count')


def describe_severity(outc_df):
    # Extract only the outcome columns like 'outc_cod1', 'outc_cod2', ...
    outcome_cols = [col for col in outc_df.columns if col.startswith('outc_cod')]
    
    if not outcome_cols:
        return {'error': 'No outcome columns (outc_cod*) found in dataset'}
    
    # Flatten to long format
    outc_long = outc_df[outcome_cols].melt(value_name='outc_cod')
    
    # Drop missing values
    outc_long = outc_long.dropna(subset=['outc_cod'])

    # Map to human-readable labels
    outcome_labels = {
        'DE': 'Death',
        'LT': 'Life-Threatening',
        'HO': 'Hospitalization',
        'DS': 'Disability',
        'CA': 'Congenital Anomaly',
        'RI': 'Required Intervention',
        'OT': 'Other Serious'
    }
    outc_long['outcome'] = outc_long['outc_cod'].map(outcome_labels)

    # Count outcomes
    return outc_long['outcome'].value_counts(dropna=False).to_frame(name='count')


#Report delay calculation
def describe_reporting_delay(demo_df):
    required_cols = ['event_dt', 'fda_dt']
    missing_cols = [col for col in required_cols if col not in demo_df.columns]
    if missing_cols:
        return {'error': f'Required columns not found: {missing_cols}'}
    
    date_df = demo_df.copy()

    # Clean up float-to-int, convert to string, and extract valid 8-digit dates
    date_df['event_dt'] = (
        date_df['event_dt']
        .dropna()
        .astype(float)
        .astype(int)
        .astype(str)
        .str.extract(r'(\d{8})')[0]
    )
    date_df['fda_dt'] = (
        date_df['fda_dt']
        .dropna()
        .astype(float)
        .astype(int)
        .astype(str)
        .str.extract(r'(\d{8})')[0]
    )

    # Convert to datetime
    date_df['event_dt'] = pd.to_datetime(date_df['event_dt'], format='%Y%m%d', errors='coerce')
    date_df['fda_dt'] = pd.to_datetime(date_df['fda_dt'], format='%Y%m%d', errors='coerce')

    # Filter out rows where either is missing
    date_df = date_df.dropna(subset=['event_dt', 'fda_dt'])

    if len(date_df) == 0:
        return {'error': 'No valid date pairs found for delay calculation'}

    # Compute delay
    date_df['reporting_delay'] = (date_df['fda_dt'] - date_df['event_dt']).dt.days

    return date_df['reporting_delay'].describe(percentiles=[0.25, 0.5, 0.75])


#General describe of the dataset
def describe_overall(demo_df):
    return demo_df.describe(include='all')

#print the result based on description type
def print_result(result, description_type):

    if isinstance(result, dict) and 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    if description_type == 'age':
        df_part, dict_part = result
        if df_part is not None:
            print("Age Summary:")
            print(df_part)
        print("Missing Age Count:")
        print(dict_part)
    else:
        print(f"{description_type.title()} Summary:")
        print(result)


def main():
    parser = argparse.ArgumentParser(description='Describe pharmaceutical adverse event data')
    parser.add_argument('data_dir', help='Directory containing the CSV files')
    parser.add_argument('description_type', choices=[
        'age', 'sex', 'country', 'severity', 'delay', 'overall'
    ], help='Type of description to generate')
    
    args = parser.parse_args()
    
    data_path = Path(args.data_dir)
    
    #Decide file in folder based on description type
    if args.description_type == 'severity':
        csv_file = data_path / 'outc.csv'
    else:
        # For age, sex, country, delay, overall - use demo file
        csv_file = data_path / 'demo.csv'
    
    if not csv_file.exists():
        print(f"Error: Required file not found: {csv_file}", file=sys.stderr)
        sys.exit(1)
    

    df = load_data(csv_file)
    
    # Execute the requested description
    if args.description_type == 'age':
        result = describe_age(df)
    elif args.description_type == 'sex':
        result = describe_sex(df)
    elif args.description_type == 'country':
        result = describe_country(df)
    elif args.description_type == 'severity':
        result = describe_severity(df)
    elif args.description_type == 'delay':
        result = describe_reporting_delay(df)
    elif args.description_type == 'overall':
        result = describe_overall(df)
    
    # Print
    print_result(result, args.description_type)


if __name__ == '__main__':
    main()