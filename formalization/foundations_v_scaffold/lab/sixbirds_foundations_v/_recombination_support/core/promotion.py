from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


PROMOTION_RULE_VERSION = "ticket17.discovery.v1"
PREFERRED_PROMOTION_LABELS = {"coherent_branch_candidate", "erasure_recovery"}


@dataclass(frozen=True)
class RankedCase:
    row: dict[str, Any]
    rank: int
    eligible: bool


def promotion_eligible(row: Mapping[str, Any]) -> bool:
    if str(row.get("class_label", "")) not in PREFERRED_PROMOTION_LABELS:
        return False
    if str(row.get("protocol_internalization_status", "skipped")) == "failed":
        return False
    if str(row.get("flattening_status", "skipped")) == "failed":
        return False
    return True


def rank_candidates(rows: list[dict[str, Any]]) -> list[RankedCase]:
    ranked_rows = sorted(rows, key=_ranking_key)
    return [
        RankedCase(row=dict(row), rank=index, eligible=promotion_eligible(row))
        for index, row in enumerate(ranked_rows, start=1)
    ]


def build_ranked_candidates_payload(
    *,
    search_id: str,
    search_space_id: str,
    ranked_cases: list[RankedCase],
    promotion_limit: int,
) -> dict[str, Any]:
    promoted_count = sum(1 for case in ranked_cases if case.eligible and case.rank <= promotion_limit)
    verdict = (
        "promotable_candidates_found"
        if promoted_count > 0
        else "no_promotable_candidates_found"
    )
    return {
        "search_id": search_id,
        "search_space_id": search_space_id,
        "promotion_limit": promotion_limit,
        "promotion_rule_version": PROMOTION_RULE_VERSION,
        "verdict": verdict,
        "ranked_candidates": [
            _ranked_case_payload(case)
            for case in ranked_cases
        ],
    }


def build_open_issues_payload(
    *,
    search_id: str,
    ranked_cases: list[RankedCase],
    promotion_limit: int,
) -> dict[str, Any]:
    unclassified_cases = [
        {
            "case_id": case.row["case_id"],
            "class_label": case.row["class_label"],
            "reason": "classifier fell through to unclassified_fallback",
        }
        for case in ranked_cases
        if str(case.row.get("class_label")) == "unclassified"
    ]
    demoted_by_audit = [
        {
            "case_id": case.row["case_id"],
            "protocol_internalization_status": case.row.get(
                "protocol_internalization_status",
                "skipped",
            ),
            "flattening_status": case.row.get("flattening_status", "skipped"),
        }
        for case in ranked_cases
        if str(case.row.get("protocol_internalization_status", "skipped")) == "failed"
        or str(case.row.get("flattening_status", "skipped")) == "failed"
    ]
    borderline_cases = [
        {
            "case_id": case.row["case_id"],
            "promotion_rank": case.rank,
            "class_label": case.row["class_label"],
            "recombination_gap_value": case.row["recombination_gap_value"],
            "visibility_recovery_gap": case.row["visibility_recovery_gap"],
        }
        for case in ranked_cases
        if case.eligible and case.rank > promotion_limit
    ]
    follow_up_tuning_hypotheses = []
    if unclassified_cases:
        follow_up_tuning_hypotheses.append(
            "Unclassified symmetric equal-weight cases may need either richer observables or explicit symmetry-aware classifier refinement."
        )
    if borderline_cases:
        follow_up_tuning_hypotheses.append(
            "Borderline positive cases below the shortlist cut line are plausible robustness-sweep inputs if the top shortlist destabilizes later."
        )
    return {
        "search_id": search_id,
        "promotion_rule_version": PROMOTION_RULE_VERSION,
        "unclassified_cases": unclassified_cases,
        "borderline_cases": borderline_cases,
        "demoted_by_audit": demoted_by_audit,
        "follow_up_tuning_hypotheses": follow_up_tuning_hypotheses,
        "verdict": "open_issues_recorded",
    }


def build_promoted_benchmark_config_payload(
    row: Mapping[str, Any],
    *,
    rank: int,
) -> dict[str, Any]:
    case_id = str(row["case_id"])
    return {
        "schema_version": "recombination-benchmark-run-config.v1",
        "config_kind": "benchmark-run",
        "config_id": f"promoted_{case_id}",
        "benchmark_id": "relative_cycle_carrier_base",
        "interface_id": "mid",
        "assemblage_family_id": "relative_cycle_promoted_dynamic_family",
        "observable_family_id": "relative_cycle_promoted_dynamic_observable_family",
        "carrier_size": int(row["carrier_size"]),
        "route_shift_delta": int(row["route_shift_delta"]),
        "weight_left": str(row["weight_left"]),
        "weight_right": str(row["weight_right"]),
        "seed": 0,
        "run_id": f"run_promoted_{case_id}_seed0",
        "generate_plot_artifacts": False,
        "tags": [
            "promoted_candidate",
            "ticket17_discovery",
            f"promotion_rank_{rank}",
        ],
    }


def write_promoted_benchmark_config(
    row: Mapping[str, Any],
    *,
    rank: int,
    config_root: Path,
) -> Path:
    promoted_dir = config_root / "configs" / "recombination" / "benchmarks" / "promoted"
    promoted_dir.mkdir(parents=True, exist_ok=True)
    config_path = promoted_dir / f"{row['case_id']}.json"
    payload = build_promoted_benchmark_config_payload(row, rank=rank)
    config_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return config_path


def build_promoted_candidates_payload(
    *,
    search_id: str,
    promoted_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    verdict = (
        "promoted_candidates_materialized"
        if promoted_candidates
        else "no_promotable_candidates_found"
    )
    return {
        "search_id": search_id,
        "promotion_rule_version": PROMOTION_RULE_VERSION,
        "promoted_count": len(promoted_candidates),
        "verdict": verdict,
        "promoted_candidates": promoted_candidates,
    }


def _ranking_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    eligible = promotion_eligible(row)
    recombination_gap = Fraction(str(row.get("recombination_gap_value", "0")))
    eta = int(row.get("eta_max_fiber_size", 0))
    visibility_gap = Fraction(str(row.get("visibility_recovery_gap", "0")))
    readability = Fraction(str(row.get("route_readability_score", "0")))
    weight_left = Fraction(str(row.get("weight_left", "0")))
    weight_right = Fraction(str(row.get("weight_right", "0")))
    unequal_weights = weight_left != weight_right
    carrier_size = int(row.get("carrier_size", 0))
    return (
        0 if eligible else 1,
        -recombination_gap,
        -eta,
        -visibility_gap,
        readability,
        0 if unequal_weights else 1,
        -carrier_size,
        str(row.get("case_id", "")),
    )


def _ranked_case_payload(case: RankedCase) -> dict[str, Any]:
    payload = dict(case.row)
    payload["promotion_rank"] = case.rank
    payload["promotion_eligible"] = case.eligible
    return payload


__all__ = [
    "PROMOTION_RULE_VERSION",
    "PREFERRED_PROMOTION_LABELS",
    "RankedCase",
    "build_open_issues_payload",
    "build_promoted_benchmark_config_payload",
    "build_promoted_candidates_payload",
    "build_ranked_candidates_payload",
    "promotion_eligible",
    "rank_candidates",
    "write_promoted_benchmark_config",
]
