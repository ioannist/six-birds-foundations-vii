"""Command-line runner for the G6 tunable Recaman-variant lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g06_needle.tunable import TunableSummary, verify_tunable_variants


PROOFS_TEXT = """# G6-L2 Proofs - Tunable Recaman Variants

## Variant A: even-jump permanent holes

Define `a_0 = 0`. At step `n >= 1`, set `candidate = a_{n-1} - 2n`; if
`candidate > 0` and has not been visited, set `a_n = candidate`, otherwise set
`a_n = a_{n-1} + 2n`.

Claim: every `a_n` is even.

Proof: By induction on `n`. The base case is `a_0 = 0`, which is even. For the
inductive step, assume `a_{n-1}` is even. The jump `2n` is even, so both
`a_{n-1} - 2n` and `a_{n-1} + 2n` are even. The recurrence chooses one of these
two values, so `a_n` is even. Therefore every term is even.

Consequently no odd positive integer is ever visited. For any fixed odd target
`y`, define `visited_y(n)` to mean that `y` appears among `a_0,...,a_n`.
The parity invariant proves `¬ visited_y(n)` for every `n`; in particular
`¬ visited_y(0)`, and the implication `¬ visited_y(n) -> ¬ visited_y(n+1)` holds
for every `n`. Thus Variant A supplies `DominantObstruction visited_y 0`, and
G6's `hole_forming_schema` applies to every odd `y`.

## Variant B: constant-unit full coverage

Define `a_0 = 0`. At step `n >= 1`, set `candidate = a_{n-1} - 1`; if
`candidate > 0` and has not been visited, set `a_n = candidate`, otherwise set
`a_n = a_{n-1} + 1`.

Claim: for every `n >= 0`, `a_n = n`, and after step `n` the visited set is
exactly `{0,1,...,n}`.

Proof: Use induction on `n` with the invariant
`a_n = n` and `V_n = {0,1,...,n}`, where `V_n` is the set of values visited
through step `n`. The base case is `n=0`: `a_0=0` and `V_0={0}`. For the
inductive step, assume `a_n=n` and `V_n={0,1,...,n}`. At step `n+1`, the
candidate is `a_n - 1 = n - 1`. If `n=0`, this candidate is `-1`, not positive,
so the forward branch gives `a_1=1`. If `n>0`, then `n-1` is already in
`V_n`, so the backward branch is blocked. In all cases the recurrence takes the
forward branch and sets `a_{n+1}=a_n+1=n+1`. Therefore
`V_{n+1}=V_n ∪ {n+1}={0,1,...,n+1}`. The invariant holds for all `n`.

For any finite audit window `W_M={1,...,M}`, the hole count after step `n` is
`holes_M(n)=max(M-n,0)`. Whenever `holes_M(n)>0`, we have `n<M`, so
`holes_M(n+1)=holes_M(n)-1 < holes_M(n)`. This discharges
`DominantPressure holes_M`, and G6's `covering_schema` applies to every fixed
finite window.
"""


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_proofs(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PROOFS_TEXT, encoding="utf-8")


def _write_verdict(path: Path, summary: TunableSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    even = summary.even_jump
    unit = summary.unit_jump
    status = "PASS" if even.all_even and unit.identity_holds and unit.visited_set_exact else "FAIL"
    path.write_text(
        "\n".join(
            [
                "# G6-L2 Verdict - Tunable Recaman Variants",
                "",
                "## Hypothesis",
                (
                    "Variant A with jump `2n` should visit only even values, making "
                    "all odd positive integers permanent holes. Variant B with constant "
                    "jump `1` should satisfy `a_n=n` and visit exactly `{0,...,n}` "
                    "after step `n`."
                ),
                "",
                "## Outcome",
                f"{status}.",
                (
                    f"Variant A checked `{even.steps}` steps: all-even=`{even.all_even}`, "
                    f"unique visited=`{even.unique_visited}`, final=`{even.final_value}`, "
                    f"max=`{even.max_value}`, odd violations recorded=`{len(even.odd_violations)}`."
                ),
                (
                    f"Variant B checked `{unit.steps}` steps: identity holds=`{unit.identity_holds}`, "
                    f"visited set exact=`{unit.visited_set_exact}`, unique visited=`{unit.unique_visited}`, "
                    f"final=`{unit.final_value}`, max=`{unit.max_value}`."
                ),
                "",
                "## Proof Artifacts",
                (
                    "`lab/results/G6-L2-proofs.md` records the parity-invariant proof "
                    "for Variant A and the exact visited-set induction proof for Variant B."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Scope Note",
                (
                    "This is a genuine worked instantiation of both abstract G6 schemas "
                    "for deliberately simplified tunable variants. It says nothing about "
                    "the original Recaman sequence's open coverage question."
                ),
                (
                    "Variant A discharges `DominantObstruction visited_y 0` for every odd "
                    "target `y`, because the parity invariant proves `visited_y(n)` is "
                    "always false. This instantiates `hole_forming_schema`."
                ),
                (
                    "Variant B discharges `DominantPressure holes_M` for every finite "
                    "window `W_M={1,...,M}`, because `holes_M(n)=max(M-n,0)` strictly "
                    "decreases whenever positive. This instantiates `covering_schema`."
                ),
                "",
                (
                    "Traceability: Variant A is a concrete proof instance of "
                    "`SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration.hole_forming_schema`; "
                    "Variant B is a concrete proof instance of "
                    "`SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration.covering_schema`. "
                    "Neither variant is the original Recaman recurrence."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g6_l2(args: argparse.Namespace) -> TunableSummary:
    """Run G6-L2 and optionally write result artifacts."""

    summary = verify_tunable_variants(
        even_steps=args.even_steps,
        unit_steps=args.unit_steps,
    )
    if args.write_results:
        _write_proofs(args.results_dir / "G6-L2-proofs.md")
        out_dir = args.results_dir / "G6-L2"
        _write_json(out_dir / "run.json", asdict(summary))
        _write_verdict(out_dir / "verdict.md", summary)
    status = (
        "PASS"
        if summary.even_jump.all_even
        and summary.unit_jump.identity_holds
        and summary.unit_jump.visited_set_exact
        else "FAIL"
    )
    print(
        "G6-L2 "
        f"{status}: even_steps={summary.even_jump.steps} "
        f"all_even={summary.even_jump.all_even} "
        f"unit_steps={summary.unit_jump.steps} "
        f"identity={summary.unit_jump.identity_holds} "
        f"visited_exact={summary.unit_jump.visited_set_exact}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G6-L2 CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--even-steps", type=int, default=1_000_000)
    parser.add_argument("--unit-steps", type=int, default=1_000_000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g6_l2)
    return parser


def main() -> None:
    """Run G6-L2."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
