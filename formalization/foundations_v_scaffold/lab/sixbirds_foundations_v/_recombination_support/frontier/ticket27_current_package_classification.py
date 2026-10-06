from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ticket27_staging_packaging import (
    CANDIDATE_LEDGER_ARTIFACT,
    PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
    PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
    PROTOCOL_REGISTRY_ARTIFACT,
    PROTOCOL_SUMMARY_ARTIFACT,
    SHADOW_PRICE_SUMMARY_ARTIFACT,
    SLICE_FRONTIERS_ARTIFACT,
    _load_json,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

R2_SECOND_STAGE_REGISTRY_ARTIFACT = "results/derived/ticket27r2_second_stage_registry.json"
R2_SECOND_STAGE_STABILITY_SUMMARY_ARTIFACT = (
    "results/derived/ticket27r2_second_stage_stability_summary.json"
)
R2_GATE_DECISION_ARTIFACT = "results/derived/ticket27r2_gate_decision.json"
LIFT_INTRINSIC_BASELINE_ARTIFACT = "results/derived/ticket27_lift_intrinsic_baseline.json"
LIFT_SELECTION_REGISTRY_ARTIFACT = "results/derived/ticket27_lift_selection_registry.json"
LIFT_SELECTION_SUMMARY_ARTIFACT = "results/derived/ticket27_lift_selection_summary.json"
DEFECT_SUMMARY_ARTIFACT = "results/derived/ticket27_staging_packaging_defect_summary.json"
PROMOTION_DEFECT_ATLAS_ARTIFACT = "results/derived/ticket27_promotion_vs_defect_atlas.json"

THRESHOLDS_ARTIFACT = "results/derived/ticket27_classification_thresholds.json"
CURRENT_PACKAGE_ATLAS_ARTIFACT = "results/derived/ticket27_current_package_atlas.json"
CURRENT_PACKAGE_NOTE_ARTIFACT = "results/notes/ticket27_current_package_decision_note.md"
CURRENT_PACKAGE_DESIGN_ARTIFACT = "docs/internal/ticket27_classification_design.md"

SURVIVOR_LABELS = {
    "intrinsic_promotion",
    "lift_selected_promotion",
    "protocol_indexed_promotion",
}
PROTOCOL_LIVE_STATUSES = {
    "survives_without_protocol_requirement",
    "protocol_cleared_by_ticket27_adapter",
    "protocol_required",
}
FRESHNESS_DECISION_ELIGIBLE = {"fresh", "fresh_with_override"}
PAIR_FAMILY_KEY = ("paired_observable_enrichment", "paired_flattening_control")
DECLARED_FAMILY_KEY = ("declared_completion_family", "none")


def write_ticket27_current_package_artifacts(
    *,
    repo_root: Path | None = None,
) -> dict[str, Path]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    thresholds = build_ticket27_classification_thresholds()
    atlas = build_ticket27_current_package_atlas(
        repo_root=resolved_repo_root,
        thresholds_payload=thresholds,
    )
    note = build_ticket27_current_package_decision_note(atlas_payload=atlas)
    design = build_ticket27_classification_design_note()

    thresholds_path = resolved_repo_root / THRESHOLDS_ARTIFACT
    thresholds_path.parent.mkdir(parents=True, exist_ok=True)
    thresholds_path.write_text(
        json.dumps(thresholds, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    atlas_path = resolved_repo_root / CURRENT_PACKAGE_ATLAS_ARTIFACT
    atlas_path.parent.mkdir(parents=True, exist_ok=True)
    atlas_path.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    note_path = resolved_repo_root / CURRENT_PACKAGE_NOTE_ARTIFACT
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")

    design_path = resolved_repo_root / CURRENT_PACKAGE_DESIGN_ARTIFACT
    design_path.parent.mkdir(parents=True, exist_ok=True)
    design_path.write_text(design, encoding="utf-8")

    return {
        "thresholds_path": thresholds_path,
        "atlas_path": atlas_path,
        "note_path": note_path,
        "design_path": design_path,
    }


def build_ticket27_classification_thresholds() -> dict[str, Any]:
    return {
        "ticket": "T27-17",
        "schema_version": "ticket27-current-package-thresholds.v1",
        "label_vocabulary": [
            "compression_only",
            "intrinsic_promotion",
            "lift_selected_promotion",
            "slice_selected_dual_support_only",
            "protocol_indexed_promotion",
            "artifact",
            "no_promotion",
        ],
        "freshness_rules": {
            "fresh": {
                "decision_eligible": True,
                "description": (
                    "Current protocol-aware intrinsic or declared-family lift evidence backed "
                    "by live ticket27 artifacts."
                ),
            },
            "fresh_with_override": {
                "decision_eligible": True,
                "description": (
                    "Current evidence made decision-eligible only through the paired-family "
                    "protocol adapter override artifacts."
                ),
            },
            "supporting_provisional": {
                "decision_eligible": False,
                "description": "Supportive evidence that is not fresh enough to classify by itself.",
            },
            "stale": {
                "decision_eligible": False,
                "description": "Evidence that is not eligible for survivor classification.",
            },
        },
        "protocol_status_resolution": {
            "default_summary_artifact": PROTOCOL_SUMMARY_ARTIFACT,
            "default_registry_artifact": PROTOCOL_REGISTRY_ARTIFACT,
            "paired_family_override": {
                "family_id": PAIR_FAMILY_KEY[0],
                "flattening_mode": PAIR_FAMILY_KEY[1],
                "gate_artifact": PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
                "audit_artifact": PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
                "resolved_status": "protocol_cleared_by_ticket27_adapter",
                "resolved_artifact_contrast_status": "survives_pair_honestly",
                "override_condition": (
                    "Use the adapter-cleared paired-lift artifacts whenever the route family is "
                    "paired_observable_enrichment + paired_flattening_control."
                ),
            },
        },
        "survivor_thresholds": {
            "flagship_core_support_condition": {
                "machine_rule": (
                    "flagship_gate_supported_count >= 2 OR supports_both_flagships_honestly == true"
                ),
            },
            "required_protocol_statuses": sorted(PROTOCOL_LIVE_STATUSES),
            "artifact_collapse_reject_statuses": ["artifact_collapse", "collapses_under_pair"],
            "required_freshness_statuses": sorted(FRESHNESS_DECISION_ELIGIBLE),
            "decision_note": "Defect metric is not a primary classifier for survivor status.",
        },
        "label_rules": {
            "intrinsic_promotion": {
                "required_route_class": "intrinsic_surface_coarsening",
                "requires_survivor_threshold": True,
                "requires_protocol_indexed_dependence": False,
            },
            "lift_selected_promotion": {
                "required_route_class": "representative_selected_lift",
                "requires_survivor_threshold": True,
                "requires_lift_added_value": True,
                "strategy_superiority_guard": (
                    "Strategy rows may not claim strategy-specific superiority unless materially "
                    "distinct evidence supports it."
                ),
            },
            "protocol_indexed_promotion": {
                "required_protocol_status": "protocol_required",
                "requires_survivor_threshold": True,
            },
            "artifact": {
                "artifact_statuses": ["artifact_collapse", "collapses_under_pair"],
            },
            "compression_only": {
                "description": "Behaviorally useful but below the explicit survivor threshold.",
            },
            "slice_selected_dual_support_only": {
                "decision_eligible": False,
                "description": "Support-only slice/dual evidence pending a fresh rerun.",
            },
        },
        "non_gating_support_rules": {
            "defect_metric": "auxiliary_only",
            "slice_dual_evidence": "support_only_provisional",
            "strategy_tie_rule": "no_unique_best_strategy_claim_when_tied",
        },
        "branch_decision_rule": {
            "CURRENT_PACKAGE_SURVIVOR_EXISTS": {
                "machine_rule": (
                    "At least one decision-eligible flagship-core route family is labeled "
                    "intrinsic_promotion, lift_selected_promotion, or protocol_indexed_promotion."
                ),
            },
            "CURRENT_PACKAGE_ALL_FAIL": {
                "machine_rule": "No decision-eligible flagship-core route family has a survivor label.",
            },
        },
    }


def build_ticket27_current_package_atlas(
    *,
    repo_root: Path | None = None,
    thresholds_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    thresholds = thresholds_payload or build_ticket27_classification_thresholds()
    candidate_ledger = _load_json(resolved_repo_root / CANDIDATE_LEDGER_ARTIFACT)
    protocol_summary = _load_json(resolved_repo_root / PROTOCOL_SUMMARY_ARTIFACT)
    protocol_registry = _load_json(resolved_repo_root / PROTOCOL_REGISTRY_ARTIFACT)
    paired_gate = _load_json(resolved_repo_root / PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT)
    paired_audit = _load_json(resolved_repo_root / PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT)
    lift_baseline = _load_json(resolved_repo_root / LIFT_INTRINSIC_BASELINE_ARTIFACT)
    lift_summary = _load_json(resolved_repo_root / LIFT_SELECTION_SUMMARY_ARTIFACT)
    slice_frontiers = _load_json(resolved_repo_root / SLICE_FRONTIERS_ARTIFACT)
    shadow_price = _load_json(resolved_repo_root / SHADOW_PRICE_SUMMARY_ARTIFACT)
    defect_summary = _load_json(resolved_repo_root / DEFECT_SUMMARY_ARTIFACT)
    promotion_defect = _load_json(resolved_repo_root / PROMOTION_DEFECT_ATLAS_ARTIFACT)

    ledger_rows = candidate_ledger["rows"]
    ledger_index = {row["candidate_id"]: row for row in ledger_rows}
    protocol_registry_index = {row["candidate_id"]: row for row in protocol_registry["rows"]}
    protocol_summary_index = {
        row["candidate_id"]: row for row in protocol_summary["flagship_core_route_outcomes"]
    }
    lift_strategy_summaries = {
        row["strategy_id"]: row for row in lift_summary["strategies"]
    }

    representative_strategy_rows = _select_materially_distinct_strategy_rows(ledger_rows)
    candidate_rows = [
        _classify_row(
            ledger_row=ledger_index["candidate.intrinsic_baseline.best_envelope"],
            thresholds=thresholds,
            protocol_registry_index=protocol_registry_index,
            protocol_summary_index=protocol_summary_index,
            paired_gate=paired_gate,
            paired_audit=paired_audit,
            lift_baseline=lift_baseline,
            lift_strategy_summaries=lift_strategy_summaries,
            defect_summary=defect_summary,
        ),
        _classify_row(
            ledger_row=ledger_index["candidate.intrinsic_proposal.screen_label_anonymized_completion_removed"],
            thresholds=thresholds,
            protocol_registry_index=protocol_registry_index,
            protocol_summary_index=protocol_summary_index,
            paired_gate=paired_gate,
            paired_audit=paired_audit,
            lift_baseline=lift_baseline,
            lift_strategy_summaries=lift_strategy_summaries,
            defect_summary=defect_summary,
        ),
        _classify_row(
            ledger_row=ledger_index["candidate.lift_route_class.declared_completion_family.none.identity_surface"],
            thresholds=thresholds,
            protocol_registry_index=protocol_registry_index,
            protocol_summary_index=protocol_summary_index,
            paired_gate=paired_gate,
            paired_audit=paired_audit,
            lift_baseline=lift_baseline,
            lift_strategy_summaries=lift_strategy_summaries,
            defect_summary=defect_summary,
        ),
        _classify_row(
            ledger_row=ledger_index[
                "candidate.lift_route_class.paired_observable_enrichment.paired_flattening_control.identity_surface"
            ],
            thresholds=thresholds,
            protocol_registry_index=protocol_registry_index,
            protocol_summary_index=protocol_summary_index,
            paired_gate=paired_gate,
            paired_audit=paired_audit,
            lift_baseline=lift_baseline,
            lift_strategy_summaries=lift_strategy_summaries,
            defect_summary=defect_summary,
        ),
    ]
    for row in representative_strategy_rows:
        candidate_rows.append(
            _classify_row(
                ledger_row=row,
                thresholds=thresholds,
                protocol_registry_index=protocol_registry_index,
                protocol_summary_index=protocol_summary_index,
                paired_gate=paired_gate,
                paired_audit=paired_audit,
                lift_baseline=lift_baseline,
                lift_strategy_summaries=lift_strategy_summaries,
                defect_summary=defect_summary,
            )
        )
    candidate_rows.append(
        _build_slice_support_row(
            slice_frontiers=slice_frontiers,
            shadow_price=shadow_price,
            thresholds=thresholds,
        )
    )

    route_family_rollup = _build_route_family_rollup(candidate_rows)
    flagship_core_decision = _build_flagship_core_decision(candidate_rows)
    provenance_guard = {
        "defect_metric_dependency": "auxiliary_only",
        "slice_dual_dependency": "support_only",
        "paired_family_protocol_override_applied": any(
            row["protocol_status_override_applied"] for row in candidate_rows
        ),
        "no_route_classification_depended_solely_on_defect_metric": (
            defect_summary["classification_dependency_guard"]
            == "no_route_classification_depended_solely_on_defect_metric"
        ),
    }

    return {
        "ticket": "T27-17",
        "schema_version": "ticket27-current-package-atlas.v1",
        "thresholds_ref": THRESHOLDS_ARTIFACT,
        "canonical_input_artifacts": [
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_STABILITY_SUMMARY_ARTIFACT,
            R2_GATE_DECISION_ARTIFACT,
            LIFT_INTRINSIC_BASELINE_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
            LIFT_SELECTION_SUMMARY_ARTIFACT,
            CANDIDATE_LEDGER_ARTIFACT,
            SLICE_FRONTIERS_ARTIFACT,
            SHADOW_PRICE_SUMMARY_ARTIFACT,
            PROTOCOL_REGISTRY_ARTIFACT,
            PROTOCOL_SUMMARY_ARTIFACT,
            PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
            PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
            DEFECT_SUMMARY_ARTIFACT,
            PROMOTION_DEFECT_ATLAS_ARTIFACT,
        ],
        "candidate_rows": candidate_rows,
        "route_family_rollup": route_family_rollup,
        "flagship_core_decision": flagship_core_decision,
        "provenance_guard": provenance_guard,
        "branch_decision": flagship_core_decision["recommended_project_branch_decision"],
    }


def build_ticket27_current_package_decision_note(
    *,
    atlas_payload: dict[str, Any],
) -> str:
    decision = atlas_payload["flagship_core_decision"]
    rollup = atlas_payload["route_family_rollup"]
    paired = rollup["paired_observable_enrichment_lift_route_class"]
    strategy_rollup = rollup["strategy_specific_lift_effect"]
    slice_rollup = rollup["slice_dual_support_state"]
    survivors = ", ".join(decision["surviving_route_families"]) or "none"
    return "\n".join(
        [
            "# Ticket27 Current-Package Decision",
            "",
            f"- Flagship-core survivor route families: {survivors}",
            (
                "- Paired-observable-enrichment lift family protocol-cleared: "
                f"{paired['protocol_cleared_live']}"
            ),
            (
                "- Unique best strategy supported: "
                f"{strategy_rollup['unique_best_strategy_supported']}"
            ),
            (
                "- Slice/dual evidence status: "
                f"{slice_rollup['slice_dual_support_status']}"
            ),
            (
                "- Recommended branch: "
                f"{decision['recommended_project_branch']} because "
                f"{decision['decision_basis']}"
            ),
            "",
        ]
    )


def build_ticket27_classification_design_note() -> str:
    return "\n".join(
        [
            "# Ticket27 Classification Design",
            "",
            "- Thresholds are explicit and machine-readable in `results/derived/ticket27_classification_thresholds.json`.",
            "- Protocol status is resolved from the live protocol audit artifacts, with a ticket27-only override for paired observable enrichment.",
            "- Defect is auxiliary only and cannot reject a route by itself.",
            "- Slice/dual evidence remains supporting/provisional because the frontiers were not rerun after the paired-family protocol unlock.",
            "- Strategy rows are included only where materially distinct on classification-relevant metrics, and ties never imply unique strategy superiority.",
            "",
        ]
    )


def _select_materially_distinct_strategy_rows(
    ledger_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    strategy_rows = [row for row in ledger_rows if row["candidate_kind"] == "lift_strategy"]
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in strategy_rows:
        key = (
            row["family_id"],
            row["flattening_mode"],
            row["proposal_id"],
            row["flagship_gate_supported_count"],
            row["flagship_non_fallback_supported_count"],
            row["preserved_required_control_contrast_count"],
            row["nearby_positive_supported_count"],
            row["best_common_flagship_burden"],
            row["fallback_involved"],
            row["representative_selection_effective"],
        )
        grouped.setdefault(key, []).append(row)
    representatives = [sorted(rows, key=lambda row: row["candidate_id"])[0] for rows in grouped.values()]
    return sorted(representatives, key=lambda row: row["candidate_id"])


def _classify_row(
    *,
    ledger_row: dict[str, Any],
    thresholds: dict[str, Any],
    protocol_registry_index: dict[str, dict[str, Any]],
    protocol_summary_index: dict[str, dict[str, Any]],
    paired_gate: dict[str, Any],
    paired_audit: dict[str, Any],
    lift_baseline: dict[str, Any],
    lift_strategy_summaries: dict[str, dict[str, Any]],
    defect_summary: dict[str, Any],
) -> dict[str, Any]:
    protocol_state = _resolve_protocol_state(
        ledger_row=ledger_row,
        protocol_registry_index=protocol_registry_index,
        protocol_summary_index=protocol_summary_index,
        paired_gate=paired_gate,
        paired_audit=paired_audit,
    )
    freshness_status = _resolve_freshness_status(ledger_row, protocol_state)
    flagship_core_supported = _flagship_core_supported(ledger_row, protocol_state)
    artifact_contrast_status = protocol_state["artifact_contrast_status"]
    lift_added_value_status = _resolve_lift_added_value_status(
        ledger_row=ledger_row,
        lift_baseline=lift_baseline,
    )
    strategy_specific_superiority_supported = _resolve_strategy_superiority(
        ledger_row=ledger_row,
        paired_audit=paired_audit,
    )
    decision_eligible = _decision_eligible(
        ledger_row=ledger_row,
        freshness_status=freshness_status,
        protocol_state=protocol_state,
        flagship_core_supported=flagship_core_supported,
        strategy_specific_superiority_supported=strategy_specific_superiority_supported,
    )
    classification_label, basis = _classification_label_and_basis(
        ledger_row=ledger_row,
        freshness_status=freshness_status,
        protocol_state=protocol_state,
        flagship_core_supported=flagship_core_supported,
        lift_added_value_status=lift_added_value_status,
        strategy_specific_superiority_supported=strategy_specific_superiority_supported,
        decision_eligible=decision_eligible,
    )
    defect_support_reading = (
        "auxiliary_explanatory"
        if defect_summary["signal_reading"] == "explanatory"
        else "auxiliary_weak"
    )
    return {
        "candidate_id": ledger_row["candidate_id"],
        "candidate_kind": ledger_row["candidate_kind"],
        "route_class": ledger_row["route_class"],
        "strategy_id": ledger_row["strategy_id"],
        "proposal_id": ledger_row["proposal_id"],
        "family_id": ledger_row["family_id"],
        "flattening_mode": ledger_row["flattening_mode"],
        "classification_label": classification_label,
        "freshness_status": freshness_status,
        "decision_eligible": decision_eligible,
        "canonical_protocol_status": protocol_state["canonical_protocol_status"],
        "canonical_protocol_status_source": protocol_state["canonical_protocol_status_source"],
        "protocol_status_override_applied": protocol_state["protocol_status_override_applied"],
        "flagship_core_supported": flagship_core_supported,
        "artifact_contrast_status": artifact_contrast_status,
        "lift_added_value_status": lift_added_value_status,
        "strategy_specific_superiority_supported": strategy_specific_superiority_supported,
        "defect_support_reading": defect_support_reading,
        "slice_dual_support_status": "not_applicable",
        "classification_basis": basis,
        "source_artifacts": _source_artifacts_for_row(
            ledger_row=ledger_row,
            protocol_state=protocol_state,
            lift_added_value_status=lift_added_value_status,
        ),
        "classification_metrics": {
            "flagship_gate_supported_count": ledger_row["flagship_gate_supported_count"],
            "flagship_non_fallback_supported_count": ledger_row["flagship_non_fallback_supported_count"],
            "preserved_required_control_contrast_count": ledger_row["preserved_required_control_contrast_count"],
            "nearby_positive_supported_count": ledger_row["nearby_positive_supported_count"],
            "best_common_flagship_burden": ledger_row["best_common_flagship_burden"],
            "representative_selection_effective": ledger_row["representative_selection_effective"],
            "fallback_involved": ledger_row["fallback_involved"],
        },
        "tie_set_summary": _tie_set_summary(
            ledger_row=ledger_row,
            lift_strategy_summaries=lift_strategy_summaries,
            paired_audit=paired_audit,
        ),
    }


def _resolve_protocol_state(
    *,
    ledger_row: dict[str, Any],
    protocol_registry_index: dict[str, dict[str, Any]],
    protocol_summary_index: dict[str, dict[str, Any]],
    paired_gate: dict[str, Any],
    paired_audit: dict[str, Any],
) -> dict[str, Any]:
    family_key = (ledger_row["family_id"], ledger_row["flattening_mode"])
    if family_key == PAIR_FAMILY_KEY:
        return {
            "canonical_protocol_status": "protocol_cleared_by_ticket27_adapter",
            "canonical_protocol_status_source": PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
            "protocol_status_override_applied": True,
            "artifact_contrast_status": "survives_pair_honestly",
            "supports_both_flagships_honestly": True,
            "paired_gate_result": paired_gate["gate_result"],
            "paired_resolution": paired_audit["route_class_summary"]["resolution"],
        }

    registry_row = protocol_registry_index.get(ledger_row["candidate_id"], {})
    summary_row = protocol_summary_index.get(ledger_row["candidate_id"], {})
    canonical_status = registry_row.get(
        "protocol_honesty_status",
        summary_row.get("protocol_honesty_status", "unsupported"),
    )
    return {
        "canonical_protocol_status": canonical_status,
        "canonical_protocol_status_source": (
            PROTOCOL_REGISTRY_ARTIFACT if registry_row else PROTOCOL_SUMMARY_ARTIFACT
        ),
        "protocol_status_override_applied": False,
        "artifact_contrast_status": registry_row.get(
            "artifact_contrast_status",
            summary_row.get("artifact_contrast_status", "inconclusive"),
        ),
        "supports_both_flagships_honestly": registry_row.get(
            "supports_both_flagships_honestly",
            summary_row.get("supports_both_flagships_honestly", False),
        ),
    }


def _resolve_freshness_status(
    ledger_row: dict[str, Any],
    protocol_state: dict[str, Any],
) -> str:
    if (ledger_row["family_id"], ledger_row["flattening_mode"]) == PAIR_FAMILY_KEY:
        return "fresh_with_override"
    if ledger_row["candidate_kind"] == "support_assessment":
        return "supporting_provisional"
    if protocol_state["canonical_protocol_status"] in PROTOCOL_LIVE_STATUSES:
        return "fresh"
    return "stale"


def _flagship_core_supported(
    ledger_row: dict[str, Any],
    protocol_state: dict[str, Any],
) -> bool:
    return bool(
        ledger_row["flagship_gate_supported_count"] >= 2
        or protocol_state["supports_both_flagships_honestly"]
    )


def _resolve_lift_added_value_status(
    *,
    ledger_row: dict[str, Any],
    lift_baseline: dict[str, Any],
) -> str | None:
    if ledger_row["candidate_kind"] not in {"lift_route_class", "lift_strategy"}:
        return None
    baseline = lift_baseline["best_intrinsic_envelope"]
    candidate_burden = ledger_row["best_common_flagship_burden"]
    candidate_controls = ledger_row["preserved_required_control_contrast_count"]
    candidate_nearby = ledger_row["nearby_positive_supported_count"]
    baseline_burden = baseline["coarsening_burden"]
    baseline_controls = baseline["preserved_required_control_contrast_count"]
    baseline_nearby = baseline["nearby_positive_supported_count"]
    if candidate_burden < baseline_burden:
        return "improves_over_best_intrinsic_envelope"
    if candidate_burden == baseline_burden and candidate_controls > baseline_controls:
        return "improves_over_best_intrinsic_envelope"
    if (
        candidate_burden == baseline_burden
        and candidate_controls == baseline_controls
        and candidate_nearby > baseline_nearby
    ):
        return "improves_over_best_intrinsic_envelope"
    return "ties_or_worse_than_intrinsic"


def _resolve_strategy_superiority(
    *,
    ledger_row: dict[str, Any],
    paired_audit: dict[str, Any],
) -> bool | None:
    if ledger_row["candidate_kind"] != "lift_strategy":
        return None
    if (ledger_row["family_id"], ledger_row["flattening_mode"]) == PAIR_FAMILY_KEY:
        return bool(
            paired_audit["route_class_summary"]["strategy_specific_superiority_supported"]
        )
    return False


def _decision_eligible(
    *,
    ledger_row: dict[str, Any],
    freshness_status: str,
    protocol_state: dict[str, Any],
    flagship_core_supported: bool,
    strategy_specific_superiority_supported: bool | None,
) -> bool:
    if freshness_status not in FRESHNESS_DECISION_ELIGIBLE:
        return False
    if not flagship_core_supported:
        return False
    if protocol_state["canonical_protocol_status"] not in PROTOCOL_LIVE_STATUSES:
        return False
    if protocol_state["artifact_contrast_status"] in {"artifact_collapse", "collapses_under_pair"}:
        return False
    if ledger_row["candidate_kind"] == "lift_strategy":
        return bool(strategy_specific_superiority_supported)
    return True


def _classification_label_and_basis(
    *,
    ledger_row: dict[str, Any],
    freshness_status: str,
    protocol_state: dict[str, Any],
    flagship_core_supported: bool,
    lift_added_value_status: str | None,
    strategy_specific_superiority_supported: bool | None,
    decision_eligible: bool,
) -> tuple[str, list[str]]:
    basis: list[str] = []
    if protocol_state["protocol_status_override_applied"]:
        basis.append("paired_family_protocol_override_applied")
    if freshness_status == "supporting_provisional":
        return (
            "slice_selected_dual_support_only",
            [
                "slice_dual_support_only",
                "supporting_provisional",
                "not_decision_eligible",
            ],
        )
    if protocol_state["artifact_contrast_status"] in {"artifact_collapse", "collapses_under_pair"}:
        return ("artifact", ["artifact_collapse_under_protocol_audit"])
    if (
        ledger_row["route_class"] == "intrinsic_surface_coarsening"
        and flagship_core_supported
        and decision_eligible
        and protocol_state["canonical_protocol_status"] != "protocol_required"
    ):
        basis.extend(["flagship_core_survivor", "intrinsic_surface_coarsening"])
        return ("intrinsic_promotion", basis)
    if (
        ledger_row["route_class"] == "representative_selected_lift"
        and flagship_core_supported
        and lift_added_value_status == "improves_over_best_intrinsic_envelope"
        and protocol_state["canonical_protocol_status"] == "protocol_required"
        and decision_eligible
    ):
        basis.extend(["flagship_core_survivor", "lift_added_value", "protocol_indexed_only"])
        return ("protocol_indexed_promotion", basis)
    if (
        ledger_row["route_class"] == "representative_selected_lift"
        and flagship_core_supported
        and lift_added_value_status == "improves_over_best_intrinsic_envelope"
        and protocol_state["canonical_protocol_status"] in PROTOCOL_LIVE_STATUSES
    ):
        basis.extend(["flagship_core_survivor", "lift_added_value"])
        if ledger_row["candidate_kind"] == "lift_strategy":
            basis.append("strategy_member_of_survivor_route_class")
            basis.append("no_unique_strategy_superiority")
        return ("lift_selected_promotion", basis)
    if (
        flagship_core_supported
        or ledger_row["preserved_required_control_contrast_count"] > 0
        or ledger_row["nearby_positive_supported_count"] > 0
    ):
        basis.append("below_survivor_threshold")
        return ("compression_only", basis)
    return ("no_promotion", ["no_survivor_or_support_signal"])


def _source_artifacts_for_row(
    *,
    ledger_row: dict[str, Any],
    protocol_state: dict[str, Any],
    lift_added_value_status: str | None,
) -> list[str]:
    artifacts = [CANDIDATE_LEDGER_ARTIFACT, protocol_state["canonical_protocol_status_source"]]
    if protocol_state["protocol_status_override_applied"]:
        artifacts.append(PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT)
    if lift_added_value_status is not None:
        artifacts.extend([LIFT_INTRINSIC_BASELINE_ARTIFACT, LIFT_SELECTION_SUMMARY_ARTIFACT])
    return sorted(dict.fromkeys(artifacts))


def _tie_set_summary(
    *,
    ledger_row: dict[str, Any],
    lift_strategy_summaries: dict[str, dict[str, Any]],
    paired_audit: dict[str, Any],
) -> dict[str, Any] | None:
    if ledger_row["candidate_kind"] != "lift_strategy":
        return None
    if (ledger_row["family_id"], ledger_row["flattening_mode"]) == PAIR_FAMILY_KEY:
        return {
            "all_five_strategies_tied": True,
            "member_strategy_ids": paired_audit["route_class_summary"]["member_strategy_ids"],
            "strategy_specific_superiority_supported": False,
        }
    same_family = [
        summary["strategy_id"]
        for summary in lift_strategy_summaries.values()
        if summary["best_common_family_id"] == ledger_row["family_id"]
        and summary["best_common_flattening_mode"] == ledger_row["flattening_mode"]
        and summary["best_common_flagship_proposal_id"] == ledger_row["proposal_id"]
        and summary["best_common_flagship_burden"] == ledger_row["best_common_flagship_burden"]
        and summary["preserved_required_control_contrast_count"]
        == ledger_row["preserved_required_control_contrast_count"]
    ]
    return {
        "all_five_strategies_tied": len(same_family) == 5,
        "member_strategy_ids": sorted(same_family),
        "strategy_specific_superiority_supported": False,
    }


def _build_slice_support_row(
    *,
    slice_frontiers: dict[str, Any],
    shadow_price: dict[str, Any],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    _ = thresholds
    return {
        "candidate_id": "candidate.support.slice_dual.current_package",
        "candidate_kind": "support_assessment",
        "route_class": "slice_dual_support",
        "strategy_id": None,
        "proposal_id": None,
        "family_id": None,
        "flattening_mode": None,
        "classification_label": "slice_selected_dual_support_only",
        "freshness_status": "supporting_provisional",
        "decision_eligible": False,
        "canonical_protocol_status": "not_applicable",
        "canonical_protocol_status_source": SLICE_FRONTIERS_ARTIFACT,
        "protocol_status_override_applied": False,
        "flagship_core_supported": False,
        "artifact_contrast_status": "not_applicable",
        "lift_added_value_status": None,
        "strategy_specific_superiority_supported": None,
        "defect_support_reading": "not_used",
        "slice_dual_support_status": "supporting_provisional",
        "classification_basis": [
            "slice_dual_signal_present",
            "not_rerun_after_paired_protocol_unlock",
            "support_only",
        ],
        "source_artifacts": [
            SLICE_FRONTIERS_ARTIFACT,
            SHADOW_PRICE_SUMMARY_ARTIFACT,
        ],
        "support_snapshot": {
            "slice_winner_sets_agree": shadow_price["cross_slice_winner_comparison"][
                "material_winner_sets_agree"
            ],
            "shadow_price_label": shadow_price["core_case_dual_signal"]["label"],
            "winner_pattern_by_slice": {
                frontier["slice_id"]: frontier["winner_pattern"]
                for frontier in slice_frontiers["frontier_results"]
            },
        },
    }


def _build_route_family_rollup(candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_index = {row["candidate_id"]: row for row in candidate_rows}
    intrinsic_rows = [
        row for row in candidate_rows if row["route_class"] == "intrinsic_surface_coarsening"
    ]
    declared_row = candidate_index[
        "candidate.lift_route_class.declared_completion_family.none.identity_surface"
    ]
    paired_row = candidate_index[
        "candidate.lift_route_class.paired_observable_enrichment.paired_flattening_control.identity_surface"
    ]
    strategy_rows = [row for row in candidate_rows if row["candidate_kind"] == "lift_strategy"]
    slice_row = candidate_index["candidate.support.slice_dual.current_package"]
    return {
        "intrinsic_surface_coarsening": {
            "member_candidate_ids": [row["candidate_id"] for row in intrinsic_rows],
            "survivor_classification_present": any(
                row["classification_label"] == "intrinsic_promotion" for row in intrinsic_rows
            ),
            "freshness_statuses": sorted({row["freshness_status"] for row in intrinsic_rows}),
        },
        "declared_completion_family_lift_route_class": {
            "candidate_id": declared_row["candidate_id"],
            "classification_label": declared_row["classification_label"],
            "flagship_core_supported": declared_row["flagship_core_supported"],
            "canonical_protocol_status": declared_row["canonical_protocol_status"],
        },
        "paired_observable_enrichment_lift_route_class": {
            "candidate_id": paired_row["candidate_id"],
            "classification_label": paired_row["classification_label"],
            "flagship_core_supported": paired_row["flagship_core_supported"],
            "canonical_protocol_status": paired_row["canonical_protocol_status"],
            "protocol_cleared_live": paired_row["canonical_protocol_status"]
            == "protocol_cleared_by_ticket27_adapter",
        },
        "strategy_specific_lift_effect": {
            "member_candidate_ids": [row["candidate_id"] for row in strategy_rows],
            "decision_eligible_strategy_rows": [
                row["candidate_id"] for row in strategy_rows if row["decision_eligible"]
            ],
            "unique_best_strategy_supported": any(
                bool(row["strategy_specific_superiority_supported"]) for row in strategy_rows
            ),
            "tie_sets": [
                row["tie_set_summary"]
                for row in strategy_rows
                if row.get("tie_set_summary") is not None
            ],
        },
        "slice_dual_support_state": {
            "candidate_id": slice_row["candidate_id"],
            "classification_label": slice_row["classification_label"],
            "slice_dual_support_status": slice_row["slice_dual_support_status"],
            "decision_eligible": slice_row["decision_eligible"],
        },
    }


def _build_flagship_core_decision(candidate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    family_rows = [
        row
        for row in candidate_rows
        if row["candidate_kind"] in {"intrinsic_baseline_envelope", "lift_route_class"}
    ]
    surviving_rows = [
        row
        for row in family_rows
        if row["decision_eligible"] and row["classification_label"] in SURVIVOR_LABELS
    ]
    branch_decision = (
        "CURRENT_PACKAGE_SURVIVOR_EXISTS"
        if surviving_rows
        else "CURRENT_PACKAGE_ALL_FAIL"
    )
    return {
        "surviving_route_families": [row["candidate_id"] for row in surviving_rows],
        "non_surviving_route_families": [
            row["candidate_id"]
            for row in family_rows
            if row["candidate_id"] not in {item["candidate_id"] for item in surviving_rows}
        ],
        "protocol_indexed_only_route_families": [
            row["candidate_id"]
            for row in surviving_rows
            if row["classification_label"] == "protocol_indexed_promotion"
        ],
        "artifact_like_route_families": [
            row["candidate_id"]
            for row in family_rows
            if row["classification_label"] == "artifact"
        ],
        "recommended_project_branch_decision": branch_decision,
        "recommended_project_branch": "T27-18A" if surviving_rows else "T27-18B",
        "decision_basis": (
            "at_least_one_fresh_flagship_core_route_family_meets_survivor_thresholds"
            if surviving_rows
            else "no_fresh_flagship_core_route_family_meets_survivor_thresholds"
        ),
    }
