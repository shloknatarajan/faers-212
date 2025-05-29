import pandas as pd
import numpy as np


def load_filtered_mapping(mapping_path, drug_df):
    
    # Load full mapping
    print(f"Loading RxNorm mapping from: {mapping_path}")
    mapping = pd.read_csv(mapping_path)

    # Get unique drugnames from FAERS drug table for given time frame
    faers_drugnames = drug_df['drugname'].dropna().unique()

    # Only keep relevant names to minimize merge time
    mapping = mapping[mapping['drugname'].isin(faers_drugnames)]

    return mapping


def preprocess_drug_df(drug, name_mapping):
    drug = drug[['primaryid', 'caseid', 'role_cod', 'drugname', 'prod_ai', 'drug_seq', 'dechal', 'rechal']]
    
    print("Starting number of reports in 'drug' file: ", drug.shape[0]) 
    
    drug = drug[drug['role_cod'] == 'PS']
    print("Number of reports in the 'drug' file where drug is the primary suspect: ", drug.shape[0]) 

    drug = drug[pd.notnull(drug['drugname'])]  # Drops Nulls
    drug = drug[~drug['drugname'].isin(['unknown'])]  # Drops unknowns
    
    print("Number of reports in the 'drug' file after unknown/null drugs are removed: ", drug.shape[0]) 
    
    drug['drugname'] = drug['drugname'].str.strip().str.lower()  # Stips whitespace, Transforms to lowercase

    # Add in rxnorm mapping results
    drug = drug.merge(
        name_mapping[['drugname', 'best_match_name', 'rxnorm_name']],
        how='left',
        on='drugname'
    )
    
    drug['drugname'] = drug['drugname'].str.replace('\\', '/')  # Standardizes slashes to '/'
    drug['drugname'] = drug['drugname'].map(
        lambda x: x[:-1] if str(x).endswith(".") else x)  # Removes periods at the end of drug names

    drug['prod_ai'] = drug['prod_ai'].str.lower()
    drug = drug.drop_duplicates(subset=['primaryid'], keep='first')

    
    return drug

def preprocess_reac_df(reac):
    print("Starting number of reports in 'reac' file: ", reac.shape[0]) 

    reac = reac[pd.notnull(reac['pt'])] # Drops Nulls
    reac = reac[~reac['pt'].isin(['unknown'])]  # Drops unknowns
    
    print("Number of reports in the 'reac' file after unknown/null reacs are removed: ", reac.shape[0]) 

    reac['pt'] = reac['pt'].str.strip().str.lower()  # Transforms to lowercase
    reac['pt'] = reac['pt'].map(
        lambda x: x[:-1] if str(x).endswith(".") else x)  # Removes periods at the end of drug names

    return reac

def preprocess_demo_df(demo):
    print("Starting number of reports in 'demo' file: ", demo.shape[0]) 

    demo = demo[['primaryid', 'caseid', 'caseversion', 'age_cod', 'age', 'sex', 'wt', 'fda_dt', 'event_dt', 'occr_country']]
    
    # If multiple reports have the same primary id and case id, keep the most recent one 
    demo = demo.sort_values(by=['caseid', 'fda_dt', 'primaryid'], ascending=[True, False, False])
    demo = demo.drop_duplicates(subset=['caseid'], keep='first')
    
    print("Number of reports in the 'demo' file after duplicate primary/case id combos are removed: ", demo.shape[0]) 

    demo = demo[pd.notnull(demo['age'])]
    demo = demo[demo.age_cod != 'dec'].reset_index(drop=True)
    demo['age'] = demo['age'].apply(pd.to_numeric, errors='coerce')
    demo['age'] = np.where(demo['age_cod'] == 'MON', demo['age'] * 1 / 12, demo['age'])  # mounth
    demo['age'] = np.where(demo['age_cod'] == 'WK', demo['age'] * 1 / 52, demo['age'])  # week
    demo['age'] = np.where(demo['age_cod'] == 'DY', demo['age'] * 1 / 365, demo['age'])  # day
    demo['age'] = np.where(demo['age_cod'] == 'HR', demo['age'] * 1 / 8760, demo['age'])  # hour
    demo = demo.drop(['age_cod'], axis=1)

    print("Number of reports in the 'demo' file after unknown/invalid ages are removed: ", demo.shape[0]) 


    return demo

def preprocess_outc_df(outc): 
    print("Starting number of reports in 'outc' file: ", reac.shape[0]) 

    outc['outc_number'] = outc.groupby(['primaryid', 'caseid']).cumcount() + 1
    
    outc_pivot = outc.pivot(index=['primaryid', 'caseid'], 
                        columns='outc_number', 
                        values='outc_cod')
    
    # Renames the columns to outc_cod1, outc_cod2, ...
    outc_pivot.columns = [f'outc_cod{i}' for i in outc_pivot.columns]
    outc_final = outc_pivot.reset_index()
    
    return outc_final

def preprocess_ther_df(ther):
    print("Starting number of reports in 'ther' file: ", ther.shape[0]) 

    ther = ther[['primaryid', 'caseid', 'start_dt', 'dsg_drug_seq']] 

    ther = ther.rename(columns={'dsg_drug_seq': 'drug_seq'})

    return ther

def preprocess_indi_df(indi):
    print("Starting number of reports in 'indi' file: ", indi.shape[0]) 

    indi = indi.rename(columns={'indi_drug_seq': 'drug_seq'})

    return indi



def run_preprocess_pipeline(input_dir, output_dir, drug_name = None):
  
    # load filtered RxNorm mapping - assume exists
    mapping_path = 'data_files/full_final_mapping.csv'
    name_mapping = load_filtered_mapping(mapping_path, drug_name)

    # Load dataframes
    demo = pd.read_csv(input_dir / "demo.csv")
    drug = pd.read_csv(input_dir / "drug.csv")
    reac = pd.read_csv(input_dir / "reac.csv")
    ther = pd.read_csv(input_dir / "ther.csv")
    outc = pd.read_csv(input_dir / "outc.csv")
    indi = pd.read_csv(input_dir / "indi.csv")



    # Preprocess drug dataframe
    demo = preprocess_demo_df(demo)
    drug = preprocess_drug_df(drug, name_mapping)
    reac = preprocess_reac_df(reac)
    ther = preprocess_ther_df(ther)
    outc = preprocess_outc_df(outc)
    indi = preprocess_indi_df(indi)







