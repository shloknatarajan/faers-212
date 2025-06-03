from src.data_loader import FAERSData


class Experiment:
    """
    Experiment class to manage a search run. Each experiment instance is a single search run.
    Should take in a preprocessed dataframe with all the tables and do needed filtering
    and create a contingency table.
    Should consider pydantic for input validation / taking a config for setup

    Would make sense to accept a FAERSData class instead of a bunch of dataframes
    """

    def __init__(self, faers_data: FAERSData):
        self.faers_data = faers_data.copy()
        self.contingency_table = None
        self.original_data = None
        self.drug_term = None
        self.ae_term = None

    def set_drug(self, drug_term: str):
        """
        Set the drug term for the experiment
        """
        self.drug_term = drug_term

    def set_ae(self, ae_term: str):
        """
        Set the AE term for the experiment
        """
        self.ae_term = ae_term

    def filter_by_drug_name(self):
        """
        Filter the working dataframe by the drug name
        """
        self.working_df = pt_filter(self.faers_data.drug_data, [self.drug_term])

    def filter_by_preferred_term(self):
        """
        Filter the working dataframe by the preferred term
        """
        self.working_df = pt_filter(self.working_df, [self.ae_term])

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
