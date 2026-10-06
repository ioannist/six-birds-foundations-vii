from __future__ import annotations

import json
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from .relative_cycle import RelativeCycleParameters, normalize_relative_cycle_parameters


PROMOTED_CANDIDATES_PATH = (
    Path("results")
    / "derived"
    / "search_cyclic_relative_carrier_discovery_seed0"
    / "promoted_candidates.json"
)
ROBUSTNESS_RULE_VERSION = "ticket18.robustness.v1"
POSITIVE_LABELS = {"coherent_branch_candidate", "erasure_recovery"}
_CANDIDATE_ID_RE = re.compile(
    r"^n(?P<carrier>\d+)_d(?P<delta>\d+)_w(?P<left_num>\d+)of(?P<left_den>\d+)_(?P<right_num>\d+)of(?P<right_den>\d+)$"
)


@dataclass(frozen=True)
class ThresholdProfile:
    name: str
    min_recombination_gap: Fraction
    min_visibility_recovery_gap: Fraction
    max_route_readability: Fraction


@dataclass(frozen=True)
class CandidateReference:
    candidate_id: str
    reference_run_id: str
    parameters: RelativeCycleParameters
    config_path: str


def load_promoted_candidate_references(repo_root: Path) -> dict[str, CandidateReference]:
    promoted_payload = json.loads(
        (repo_root / PROMOTED_CANDIDATES_PATH).read_text(encoding="utf-8")
    )
    references: dict[str, CandidateReference] = {}
    for candidate in promoted_payload["promoted_candidates"]:
        candidate_id = str(candidate["case_id"])
        references[candidate_id] = CandidateReference(
            candidate_id=candidate_id,
            reference_run_id=str(candidate["run_id"]),
            parameters=parse_candidate_id(candidate_id),
            config_path=str(candidate["config_path"]),
        )
    return references


def parse_candidate_id(candidate_id: str) -> RelativeCycleParameters:
    match = _CANDIDATE_ID_RE.fullmatch(candidate_id)
    if match is None:
        raise ValueError(f"unrecognized candidate id {candidate_id!r}")
    return normalize_relative_cycle_parameters(
        carrier_size=int(match.group("carrier")),
        route_shift_delta=int(match.group("delta")),
        weight_left=Fraction(
            int(match.group("left_num")),
            int(match.group("left_den")),
        ),
        weight_right=Fraction(
            int(match.group("right_num")),
            int(match.group("right_den")),
        ),
    )


def threshold_profiles_from_config(
    threshold_profiles: Mapping[str, Mapping[str, str]] | None,
) -> tuple[ThresholdProfile, ...]:
    payload = threshold_profiles or {
        "lenient": {
            "min_recombination_gap": "1/6",
            "min_visibility_recovery_gap": "1/6",
            "max_route_readability": "1/6",
        },
        "default": {
            "min_recombination_gap": "1/3",
            "min_visibility_recovery_gap": "1/3",
            "max_route_readability": "0",
        },
        "strict": {
            "min_recombination_gap": "1/2",
            "min_visibility_recovery_gap": "1/2",
            "max_route_readability": "0",
        },
    }
    ordered_names = [
        name for name in ("lenient", "default", "strict") if name in payload
    ] + sorted(name for name in payload if name not in {"lenient", "default", "strict"})
    return tuple(
        ThresholdProfile(
            name=name,
            min_recombination_gap=Fraction(payload[name]["min_recombination_gap"]),
            min_visibility_recovery_gap=Fraction(
                payload[name]["min_visibility_recovery_gap"]
            ),
            max_route_readability=Fraction(payload[name]["max_route_readability"]),
        )
        for name in ordered_names
    )


def enumerate_candidate_neighborhood(
    candidate: CandidateReference,
    *,
    carrier_sizes: Sequence[int],
    route_shift_deltas: Sequence[int],
    weight_lefts: Sequence[str],
) -> tuple[RelativeCycleParameters, ...]:
    cases: list[RelativeCycleParameters] = []
    for carrier_size in carrier_sizes:
        for delta in route_shift_deltas:
            if delta <= 0 or delta >= carrier_size:
                continue
            for weight_left in weight_lefts:
                left = Fraction(weight_left)
                right = Fraction(1, 1) - left
                cases.append(
                    normalize_relative_cycle_parameters(
                        carrier_size=carrier_size,
                        route_shift_delta=delta,
                        weight_left=left,
                        weight_right=right,
                    )
                )
    return tuple(cases)


def default_candidate_carrier_sizes(candidate: CandidateReference) -> tuple[int, ...]:
    carrier_size = candidate.parameters.carrier_size
    if carrier_size == 5:
        return (4, 5)
    if carrier_size == 4:
        return (3, 4, 5)
    lower = max(2, carrier_size - 1)
    return tuple(sorted({lower, carrier_size, carrier_size + 1}))


def evaluate_threshold_profiles(
    case_rows: Sequence[Mapping[str, Any]],
    profiles: Sequence[ThresholdProfile],
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        survival_case_ids = [
            str(row["case_id"])
            for row in case_rows
            if _survives_profile(row, profile)
        ]
        brittle_case_ids = [
            str(row["case_id"])
            for row in case_rows
            if str(row["case_id"]) not in survival_case_ids
        ]
        survival_fraction = Fraction(len(survival_case_ids), len(case_rows))
        results[profile.name] = {
            "survival_fraction": str(survival_fraction),
            "survival_case_ids": survival_case_ids,
            "brittle_case_ids": brittle_case_ids,
            "verdict": recommended_status_from_fraction(survival_fraction),
        }
    return results


def recommended_status_from_fraction(survival_fraction: Fraction) -> str:
    if survival_fraction >= Fraction(2, 3):
        return "stable"
    if survival_fraction >= Fraction(1, 3):
        return "borderline"
    return "demote"


def build_candidate_robustness_record(
    *,
    candidate: CandidateReference,
    case_rows: Sequence[Mapping[str, Any]],
    profile_results: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    class_label_counts: dict[str, int] = {}
    for row in case_rows:
        label = str(row["class_label"])
        class_label_counts[label] = class_label_counts.get(label, 0) + 1
    default_fraction = Fraction(profile_results["default"]["survival_fraction"])
    return {
        "candidate_id": candidate.candidate_id,
        "reference_run_id": candidate.reference_run_id,
        "physical_case_count": len(case_rows),
        "class_label_counts": class_label_counts,
        "min_recombination_gap_value": str(
            min(Fraction(str(row["recombination_gap_value"])) for row in case_rows)
        ),
        "max_recombination_gap_value": str(
            max(Fraction(str(row["recombination_gap_value"])) for row in case_rows)
        ),
        "min_visibility_recovery_gap": str(
            min(Fraction(str(row["visibility_recovery_gap"])) for row in case_rows)
        ),
        "max_visibility_recovery_gap": str(
            max(Fraction(str(row["visibility_recovery_gap"])) for row in case_rows)
        ),
        "max_route_readability_score": str(
            max(Fraction(str(row["route_readability_score"])) for row in case_rows)
        ),
        "min_eta_max_fiber_size": min(int(row["eta_max_fiber_size"]) for row in case_rows),
        "max_eta_max_fiber_size": max(int(row["eta_max_fiber_size"]) for row in case_rows),
        "profile_results": profile_results,
        "recommended_status": recommended_status_from_fraction(default_fraction),
    }


def build_robustness_summary_rows(
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": record["candidate_id"],
            "reference_run_id": record["reference_run_id"],
            "physical_case_count": record["physical_case_count"],
            "lenient_survival_fraction": record["profile_results"]["lenient"]["survival_fraction"],
            "default_survival_fraction": record["profile_results"]["default"]["survival_fraction"],
            "strict_survival_fraction": record["profile_results"]["strict"]["survival_fraction"],
            "min_recombination_gap_value": record["min_recombination_gap_value"],
            "min_visibility_recovery_gap": record["min_visibility_recovery_gap"],
            "max_route_readability_score": record["max_route_readability_score"],
            "min_eta_max_fiber_size": record["min_eta_max_fiber_size"],
            "recommended_status": record["recommended_status"],
        }
        for record in records
    ]


def build_top_stable_cases_payload(
    *,
    robustness_id: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    ranked = sorted(records, key=_candidate_stability_key)
    top_candidates = [
        {
            "candidate_id": record["candidate_id"],
            "reference_run_id": record["reference_run_id"],
            "default_survival_fraction": record["profile_results"]["default"]["survival_fraction"],
            "strict_survival_fraction": record["profile_results"]["strict"]["survival_fraction"],
            "min_recombination_gap_value": record["min_recombination_gap_value"],
            "min_visibility_recovery_gap": record["min_visibility_recovery_gap"],
            "max_route_readability_score": record["max_route_readability_score"],
            "min_eta_max_fiber_size": record["min_eta_max_fiber_size"],
            "recommended_status": record["recommended_status"],
        }
        for record in ranked
    ]
    return {
        "robustness_id": robustness_id,
        "robustness_rule_version": ROBUSTNESS_RULE_VERSION,
        "ranking_order": [record["candidate_id"] for record in ranked],
        "top_stable_cases": top_candidates,
        "verdict": "stable_candidates_ranked",
    }


def build_cases_to_demote_payload(
    *,
    robustness_id: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    cases_to_demote = [
        {
            "candidate_id": record["candidate_id"],
            "reference_run_id": record["reference_run_id"],
            "default_survival_fraction": record["profile_results"]["default"]["survival_fraction"],
            "recommended_status": record["recommended_status"],
        }
        for record in records
        if record["recommended_status"] == "demote"
    ]
    verdict = (
        "demotions_identified" if cases_to_demote else "no_candidates_to_demote"
    )
    return {
        "robustness_id": robustness_id,
        "robustness_rule_version": ROBUSTNESS_RULE_VERSION,
        "cases_to_demote": cases_to_demote,
        "verdict": verdict,
    }


def _survives_profile(
    row: Mapping[str, Any],
    profile: ThresholdProfile,
) -> bool:
    return (
        str(row["class_label"]) in POSITIVE_LABELS
        and Fraction(str(row["recombination_gap_value"])) >= profile.min_recombination_gap
        and Fraction(str(row["visibility_recovery_gap"]))
        >= profile.min_visibility_recovery_gap
        and Fraction(str(row["route_readability_score"])) <= profile.max_route_readability
    )


def _candidate_stability_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
    status_order = {"stable": 0, "borderline": 1, "demote": 2}
    return (
        status_order[str(record["recommended_status"])],
        -Fraction(record["profile_results"]["default"]["survival_fraction"]),
        -Fraction(record["profile_results"]["strict"]["survival_fraction"]),
        -Fraction(str(record["min_recombination_gap_value"])),
        str(record["candidate_id"]),
    )


__all__ = [
    "CandidateReference",
    "PROMOTED_CANDIDATES_PATH",
    "ROBUSTNESS_RULE_VERSION",
    "ThresholdProfile",
    "build_candidate_robustness_record",
    "build_cases_to_demote_payload",
    "build_robustness_summary_rows",
    "build_top_stable_cases_payload",
    "default_candidate_carrier_sizes",
    "enumerate_candidate_neighborhood",
    "evaluate_threshold_profiles",
    "load_promoted_candidate_references",
    "parse_candidate_id",
    "recommended_status_from_fraction",
    "threshold_profiles_from_config",
]
