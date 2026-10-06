from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

CANDIDATE_LEDGER_ARTIFACT = "results/derived/ticket27_candidate_observation_ledger.json"
SLICE_FRONTIERS_ARTIFACT = "results/derived/ticket27_slice_frontiers.json"
SHADOW_PRICE_SUMMARY_ARTIFACT = "results/derived/ticket27_shadow_price_summary.json"
PROTOCOL_SUMMARY_ARTIFACT = "results/derived/ticket27_protocol_internalization_summary.json"
PROTOCOL_REGISTRY_ARTIFACT = "results/derived/ticket27_protocol_internalization_registry.json"
PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT = "results/derived/ticket27_paired_lift_protocol_gate.json"
PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT = "results/derived/ticket27_paired_lift_protocol_audit.json"
R2_SECOND_STAGE_REGISTRY_ARTIFACT = "results/derived/ticket27r2_second_stage_registry.json"
LIFT_SELECTION_REGISTRY_ARTIFACT = "results/derived/ticket27_lift_selection_registry.json"

SPEC_ARTIFACT = "docs/internal/ticket27_staging_packaging_spec.md"
SMOKE_ARTIFACT = "results/derived/ticket27_staging_packaging_smoke.json"
SMOKE_NOTE_ARTIFACT = "results/notes/ticket27_staging_packaging_smoke_note.md"

POSITIVE_CASE_ID = "t27.flagship.completion_partner"
POSITIVE_CONFIG_PATH = (
    "configs/recombination/benchmarks/interference/flattening_control/completion_partner.json"
)
CONTROL_LOGICAL_CASE_ID = "t27.control.artifact"
CONTROL_UNINTERNALIZED_CONFIG_PATH = (
    "configs/recombination/benchmarks/interference/protocol_artifact/uninternalized.json"
)
CONTROL_INTERNALIZED_CONFIG_PATH = (
    "configs/recombination/benchmarks/interference/protocol_artifact/internalized.json"
)

INTRINSIC_BASELINE_CANDIDATE_ID = "candidate.intrinsic_baseline.best_envelope"
DECLARED_LIFT_CANDIDATE_ID = (
    "candidate.lift_route_class.declared_completion_family.none.identity_surface"
)
PAIRED_LIFT_CANDIDATE_ID = (
    "candidate.lift_route_class.paired_observable_enrichment."
    "paired_flattening_control.identity_surface"
)

METRIC_COMPONENTS = [
    "proposal_mismatch",
    "burden_delta_abs",
    "target_package_size_delta_abs",
    "control_contrast_delta",
    "protocol_status_delta",
    "fallback_penalty",
    "representative_selection_delta",
    "signature_distance",
]

COMPONENT_WEIGHTS = {
    "proposal_mismatch": 2,
    "burden_delta_abs": 1,
    "target_package_size_delta_abs": 1,
    "control_contrast_delta": 1,
    "protocol_status_delta": 2,
    "fallback_penalty": 2,
    "representative_selection_delta": 1,
    "signature_distance": 1,
}

SIGNATURE_FIELDS = [
    "proposal_id",
    "burden",
    "target_package_size",
    "protocol_status_rank",
    "fallback_involved",
    "representative_selection_effective",
    "family_id",
    "flattening_mode",
]

INTERPRETATION_THRESHOLDS = {
    "low_defect_max": 5,
    "moderate_defect_max": 9,
}

PROTOCOL_STATUS_RANK = {
    "survives_without_protocol_requirement": 0,
    "protocol_cleared_by_ticket27_adapter": 0,
    "protocol_required": 1,
    "inconclusive": 2,
    "artifact_collapse": 3,
    "survives_pair_honestly": 0,
    "requires_internalized_partner": 1,
    "collapses_under_pair": 3,
}


def write_ticket27_staging_packaging_artifacts(
    *,
    repo_root: Path | None = None,
) -> dict[str, Path]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    smoke = build_ticket27_staging_packaging_smoke(repo_root=resolved_repo_root)
    spec = build_ticket27_staging_packaging_spec()
    note = build_ticket27_staging_packaging_smoke_note(smoke)

    spec_path = resolved_repo_root / SPEC_ARTIFACT
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec, encoding="utf-8")

    smoke_path = resolved_repo_root / SMOKE_ARTIFACT
    smoke_path.parent.mkdir(parents=True, exist_ok=True)
    smoke_path.write_text(json.dumps(smoke, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    note_path = resolved_repo_root / SMOKE_NOTE_ARTIFACT
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")
    return {
        "spec_path": spec_path,
        "smoke_path": smoke_path,
        "note_path": note_path,
    }


def build_ticket27_staging_packaging_smoke(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    ledger = _load_json(resolved_repo_root / CANDIDATE_LEDGER_ARTIFACT)
    protocol_summary = _load_json(resolved_repo_root / PROTOCOL_SUMMARY_ARTIFACT)
    protocol_registry = _load_json(resolved_repo_root / PROTOCOL_REGISTRY_ARTIFACT)
    paired_gate = _load_json(resolved_repo_root / PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT)
    paired_audit = _load_json(resolved_repo_root / PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT)
    r2_registry = _load_json(resolved_repo_root / R2_SECOND_STAGE_REGISTRY_ARTIFACT)
    lift_registry = _load_json(resolved_repo_root / LIFT_SELECTION_REGISTRY_ARTIFACT)

    ledger_index = {row["candidate_id"]: row for row in ledger["rows"]}
    protocol_index = {row["candidate_id"]: row for row in protocol_registry["rows"]}

    positive_packaging = _build_positive_intrinsic_side(
        ledger_row=ledger_index[INTRINSIC_BASELINE_CANDIDATE_ID],
        r2_registry=r2_registry,
        protocol_row=protocol_index[INTRINSIC_BASELINE_CANDIDATE_ID],
    )
    positive_declared = _build_positive_lift_route_class_side(
        ledger_row=ledger_index[DECLARED_LIFT_CANDIDATE_ID],
        protocol_row=protocol_index[DECLARED_LIFT_CANDIDATE_ID],
        lift_registry=lift_registry,
        family_id="declared_completion_family",
        flattening_mode="none",
    )
    positive_paired = _build_positive_lift_route_class_side(
        ledger_row=ledger_index[PAIRED_LIFT_CANDIDATE_ID],
        protocol_row=None,
        lift_registry=lift_registry,
        family_id="paired_observable_enrichment",
        flattening_mode="paired_flattening_control",
        protocol_status_override="protocol_cleared_by_ticket27_adapter",
    )

    control_packaging_by_phase = _build_control_intrinsic_sides(
        ledger_row=ledger_index[INTRINSIC_BASELINE_CANDIDATE_ID],
        protocol_row=protocol_index[INTRINSIC_BASELINE_CANDIDATE_ID],
    )
    control_declared_by_phase = _build_control_declared_lift_route_class_sides(
        ledger_row=ledger_index[DECLARED_LIFT_CANDIDATE_ID],
        protocol_row=protocol_index[DECLARED_LIFT_CANDIDATE_ID],
        protocol_registry=protocol_registry,
    )
    control_paired_by_phase = _build_control_paired_lift_route_class_sides(
        ledger_row=ledger_index[PAIRED_LIFT_CANDIDATE_ID],
        paired_gate=paired_gate,
        paired_audit=paired_audit,
    )

    comparison_rows = [
        _build_comparison_row(
            comparison_id="comparison.positive.declared_route_class",
            comparison_kind="intrinsic_vs_lift_route_class",
            logical_case_id=POSITIVE_CASE_ID,
            protocol_phase_mode=None,
            logical_protocol_pair_mode="single_case",
            family_id="declared_completion_family",
            flattening_mode="none",
            strategy_id=None,
            packaging_side=positive_packaging,
            staging_side=positive_declared,
            source_artifacts=[
                R2_SECOND_STAGE_REGISTRY_ARTIFACT,
                CANDIDATE_LEDGER_ARTIFACT,
                LIFT_SELECTION_REGISTRY_ARTIFACT,
                PROTOCOL_REGISTRY_ARTIFACT,
            ],
        ),
        _build_comparison_row(
            comparison_id="comparison.positive.paired_route_class",
            comparison_kind="intrinsic_vs_lift_route_class",
            logical_case_id=POSITIVE_CASE_ID,
            protocol_phase_mode=None,
            logical_protocol_pair_mode="single_case",
            family_id="paired_observable_enrichment",
            flattening_mode="paired_flattening_control",
            strategy_id=None,
            packaging_side=positive_packaging,
            staging_side=positive_paired,
            source_artifacts=[
                R2_SECOND_STAGE_REGISTRY_ARTIFACT,
                CANDIDATE_LEDGER_ARTIFACT,
                LIFT_SELECTION_REGISTRY_ARTIFACT,
                PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
                PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
            ],
        ),
    ]

    for phase_mode in ("as_run_uninternalized", "internalized_partner"):
        comparison_rows.append(
            _build_comparison_row(
                comparison_id=f"comparison.control.declared_route_class.{phase_mode}",
                comparison_kind="intrinsic_vs_lift_route_class",
                logical_case_id=CONTROL_LOGICAL_CASE_ID,
                protocol_phase_mode=phase_mode,
                logical_protocol_pair_mode="paired_protocol_control",
                family_id="declared_completion_family",
                flattening_mode="none",
                strategy_id=None,
                packaging_side=control_packaging_by_phase[phase_mode],
                staging_side=control_declared_by_phase[phase_mode],
                source_artifacts=[
                    PROTOCOL_REGISTRY_ARTIFACT,
                    CANDIDATE_LEDGER_ARTIFACT,
                ],
            )
        )
        comparison_rows.append(
            _build_comparison_row(
                comparison_id=f"comparison.control.paired_route_class.{phase_mode}",
                comparison_kind="intrinsic_vs_lift_route_class",
                logical_case_id=CONTROL_LOGICAL_CASE_ID,
                protocol_phase_mode=phase_mode,
                logical_protocol_pair_mode="paired_protocol_control",
                family_id="paired_observable_enrichment",
                flattening_mode="paired_flattening_control",
                strategy_id=None,
                packaging_side=control_packaging_by_phase[phase_mode],
                staging_side=control_paired_by_phase[phase_mode],
                source_artifacts=[
                    PROTOCOL_REGISTRY_ARTIFACT,
                    PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT,
                    PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT,
                    CANDIDATE_LEDGER_ARTIFACT,
                ],
            )
        )

    positive_rows = [row for row in comparison_rows if row["logical_case_id"] == POSITIVE_CASE_ID]
    control_rows = [row for row in comparison_rows if row["logical_case_id"] == CONTROL_LOGICAL_CASE_ID]
    positive_average = _average_score(positive_rows)
    control_average = _average_score(control_rows)

    return {
        "ticket": "T27-15",
        "schema_version": "ticket27-staging-packaging-smoke.v1",
        "metric_definition": {
            "component_vocabulary": list(METRIC_COMPONENTS),
            "component_weights": dict(COMPONENT_WEIGHTS),
            "signature_fields": list(SIGNATURE_FIELDS),
            "scalar_summary_rule": "weighted_sum",
            "interpretation_thresholds": dict(INTERPRETATION_THRESHOLDS),
            "protocol_status_rank": dict(PROTOCOL_STATUS_RANK),
        },
        "smoke_cases": {
            "positive_case": {
                "logical_case_id": POSITIVE_CASE_ID,
                "config_path": POSITIVE_CONFIG_PATH,
                "packaging_side_candidate_id": INTRINSIC_BASELINE_CANDIDATE_ID,
                "attempted_lift_route_classes": [
                    {
                        "candidate_id": DECLARED_LIFT_CANDIDATE_ID,
                        "family_id": "declared_completion_family",
                        "flattening_mode": "none",
                    },
                    {
                        "candidate_id": PAIRED_LIFT_CANDIDATE_ID,
                        "family_id": "paired_observable_enrichment",
                        "flattening_mode": "paired_flattening_control",
                    },
                ],
            },
            "control_case": {
                "logical_case_id": CONTROL_LOGICAL_CASE_ID,
                "protocol_pair_mode": "paired_protocol_control",
                "uninternalized_config_path": CONTROL_UNINTERNALIZED_CONFIG_PATH,
                "internalized_config_path": CONTROL_INTERNALIZED_CONFIG_PATH,
                "packaging_side_candidate_id": INTRINSIC_BASELINE_CANDIDATE_ID,
                "attempted_lift_route_classes": [
                    {
                        "candidate_id": DECLARED_LIFT_CANDIDATE_ID,
                        "family_id": "declared_completion_family",
                        "flattening_mode": "none",
                    },
                    {
                        "candidate_id": PAIRED_LIFT_CANDIDATE_ID,
                        "family_id": "paired_observable_enrichment",
                        "flattening_mode": "paired_flattening_control",
                    },
                ],
            },
        },
        "comparison_rows": comparison_rows,
        "contrast_summary": {
            "positive_case_average_defect_score": positive_average,
            "control_case_average_defect_score": control_average,
            "positive_control_defect_contrast_visible": positive_average < control_average,
            "paired_observable_enrichment_route_class_control_executable": paired_gate["gate_result"]
            == "PASS_GATE"
            and paired_audit["resolution"] == "resolved_pass",
            "route_class_only_no_strategy_split": (
                paired_audit["route_class_summary"]["all_strategy_rows_tied"]
                and not paired_audit["route_class_summary"]["strategy_specific_superiority_supported"]
            ),
            "protocol_state_merge_basis": {
                "protocol_summary_branch_decision": protocol_summary["branch_decision"],
                "paired_family_gate_result": paired_gate["gate_result"],
                "paired_family_resolution": paired_audit["resolution"],
            },
            "summary_labels": [
                "paired_family_executable_on_control",
                "positive_control_defect_contrast_visible"
                if positive_average < control_average
                else "positive_control_defect_contrast_not_visible",
                "route_class_only_no_strategy_split",
            ],
        },
    }


def build_ticket27_staging_packaging_spec() -> str:
    return "\n".join(
        [
            "# Ticket27 Staging–Packaging Defect Spec",
            "",
            "## Compared Sides",
            "- Packaging-first side: the ticket27 intrinsic surface-coarsening baseline route anchored on `candidate.intrinsic_baseline.best_envelope`.",
            "- Staging-sensitive side: a ticket27 lift route-class or lift strategy route, compared on the same logical case.",
            "",
            "## Allowed Pair Types",
            "- `intrinsic_vs_lift_route_class`",
            "- `intrinsic_vs_lift_strategy`",
            "",
            "## Metric Components",
            "- `proposal_mismatch`",
            "- `burden_delta_abs`",
            "- `target_package_size_delta_abs`",
            "- `control_contrast_delta`",
            "- `protocol_status_delta`",
            "- `fallback_penalty`",
            "- `representative_selection_delta`",
            "- `signature_distance`",
            "",
            "## Scalar Summary Rule",
            "- Weighted sum over the eight components.",
            f"- Weights: `{json.dumps(COMPONENT_WEIGHTS, sort_keys=True)}`.",
            "",
            "## Compact Signature Surrogate",
            "- Deterministic signature fields:",
            f"  `{', '.join(SIGNATURE_FIELDS)}`",
            "- `signature_distance` is the count of differing fields across that compact signature.",
            "",
            "## Interpretation Labels",
            "- `low_defect`: weighted score <= 5",
            "- `moderate_defect`: weighted score 6..9",
            "- `high_defect`: weighted score >= 10",
            "- `unsupported_pair`: reserved for later tickets if either side is not executable",
            "",
            "## Smoke Comparison Set",
            f"- Positive case: `{POSITIVE_CONFIG_PATH}`.",
            "- Control logical case: `t27.control.artifact` via both canonical protocol endpoints.",
            "- Attempted lift families:",
            "  `declared_completion_family + none`",
            "  `paired_observable_enrichment + paired_flattening_control`",
            "",
            "## Protocol Reading",
            "- Intrinsic surface-coarsening routes are live and protocol-honest.",
            "- Declared-completion-family lift route class is live and protocol-honest.",
            "- `paired_observable_enrichment + paired_flattening_control` is protocol-cleared for ticket27 by the adapter artifacts:",
            f"  `{PAIRED_LIFT_PROTOCOL_GATE_ARTIFACT}` and `{PAIRED_LIFT_PROTOCOL_AUDIT_ARTIFACT}`.",
            "- Strategy-specific superiority on that paired family is not supported because all five strategies still tie.",
            "",
        ]
    )


def build_ticket27_staging_packaging_smoke_note(
    smoke_payload: dict[str, Any],
) -> str:
    summary = smoke_payload["contrast_summary"]
    return "\n".join(
        [
            "# Ticket27 Staging–Packaging Smoke Note",
            "",
            f"- Positive case: `{POSITIVE_CONFIG_PATH}`.",
            (
                "- Control pair: "
                f"`{CONTROL_UNINTERNALIZED_CONFIG_PATH}` and `{CONTROL_INTERNALIZED_CONFIG_PATH}`."
            ),
            (
                "- Positive/control defect contrast visible: "
                f"`{summary['positive_control_defect_contrast_visible']}`."
            ),
            (
                "- Paired-observable-enrichment executable on control: "
                f"`{summary['paired_observable_enrichment_route_class_control_executable']}`."
            ),
            (
                "- Route-class only, no strategy split: "
                f"`{summary['route_class_only_no_strategy_split']}`."
            ),
            "",
        ]
    )


def _build_positive_intrinsic_side(
    *,
    ledger_row: dict[str, Any],
    r2_registry: dict[str, Any],
    protocol_row: dict[str, Any],
) -> dict[str, Any]:
    case = next(case for case in r2_registry["cases"] if case["stable_id"] == POSITIVE_CASE_ID)
    candidate = next(
        payload
        for payload in case["candidates"]
        if payload["proposal"]["proposal_id"] == ledger_row["proposal_id"]
    )
    return _side_payload(
        candidate_id=f"{ledger_row['candidate_id']}::{POSITIVE_CASE_ID}",
        proposal_id=ledger_row["proposal_id"],
        burden=ledger_row["best_common_flagship_burden"],
        target_package_size=candidate["target_package_size"],
        preserved_required_control_contrast_count=ledger_row[
            "preserved_required_control_contrast_count"
        ],
        protocol_status=protocol_row["protocol_honesty_status"],
        fallback_involved=False,
        representative_selection_effective=False,
        family_id=None,
        flattening_mode=None,
        signature_material={
            "candidate_fingerprint": candidate["candidate_fingerprint"],
            "closure_status": candidate["closure_status"],
            "source_package_size": case["source_package_size"],
        },
    )


def _build_positive_lift_route_class_side(
    *,
    ledger_row: dict[str, Any],
    protocol_row: dict[str, Any] | None,
    lift_registry: dict[str, Any],
    family_id: str,
    flattening_mode: str,
    protocol_status_override: str | None = None,
) -> dict[str, Any]:
    rows = [
        row
        for row in lift_registry["rows"]
        if row["stable_id"] == POSITIVE_CASE_ID
        and row["family_id"] == family_id
        and row["flattening_mode"] == flattening_mode
        and row["skip_reason"] is None
    ]
    target_package_sizes = sorted(
        {row["best_second_stage_target_package_size"] for row in rows}
    )
    burdens = sorted({row["best_second_stage_coarsening_burden"] for row in rows})
    fallback_involved = any(row["fallback_used"] for row in rows)
    signature_basis = {
        "candidate_route_signature_ids": sorted(
            {
                _proposal_summary_signature(row["proposal_summaries"], ledger_row["proposal_id"])
                for row in rows
            }
        ),
        "strategy_ids": sorted({row["strategy_id"] for row in rows}),
    }
    return _side_payload(
        candidate_id=f"{ledger_row['candidate_id']}::{POSITIVE_CASE_ID}",
        proposal_id=ledger_row["proposal_id"],
        burden=_common_value(burdens),
        target_package_size=_common_value(target_package_sizes),
        preserved_required_control_contrast_count=ledger_row[
            "preserved_required_control_contrast_count"
        ],
        protocol_status=protocol_status_override
        or protocol_row["protocol_honesty_status"],
        fallback_involved=fallback_involved,
        representative_selection_effective=False,
        family_id=family_id,
        flattening_mode=flattening_mode,
        signature_material=signature_basis,
    )


def _build_control_intrinsic_sides(
    *,
    ledger_row: dict[str, Any],
    protocol_row: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    sides: dict[str, dict[str, Any]] = {}
    for endpoint in protocol_row["artifact_pair_rows"]:
        sides[endpoint["protocol_phase_mode"]] = _side_payload(
            candidate_id=(
                f"{ledger_row['candidate_id']}::{CONTROL_LOGICAL_CASE_ID}::"
                f"{endpoint['protocol_phase_mode']}"
            ),
            proposal_id=endpoint["candidate_route_proposal_id"],
            burden=ledger_row["best_common_flagship_burden"],
            target_package_size=endpoint["candidate_route_target_package_size"],
            preserved_required_control_contrast_count=ledger_row[
                "preserved_required_control_contrast_count"
            ],
            protocol_status=protocol_row["protocol_honesty_status"],
            fallback_involved=False,
            representative_selection_effective=False,
            family_id=None,
            flattening_mode=None,
            signature_material={
                "candidate_route_signature_id": endpoint["candidate_route_signature_id"],
                "artifact_or_control_reading": endpoint["artifact_or_control_reading"],
                "protocol_internalization_status": endpoint["protocol_internalization_status"],
            },
        )
    return sides


def _build_control_declared_lift_route_class_sides(
    *,
    ledger_row: dict[str, Any],
    protocol_row: dict[str, Any],
    protocol_registry: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    strategy_rows = [
        row
        for row in protocol_registry["rows"]
        if row["candidate_kind"] == "lift_strategy"
        and row["family_id"] == ledger_row["family_id"]
        and row["flattening_mode"] == ledger_row["flattening_mode"]
        and row["proposal_id"] == ledger_row["proposal_id"]
    ]
    by_phase: dict[str, list[dict[str, Any]]] = {}
    for strategy_row in strategy_rows:
        for endpoint in strategy_row["artifact_pair_rows"]:
            by_phase.setdefault(endpoint["protocol_phase_mode"], []).append(endpoint)
    endpoint_rows = {}
    for endpoint in protocol_row["artifact_pair_rows"]:
        phase_rows = by_phase[endpoint["protocol_phase_mode"]]
        endpoint_rows[endpoint["protocol_phase_mode"]] = _side_payload(
            candidate_id=(
                f"{ledger_row['candidate_id']}::{CONTROL_LOGICAL_CASE_ID}::"
                f"{endpoint['protocol_phase_mode']}"
            ),
            proposal_id=ledger_row["proposal_id"],
            burden=ledger_row["best_common_flagship_burden"],
            target_package_size=_common_value(
                [row["candidate_route_target_package_size"] for row in phase_rows]
            ),
            preserved_required_control_contrast_count=ledger_row[
                "preserved_required_control_contrast_count"
            ],
            protocol_status=protocol_row["protocol_honesty_status"],
            fallback_involved=any(row["fallback_used"] for row in phase_rows),
            representative_selection_effective=False,
            family_id=ledger_row["family_id"],
            flattening_mode=ledger_row["flattening_mode"],
            signature_material={
                "candidate_route_signature_ids": sorted(
                    {row["candidate_route_signature_id"] for row in phase_rows}
                ),
                "strategy_ids": sorted({row["strategy_id"] for row in phase_rows}),
            },
        )
    return endpoint_rows


def _build_control_paired_lift_route_class_sides(
    *,
    ledger_row: dict[str, Any],
    paired_gate: dict[str, Any],
    paired_audit: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    if paired_gate["gate_result"] != "PASS_GATE" or paired_audit["resolution"] != "resolved_pass":
        raise ValueError("paired ticket27 lift route is not protocol-cleared for staging smoke")
    by_phase: dict[str, list[dict[str, Any]]] = {}
    for strategy_row in paired_audit["strategy_rows"]:
        for endpoint in strategy_row["endpoint_rows"]:
            by_phase.setdefault(endpoint["protocol_phase_mode"], []).append(endpoint)
    sides: dict[str, dict[str, Any]] = {}
    for phase_mode, rows in sorted(by_phase.items()):
        target_package_sizes = sorted(
            {row["candidate_route_signature"]["target_package_size"] for row in rows}
        )
        signature_ids = sorted({row["candidate_route_signature_id"] for row in rows})
        sides[phase_mode] = _side_payload(
            candidate_id=f"{ledger_row['candidate_id']}::{CONTROL_LOGICAL_CASE_ID}::{phase_mode}",
            proposal_id=ledger_row["proposal_id"],
            burden=ledger_row["best_common_flagship_burden"],
            target_package_size=_common_value(target_package_sizes),
            preserved_required_control_contrast_count=ledger_row[
                "preserved_required_control_contrast_count"
            ],
            protocol_status="protocol_cleared_by_ticket27_adapter",
            fallback_involved=any(row["fallback_used"] for row in rows),
            representative_selection_effective=False,
            family_id=ledger_row["family_id"],
            flattening_mode=ledger_row["flattening_mode"],
            signature_material={
                "candidate_route_signature_ids": signature_ids,
                "strategy_ids": [
                    row["strategy_id"] for row in paired_audit["strategy_rows"]
                ],
            },
        )
    return sides


def _build_comparison_row(
    *,
    comparison_id: str,
    comparison_kind: str,
    logical_case_id: str,
    protocol_phase_mode: str | None,
    logical_protocol_pair_mode: str,
    family_id: str,
    flattening_mode: str,
    strategy_id: str | None,
    packaging_side: dict[str, Any],
    staging_side: dict[str, Any],
    source_artifacts: list[str],
) -> dict[str, Any]:
    component_values = _component_values(packaging_side, staging_side)
    defect_score = sum(
        COMPONENT_WEIGHTS[name] * component_values[name] for name in METRIC_COMPONENTS
    )
    return {
        "comparison_id": comparison_id,
        "comparison_kind": comparison_kind,
        "logical_case_id": logical_case_id,
        "protocol_phase_mode": protocol_phase_mode,
        "logical_protocol_pair_mode": logical_protocol_pair_mode,
        "family_id": family_id,
        "flattening_mode": flattening_mode,
        "strategy_id": strategy_id,
        "packaging_side_candidate_id": packaging_side["candidate_id"],
        "staging_side_candidate_id": staging_side["candidate_id"],
        "packaging_side_signature": packaging_side["compact_signature"],
        "staging_side_signature": staging_side["compact_signature"],
        **component_values,
        "defect_score": defect_score,
        "interpretation_label": _interpretation_label(defect_score),
        "source_artifacts": list(source_artifacts),
    }


def _component_values(
    packaging_side: dict[str, Any],
    staging_side: dict[str, Any],
) -> dict[str, int]:
    return {
        "proposal_mismatch": int(
            packaging_side["proposal_id"] != staging_side["proposal_id"]
        ),
        "burden_delta_abs": abs(packaging_side["burden"] - staging_side["burden"]),
        "target_package_size_delta_abs": abs(
            packaging_side["target_package_size"] - staging_side["target_package_size"]
        ),
        "control_contrast_delta": abs(
            packaging_side["preserved_required_control_contrast_count"]
            - staging_side["preserved_required_control_contrast_count"]
        ),
        "protocol_status_delta": abs(
            packaging_side["protocol_status_rank"] - staging_side["protocol_status_rank"]
        ),
        "fallback_penalty": int(staging_side["fallback_involved"]),
        "representative_selection_delta": abs(
            int(packaging_side["representative_selection_effective"])
            - int(staging_side["representative_selection_effective"])
        ),
        "signature_distance": _signature_distance(
            packaging_side["compact_signature"], staging_side["compact_signature"]
        ),
    }


def _interpretation_label(defect_score: int) -> str:
    if defect_score <= INTERPRETATION_THRESHOLDS["low_defect_max"]:
        return "low_defect"
    if defect_score <= INTERPRETATION_THRESHOLDS["moderate_defect_max"]:
        return "moderate_defect"
    return "high_defect"


def _side_payload(
    *,
    candidate_id: str,
    proposal_id: str,
    burden: int,
    target_package_size: int,
    preserved_required_control_contrast_count: int,
    protocol_status: str,
    fallback_involved: bool,
    representative_selection_effective: bool,
    family_id: str | None,
    flattening_mode: str | None,
    signature_material: dict[str, Any],
) -> dict[str, Any]:
    compact_signature = {
        "proposal_id": proposal_id,
        "burden": burden,
        "target_package_size": target_package_size,
        "protocol_status_rank": PROTOCOL_STATUS_RANK[protocol_status],
        "fallback_involved": fallback_involved,
        "representative_selection_effective": representative_selection_effective,
        "family_id": family_id,
        "flattening_mode": flattening_mode,
    }
    compact_signature_id = hashlib.sha256(
        json.dumps(compact_signature, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "candidate_id": candidate_id,
        "proposal_id": proposal_id,
        "burden": burden,
        "target_package_size": target_package_size,
        "preserved_required_control_contrast_count": preserved_required_control_contrast_count,
        "protocol_status": protocol_status,
        "protocol_status_rank": PROTOCOL_STATUS_RANK[protocol_status],
        "fallback_involved": fallback_involved,
        "representative_selection_effective": representative_selection_effective,
        "family_id": family_id,
        "flattening_mode": flattening_mode,
        "signature_material": signature_material,
        "compact_signature": {
            **compact_signature,
            "compact_signature_id": compact_signature_id,
        },
    }


def _signature_distance(left: dict[str, Any], right: dict[str, Any]) -> int:
    return sum(int(left.get(field) != right.get(field)) for field in SIGNATURE_FIELDS)


def _proposal_summary_signature(
    proposal_summaries: list[dict[str, Any]],
    proposal_id: str,
) -> str:
    summary = next(payload for payload in proposal_summaries if payload["proposal_id"] == proposal_id)
    core = {
        "proposal_id": summary["proposal_id"],
        "target_package_size": summary["target_package_size"],
        "candidate_fingerprint": summary["candidate_fingerprint"],
        "closure_status": summary["closure_status"],
    }
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _average_score(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return round(sum(row["defect_score"] for row in rows) / len(rows), 3)


def _common_value(values: list[Any]) -> Any:
    if not values:
        return None
    first = values[0]
    if any(value != first for value in values[1:]):
        raise ValueError(f"expected a common value, got {values!r}")
    return first


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
