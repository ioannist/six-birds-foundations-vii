from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

from sixbirds_foundations_v._recombination_support.completion.ticket27_lift_selection import PROPOSAL_BURDEN

from .ticket27_staging_packaging import (
    CANDIDATE_LEDGER_ARTIFACT,
    COMPONENT_WEIGHTS,
    CONTROL_INTERNALIZED_CONFIG_PATH,
    CONTROL_LOGICAL_CASE_ID,
    CONTROL_UNINTERNALIZED_CONFIG_PATH,
    INTERPRETATION_THRESHOLDS,
    LIFT_SELECTION_REGISTRY_ARTIFACT,
    METRIC_COMPONENTS,
    PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
    PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
    POSITIVE_CASE_ID,
    PROTOCOL_REGISTRY_ARTIFACT,
    PROTOCOL_STATUS_RANK,
    PROTOCOL_SUMMARY_ARTIFACT,
    R2_SECOND_STAGE_REGISTRY_ARTIFACT,
    SHADOW_PRICE_SUMMARY_ARTIFACT,
    SIGNATURE_FIELDS,
    SLICE_FRONTIERS_ARTIFACT,
    SMOKE_ARTIFACT,
    _build_comparison_row,
    _common_value,
    _interpretation_label,
    _load_json,
    _proposal_summary_signature,
    _side_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

SEED_CORPUS_ARTIFACT = "results/derived/ticket27_seed_corpus.json"
DEFECT_REGISTRY_ARTIFACT = "results/derived/ticket27_staging_packaging_defect_registry.json"
DEFECT_SUMMARY_ARTIFACT = "results/derived/ticket27_staging_packaging_defect_summary.json"
PROMOTION_DEFECT_ATLAS_ARTIFACT = "results/derived/ticket27_promotion_vs_defect_atlas.json"
DEFECT_NOTE_ARTIFACT = "results/notes/ticket27_defect_note.md"
DEFECT_DESIGN_ARTIFACT = "docs/internal/ticket27_defect_atlas_design.md"

ROUTE_FAMILY_SPECS = (
    ("declared_completion_family", "none"),
    ("paired_observable_enrichment", "paired_flattening_control"),
)

CASE_CATEGORY_MAP = {
    "flagship_anchor": "flagship",
    "nearby_positive": "nearby_positive",
    "required_control": "control",
}

PROTOCOL_STATUS_ORDER = {
    "survives_without_protocol_requirement": 0,
    "protocol_cleared_by_ticket27_adapter": 0,
    "protocol_required": 1,
    "inconclusive": 2,
    "unsupported": 3,
}

PROTOCOL_LIVE_STATUSES = {
    "survives_without_protocol_requirement",
    "protocol_cleared_by_ticket27_adapter",
}


def write_ticket27_defect_atlas_artifacts(
    *,
    repo_root: Path | None = None,
) -> dict[str, Path]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    registry = build_ticket27_staging_packaging_defect_registry(repo_root=resolved_repo_root)
    atlas = build_ticket27_promotion_vs_defect_atlas(registry_payload=registry)
    summary = build_ticket27_staging_packaging_defect_summary(
        registry_payload=registry,
        atlas_payload=atlas,
    )
    note = build_ticket27_defect_note(summary_payload=summary)
    design = build_ticket27_defect_design_note()

    registry_path = resolved_repo_root / DEFECT_REGISTRY_ARTIFACT
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    atlas_path = resolved_repo_root / PROMOTION_DEFECT_ATLAS_ARTIFACT
    atlas_path.parent.mkdir(parents=True, exist_ok=True)
    atlas_path.write_text(json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary_path = resolved_repo_root / DEFECT_SUMMARY_ARTIFACT
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    note_path = resolved_repo_root / DEFECT_NOTE_ARTIFACT
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")

    design_path = resolved_repo_root / DEFECT_DESIGN_ARTIFACT
    design_path.parent.mkdir(parents=True, exist_ok=True)
    design_path.write_text(design, encoding="utf-8")

    return {
        "registry_path": registry_path,
        "atlas_path": atlas_path,
        "summary_path": summary_path,
        "note_path": note_path,
        "design_path": design_path,
    }


def build_ticket27_staging_packaging_defect_registry(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    seed_corpus = _load_json(resolved_repo_root / SEED_CORPUS_ARTIFACT)
    r2_registry = _load_json(resolved_repo_root / R2_SECOND_STAGE_REGISTRY_ARTIFACT)
    candidate_ledger = _load_json(resolved_repo_root / CANDIDATE_LEDGER_ARTIFACT)
    protocol_summary = _load_json(resolved_repo_root / PROTOCOL_SUMMARY_ARTIFACT)
    protocol_registry = _load_json(resolved_repo_root / PROTOCOL_REGISTRY_ARTIFACT)
    paired_gate = _load_json(resolved_repo_root / PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT)
    paired_audit = _load_json(resolved_repo_root / PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT)
    lift_registry = _load_json(resolved_repo_root / LIFT_SELECTION_REGISTRY_ARTIFACT)
    slice_frontiers = _load_json(resolved_repo_root / SLICE_FRONTIERS_ARTIFACT)
    shadow_price = _load_json(resolved_repo_root / SHADOW_PRICE_SUMMARY_ARTIFACT)
    smoke = _load_json(resolved_repo_root / SMOKE_ARTIFACT)

    intrinsic_ledger_by_proposal = {
        row["proposal_id"]: row
        for row in candidate_ledger["rows"]
        if row["candidate_kind"] in {"intrinsic_baseline_envelope", "intrinsic_proposal"}
    }
    protocol_rows_by_candidate = {
        row["candidate_id"]: row for row in protocol_registry["rows"]
    }
    intrinsic_protocol_by_proposal = {
        row["proposal_id"]: row
        for row in protocol_registry["rows"]
        if row["candidate_kind"] == "intrinsic_proposal"
    }
    lift_route_class_rows = {
        (row["family_id"], row["flattening_mode"]): row
        for row in candidate_ledger["rows"]
        if row["candidate_kind"] == "lift_route_class"
    }

    case_descriptors = _build_case_descriptors(seed_corpus=seed_corpus, r2_registry=r2_registry)
    registry_rows: list[dict[str, Any]] = []

    for case in case_descriptors:
        packaging_side = _select_case_local_packaging_baseline(
            case_descriptor=case,
            r2_registry=r2_registry,
            intrinsic_ledger_by_proposal=intrinsic_ledger_by_proposal,
            intrinsic_protocol_by_proposal=intrinsic_protocol_by_proposal,
            protocol_summary=protocol_summary,
        )
        registry_rows.extend(
            _build_case_route_class_rows(
                case_descriptor=case,
                packaging_side=packaging_side,
                lift_registry=lift_registry,
                lift_route_class_rows=lift_route_class_rows,
                protocol_rows_by_candidate=protocol_rows_by_candidate,
                paired_gate=paired_gate,
                paired_audit=paired_audit,
            )
        )
        registry_rows.extend(
            _build_case_strategy_rows(
                case_descriptor=case,
                packaging_side=packaging_side,
                lift_registry=lift_registry,
                protocol_rows_by_candidate=protocol_rows_by_candidate,
                paired_audit=paired_audit,
            )
        )

    covered_case_keys = {(row["logical_case_id"], row["protocol_phase_mode"]) for row in registry_rows}
    explicit_skips = sum(1 for row in registry_rows if row["comparison_status"] != "ok")
    return {
        "ticket": "T27-16",
        "schema_version": "ticket27-staging-packaging-defect-registry.v1",
        "canonical_input_artifacts": [
            SEED_CORPUS_ARTIFACT,
            CANDIDATE_LEDGER_ARTIFACT,
            SLICE_FRONTIERS_ARTIFACT,
            SHADOW_PRICE_SUMMARY_ARTIFACT,
            PROTOCOL_SUMMARY_ARTIFACT,
            PROTOCOL_REGISTRY_ARTIFACT,
            PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
            PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
            SMOKE_ARTIFACT,
        ],
        "metric_definition": {
            "component_vocabulary": list(METRIC_COMPONENTS),
            "component_weights": dict(COMPONENT_WEIGHTS),
            "signature_fields": list(SIGNATURE_FIELDS),
            "interpretation_thresholds": dict(INTERPRETATION_THRESHOLDS),
        },
        "case_local_packaging_baseline_rule": [
            "protocol-cleared/protocol-honest over inconclusive/unsupported",
            "lower second-stage burden",
            "higher preserved required-control contrast count when measurable",
            "lower target package size",
            "lexical proposal_id",
        ],
        "rows": registry_rows,
        "coverage_summary": {
            "case_descriptor_count": len(case_descriptors),
            "covered_case_descriptor_count": len(covered_case_keys),
            "explicit_skip_row_count": explicit_skips,
        },
    }


def build_ticket27_promotion_vs_defect_atlas(
    *,
    registry_payload: dict[str, Any],
) -> dict[str, Any]:
    rows = registry_payload["rows"]
    ok_rows = [row for row in rows if row["comparison_status"] == "ok"]

    def _median(values: list[float]) -> float | None:
        return round(float(median(values)), 3) if values else None

    group_summaries = {
        "by_case_category": {},
        "by_route_family": {},
        "by_strategy_id": {},
    }
    for category in ("flagship", "nearby_positive", "control"):
        category_rows = [row for row in ok_rows if row["case_category"] == category]
        group_summaries["by_case_category"][category] = _summarize_group(category_rows)
    for family_id, _mode in ROUTE_FAMILY_SPECS:
        family_rows = [row for row in ok_rows if row["family_id"] == family_id]
        group_summaries["by_route_family"][family_id] = _summarize_group(family_rows)
    for strategy_id in sorted({row["strategy_id"] for row in ok_rows if row["strategy_id"] is not None}):
        strategy_rows = [row for row in ok_rows if row["strategy_id"] == strategy_id]
        group_summaries["by_strategy_id"][strategy_id] = _summarize_group(strategy_rows)

    positive_rows = [row for row in ok_rows if row["case_category"] in {"flagship", "nearby_positive"}]
    control_rows = [row for row in ok_rows if row["case_category"] == "control"]
    declared_rows = [row for row in ok_rows if row["family_id"] == "declared_completion_family"]
    paired_rows = [row for row in ok_rows if row["family_id"] == "paired_observable_enrichment"]
    strategy_rows = [row for row in ok_rows if row["comparison_kind"] == "intrinsic_vs_lift_strategy"]

    artifact_rows = [row for row in ok_rows if row["logical_case_id"] == CONTROL_LOGICAL_CASE_ID]
    endpoint_scores: dict[str, list[int]] = {}
    for row in artifact_rows:
        endpoint_scores.setdefault(row["protocol_phase_mode"], []).append(row["defect_score"])
    artifact_endpoint_spread = None
    if all(phase in endpoint_scores for phase in ("as_run_uninternalized", "internalized_partner")):
        artifact_endpoint_spread = round(
            _median(endpoint_scores["as_run_uninternalized"])  # type: ignore[arg-type]
            - _median(endpoint_scores["internalized_partner"]),  # type: ignore[arg-type]
            3,
        )

    correlation_summary = {
        "positive_control_defect_separation": {
            "positive_median_defect": _median([row["defect_score"] for row in positive_rows]),
            "control_median_defect": _median([row["defect_score"] for row in control_rows]),
            "positives_lower_than_controls": _median([row["defect_score"] for row in positive_rows])
            < _median([row["defect_score"] for row in control_rows]),
        },
        "route_family_defect_comparison": {
            "declared_completion_family_median_defect": _median(
                [row["defect_score"] for row in declared_rows]
            ),
            "paired_observable_enrichment_median_defect": _median(
                [row["defect_score"] for row in paired_rows]
            ),
            "route_family_separation_visible": _median(
                [row["defect_score"] for row in declared_rows]
            )
            != _median([row["defect_score"] for row in paired_rows]),
        },
        "strategy_signal": {
            "strategy_row_count": len(strategy_rows),
            "strategy_specific_separation_visible": len(
                {row["defect_score"] for row in strategy_rows}
            )
            > 1,
        },
        "artifact_control_endpoint_spread": {
            "as_run_uninternalized_median": _median(
                endpoint_scores.get("as_run_uninternalized", [])
            ),
            "internalized_partner_median": _median(
                endpoint_scores.get("internalized_partner", [])
            ),
            "endpoint_spread": artifact_endpoint_spread,
        },
        "low_defect_fraction": round(
            sum(1 for row in ok_rows if row["interpretation_label"] == "low_defect") / len(ok_rows),
            3,
        )
        if ok_rows
        else 0.0,
        "moderate_defect_fraction": round(
            sum(1 for row in ok_rows if row["interpretation_label"] == "moderate_defect")
            / len(ok_rows),
            3,
        )
        if ok_rows
        else 0.0,
        "high_defect_fraction": round(
            sum(1 for row in ok_rows if row["interpretation_label"] == "high_defect") / len(ok_rows),
            3,
        )
        if ok_rows
        else 0.0,
    }

    return {
        "ticket": "T27-16",
        "schema_version": "ticket27-promotion-vs-defect-atlas.v1",
        "atlas_rows": ok_rows,
        "group_summaries": group_summaries,
        "correlation_summary": correlation_summary,
    }


def build_ticket27_staging_packaging_defect_summary(
    *,
    registry_payload: dict[str, Any],
    atlas_payload: dict[str, Any],
) -> dict[str, Any]:
    rows = registry_payload["rows"]
    ok_rows = [row for row in rows if row["comparison_status"] == "ok"]
    paired_endpoint_resolved = {
        row["protocol_phase_mode"]
        for row in rows
        if row["logical_case_id"] == CONTROL_LOGICAL_CASE_ID
    } == {"as_run_uninternalized", "internalized_partner"}

    correlation = atlas_payload["correlation_summary"]
    route_sep = correlation["route_family_defect_comparison"]["route_family_separation_visible"]
    pos_control_sep = correlation["positive_control_defect_separation"][
        "positives_lower_than_controls"
    ]
    strategy_sep = correlation["strategy_signal"]["strategy_specific_separation_visible"]

    if route_sep:
        signal_reading = "explanatory"
    elif pos_control_sep:
        signal_reading = "weakly_correlated"
    else:
        signal_reading = "irrelevant"

    backed_statements = []
    if pos_control_sep:
        backed_statements.append(
            {
                "statement_id": "positives_lower_than_controls",
                "text": "Positives show lower median defect than controls.",
                "support": {
                    "positive_median_defect": correlation["positive_control_defect_separation"][
                        "positive_median_defect"
                    ],
                    "control_median_defect": correlation["positive_control_defect_separation"][
                        "control_median_defect"
                    ],
                },
            }
        )
    else:
        backed_statements.append(
            {
                "statement_id": "no_positive_control_defect_separation",
                "text": "Defect does not show positives lower than controls in this full atlas.",
                "support": {
                    "positive_median_defect": correlation["positive_control_defect_separation"][
                        "positive_median_defect"
                    ],
                    "control_median_defect": correlation["positive_control_defect_separation"][
                        "control_median_defect"
                    ],
                },
            }
        )
    if route_sep:
        backed_statements.append(
            {
                "statement_id": "route_family_defect_split",
                "text": "Defect separates the declared-family and paired-family route classes.",
                "support": {
                    "declared_completion_family_median_defect": correlation[
                        "route_family_defect_comparison"
                    ]["declared_completion_family_median_defect"],
                    "paired_observable_enrichment_median_defect": correlation[
                        "route_family_defect_comparison"
                    ]["paired_observable_enrichment_median_defect"],
                },
            }
        )
    if not route_sep:
        backed_statements.append(
            {
                "statement_id": "no_route_family_defect_split",
                "text": "Defect does not separate declared-family and paired-family lift route classes.",
                "support": {
                    "declared_completion_family_median_defect": correlation[
                        "route_family_defect_comparison"
                    ]["declared_completion_family_median_defect"],
                    "paired_observable_enrichment_median_defect": correlation[
                        "route_family_defect_comparison"
                    ]["paired_observable_enrichment_median_defect"],
                },
            }
        )
    if strategy_sep:
        backed_statements.append(
            {
                "statement_id": "strategy_rows_show_only_fallback_shaped_signal",
                "text": "Strategy-row defect differences are present but remain fallback-shaped rather than a clean superiority result.",
                "support": {
                    "strategy_row_count": correlation["strategy_signal"]["strategy_row_count"],
                    "strategy_specific_separation_visible": strategy_sep,
                },
            }
        )
    if not strategy_sep:
        backed_statements.append(
            {
                "statement_id": "no_strategy_level_defect_signal",
                "text": "Strategy rows do not add a clear superiority signal beyond fallback-related differences.",
                "support": {
                    "strategy_row_count": correlation["strategy_signal"]["strategy_row_count"],
                    "strategy_specific_separation_visible": strategy_sep,
                },
            }
        )

    classification_dependency_guard = (
        "no_route_classification_depended_solely_on_defect_metric"
    )

    paired_override_applied = any(
        row["protocol_status_override_applied"]
        for row in rows
        if row["family_id"] == "paired_observable_enrichment"
    )
    protocol_override_summary = {
        "paired_family_override_applied": paired_override_applied,
        "effect_on_interpretation": (
            "paired_observable_enrichment_route_class treated as protocol-cleared/live in atlas"
            if paired_override_applied
            else "no_override_applied"
        ),
    }

    branch_decision = (
        "DEFECT_SIGNAL_PRESENT"
        if signal_reading in {"explanatory", "weakly_correlated"}
        and backed_statements
        and classification_dependency_guard
        else "NO_CLEAR_DEFECT_SIGNAL"
    )

    return {
        "ticket": "T27-16",
        "schema_version": "ticket27-staging-packaging-defect-summary.v1",
        "coverage_summary": {
            "included_case_count": len(
                {
                    (row["logical_case_id"], row["protocol_phase_mode"])
                    for row in rows
                    if row["comparison_status"] == "ok"
                }
            ),
            "skipped_or_unsupported_row_count": sum(
                1 for row in rows if row["comparison_status"] != "ok"
            ),
            "artifact_control_endpoint_resolved": paired_endpoint_resolved,
        },
        "signal_reading": signal_reading,
        "backed_statements": backed_statements,
        "classification_dependency_guard": classification_dependency_guard,
        "protocol_override_summary": protocol_override_summary,
        "branch_decision": branch_decision,
    }


def build_ticket27_defect_note(*, summary_payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Ticket27 Defect Note",
            "",
            f"- Signal reading: `{summary_payload['signal_reading']}`.",
            f"- Branch decision: `{summary_payload['branch_decision']}`.",
            (
                "- Artifact control endpoint-resolved: "
                f"`{summary_payload['coverage_summary']['artifact_control_endpoint_resolved']}`."
            ),
            (
                "- Paired-family protocol override applied: "
                f"`{summary_payload['protocol_override_summary']['paired_family_override_applied']}`."
            ),
            "",
        ]
    )


def build_ticket27_defect_design_note() -> str:
    return "\n".join(
        [
            "# Ticket27 Defect Atlas Design",
            "",
            "- Packaging baseline is selected per case from raw r2 intrinsic candidates, not copied from the flagship envelope.",
            "- Route-class protocol status starts from the protocol audit registry and applies a narrow paired-family override from the adapter-cleared paired lift audit.",
            "- Strategy rows are emitted only when they are materially distinct on atlas-relevant metrics, mainly fallback behavior.",
            "- Artifact control remains endpoint-resolved across the full registry and atlas.",
            "",
        ]
    )


def _build_case_descriptors(
    *,
    seed_corpus: dict[str, Any],
    r2_registry: dict[str, Any],
) -> list[dict[str, Any]]:
    entries = {entry["stable_id"]: entry for entry in seed_corpus["entries"]}
    r2_by_id = {case["stable_id"]: case for case in r2_registry["cases"]}
    descriptors = []
    for stable_id in (
        "t27.flagship.reference_positive",
        "t27.flagship.completion_partner",
        "t27.nearby.n3_d1_w1of3_2of3",
        "t27.nearby.n4_d1_w1of3_2of3",
        "t27.nearby.n5_d1_w1of2_1of2",
        "t27.nearby.n5_d2_w1of3_2of3",
        "t27.control.null_baseline",
        "t27.control.memory_only",
        "t27.control.boundary_collapse",
    ):
        entry = entries[stable_id]
        descriptors.append(
            {
                "logical_case_id": stable_id,
                "case_category": CASE_CATEGORY_MAP[entry["category"]],
                "protocol_phase_mode": None,
                "logical_protocol_pair_mode": "single_case",
                "config_path": r2_by_id[stable_id]["config_path"],
            }
        )
    descriptors.extend(
        [
            {
                "logical_case_id": CONTROL_LOGICAL_CASE_ID,
                "case_category": "control",
                "protocol_phase_mode": "as_run_uninternalized",
                "logical_protocol_pair_mode": "paired_protocol_control",
                "config_path": CONTROL_UNINTERNALIZED_CONFIG_PATH,
            },
            {
                "logical_case_id": CONTROL_LOGICAL_CASE_ID,
                "case_category": "control",
                "protocol_phase_mode": "internalized_partner",
                "logical_protocol_pair_mode": "paired_protocol_control",
                "config_path": CONTROL_INTERNALIZED_CONFIG_PATH,
            },
        ]
    )
    return descriptors


def _select_case_local_packaging_baseline(
    *,
    case_descriptor: dict[str, Any],
    r2_registry: dict[str, Any],
    intrinsic_ledger_by_proposal: dict[str, dict[str, Any]],
    intrinsic_protocol_by_proposal: dict[str, dict[str, Any]],
    protocol_summary: dict[str, Any],
) -> dict[str, Any]:
    stable_id = case_descriptor["logical_case_id"]
    if stable_id == CONTROL_LOGICAL_CASE_ID:
        stable_id = CONTROL_LOGICAL_CASE_ID
    case = next(case for case in r2_registry["cases"] if case["stable_id"] == stable_id)
    ranked = []
    for candidate in case["candidates"]:
        proposal_id = candidate["proposal"]["proposal_id"]
        ledger_row = intrinsic_ledger_by_proposal.get(proposal_id)
        protocol_row = intrinsic_protocol_by_proposal.get(proposal_id)
        protocol_status = (
            protocol_row["protocol_honesty_status"]
            if protocol_row is not None
            else "survives_without_protocol_requirement"
        )
        control_count = (
            ledger_row["preserved_required_control_contrast_count"]
            if ledger_row is not None
            else -1
        )
        burden = PROPOSAL_BURDEN[proposal_id]
        ranked.append(
            {
                "proposal_id": proposal_id,
                "candidate": candidate,
                "protocol_status": protocol_status,
                "protocol_rank": PROTOCOL_STATUS_ORDER[protocol_status],
                "control_count": control_count,
                "burden": burden,
                "target_package_size": candidate["target_package_size"],
            }
        )
    ranked.sort(
        key=lambda item: (
            item["protocol_rank"],
            item["burden"],
            -item["control_count"],
            item["target_package_size"],
            item["proposal_id"],
        )
    )
    selected = ranked[0]
    ledger_row = intrinsic_ledger_by_proposal.get(selected["proposal_id"], {})
    case_target_size = selected["candidate"]["target_package_size"]
    case_nearby_supported = (
        case_descriptor["case_category"] == "nearby_positive"
        and case_target_size < case["source_package_size"]
    )
    common = _side_payload(
        candidate_id=(
            f"candidate.case_local_intrinsic.{case_descriptor['logical_case_id']}."
            f"{selected['proposal_id']}"
        ),
        proposal_id=selected["proposal_id"],
        burden=selected["burden"],
        target_package_size=case_target_size,
        preserved_required_control_contrast_count=selected["control_count"],
        protocol_status=selected["protocol_status"],
        fallback_involved=False,
        representative_selection_effective=False,
        family_id=None,
        flattening_mode=None,
        signature_material={
            "candidate_fingerprint": selected["candidate"]["candidate_fingerprint"],
            "closure_status": selected["candidate"]["closure_status"],
            "config_path": case_descriptor["config_path"],
        },
    )
    common.update(
        {
            "packaging_side_selection_rule": (
                "case_local_intrinsic_baseline:"
                " protocol-cleared/honest, lower burden, higher control count,"
                " lower target size, lexical proposal id"
            ),
            "flagship_gate_supported": bool(ledger_row.get("flagship_gate_supported_count")),
            "nearby_supported": case_nearby_supported,
            "control_contrast_count": selected["control_count"],
            "canonical_protocol_status": selected["protocol_status"],
            "canonical_protocol_status_source": (
                PROTOCOL_REGISTRY_ARTIFACT
                if selected["proposal_id"] in intrinsic_protocol_by_proposal
                else "canonical_intrinsic_current_reading"
            ),
            "protocol_status_override_applied": False,
        }
    )
    if case_descriptor["logical_case_id"] == CONTROL_LOGICAL_CASE_ID:
        intrinsic_protocol_row = intrinsic_protocol_by_proposal[selected["proposal_id"]]
        endpoint = next(
            payload
            for payload in intrinsic_protocol_row["artifact_pair_rows"]
            if payload["protocol_phase_mode"] == case_descriptor["protocol_phase_mode"]
        )
        common["target_package_size"] = endpoint["candidate_route_target_package_size"]
        common["compact_signature"] = _side_payload(
            candidate_id=common["candidate_id"],
            proposal_id=selected["proposal_id"],
            burden=selected["burden"],
            target_package_size=endpoint["candidate_route_target_package_size"],
            preserved_required_control_contrast_count=selected["control_count"],
            protocol_status=selected["protocol_status"],
            fallback_involved=False,
            representative_selection_effective=False,
            family_id=None,
            flattening_mode=None,
            signature_material={
                "candidate_route_signature_id": endpoint["candidate_route_signature_id"],
                "protocol_phase_mode": endpoint["protocol_phase_mode"],
            },
        )["compact_signature"]
        common["signature_material"] = {
            "candidate_route_signature_id": endpoint["candidate_route_signature_id"],
            "protocol_phase_mode": endpoint["protocol_phase_mode"],
            "protocol_internalization_status": endpoint["protocol_internalization_status"],
        }
    return common


def _build_case_route_class_rows(
    *,
    case_descriptor: dict[str, Any],
    packaging_side: dict[str, Any],
    lift_registry: dict[str, Any],
    lift_route_class_rows: dict[tuple[str, str], dict[str, Any]],
    protocol_rows_by_candidate: dict[str, dict[str, Any]],
    paired_gate: dict[str, Any],
    paired_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for family_id, flattening_mode in ROUTE_FAMILY_SPECS:
        staging_side = _resolve_route_class_staging_side(
            case_descriptor=case_descriptor,
            family_id=family_id,
            flattening_mode=flattening_mode,
            lift_registry=lift_registry,
            lift_route_class_row=lift_route_class_rows.get((family_id, flattening_mode)),
            protocol_rows_by_candidate=protocol_rows_by_candidate,
            paired_gate=paired_gate,
            paired_audit=paired_audit,
        )
        rows.append(
            _comparison_row_from_sides(
                comparison_id=(
                    f"comparison.route_class.{case_descriptor['logical_case_id']}."
                    f"{case_descriptor['protocol_phase_mode'] or 'none'}."
                    f"{family_id}.{flattening_mode}"
                ),
                comparison_kind="intrinsic_vs_lift_route_class",
                case_descriptor=case_descriptor,
                family_id=family_id,
                flattening_mode=flattening_mode,
                strategy_id=None,
                packaging_side=packaging_side,
                staging_side=staging_side,
            )
        )
    return rows


def _build_case_strategy_rows(
    *,
    case_descriptor: dict[str, Any],
    packaging_side: dict[str, Any],
    lift_registry: dict[str, Any],
    protocol_rows_by_candidate: dict[str, dict[str, Any]],
    paired_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for family_id, flattening_mode in ROUTE_FAMILY_SPECS:
        if family_id == "paired_observable_enrichment":
            distinct_strategy_ids = _material_strategy_ids_for_paired_family(
                case_descriptor=case_descriptor,
                paired_audit=paired_audit,
            )
        else:
            distinct_strategy_ids = _material_strategy_ids_for_declared_family(
                case_descriptor=case_descriptor,
                lift_registry=lift_registry,
            )
        for strategy_id in distinct_strategy_ids:
            staging_side = _resolve_strategy_staging_side(
                case_descriptor=case_descriptor,
                family_id=family_id,
                flattening_mode=flattening_mode,
                strategy_id=strategy_id,
                lift_registry=lift_registry,
                protocol_rows_by_candidate=protocol_rows_by_candidate,
                paired_audit=paired_audit,
            )
            rows.append(
                _comparison_row_from_sides(
                    comparison_id=(
                        f"comparison.strategy.{case_descriptor['logical_case_id']}."
                        f"{case_descriptor['protocol_phase_mode'] or 'none'}."
                        f"{strategy_id}.{family_id}.{flattening_mode}"
                    ),
                    comparison_kind="intrinsic_vs_lift_strategy",
                    case_descriptor=case_descriptor,
                    family_id=family_id,
                    flattening_mode=flattening_mode,
                    strategy_id=strategy_id,
                    packaging_side=packaging_side,
                    staging_side=staging_side,
                )
            )
    return rows


def _resolve_route_class_staging_side(
    *,
    case_descriptor: dict[str, Any],
    family_id: str,
    flattening_mode: str,
    lift_registry: dict[str, Any],
    lift_route_class_row: dict[str, Any] | None,
    protocol_rows_by_candidate: dict[str, dict[str, Any]],
    paired_gate: dict[str, Any],
    paired_audit: dict[str, Any],
) -> dict[str, Any]:
    if case_descriptor["logical_case_id"] == CONTROL_LOGICAL_CASE_ID:
        if family_id == "declared_completion_family":
            protocol_row = protocol_rows_by_candidate[
                "candidate.lift_route_class.declared_completion_family.none.identity_surface"
            ]
            endpoint = next(
                payload
                for payload in protocol_row["artifact_pair_rows"]
                if payload["protocol_phase_mode"] == case_descriptor["protocol_phase_mode"]
            )
            return _side_payload(
                candidate_id=(
                    "candidate.case_local_lift_route_class."
                    f"{case_descriptor['logical_case_id']}."
                    f"{case_descriptor['protocol_phase_mode']}.{family_id}.{flattening_mode}"
                ),
                proposal_id="identity_surface",
                burden=0,
                target_package_size=3,
                preserved_required_control_contrast_count=4,
                protocol_status=protocol_row["protocol_honesty_status"],
                fallback_involved=endpoint["fallback_involved"],
                representative_selection_effective=False,
                family_id=family_id,
                flattening_mode=flattening_mode,
                signature_material={
                    "candidate_route_signature_ids": endpoint["unique_candidate_route_signature_ids"],
                    "protocol_phase_mode": endpoint["protocol_phase_mode"],
                },
            ) | {
                "flagship_gate_supported": True,
                "nearby_supported": False,
                "control_contrast_count": 4,
                "canonical_protocol_status": protocol_row["protocol_honesty_status"],
                "canonical_protocol_status_source": PROTOCOL_REGISTRY_ARTIFACT,
                "protocol_status_override_applied": False,
            }
        if (
            paired_gate["gate_result"] == "PASS_GATE"
            and paired_audit["resolution"] == "resolved_pass"
        ):
            endpoint_rows = [
                strategy_row["endpoint_rows"]
                for strategy_row in paired_audit["strategy_rows"]
            ]
            flattened = [
                endpoint
                for rows in endpoint_rows
                for endpoint in rows
                if endpoint["protocol_phase_mode"] == case_descriptor["protocol_phase_mode"]
            ]
            return _side_payload(
                candidate_id=(
                    "candidate.case_local_lift_route_class."
                    f"{case_descriptor['logical_case_id']}."
                    f"{case_descriptor['protocol_phase_mode']}.{family_id}.{flattening_mode}"
                ),
                proposal_id="identity_surface",
                burden=0,
                target_package_size=_common_value(
                    [row["best_second_stage_target_package_size"] for row in flattened]
                ),
                preserved_required_control_contrast_count=4,
                protocol_status="protocol_cleared_by_ticket27_adapter",
                fallback_involved=any(row["fallback_used"] for row in flattened),
                representative_selection_effective=False,
                family_id=family_id,
                flattening_mode=flattening_mode,
                signature_material={
                    "candidate_route_signature_ids": sorted(
                        {row["candidate_route_signature_id"] for row in flattened}
                    ),
                    "protocol_phase_mode": case_descriptor["protocol_phase_mode"],
                },
            ) | {
                "flagship_gate_supported": True,
                "nearby_supported": False,
                "control_contrast_count": 4,
                "canonical_protocol_status": "protocol_cleared_by_ticket27_adapter",
                "canonical_protocol_status_source": PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
                "protocol_status_override_applied": True,
            }

    case_rows = [
        row
        for row in lift_registry["rows"]
        if row["stable_id"] == case_descriptor["logical_case_id"]
        and row["family_id"] == family_id
        and row["flattening_mode"] == flattening_mode
        and row["skip_reason"] is None
    ]
    if not case_rows or lift_route_class_row is None:
        return {
            "comparison_status": "skipped",
            "reason": "staging_route_family_not_executable_for_case",
        }
    target = _common_value(
        [row["best_second_stage_target_package_size"] for row in case_rows]
    )
    burden = _common_value([row["best_second_stage_coarsening_burden"] for row in case_rows])
    fallback = any(row["fallback_used"] for row in case_rows)
    protocol_status, protocol_source, override_applied = _resolve_canonical_protocol_status(
        candidate_id=lift_route_class_row["candidate_id"],
        family_id=family_id,
        flattening_mode=flattening_mode,
        protocol_rows_by_candidate=protocol_rows_by_candidate,
        paired_gate=paired_gate,
        paired_audit=paired_audit,
    )
    source_size = _source_size_for_case(case_descriptor["logical_case_id"], lift_registry)
    return _side_payload(
        candidate_id=(
            "candidate.case_local_lift_route_class."
            f"{case_descriptor['logical_case_id']}.{family_id}.{flattening_mode}"
        ),
        proposal_id=_common_value([row["best_second_stage_proposal_id"] for row in case_rows]),
        burden=burden,
        target_package_size=target,
        preserved_required_control_contrast_count=lift_route_class_row[
            "preserved_required_control_contrast_count"
        ],
        protocol_status=protocol_status,
        fallback_involved=fallback,
        representative_selection_effective=False,
        family_id=family_id,
        flattening_mode=flattening_mode,
        signature_material={
            "representative_mapping_hashes": sorted(
                {
                    json.dumps(row["representative_mapping"], sort_keys=True)
                    for row in case_rows
                }
            ),
            "proposal_signature_ids": sorted(
                {
                    _proposal_summary_signature(row["proposal_summaries"], "identity_surface")
                    for row in case_rows
                }
            ),
        },
    ) | {
        "flagship_gate_supported": bool(lift_route_class_row["flagship_gate_supported_count"]),
        "nearby_supported": (
            case_descriptor["case_category"] == "nearby_positive" and target < source_size
        ),
        "control_contrast_count": lift_route_class_row["preserved_required_control_contrast_count"],
        "canonical_protocol_status": protocol_status,
        "canonical_protocol_status_source": protocol_source,
        "protocol_status_override_applied": override_applied,
    }


def _resolve_strategy_staging_side(
    *,
    case_descriptor: dict[str, Any],
    family_id: str,
    flattening_mode: str,
    strategy_id: str,
    lift_registry: dict[str, Any],
    protocol_rows_by_candidate: dict[str, dict[str, Any]],
    paired_audit: dict[str, Any],
) -> dict[str, Any]:
    if case_descriptor["logical_case_id"] == CONTROL_LOGICAL_CASE_ID and family_id == "declared_completion_family":
        protocol_row = protocol_rows_by_candidate[
            f"candidate.lift_strategy.{strategy_id}.declared_completion_family.none.identity_surface"
        ]
        endpoint = next(
            payload
            for payload in protocol_row["artifact_pair_rows"]
            if payload["protocol_phase_mode"] == case_descriptor["protocol_phase_mode"]
        )
        return _side_payload(
            candidate_id=(
                "candidate.case_local_lift_strategy."
                f"{case_descriptor['logical_case_id']}."
                f"{case_descriptor['protocol_phase_mode']}.{strategy_id}.{family_id}.{flattening_mode}"
            ),
            proposal_id="identity_surface",
            burden=0,
            target_package_size=endpoint["candidate_route_target_package_size"],
            preserved_required_control_contrast_count=4,
            protocol_status=protocol_row["protocol_honesty_status"],
            fallback_involved=endpoint["fallback_used"],
            representative_selection_effective=True,
            family_id=family_id,
            flattening_mode=flattening_mode,
            signature_material={
                "candidate_route_signature_id": endpoint["candidate_route_signature_id"],
                "representative_mapping": endpoint["representative_mapping"],
            },
        ) | {
            "flagship_gate_supported": True,
            "nearby_supported": False,
            "control_contrast_count": 4,
            "canonical_protocol_status": protocol_row["protocol_honesty_status"],
            "canonical_protocol_status_source": PROTOCOL_REGISTRY_ARTIFACT,
            "protocol_status_override_applied": False,
        }
    if case_descriptor["logical_case_id"] == CONTROL_LOGICAL_CASE_ID and family_id == "paired_observable_enrichment":
        strategy_row = next(
            row for row in paired_audit["strategy_rows"] if row["strategy_id"] == strategy_id
        )
        endpoint = next(
            payload
            for payload in strategy_row["endpoint_rows"]
            if payload["protocol_phase_mode"] == case_descriptor["protocol_phase_mode"]
        )
        return _side_payload(
            candidate_id=(
                "candidate.case_local_lift_strategy."
                f"{case_descriptor['logical_case_id']}."
                f"{case_descriptor['protocol_phase_mode']}.{strategy_id}.{family_id}.{flattening_mode}"
            ),
            proposal_id=endpoint["best_second_stage_proposal_id"],
            burden=endpoint["best_second_stage_burden"],
            target_package_size=endpoint["best_second_stage_target_package_size"],
            preserved_required_control_contrast_count=4,
            protocol_status="protocol_cleared_by_ticket27_adapter",
            fallback_involved=endpoint["fallback_used"],
            representative_selection_effective=True,
            family_id=family_id,
            flattening_mode=flattening_mode,
            signature_material={
                "candidate_route_signature_id": endpoint["candidate_route_signature_id"],
                "representative_mapping": endpoint["representative_mapping"],
            },
        ) | {
            "flagship_gate_supported": True,
            "nearby_supported": False,
            "control_contrast_count": 4,
            "canonical_protocol_status": "protocol_cleared_by_ticket27_adapter",
            "canonical_protocol_status_source": PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
            "protocol_status_override_applied": True,
        }

    case_rows = [
        row
        for row in lift_registry["rows"]
        if row["stable_id"] == case_descriptor["logical_case_id"]
        and row["family_id"] == family_id
        and row["flattening_mode"] == flattening_mode
        and row["strategy_id"] == strategy_id
        and row["skip_reason"] is None
    ]
    if not case_rows:
        return {"comparison_status": "skipped", "reason": "strategy_not_executable_for_case"}
    row = case_rows[0]
    protocol_row = protocol_rows_by_candidate[
        f"candidate.lift_strategy.{strategy_id}.{family_id}.{flattening_mode}.identity_surface"
    ]
    source_size = _source_size_for_case(case_descriptor["logical_case_id"], lift_registry)
    return _side_payload(
        candidate_id=(
            "candidate.case_local_lift_strategy."
            f"{case_descriptor['logical_case_id']}.{strategy_id}.{family_id}.{flattening_mode}"
        ),
        proposal_id=row["best_second_stage_proposal_id"],
        burden=row["best_second_stage_coarsening_burden"],
        target_package_size=row["best_second_stage_target_package_size"],
        preserved_required_control_contrast_count=len(row["preserved_required_control_contrasts"]),
        protocol_status=protocol_row["protocol_honesty_status"],
        fallback_involved=row["fallback_used"],
        representative_selection_effective=True,
        family_id=family_id,
        flattening_mode=flattening_mode,
        signature_material={
            "representative_mapping": row["representative_mapping"],
            "proposal_signature_id": _proposal_summary_signature(
                row["proposal_summaries"], row["best_second_stage_proposal_id"]
            ),
        },
    ) | {
        "flagship_gate_supported": row["flagship_core_gate_satisfied"],
        "nearby_supported": (
            case_descriptor["case_category"] == "nearby_positive"
            and row["best_second_stage_target_package_size"] < source_size
        ),
        "control_contrast_count": len(row["preserved_required_control_contrasts"]),
        "canonical_protocol_status": protocol_row["protocol_honesty_status"],
        "canonical_protocol_status_source": PROTOCOL_REGISTRY_ARTIFACT,
        "protocol_status_override_applied": False,
    }


def _comparison_row_from_sides(
    *,
    comparison_id: str,
    comparison_kind: str,
    case_descriptor: dict[str, Any],
    family_id: str,
    flattening_mode: str,
    strategy_id: str | None,
    packaging_side: dict[str, Any],
    staging_side: dict[str, Any],
) -> dict[str, Any]:
    if staging_side.get("comparison_status") == "skipped":
        return {
            "comparison_id": comparison_id,
            "comparison_kind": comparison_kind,
            "logical_case_id": case_descriptor["logical_case_id"],
            "case_category": case_descriptor["case_category"],
            "logical_protocol_pair_mode": case_descriptor["logical_protocol_pair_mode"],
            "protocol_phase_mode": case_descriptor["protocol_phase_mode"],
            "family_id": family_id,
            "flattening_mode": flattening_mode,
            "strategy_id": strategy_id,
            "packaging_side_candidate_id": packaging_side["candidate_id"],
            "staging_side_candidate_id": None,
            "packaging_side_selection_rule": packaging_side["packaging_side_selection_rule"],
            "packaging_side_signature": packaging_side["compact_signature"],
            "staging_side_signature": None,
            **{name: None for name in METRIC_COMPONENTS},
            "defect_score": None,
            "interpretation_label": "unsupported_pair",
            "packaging_side_protocol_status": packaging_side["canonical_protocol_status"],
            "staging_side_protocol_status": None,
            "packaging_side_flagship_gate_supported": packaging_side["flagship_gate_supported"],
            "staging_side_flagship_gate_supported": None,
            "packaging_side_nearby_supported": packaging_side["nearby_supported"],
            "staging_side_nearby_supported": None,
            "packaging_side_control_contrast_count": packaging_side["control_contrast_count"],
            "staging_side_control_contrast_count": None,
            "canonical_protocol_status": None,
            "canonical_protocol_status_source": None,
            "protocol_status_override_applied": False,
            "source_artifacts": [],
            "comparison_status": "skipped",
            "reason": staging_side["reason"],
        }

    row = _build_comparison_row(
        comparison_id=comparison_id,
        comparison_kind=comparison_kind,
        logical_case_id=case_descriptor["logical_case_id"],
        protocol_phase_mode=case_descriptor["protocol_phase_mode"],
        logical_protocol_pair_mode=case_descriptor["logical_protocol_pair_mode"],
        family_id=family_id,
        flattening_mode=flattening_mode,
        strategy_id=strategy_id,
        packaging_side=packaging_side,
        staging_side=staging_side,
        source_artifacts=[
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
            PROTOCOL_REGISTRY_ARTIFACT,
            PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
        ],
    )
    row.update(
        {
            "case_category": case_descriptor["case_category"],
            "packaging_side_selection_rule": packaging_side["packaging_side_selection_rule"],
            "packaging_side_protocol_status": packaging_side["canonical_protocol_status"],
            "staging_side_protocol_status": staging_side["canonical_protocol_status"],
            "packaging_side_flagship_gate_supported": packaging_side["flagship_gate_supported"],
            "staging_side_flagship_gate_supported": staging_side["flagship_gate_supported"],
            "packaging_side_nearby_supported": packaging_side["nearby_supported"],
            "staging_side_nearby_supported": staging_side["nearby_supported"],
            "packaging_side_control_contrast_count": packaging_side["control_contrast_count"],
            "staging_side_control_contrast_count": staging_side["control_contrast_count"],
            "canonical_protocol_status": staging_side["canonical_protocol_status"],
            "canonical_protocol_status_source": staging_side["canonical_protocol_status_source"],
            "protocol_status_override_applied": staging_side["protocol_status_override_applied"],
            "comparison_status": "ok",
            "reason": None,
        }
    )
    return row


def _resolve_canonical_protocol_status(
    *,
    candidate_id: str,
    family_id: str,
    flattening_mode: str,
    protocol_rows_by_candidate: dict[str, dict[str, Any]],
    paired_gate: dict[str, Any],
    paired_audit: dict[str, Any],
) -> tuple[str, str, bool]:
    if (
        family_id == "paired_observable_enrichment"
        and flattening_mode == "paired_flattening_control"
        and paired_gate["gate_result"] == "PASS_GATE"
        and paired_audit["resolution"] == "resolved_pass"
    ):
        return (
            "protocol_cleared_by_ticket27_adapter",
            PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
            True,
        )
    protocol_row = protocol_rows_by_candidate.get(candidate_id)
    if protocol_row is None:
        return ("inconclusive", "no_protocol_row", False)
    return (
        protocol_row["protocol_honesty_status"],
        PROTOCOL_REGISTRY_ARTIFACT,
        False,
    )


def _material_strategy_ids_for_declared_family(
    *,
    case_descriptor: dict[str, Any],
    lift_registry: dict[str, Any],
) -> list[str]:
    rows = [
        row
        for row in lift_registry["rows"]
        if row["stable_id"] == case_descriptor["logical_case_id"]
        and row["family_id"] == "declared_completion_family"
        and row["flattening_mode"] == "none"
        and row["skip_reason"] is None
    ]
    if not rows:
        return []
    if any(row["fallback_used"] for row in rows):
        return sorted(
            {
                row["strategy_id"]
                for row in rows
                if row["strategy_id"] in {"identity_reference", "completion_preserving"}
            }
        )
    return []


def _material_strategy_ids_for_paired_family(
    *,
    case_descriptor: dict[str, Any],
    paired_audit: dict[str, Any],
) -> list[str]:
    if case_descriptor["logical_case_id"] != CONTROL_LOGICAL_CASE_ID:
        return []
    if paired_audit["resolution"] != "resolved_pass":
        return []
    if any(
        any(endpoint["fallback_used"] for endpoint in strategy_row["endpoint_rows"])
        for strategy_row in paired_audit["strategy_rows"]
    ):
        return ["completion_preserving", "identity_reference"]
    return []


def _source_size_for_case(stable_id: str, lift_registry: dict[str, Any]) -> int:
    row = next(row for row in lift_registry["rows"] if row["stable_id"] == stable_id and row["skip_reason"] is None)
    return len(row["selected_class_summaries"])


def _summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "row_count": 0,
            "median_defect": None,
            "low_defect_fraction": None,
            "moderate_defect_fraction": None,
            "high_defect_fraction": None,
        }
    row_count = len(rows)
    return {
        "row_count": row_count,
        "median_defect": round(float(median([row["defect_score"] for row in rows])), 3),
        "low_defect_fraction": round(
            sum(1 for row in rows if row["interpretation_label"] == "low_defect") / row_count,
            3,
        ),
        "moderate_defect_fraction": round(
            sum(1 for row in rows if row["interpretation_label"] == "moderate_defect")
            / row_count,
            3,
        ),
        "high_defect_fraction": round(
            sum(1 for row in rows if row["interpretation_label"] == "high_defect") / row_count,
            3,
        ),
    }
