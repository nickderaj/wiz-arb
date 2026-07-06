"""Command-line entry points: `wizarb ingest|build-panel|base-rates`."""

from __future__ import annotations

import argparse
import logging


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="wizarb")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="download CAA punctuality CSVs")
    p_ingest.add_argument("--from-year", type=int, default=2019)
    p_ingest.add_argument("--to-year", type=int, default=2025)

    sub.add_parser("build-panel", help="parse raw CSVs into the interim parquet panel")
    sub.add_parser("base-rates", help="compute base-rate tables and report")
    sub.add_parser("shortlist", help="compute the ranked candidate shortlist (doc 02 §4)")
    sub.add_parser("model-backtest", help="walk-forward validate the P(delay>=3h) model ladder")

    args = parser.parse_args()
    if args.cmd == "ingest":
        from wizarb.ingest import caa

        paths = caa.download(list(range(args.from_year, args.to_year + 1)))
        print(f"{len(paths)} files present in data/raw/caa")
    elif args.cmd == "build-panel":
        from wizarb.ingest import caa

        print(caa.build_panel())
    elif args.cmd == "base-rates":
        from wizarb.analysis import base_rates

        print(base_rates.write_report())
    elif args.cmd == "shortlist":
        from wizarb.analysis import shortlist

        print(shortlist.write_report())
    elif args.cmd == "model-backtest":
        from wizarb.models import walkforward

        print(walkforward.write_report())


if __name__ == "__main__":
    main()
