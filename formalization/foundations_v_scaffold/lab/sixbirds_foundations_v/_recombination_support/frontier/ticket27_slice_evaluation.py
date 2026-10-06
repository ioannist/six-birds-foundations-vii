from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._recombination_support.completion.ticket27_lift_selection import (
    FLAGSHIP_IDS,
    NEARBY_POSITIVE_IDS,
    REQUIRED_CONTROL_IDS,
    _contrast_preserved,
    _flagship_candidates_structurally_match,
    _proposal_payload,
)
from sixbirds_foundations_v._recombination_support.frontier.engine import evaluate_frozen_slice, validate_frozen_slice_metric_names
from sixbirds_foundations_v._recombination_support.schemas import FrozenSliceConfig

from .ticket27_slice_scaffold import (
    FIELD_TO_METRIC_NAME,
    LEDGER_SMOKE_ARTIFACT,
    ROUTE_COMPLEXITY_PENALTY,
    R2_GATE_DECISION_ARTIFACT,
    R2_SECOND_STAGE_REGISTRY_ARTIFACT,
    R2_SECOND_STAGE_SUMMARY_ARTIFACT,
    SLICE_REGISTRY_ARTIFACT,
    SUPPORT_ATOM_ID,
    _load_json,
    _make_candidate_row,
    _to_frontier_candidate_observation_ledger,
    _write_json_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

SEED_CORPUS_ARTIFACT = "results/derived/ticket27_seed_corpus.json"
LIFT_INTRINSIC_BASELINE_ARTIFACT = "results/derived/ticket27_lift_intrinsic_baseline.json"
LIFT_SELECTION_REGISTRY_ARTIFACT = "results/derived/ticket27_lift_selection_registry.json"
LIFT_SELECTION_SUMMARY_ARTIFACT = "results/derived/ticket27_lift_selection_summary.json"

FULL_LEDGER_ARTIFACT = "results/derived/ticket27_candidate_observation_ledger.json"
FULL_EQUIVALENCE_ARTIFACT = "results/derived/ticket27_slice_equivalence_classes.json"
FULL_FRONTIER_ARTIFACT = "results/derived/ticket27_slice_frontiers.json"
SHADOW_PRICE_ARTIFACT = "results/derived/ticket27_shadow_price_summary.json"
SLICE_NOTE_ARTIFACT = "results/notes/ticket27_slice_note.md"

CONTROL_LABELS = {
    "t27.control.null_baseline": "null_baseline",
    "t27.control.memory_only": "memory_only",
    "t27.control.artifact": "artifact",
    "t27.control.boundary_collapse": "boundary_completion_sensitive",
}


def build_ticket27_full_slice_evaluation_artifacts(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    slice_registry = _load_json(resolved_repo_root / SLICE_REGISTRY_ARTIFACT)
    ledger = build_ticket27_candidate_observation_ledger(repo_root=resolved_repo_root)
    equivalence = build_ticket27_slice_equivalence_classes(ledger)
    frontiers = build_ticket27_slice_frontiers(ledger, slice_registry=slice_registry)
    shadow = build_ticket27_shadow_price_summary(
        ledger,
        equivalence_payload=equivalence,
        frontier_payload=frontiers,
        slice_registry=slice_registry,
    )
    note = build_ticket27_slice_note(
        frontier_payload=frontiers,
        shadow_payload=shadow,
    )

    ledger_path = _write_json_artifact(resolved_repo_root / FULL_LEDGER_ARTIFACT, ledger)
    equivalence_path = _write_json_artifact(
        resolved_repo_root / FULL_EQUIVALENCE_ARTIFACT,
        equivalence,
    )
    frontier_path = _write_json_artifact(resolved_repo_root / FULL_FRONTIER_ARTIFACT, frontiers)
    shadow_path = _write_json_artifact(resolved_repo_root / SHADOW_PRICE_ARTIFACT, shadow)
    note_path = resolved_repo_root / SLICE_NOTE_ARTIFACT
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")
    return {
        "ledger_path": ledger_path,
        "equivalence_path": equivalence_path,
        "frontier_path": frontier_path,
        "shadow_path": shadow_path,
        "note_path": note_path,
        "branch_decision": shadow["branch_decision"],
    }


def build_ticket27_candidate_observation_ledger(
    *,
    repo_root: Path | None = None,
    lift_registry_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    seed_corpus = _load_json(resolved_repo_root / SEED_CORPUS_ARTIFACT)
    r2_registry = _load_json(resolved_repo_root / R2_SECOND_STAGE_REGISTRY_ARTIFACT)
    r2_summary = _load_json(resolved_repo_root / R2_SECOND_STAGE_SUMMARY_ARTIFACT)
    gate_payload = _load_json(resolved_repo_root / R2_GATE_DECISION_ARTIFACT)
    intrinsic_baseline = _load_json(resolved_repo_root / LIFT_INTRINSIC_BASELINE_ARTIFACT)
    lift_registry = lift_registry_payload or _load_json(resolved_repo_root / LIFT_SELECTION_REGISTRY_ARTIFACT)
    lift_summary = _load_json(resolved_repo_root / LIFT_SELECTION_SUMMARY_ARTIFACT)

    rows = []
    rows.extend(
        _build_intrinsic_rows(
            seed_corpus=seed_corpus,
            r2_registry=r2_registry,
            gate_payload=gate_payload,
            intrinsic_baseline=intrinsic_baseline,
        )
    )
    rows.extend(_build_lift_route_class_rows(lift_registry=lift_registry))
    rows.extend(_build_lift_strategy_rows(lift_registry=lift_registry))

    equivalence = _compute_material_equivalence(rows)
    class_by_candidate = equivalence["class_by_candidate_id"]
    enriched_rows = []
    for row in rows:
        enriched_row = dict(row)
        enriched_row["material_equivalence_class_id"] = class_by_candidate[row["candidate_id"]]
        enriched_rows.append(enriched_row)

    return {
        "ticket": "T27-12",
        "schema_version": "ticket27-candidate-observation-ledger.v1",
        "canonical_input_artifacts": [
            SEED_CORPUS_ARTIFACT,
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_SUMMARY_ARTIFACT,
            R2_GATE_DECISION_ARTIFACT,
            LIFT_INTRINSIC_BASELINE_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
            LIFT_SELECTION_SUMMARY_ARTIFACT,
            SLICE_REGISTRY_ARTIFACT,
        ],
        "source_smoke_reference_artifact": LEDGER_SMOKE_ARTIFACT,
        "current_gate_decision": gate_payload["gate_decision"],
        "route_complexity_penalty_by_candidate_kind": dict(ROUTE_COMPLEXITY_PENALTY),
        "rows": enriched_rows,
    }


def build_ticket27_slice_equivalence_classes(
    ledger_payload: dict[str, Any],
) -> dict[str, Any]:
    rows = ledger_payload["rows"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["material_equivalence_class_id"]].append(row)

    classes = []
    for class_id in sorted(grouped):
        members = sorted(grouped[class_id], key=lambda item: item["candidate_id"])
        representative = members[0]
        classes.append(
            {
                "material_equivalence_class_id": class_id,
                "candidate_ids": [member["candidate_id"] for member in members],
                "class_type": _class_type_for_row(representative),
                "representative_summary": {
                    "route_class": representative["route_class"],
                    "proposal_id": representative["proposal_id"],
                    "family_id": representative["family_id"],
                    "flattening_mode": representative["flattening_mode"],
                    "flagship_gate_supported_count": representative["flagship_gate_supported_count"],
                    "flagship_non_fallback_supported_count": representative[
                        "flagship_non_fallback_supported_count"
                    ],
                    "preserved_required_control_contrast_count": representative[
                        "preserved_required_control_contrast_count"
                    ],
                    "nearby_positive_supported_count": representative[
                        "nearby_positive_supported_count"
                    ],
                    "best_common_flagship_burden": representative[
                        "best_common_flagship_burden"
                    ],
                    "route_complexity_penalty": representative["route_complexity_penalty"],
                    "fallback_involved": representative["fallback_involved"],
                    "representative_selection_effective": representative[
                        "representative_selection_effective"
                    ],
                },
            }
        )
    return {
        "ticket": "T27-12",
        "schema_version": "ticket27-slice-equivalence-classes.v1",
        "equivalence_key_fields": [
            "route_class",
            "proposal_id",
            "family_id",
            "flattening_mode",
            "flagship_gate_supported_count",
            "flagship_non_fallback_supported_count",
            "preserved_required_control_contrast_count",
            "nearby_positive_supported_count",
            "best_common_flagship_burden",
            "route_complexity_penalty",
            "fallback_involved",
            "representative_selection_effective",
            "target_package_size",
        ],
        "classes": classes,
    }


def build_ticket27_slice_frontiers(
    ledger_payload: dict[str, Any],
    *,
    slice_registry: dict[str, Any],
) -> dict[str, Any]:
    candidate_index = {row["candidate_id"]: row for row in ledger_payload["rows"]}
    frontier_ledger = _to_frontier_candidate_observation_ledger(ledger_payload["rows"])
    class_representatives = _class_representative_rows(ledger_payload["rows"])

    frontier_results = []
    for slice_payload in slice_registry["slices"]:
        config = FrozenSliceConfig.model_validate(slice_payload["frozen_slice_config"])
        validate_frozen_slice_metric_names(config)
        result = evaluate_frozen_slice(config, frontier_ledger)
        raw_non_dominated = sorted(result.frontier_candidate_ids)
        material_non_dominated = sorted(
            {
                candidate_index[candidate_id]["material_equivalence_class_id"]
                for candidate_id in raw_non_dominated
            }
        )
        winner_equivalence_classes = _winner_equivalence_classes_for_slice(
            material_non_dominated,
            slice_payload=slice_payload,
            class_representatives=class_representatives,
        )
        winner_candidate_ids = sorted(
            [
                row["candidate_id"]
                for row in ledger_payload["rows"]
                if row["material_equivalence_class_id"] in winner_equivalence_classes
            ]
        )
        frontier_results.append(
            {
                "slice_id": slice_payload["slice_id"],
                "yield_fields": slice_payload["yield_fields"],
                "cost_fields": slice_payload["cost_fields"],
                "candidate_ids_considered": [row["candidate_id"] for row in ledger_payload["rows"]],
                "raw_non_dominated_candidate_ids": raw_non_dominated,
                "material_non_dominated_equivalence_class_ids": material_non_dominated,
                "winner_candidate_ids": winner_candidate_ids,
                "winner_equivalence_class_ids": winner_equivalence_classes,
                "winner_pattern": (
                    "single_material_winner"
                    if len(winner_equivalence_classes) == 1
                    else "multiple_material_winners"
                ),
                "candidate_metric_summaries": [
                    {
                        "candidate_id": result_row.candidate_id,
                        "material_equivalence_class_id": candidate_index[result_row.candidate_id][
                            "material_equivalence_class_id"
                        ],
                        "candidate_kind": candidate_index[result_row.candidate_id]["candidate_kind"],
                        "route_class": candidate_index[result_row.candidate_id]["route_class"],
                        "strategy_id": candidate_index[result_row.candidate_id]["strategy_id"],
                        "proposal_id": candidate_index[result_row.candidate_id]["proposal_id"],
                        "family_id": candidate_index[result_row.candidate_id]["family_id"],
                        "flattening_mode": candidate_index[result_row.candidate_id][
                            "flattening_mode"
                        ],
                        "aggregated_yield_vector": result_row.aggregated_yield_vector,
                        "aggregated_cost_vector": result_row.aggregated_cost_vector,
                        "frontier_member": result_row.frontier_member,
                        "dominated_by": result_row.dominated_by,
                    }
                    for result_row in result.rows
                ],
            }
        )

    return {
        "ticket": "T27-12",
        "schema_version": "ticket27-slice-frontiers.v1",
        "ledger_artifact": FULL_LEDGER_ARTIFACT,
        "slice_registry_artifact": SLICE_REGISTRY_ARTIFACT,
        "frontier_results": frontier_results,
    }


def build_ticket27_shadow_price_summary(
    ledger_payload: dict[str, Any],
    *,
    equivalence_payload: dict[str, Any],
    frontier_payload: dict[str, Any],
    slice_registry: dict[str, Any],
) -> dict[str, Any]:
    del slice_registry
    class_payloads = {
        payload["material_equivalence_class_id"]: payload
        for payload in equivalence_payload["classes"]
    }
    row_by_class = _class_representative_rows(ledger_payload["rows"])

    per_slice = {}
    winner_sets = {}
    for frontier_result in frontier_payload["frontier_results"]:
        class_ids = frontier_result["material_non_dominated_equivalence_class_ids"]
        winner_sets[frontier_result["slice_id"]] = sorted(frontier_result["winner_equivalence_class_ids"])
        frontier_rows = [row_by_class[class_id] for class_id in class_ids]
        nearby_class = _select_extreme_class(
            frontier_rows,
            maximize_field="nearby_positive_supported_count",
        )
        burden_class = _select_extreme_class(
            frontier_rows,
            minimize_field="best_common_flagship_burden",
        )
        complexity_class = _select_extreme_class(
            frontier_rows,
            minimize_field="route_complexity_penalty",
        )
        controls_class = _select_extreme_class(
            frontier_rows,
            maximize_field="preserved_required_control_contrast_count",
        )
        per_slice[frontier_result["slice_id"]] = {
            "material_frontier_equivalence_class_ids": class_ids,
            "winner_equivalence_class_ids": frontier_result["winner_equivalence_class_ids"],
            "tradeoff_proxies": {
                "delta_burden_per_extra_nearby_support": _delta_ratio(
                    numerator_value=_metric_value(nearby_class, "best_common_flagship_burden"),
                    denominator_value=_metric_value(nearby_class, "nearby_positive_supported_count")
                    - _metric_value(burden_class, "nearby_positive_supported_count"),
                    baseline_numerator=_metric_value(burden_class, "best_common_flagship_burden"),
                    source_class_ids=[
                        burden_class["material_equivalence_class_id"],
                        nearby_class["material_equivalence_class_id"],
                    ],
                ),
                "delta_complexity_per_burden_reduction": _delta_ratio(
                    numerator_value=_metric_value(complexity_class, "route_complexity_penalty"),
                    denominator_value=_metric_value(complexity_class, "best_common_flagship_burden")
                    - _metric_value(burden_class, "best_common_flagship_burden"),
                    baseline_numerator=_metric_value(burden_class, "route_complexity_penalty"),
                    source_class_ids=[
                        burden_class["material_equivalence_class_id"],
                        complexity_class["material_equivalence_class_id"],
                    ],
                ),
                "delta_controls_per_burden_increase": _delta_ratio(
                    numerator_value=_metric_value(controls_class, "preserved_required_control_contrast_count"),
                    denominator_value=_metric_value(controls_class, "best_common_flagship_burden")
                    - _metric_value(burden_class, "best_common_flagship_burden"),
                    baseline_numerator=_metric_value(
                        burden_class, "preserved_required_control_contrast_count"
                    ),
                    source_class_ids=[
                        burden_class["material_equivalence_class_id"],
                        controls_class["material_equivalence_class_id"],
                    ],
                ),
            },
        }

    unique_winner_sets = {
        tuple(class_ids) for class_ids in winner_sets.values()
    }
    material_winner_sets_agree = len(unique_winner_sets) == 1
    responsible_dimensions = []
    if winner_sets.get("coverage_first") != winner_sets.get("stability_first"):
        responsible_dimensions.append("nearby_positive_supported_count")
    if winner_sets.get("parsimony_first") != winner_sets.get("stability_first"):
        responsible_dimensions.append("route_complexity_penalty")
    if not responsible_dimensions and not material_winner_sets_agree:
        responsible_dimensions.append("best_common_flagship_burden")

    all_class_ids = list(class_payloads)
    global_best_burden = min(
        _metric_value(row_by_class[class_id], "best_common_flagship_burden") for class_id in all_class_ids
    )
    global_best_nearby = max(
        _metric_value(row_by_class[class_id], "nearby_positive_supported_count") for class_id in all_class_ids
    )
    global_best_complexity = min(
        _metric_value(row_by_class[class_id], "route_complexity_penalty") for class_id in all_class_ids
    )
    global_best_controls = max(
        _metric_value(row_by_class[class_id], "preserved_required_control_contrast_count")
        for class_id in all_class_ids
    )
    simultaneously_optimizing_classes = sorted(
        [
            class_id
            for class_id in all_class_ids
            if _metric_value(row_by_class[class_id], "best_common_flagship_burden") == global_best_burden
            and _metric_value(row_by_class[class_id], "nearby_positive_supported_count")
            == global_best_nearby
            and _metric_value(row_by_class[class_id], "route_complexity_penalty")
            == global_best_complexity
            and _metric_value(
                row_by_class[class_id], "preserved_required_control_contrast_count"
            )
            == global_best_controls
        ]
    )
    stable_tradeoff_without_single_optimizer = not simultaneously_optimizing_classes

    if not material_winner_sets_agree or stable_tradeoff_without_single_optimizer:
        branch_decision = "DUAL_ROUTE_LIVE"
        core_signal = "slice_selected_tradeoff"
    else:
        branch_decision = "DUAL_ROUTE_WEAK"
        core_signal = "single_carrier_like"

    return {
        "ticket": "T27-12",
        "schema_version": "ticket27-shadow-price-summary.v1",
        "frontier_artifact": FULL_FRONTIER_ARTIFACT,
        "equivalence_artifact": FULL_EQUIVALENCE_ARTIFACT,
        "per_slice_tradeoff_summary": per_slice,
        "cross_slice_winner_comparison": {
            "winner_equivalence_class_ids_by_slice": winner_sets,
            "material_winner_sets_agree": material_winner_sets_agree,
            "responsible_dimensions": sorted(set(responsible_dimensions)),
        },
        "core_case_dual_signal": {
            "label": core_signal,
            "stable_tradeoff_without_single_optimizer": stable_tradeoff_without_single_optimizer,
            "simultaneously_optimizing_class_ids": simultaneously_optimizing_classes,
        },
        "branch_decision": branch_decision,
    }


def build_ticket27_slice_note(
    *,
    frontier_payload: dict[str, Any],
    shadow_payload: dict[str, Any],
) -> str:
    lines = [
        "# Ticket27 Slice Note",
        "",
        f"- Branch decision: `{shadow_payload['branch_decision']}`.",
    ]
    for frontier_result in frontier_payload["frontier_results"]:
        lines.append(
            f"- `{frontier_result['slice_id']}` winners: {', '.join(f'`{class_id}`' for class_id in frontier_result['winner_equivalence_class_ids'])}."
        )
    lines.append(
        "- Cross-slice material winner agreement: "
        f"`{shadow_payload['cross_slice_winner_comparison']['material_winner_sets_agree']}`."
    )
    return "\n".join(lines)


def _build_intrinsic_rows(
    *,
    seed_corpus: dict[str, Any],
    r2_registry: dict[str, Any],
    gate_payload: dict[str, Any],
    intrinsic_baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    del seed_corpus
    by_id = {case["stable_id"]: case for case in r2_registry["cases"]}
    qualifying_proposals = {
        candidate["proposal_id"] for candidate in gate_payload.get("qualifying_candidates", [])
    }
    rows = []

    baseline = intrinsic_baseline["best_intrinsic_envelope"]
    if baseline is not None:
        baseline_row = _build_intrinsic_row(
            proposal_id=baseline["proposal_id"],
            by_id=by_id,
            gate_supported=baseline["proposal_id"] in qualifying_proposals,
            candidate_id="candidate.intrinsic_baseline.best_envelope",
            candidate_kind="intrinsic_baseline_envelope",
            selection_basis_summary=(
                "Best intrinsic envelope carried forward from the full T27-10 ranking over qualifying "
                "r2 proposals."
            ),
        )
        rows.append(baseline_row)

    for proposal_id in r2_registry["proposal_ids"]:
        if any(_proposal_payload(by_id[stable_id], proposal_id) is None for stable_id in FLAGSHIP_IDS):
            continue
        rows.append(
            _build_intrinsic_row(
                proposal_id=proposal_id,
                by_id=by_id,
                gate_supported=proposal_id in qualifying_proposals,
                candidate_id=f"candidate.intrinsic_proposal.{proposal_id}",
                candidate_kind="intrinsic_proposal",
                selection_basis_summary="Evaluable intrinsic proposal derived directly from the r2 second-stage registry.",
            )
        )
    return rows


def _build_intrinsic_row(
    *,
    proposal_id: str,
    by_id: dict[str, dict[str, Any]],
    gate_supported: bool,
    candidate_id: str,
    candidate_kind: str,
    selection_basis_summary: str,
) -> dict[str, Any]:
    left = _proposal_payload(by_id[FLAGSHIP_IDS[0]], proposal_id)
    right = _proposal_payload(by_id[FLAGSHIP_IDS[1]], proposal_id)
    assert left is not None and right is not None

    preserved_controls = []
    required_control_breakdown = {}
    for control_id in REQUIRED_CONTROL_IDS:
        control_payload = _proposal_payload(by_id[control_id], proposal_id)
        preserved = (
            control_payload is not None
            and _contrast_preserved(left, control_payload)
            and _contrast_preserved(right, control_payload)
        )
        if preserved:
            preserved_controls.append(control_id)
        required_control_breakdown[CONTROL_LABELS[control_id]] = {
            "stable_id": control_id,
            "preserved": preserved,
            "target_package_size": (
                control_payload["target_package_size"] if control_payload is not None else None
            ),
        }

    nearby_breakdown = {}
    nearby_count = 0
    for nearby_id in NEARBY_POSITIVE_IDS:
        payload = _proposal_payload(by_id[nearby_id], proposal_id)
        supported = bool(payload and payload["proposal"]["non_identity"])
        if supported:
            nearby_count += 1
        nearby_breakdown[nearby_id] = {
            "supported": supported,
            "target_package_size": payload["target_package_size"] if payload else None,
        }

    structurally_reproducible = _flagship_candidates_structurally_match(left, right)
    flagship_breakdown = {
        stable_id: _intrinsic_flagship_breakdown(
            payload=_proposal_payload(by_id[stable_id], proposal_id),
            structurally_reproducible=structurally_reproducible,
            gate_supported=gate_supported,
        )
        for stable_id in FLAGSHIP_IDS
    }

    row = _make_candidate_row(
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        route_class="intrinsic_surface_coarsening",
        strategy_id=None,
        proposal_id=proposal_id,
        family_id=None,
        flattening_mode=None,
        source_artifacts=[
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_SUMMARY_ARTIFACT,
            R2_GATE_DECISION_ARTIFACT,
        ],
        flagship_gate_supported_count=2 if gate_supported else 0,
        flagship_non_fallback_supported_count=2 if gate_supported else 0,
        preserved_required_control_contrast_count=len(preserved_controls),
        nearby_positive_supported_count=nearby_count,
        best_common_flagship_burden=_intrinsic_burden_for_proposal(proposal_id),
        target_package_size=left["target_package_size"],
        fallback_involved=False,
        representative_selection_effective=False,
        selection_basis_summary=selection_basis_summary,
    )
    row.update(
        {
            "required_control_breakdown": required_control_breakdown,
            "flagship_breakdown": flagship_breakdown,
            "nearby_breakdown": nearby_breakdown,
            "jointly_evaluable_on_flagship_core": True,
        }
    )
    return row


def _build_lift_route_class_rows(
    *,
    lift_registry: dict[str, Any],
) -> list[dict[str, Any]]:
    groups = _group_lift_registry_rows(
        lift_registry["rows"],
        key_fields=("family_id", "flattening_mode", "best_second_stage_proposal_id"),
    )
    rows = []
    for (family_id, flattening_mode, proposal_id), group_rows in sorted(groups.items()):
        if not _jointly_evaluable_on_flagship_core(group_rows):
            continue
        rows.append(
            _build_lift_group_row(
                candidate_id=(
                    "candidate.lift_route_class."
                    f"{family_id}.{flattening_mode}.{proposal_id}"
                ),
                candidate_kind="lift_route_class",
                route_class="representative_selected_lift",
                strategy_id=None,
                family_id=family_id,
                flattening_mode=flattening_mode,
                proposal_id=proposal_id,
                grouped_rows=group_rows,
                representative_selection_effective=False,
                selection_basis_summary=(
                    "Order-independent lift route-class aggregate derived from raw "
                    "(family_id, flattening_mode, proposal_id) registry grouping."
                ),
            )
        )
    return rows


def _build_lift_strategy_rows(
    *,
    lift_registry: dict[str, Any],
) -> list[dict[str, Any]]:
    groups = _group_lift_registry_rows(
        lift_registry["rows"],
        key_fields=("strategy_id", "family_id", "flattening_mode", "best_second_stage_proposal_id"),
    )
    rows = []
    for (strategy_id, family_id, flattening_mode, proposal_id), group_rows in sorted(groups.items()):
        if not _jointly_evaluable_on_flagship_core(group_rows):
            continue
        rows.append(
            _build_lift_group_row(
                candidate_id=(
                    "candidate.lift_strategy."
                    f"{strategy_id}.{family_id}.{flattening_mode}.{proposal_id}"
                ),
                candidate_kind="lift_strategy",
                route_class="representative_selected_lift",
                strategy_id=strategy_id,
                family_id=family_id,
                flattening_mode=flattening_mode,
                proposal_id=proposal_id,
                grouped_rows=group_rows,
                representative_selection_effective=_lift_group_selection_effective(group_rows),
                selection_basis_summary=(
                    "Jointly evaluable lift strategy route derived from raw "
                    "(strategy_id, family_id, flattening_mode, proposal_id) grouping."
                ),
            )
        )
    return rows


def _build_lift_group_row(
    *,
    candidate_id: str,
    candidate_kind: str,
    route_class: str,
    strategy_id: str | None,
    family_id: str,
    flattening_mode: str,
    proposal_id: str,
    grouped_rows: list[dict[str, Any]],
    representative_selection_effective: bool,
    selection_basis_summary: str,
) -> dict[str, Any]:
    flagship_rows = {
        stable_id: [
            row
            for row in grouped_rows
            if row["stable_id"] == stable_id and row["skip_reason"] is None
        ]
        for stable_id in FLAGSHIP_IDS
    }
    gate_supported_flagships = {
        stable_id: any(row["flagship_core_gate_satisfied"] for row in rows)
        for stable_id, rows in flagship_rows.items()
    }
    non_fallback_flagships = {
        stable_id: any(row["flagship_core_gate_satisfied"] and not row["fallback_used"] for row in rows)
        for stable_id, rows in flagship_rows.items()
    }
    flagship_gate_supported_count = sum(1 for value in gate_supported_flagships.values() if value)
    flagship_non_fallback_supported_count = sum(
        1 for value in non_fallback_flagships.values() if value
    )

    control_sets = [
        set(row["preserved_required_control_contrasts"])
        for rows in flagship_rows.values()
        for row in rows
        if row["flagship_core_gate_satisfied"]
    ]
    preserved_controls = sorted(set.intersection(*control_sets)) if control_sets else []
    required_control_breakdown = {
        CONTROL_LABELS[control_id]: {
            "stable_id": control_id,
            "preserved": control_id in preserved_controls,
        }
        for control_id in REQUIRED_CONTROL_IDS
    }

    nearby_breakdown = {}
    nearby_count = 0
    for nearby_id in NEARBY_POSITIVE_IDS:
        nearby_rows = [
            row for row in grouped_rows if row["stable_id"] == nearby_id and row["skip_reason"] is None
        ]
        supported = any(
            row["best_second_stage_target_package_size"] < len(row["selected_class_summaries"])
            for row in nearby_rows
        )
        if supported:
            nearby_count += 1
        nearby_breakdown[nearby_id] = {
            "supported": supported,
            "observed_row_count": len(nearby_rows),
        }

    target_size = _common_or_none(
        [
            row["best_second_stage_target_package_size"]
            for rows in flagship_rows.values()
            for row in rows
            if row["flagship_core_gate_satisfied"]
        ]
    )
    burden = _common_or_none(
        [
            row["best_second_stage_coarsening_burden"]
            for rows in flagship_rows.values()
            for row in rows
            if row["flagship_core_gate_satisfied"]
        ]
    )
    fallback_involved = any(
        not non_fallback_flagships[stable_id] and gate_supported_flagships[stable_id]
        for stable_id in FLAGSHIP_IDS
    )
    flagship_breakdown = {
        stable_id: {
            "row_count": len(flagship_rows[stable_id]),
            "gate_supported": gate_supported_flagships[stable_id],
            "non_fallback_supported": non_fallback_flagships[stable_id],
            "target_package_size": _common_or_none(
                [row["best_second_stage_target_package_size"] for row in flagship_rows[stable_id]]
            ),
            "strategy_ids": sorted({row["strategy_id"] for row in flagship_rows[stable_id]}),
        }
        for stable_id in FLAGSHIP_IDS
    }

    row = _make_candidate_row(
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        route_class=route_class,
        strategy_id=strategy_id,
        proposal_id=proposal_id,
        family_id=family_id,
        flattening_mode=flattening_mode,
        source_artifacts=[LIFT_SELECTION_REGISTRY_ARTIFACT, LIFT_SELECTION_SUMMARY_ARTIFACT],
        flagship_gate_supported_count=flagship_gate_supported_count,
        flagship_non_fallback_supported_count=flagship_non_fallback_supported_count,
        preserved_required_control_contrast_count=len(preserved_controls),
        nearby_positive_supported_count=nearby_count,
        best_common_flagship_burden=burden,
        target_package_size=target_size,
        fallback_involved=fallback_involved,
        representative_selection_effective=representative_selection_effective,
        selection_basis_summary=selection_basis_summary,
    )
    row.update(
        {
            "required_control_breakdown": required_control_breakdown,
            "flagship_breakdown": flagship_breakdown,
            "nearby_breakdown": nearby_breakdown,
            "jointly_evaluable_on_flagship_core": True,
        }
    )
    return row


def _compute_material_equivalence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_material_equivalence_key(row)].append(row)
    class_by_candidate: dict[str, str] = {}
    for index, key in enumerate(sorted(grouped, key=lambda item: repr(item)), start=1):
        class_id = f"ticket27.material_class.{index:02d}"
        for row in grouped[key]:
            class_by_candidate[row["candidate_id"]] = class_id
    return {"class_by_candidate_id": class_by_candidate}


def _material_equivalence_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["route_class"],
        row["proposal_id"],
        row["family_id"],
        row["flattening_mode"],
        row["flagship_gate_supported_count"],
        row["flagship_non_fallback_supported_count"],
        row["preserved_required_control_contrast_count"],
        row["nearby_positive_supported_count"],
        row["best_common_flagship_burden"],
        row["route_complexity_penalty"],
        row["fallback_involved"],
        row["representative_selection_effective"],
        row["target_package_size"],
    )


def _class_type_for_row(row: dict[str, Any]) -> str:
    if row["route_class"] == "intrinsic_surface_coarsening":
        return "intrinsic_like"
    if row["representative_selection_effective"]:
        return "strategy_specific"
    return "lift_route_like"


def _class_representative_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["material_equivalence_class_id"]].append(row)
    return {
        class_id: sorted(grouped[class_id], key=lambda item: item["candidate_id"])[0]
        for class_id in grouped
    }


def _winner_equivalence_classes_for_slice(
    material_frontier_class_ids: list[str],
    *,
    slice_payload: dict[str, Any],
    class_representatives: dict[str, dict[str, Any]],
) -> list[str]:
    if not material_frontier_class_ids:
        return []
    scored = []
    for class_id in material_frontier_class_ids:
        row = class_representatives[class_id]
        vector = tuple(
            [-_metric_value(row, field_name) for field_name in slice_payload["yield_fields"]]
            + [_metric_value(row, field_name) for field_name in slice_payload["cost_fields"]]
        )
        scored.append((vector, class_id))
    best_vector = min(vector for vector, _ in scored)
    return sorted([class_id for vector, class_id in scored if vector == best_vector])


def _group_lift_registry_rows(
    rows: list[dict[str, Any]],
    *,
    key_fields: tuple[str, ...],
) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["skip_reason"] is not None:
            continue
        key = tuple(row[field_name] for field_name in key_fields)
        grouped[key].append(row)
    return grouped


def _jointly_evaluable_on_flagship_core(group_rows: list[dict[str, Any]]) -> bool:
    flagship_ids = {row["stable_id"] for row in group_rows if row["stable_id"] in FLAGSHIP_IDS}
    return flagship_ids == set(FLAGSHIP_IDS)


def _lift_group_selection_effective(group_rows: list[dict[str, Any]]) -> bool:
    strategy_ids = {row["strategy_id"] for row in group_rows}
    if strategy_ids == {"identity_reference"}:
        return False
    return any(
        row["stable_id"] in FLAGSHIP_IDS and row["mapping_differs_from_identity_reference"]
        for row in group_rows
    )


def _intrinsic_flagship_breakdown(
    *,
    payload: dict[str, Any] | None,
    structurally_reproducible: bool,
    gate_supported: bool,
) -> dict[str, Any]:
    if payload is None:
        return {
            "applicable": False,
            "non_identity": False,
            "closure_status": None,
            "target_package_size": None,
            "structurally_reproducible": False,
            "gate_supported": False,
        }
    return {
        "applicable": True,
        "non_identity": payload["proposal"]["non_identity"],
        "closure_status": payload["closure_status"],
        "target_package_size": payload["target_package_size"],
        "structurally_reproducible": structurally_reproducible,
        "gate_supported": gate_supported,
    }


def _intrinsic_burden_for_proposal(proposal_id: str) -> int:
    if proposal_id == "identity_surface":
        return 0
    if proposal_id in {
        "screen_label_anonymized",
        "screen_history_removed",
        "completion_removed",
    }:
        return 1
    return 2


def _select_extreme_class(
    rows: list[dict[str, Any]],
    *,
    maximize_field: str | None = None,
    minimize_field: str | None = None,
) -> dict[str, Any]:
    assert (maximize_field is None) != (minimize_field is None)
    if maximize_field is not None:
        return sorted(
            rows,
            key=lambda row: (
                -_metric_value(row, maximize_field),
                _metric_value(row, "best_common_flagship_burden"),
                row["material_equivalence_class_id"],
            ),
        )[0]
    return sorted(
        rows,
        key=lambda row: (
            _metric_value(row, minimize_field),
            -_metric_value(row, "preserved_required_control_contrast_count"),
            row["material_equivalence_class_id"],
        ),
    )[0]


def _delta_ratio(
    *,
    numerator_value: int | float,
    denominator_value: int | float,
    baseline_numerator: int | float,
    source_class_ids: list[str],
) -> dict[str, Any]:
    delta_numerator = numerator_value - baseline_numerator
    if denominator_value == 0:
        ratio = None
    else:
        ratio = delta_numerator / denominator_value
    return {
        "value": ratio,
        "delta_numerator": delta_numerator,
        "delta_denominator": denominator_value,
        "source_equivalence_class_ids": source_class_ids,
    }


def _metric_value(row: dict[str, Any], field_name: str) -> int | float:
    value = row[field_name]
    if isinstance(value, bool):
        return 1 if value else 0
    assert value is not None
    return value


def _common_or_none(values: list[Any]) -> Any:
    values = [value for value in values if value is not None]
    if not values:
        return None
    first = values[0]
    return first if all(value == first for value in values) else None
