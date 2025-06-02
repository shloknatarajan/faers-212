from typing import List
from loguru import logger
from src.utils.supported_quarters import get_available_online_quarters, get_available_downloaded_quarters, get_available_processed_quarters

class ParseQuarters:
    """
    Class to perform initial parsing and validation of the start and end years and quarters
    Args:
        start_year: int = None
        end_year: int = None
        start_quarter: int = 1
        end_quarter: int = 4
        debug: bool = False
    """
    def __init__(self, start_year: int = None, end_year: int = None, start_quarter: int = 1, end_quarter: int = 4, debug: bool = False):
        self.start_year = start_year
        self.end_year = end_year
        self.start_quarter = start_quarter
        self.end_quarter = end_quarter
        self.basic_validation()
        self.parsed_quarters = self.parse_quarter_strings(debug=debug)

    def parse_quarter_strings(self, debug: bool = False) -> List[str]:
        """
        Turn start year, end year, start quarter, end quarter into a list of quarters
        """
        quarters = []
        for year in range(self.start_year, self.end_year + 1):
            for quarter in range(self.start_quarter, self.end_quarter + 1):
                quarters.append(f"{year}Q{quarter}")
        if debug:
            logger.debug(f"Parsed quarters: {quarters}")
        return quarters
    
    def basic_validation(self):
        """
        Validate the input parameters
        """
        if self.start_year is None:
            logger.error("Start year is required")
            raise ValueError("Start year is required")
        if self.end_year is None:
            logger.error("End year is required")
            raise ValueError("End year is required")
        if self.start_quarter is None:
            logger.error("Start quarter is required")
            raise ValueError("Start quarter is required")
        if self.end_quarter is None:
            logger.error("End quarter is required")
            raise ValueError("End quarter is required")
        if self.start_year > self.end_year:
            logger.error("Start year must be before end year")
            raise ValueError("Start year must be before end year")
        if self.start_quarter > self.end_quarter:
            logger.error("Start quarter must be before end quarter")
            raise ValueError("Start quarter must be before end quarter")
        return None
    
    def get_quarters(self) -> List[str]:
        """
        Get the list of parsed quarter strings
        """
        return self.parsed_quarters
    
    def check_available_online(self) -> None:
        """
        Check if the quarters are available online
        """
        missing_quarters = []
        available_online_quarters = get_available_online_quarters()
        for quarter in self.parsed_quarters:
            if quarter not in available_online_quarters:
                missing_quarters.append(quarter)
        if missing_quarters:
            logger.error(f"Quarters {missing_quarters} not found on FAERS Download Page (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)")
            raise ValueError(f"Quarters {missing_quarters} not found in {available_online_quarters.keys()}")
        logger.info(f"All quarters {self.parsed_quarters} found on FAERS Download Page (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)")

    def check_available_downloaded(self, save_dir: str = "data") -> None:
        """
        Check if the quarters are available in the save_dir/faers_reports directory
        """
        missing_quarters = []
        available_downloaded_quarters = get_available_downloaded_quarters(save_dir)
        for quarter in self.parsed_quarters:
            if quarter not in available_downloaded_quarters:
                missing_quarters.append(quarter)
        if missing_quarters:
            logger.error(f"Quarters {missing_quarters} not found in {save_dir}/faers_reports")
            raise ValueError(f"Quarters {missing_quarters} not found in {save_dir}/faers_reports")
        logger.info(f"All quarters {self.parsed_quarters} found in {save_dir}/faers_reports")

    def check_available_processed(self, save_dir: str = "data") -> None:
        """
        Check if the quarters are available in the processed data directory
        """
        missing_quarters = []
        available_processed_quarters = get_available_processed_quarters(save_dir)
        for quarter in self.parsed_quarters:
            if quarter not in available_processed_quarters:
                missing_quarters.append(quarter)
        if missing_quarters:
            logger.error(f"Quarters {missing_quarters} not found in {save_dir}/processed")
            raise ValueError(f"Quarters {missing_quarters} not found in {save_dir}/processed")
        logger.info(f"All quarters {self.parsed_quarters} found in {save_dir}/processed")
