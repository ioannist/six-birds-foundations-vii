from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compare import compare_with_lean, write_results
from .fixtures import load_countermodels, load_scenarios


def main() -> int:
    parser = argparse.ArgumentParser(description="Foundations VII finite reference world")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="validate fixtures and run the Python evaluator")
    run.add_argument("--output", type=Path, default=Path("results"))
    compare = sub.add_parser("compare", help="compare Python and executed Lean JSONL")
    compare.add_argument("lean_results", type=Path)
    compare.add_argument("--output", type=Path, default=Path("results/cross_implementation.json"))
    inspect = sub.add_parser("inspect", help="print fixture counts")
    args = parser.parse_args()
    if args.command == "run":
        summary = write_results(args.output)
        print(json.dumps(summary, sort_keys=True))
        return 0 if summary["all_pass"] else 1
    if args.command == "compare":
        report = compare_with_lean(args.lean_results, args.output)
        print(json.dumps(report, sort_keys=True))
        return 0 if report["all_pass"] else 1
    if args.command == "inspect":
        print(json.dumps({"scenarios": len(load_scenarios()), "countermodels": len(load_countermodels())}, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
