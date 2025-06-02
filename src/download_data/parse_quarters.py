from typing import List
from loguru import logger

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
        self.validate_params()
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
    
    def validate_params(self):
        """
        Validate the input
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