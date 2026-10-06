"""Command-line runner for the G4 greedy Egyptian-fraction lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g04_exhaustion.egyptian import (
    SweepSummary,
    expand_fraction,
    sweep_proper_fractions,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_histogram(histogram: dict[int, int]) -> str:
    return ", ".join(f"`{length}`: `{count}`" for length, count in histogram.items())


def _sample_q_table(summary: SweepSummary) -> str:
    selected = [2, 10, 50, 100, 250, summary.max_q]
    rows = ["| max denominator q | max certificate length among p/q with this q |", "|---:|---:|"]
    for q in selected:
        rows.append(f"| {q} | {summary.max_length_by_q[q]} |")
    return "\n".join(rows)


def _write_verdict(path: Path, summary: SweepSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if not summary.failures else "FAIL"
    examples = ", ".join(f"`{example}`" for example in summary.max_length_examples[:12])
    if len(summary.max_length_examples) > 12:
        examples += f", ... ({len(summary.max_length_examples)} total)"
    sample = expand_fraction(3, 7)
    sample_terms = " + ".join(f"1/{d}" for d in sample.denominators)
    path.write_text(
        "\n".join(
            [
                "# G4-L1 Verdict - Greedy Egyptian-Fraction Exhaustion",
                "",
                "## Hypothesis",
                (
                    "Every proper fraction `p/q` with `0 < p < q <= 500`, after "
                    "reduction to lowest terms, terminates under the Fibonacci-Sylvester "
                    "greedy algorithm with a strictly decreasing numerator budget and an "
                    "exact unit-fraction certificate."
                ),
                "",
                "## Outcome",
                (
                    f"{status}. Swept `{summary.raw_fraction_count}` raw proper fractions "
                    f"`p/q` with `0 < p < q <= {summary.max_q}`, representing "
                    f"`{summary.distinct_reduced_count}` distinct reduced fractions."
                ),
                (
                    f"Failures: `{len(summary.failures)}`. Step cap: `{summary.step_cap}`. "
                    f"Maximum certificate length: `{summary.max_length}`, attained by {examples}."
                ),
                "",
                "## Certificate-Length Distribution",
                _format_histogram(summary.length_histogram),
                "",
                "## Target-Size Exhibit",
                _sample_q_table(summary),
                "",
                "## Worked Example",
                (
                    f"`3/7 = {sample_terms}` with denominator certificate "
                    f"`{list(sample.denominators)}` and numerator budget "
                    f"`{list(sample.numerators)}`."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Scope Note",
                (
                    "This lab calibrates G4's positive schema only: local arithmetic "
                    "checks discharge patch soundness, and the strict positive-integer "
                    "numerator descent discharges exhaustion for the tested greedy "
                    "Egyptian-fraction instance."
                ),
                (
                    "It does not exercise `LanguageComplete` or "
                    "`conditional_biconditional`, and it does not exercise "
                    "`FixedLeak` or `fixed_package_no_go`. G4-L2 Erdos-Straus content "
                    "is deliberately out of scope."
                ),
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G4MovingCoverExhaustion.positive_schema` "
                    "for the concrete Fibonacci-Sylvester greedy Egyptian-fraction "
                    "calibration, with `Sound` represented by exact unit-subtraction "
                    "checks and `Exhausted` represented by strict numerator descent."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g4_l1(args: argparse.Namespace) -> SweepSummary:
    """Run G4-L1 and optionally write result artifacts."""

    summary = sweep_proper_fractions(max_q=args.max_q, step_cap=args.step_cap)
    if args.write_results:
        out_dir = args.results_dir / "G4-L1"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    status = "PASS" if not summary.failures else "FAIL"
    print(
        "G4-L1 "
        f"{status}: max_q={summary.max_q} raw={summary.raw_fraction_count} "
        f"distinct_reduced={summary.distinct_reduced_count} "
        f"failures={len(summary.failures)} max_length={summary.max_length} "
        f"max_examples={list(summary.max_length_examples[:8])}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G4 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-q", type=int, default=500)
    parser.add_argument("--step-cap", type=int, default=1000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g4_l1)
    return parser


def main() -> None:
    """Run G4-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
