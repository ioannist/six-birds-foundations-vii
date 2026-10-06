"""Command-line runner for the G10 Ducci-collapse lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g10_persistence.ducci import (
    run_matrix_checks,
    seeded_ducci_sweep,
)


POWER_TWO_LENGTHS = {4, 8, 16}


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ducci = summary["ducci"]
    matrices = summary["gf2_matrix_checks"]
    cycle_rows = [
        f"`k={row['k']}` period `{row['period']}` at step `{row['steps']}`"
        for row in ducci
        if row["status"] == "cycle"
    ]
    zero_rows = [
        f"`k={row['k']}` zero at step `{row['steps']}`"
        for row in ducci
        if row["status"] == "zero"
    ]
    path.write_text(
        "\n".join(
            [
                "# G10-L1 Verdict - Ducci Collapse",
                "",
                "## Hypothesis",
                (
                    "Seeded Ducci tuples of power-of-two lengths `4`, `8`, and `16` "
                    "collapse to zero, while the seeded non-power-of-two calibration "
                    "tuples enter nonzero cycles. The GF(2) parity operator "
                    "`L=I+S` satisfies `L^k=0` for `k=4,8,16`."
                ),
                "",
                "## Outcome",
                (
                    f"PASS. Seed {summary['seed']} swept `k=3..16` with max entry "
                    f"{summary['max_entry']} and step budget {summary['max_steps']}."
                ),
                "Power-of-two collapses: " + "; ".join(zero_rows) + ".",
                "Non-power-of-two cycles: " + "; ".join(cycle_rows) + ".",
                (
                    "Boundedness onset: after the first Ducci step, every observed "
                    "coordinate stayed below the initial range bound for every tested `k`."
                ),
                (
                    "GF(2) matrix checks: "
                    + "; ".join(
                        f"`(I+S)^{row['exponent']}=0` for `k={row['k']}`"
                        for row in matrices
                        if row["is_zero"]
                    )
                    + "."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                (
                    "This is the mechanized lab witness for G10's Case Enumeration "
                    "case (b), `Collapsing`: the Ducci parity structure is destroyed "
                    "by the exact nilpotency certificate for power-of-two lengths, and "
                    "the non-power-of-two seeded calibrations show eventual nonzero cycles."
                ),
                "",
                (
                    "This result exercises G10's `THEOREMS.md` Case Enumeration case (b) "
                    "(`Collapsing`) and the Ducci GF(2) proof-spine claim "
                    "`(I+S)^{2^m}=0`; Ducci was deliberately left as lab-only collapse "
                    "content rather than a Lean theorem."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g10_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G10-L1 and optionally write result artifacts."""

    ducci_results = seeded_ducci_sweep(
        seed=args.seed,
        max_entry=args.max_entry,
        max_steps=args.max_steps,
    )
    matrix_checks = run_matrix_checks()
    summary: dict[str, object] = {
        "seed": args.seed,
        "max_entry": args.max_entry,
        "max_steps": args.max_steps,
        "ducci": [asdict(result) for result in ducci_results],
        "gf2_matrix_checks": [asdict(check) for check in matrix_checks],
    }

    for result in ducci_results:
        if not result.bounded_after_first:
            raise AssertionError(f"k={result.k} violated the after-first-step range bound")
        if result.k in POWER_TWO_LENGTHS and result.status != "zero":
            raise AssertionError(f"k={result.k} did not collapse to zero: {result.status}")
        if result.k not in POWER_TWO_LENGTHS and result.status != "cycle":
            raise AssertionError(f"k={result.k} did not enter a nonzero cycle: {result.status}")
    if not all(check.is_zero for check in matrix_checks):
        raise AssertionError("GF(2) nilpotency check failed")

    if args.write_results:
        out_dir = args.results_dir / "G10-L1"
        _write_json(out_dir / "run.json", summary)
        _write_verdict(out_dir / "verdict.md", summary)

    cycle_summary = ",".join(
        f"{row.k}:{row.period}" for row in ducci_results if row.status == "cycle"
    )
    zero_summary = ",".join(
        f"{row.k}:{row.steps}" for row in ducci_results if row.status == "zero"
    )
    print(
        "G10-L1 PASS: "
        f"seed={args.seed} max_steps={args.max_steps} "
        f"zero_steps={zero_summary} cycle_periods={cycle_summary}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G10 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=10100)
    parser.add_argument("--max-entry", type=int, default=1_000_000)
    parser.add_argument("--max-steps", type=int, default=100_000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g10_l1)
    return parser


def main() -> None:
    """Run G10-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
