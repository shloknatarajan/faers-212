# Data Folder
This folder contains all of the data used throughout the repo.

## Data Sources
- FAERS Raw Data
- FAERS Merged Data (merged on primaryid)
- MedDRA Terms and Maps (this needs to be requested outside the scope of this repo)
- RxNORM maps?
- DrugBank IDs?

## Thoughts
- Do we even need to download the meddra terms if we provide the excel with the hierarchies?
- It may be necessary to create a pipeline for transforming the raw data to lit_soc.csv if we aren't allowed to share meddra terms like that
- Need to also specifiy meddra version numbers somewhere

## Usage
Example usage for downloading the raw FAERS data:
```
python -m src.download_data.faers_downloader --quarters 2024Q1
```
Or
```
python -m src.download_data.faers_downloader --quarters all
```

Example usage for converting the raw data to processed
```
python -m src.preprocessing.merge_reports --quarters 2024Q1
```
```
python -m src.preprocessing.merge_reports --quarters all
```