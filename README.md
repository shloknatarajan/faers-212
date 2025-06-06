# FAERS-212: Automated Pharmacovigilance Pipeline

A comprehensive Python toolkit for analyzing FDA Adverse Event Reporting System (FAERS) data, implementing standardized pharmacovigilance methods for drug safety signal detection.

## Overview

This pipeline automates the standard pharmacovigilance workflow:
1. **Data Acquisition**: Download and cache FAERS quarterly data
2. **Preprocessing**: Clean drug names, standardize demographics, map MedDRA terms
3. **Cohort Generation**: Filter by drugs, adverse events, demographics
4. **Statistical Analysis**: Compute disproportionality measures (PRR, ROR, IC, EBGM)
5. **Reporting**: Generate descriptive statistics and visualizations

### Supported Statistical Methods
- **PRR** (Proportional Reporting Ratio)
- **ROR** (Reporting Odds Ratio) 
- **IC** (Information Component)
- **EBGM** (Empirical Bayes Geometric Mean) with full Bayesian confidence intervals

## Quick Start

### Basic Drug Analysis
```python
from src.data_loader import load_faers_data
from src.report_downloader import download_faers_quarters
from src.drug_search import run_indications_analysis
from src.descriptive_stats import describe

# Download and load 2024 data
faers_data = download_faers_quarters(2024, 2024, 1, 4)
data = load_faers_data(2024, 1, 2024, 4, save_dir="data")

# Analyze drug indications and demographics
results = run_indications_analysis(data, "erdafitinib", min_age=0, max_age=100)
describe(results, 'all_demographics')
```

### Advanced Statistical Analysis
```python
from src.contingency_analysis import analyze_adverse_events
from src.filters import filter_by

# Filter cohort
drug_cohort = filter_by(data, drug="erdafitinib", min_age=18, max_age=85)

# Comprehensive adverse event analysis with multiple statistical measures
results = analyze_adverse_events(
    data, 
    query_drug="erdafitinib",
    preferred_terms=["Nausea", "Fatigue", "Rash"],
    methods=["prr", "ror", "ebgm", "ic"]
)
```

## Core Modules

### Data Management
- **`data_loader.py`**: Intelligent caching, multi-quarter loading, data merging
- **`preprocessing.py`**: Drug name standardization, demographic cleaning, MedDRA mapping
- **`report_downloader.py`**: Automated FAERS data downloading

### Analysis & Filtering  
- **`drug_search.py`**: Drug-based filtering with flexible name matching
- **`meddra_search.py`**: MedDRA preferred term and SOC filtering
- **`filters.py`**: Unified filtering interface
- **`contingency_analysis.py`**: Complete statistical analysis suite
- **`descriptive_stats.py`**: Demographic and descriptive analysis

### Research Applications
This pipeline supports:
- **Signal Detection**: Automated screening for drug-adverse event associations
- **Cohort Studies**: Flexible demographic and clinical filtering
- **Comparative Analysis**: Multi-drug safety profiles
- **Regulatory Research**: Standardized pharmacovigilance methods

## Legacy Research Methods
### Automated Pipeline for Current Research Methods
Current research methods follow relatively similar set of steps in order to create 2x2 contingency tables followed up with the application of some of the following statistical tests:
- PRR (Proportional Reporting Ratio)
- ROR (Reporting Odds Ratio)
- IC (Information Component)
- Empirical Bayes Geometric Mean (EBGM) / MGPS
    - This is a more long-term goal since it requires running against all (Drug, SE) pairs

The general process is as follows:
1. Cohort generation: Perform data cleaning / processing to apply your desired drug or adverse event label to records in the database. You may need to remove or add labels to records as the records are not necessarily perfect
2. Construct your 2x2 contingency table from created cohorts
3. Apply the statistical test of your choice

### Expand cohort generation methods
A lot of the accuracy will likely based upon how cohorts pertaining 
to the drug / adverse event are created. Research on current methods along with the ability to select from a suite of options should be added to our pipeline
Current Methods (add approaches here):
- Create a set of “preferred terms” using Standardized MedDRA Queries (SMQs). They group preferred terms indicating similar medical conditions. They were specifically made to help retrieve cases of interest from MedDRA-coded database [Paper](https://ascpt.onlinelibrary.wiley.com/doi/epdf/10.1002/cpt.3139)
- Exclude non-primary suspect drugs

### Automatic Querying of Pipeline
Rather than relying on researchers to spot trends and study them, the pipeline should be able to automatically run on drugs/adverse events within the database and extract insights. This builds upon research trends. This can be via brute force investigation of the databse or via some intelligent search, potentially drawing from current ideas surrounding [AI Research Scientists](https://sakana.ai/ai-scientist/).
Another route could be centered around creating a frontend/dashboards for researchers to use but I think that's potentially less novel, still requires manual work by researchers, and may already exist internally within the FDA.
Rather than relying on researchers to spot trends and study them, the pipeline should be able to automatically run on drugs/adverse events within the database and extract insights. This builds upon research trends. This can be via brute force investigation of the databse or via some intelligent search, potentially drawing from current ideas surrounding [AI Research Scientists](https://sakana.ai/ai-scientist/)

## Setting up Environment 
We porvide a conda environment.yml file as well as a pixi toml

To create the conda environment locally, save environment.yml in the faers-cohort-generation folder. Then, run:
```
conda env create -f environment.yml
conda activate faers-env
```
or install [pixi](https://pixi.sh/latest/) and run pixi install to download the correct dependencies

### To add a new dependency:

conda install (your package)
Make sure to add the new dependency to the environment.yml file!

### To update your local environment after someone else has added a dependency:

conda env update --file environment.yml --prune


## Command Line Interface

### Main Pipeline
```bash
# Run complete drug analysis pipeline
python main.py erdafitinib --start-year 2024 --start-quarter 1 --end-year 2024 --end-quarter 4

# With age filtering
python main.py erdafitinib --min-age 18 --max-age 85 --start-year 2024 --start-quarter 1 --end-year 2024 --end-quarter 4
```

### Data Description
```bash
# Describe demographics and distributions
python drug_analysis.py erdafitinib --describe-demographics

# Overall dataset statistics  
python drug_analysis.py erdafitinib --describe-overall
```

### Download Data
```bash
# Download specific quarters
python download_data.py --start-year 2024 --start-quarter 1 --end-year 2024 --end-quarter 4
```
## Contributors

| Name        | Main Contributions |
|-------------|-------------------|
| **Shlock**  | Built out download logic, and converted core scripts to the new API. Wrote out readme and API code structure. |
| **Jodie**   | Notebook runs &dash; assisted with preprocessing, drug searches, time-to-event analyses |
| **Michael** | Notebook runs &dash; assisted with statistical methods and drug search functions |
| **Ariana**  | Notebook runs &dash; wrote name-mapping steps and descriptive analyses. |
| **May**     | Wrote the MedDRA mapping script and inital bayesian shriking code. Helped adapt the pipeline to the API interface. |

Note: Automatic download script from FDA FAERS website (faersDownloader.py) was adapted from FAERS-data-toolkit (https://github.com/Judenpech/FAERS-data-toolkit), a github repo written by Judenpech. This enables for most recent FAERS Quarterly Data Extract Files to be automatically downloaded from the FDA website. (https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html). 

 


