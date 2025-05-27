from loguru import logger
import pandas as pd
from src.utils import get_raw_quarters, get_processed_quarters, format_quarter

"""
Parameters:
- Drug Name to Search for
- AE Term to Search for 
- The quarters to search within
- Stats test to run? Once you save contingency table any stats test can be run

Let's separate data and the search process

To Manage:
- Drug name
- AE Term
- Merged dataframe that gets filtered down by drug and AE term
- Contingency table
"""
class FAERSData:
    def __init__(self, quarters: list[str]):
        self.quarters = quarters
        self.working_df = None
        self.available_processed_quarters = get_processed_quarters()
        self.available_raw_quarters = get_raw_quarters()
        self.missing_processed_quarters = self.check_missing_data()

    def merge_processed_quarters(self):
        """
        Merge the processed quarters into a single dataframe. Helper method for setup_data
        """
        pass

    def convert_raw_quarters(self):
        """
        Convert the raw quarters into processed quarters. Helper method for setup_data
        """
        if len(self.missing_processed_quarters) > 0:
            logger.warning(f"Missing processed quarters: {self.missing_processed_quarters}. Converting raw quarters to processed quarters.")
        for quarter in self.missing_processed_quarters:
            

    def check_missing_data(self) -> list[str]:
        """
        Check if the dataframe exists in the data/processed_faers/ directory. Helper method for setup_data
        1. Sets the attributes for available_processed_quarters and available_raw_quarters
        2. Returns a list of missing quarters
        """
        missing_processed_quarters = []
        missing_raw_quarters = []
        for quarter in self.quarters:
            if quarter not in self.available_processed_quarters:
                if quarter in self.available_raw_quarters:
                    missing_processed_quarters.append(quarter)
                else:
                    missing_raw_quarters.append(quarter)
        if len(missing_raw_quarters) > 0:
            error_message = f"Missing raw quarters: {missing_raw_quarters}. Please download the data first."
            logger.error(error_message)
            raise ValueError(error_message)

        return missing_processed_quarters
    
    def setup_data(self):
        """
        Create the working dataframe from the quarters param
        1. Check if the dataframe exists in the data/processed_faers/ directory
        2. If it does, load the dataframes and merge them
        3. If it doesn't, check if the raw dataframes exist in the data/raw_faers/ directory
        4. If they do, merge them and save the processed dataframe to the data/processed_faers/ directory
        5. If they don't, raise an error
        """
        pass

    def preprocess_data(self):
        """
        Preprocess the dataframe
        """
        pass
    
    def get_data(self) -> pd.DataFrame:
        """
        Returns the working dataframe (getter method)
        """
        return self.working_df


class Pipeline:
    """
    Pipeline class to manage a search run. Each pipeline instance is a single search run.
    """
    def __init__(self, drug_name: str, ae_term: str):
        self.drug_name = drug_name
        self.ae_term = ae_term
        self.working_df = None
        self.contingency_table = None
        self.original_data = None

    def set_data(self, data: FAERSData | list[str]):
        """
        Set the data
        """
        if isinstance(data, FAERSData):
            self.original_data = data
        elif isinstance(data, list):
            self.original_data = FAERSData(data)
        else:
            raise ValueError("Invalid data type")

    def filter_by_drug_name(self):
        """
        Filter the working dataframe by the drug name
        """
        pass

    def filter_by_ae_term(self):
        """
        Filter the working dataframe by the AE term
        """
        pass
    
    def create_contingency_table(self):
        """
        Create the contingency table using the working dataframe
        """
        pass
    
    def run_stats_test(self):
        """
        Run the stats test on the contingency table
        """
        pass
    
    def run(self):
        pass
