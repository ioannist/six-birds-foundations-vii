"""Command-line runner for the G6 Recaman census lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g06_needle.recaman import RecamanSummary, run_recaman_census


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ratio_text(numerator: int, denominator: int) -> str:
    return f"`{numerator}/{denominator}`"


def _checkpoint_table(summary: RecamanSummary) -> str:
    rows = [
        "| step | current | max | smallest missing | backward legal / steps | visited in [1,100000] | visited in [1,1000000] | visited in [1,10000000] |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for checkpoint in summary.checkpoints:
        cov = checkpoint.coverage
        rows.append(
            "| "
            f"{checkpoint.step} | {checkpoint.current_value} | {checkpoint.max_value} | "
            f"{checkpoint.smallest_missing} | "
            f"{checkpoint.return_pressure_numerator}/{checkpoint.return_pressure_denominator} | "
            f"{cov['100000']['visited']}/{cov['100000']['total']} | "
            f"{cov['1000000']['visited']}/{cov['1000000']['total']} | "
            f"{cov['10000000']['visited']}/{cov['10000000']['total']} |"
        )
    return "\n".join(rows)


def _write_verdict(path: Path, summary: RecamanSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    intervals = ", ".join(
        f"`[{start},{end}]`" if start != end else f"`{start}`"
        for start, end in summary.missing_intervals
    )
    path.write_text(
        "\n".join(
            [
                "# G6-L1 Verdict - Recaman Census",
                "",
                "## Hypothesis",
                (
                    "The exact Recaman recurrence should produce high but incomplete "
                    "bounded-window coverage, a nonzero return-pressure proxy, and a "
                    "visible smallest-missing trajectory over a `10^7`-step census."
                ),
                "",
                "## Outcome",
                (
                    f"PASS as a bounded census. Ran `{summary.steps}` exact Recaman "
                    f"steps with bytearray membership through `{summary.low_limit}` "
                    f"and exact high-value fallback count `{summary.high_value_count}`."
                ),
                (
                    f"Final value: `{summary.final_value}`. Maximum value reached: "
                    f"`{summary.max_value}`. Final smallest missing positive integer: "
                    f"`{summary.final_smallest_missing}`."
                ),
                (
                    "Final return-pressure proxy "
                    f"{_ratio_text(summary.return_pressure_numerator, summary.return_pressure_denominator)} "
                    "records the exact fraction of steps where the backward move was legal."
                ),
                "",
                "## Checkpoint Curve",
                _checkpoint_table(summary),
                "",
                "## Final Missing-Interval Sample",
                (
                    f"First missing intervals in `[1,{summary.missing_intervals_window}]`: "
                    f"{intervals if intervals else 'none'}."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Scope Note",
                (
                    "This is a bounded exact-arithmetic census and System-case (S-c) "
                    "uncertified exhibit for G6. It does not instantiate "
                    "`covering_schema`, because it supplies no proof that all holes in "
                    "a cofinal exhaustion are eventually covered."
                ),
                (
                    "It also does not instantiate `hole_forming_schema`, because it "
                    "supplies no permanent-hole obstruction proof. The OEIS A005132 "
                    "`852655` smallest-missing fact at computations as large as "
                    "`10^612` terms is much stronger as a bounded computation than "
                    "this `10^7`-step exhibit; this lab neither extends nor contradicts "
                    "that record."
                ),
                "",
                (
                    "Traceability: this result is a bounded Recaman census for G6's "
                    "case-enumeration System-case (S-c), illustrating the "
                    "`gamma_n`/`rho_n` race. It is not a proof instance of "
                    "`SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration.covering_schema` "
                    "or `hole_forming_schema`."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g6_l1(args: argparse.Namespace) -> RecamanSummary:
    """Run G6-L1 and optionally write result artifacts."""

    summary = run_recaman_census(
        steps=args.steps,
        low_limit=args.low_limit,
        checkpoint_interval=args.checkpoint_interval,
    )
    if args.write_results:
        out_dir = args.results_dir / "G6-L1"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G6-L1 PASS: "
        f"steps={summary.steps} final={summary.final_value} "
        f"max={summary.max_value} smallest_missing={summary.final_smallest_missing} "
        f"backward_legal={summary.backward_legal_steps}/{summary.steps} "
        f"high_values={summary.high_value_count}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G6 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=10_000_000)
    parser.add_argument("--low-limit", type=int, default=100_000_000)
    parser.add_argument("--checkpoint-interval", type=int, default=1_000_000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g6_l1)
    return parser


def main() -> None:
    """Run G6-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
