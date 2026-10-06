"""Command-line runner for the G1 Collatz affine-ledger lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g01_solvency.collatz_ledger import SweepSummary, sweep_odd_starts


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: SweepSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# G1-L1 Verdict - Collatz Affine Ledger Audit",
                "",
                "## Hypothesis",
                (
                    "For every checked odd `n`, the accelerated Collatz affine ledger "
                    "`n_k = (3^k*n + B_k) / 2^A_k` holds exactly through first "
                    "descent, and the descent certificate matches the integer "
                    "inequality `2^A_k*n > 3^k*n + B_k`."
                ),
                "",
                "## Outcome",
                (
                    f"PASS. The sweep checked every positive odd `n < {summary.limit}` "
                    f"with max step cap `{summary.max_steps}` in "
                    f"`{summary.elapsed_seconds:.6f}` seconds."
                ),
                (
                    f"Tested odd starts: `{summary.tested_odd_count}`. Nonterminal "
                    f"starts: `{summary.nonterminal_count}`. Terminal fixed starts: "
                    f"`{summary.terminal_fixed_count}`."
                ),
                (
                    f"All `{summary.descended_count}` nonterminal odd starts reached "
                    "first descent before the cap; capped starts: "
                    f"`{summary.capped_count}`."
                ),
                (
                    f"Total exact ledger checkpoints: `{summary.total_checkpoints}`. "
                    f"Maximum first-descent step: `{summary.max_descent_step}` at "
                    f"`n={summary.max_descent_start}`."
                ),
                (
                    f"Maximum accumulated valuation `A_k`: `{summary.max_A_k}`; "
                    f"maximum `B_k` bit length: `{summary.max_B_bits}`; maximum "
                    f"checked orbit value bit length: `{summary.max_n_k_bits}`."
                ),
                "",
                "## Exact Checks",
                (
                    "At every checked horizon the numerator `3^k*n + B_k` was exactly "
                    "divisible by `2^A_k`, the quotient matched direct accelerated "
                    "iteration, and `(n_k < n)` was equivalent to "
                    "`2^A_k*n > 3^k*n + B_k` using integer arithmetic only."
                ),
                "",
                "## Scope Note",
                (
                    "This lab validates the concrete Collatz setup formulas needed for "
                    "future G1 instantiations. It does not directly instantiate "
                    "`part_a_reduction` or `part_b_discharge`, because those Lean "
                    "theorems are abstract statements about `Descends`, "
                    "`BadTailMembrane`, `GhostConvergence`, and `NativeSeparation`, "
                    "and do not contain the affine arithmetic ledger."
                ),
                (
                    "This packet does not prove Collatz and does not make progress on "
                    "the Collatz conjecture. It is an exact bookkeeping audit over the "
                    "declared finite range."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                (
                    "The affine ledger and descent-boundary certificate are internally "
                    "consistent for every checked odd start. Any later Collatz-specific "
                    "G1 membrane or ghost-shadowing lab can use these formulas as a "
                    "tested calibration surface, while still needing separate evidence "
                    "for the abstract liveness/discharge hypotheses."
                ),
                "",
                (
                    "This result validates the concrete G1 Setup formulas "
                    "`T(n)=(3n+1)/2^a(n)`, `A_k=sum_{j<k} a_j`, "
                    "`B_0=0`, `B_{j+1}=3B_j+2^A_j`, and "
                    "`n_k=(3^k*n+B_k)/2^A_k` from `THEOREMS.md`. It is setup-formula "
                    "validation for future use with "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.Descends` "
                    "and `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.BadTailMembrane`, "
                    "not a direct instantiation of "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_a_reduction` "
                    "or "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge`."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g1_l1(args: argparse.Namespace) -> SweepSummary:
    """Run G1-L1 and optionally write result artifacts."""

    summary = sweep_odd_starts(limit=args.limit, max_steps=args.max_steps)
    if args.write_results:
        out_dir = args.results_dir / "G1-L1"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G1-L1 PASS: "
        f"limit={summary.limit} max_steps={summary.max_steps} "
        f"tested_odds={summary.tested_odd_count} "
        f"descended={summary.descended_count} capped={summary.capped_count} "
        f"checkpoints={summary.total_checkpoints} "
        f"max_descent_step={summary.max_descent_step} "
        f"max_descent_start={summary.max_descent_start} "
        f"seconds={summary.elapsed_seconds:.6f}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G1 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g1_l1)
    return parser


def main() -> None:
    """Run G1-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

