# FAERS Surveillance BMI 212
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


##Describe Data Calls

```bash
# Describe age distribution
python describe_data.py /path/to/data/ age

# Describe sex distribution
python describe_data.py /path/to/data/ sex

# Describe country distribution
python describe_data.py /path/to/data/ country

# Describe outcome severity
python describe_data.py /path/to/data/ severity

# Describe reporting delay 
python describe_data.py /path/to/data/ delay

# Overall dataset description
python describe_data.py /path/to/data/ overall
```

## Drug Analysis Calls

```bash
# Basic analysis
python drug_analysis.py /path/to/data/ erdafitinib

# With age filtering  
python drug_analysis.py /path/to/data/ erdafitinib --min-age 18 --max-age 85

# With custom top indications count
python drug_analysis.py /path/to/data/ erdafitinib --top-indications 5
```

