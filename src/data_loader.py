from src.utils import (
    get_available_downloaded_quarters,
    get_available_processed_quarters,
    convert_quarter_file_str,
)
from src.parse_quarters import ParseQuarters
import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path
from tqdm import tqdm
from src.preprocessing import preprocess

# suppress pandas warnings
import warnings

warnings.filterwarnings("ignore")


class FAERSDataLoader:
    """
    Loads the FAERS data for the given start and end years and quarters.

    Args:
        save_dir: str
        start_year: int
        end_year: int
        start_quarter: int
        end_quarter: int
        debug: bool
    """

    def __init__(
        self,
        start_year: int,
        end_year: int,
        start_quarter: int = 1,
        end_quarter: int = 4,
        save_dir: str = "data",
        debug: bool = False,
    ):
        self.save_dir = save_dir
        self.available_downloaded_quarters = get_available_downloaded_quarters(save_dir)

        # Parse the quarters and make sure they are available locally
        self.parsed_quarters = ParseQuarters(
            start_year, end_year, start_quarter, end_quarter
        )
        self.parsed_quarters.check_available_downloaded(save_dir)
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
            logger.error(
                f"Quarter {quarter} not found in {self.save_dir}/faers_reports"
            )
            raise ValueError(
                f"Quarter {quarter} not found in {self.save_dir}/faers_reports"
            )

        # Construct the file paths
        reac_file_path = Path(self.save_dir).joinpath(
            "faers_reports", quarter, f"REAC{convert_quarter_file_str(quarter)}.txt"
        )
        drug_file_path = Path(self.save_dir).joinpath(
            "faers_reports", quarter, f"DRUG{convert_quarter_file_str(quarter)}.txt"
        )
        demo_file_path = Path(self.save_dir).joinpath(
            "faers_reports", quarter, f"DEMO{convert_quarter_file_str(quarter)}.txt"
        )
        outc_file_path = Path(self.save_dir).joinpath(
            "faers_reports", quarter, f"OUTC{convert_quarter_file_str(quarter)}.txt"
        )
        ther_file_path = Path(self.save_dir).joinpath(
            "faers_reports", quarter, f"THER{convert_quarter_file_str(quarter)}.txt"
        )
        indi_file_path = Path(self.save_dir).joinpath(
            "faers_reports", quarter, f"INDI{convert_quarter_file_str(quarter)}.txt"
        )

        # Preprocess the data
        reac = preprocess(pd.read_csv(reac_file_path, sep="$"), "reac")
        drug = preprocess(pd.read_csv(drug_file_path, sep="$"), "drug")
        demo = preprocess(pd.read_csv(demo_file_path, sep="$"), "demo")
        outc = preprocess(pd.read_csv(outc_file_path, sep="$"), "outc")
        ther = preprocess(pd.read_csv(ther_file_path, sep="$"), "ther")
        indi = preprocess(pd.read_csv(indi_file_path, sep="$"), "indi")

        return reac, drug, demo, outc, ther, indi

    def load_quarters(self) -> None:
        """
        Load the data for the given start and end years and quarters.
        """
        for quarter in tqdm(self.parsed_quarters, desc="Loading quarters"):
            logger.info(f"Loading quarter: {quarter}")
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
        return (
            self.reac_data,
            self.drug_data,
            self.demo_data,
            self.outc_data,
            self.ther_data,
            self.indi_data,
        )

    def help(self):
        """
        List all available online quarters and print example message
        """
        print(
            f"Available locally downloaded quarters: {get_available_downloaded_quarters(self.base_save_dir)}"
        )
        print(f"Example usage: ")
        print(
            f"loader = FAERSDataLoader(save_dir='data', start_year=2023, end_year=2023, start_quarter=1, end_quarter=4, debug=True)"
        )
        print(
            f"loader.get_data() # Returns the reac, drug, demo, outc, ther, indi dataframes"
        )


def load_faers_data(
    save_dir: str,
    start_year: int,
    end_year: int,
    start_quarter: int,
    end_quarter: int,
    debug: bool = False,
):
    """
    Load the FAERS data for the given start and end years and quarters.
    """
    loader = FAERSDataLoader(
        start_year=start_year,
        end_year=end_year,
        start_quarter=start_quarter,
        end_quarter=end_quarter,
        save_dir=save_dir,
        debug=debug,
    )
    return loader.get_data()
