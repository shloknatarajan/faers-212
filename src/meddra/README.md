# MedDRA Package

This package provides utilities for working with the Medical Dictionary for Regulatory Activities (MedDRA) terminology in the context of FDA Adverse Event Reporting System (FAERS) data analysis.

## Overview

MedDRA is a clinically validated international medical terminology used by regulatory authorities and the pharmaceutical industry for data entry, retrieval, evaluation, and presentation of regulatory information. This package helps to search, filter, and analyze FAERS reports using MedDRA terminology.

## MedDRA Hierarchy

MedDRA has a hierarchical structure with five levels (from most specific to most general):

1. **Lowest Level Term (LLT)** - Most specific, e.g., "Cardiac Decompensation"
2. **Preferred Term (PT)** - Clinical concepts, e.g., "Congestive Heart Failure"
3. **High Level Term (HLT)** - Grouping terms, e.g., "Left Ventricular Failures"
4. **High Level Group Term (HLGT)** - Broad grouping terms, e.g., "Heart Failures"
5. **System Organ Class (SOC)** - Highest level, e.g., "Cardiac Disorders"

Each term in a lower level is linked to at least one term in the level above it, creating a hierarchical relationship.

## Features

### MedDRA Search

The package allows you to search the FAERS database for events related to any level of MedDRA terms:

- **System Organ Class (SOC)**: Broadest level, categorizes adverse events by anatomical or physiological system
- **High Level Group Term (HLGT)**: Groups HTLs by anatomy, pathology, physiology, etiology, or function
- **High Level Term (HLT)**: Groups PTs based on anatomy, pathology, physiology, etiology, or function
- **Preferred Term (PT)**: Single medical concept representing symptoms, signs, diseases, diagnoses, etc.
- **Lowest Level Term (LLT)**: Most specific level, includes synonyms and lexical variants of PTs

NOTE: Right now, you can just search a report by LLT since that's what contained in FAERS, but it's theoretically possible to search for any term in the hierarchy by checking get_system_organ_class() function and run across all rows/LLTs.

### Data Mapping

The package provides functionality to:

- Map between different levels of MedDRA terms
- Convert lower level terms (LLT, PT, HLT, HLGT) to their corresponding System Organ Class (SOC)
- Support searching and filtering FAERS reports based on MedDRA terms at any level

## Key Components

### Files

- **search.py**: Contains functions for searching and filtering FAERS reports using MedDRA terms
- **llt_soc.csv**: Mapping file that connects Lowest Level Terms (LLTs) to their corresponding System Organ Classes (SOCs) and intermediate levels
- **medra_loading.ipynb**: Jupyter notebook demonstrating how the MedDRA data is loaded and processed

### Functions

- `filter_by_any_terms(df, terms)`: Filter a DataFrame to include rows containing ANY of the specified MedDRA terms
- `filter_by_all_terms(df, terms)`: Filter a DataFrame to include rows containing ALL of the specified MedDRA terms
- `search_meddra(report, preferred_terms)`: Search a FAERS report for specific MedDRA Preferred Terms
- `get_system_organ_class(meddra_term)`: Retrieve the System Organ Class for a given MedDRA term

## Usage Examples

### Searching for Specific Terms in FAERS Reports

```python
from src.load_data.load_report import load_report
from src.meddra.search import search_meddra

# Load a FAERS report
report_quarter = "25Q1"
report = load_report(report_quarter)

# Search for specific preferred terms
preferred_terms = ["Palmar-plantar erythrodysaesthesia syndrome"]
matching_rows = search_meddra(report, preferred_terms)
```

### Getting System Organ Class for a Term

```python
from src.meddra.search import get_system_organ_class

# Get the SOC for a specific MedDRA term
soc = get_system_organ_class("Congestive Heart Failure")
print(soc)  # Output: "Cardiac disorders"
```

## Data Sources

The MedDRA data in this package is derived from MedDRA version 28.0 (English). The raw MedDRA files are stored in the `MedDRA_28_0_ENglish` directory and include:

- **llt.asc**: Contains Lowest Level Terms and their relationships to Preferred Terms
- **soc.asc**: Contains System Organ Classes
- **mdhier.asc**: Contains the hierarchical relationships between MedDRA terms

These files were processed to create the consolidated `llt_soc.csv` file that maps between all MedDRA levels.