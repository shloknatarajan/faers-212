from src.data_loader import FAERSData
from src.drug_search import filter_by_drug_name
from src.meddra_search import filter_by_preferred_terms
class FilterExperiment:
    """
    Experiment class to manage a search run. Each experiment instance is a single search run.
    Should take in a preprocessed dataframe with all the tables and do needed filtering
    and create a contingency table.
    Should consider pydantic for input validation / taking a config for setup

    Would make sense to accept a FAERSData class instead of a bunch of dataframes
    """

    def __init__(self, faers_data: FAERSData):
        self.working_df = faers_data.copy()
        self.contingency_table = None
        self.original_data = None
        self.drug_term = None
        self.ae_term = None


    def filter_by_drug_name(self, drug_term: str):
        """
        Filter the working dataframe by the drug name
        """
        self.drug_term = drug_term
        self.working_df = filter_by_drug_name(self.working_df.drug_data, drug_term)

    def filter_by_preferred_term(self, ae_term: str):
        """
        Filter the working dataframe by the preferred term
        """
        self.ae_term = ae_term
        self.working_df = filter_by_preferred_term(self.working_df, ae_term)

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
