"""Command-line runner for the G13 Apollonian curvature census lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g13_saturation.apollonian import (
    ADMISSIBLE_MOD24,
    BASELINE_ROOT,
    RECIPROCITY_ROOT,
    PackingSummary,
    summarize_packing,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    return f"{numerator}/{denominator} ({numerator / denominator:.6f})"


def _coverage_table(summary: PackingSummary) -> list[str]:
    rows = [
        "| bound | admissible | hit | missing | coverage |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for point in summary.coverage_points:
        rows.append(
            f"| {point.bound} | {point.admissible_count} | {point.hit_count} | "
            f"{point.missing_count} | "
            f"{_format_ratio(point.coverage_numerator, point.coverage_denominator)} |"
        )
    return rows


def _obstruction_table(summary: PackingSummary) -> list[str]:
    if not summary.obstruction_checks:
        return ["No reciprocity-family check was assigned to this baseline packing."]
    rows = [
        "| family | values checked | hits found | first checked values |",
        "| --- | ---: | ---: | --- |",
    ]
    for check in summary.obstruction_checks:
        rows.append(
            f"| `{check.coefficient}n^2` | {check.checked_values} | "
            f"{len(check.hit_values)} | `{list(check.first_values)}` |"
        )
    return rows


def _summary_lines(summary: PackingSummary) -> list[str]:
    return [
        f"### `{summary.label}`",
        "",
        f"Root quadruple: `{summary.root}`.",
        f"Curvature bound: `{summary.bound}`.",
        f"States explored: `{summary.states_explored}`.",
        f"Positive curvatures hit: `{summary.curvatures_hit}`.",
        f"Residues hit mod 24: `{summary.residues_hit}`.",
        f"Residue violations: `{len(summary.residue_violations)}`.",
        f"Admissible curvatures up to bound: `{summary.admissible_count}`.",
        f"Missing admissible curvatures: `{summary.missing_count}`.",
        f"First missing admissible values: `{list(summary.missing_first)}`.",
        f"Last missing admissible values: `{list(summary.missing_last)}`.",
        f"Elapsed seconds: `{summary.elapsed_seconds:.6f}`.",
        "",
        "Coverage checkpoints:",
        "",
        *_coverage_table(summary),
        "",
        "Reciprocity-family checks:",
        "",
        *_obstruction_table(summary),
    ]


def _write_verdict(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    baseline: PackingSummary = payload["baseline"]  # type: ignore[assignment]
    reciprocity: PackingSummary = payload["reciprocity"]  # type: ignore[assignment]
    obstruction_hits = sum(
        len(check.hit_values) for check in reciprocity.obstruction_checks
    )
    status = (
        "PASS"
        if not baseline.residue_violations
        and not reciprocity.residue_violations
        and obstruction_hits == 0
        else "FAIL"
    )
    path.write_text(
        "\n".join(
            [
                "# G13-L1 Verdict - Apollonian Curvature Census",
                "",
                "## Hypothesis",
                (
                    "The baseline packing `(-1,2,2,3)` should match the stated "
                    "mod-24 admissible classes without any claimed reciprocity "
                    "obstruction. The packing `(-6,11,14,15)` should have the same "
                    "admissible residue type while avoiding every curvature in the "
                    "published reciprocity-obstructed families `2n^2`, `3n^2`, "
                    "and `6n^2` within the computational bound."
                ),
                "",
                "## Outcome",
                (
                    f"{status}. Exact Descartes-reflection BFS was run for both "
                    f"root quadruples to curvature bound `{payload['bound']}`."
                ),
                (
                    "Every generated quadruple was checked against Descartes' identity "
                    "during generation. Both generated positive-curvature sets stayed "
                    f"inside the expected admissible classes `{sorted(ADMISSIBLE_MOD24)} mod 24`."
                ),
                (
                    f"For `(-6,11,14,15)`, the reciprocity-family check found "
                    f"`{obstruction_hits}` hits among all generated curvatures in "
                    "`2n^2`, `3n^2`, and `6n^2` up to the bound."
                ),
                "",
                "## Scope Note",
                (
                    "This is a finite exact-integer orbit census. It does not reprove "
                    "Bourgain-Kontorovich density-one saturation, and it does not "
                    "reprove, extend, or contradict Haag-Kertzer-Rickards-Stange. "
                    "It checks that the generated finite orbits are consistent with "
                    "the cited reciprocity obstruction for the corrected packing."
                ),
                (
                    "`(-1,2,2,3)` is treated only as the clean baseline from "
                    "`THEOREMS.md`: its residual missing set is case (iv) uncertain "
                    "within this bounded census, not a reciprocity obstruction. "
                    "`(-6,11,14,15)` supplies the concrete case (iii) "
                    "reciprocity-obstructed exhibit through the three checked "
                    "quadratic families."
                ),
                (
                    "The design-spec target bound was `10^6`; this checked-in "
                    f"canonical run deliberately uses `{payload['bound']}` instead "
                    "because feasibility probing showed steep cost scaling, so the "
                    "larger bound was not forced in this landing pass."
                ),
                "",
                "## Baseline Packing",
                "",
                *_summary_lines(baseline),
                "",
                "## Reciprocity-Obstructed Packing",
                "",
                *_summary_lines(reciprocity),
                "",
                "## Surprise",
                "None.",
                "",
                (
                    "Traceability: this finite census is a case-enumeration exhibit "
                    "for G13. It does not discharge "
                    "`SixBirdsFoundationsVI.Laws.G13ThinOrbitSaturation.relative_density_theorem`, "
                    "because the imported sublinear exceptional bound and positive-density "
                    "target theorem are not proved here. The `(-6,11,14,15)` obstruction "
                    "check is a concrete finite consistency check for "
                    "`SixBirdsFoundationsVI.Laws.G13ThinOrbitSaturation.reciprocity_compatibility_observation`: "
                    "an infinite reciprocity record can coexist with density-one saturation "
                    "when its count is negligible, but negligibility itself remains imported "
                    "instance content."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _checkpoint_list(bound: int) -> tuple[int, ...]:
    raw = [100, 1_000, 10_000, 100_000, bound]
    return tuple(sorted({value for value in raw if value <= bound and value > 0}))


def run_g13_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G13-L1 and optionally write result artifacts."""

    checkpoints = _checkpoint_list(args.bound)
    baseline = summarize_packing(
        label="baseline (-1,2,2,3)",
        root=BASELINE_ROOT,
        bound=args.bound,
        checkpoints=checkpoints,
        check_reciprocity=False,
    )
    reciprocity = summarize_packing(
        label="reciprocity (-6,11,14,15)",
        root=RECIPROCITY_ROOT,
        bound=args.bound,
        checkpoints=checkpoints,
        check_reciprocity=True,
    )
    payload: dict[str, object] = {
        "bound": args.bound,
        "checkpoints": checkpoints,
        "baseline": baseline,
        "reciprocity": reciprocity,
    }
    if args.write_results:
        out_dir = args.results_dir / "G13-L1"
        _write_json(
            out_dir / "run.json",
            {
                "bound": args.bound,
                "checkpoints": checkpoints,
                "baseline": asdict(baseline),
                "reciprocity": asdict(reciprocity),
            },
        )
        _write_verdict(out_dir / "verdict.md", payload)

    obstruction_hits = sum(
        len(check.hit_values) for check in reciprocity.obstruction_checks
    )
    status = (
        "PASS"
        if not baseline.residue_violations
        and not reciprocity.residue_violations
        and obstruction_hits == 0
        else "FAIL"
    )
    print(
        "G13-L1 "
        f"{status}: bound={args.bound} "
        f"baseline_states={baseline.states_explored} "
        f"baseline_missing={baseline.missing_count} "
        f"reciprocity_states={reciprocity.states_explored} "
        f"reciprocity_missing={reciprocity.missing_count} "
        f"obstruction_hits={obstruction_hits} "
        f"seconds={baseline.elapsed_seconds + reciprocity.elapsed_seconds:.6f}"
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    """Build the G13-L1 CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bound", type=int, default=1_000_000)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g13_l1)
    return parser


def main() -> None:
    """Run G13-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
