# MedDRA / SMQs
Extract terms and create functions that can extract records based on the relavent terms


## Subgoals
### MedDRA Search
Be able to search the FAERS database for events related to the levels of MedDRA Terms:
1. System Organ Class (SOC) ex. "Cardiac Disorders"
2. High Level Group Term (HLGT) ex. "Heart Failures"
3. High Level Term (HLT) ex. "Left Ventricular Failures"
4. Preferred Term (PT) ex. "Congestive Heart Failure"
5. Lowest Level Term (LLT) ex. "Cardiac Decompensation"
Each AE report should contain several MedDRA terms

### Steps
1. Import a FAERS dataset
