from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._recombination_support.benchmarks.loader import load_benchmark
from sixbirds_foundations_v._recombination_support.completion.framework import (
    CompletionFamilyId,
    CompletionInputKind,
    CompletionRequest,
    CompletionSourceKind,
    FlatteningControlMode,
    apply_completion_request,
    build_completion_family_benchmark_view,
    build_completion_source_surface,
)
from sixbirds_foundations_v._recombination_support.completion.ticket27_lift import (
    CANONICAL_GATE_ARTIFACT_PATH,
    CONTROL_SMOKE_CONFIG_PATH,
    FLAGSHIP_SMOKE_CONFIG_PATH,
    REQUIRED_STRATEGY_IDS,
)
from sixbirds_foundations_v._recombination_support.completion.ticket27_support import (
    strip_completion_sensitive_signature,
)
from sixbirds_foundations_v._recombination_support.promotion_r1.runtime_surface import (
    load_review_benchmark,
    load_review_benchmark_from_config,
)
from sixbirds_foundations_v._recombination_support.schemas import BenchmarkRunConfig


REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_CORPUS_ARTIFACT = "results/derived/ticket27_seed_corpus.json"
R1_INTRINSIC_REGISTRY_ARTIFACT = "results/derived/ticket27r1_intrinsic_candidate_registry.json"
R2_SECOND_STAGE_REGISTRY_ARTIFACT = "results/derived/ticket27r2_second_stage_registry.json"
R2_SECOND_STAGE_SUMMARY_ARTIFACT = "results/derived/ticket27r2_second_stage_stability_summary.json"
R2_GATE_DECISION_ARTIFACT = CANONICAL_GATE_ARTIFACT_PATH
LIFT_SMOKE_ARTIFACT = "results/derived/ticket27_lift_smoke.json"
LIFT_INTRINSIC_BASELINE_ARTIFACT = "results/derived/ticket27_lift_intrinsic_baseline.json"
LIFT_SELECTION_REGISTRY_ARTIFACT = "results/derived/ticket27_lift_selection_registry.json"
LIFT_SELECTION_SUMMARY_ARTIFACT = "results/derived/ticket27_lift_selection_summary.json"
REPRESENTATIVE_FRONTIER_ARTIFACT = "results/derived/ticket27_representative_frontier.json"
LIFT_NOTE_ARTIFACT = "results/notes/ticket27_lift_note.md"

FLAGSHIP_IDS = (
    "t27.flagship.reference_positive",
    "t27.flagship.completion_partner",
)
REQUIRED_CONTROL_IDS = (
    "t27.control.null_baseline",
    "t27.control.memory_only",
    "t27.control.artifact",
    "t27.control.boundary_collapse",
)
NEARBY_POSITIVE_IDS = (
    "t27.nearby.n3_d1_w1of3_2of3",
    "t27.nearby.n4_d1_w1of3_2of3",
    "t27.nearby.n5_d1_w1of2_1of2",
    "t27.nearby.n5_d2_w1of3_2of3",
)
CASE_ID_PATTERN = re.compile(
    r"^n(?P<carrier_size>\d+)_d(?P<route_shift_delta>\d+)_"
    r"w(?P<left_num>\d+)of(?P<left_den>\d+)_(?P<right_num>\d+)of(?P<right_den>\d+)$"
)
PROPOSAL_BURDEN = {
    "identity_surface": 0,
    "screen_label_anonymized": 1,
    "screen_history_removed": 1,
    "completion_removed": 1,
    "screen_anonymized_plus_history_removed": 2,
    "screen_label_anonymized_completion_removed": 2,
}
PROPOSAL_ORDER = tuple(PROPOSAL_BURDEN)


def build_ticket27_lift_artifacts(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    intrinsic_baseline = build_intrinsic_baseline_artifact(repo_root=resolved_repo_root)
    registry = build_lift_selection_registry(repo_root=resolved_repo_root)
    summary = build_lift_selection_summary(registry, intrinsic_baseline=intrinsic_baseline)
    frontier = build_representative_frontier(
        summary=summary,
        intrinsic_baseline=intrinsic_baseline,
    )
    note = build_lift_note(summary, intrinsic_baseline=intrinsic_baseline)

    baseline_path = _write_json_artifact(
        resolved_repo_root / LIFT_INTRINSIC_BASELINE_ARTIFACT,
        intrinsic_baseline,
    )
    registry_path = _write_json_artifact(
        resolved_repo_root / LIFT_SELECTION_REGISTRY_ARTIFACT,
        registry,
    )
    summary_path = _write_json_artifact(
        resolved_repo_root / LIFT_SELECTION_SUMMARY_ARTIFACT,
        summary,
    )
    frontier_path = _write_json_artifact(
        resolved_repo_root / REPRESENTATIVE_FRONTIER_ARTIFACT,
        frontier,
    )
    note_path = resolved_repo_root / LIFT_NOTE_ARTIFACT
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")
    return {
        "baseline_path": baseline_path,
        "registry_path": registry_path,
        "summary_path": summary_path,
        "frontier_path": frontier_path,
        "note_path": note_path,
        "branch_decision": summary["branch_decision"],
    }


def build_intrinsic_baseline_artifact(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    registry = json.loads(
        (resolved_repo_root / R2_SECOND_STAGE_REGISTRY_ARTIFACT).read_text(encoding="utf-8")
    )
    by_id = {case["stable_id"]: case for case in registry["cases"]}
    qualifying_proposals = []
    for proposal_id in registry["proposal_ids"]:
        flagship_candidates = {
            stable_id: _proposal_payload(by_id[stable_id], proposal_id) for stable_id in FLAGSHIP_IDS
        }
        if any(candidate is None for candidate in flagship_candidates.values()):
            continue
        if not all(candidate["proposal"]["non_identity"] for candidate in flagship_candidates.values()):
            continue
        if not all(candidate["reduction_amount"] > 0 for candidate in flagship_candidates.values()):
            continue
        if not all(
            candidate["closure_status"] == "preserved_on_coarsened_surface"
            for candidate in flagship_candidates.values()
        ):
            continue
        if not _flagship_candidates_structurally_match(
            flagship_candidates[FLAGSHIP_IDS[0]],
            flagship_candidates[FLAGSHIP_IDS[1]],
        ):
            continue
        preserved_controls = _preserved_controls_for_intrinsic_proposal(
            by_id=by_id,
            proposal_id=proposal_id,
        )
        if len(preserved_controls) < 2 or not any(
            control_id in preserved_controls
            for control_id in ("t27.control.null_baseline", "t27.control.artifact")
        ):
            continue
        nearby_supported = _nearby_positive_supported_count_for_intrinsic_proposal(
            by_id=by_id,
            proposal_id=proposal_id,
        )
        if _proposal_shared_by_every_real_case(by_id=by_id, proposal_id=proposal_id):
            continue
        qualifying_proposals.append(
            {
                "proposal_id": proposal_id,
                "coarsening_burden": PROPOSAL_BURDEN[proposal_id],
                "flagship_target_package_size": flagship_candidates[
                    "t27.flagship.reference_positive"
                ]["target_package_size"],
                "preserved_required_control_contrast_count": len(preserved_controls),
                "preserved_required_control_contrasts": preserved_controls,
                "nearby_positive_supported_count": nearby_supported,
                "flagship_candidate_fingerprint": flagship_candidates[
                    "t27.flagship.reference_positive"
                ]["candidate_fingerprint"],
            }
        )
    qualifying_proposals.sort(
        key=lambda item: (
            item["coarsening_burden"],
            -item["preserved_required_control_contrast_count"],
            -item["nearby_positive_supported_count"],
            item["flagship_target_package_size"],
            item["proposal_id"],
        )
    )
    best_envelope = qualifying_proposals[0] if qualifying_proposals else None
    gate_payload = json.loads(
        (resolved_repo_root / R2_GATE_DECISION_ARTIFACT).read_text(encoding="utf-8")
    )
    return {
        "ticket": "T27-10",
        "schema_version": "ticket27-lift-intrinsic-baseline.v1",
        "generated_from": [
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_SUMMARY_ARTIFACT,
            R2_GATE_DECISION_ARTIFACT,
        ],
        "canonical_gate_artifact": R2_GATE_DECISION_ARTIFACT,
        "canonical_gate_decision": gate_payload["gate_decision"],
        "qualifying_proposals": qualifying_proposals,
        "qualifying_proposal_ids": [item["proposal_id"] for item in qualifying_proposals],
        "best_intrinsic_envelope": best_envelope,
        "intrinsic_baseline_ranking_rule": [
            "lower coarsening_burden",
            "higher preserved_required_control_contrast_count",
            "higher nearby_positive_supported_count",
            "lower flagship_target_package_size",
            "lexical proposal_id",
        ],
    }


def build_lift_selection_registry(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    seed_corpus = json.loads((resolved_repo_root / SEED_CORPUS_ARTIFACT).read_text(encoding="utf-8"))
    entries = {
        entry["stable_id"]: entry
        for entry in seed_corpus["entries"]
        if entry["stable_id"] in FLAGSHIP_IDS + REQUIRED_CONTROL_IDS + NEARBY_POSITIVE_IDS
    }
    smoke_payload = json.loads((resolved_repo_root / LIFT_SMOKE_ARTIFACT).read_text(encoding="utf-8"))
    identity_rows = {
        (row["case_id"], row["family_id"]): row["representative_mapping"]
        for row in smoke_payload["rows"]
        if row["strategy_id"] == "identity_reference"
    }

    reference_payloads = _build_reference_payloads(resolved_repo_root)
    rows = []
    for stable_id, entry in entries.items():
        benchmark, config_path_for_request = _load_ticket27_benchmark(
            entry,
            repo_root=resolved_repo_root,
        )
        variants = _strategy_variants_for_case(
            stable_id=stable_id,
            entry=entry,
            reference_payloads=reference_payloads,
        )
        for strategy_id in REQUIRED_STRATEGY_IDS:
            for variant in variants:
                row = _evaluate_lift_row(
                    stable_id=stable_id,
                    entry=entry,
                    benchmark=benchmark,
                    config_path_for_request=config_path_for_request,
                    strategy_id=strategy_id,
                    family_id=variant["family_id"],
                    flattening_mode=variant["flattening_mode"],
                    strategy_parameters=variant["strategy_parameters_by_strategy"].get(
                        strategy_id,
                        {},
                    ),
                    identity_mapping_by_case_and_family=identity_rows,
                )
                rows.append(row)

    rows = _annotate_lift_rows_with_best_proposals(rows)
    return {
        "ticket": "T27-10",
        "schema_version": "ticket27-lift-selection-registry.v1",
        "generated_from": [
            SEED_CORPUS_ARTIFACT,
            R1_INTRINSIC_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_SUMMARY_ARTIFACT,
            R2_GATE_DECISION_ARTIFACT,
            LIFT_SMOKE_ARTIFACT,
        ],
        "source_kind": CompletionSourceKind.RECOMBINATION_QUOTIENT.value,
        "rows": rows,
    }


def build_lift_selection_summary(
    registry: dict[str, Any],
    *,
    intrinsic_baseline: dict[str, Any],
) -> dict[str, Any]:
    rows = registry["rows"]
    baseline = intrinsic_baseline["best_intrinsic_envelope"]
    strategy_summaries = []
    for strategy_id in REQUIRED_STRATEGY_IDS:
        strategy_rows = [row for row in rows if row["strategy_id"] == strategy_id]
        flagship_rows = [row for row in strategy_rows if row["stable_id"] in FLAGSHIP_IDS]
        nearby_rows = [row for row in strategy_rows if row["stable_id"] in NEARBY_POSITIVE_IDS]

        best_core = _best_common_flagship_outcome(strategy_rows)
        if best_core is None:
            materially_improves = False
            reason = "fallback_only_on_core" if any(
                row["stable_id"] in FLAGSHIP_IDS and row["skip_reason"] is None and row["fallback_used"]
                for row in strategy_rows
            ) else "not_evaluable_on_core"
            summary_row = {
                "strategy_id": strategy_id,
                "flagship_core_evaluable_row_count": sum(
                    1 for row in flagship_rows if row["skip_reason"] is None
                ),
                "flagship_core_non_fallback_row_count": sum(
                    1
                    for row in flagship_rows
                    if row["skip_reason"] is None and not row["fallback_used"]
                ),
                "both_flagships_gate_supported": False,
                "best_common_flagship_proposal_id": None,
                "best_common_flagship_burden": None,
                "preserved_required_control_contrast_count": 0,
                "nearby_positive_supported_count": 0,
                "materially_improves_over_intrinsic": materially_improves,
                "comparison_reason": reason,
                "best_common_family_id": None,
                "best_common_flattening_mode": None,
            }
        else:
            nearby_count = _nearby_positive_supported_count_for_strategy(
                nearby_rows=nearby_rows,
                proposal_id=best_core["proposal_id"],
            )
            materially_improves, reason = _compare_lift_outcome_to_intrinsic(
                burden=best_core["coarsening_burden"],
                control_count=best_core["preserved_required_control_contrast_count"],
                nearby_count=nearby_count,
                intrinsic_baseline=baseline,
            )
            summary_row = {
                "strategy_id": strategy_id,
                "flagship_core_evaluable_row_count": sum(
                    1 for row in flagship_rows if row["skip_reason"] is None
                ),
                "flagship_core_non_fallback_row_count": sum(
                    1
                    for row in flagship_rows
                    if row["skip_reason"] is None and not row["fallback_used"]
                ),
                "both_flagships_gate_supported": True,
                "best_common_flagship_proposal_id": best_core["proposal_id"],
                "best_common_flagship_burden": best_core["coarsening_burden"],
                "preserved_required_control_contrast_count": best_core[
                    "preserved_required_control_contrast_count"
                ],
                "nearby_positive_supported_count": nearby_count,
                "materially_improves_over_intrinsic": materially_improves,
                "comparison_reason": reason,
                "best_common_family_id": best_core["family_id"],
                "best_common_flattening_mode": best_core["flattening_mode"],
            }
        strategy_summaries.append(summary_row)

    improving_strategies = [
        row for row in strategy_summaries if row["materially_improves_over_intrinsic"]
    ]
    if improving_strategies:
        branch_decision = "LIFT_ADDS_VALUE"
        winning_strategy = sorted(
            improving_strategies,
            key=lambda row: (
                row["best_common_flagship_burden"],
                -row["preserved_required_control_contrast_count"],
                -row["nearby_positive_supported_count"],
                row["strategy_id"],
            ),
        )[0]["strategy_id"]
    else:
        branch_decision = "LIFT_NO_ADDED_VALUE"
        winning_strategy = None

    return {
        "ticket": "T27-10",
        "schema_version": "ticket27-lift-selection-summary.v1",
        "registry_artifact": LIFT_SELECTION_REGISTRY_ARTIFACT,
        "intrinsic_baseline_artifact": LIFT_INTRINSIC_BASELINE_ARTIFACT,
        "strategies": strategy_summaries,
        "branch_decision": branch_decision,
        "winning_strategy": winning_strategy,
    }


def build_representative_frontier(
    *,
    summary: dict[str, Any],
    intrinsic_baseline: dict[str, Any],
) -> dict[str, Any]:
    baseline = intrinsic_baseline["best_intrinsic_envelope"]
    entries = [
        {
            "entry_id": "intrinsic_baseline",
            "entry_type": "intrinsic_baseline",
            "strategy_id": None,
            "flagship_gate_supported_count": 2 if baseline is not None else 0,
            "flagship_non_fallback_supported_count": 2 if baseline is not None else 0,
            "best_common_flagship_burden": (
                baseline["coarsening_burden"] if baseline is not None else None
            ),
            "preserved_required_control_contrast_count": (
                baseline["preserved_required_control_contrast_count"]
                if baseline is not None
                else 0
            ),
            "nearby_positive_supported_count": (
                baseline["nearby_positive_supported_count"] if baseline is not None else 0
            ),
            "beats_intrinsic_baseline": False,
        }
    ]
    for strategy in summary["strategies"]:
        entries.append(
            {
                "entry_id": strategy["strategy_id"],
                "entry_type": "lift_strategy",
                "strategy_id": strategy["strategy_id"],
                "flagship_gate_supported_count": 2 if strategy["both_flagships_gate_supported"] else 0,
                "flagship_non_fallback_supported_count": (
                    2
                    if strategy["both_flagships_gate_supported"]
                    and strategy["flagship_core_non_fallback_row_count"] >= 2
                    else 0
                ),
                "best_common_flagship_burden": strategy["best_common_flagship_burden"],
                "preserved_required_control_contrast_count": strategy[
                    "preserved_required_control_contrast_count"
                ],
                "nearby_positive_supported_count": strategy["nearby_positive_supported_count"],
                "beats_intrinsic_baseline": strategy["materially_improves_over_intrinsic"],
            }
        )
    non_dominated = [
        entry["entry_id"]
        for entry in entries
        if not any(_dominates(other, entry) for other in entries if other["entry_id"] != entry["entry_id"])
    ]
    return {
        "ticket": "T27-10",
        "schema_version": "ticket27-representative-frontier.v1",
        "intrinsic_baseline_artifact": LIFT_INTRINSIC_BASELINE_ARTIFACT,
        "lift_selection_summary_artifact": LIFT_SELECTION_SUMMARY_ARTIFACT,
        "entries": entries,
        "non_dominated_entry_ids": non_dominated,
        "any_lift_strategy_beats_intrinsic_baseline": any(
            entry["entry_type"] == "lift_strategy" and entry["beats_intrinsic_baseline"]
            for entry in entries
        ),
    }


def build_lift_note(
    summary: dict[str, Any],
    *,
    intrinsic_baseline: dict[str, Any],
) -> str:
    baseline = intrinsic_baseline["best_intrinsic_envelope"]
    lines = [
        "# Ticket27 Lift Note",
        "",
        (
            "- Best intrinsic envelope: "
            f"`{baseline['proposal_id'] if baseline is not None else 'none'}`."
        ),
        f"- Branch decision: `{summary['branch_decision']}`.",
        "",
        "## Strategy Outcomes",
    ]
    for strategy in summary["strategies"]:
        lines.append(
            f"- `{strategy['strategy_id']}`: proposal `{strategy['best_common_flagship_proposal_id']}`, burden `{strategy['best_common_flagship_burden']}`, controls `{strategy['preserved_required_control_contrast_count']}`, nearby `{strategy['nearby_positive_supported_count']}`, reason `{strategy['comparison_reason']}`."
        )
    lines.append("")
    return "\n".join(lines)


def _evaluate_lift_row(
    *,
    stable_id: str,
    entry: dict[str, Any],
    benchmark: Any,
    config_path_for_request: str,
    strategy_id: str,
    family_id: CompletionFamilyId,
    flattening_mode: FlatteningControlMode,
    strategy_parameters: dict[str, Any],
    identity_mapping_by_case_and_family: dict[tuple[str, str], dict[str, str]],
) -> dict[str, Any]:
    request = CompletionRequest(
        input_kind=CompletionInputKind.BENCHMARK_REQUEST,
        source_kind=CompletionSourceKind.RECOMBINATION_QUOTIENT,
        strategy_id=strategy_id,
        family_id=family_id,
        config_path=config_path_for_request,
        strategy_parameters=strategy_parameters,
        flattening_mode=flattening_mode,
    )
    result = apply_completion_request(request, benchmark=benchmark)
    if result.status.value != "ok":
        return {
            "stable_id": stable_id,
            "category": entry["category"],
            "config_path": config_path_for_request,
            "source_kind": CompletionSourceKind.RECOMBINATION_QUOTIENT.value,
            "family_id": family_id.value,
            "flattening_mode": flattening_mode.value,
            "strategy_id": strategy_id,
            "fallback_used": False,
            "fallback_reason": None,
            "reference_config_path": None,
            "reference_config_id": None,
            "representative_mapping": {},
            "selected_class_summaries": {},
            "mapping_differs_from_identity_reference": False,
            "proposal_summaries": [],
            "best_second_stage_proposal_id": None,
            "best_second_stage_target_package_size": None,
            "best_second_stage_coarsening_burden": None,
            "closure_status": None,
            "preserved_required_control_contrasts": [],
            "flagship_core_gate_satisfied": False,
            "skip_reason": result.warnings[-1] if result.warnings else result.status.value,
        }

    family_view = build_completion_family_benchmark_view(benchmark, family_id)
    surface_benchmark = family_view.benchmark or benchmark
    source_surface = build_completion_source_surface(
        surface_benchmark,
        CompletionSourceKind.RECOMBINATION_QUOTIENT,
    )
    source_classes = {completion_class.class_id: completion_class for completion_class in source_surface.classes}
    selected_class_summaries = {}
    for class_id, candidate_id in result.representative_mapping.items():
        completion_class = source_classes[class_id]
        candidate = next(
            candidate for candidate in completion_class.candidates if candidate.candidate_id == candidate_id
        )
        selected_class_summaries[class_id] = {
            "selected_candidate_id": candidate.candidate_id,
            "candidate_signature": candidate.candidate_signature,
            "predictive_signature_key": candidate.predictive_signature_key,
            "branch_member_count": candidate.branch_member_count,
            "max_member_weight": candidate.max_member_weight,
            "score_summary": next(
                selection.score_summary
                for selection in result.class_selections
                if selection.class_id == class_id
            ),
        }
    proposal_summaries = [
        _evaluate_lifted_surface_proposal(
            selected_class_summaries=selected_class_summaries,
            proposal_id=proposal_id,
        )
        for proposal_id in PROPOSAL_ORDER
    ]
    strategy_parameter_payload = strategy_parameters.get(strategy_id, {})
    case_key = (
        _strategy_case_id_for_identity_lookup(stable_id),
        family_id.value,
    )
    identity_mapping = identity_mapping_by_case_and_family.get(case_key, {})
    return {
        "stable_id": stable_id,
        "category": entry["category"],
        "config_path": config_path_for_request,
        "source_kind": CompletionSourceKind.RECOMBINATION_QUOTIENT.value,
        "family_id": family_id.value,
        "flattening_mode": flattening_mode.value,
        "strategy_id": strategy_id,
        "fallback_used": result.provenance.fallback_used is not None,
        "fallback_reason": result.provenance.fallback_used,
        "reference_config_path": strategy_parameter_payload.get("reference_config_path"),
        "reference_config_id": strategy_parameter_payload.get("reference_config_id"),
        "representative_mapping": result.representative_mapping,
        "selected_class_summaries": selected_class_summaries,
        "score_basis": {
            selection.class_id: selection.score_summary for selection in result.class_selections
        },
        "mapping_differs_from_identity_reference": result.representative_mapping != identity_mapping,
        "proposal_summaries": proposal_summaries,
        "best_second_stage_proposal_id": None,
        "best_second_stage_target_package_size": None,
        "best_second_stage_coarsening_burden": None,
        "closure_status": None,
        "preserved_required_control_contrasts": [],
        "flagship_core_gate_satisfied": False,
        "skip_reason": None,
    }


def _annotate_lift_rows_with_best_proposals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (row["stable_id"], row["strategy_id"], row["family_id"], row["flattening_mode"]): row
        for row in rows
    }
    for row in rows:
        if row["skip_reason"] is not None:
            continue
        best = min(
            row["proposal_summaries"],
            key=lambda payload: (
                payload["coarsening_burden"],
                payload["target_package_size"],
                payload["proposal_id"],
            ),
        )
        preserved_controls = _preserved_controls_for_lift_row(
            row=row,
            best_proposal_id=best["proposal_id"],
            by_key=by_key,
        )
        row["best_second_stage_proposal_id"] = best["proposal_id"]
        row["best_second_stage_target_package_size"] = best["target_package_size"]
        row["best_second_stage_coarsening_burden"] = best["coarsening_burden"]
        row["closure_status"] = best["closure_status"]
        row["preserved_required_control_contrasts"] = preserved_controls
    qualifying_pairs = _qualifying_flagship_pairs(rows)
    qualifying_keys = {
        tuple(pair["left_row_key"])
        for pair in qualifying_pairs
    } | {
        tuple(pair["right_row_key"])
        for pair in qualifying_pairs
    }
    for row in rows:
        row["flagship_core_gate_satisfied"] = (
            (row["stable_id"], row["strategy_id"], row["family_id"], row["flattening_mode"])
            in qualifying_keys
        )
    return rows


def _evaluate_lifted_surface_proposal(
    *,
    selected_class_summaries: dict[str, dict[str, Any]],
    proposal_id: str,
) -> dict[str, Any]:
    coarsened_signatures = {
        class_id: _coarsen_completion_signature(
            payload["candidate_signature"],
            proposal_id=proposal_id,
        )
        for class_id, payload in selected_class_summaries.items()
    }
    grouped: dict[Any, dict[str, Any]] = {}
    for class_id, signature in coarsened_signatures.items():
        key = _canonical_key(signature)
        if key not in grouped:
            grouped[key] = {
                "members": [],
                "signature": signature,
            }
        grouped[key]["members"].append(class_id)
    grouped_items = sorted(
        grouped.items(),
        key=lambda item: (len(item[1]["members"]), item[1]["members"]),
    )
    target_size = len(grouped_items)
    target_observable_signature = {
        f"L{index}": _structuralize_completion_signature(grouped_items[index][1]["signature"])
        for index in range(len(grouped_items))
    }
    fingerprint = _fingerprint(target_observable_signature)
    return {
        "proposal_id": proposal_id,
        "coarsening_burden": PROPOSAL_BURDEN[proposal_id],
        "target_package_size": target_size,
        "non_identity": proposal_id != "identity_surface" and target_size < len(selected_class_summaries),
        "closure_status": "preserved_on_selected_quotient_surface",
        "candidate_fingerprint": fingerprint,
        "coarsened_surface_signature": target_observable_signature,
    }


def _best_common_flagship_outcome(strategy_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    qualifying_pairs = _qualifying_flagship_pairs(strategy_rows)
    if not qualifying_pairs:
        return None
    qualifying_pairs.sort(
        key=lambda pair: (
            pair["coarsening_burden"],
            -pair["preserved_required_control_contrast_count"],
            pair["target_package_size"],
            pair["proposal_id"],
            pair["family_id"],
            pair["flattening_mode"],
        )
    )
    return qualifying_pairs[0]


def _qualifying_flagship_pairs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, list[dict[str, Any]]] = {stable_id: [] for stable_id in FLAGSHIP_IDS}
    for row in rows:
        if row["stable_id"] in FLAGSHIP_IDS and row["skip_reason"] is None:
            by_id[row["stable_id"]].append(row)
    qualifying = []
    for left in by_id["t27.flagship.reference_positive"]:
        for right in by_id["t27.flagship.completion_partner"]:
            if left["strategy_id"] != right["strategy_id"]:
                continue
            if left["family_id"] != right["family_id"]:
                continue
            if left["flattening_mode"] != right["flattening_mode"]:
                continue
            if left["fallback_used"] or right["fallback_used"]:
                continue
            for proposal_id in PROPOSAL_ORDER:
                left_payload = _proposal_summary_by_id(left, proposal_id)
                right_payload = _proposal_summary_by_id(right, proposal_id)
                if left_payload is None or right_payload is None:
                    continue
                if not _flagship_candidates_structurally_match(left_payload, right_payload):
                    continue
                preserved_controls = sorted(
                    set(left.get("preserved_required_control_contrasts", []))
                    .intersection(right.get("preserved_required_control_contrasts", []))
                )
                if len(preserved_controls) < 2 or not any(
                    control_id in preserved_controls
                    for control_id in ("t27.control.null_baseline", "t27.control.artifact")
                ):
                    continue
                qualifying.append(
                    {
                        "strategy_id": left["strategy_id"],
                        "family_id": left["family_id"],
                        "flattening_mode": left["flattening_mode"],
                        "proposal_id": proposal_id,
                        "coarsening_burden": left_payload["coarsening_burden"],
                        "target_package_size": left_payload["target_package_size"],
                        "preserved_required_control_contrast_count": len(preserved_controls),
                        "preserved_required_control_contrasts": preserved_controls,
                        "left_row_key": [
                            left["stable_id"],
                            left["strategy_id"],
                            left["family_id"],
                            left["flattening_mode"],
                        ],
                        "right_row_key": [
                            right["stable_id"],
                            right["strategy_id"],
                            right["family_id"],
                            right["flattening_mode"],
                        ],
                    }
                )
    return qualifying


def _preserved_controls_for_intrinsic_proposal(
    *,
    by_id: dict[str, dict[str, Any]],
    proposal_id: str,
) -> list[str]:
    flagship_reference = _proposal_payload(by_id["t27.flagship.reference_positive"], proposal_id)
    if flagship_reference is None:
        return []
    preserved = []
    for control_id in REQUIRED_CONTROL_IDS:
        control_payload = _proposal_payload(by_id[control_id], proposal_id)
        if control_payload is None:
            continue
        if _contrast_preserved(flagship_reference, control_payload):
            preserved.append(control_id)
    return preserved


def _nearby_positive_supported_count_for_intrinsic_proposal(
    *,
    by_id: dict[str, dict[str, Any]],
    proposal_id: str,
) -> int:
    count = 0
    for nearby_id in NEARBY_POSITIVE_IDS:
        payload = _proposal_payload(by_id[nearby_id], proposal_id)
        if payload is None:
            continue
        if payload["proposal"]["non_identity"]:
            count += 1
    return count


def _proposal_shared_by_every_real_case(
    *,
    by_id: dict[str, dict[str, Any]],
    proposal_id: str,
) -> bool:
    available = []
    for stable_id, case in by_id.items():
        payload = _proposal_payload(case, proposal_id)
        if payload is not None:
            available.append(payload)
    if not available:
        return False
    return all(payload["proposal"]["non_identity"] for payload in available)


def _preserved_controls_for_lift_row(
    *,
    row: dict[str, Any],
    best_proposal_id: str,
    by_key: dict[tuple[str, str, str, str], dict[str, Any]],
) -> list[str]:
    best_payload = _proposal_summary_by_id(row, best_proposal_id)
    if best_payload is None:
        return []
    preserved = []
    for control_id in REQUIRED_CONTROL_IDS:
        control_row = by_key.get(
            (
                control_id,
                row["strategy_id"],
                CompletionFamilyId.DECLARED_COMPLETION_FAMILY.value,
                FlatteningControlMode.NONE.value,
            )
        )
        if control_row is None or control_row["skip_reason"] is not None:
            continue
        control_payload = _proposal_summary_by_id(control_row, best_proposal_id)
        if control_payload is None:
            continue
        if _contrast_preserved(best_payload, control_payload):
            preserved.append(control_id)
    return preserved


def _nearby_positive_supported_count_for_strategy(
    *,
    nearby_rows: list[dict[str, Any]],
    proposal_id: str,
) -> int:
    count = 0
    for row in nearby_rows:
        if row["skip_reason"] is not None or row["fallback_used"]:
            continue
        payload = _proposal_summary_by_id(row, proposal_id)
        if payload is None:
            continue
        if payload["target_package_size"] < len(row["selected_class_summaries"]):
            count += 1
    return count


def _compare_lift_outcome_to_intrinsic(
    *,
    burden: int,
    control_count: int,
    nearby_count: int,
    intrinsic_baseline: dict[str, Any] | None,
) -> tuple[bool, str]:
    if intrinsic_baseline is None:
        return False, "not_evaluable_on_core"
    baseline_burden = intrinsic_baseline["coarsening_burden"]
    baseline_controls = intrinsic_baseline["preserved_required_control_contrast_count"]
    baseline_nearby = intrinsic_baseline["nearby_positive_supported_count"]
    if burden < baseline_burden:
        return True, "strictly_lower_burden_than_intrinsic"
    if burden > baseline_burden:
        return False, "worse_than_intrinsic"
    if control_count > baseline_controls:
        return True, "same_burden_more_controls"
    if control_count < baseline_controls:
        return False, "worse_than_intrinsic"
    if nearby_count > baseline_nearby:
        return True, "same_burden_more_nearby_support"
    if nearby_count < baseline_nearby:
        return False, "worse_than_intrinsic"
    return False, "ties_intrinsic"


def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_burden = left["best_common_flagship_burden"]
    right_burden = right["best_common_flagship_burden"]
    if left_burden is None:
        return False
    if right_burden is None:
        return left["flagship_gate_supported_count"] >= right["flagship_gate_supported_count"]
    left_metrics = (
        left["flagship_gate_supported_count"],
        left["flagship_non_fallback_supported_count"],
        -left_burden,
        left["preserved_required_control_contrast_count"],
        left["nearby_positive_supported_count"],
    )
    right_metrics = (
        right["flagship_gate_supported_count"],
        right["flagship_non_fallback_supported_count"],
        -right_burden,
        right["preserved_required_control_contrast_count"],
        right["nearby_positive_supported_count"],
    )
    return left_metrics >= right_metrics and left_metrics != right_metrics


def _load_ticket27_benchmark(
    entry: dict[str, Any],
    *,
    repo_root: Path,
) -> tuple[Any, str]:
    config_path = _select_benchmark_config_path(entry)
    if entry["category"] == "nearby_positive" and config_path.startswith("configs/recombination/search/"):
        synthetic_config = _build_relative_cycle_case_config(entry["source_case_id"])
        return (
            load_review_benchmark_from_config(synthetic_config, config_path=config_path),
            config_path,
        )
    return load_review_benchmark(repo_root / config_path), config_path


def _strategy_variants_for_case(
    *,
    stable_id: str,
    entry: dict[str, Any],
    reference_payloads: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    variants = [
        {
            "family_id": CompletionFamilyId.DECLARED_COMPLETION_FAMILY,
            "flattening_mode": FlatteningControlMode.NONE,
            "strategy_parameters_by_strategy": _strategy_parameters_for_case(
                stable_id=stable_id,
                entry=entry,
                reference_payloads=reference_payloads,
                paired=False,
            ),
        }
    ]
    if stable_id in FLAGSHIP_IDS:
        variants.append(
            {
                "family_id": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
                "flattening_mode": FlatteningControlMode.PAIRED_FLATTENING_CONTROL,
                "strategy_parameters_by_strategy": _strategy_parameters_for_case(
                    stable_id=stable_id,
                    entry=entry,
                    reference_payloads=reference_payloads,
                    paired=True,
                ),
            }
        )
    return variants


def _strategy_parameters_for_case(
    *,
    stable_id: str,
    entry: dict[str, Any],
    reference_payloads: dict[str, dict[str, Any]],
    paired: bool,
) -> dict[str, dict[str, Any]]:
    del entry
    parameters = {strategy_id: {} for strategy_id in REQUIRED_STRATEGY_IDS}

    if stable_id in FLAGSHIP_IDS:
        partner_key = (
            "t27.flagship.completion_partner"
            if stable_id == "t27.flagship.reference_positive"
            else "t27.flagship.reference_positive"
        )
        parameters["completion_preserving"] = {
            "completion_preserving": {
                "reference_config_path": reference_payloads[partner_key]["config_path"],
                "reference_config_id": reference_payloads[partner_key]["config_id"],
                "per_class": reference_payloads[partner_key]["per_class"],
            }
        }
    control_reference_key = (
        "t27.flagship.reference_positive"
        if stable_id == "t27.control.memory_only"
        else "t27.control.memory_only"
    )
    parameters["control_matched"] = {
        "control_matched": {
            "reference_config_path": reference_payloads[control_reference_key]["config_path"],
            "reference_config_id": reference_payloads[control_reference_key]["config_id"],
            "per_class": reference_payloads[control_reference_key]["per_class"],
        }
    }
    if paired:
        return parameters
    return parameters


def _build_reference_payloads(repo_root: Path) -> dict[str, dict[str, Any]]:
    references = {}
    for stable_id, config_path in {
        "t27.flagship.reference_positive": "configs/recombination/benchmarks/interference/flattening_control/reference_positive.json",
        "t27.flagship.completion_partner": FLAGSHIP_SMOKE_CONFIG_PATH,
        "t27.control.memory_only": CONTROL_SMOKE_CONFIG_PATH,
    }.items():
        benchmark = load_review_benchmark(repo_root / config_path)
        references[stable_id] = {
            "config_path": config_path,
            "config_id": benchmark.config_id,
            "per_class": _reference_payload_by_class(benchmark, config_path),
        }
    return references


def _reference_payload_by_class(
    benchmark: Any,
    config_path: str,
) -> dict[str, dict[str, Any]]:
    request = CompletionRequest(
        input_kind=CompletionInputKind.BENCHMARK_REQUEST,
        source_kind=CompletionSourceKind.RECOMBINATION_QUOTIENT,
        strategy_id="identity_reference",
        config_path=config_path,
    )
    result = apply_completion_request(request, benchmark=benchmark)
    source_surface = build_completion_source_surface(
        benchmark,
        CompletionSourceKind.RECOMBINATION_QUOTIENT,
    )
    source_classes = {completion_class.class_id: completion_class for completion_class in source_surface.classes}
    payload = {}
    for selection in result.class_selections:
        completion_class = source_classes[selection.class_id]
        candidate = next(
            candidate
            for candidate in completion_class.candidates
            if candidate.candidate_id == selection.selected_representative_id
        )
        payload[selection.class_id] = {
            "partner_config_path": config_path,
            "partner_config_id": benchmark.config_id,
            "partner_selected_candidate_id": candidate.candidate_id,
            "partner_normalized_signature": strip_completion_sensitive_signature(
                candidate.candidate_signature
            ),
            "matched_control_config_path": config_path,
            "matched_control_config_id": benchmark.config_id,
            "reference_candidate_id": candidate.candidate_id,
            "reference_branch_member_count": candidate.branch_member_count,
            "reference_max_member_weight": candidate.max_member_weight,
        }
    return payload


def _coarsen_completion_signature(signature: Any, *, proposal_id: str) -> Any:
    coarsened = deepcopy(signature)
    if not isinstance(coarsened, dict):
        return coarsened
    if proposal_id in {
        "screen_label_anonymized",
        "screen_anonymized_plus_history_removed",
        "screen_label_anonymized_completion_removed",
    }:
        distributions = []
        for distribution in coarsened.get("distributions", []):
            if not isinstance(distribution, dict):
                distributions.append(distribution)
                continue
            probabilities = distribution.get("probabilities")
            if isinstance(probabilities, dict) and any(
                event_id.startswith("screen_") and value != "0"
                for event_id, value in probabilities.items()
            ):
                distributions.append(
                    {
                        "event_ids": ["screen_any"],
                        "probabilities": {"screen_any": "1"},
                    }
                )
            else:
                distributions.append(distribution)
        coarsened["distributions"] = distributions
    if proposal_id in {
        "screen_history_removed",
        "screen_anonymized_plus_history_removed",
    }:
        coarsened = _remove_observable_id(coarsened, "relative_cycle_screen_history")
    if proposal_id in {
        "completion_removed",
        "screen_label_anonymized_completion_removed",
    }:
        coarsened = _remove_observable_id(coarsened, "relative_cycle_completion_bins")
    return coarsened


def _remove_observable_id(signature: dict[str, Any], observable_id: str) -> dict[str, Any]:
    if "observable_ids" not in signature or "distributions" not in signature:
        return signature
    observable_ids = list(signature.get("observable_ids", []))
    distributions = list(signature.get("distributions", []))
    paired = [
        (obs_id, distribution)
        for obs_id, distribution in zip(observable_ids, distributions, strict=True)
        if obs_id != observable_id
    ]
    signature["observable_ids"] = [obs_id for obs_id, _ in paired]
    signature["distributions"] = [distribution for _, distribution in paired]
    return signature


def _proposal_payload(case: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    for candidate in case.get("candidates", []):
        if candidate["proposal"]["proposal_id"] == proposal_id:
            return candidate
    return None


def _proposal_summary_by_id(row: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    for payload in row.get("proposal_summaries", []):
        if payload["proposal_id"] == proposal_id:
            return payload
    return None


def _flagship_candidates_structurally_match(
    left: dict[str, Any],
    right: dict[str, Any],
) -> bool:
    return (
        left["target_package_size"] == right["target_package_size"]
        and left["candidate_fingerprint"] == right["candidate_fingerprint"]
    )


def _contrast_preserved(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["target_package_size"] != right["target_package_size"]
        or left["candidate_fingerprint"] != right["candidate_fingerprint"]
    )


def _strategy_case_id_for_identity_lookup(stable_id: str) -> str:
    if stable_id == "t27.flagship.completion_partner":
        return "ticket27.flagship.completion_partner"
    if stable_id == "t27.control.memory_only":
        return "ticket27.control.memory_only"
    return stable_id


def _build_relative_cycle_case_config(case_id: str) -> BenchmarkRunConfig:
    match = CASE_ID_PATTERN.match(case_id)
    if match is None:
        raise ValueError(f"unsupported nearby-positive case id {case_id!r}")
    groups = match.groupdict()
    return BenchmarkRunConfig(
        schema_version="recombination-benchmark-run-config.v1",
        config_kind="benchmark-run",
        config_id=f"ticket27.lift.{case_id}",
        benchmark_id="relative_cycle_carrier_base",
        interface_id="mid",
        assemblage_family_id="ticket27_relative_cycle_candidate_family",
        observable_family_id="ticket27_relative_cycle_candidate_observable_family",
        route_readability_scenario_id="relative_cycle_anchor_readability",
        visibility_scenario_id="relative_cycle_anchor_screen_visibility",
        carrier_size=int(groups["carrier_size"]),
        route_shift_delta=int(groups["route_shift_delta"]),
        weight_left=f"{groups['left_num']}/{groups['left_den']}",
        weight_right=f"{groups['right_num']}/{groups['right_den']}",
        seed=0,
        run_id=f"run_ticket27_lift_{case_id}",
        generate_plot_artifacts=False,
        tags=["ticket27", "ticket27_lift", "nearby_positive"],
    )


def _select_benchmark_config_path(entry: dict[str, Any]) -> str:
    config_refs = list(entry.get("config_refs", []))
    benchmark_refs = [
        ref
        for ref in config_refs
        if ref.startswith("configs/recombination/benchmarks/")
    ]
    if benchmark_refs:
        return benchmark_refs[0]
    if config_refs:
        return config_refs[0]
    raise ValueError(f"seed entry {entry['stable_id']} has no config refs")


def _canonical_key(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((key, _canonical_key(item)) for key, item in sorted(value.items()))
    if isinstance(value, list):
        return tuple(_canonical_key(item) for item in value)
    return value


def _fingerprint(signature_payload: dict[str, Any]) -> str:
    return json.dumps(signature_payload, sort_keys=True)


def _structuralize_completion_signature(signature: Any) -> Any:
    if isinstance(signature, dict):
        cleaned = {}
        for key, value in signature.items():
            if key in {"family_id", "event_package_id"}:
                continue
            cleaned[key] = _structuralize_completion_signature(value)
        return cleaned
    if isinstance(signature, list):
        return [_structuralize_completion_signature(item) for item in signature]
    return signature


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


__all__ = [
    "LIFT_INTRINSIC_BASELINE_ARTIFACT",
    "LIFT_NOTE_ARTIFACT",
    "LIFT_SELECTION_REGISTRY_ARTIFACT",
    "LIFT_SELECTION_SUMMARY_ARTIFACT",
    "REPRESENTATIVE_FRONTIER_ARTIFACT",
    "build_intrinsic_baseline_artifact",
    "build_lift_note",
    "build_lift_selection_registry",
    "build_lift_selection_summary",
    "build_representative_frontier",
    "build_ticket27_lift_artifacts",
]
