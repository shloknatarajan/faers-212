import pandas as pd


drug = pd.read_csv('DRUG24Q4.TXT', sep='$', encoding='latin-1')
reac = pd.read_csv('REAC24Q4.TXT', sep='$', encoding='latin-1')

print(drug)


