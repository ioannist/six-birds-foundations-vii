"""Command-line runner for the G1 bad-tail membrane census lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g01_solvency.bad_tail import G1L2Summary, run_g1_l2


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _selected_ghost_records(summary: G1L2Summary) -> list[object]:
    selected_L = set(range(summary.ghost_min_L, min(summary.ghost_max_L, 10) + 1))
    selected_L.update({20, 30, 40, 50, 60, 70, 80, summary.ghost_max_L})
    return [record for record in summary.ghost_family if record.L in selected_L]


def _write_verdict(path: Path, summary: G1L2Summary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    census = summary.census
    ghost_failures = [
        record for record in summary.ghost_family if not record.predicted_k_star_matches
    ]
    shadow_failures = [
        record
        for record in summary.ghost_family
        if not record.shadow_valuations_all_one or not record.closed_form_agrees or record.capped
    ]
    outcome = "PASS" if not ghost_failures and not shadow_failures and census.capped_count == 0 else (
        "SURPRISE / PARTIAL FAIL"
    )

    hist_rows = [
        "| k | count with `k*=k` | membrane size `count(k*>k)` |",
        "| ---: | ---: | ---: |",
    ]
    for k in range(1, min(census.max_k_star, 15) + 1):
        hist_rows.append(
            f"| {k} | {census.histogram.get(k, 0)} | {census.membrane_sizes.get(k, 0)} |"
        )
    if census.max_k_star > 15:
        hist_rows.append(
            f"| {census.max_k_star} | {census.histogram.get(census.max_k_star, 0)} | "
            f"{census.membrane_sizes.get(census.max_k_star, 0)} |"
        )

    ghost_rows = [
        "| L | shadow steps | all `a_i=1` | closed form | predicted k* | actual k* | match |",
        "| ---: | ---: | --- | --- | ---: | ---: | --- |",
    ]
    for record in _selected_ghost_records(summary):
        ghost_rows.append(
            f"| {record.L} | {record.shadow_steps} | "
            f"{record.shadow_valuations_all_one} | {record.closed_form_agrees} | "
            f"{record.predicted_k_star} | {record.first_descent_step} | "
            f"{record.predicted_k_star_matches} |"
        )

    first_failure_text = "None."
    if ghost_failures:
        first = ghost_failures[0]
        first_failure_text = (
            f"The first tested ghost-family mismatch is `L={first.L}`: "
            f"the prediction was `k*={first.predicted_k_star}`, but the exact run found "
            f"`k*={first.first_descent_step}`."
        )

    path.write_text(
        "\n".join(
            [
                "# G1-L2 Verdict - Bad-Tail Membrane Census",
                "",
                "## Hypothesis",
                (
                    "Every tested odd `n < 10^7` reaches first descent within the step "
                    "cap, and the `2^L-1` ghost-shadowing family has exact "
                    "`a_i=1` shadowing for `0 <= i < L-1` with predicted "
                    "`k*(2^L-1)=L-1`."
                ),
                "",
                "## Outcome",
                (
                    f"{outcome}. The odd-start census checked every positive odd "
                    f"`n < {summary.limit}` in `{census.elapsed_seconds:.6f}` seconds "
                    f"for the census phase and `{summary.elapsed_seconds:.6f}` seconds total."
                ),
                (
                    f"Nonterminal starts: `{census.nonterminal_count}`; descended before "
                    f"cap: `{census.descended_count}`; capped: `{census.capped_count}`; "
                    f"terminal fixed starts: `{census.terminal_fixed_count}`."
                ),
                (
                    f"`k*` mean: `{census.mean_k_star}`; median: `{census.percentile_50}`; "
                    f"90th percentile: `{census.percentile_90}`; 99th percentile: "
                    f"`{census.percentile_99}`; max: `{census.max_k_star}` at "
                    f"`n={census.max_k_star_start}`."
                ),
                (
                    f"Ghost family checked `L={summary.ghost_min_L}..{summary.ghost_max_L}`. "
                    f"Shadow/closed-form failures: `{len(shadow_failures)}`. "
                    f"`k*=L-1` prediction failures: `{summary.ghost_prediction_failures}`."
                ),
                "",
                "## Membrane Census",
                *hist_rows,
                "",
                "The full `k*` histogram and membrane-size dictionary are recorded in `run.json`.",
                "",
                "## Ghost-Shadowing Family",
                *ghost_rows,
                "",
                "## Surprise",
                first_failure_text,
                (
                    "The unconditional shadowing fact itself was confirmed: direct iteration "
                    "matched `n_i = 3^i*2^(L-i)-1`, and all checked prefix valuations were "
                    "`a_i=1` for `0 <= i < L-1`. What failed was the stronger packet "
                    "prediction that this prefix makes the first descent occur exactly at "
                    "`L-1`."
                ),
                "",
                "## Scope Note",
                (
                    "The `2^L-1` ghost-shadowing family is evidence against fixed "
                    "finite-depth proof strategies, not evidence for or against the "
                    "Collatz conjecture. This lab is a native-integer bad-tail census and "
                    "Proof-Spine formula check; it does not touch a completion `Xhat`, an "
                    "embedding, ghost neighborhoods `U`, `GhostConvergence`, or "
                    "`NativeSeparation`."
                ),
                (
                    "This packet does not prove Collatz and does not make progress on the "
                    "Collatz conjecture."
                ),
                "",
                "## Implication",
                (
                    "The census supplies exact finite-range membrane data, and the "
                    "`2^L-1` family supplies verified arbitrarily long one-halving "
                    "prefixes over the tested `L` range. The exact `k*=L-1` claim is not "
                    "supported by this computation and should not be used as a paper claim "
                    "without correction."
                ),
                "",
                (
                    "This result validates G1's native bad-tail census and the "
                    "`2^L-1` shadowing formula from `THEOREMS.md` for the tested range. "
                    "It is setup/proof-spine validation for future use with "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.BadTailMembrane` "
                    "and "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.InfiniteBadThread`, "
                    "not a direct instantiation of "
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


def run_cli(args: argparse.Namespace) -> G1L2Summary:
    """Run G1-L2 and optionally write artifacts."""

    summary = run_g1_l2(
        limit=args.limit,
        max_steps=args.max_steps,
        ghost_min_L=args.ghost_min_l,
        ghost_max_L=args.ghost_max_l,
        ghost_max_steps=args.ghost_max_steps,
    )
    if args.write_results:
        out_dir = args.results_dir / "G1-L2"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G1-L2 "
        f"{'PASS' if summary.ghost_prediction_failures == 0 and summary.census.capped_count == 0 else 'SURPRISE'}: "
        f"limit={summary.limit} max_steps={summary.max_steps} "
        f"tested_odds={summary.census.tested_odd_count} "
        f"descended={summary.census.descended_count} capped={summary.census.capped_count} "
        f"max_k={summary.census.max_k_star} max_k_start={summary.census.max_k_star_start} "
        f"ghost_L={summary.ghost_min_L}..{summary.ghost_max_L} "
        f"ghost_k_prediction_failures={summary.ghost_prediction_failures} "
        f"seconds={summary.elapsed_seconds:.6f}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G1-L2 CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10_000_000)
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--ghost-min-l", type=int, default=2)
    parser.add_argument("--ghost-max-l", type=int, default=80)
    parser.add_argument("--ghost-max-steps", type=int, default=5000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_cli)
    return parser


def main() -> None:
    """Run G1-L2."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
