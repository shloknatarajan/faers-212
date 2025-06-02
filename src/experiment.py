from src.data_loader import FAERSDataLoader

class Experiment:
    """
    Experiment class to manage a search run. Each experiment instance is a single search run.
    Should take in a preprocessed dataframe with all the tables and do needed filtering
    and create a contingency table.
    Should consider pydantic for input validation / taking a config for setup

    Would make sense to accept a FAERSData class instead of a bunch of dataframes
    """
    def __init__(self, drug_name: str, ae_term: str):
        self.drug_name = drug_name
        self.ae_term = ae_term
        self.working_df = None
        self.contingency_table = None
        self.original_data = None

    def set_data(self, data: FAERSDataLoader):
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
