"""Command-line runner for the G1 aliquot ledger illustration."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g01_solvency.aliquot import AliquotSweepSummary, sweep_aliquot


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_cycles(cycles: tuple[tuple[int, ...], ...], *, limit: int = 12) -> str:
    if not cycles:
        return "`[]`"
    shown = ", ".join(str(cycle) for cycle in cycles[:limit])
    if len(cycles) > limit:
        shown += f", ... ({len(cycles)} total)"
    return f"`[{shown}]`"


def _write_verdict(path: Path, summary: AliquotSweepSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# G1-L4 Verdict - Aliquot Ledger Illustration",
                "",
                "## Hypothesis",
                (
                    f"For starts `1 <= n <= {summary.limit}`, exact aliquot iteration "
                    f"`s(n)=sigma(n)-n` is tracked for up to `{summary.max_steps}` "
                    f"steps, with values above `{summary.cap}` recorded as "
                    "`escaped_cap`."
                ),
                "",
                "## Outcome",
                (
                    f"PASS as an illustrative exact-arithmetic exhibit. Checked "
                    f"`{summary.tested_count}` starts in "
                    f"`{summary.elapsed_seconds:.6f}` seconds."
                ),
                (
                    f"Terminated at `0`: `{summary.terminated_count}`. Entered a "
                    f"cycle: `{summary.cycled_count}`. Escaped cap: "
                    f"`{summary.escaped_cap_count}`. Step-cap unresolved: "
                    f"`{summary.step_cap_count}`."
                ),
                (
                    f"Unique cycles found: `{summary.unique_cycle_count}`. Starts "
                    f"landing on fixed-point cycles: `{summary.fixed_point_count}`. "
                    f"Unique fixed points: `{summary.unique_fixed_points}`."
                ),
                (
                    f"Maximum observed steps before classification: "
                    f"`{summary.max_steps_observed}` at start `{summary.max_steps_start}`. "
                    f"Maximum value seen before stopping: `{summary.max_value_seen}`."
                ),
                (
                    f"Factorized sigma was cross-checked against brute-force divisor "
                    f"sums for `1..{summary.sigma_spot_check_limit}`: "
                    f"`{summary.sigma_spot_checks_passed}`."
                ),
                "",
                "## Cycles and Open Cases",
                f"Representative unique cycles: {_format_cycles(summary.unique_cycles)}.",
                (
                    f"Escaped-cap start sample: `{summary.escaped_cap_starts_sample}`. "
                    f"Step-cap start sample: `{summary.step_cap_starts_sample}`."
                ),
                "",
                "## Ledger Note",
                (
                    "For each traced orbit step, the implementation can record "
                    "`nu_2(sigma(n_k))` alongside `n_k`, `sigma(n_k)`, and "
                    "`s(n_k)`. This is only one projection of the divisor-supply "
                    "ledger: the relevant currency is the full factorization and "
                    "divisor structure, not a one-dimensional scalar."
                ),
                "",
                "## Scope Note",
                (
                    "This is an illustrative folded G1 instance only. Escaped-cap and "
                    "step-cap cases are reported as open within this finite budget; "
                    "they are not evidence that a sequence is unbounded and not "
                    "evidence that it would terminate with more time."
                ),
                (
                    "The run makes no claim about the Catalan-Dickson boundedness/"
                    "termination conjecture, the Guy-Selfridge unboundedness question, "
                    "or the Collatz conjecture."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                (
                    "This result is a G1 ledger-dimensionality illustration: it shows "
                    "that a G1-style currency can be the non-scalar "
                    "factorization/divisor-supply ledger. It does not instantiate "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_a_reduction`, "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge`, "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.GhostConvergence`, "
                    "or "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.NativeSeparation`."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_cli(args: argparse.Namespace) -> AliquotSweepSummary:
    summary = sweep_aliquot(
        limit=args.limit,
        max_steps=args.max_steps,
        cap=args.cap,
        sigma_spot_check_limit=args.sigma_spot_check_limit,
    )
    if args.write_results:
        out_dir = args.results_dir / "G1-L4"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G1-L4 PASS: "
        f"limit={summary.limit} max_steps={summary.max_steps} cap={summary.cap} "
        f"terminated={summary.terminated_count} cycled={summary.cycled_count} "
        f"escaped_cap={summary.escaped_cap_count} step_cap={summary.step_cap_count} "
        f"unique_cycles={summary.unique_cycle_count} "
        f"sigma_spot_checks={summary.sigma_spot_checks_passed} "
        f"seconds={summary.elapsed_seconds:.6f}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100_000)
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--cap", type=int, default=10**12)
    parser.add_argument("--sigma-spot-check-limit", type=int, default=1000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_cli)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

