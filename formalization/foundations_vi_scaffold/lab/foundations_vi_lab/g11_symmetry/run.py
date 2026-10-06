"""Command-line runner for the G11 Wang-tile SAT lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g11_symmetry.wang_sat import (
    CONTROL_TILES,
    JEANDEL_RAO_TILES,
    TorusInstance,
    solve_torus,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    control = summary["control"]
    jr_results = summary["jeandel_rao"]
    jr_rows = [
        f"`{result['rows']}x{result['cols']}` {result['status']} "
        f"({result['variables']} vars, {result['clauses']} clauses)"
        for result in jr_results
    ]
    path.write_text(
        "\n".join(
            [
                "# G11-L1 Verdict - Periodic-Defect Certificates On Wang Sets",
                "",
                "## Hypothesis",
                (
                    "The monochromatic two-tile control set is periodic-admissible, "
                    "while the Jeandel-Rao 11-tile set has no tiling on any tested "
                    "small torus."
                ),
                "",
                "## Outcome",
                (
                    f"PASS. The control set was SAT on a `{control['rows']}x{control['cols']}` "
                    f"torus with assignment `{control['assignment']}`."
                ),
                (
                    f"PASS. The Jeandel-Rao sweep tested every `p1 x p2` torus with "
                    f"`1 <= p1,p2 <= {summary['period_bound']}` and every instance was UNSAT."
                ),
                "Jeandel-Rao instances: " + "; ".join(jr_rows) + ".",
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                (
                    "The control instance supplies a case-(a) periodic-admissible witness. "
                    "The Jeandel-Rao UNSAT sweep supplies bounded small-period defect "
                    "certificates for case (b), consistent with the published aperiodicity theorem."
                ),
                "",
                "## Scope Note",
                (
                    "This lab tests rectangular `p1 x p2` torus period lattices only: "
                    "periods of the form `(p1,0)` and `(0,p2)` jointly realized as one "
                    "rectangular fundamental domain. It does not test arbitrary "
                    "non-axis-aligned period vectors `p=(a,b)` with both components "
                    "nonzero as a single period."
                ),
                (
                    "This lab also records only the full-instance UNSAT result and "
                    "commits the full DIMACS instance for each tested torus. It does "
                    "not extract UNSAT cores or minimize finite defect regions, so "
                    "`design/04_LABS.md`'s G11-L1 UNSAT-core/minimal-region refinement "
                    "remains future work."
                ),
                "",
                (
                    "This result exercises G11's Case Enumeration cases (a) and (b), and the "
                    "abstract `Hierarchy`/`ForcedBreaksPeriod` schema from "
                    "`SixBirdsFoundationsVI.Laws.G11GlobalAntiSymmetry`, made concrete at bounded "
                    "small-period SAT scale rather than as a specific Lean theorem."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g11_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G11-L1 and optionally write result artifacts."""

    dimacs_dir = args.results_dir / "G11-L1" / "dimacs"
    control = solve_torus(
        "control_1x1",
        TorusInstance(CONTROL_TILES, 1, 1),
        dimacs_path=dimacs_dir / "control_1x1.cnf",
    )
    if control.status != "SAT":
        raise AssertionError("control torus unexpectedly UNSAT")

    jr_results = []
    for rows in range(1, args.period_bound + 1):
        for cols in range(1, args.period_bound + 1):
            name = f"jeandel_rao_{rows}x{cols}"
            result = solve_torus(
                name,
                TorusInstance(JEANDEL_RAO_TILES, rows, cols),
                dimacs_path=dimacs_dir / f"{name}.cnf",
            )
            if result.status != "UNSAT":
                raise AssertionError(f"Jeandel-Rao instance {rows}x{cols} was SAT")
            jr_results.append(result)

    summary: dict[str, object] = {
        "period_bound": args.period_bound,
        "control": asdict(control),
        "jeandel_rao": [asdict(result) for result in jr_results],
    }
    if args.write_results:
        out_dir = args.results_dir / "G11-L1"
        _write_json(out_dir / "run.json", summary)
        _write_verdict(out_dir / "verdict.md", summary)

    result_summary = ",".join(f"{result.rows}x{result.cols}:{result.status}" for result in jr_results)
    print(
        "G11-L1 PASS: "
        f"control={control.status} assignment={control.assignment} "
        f"period_bound={args.period_bound} jeandel_rao={result_summary}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G11 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period-bound", type=int, default=4)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g11_l1)
    return parser


def main() -> None:
    """Run G11-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
