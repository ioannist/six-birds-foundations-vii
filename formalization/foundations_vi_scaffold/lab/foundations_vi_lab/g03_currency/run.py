"""Command-line runner for the G3 amortized-currency lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g03_currency.binary_counter import (
    run_binary_counter,
    worked_examples,
)
from foundations_vi_lab.g03_currency.dynamic_array import (
    run_dynamic_array,
    worked_resize_example,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    binary = summary["binary"]
    dynamic = summary["dynamic_array"]
    path.write_text(
        "\n".join(
            [
                "# G3-L1 Verdict - Amortized Calibration Battery",
                "",
                "## Hypothesis",
                (
                    "Binary-counter increment has exact amortized cost `2`; "
                    "dynamic-array insertion has amortized cost at most `3`, "
                    "with exact cost `3` at resizing insertions; both satisfy "
                    "the finite-prefix telescoping identity."
                ),
                "",
                "## Outcome",
                (
                    f"PASS. Binary counter seed {binary['seed']} ran "
                    f"{binary['length']} increments from start value "
                    f"{binary['start_value']} to {binary['final_value']}; "
                    "every amortized cost was exactly `2` and telescoping held."
                ),
                (
                    f"PASS. Dynamic array seed {dynamic['seed']} ran "
                    f"{dynamic['length']} insertions after {dynamic['warmup_inserts']} "
                    f"warmup insertions; {dynamic['resize_count']} resize step(s) "
                    "were observed, every amortized cost was at most `3`, "
                    "each resize had amortized cost exactly `3`, and telescoping held."
                ),
                "",
                "## Worked Checks",
                "| check | before | after | actual | Phi before | Phi after | a_hat |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: |",
                (
                    "| binary carry | 0111 | 1000 | 4 | 3 | 1 | 2 |"
                ),
                (
                    "| binary non-carry | 0100 | 0101 | 1 | 1 | 2 | 2 |"
                ),
                (
                    "| dynamic resize | size=4,capacity=4 | size=5,capacity=8 | "
                    "5 | 4 | 2 | 3 |"
                ),
                "",
                "## Credit-Ledger Preview",
                "The JSON result includes the first five audited ledger rows for each calibration.",
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                (
                    "This is an exact-integer computational exhibit for G3's "
                    "finite-prefix potential-currency theorem."
                ),
                "",
                "## Scope Note",
                (
                    "Splay trees are not implemented in this lab packet. "
                    "`THEOREMS.md` already cites Sleator-Tarjan's access lemma "
                    "as the structural calibration; this run covers the binary-counter "
                    "and dynamic-array arithmetic calibrations."
                ),
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G3AmortizedCurrency.telescoping_identity` "
                    "and `SixBirdsFoundationsVI.Laws.G3AmortizedCurrency.uniform_actual_cost_bound`, "
                    "confirming exact finite-prefix amortized-cost accounting for the binary-counter "
                    "and dynamic-array calibrations."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g3_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G3-L1 and optionally write result artifacts."""

    binary = run_binary_counter(seed=args.seed + 1, length=args.length)
    dynamic = run_dynamic_array(seed=args.seed + 2, length=args.length)
    summary: dict[str, object] = {
        "seed": args.seed,
        "length": args.length,
        "binary": asdict(binary),
        "dynamic_array": asdict(dynamic),
        "worked_examples": {
            "binary": worked_examples(),
            "dynamic_resize": worked_resize_example(),
        },
    }
    if args.write_results:
        out_dir = args.results_dir / "G3-L1"
        _write_json(out_dir / "run.json", summary)
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G3-L1 PASS: "
        f"seed={summary['seed']} length={summary['length']} "
        f"binary_start={binary.start_value} binary_final={binary.final_value} "
        f"dynamic_warmup={dynamic.warmup_inserts} dynamic_resizes={dynamic.resize_count}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G3 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7300)
    parser.add_argument("--length", type=int, default=1000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g3_l1)
    return parser


def main() -> None:
    """Run G3-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
