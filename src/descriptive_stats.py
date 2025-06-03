
from src.data_loader import FAERSData
import pandas as pd
from loguru import logger

def describe(data: pd.DataFrame | FAERSData, description_type: str):
    if description_type == 'age':
        if isinstance(data, FAERSData):
            return describe_age(data.demo_data)
        else:
            return describe_age(data)
    elif description_type == 'sex':
        if isinstance(data, FAERSData):
            return describe_sex(data.demo_data)
        else:
            return describe_sex(data)
    elif description_type == 'country':
        if isinstance(data, FAERSData):
            return describe_country(data.demo_data)
        else:
            return describe_country(data)
    elif description_type == 'severity':
        if isinstance(data, FAERSData):
            return describe_severity(data.outc_data)
        else:
            return describe_severity(data)
    elif description_type == 'delay':
        if isinstance(data, FAERSData):
            return describe_reporting_delay(data.demo_data)
        else:
            return describe_reporting_delay(data)
    elif description_type == 'all_demographics':
        if isinstance(data, FAERSData):
            return describe_all_demographics(data.demo_data)
        else:
            return describe_all_demographics(data)
    else:
        raise ValueError(f"Invalid description type: {description_type}")

def describe_all_demographics(demo_df):
    print("====== Demographic Information ======")
    print("Age:")
    print(describe_age(demo_df))
    print("\nSex:")
    print(describe_sex(demo_df))
    # print("\nCountry:")
    # print(describe_country(demo_df))
    print("\nReporting Delay:")
    print(describe_reporting_delay(demo_df))
    
def describe_age(demo_df):
    try:
        age_desc = demo_df['age'].describe(percentiles=[0.25, 0.5, 0.75])
        missing = demo_df['age'].isna().sum()
        
        return age_desc.to_frame(name='age'), {'missing_age_count': missing}
    except KeyError:
        logger.error("Age column not found in dataset")

def describe_sex(demo_df):
    try:
        counts = demo_df['sex'].value_counts(dropna=False)
        percentages = demo_df['sex'].value_counts(normalize=True, dropna=False) * 100
        return pd.DataFrame({'count': counts, 'percent': percentages.round(2)})
    except KeyError:
        logger.error("Sex column not found in dataset")

def describe_country(demo_df):
    try:
        country_counts = demo_df['occr_country'].value_counts(dropna=False).head(10)
        return country_counts.to_frame(name='report_count')
    except KeyError:
        logger.error("occr_country column not found in dataset")

def describe_severity(outc_df):
    try:
        # Count outcomes
        return outc_df['outc_labels'].value_counts(dropna=False).to_frame(name='count')
    except KeyError:
        logger.error("outc_labels column not found in dataset")

def describe_reporting_delay(demo_df):
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
    try:
        date_df['event_dt'] = pd.to_datetime(date_df['event_dt'], format='%Y%m%d', errors='coerce')
        date_df['fda_dt'] = pd.to_datetime(date_df['fda_dt'], format='%Y%m%d', errors='coerce')
    except Exception as e:
        logger.error(f"Error converting dates: {str(e)}")
        return None

    # Filter out rows where either is missing
    try:
        date_df = date_df.dropna(subset=['event_dt', 'fda_dt'])
    except Exception as e:
        logger.error(f"Error filtering missing dates: {str(e)}")
        return None

    # Compute delay
    try:
        date_df['reporting_delay'] = (date_df['fda_dt'] - date_df['event_dt']).dt.days
    except Exception as e:
        logger.error(f"Error computing reporting delay: {str(e)}")
        return None

    return date_df['reporting_delay'].describe(percentiles=[0.25, 0.5, 0.75])
