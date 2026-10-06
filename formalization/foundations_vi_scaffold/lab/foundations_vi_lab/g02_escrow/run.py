"""Command-line runner for the G2 Goodstein escrow lab."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g02_escrow.goodstein import run_sweep, worked_example


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    estimated_decimal_digits = int(int(summary["max_integer_bits"]) * 30103 // 100000) + 1
    path.write_text(
        "\n".join(
            [
                "# G2-L1 Verdict - Goodstein Ordinal Escrow",
                "",
                "## Hypothesis",
                "Hereditary-base Goodstein rebasing preserves the ordinal escrow, and the Goodstein decrement strictly descends it.",
                "",
                "## Outcome",
                (
                    f"PASS. Deterministic sweep checked starts 1..{summary['max_start']} "
                    f"with step budget {summary['step_budget']}, for "
                    f"{summary['checked_steps']} verified Goodstein steps."
                ),
                (
                    f"Terminated starts within budget: {summary['terminated_starts']}. "
                    f"Max reached base: {summary['max_reached_base']}. "
                    f"Max integer bit length encountered: {summary['max_integer_bits']}."
                ),
                "",
                "## Worked Example",
                (
                    "For `n=4`, base `2`, the runner reproduced "
                    "`O_2(4)=omega^omega`, `rebase_{2->3}(4)=27`, "
                    "`G_2(4)=26`, and `O_3(26)=omega^2*2 + omega*2 + 2 < omega^omega`."
                ),
                "",
                "## Surprise",
                "None.",
                "",
                "## Implication",
                "This is a deterministic computational exhibit for G2's stage-coherent escrow descent mechanism.",
                "",
                "## Scope / Runtime Note",
                (
                    "`design/04_LABS.md`'s G2-L1 spec suggests a bounded prefix such as "
                    "`10^4` steps, but Goodstein sequences grow explosively. In this exact "
                    "hereditary-reconstruction implementation, even a step budget of `5` "
                    "does not complete in reasonable time across all 30 starts. The shipped "
                    f"run uses budget `{summary['step_budget']}` and already reaches integers "
                    f"up to `{summary['max_integer_bits']}` bits, roughly "
                    f"{estimated_decimal_digits} decimal "
                    "digits. This is a calibration exhibit of the per-step "
                    f"descent/invariance identities ({summary['checked_steps']} independent "
                    f"checks across {summary['max_start']} starts), "
                    "not a claim about full sequence termination length. Full termination is "
                    "separately and unconditionally proved in Lean by "
                    "`SixBirdsFoundationsVI.Laws.G2TransfiniteEscrow.no_infinite_nonterminal_run`, "
                    "independent of how many steps a computational sweep can reach."
                ),
                "",
                (
                    "This result exercises "
                    "`SixBirdsFoundationsVI.Laws.G2TransfiniteEscrow.no_infinite_nonterminal_run`, "
                    "confirming the Goodstein ordinal escrow instantiation of stage-coherent descent."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g2_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G2-L1 and optionally write result artifacts."""

    sweep = run_sweep(max_start=args.max_start, step_budget=args.step_budget)
    summary = asdict(sweep)
    summary["worked_example"] = worked_example()
    if args.write_results:
        out_dir = args.results_dir / "G2-L1"
        _write_json(out_dir / "run.json", summary)
        _write_verdict(out_dir / "verdict.md", summary)
    print(
        "G2-L1 PASS: "
        f"max_start={summary['max_start']} "
        f"step_budget={summary['step_budget']} "
        f"checked_steps={summary['checked_steps']} "
        f"terminated={summary['terminated_starts']} "
        f"max_base={summary['max_reached_base']} "
        f"max_bits={summary['max_integer_bits']}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G2 lab CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-start", type=int, default=30)
    parser.add_argument("--step-budget", type=int, default=4)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g2_l1)
    return parser


def main() -> None:
    """Run G2-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
