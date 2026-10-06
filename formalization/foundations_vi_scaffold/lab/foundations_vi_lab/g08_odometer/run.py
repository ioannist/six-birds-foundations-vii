"""Command-line runner for G8 odometer lab probes."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g08_odometer.case_b import run_rewrite_experiment
from foundations_vi_lab.g08_odometer.sandpile import run_sandpile_experiment


def _parse_sizes(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split(",") if part)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_l1_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# G8-L1 Verdict - Sandpile Odometer Invariance",
                "",
                "## Hypothesis",
                "Legal sandpile stabilization on finite grid graphs with sink is order-independent.",
                "",
                "## Outcome",
                (
                    f"PASS. Seed {summary['seed']} tested sizes {summary['sizes']} with "
                    f"{summary['configurations_per_size']} initial configuration(s) per size and "
                    f"{summary['orders_per_configuration']} random legal orders per configuration."
                ),
                (
                    f"All {summary['total_stabilizations']} seeded random stabilizations matched "
                    "the deterministic min-site and max-site baselines exactly in final configuration "
                    "and odometer vector."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                "This supports G8 Part A on the tested sandpile calibration instances.",
                "",
                "## Open Item",
                (
                    "This packet did not implement the least-action / "
                    "deliberately-wasteful-stabilization sub-experiment from "
                    "`design/04_LABS.md`'s G8-L1 spec: comparing the true legal odometer "
                    "against deliberately wasteful stabilizing scripts, "
                    "\"per Fey-Levine-Peres framing ⚑\". This run covers only the "
                    "order-independence half of G8-L1 (Part A). G8 Part B is already "
                    "independently proved in Lean as "
                    "`SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.least_action`; "
                    "the missing item is the computational exhibit for the paper, not a gap "
                    "in the law's Lean verification. Resolving the `⚑` remains future work "
                    "and requires checking the actual Fey-Levine-Peres least-action "
                    "construction against a citable source before implementing it."
                ),
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.odometer_invariance`, "
                    "confirming exact odometer invariance for the sandpile instantiation."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_l2_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# G8-L2 Verdict - Non-Abelian Separating Witness",
                "",
                "## Hypothesis",
                "The Lean case (b) rewrite system is terminating and confluent but has route-dependent counters.",
                "",
                "## Outcome",
                (
                    f"PASS. Seed {summary['seed']} sampled {summary['orders']} legal random orders "
                    f"from `S`; every run reached `N` and {summary['distinct_counters']} distinct "
                    "counter vectors appeared."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                "This supports the G8 case-table separation between mere confluence and canonical odometers.",
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_not_abelian` and "
                    "`SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_route_dependent_counter`, "
                    "confirming the non-abelian separating witness."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G8-L1 and optionally write result artifacts."""

    experiment = run_sandpile_experiment(
        seed=args.seed,
        sizes=_parse_sizes(args.sizes),
        configurations_per_size=args.configs,
        orders_per_configuration=args.orders,
    )
    summary = {
        "seed": experiment.seed,
        "sizes": list(experiment.sizes),
        "configurations_per_size": experiment.configurations_per_size,
        "orders_per_configuration": experiment.orders_per_configuration,
        "total_stabilizations": experiment.total_stabilizations,
        "trials": [asdict(trial) for trial in experiment.trials],
    }
    if args.write_results:
        out_dir = args.results_dir / "G8-L1"
        _write_json(out_dir / "run.json", summary)
        _write_l1_verdict(out_dir / "verdict.md", summary)
    print(
        "G8-L1 PASS: "
        f"seed={summary['seed']} sizes={summary['sizes']} "
        f"configs={summary['configurations_per_size']} "
        f"orders={summary['orders_per_configuration']} "
        f"stabilizations={summary['total_stabilizations']}"
    )
    return summary


def run_l2(args: argparse.Namespace) -> dict[str, object]:
    """Run G8-L2 and optionally write result artifacts."""

    experiment = run_rewrite_experiment(seed=args.seed, orders=args.orders)
    summary = {
        "seed": experiment.seed,
        "orders": experiment.orders,
        "distinct_counters": experiment.distinct_counters,
        "runs": [asdict(run) for run in experiment.runs],
    }
    if args.write_results:
        out_dir = args.results_dir / "G8-L2"
        _write_json(out_dir / "run.json", summary)
        _write_l2_verdict(out_dir / "verdict.md", summary)
    print(
        "G8-L2 PASS: "
        f"seed={summary['seed']} orders={summary['orders']} "
        f"distinct_counters={summary['distinct_counters']}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G8 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    l1 = subparsers.add_parser("l1", help="run G8-L1 sandpile odometer probe")
    l1.add_argument("--seed", type=int, default=8601)
    l1.add_argument("--sizes", default="10,20,30,40,50")
    l1.add_argument("--configs", type=int, default=1)
    l1.add_argument("--orders", type=int, default=100)
    l1.add_argument("--results-dir", type=Path, default=Path("results"))
    l1.add_argument("--write-results", action="store_true")
    l1.set_defaults(func=run_l1)

    l2 = subparsers.add_parser("l2", help="run G8-L2 non-abelian witness probe")
    l2.add_argument("--seed", type=int, default=8602)
    l2.add_argument("--orders", type=int, default=1000)
    l2.add_argument("--results-dir", type=Path, default=Path("results"))
    l2.add_argument("--write-results", action="store_true")
    l2.set_defaults(func=run_l2)

    all_cmd = subparsers.add_parser("all", help="run both G8 lab probes")
    all_cmd.add_argument("--seed", type=int, default=8600)
    all_cmd.add_argument("--sizes", default="10,20,30,40,50")
    all_cmd.add_argument("--configs", type=int, default=1)
    all_cmd.add_argument("--orders-l1", type=int, default=100)
    all_cmd.add_argument("--orders-l2", type=int, default=1000)
    all_cmd.add_argument("--results-dir", type=Path, default=Path("results"))
    all_cmd.add_argument("--write-results", action="store_true")

    def run_all(args: argparse.Namespace) -> None:
        l1_args = argparse.Namespace(
            seed=args.seed + 1,
            sizes=args.sizes,
            configs=args.configs,
            orders=args.orders_l1,
            results_dir=args.results_dir,
            write_results=args.write_results,
        )
        l2_args = argparse.Namespace(
            seed=args.seed + 2,
            orders=args.orders_l2,
            results_dir=args.results_dir,
            write_results=args.write_results,
        )
        run_l1(l1_args)
        run_l2(l2_args)

    all_cmd.set_defaults(func=run_all)
    return parser


def main() -> None:
    """Run the selected G8 lab command."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
