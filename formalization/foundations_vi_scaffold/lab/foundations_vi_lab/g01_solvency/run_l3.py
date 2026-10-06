"""Command-line runner for the G1 finite ghost-toy lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g01_solvency.ghost_toy import GhostToySummary, classify_all_residues


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_residue_list(values: tuple[int, ...], *, limit: int = 24) -> str:
    if not values:
        return "`[]`"
    shown = ", ".join(str(value) for value in values[:limit])
    if len(values) > limit:
        shown += f", ... ({len(values)} total)"
    return f"`[{shown}]`"


def _write_verdict(path: Path, summary: GhostToySummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    outcome = "PASS" if (
        summary.unclassified_count == 0
        and summary.native_separation_verified
        and summary.ghost_convergence_verified
    ) else "FAIL"
    cycle_text = (
        "No genuine nonterminal non-ghost bad cycles were found."
        if summary.genuine_bad_cycle_count == 0
        else f"Genuine nonterminal bad cycles found: `{summary.genuine_bad_cycles}`."
    )
    path.write_text(
        "\n".join(
            [
                "# G1-L3 Verdict - Finite Ghost Toy",
                "",
                "## Hypothesis",
                (
                    f"The finite accelerated-Collatz residue system on odd residues "
                    f"modulo `2^{summary.m}` should classify every native residue as "
                    "descending, declared-ghost-bound, or non-ghost bad-cycle-bound, "
                    "with zero unclassified residues."
                ),
                "",
                "## Outcome",
                (
                    f"{outcome}. Exhaustively classified `{summary.odd_residue_count}` "
                    f"odd residues modulo `{summary.modulus}` in "
                    f"`{summary.elapsed_seconds:.6f}` seconds."
                ),
                (
                    f"Terminal accepted residue: `{summary.terminal_residue}`. "
                    f"Nonterminal residues: `{summary.nonterminal_residue_count}`. "
                    f"Descended: `{summary.descended_count}`. Declared-ghost-bound: "
                    f"`{summary.ghost_bound_count}`. Genuine nonterminal bad-cycle "
                    f"starts: `{summary.genuine_bad_cycle_start_count}`. "
                    f"Unclassified: `{summary.unclassified_count}`."
                ),
                (
                    f"Maximum descent step among separating residues: "
                    f"`{summary.max_descent_step}` at residue "
                    f"`{summary.max_descent_start}`."
                ),
                "",
                "## Gamma_m",
                (
                    f"The declared ghost residue is `{summary.ghost_residue}`, the unique "
                    f"odd solution of `3*r+1 == 0 mod 2^{summary.m}`. For this `m`, "
                    f"the closed form is `{summary.ghost_residue_formula}`."
                ),
                (
                    f"The raw classifier also detects the fixed cycle `(1,)`. This is "
                    "not a new toy-specific obstruction: it is the same accelerated "
                    "Collatz terminal fixed point named in G1's Setup, where "
                    "`3*1+1=4`, `nu_2(4)=2`, and therefore `T(1)=1`. Matching the "
                    "abstract law's ordering, residue `1` is Case (a) terminal in "
                    "`A={1}` and is excluded before bad-tail/Gamma bookkeeping."
                ),
                (
                    f"With residue `1` excluded as terminal, corrected "
                    f"`Gamma_{summary.m}` has `{len(summary.gamma_nonterminal_residues)}` "
                    f"nonterminal starting residue(s): "
                    f"{_format_residue_list(summary.gamma_nonterminal_residues)}."
                ),
                cycle_text,
                "",
                "## Hypothesis Checks",
                (
                    f"`NativeSeparation` finite analogue: "
                    f"`{summary.native_separation_verified}`. Every nonterminal residue "
                    f"outside corrected `Gamma_{summary.m}` has an explicit computed "
                    "descent horizon `K=k*(r)`; residue `1` is discharged first as "
                    "terminal."
                ),
                (
                    f"`GhostConvergence` finite analogue: "
                    f"`{summary.ghost_convergence_verified}`. Every nonterminal residue "
                    f"in corrected `Gamma_{summary.m}` reaches the declared ghost before "
                    "any descent, and there are no genuine nonterminal bad cycles for "
                    f"`m={summary.m}`."
                ),
                "",
                "## Surprise",
                (
                    "None remains after applying the abstract law's terminal-first "
                    "ordering. The raw `(1,)` cycle is exactly the known `T(1)=1` "
                    "accepted terminal fixed point, not a genuine nonterminal bad "
                    "cycle or a new ghost obstruction."
                    if summary.genuine_bad_cycle_count == 0
                    else "Genuine nonterminal bad cycles appeared and are recorded above."
                ),
                "",
                "## Scope Note",
                (
                    "This is a finite toy model of G1's ghost machinery. It genuinely "
                    "discharges the finite instance's `GhostConvergence` and "
                    "`NativeSeparation` analogues, showing that the abstract hypotheses "
                    "are checkable and non-vacuous in principle."
                ),
                (
                    "It does not discharge those hypotheses for the actual infinite "
                    "Collatz system, does not construct the real `2`-adic completion, "
                    "and does not prove or make progress on the Collatz conjecture."
                ),
                "",
                (
                    "This result instantiates "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.GhostConvergence` "
                    "and "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.NativeSeparation` "
                    "for the finite residue-ring toy model, and therefore exercises the "
                    "conditional shape of "
                    "`SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge` "
                    "in a fully finite worked instance. It makes no claim that the real "
                    "Collatz instance satisfies those hypotheses."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_cli(args: argparse.Namespace) -> GhostToySummary:
    summary = classify_all_residues(args.m)
    if args.write_results:
        out_dir = args.results_dir / "G1-L3"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G1-L3 "
        f"{'PASS' if summary.unclassified_count == 0 else 'FAIL'}: "
        f"m={summary.m} odd_residues={summary.odd_residue_count} "
        f"descended={summary.descended_count} "
        f"ghost_bound={summary.ghost_bound_count} "
        f"bad_cycle_starts={summary.bad_cycle_start_count} "
        f"bad_cycles={summary.bad_cycle_count} "
        f"unclassified={summary.unclassified_count} "
        f"ghost_residue={summary.ghost_residue} "
        f"seconds={summary.elapsed_seconds:.6f}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m", type=int, default=16)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_cli)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
