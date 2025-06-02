import os
from pathlib import Path
import pandas as pd

def download_faer_files(root_dir: Path, start_year: int, start_quarter: str, end_year: int, end_quarter: str, out_dir: Path) -> dict:
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']

    root_dir = Path(root_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_quarters = []
    for year in range(start_year, end_year + 1):
        start_q = start_quarter if year == start_year else 'Q1'
        end_q = end_quarter if year == end_year else 'Q4'
        for q in quarters[quarters.index(start_q):quarters.index(end_q) + 1]:
            all_quarters.append(f"{str(year)[2:]}{q}")

    existing_quarters = [q for q in all_quarters if (root_dir / f"DEMO{q}.txt").exists()]
    data = {}

    for q in existing_quarters:
        try:
            data[q] = {
                'demo': pd.read_csv(root_dir / f"DEMO{q}.txt", delimiter='$', encoding='ISO-8859-1'),
                'drug': pd.read_csv(root_dir / f"DRUG{q}.txt", delimiter='$', encoding='ISO-8859-1'),
                'reac': pd.read_csv(root_dir / f"REAC{q}.txt", delimiter='$', encoding='ISO-8859-1'),
                'outc': pd.read_csv(root_dir / f"OUTC{q}.txt", delimiter='$', encoding='ISO-8859-1'),
                'indi': pd.read_csv(root_dir / f"INDI{q}.txt", delimiter='$', encoding='ISO-8859-1'),
                'rpsr': pd.read_csv(root_dir / f"RPSR{q}.txt", delimiter='$', encoding='ISO-8859-1'),
                'ther': pd.read_csv(root_dir / f"THER{q}.txt", delimiter='$', encoding='ISO-8859-1'),
            }
            print(f"Loaded {q} successfully.")
        except Exception as e:
            print(f"Error loading data for {q}: {e}")

    return data


def generate_periods(start_year, start_quarter, end_year, end_quarter):
    periods = []
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']

    for year in range(start_year, end_year + 1):
        start_qtr = start_quarter if year == start_year else 'Q1'
        end_qtr = end_quarter if year == end_year else 'Q4'
        for qtr in quarters[quarters.index(start_qtr):quarters.index(end_qtr) + 1]:
            periods.append(f"{str(year)[-2:]}{qtr}")
    return periods


def create_dataframes(start_year, start_quarter, end_year, end_quarter, output_dir, data):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    periods = generate_periods(start_year, start_quarter, end_year, end_quarter)
    print(periods)

    table_types = ['demo', 'drug', 'reac', 'outc', 'indi', 'rpsr', 'ther']
    data_dict = {table: [] for table in table_types}

    for period in periods:
        if period in data:
            for table in table_types:
                if table in data[period]:
                    data_dict[table].append(data[period][table])
        else:
            print(f"Warning: No data available for {period}")
            

    merged_data = {
        table: pd.concat(data_dict[table], ignore_index=True) if data_dict[table] else pd.DataFrame()
        for table in table_types
    }

    for table, df in merged_data.items():
        df.to_csv(output_dir / f"{table}.csv", index=False)

    print(f"Dataframes created and saved to {output_dir}")
    return tuple(merged_data[t] for t in table_types)


def run_download_pipeline(root_dir, out_dir, start_year, start_quarter, end_year, end_quarter):
    data = download_faer_files(
        root_dir=Path(root_dir),
        start_year=start_year,
        start_quarter=start_quarter,
        end_year=end_year,
        end_quarter=end_quarter,
        out_dir=Path(out_dir)
    )
    return create_dataframes(
        start_year=start_year,
        start_quarter=start_quarter,
        end_year=end_year,
        end_quarter=end_quarter,
        output_dir=out_dir,
        data=data
    )
