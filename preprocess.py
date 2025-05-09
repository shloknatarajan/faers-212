import pandas as pd
import numpy as np
import re

base_path = ''
drug = pd.read_csv(base_path + 'DRUG24Q4.txt', sep='$')
reac = pd.read_csv(base_path + 'REAC24Q4.txt', sep='$')
ther = pd.read_csv(base_path + 'THER24Q4.txt', sep='$')
indi = pd.read_csv(base_path + 'INDI24Q4.txt', sep='$')
rpsr = pd.read_csv(base_path + 'RPSR24Q4.txt', sep='$')
demo = pd.read_csv(base_path + 'DEMO24Q4.txt', sep='$')
outc = pd.read_csv(base_path + 'OUTC24Q4.txt', sep='$')

# Processes drug df
drug = drug[pd.notnull(drug['drugname'])]  # Drops Nulls
drug['drugname'] = drug['drugname'].str.strip().str.lower()  # Stips whitespace, Transforms to lowercase
drug = drug[~drug['drugname'].isin(['unknown'])]  # Drops unknowns
drug['drugname'] = drug['drugname'].str.replace('\\', '/')  # Standardizes slashes to '/'
drug['drugname'] = drug['drugname'].map(
    lambda x: x[:-1] if str(x).endswith(".") else x)  # Removes periods at the end of drug names

# Process reac df 
reac = reac[pd.notnull(reac['pt'])] # Drops Nulls
reac['pt'] = reac['pt'].str.strip().str.lower()  # Transforms to lowercase
reac = reac[~reac['pt'].isin(['unknown'])]  # Drops unknowns
reac['pt'] = reac['pt'].map(
    lambda x: x[:-1] if str(x).endswith(".") else x)  # Removes periods at the end of drug names

# Process demo df 
demo = demo[pd.notnull(demo['age'])]
demo = demo[demo.age_cod != 'dec'].reset_index(drop=True) 
demo['age'] = demo['age'].apply(pd.to_numeric, errors='coerce')
demo['age'] = np.where(demo['age_cod'] == 'MON', demo['age'] * 1 / 12, demo['age'])  # mounth
demo['age'] = np.where(demo['age_cod'] == 'WK', demo['age'] * 1 / 52, demo['age'])  # week
demo['age'] = np.where(demo['age_cod'] == 'DY', demo['age'] * 1 / 365, demo['age'])  # day
demo['age'] = np.where(demo['age_cod'] == 'HR', demo['age'] * 1 / 8760, demo['age'])  # hour
demo = demo.drop(['age_cod'], axis=1)

demo_latest = demo.sort_values('caseversion', ascending=False).drop_duplicates(subset='caseid', keep='last')

drug = pd.merge(drug, demo_latest, on='primaryid', how='left')

query_drug = 'aspirin' 

# Finds reports related to the query drug 
query_drug_df = drug[
    drug['drugname'].str.lower().str.contains(query_drug, na=False) |
    drug['prod_ai'].str.lower().str.contains(query_drug, na=False)
]

# Subsets to primary suspect drugs
query_drug_ps = query_drug_df[query_drug_df['role_cod'] == 'PS']

# Get AE counts for cases where query drug is mentioned
query_drug_ids = query_drug_df['primaryid'].unique()
query_drug_reac = reac[reac['primaryid'].isin(query_drug_ids)]
ae_counts = query_drug_reac['pt'].value_counts().reset_index()
ae_counts.columns = ['Adverse_Event', 'Count']

# Get AE counts for cases where query drug is the primary suspect 
ps_ids = query_drug_ps['primaryid'].unique()
ps_reac = reac[reac['primaryid'].isin(ps_ids)]
ps_ae_counts = ps_reac['pt'].value_counts().reset_index()
ps_ae_counts.columns = ['Adverse_Event', 'Count']

# Get AE counts for cases where query drug is not mentioned
non_query_drug = drug[~drug['primaryid'].isin(query_drug_ids)]
non_ps_drug = drug[~drug['primaryid'].isin(ps_ids)]
non_query_ids = non_query_drug['primaryid'].unique()
non_query_reac = reac[reac['primaryid'].isin(non_query_ids)]
non_ae_counts = non_query_reac['pt'].value_counts().reset_index()
non_ae_counts.columns = ['Adverse_Event', 'Count']

# Get AE counts for cases where query drug is not the primary suspect 
non_ps_ids = non_ps_drug['primaryid'].unique()
non_ps_reac = reac[reac['primaryid'].isin(non_ps_ids)]
ps_non_ae_counts = non_ps_reac['pt'].value_counts().reset_index()
ps_non_ae_counts.columns = ['Adverse_Event', 'Count']

ae_counts.columns = ['Adverse_Event', 'Count_query_drug']
non_ae_counts.columns = ['Adverse_Event', 'Count_non_query_drug']
ps_ae_counts.columns = ['Adverse_Event', 'Count_query_drug']
ps_non_ae_counts.columns = ['Adverse_Event', 'Count_non_query_drug']
           
print(ae_counts.head(5))
print(non_ae_counts.head(5))

# Merge AE counts for query drug and non-query drug
ae_comparison = pd.merge(
    ae_counts,
    non_ae_counts,
    on='Adverse_Event',
    how='outer'
)

# Filter to AEs with at least 3 reports for the query drug
ae_filtered = ae_comparison[
    (ae_comparison['Count_query_drug'].notna()) &
    (ae_comparison['Count_query_drug'] >= 3)
].copy()

print(ae_filtered.head(5)) 

# Merge AE counts for primary-suspect query drug and non-query drug
ps_comparison = pd.merge(
    ps_ae_counts,
    ps_non_ae_counts,
    on='Adverse_Event',
    how='outer'
)

# Filter to AEs with at least 3 reports for the query drug
ps_filtered = ps_comparison[
    (ps_comparison['Count_query_drug'].notna()) &
    (ps_comparison['Count_query_drug'] >= 3)
].copy()

print(ps_filtered.head(5))

# Calculates the number of reports that did not include a specific adverse event for both the query drug and non-query drugs
query_num = query_drug_ids.shape[0]
non_num = non_query_ids.shape[0]
ae_filtered['No_AE_query_drug'] = query_num - ae_filtered['Count_query_drug']
ae_filtered['No_AE_non_query_drug'] = non_num - ae_filtered['Count_non_query_drug']
ae_filtered

# Calculates the number of reports that did not include a specific adverse event for both the PS query drug and non-query drugs 
ps_num = ps_ids.shape[0]
ps_non_num = non_ps_ids.shape[0]
ps_filtered['No_AE_query_drug'] = ps_num - ps_filtered['Count_query_drug']
ps_filtered['No_AE_non_query_drug'] = ps_non_num - ps_filtered['Count_non_query_drug']
ps_filtered

from scipy.stats import chi2_contingency
import numpy as np

# Function to compute Odds Ratio (OR) and Confidence Interval (CI)
def compute_or_and_ci(a, b, c, d):
    # Add 0.5 to avoid zero counts
    a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5

    # Odds Ratio
    or_val = (a * d) / (b * c)

    # Log(OR) and standard error
    log_or = np.log(or_val)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)

    # Confidence Interval
    ci_low = np.exp(log_or - 1.96 * se)
    ci_high = np.exp(log_or + 1.96 * se)

    return or_val, ci_low, ci_high

# Function to compute Proportional Reporting Ratio (PRR), Standard Error (SE), and Confidence Interval (CI)
def compute_prr_and_ci(a, b, c, d):
    # Proportional Reporting Ratio (PRR)
    prr = (a / (a + b)) / (c / (c + d))

    # Standard Error (SE)
    se = np.sqrt(1/a + 1/c - 1/(a + b) - 1/(c + d))

    # Confidence Interval for PRR
    ln_prr = np.log(prr)
    ci_low = np.exp(ln_prr - 1.96 * se)
    ci_high = np.exp(ln_prr + 1.96 * se)

    return prr, se, ci_low, ci_high


# Function to add statistics (OR and PRR) to the DataFrame
def add_stats(df):
    p_values = []
    odds_ratios = []
    ci_lowers_or = []
    ci_uppers_or = []
    prr_values = []
    se_values_prr = []
    ci_lowers_prr = []
    ci_uppers_prr = []
    signals = []

    for _, row in df.iterrows():
        a = row['Count_query_drug']
        b = row['No_AE_query_drug']
        c = row['Count_non_query_drug']
        d = row['No_AE_non_query_drug']

        # Chi-squared test for independence
        _, p, _, _ = chi2_contingency([[a, b], [c, d]])
        p_values.append(p)

        # Odds Ratio (OR) and Confidence Interval (CI) for OR
        or_val, ci_low_or, ci_high_or = compute_or_and_ci(a, b, c, d)
        odds_ratios.append(or_val)
        ci_lowers_or.append(ci_low_or)
        ci_uppers_or.append(ci_high_or)

        # Proportional Reporting Ratio (PRR), SE, and Confidence Interval (CI) for PRR
        prr, se_prr, ci_low_prr, ci_high_prr = compute_prr_and_ci(a, b, c, d)
        prr_values.append(prr)
        se_values_prr.append(se_prr)
        ci_lowers_prr.append(ci_low_prr)
        ci_uppers_prr.append(ci_high_prr)

        # Signal criteria for PRR: PRR ≥ 2, A ≥ 3, and CI lower bound > 1
        signal = (prr >= 2) and (a >= 3) and (ci_low_prr > 1)
        signals.append(signal)

    # Add new columns for OR and PRR statistics
    df['p_value'] = p_values
    df['odds_ratio'] = odds_ratios
    df['ci_lower_or'] = ci_lowers_or
    df['ci_upper_or'] = ci_uppers_or
    df['prr'] = prr_values
    df['se_prr'] = se_values_prr
    df['ci_lower_prr'] = ci_lowers_prr
    df['ci_upper_prr'] = ci_uppers_prr
    df['signal'] = signals  # Signal column indicating significant PRR
    return df

ae_filtered = add_stats(ae_filtered)
ps_filtered = add_stats(ps_filtered) 

# Display the results
print(ae_filtered.head(10))


from statsmodels.stats.multitest import multipletests
ae_filtered_valid = ae_filtered[ae_filtered['p_value'].notna()].copy()
_, corrected_p_values, _, _ = multipletests(ae_filtered_valid['p_value'], alpha=0.05, method='fdr_bh')

ae_filtered_valid['corrected_p_value'] = corrected_p_values

ps_filtered_valid = ps_filtered[ps_filtered['p_value'].notna()].copy()
_, corrected_p_values, _, _ = multipletests(ps_filtered_valid['p_value'], alpha=0.05, method='fdr_bh')

ps_filtered_valid['corrected_p_value'] = corrected_p_values


