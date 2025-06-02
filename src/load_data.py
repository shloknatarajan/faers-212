
from src.utils import get_available_raw_quarters, get_available_processed_quarters
from src.parse_quarters import ParseQuarters
class FAERSDataLoader:
    def __init__(self, data_dir: str, start_year: int, end_year: int, start_quarter: int, end_quarter: int):
        self.data_dir = data_dir
        self.available_raw_quarters = get_available_raw_quarters(data_dir)
        self.available_processed_quarters = get_available_processed_quarters(data_dir)
        self.parsed_quarters = ParseQuarters(start_year, end_year, start_quarter, end_quarter).parsed_quarters
        

    def load_data(self):
        """
        Load the data for the given start and end years and quarters.
        """
        pass

    def preprocess_quarter(self, quarter: str):
        """
        Preprocess the data for the given quarter.
        """
        pass
    