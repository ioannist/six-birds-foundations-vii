"""Command-line runner for the G5 base-2 confinement lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g05_confinement.reverse_add import (
    G5RunSummary,
    verify_g5_l1,
    worked_first_cycle,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: G5RunSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    first_cycle = "; ".join(f"`R({before})={after}`" for before, after in worked_first_cycle())
    path.write_text(
        "\n".join(
            [
                "# G5-L1 Verdict - Base-2 Reverse-and-Add Confinement",
                "",
                "## Hypothesis",
                (
                    "`22 = 10110_2` enters the four-phase target-free language "
                    "`P0(r) -> P1(r) -> P2(r) -> P3(r) -> P0(r+1)` under "
                    "`R(n)=n+rev_2(n)`, and no checked phase-family iterate is a palindrome."
                ),
                "",
                "## Outcome",
                (
                    f"PASS. Starting seed `{summary.seed}` followed the exact pre-entry "
                    f"segment `{' -> '.join(summary.pre_entry_strings)}` and then completed "
                    f"{summary.cycles} full phase cycles."
                ),
                (
                    f"The phase-family sweep checked `{summary.phase_transitions}` "
                    f"reverse-and-add transitions and `{summary.phase_transitions + 1}` "
                    f"phase states, ending at `{summary.final_binary}` "
                    f"(`P0({summary.final_r})`)."
                ),
                (
                    f"Total reverse-and-add steps from the seed were "
                    f"`{summary.total_reverse_add_steps}`; the largest checked binary string "
                    f"had `{summary.max_bit_length}` bits."
                ),
                "",
                "## Worked First Cycle",
                first_cycle + ".",
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                (
                    "This is an exact-integer computational exhibit for G5's closed-pattern "
                    "confinement schema: after finite entry into `Pcal = P0 ∪ P1 ∪ P2 ∪ P3`, "
                    "closure under `R_2` and target-freeness keep the orbit out of binary "
                    "palindromes for every checked cycle."
                ),
                "",
                "## Scope Note",
                (
                    "This is a finite exact-integer sweep of the four phase identities "
                    f"from one entry point over `{summary.cycles}` checked cycles. "
                    "It is not an independent proof that `R(P_i(r))` follows the claimed "
                    "phase cycle for all `r`. The universal confinement theorem is the "
                    "Lean-abstract `closed_pattern_confinement`, which takes "
                    "`[H-G5-closed-pattern]` (`ClosedUnderR`/`TargetFree`) as a supplied "
                    "hypothesis; this lab calibrates that hypothesis's concrete instance "
                    "over a bounded run, rather than re-deriving it for unboundedly many `r`."
                ),
                "",
                (
                    "This packet does not explore base-10 Lychrel candidates such as `196`; "
                    "G5's nonclaims keep that question open unless a closed target-free "
                    "certificate is supplied."
                ),
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G5CarryHorizonConfinement.closed_pattern_confinement` "
                    "for the concrete instance `R = R_2`, `Target = Pal_2`, and "
                    "`Pcal = P0 ∪ P1 ∪ P2 ∪ P3`."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g5_l1(args: argparse.Namespace) -> G5RunSummary:
    """Run G5-L1 and optionally write result artifacts."""

    summary = verify_g5_l1(seed=args.seed, cycles=args.cycles)
    if args.write_results:
        out_dir = args.results_dir / "G5-L1"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G5-L1 PASS: "
        f"seed={summary.seed} cycles={summary.cycles} "
        f"phase_transitions={summary.phase_transitions} "
        f"total_steps={summary.total_reverse_add_steps} "
        f"final={summary.final_binary} final_phase=P0({summary.final_r})"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G5 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=22)
    parser.add_argument("--cycles", type=int, default=20)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g5_l1)
    return parser


def main() -> None:
    """Run G5-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
