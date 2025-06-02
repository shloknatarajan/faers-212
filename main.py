from pathlib import Path
import argparse
import download_data as dd
import process_data as dp
import analyze_data as da
import pandas as pd

def cmd_download(args):
    dd.run_download_pipeline(
        root_dir=args.root_dir,
        start_year=args.start_year,
        start_quarter=args.start_quarter,
        end_year=args.end_year,
        end_quarter=args.end_quarter,
        out_dir=args.output_dir
    )

def cmd_preprocess(args):
    dp.run_preprocess_pipeline(
        input_dir=args.input_dir,
        out_dir=args.output_dir,
        drug = args.drug
    )
    print("Pre-processed tables saved to", args.output_dir)


#ADD TO ANALYSIS
def cmd_analyse(args): 
    data_dir = Path(args.data_dir)
    demo = pd.read_parquet(data_dir / "demo.parquet")
    drug = pd.read_parquet(data_dir / "drug.parquet")
    # ADD IN 
    return

#Argparse setup
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="faers_pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    # download
    d = sub.add_parser("download")
    d.add_argument("--root-dir",    type=Path, required=True)
    d.add_argument("--start-year",  type=int,  required=True)
    d.add_argument("--start-quarter", choices=["Q1","Q2","Q3","Q4"], required=True)
    d.add_argument("--end-year",    type=int,  required=True)
    d.add_argument("--end-quarter", choices=["Q1","Q2","Q3","Q4"], required=True)
    d.add_argument("--output-dir", type=Path, default="faers_loaded")
    d.set_defaults(func=cmd_download)

    # preprocess
    pp = sub.add_parser("preprocess")
    pp.add_argument("--input-dir",    type=Path, required=True)
    pp.add_argument("--output-dir", type=Path, default="faers_clean")
    pp.add_argument("--drug", type=str, default=None)
    pp.set_defaults(func=cmd_preprocess)

    # analyse
    a = sub.add_parser("analyse")
    a.add_argument("--data-dir", type=Path, default="faers_clean")
    a.set_defaults(func=cmd_analyse)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
