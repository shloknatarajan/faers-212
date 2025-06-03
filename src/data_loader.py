from src.utils import (
    get_available_downloaded_quarters,
    get_available_processed_quarters,
    convert_quarter_file_str,
)
from src.aggregations import aggregate_faers_table
import pickle
import hashlib
from typing import Optional
from src.parse_quarters import ParseQuarters
import pandas as pd
import numpy as np
from loguru import logger
from pathlib import Path
from tqdm import tqdm
from src.preprocessing import preprocess
from dataclasses import dataclass
from functools import cached_property

# suppress pandas warnings
import warnings

warnings.filterwarnings("ignore")

@dataclass
class FAERSData:
    """
    Class to hold the FAERS dataframes with caching capabilities.
    
    Attributes:
        reac_data (pd.DataFrame): DataFrame containing reaction data
        drug_data (pd.DataFrame): DataFrame containing drug data
        demo_data (pd.DataFrame): DataFrame containing demographic data
        outc_data (pd.DataFrame): DataFrame containing outcome data
        ther_data (pd.DataFrame): DataFrame containing therapy data
        indi_data (pd.DataFrame): DataFrame containing indication data
    """
    reac_data: pd.DataFrame
    drug_data: pd.DataFrame
    demo_data: pd.DataFrame
    outc_data: pd.DataFrame
    ther_data: pd.DataFrame
    indi_data: pd.DataFrame
    rpsr_data: pd.DataFrame
    
    def save_to_cache(self, cache_path: Path) -> None:
        """Save the FAERSData object to cache"""
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(self, f)
    
    @classmethod
    def load_from_cache(cls, cache_path: Path) -> Optional['FAERSData']:
        """Load FAERSData object from cache if it exists"""
        try:
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
        return None

    @cached_property
    def merged(self):
        """
        Merge the data for the given start and end years and quarters.
        """
        # === Load Data ===
        logger.info(f"Merging dataframes")

        # === Start with drug_data ===
        merged = self.drug_data.copy()

        # === Merge with demo_data ===
        logger.debug(f"Merging with demo_data")
        merged = merged.merge(self.demo_data, on=["primaryid", "caseid"], how="left")

        # === Merge and aggregate reaction_data ===
        logger.debug(f"Merging with reaction_data")
        reac_agg = aggregate_faers_table(self.reac_data, 'reac', debug=False)
        merged = merged.merge(reac_agg, on=["primaryid", "caseid"], how="left")

        # === Merge outcome_data ===
        logger.debug(f"Merging with outcome_data")
        merged = merged.merge(self.outc_data, on=["primaryid", "caseid"], how="left")

        # === Merge and aggregate rpsr_data ===
        logger.debug(f"Merging with rpsr_data")
        rpsr_agg = aggregate_faers_table(self.rpsr_data, 'rpsr', debug=False)
        merged = merged.merge(rpsr_agg, on=["primaryid", "caseid"], how="left")

        # === Merge and aggregate therapy_data ===
        logger.debug(f"Merging with therapy_data")
        ther_agg = aggregate_faers_table(self.ther_data, 'ther', debug=False)
        merged = merged.merge(ther_agg, on=["primaryid", "caseid"], how="left")

        # === Final Output ===
        logger.info(f"Final merged shape: {merged.shape}")
        return merged

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
        use_cache: bool
    """

    def __init__(
        self,
        start_year: int,
        end_year: int,
        start_quarter: int = 1,
        end_quarter: int = 4,
        save_dir: str = "data",
        debug: bool = False,
        use_cache: bool = True,
    ):
        self.save_dir = save_dir
        self.use_cache = use_cache
        self.cache_dir = Path(save_dir) / "cache"
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
        self.rpsr_data = pd.DataFrame()

        # Generate cache key based on quarters
        self.cache_key = self._generate_cache_key()
        self.cache_path = self.cache_dir / f"{self.cache_key}.pkl"
        
        # Try loading from cache first, then fall back to loading quarters
        if not self._load_from_cache():
            self.load_quarters()

    def load_single_quarter(self, quarter: str):
        """
        Load the data for the given quarter.
        Args:
            quarter: str (e.g. "2024Q1")
        """
        return load_single_quarter(quarter, self.save_dir)

    def load_quarters(self) -> None:
        """
        Load the data for the given start and end years and quarters.
        """
        for quarter in tqdm(self.parsed_quarters, desc="Loading quarters"):
            logger.info(f"Loading quarter: {quarter}")
            reac, drug, demo, outc, ther, indi, rpsr = self.load_single_quarter(quarter)
            self.reac_data = pd.concat([self.reac_data, reac])
            self.drug_data = pd.concat([self.drug_data, drug])
            self.demo_data = pd.concat([self.demo_data, demo])
            self.outc_data = pd.concat([self.outc_data, outc])
            self.ther_data = pd.concat([self.ther_data, ther])
            self.indi_data = pd.concat([self.indi_data, indi])
            self.rpsr_data = pd.concat([self.rpsr_data, rpsr])
    
    def get_data_dict(self):
        """
        Get the data for the given start and end years and quarters.
        """
        return {
            "reac": self.reac_data,
            "drug": self.drug_data,
            "demo": self.demo_data,
            "outc": self.outc_data,
            "ther": self.ther_data,
            "indi": self.indi_data,
            "rpsr": self.rpsr_data,
        }
    
    def _generate_cache_key(self) -> str:
        """Generate a unique cache key based on the quarters being loaded"""
        quarters_str = ",".join(sorted(self.parsed_quarters))
        return hashlib.md5(quarters_str.encode()).hexdigest()
    
    def _load_from_cache(self) -> bool:
        """Attempt to load data from cache"""
        if not self.use_cache:
            return False
            
        logger.info(f"Checking cache at {self.cache_path}")
        cached_data = FAERSData.load_from_cache(self.cache_path)
        
        if cached_data is not None:
            logger.info("Found cached data")
            self.reac_data = cached_data.reac_data
            self.drug_data = cached_data.drug_data
            self.demo_data = cached_data.demo_data
            self.outc_data = cached_data.outc_data
            self.ther_data = cached_data.ther_data
            self.indi_data = cached_data.indi_data
            self.rpsr_data = cached_data.rpsr_data
            return True
        
        logger.info("No cached data found")
        return False

    def get_data(self):
        faers_data = FAERSData(
            reac_data=self.reac_data,
            drug_data=self.drug_data,
            demo_data=self.demo_data,
            outc_data=self.outc_data,
            ther_data=self.ther_data,
            indi_data=self.indi_data,
            rpsr_data=self.rpsr_data,
        )
        
        # Save to cache if enabled
        if self.use_cache:
            logger.info(f"Saving data to cache at {self.cache_path}")
            faers_data.save_to_cache(self.cache_path)
            
        return faers_data

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

def load_single_quarter(quarter: str, save_dir: str):
        """
        Load the data for the given quarter.
        Args:
            quarter: str (e.g. "2024Q1")
            save_dir: str
        """
        if quarter not in get_available_downloaded_quarters(save_dir):
            logger.error(
                f"Quarter {quarter} not found in {save_dir}/faers_reports"
            )
            raise ValueError(
                f"Quarter {quarter} not found in {save_dir}/faers_reports"
            )

        # Construct the file paths
        reac_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"REAC{convert_quarter_file_str(quarter)}.txt"
        )
        drug_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"DRUG{convert_quarter_file_str(quarter)}.txt"
        )
        demo_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"DEMO{convert_quarter_file_str(quarter)}.txt"
        )
        outc_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"OUTC{convert_quarter_file_str(quarter)}.txt"
        )
        ther_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"THER{convert_quarter_file_str(quarter)}.txt"
        )
        indi_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"INDI{convert_quarter_file_str(quarter)}.txt"
        )
        rpsr_file_path = Path(save_dir).joinpath(
            "faers_reports", quarter, f"RPSR{convert_quarter_file_str(quarter)}.txt"
        )

        # Load the data
        reac_raw = pd.DataFrame()
        drug_raw = pd.DataFrame()
        demo_raw = pd.DataFrame()
        outc_raw = pd.DataFrame()
        ther_raw = pd.DataFrame()
        indi_raw = pd.DataFrame()
        rpsr_raw = pd.DataFrame()

        try:
            reac_raw = pd.read_csv(reac_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"REAC file not found for quarter {quarter}")
        try:
            drug_raw = pd.read_csv(drug_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"DRUG file not found for quarter {quarter}")
        try:
            demo_raw = pd.read_csv(demo_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"DEMO file not found for quarter {quarter}")
        try:
            outc_raw = pd.read_csv(outc_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"OUTC file not found for quarter {quarter}")
        try:
            ther_raw = pd.read_csv(ther_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"THER file not found for quarter {quarter}")
        try:
            indi_raw = pd.read_csv(indi_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"INDI file not found for quarter {quarter}")
        try:
            rpsr_raw = pd.read_csv(rpsr_file_path, sep="$")
        except FileNotFoundError:
            logger.error(f"RPSR file not found for quarter {quarter}")

        # Preprocess the data
        reac = preprocess(reac_raw, "reac")
        drug = preprocess(drug_raw, "drug")
        demo = preprocess(demo_raw, "demo")
        outc = preprocess(outc_raw, "outc")
        ther = preprocess(ther_raw, "ther")
        indi = preprocess(indi_raw, "indi")
        rpsr = preprocess(rpsr_raw, "rpsr")

        return reac, drug, demo, outc, ther, indi, rpsr

def load_faers_data(
    start_year: int,
    end_year: int,
    start_quarter: int,
    end_quarter: int,
    save_dir: str = "data",
    debug: bool = False,
    cache: bool = True,
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
        use_cache=cache,
    )
    return loader.get_data()
