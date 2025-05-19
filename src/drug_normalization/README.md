# Drug Normalization
Goals:
- For a given drug, convert it to a normalized drug name
    - Another possible option would be converting to a DrugBank ID
- Be able to search for drugs within a merged excel file


Jodie's drug processing code:
```
def preprocess_drug_df(drug):
    drug = drug[['primaryid', 'caseid', 'role_cod', 'drugname', 'prod_ai']]
    drug = drug[drug['role_cod'] == 'PS']

    drug = drug[pd.notnull(drug['drugname'])]  # Drops Nulls
    drug['drugname'] = drug['drugname'].str.strip().str.lower()  # Stips whitespace, Transforms to lowercase
    drug = drug[~drug['drugname'].isin(['unknown'])]  # Drops unknowns
    drug['drugname'] = drug['drugname'].str.replace('\\', '/')  # Standardizes slashes to '/'
    drug['drugname'] = drug['drugname'].map(
        lambda x: x[:-1] if str(x).endswith(".") else x)  # Removes periods at the end of drug names

    return drug

```