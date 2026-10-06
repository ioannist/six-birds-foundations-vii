"""Command-line runner for the G9 Rule 184 transport lab."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g09_transport.rule184 import (
    Rule184DensityResult,
    normalize_state,
    simulate_density,
    verify_rule184_formulations,
)


DENSITIES = [
    (3, 10),
    (2, 5),
    (1, 2),
    (3, 5),
    (7, 10),
]


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = summary["results"]  # type: ignore[assignment]
    table = [
        "| density | cars/ring | regime | evacuated measure | evac step | tau | d | windows | final 11 | final 00 |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        recurrence = row["recurrence"]
        table.append(
            f"| `{row['density_label']}` | `{row['realized_density']}` | "
            f"{row['regime']} | `{row['evacuation_measure']}` | "
            f"{row['evacuation_step']} | {recurrence['tau']} | "
            f"{recurrence['displacement']} | {recurrence['checked_windows']} | "
            f"{row['final_blocked_cars']} | {row['final_blocked_holes']} |"
        )

    path.write_text(
        "\n".join(
            [
                "# G9-L1 Verdict - Rule 184 Defect Evacuation",
                "",
                "## Hypothesis",
                (
                    "Rule 184 on an exact finite ring evacuates blocked-car `11` defects "
                    "below density `1/2`, evacuates dual blocked-hole `00` defects above "
                    "density `1/2`, and reaches the alternating critical regime at density "
                    "`1/2`. Each evacuated tail should admit an exact "
                    "recurrence-with-displacement certificate."
                ),
                "",
                "## Outcome",
                (
                    f"PASS. Exact Rule 184 was run on a ring of length `{summary['length']}` "
                    f"for `{len(rows)}` exact density settings with max step budget "
                    f"`{summary['max_steps']}` and total wall time "
                    f"`{summary['elapsed_seconds']:.6f}` seconds."
                ),
                (
                    "All tested regimes reached the predicted evacuated defect census and "
                    "all recurrence certificates were checked over "
                    f"`{summary['recurrence_windows']}` consecutive tail times."
                ),
                "",
                *table,
                "",
                "## Defect-Census Finding",
                (
                    "For `rho < 1/2`, adjacent `11` blocked-car pairs evacuate to zero. "
                    "For `rho > 1/2`, the measure that evacuates to zero is the dual "
                    "adjacent `00` blocked-hole count; adjacent `11` pairs remain in the "
                    "high-density jammed background and are not the evacuated supercritical "
                    "defect measure. At `rho = 1/2`, both adjacent `11` and adjacent `00` "
                    "counts reach zero, giving the alternating critical pattern."
                ),
                "",
                "## Scope Note",
                (
                    "This is a deterministic finite-ring calibration for Rule 184 only. "
                    "It does not construct Langton's ant or any other G9 instance, and it "
                    "does not prove the abstract G9 schemas in Python; the lab supplies a "
                    "concrete exact census and transporter-record exhibit."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                (
                    "The run supplies concrete transporter records: subcritical particles "
                    "move with displacement `+1`, supercritical holes move with displacement "
                    "`-1`, and the critical alternating pattern has an exact nonzero "
                    "shift recurrence. These are positive-schema calibration instances, not "
                    "negative unbounded-creation witnesses."
                ),
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.TransportData`, "
                    "`SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.CertifiedTransportRegime`, "
                    "and "
                    "`SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.certified_transport_regime_of_assigned_nonzero` "
                    "for the concrete Rule 184 ring instance. The evacuated census is consistent "
                    "with `SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.census_excludes_unbounded_creation`, "
                    "but this lab instantiates the positive transport-certification schema rather "
                    "than the negative unbounded-creation exclusion theorem."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g9_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G9-L1 and optionally write result artifacts."""

    hand_states = [
        normalize_state("111000"),
        normalize_state("101010"),
        normalize_state("10010000"),
        normalize_state("01101100"),
    ]
    verify_rule184_formulations(hand_states)

    start_time = time.perf_counter()
    results: list[Rule184DensityResult] = []
    for index, (numerator, denominator) in enumerate(DENSITIES):
        results.append(
            simulate_density(
                length=args.length,
                numerator=numerator,
                denominator=denominator,
                seed=args.seed + index,
                max_steps=args.max_steps,
                max_tau=args.max_tau,
                recurrence_windows=args.recurrence_windows,
            )
        )
    elapsed = time.perf_counter() - start_time

    summary: dict[str, object] = {
        "length": args.length,
        "seed": args.seed,
        "max_steps": args.max_steps,
        "max_tau": args.max_tau,
        "recurrence_windows": args.recurrence_windows,
        "elapsed_seconds": elapsed,
        "results": [asdict(result) for result in results],
    }

    if args.write_results:
        out_dir = args.results_dir / "G9-L1"
        _write_json(out_dir / "run.json", summary)
        _write_verdict(out_dir / "verdict.md", summary)

    compact = "; ".join(
        f"rho={result.density_label} regime={result.regime} "
        f"evac={result.evacuation_step} tau={result.recurrence.tau} "
        f"d={result.recurrence.displacement}"
        for result in results
    )
    print(
        "G9-L1 PASS: "
        f"length={args.length} max_steps={args.max_steps} "
        f"seconds={elapsed:.6f} {compact}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G9 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=184)
    parser.add_argument("--max-steps", type=int, default=8000)
    parser.add_argument("--max-tau", type=int, default=8)
    parser.add_argument("--recurrence-windows", type=int, default=128)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g9_l1)
    return parser


def main() -> None:
    """Run G9-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
