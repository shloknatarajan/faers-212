from loguru import logger
"""
Parameters:
- Drug Name to Search for
- AE Term to Search for 
- The quarters to search within
- Stats test to run? Once you save contingency table any stats test can be run

To Manage:
- Drug name
- AE Term
- Merged dataframe that gets filtered down by drug and AE term
- Contingency table
"""

class Pipeline:
    def __init__(self, drug_name: str, ae_term: str, quarters: list[str]):
        self.drug_name = drug_name
        self.ae_term = ae_term
        self.quarters = quarters
        self.working_df = None
        self.contingency_table = None

    def check_data_exists(self):
        """
        Check if the merged/cleaned dataframe exists in the data/processed_faers/ directory
        """
        pass

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
