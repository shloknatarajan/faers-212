# Preprocessing
Code for
- Merging all of the data tables
- Dropping duplicates

## Usage
Here is an example of the command
```
python -m src.preprocessing.merge_reports --quarter 2024Q1
```
Flags:
```
--quarter: Specify in the format YYYYQ#
--overrite: True or False that specifies whether to overrite pre-existing data
```
The raw data is parsed from data/raw_faers and the output is MERGEDYYQ#.csv (ex. MERGED24Q1.csv) in data/processed_faers
