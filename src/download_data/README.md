# Scripts
Scripts to download the needed raw data

## Needed Scripts

## Progress Tracker
| Task | Status |
| --- | --- |
| Download FAERS data |  |
| Download FAERS data   |  |
| Create RxNorm plan | |

Note: Can't download MedDRA programatically. Needs to be downloaded and unzipped separately.



## Usage
### Download Data
```
python -m src.data_management.faers_downloader --quarter 2024Q1
```
Flags:
```
--quarter: Specify in the format YYYYQ#
--overrite: True or False that specifies whether to overrite pre-existing data
```