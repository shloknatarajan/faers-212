
from src.utils import get_available_downloaded_quarters, get_available_processed_quarters, convert_quarter_file_str
from src.parse_quarters import ParseQuarters
import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path
from tqdm import tqdm

class FAERSDataLoader:
    """
    Loads the FAERS data for the given start and end years and quarters.

    Args:
        data_dir: str
        start_year: int
        end_year: int
        start_quarter: int
        end_quarter: int
        debug: bool
    """
    def __init__(self, data_dir: str, start_year: int, end_year: int, start_quarter: int, end_quarter: int, debug: bool = False):
        self.data_dir = data_dir
        self.available_processed_quarters = get_available_processed_quarters(data_dir)

        # Parse the quarters and make sure they are available locally
        self.parsed_quarters = ParseQuarters(start_year, end_year, start_quarter, end_quarter)
        self.parsed_quarters.check_available_downloaded(data_dir)
        self.parsed_quarters = self.parsed_quarters.get_quarters()

        # Initialize dataframes
        self.reac_data = pd.DataFrame()
        self.drug_data = pd.DataFrame()
        self.demo_data = pd.DataFrame()
        self.outc_data = pd.DataFrame()
        self.ther_data = pd.DataFrame()
        self.indi_data = pd.DataFrame()

        # Load the data
        self.load_quarters()

    def load_single_quarter(self, quarter: str):
        """
        Load the data for the given quarter.
        """
        if quarter not in self.available_downloaded_quarters:
            logger.error(f"Quarter {quarter} not found in {self.data_dir}/faers_reports")
            raise ValueError(f"Quarter {quarter} not found in {self.data_dir}/faers_reports")
        
        # Load the data
        reac_file = Path(self.data_dir).joinpath("faers_reports", quarter, f"REAC{convert_quarter_file_str(quarter)}.txt")
        drug_file = Path(self.data_dir).joinpath("faers_reports", quarter, f"DRUG{convert_quarter_file_str(quarter)}.txt")
        demo_file = Path(self.data_dir).joinpath("faers_reports", quarter, f"DEMO{convert_quarter_file_str(quarter)}.txt")
        outc_file = Path(self.data_dir).joinpath("faers_reports", quarter, f"OUTC{convert_quarter_file_str(quarter)}.txt")
        ther_file = Path(self.data_dir).joinpath("faers_reports", quarter, f"THER{convert_quarter_file_str(quarter)}.txt")
        indi_file = Path(self.data_dir).joinpath("faers_reports", quarter, f"INDI{convert_quarter_file_str(quarter)}.txt")

        # Preprocess the data
        reac = preprocess(pd.read_csv(reac_file), 'reac')
        drug = preprocess(pd.read_csv(drug_file), 'drug')
        demo = preprocess(pd.read_csv(demo_file), 'demo')
        outc = preprocess(pd.read_csv(outc_file), 'outc')
        ther = preprocess(pd.read_csv(ther_file), 'ther')
        indi = preprocess(pd.read_csv(indi_file), 'indi')

        return reac, drug, demo, outc, ther, indi
    
    def load_quarters(self) -> None:
        """
        Load the data for the given start and end years and quarters.
        """
        for quarter in tqdm(self.parsed_quarters, desc="Loading quarters"):
            logger.debug(f"Loading quarter: {quarter}")
            reac, drug, demo, outc, ther, indi = self.load_single_quarter(quarter)
            self.reac_data = pd.concat([self.reac_data, reac])
            self.drug_data = pd.concat([self.drug_data, drug])
            self.demo_data = pd.concat([self.demo_data, demo])
            self.outc_data = pd.concat([self.outc_data, outc])
            self.ther_data = pd.concat([self.ther_data, ther])
            self.indi_data = pd.concat([self.indi_data, indi])
    
    def get_data(self):
        """
        Get the data for the given start and end years and quarters.
        """
        return self.reac_data, self.drug_data, self.demo_data, self.outc_data, self.ther_data, self.indi_data
    
    def help(self):
        """
        List all available online quarters and print example message
        """
        print(f"Available locally downloaded quarters: {get_available_downloaded_quarters(self.base_save_dir)}")
        print(f"Example usage: ")
        print(f"loader = FAERSDataLoader(data_dir='data', start_year=2023, end_year=2023, start_quarter=1, end_quarter=4, debug=True)")
        print(f"loader.get_data() # Returns the reac, drug, demo, outc, ther, indi dataframes")
        

def preprocess(df: pd.DataFrame, type: str) -> pd.DataFrame:
    """
    Factory function to preprocess the dataframe for the given type.

    Args:
        df: pd.DataFrame
        type: str
    Returns:
        pd.DataFrame (with preprocessed data)
    """
    if type == 'reac':
        return preprocess_reac_df(df)
    elif type == 'drug':
        return preprocess_drug_df(df)
    elif type == 'demo':
        return preprocess_demo_df(df)
    elif type == 'outc':
        return preprocess_outc_df(df)
    elif type == 'ther':
        return preprocess_ther_df(df)
    elif type == 'indi':
        return preprocess_indi_df(df)
    else:
        logger.error(f"Invalid type: {type}. Must be one of {['reac', 'drug', 'demo', 'outc', 'ther', 'indi']}")
        raise ValueError(f"Invalid type: {type}. Must be one of {['reac', 'drug', 'demo', 'outc', 'ther', 'indi']}")

def preprocess_drug_df(drug):
    drug = drug[['primaryid', 'caseid', 'role_cod', 'drugname', 'prod_ai', 'drug_seq', 'dechal', 'rechal']]
    
    print("Starting number of reports in 'drug' file: ", drug.shape[0]) 
    
    drug = drug[drug['role_cod'] == 'PS']
    print("Number of reports in the 'drug' file where drug is the primary suspect: ", drug.shape[0]) 

    drug = drug[pd.notnull(drug['drugname'])]  # Drops Nulls
    drug = drug[~drug['drugname'].isin(['unknown'])]  # Drops unknowns
    
    print("Number of reports in the 'drug' file after unknown/null drugs are removed: ", drug.shape[0]) 
    
    drug['drugname'] = drug['drugname'].str.strip().str.lower()  # Stips whitespace, Transforms to lowercase
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

    demo = demo[['primaryid', 'caseid', 'caseversion', 'age_cod', 'age', 'sex', 'wt', 'fda_dt', 'event_dt']] 
    
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


