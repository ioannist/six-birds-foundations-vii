from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._recombination_support.frontier.engine import evaluate_frozen_slice, validate_frozen_slice_metric_names
from sixbirds_foundations_v._recombination_support.frontier.models import (
    CandidateMetricObservation,
    CandidateMetricStatus,
    CandidateObservationLedger,
    CandidateObservationRow,
)
from sixbirds_foundations_v._recombination_support.schemas import FrozenSliceConfig


REPO_ROOT = Path(__file__).resolve().parents[3]

R2_SECOND_STAGE_REGISTRY_ARTIFACT = "results/derived/ticket27r2_second_stage_registry.json"
R2_SECOND_STAGE_SUMMARY_ARTIFACT = "results/derived/ticket27r2_second_stage_stability_summary.json"
R2_GATE_DECISION_ARTIFACT = "results/derived/ticket27r2_gate_decision.json"
LIFT_INTRINSIC_BASELINE_ARTIFACT = "results/derived/ticket27_lift_intrinsic_baseline.json"
LIFT_SELECTION_SUMMARY_ARTIFACT = "results/derived/ticket27_lift_selection_summary.json"
LIFT_SELECTION_REGISTRY_ARTIFACT = "results/derived/ticket27_lift_selection_registry.json"

SLICE_REGISTRY_ARTIFACT = "results/derived/ticket27_slice_registry.json"
LEDGER_SMOKE_ARTIFACT = "results/derived/ticket27_candidate_observation_ledger_smoke.json"
FRONTIER_SMOKE_ARTIFACT = "results/derived/ticket27_slice_frontier_smoke.json"
SLICE_NOTE_ARTIFACT = "results/notes/ticket27_slice_smoke_note.md"

SUPPORT_ATOM_ID = "ticket27.slice.smoke"

FIELD_TO_METRIC_NAME = {
    "flagship_gate_supported_count": "ticket27_flagship_gate_supported_count",
    "flagship_non_fallback_supported_count": "ticket27_flagship_non_fallback_supported_count",
    "preserved_required_control_contrast_count": "ticket27_preserved_required_control_contrast_count",
    "nearby_positive_supported_count": "ticket27_nearby_positive_supported_count",
    "best_common_flagship_burden": "ticket27_best_common_flagship_burden",
    "fallback_involved": "ticket27_fallback_involved",
    "route_complexity_penalty": "ticket27_route_complexity_penalty",
}

ROUTE_COMPLEXITY_PENALTY = {
    "intrinsic_baseline_envelope": 1,
    "intrinsic_proposal": 1,
    "lift_route_class": 2,
    "lift_strategy": 3,
}


def build_ticket27_slice_scaffold_artifacts(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    slice_registry = build_ticket27_slice_registry()
    ledger = build_ticket27_candidate_observation_ledger_smoke(repo_root=resolved_repo_root)
    frontier = build_ticket27_slice_frontier_smoke(
        ledger_payload=ledger,
        slice_registry=slice_registry,
    )
    note = build_ticket27_slice_smoke_note(
        slice_registry=slice_registry,
        frontier_payload=frontier,
    )

    slice_registry_path = _write_json_artifact(
        resolved_repo_root / SLICE_REGISTRY_ARTIFACT,
        slice_registry,
    )
    ledger_path = _write_json_artifact(
        resolved_repo_root / LEDGER_SMOKE_ARTIFACT,
        ledger,
    )
    frontier_path = _write_json_artifact(
        resolved_repo_root / FRONTIER_SMOKE_ARTIFACT,
        frontier,
    )
    note_path = resolved_repo_root / SLICE_NOTE_ARTIFACT
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")
    return {
        "slice_registry_path": slice_registry_path,
        "ledger_path": ledger_path,
        "frontier_path": frontier_path,
        "note_path": note_path,
    }


def build_ticket27_slice_registry() -> dict[str, Any]:
    slices = [
        _slice_payload(
            slice_id="stability_first",
            yield_fields=[
                "flagship_gate_supported_count",
                "flagship_non_fallback_supported_count",
                "preserved_required_control_contrast_count",
            ],
            cost_fields=[
                "best_common_flagship_burden",
                "fallback_involved",
            ],
            tie_break_rule=[
                "maximize flagship_gate_supported_count",
                "maximize flagship_non_fallback_supported_count",
                "maximize preserved_required_control_contrast_count",
                "minimize best_common_flagship_burden",
                "minimize fallback_involved",
                "lexical candidate_id",
            ],
        ),
        _slice_payload(
            slice_id="coverage_first",
            yield_fields=[
                "flagship_gate_supported_count",
                "preserved_required_control_contrast_count",
                "nearby_positive_supported_count",
            ],
            cost_fields=["best_common_flagship_burden"],
            tie_break_rule=[
                "maximize flagship_gate_supported_count",
                "maximize preserved_required_control_contrast_count",
                "maximize nearby_positive_supported_count",
                "minimize best_common_flagship_burden",
                "lexical candidate_id",
            ],
        ),
        _slice_payload(
            slice_id="parsimony_first",
            yield_fields=[
                "flagship_gate_supported_count",
                "preserved_required_control_contrast_count",
            ],
            cost_fields=[
                "best_common_flagship_burden",
                "route_complexity_penalty",
            ],
            tie_break_rule=[
                "maximize flagship_gate_supported_count",
                "maximize preserved_required_control_contrast_count",
                "minimize best_common_flagship_burden",
                "minimize route_complexity_penalty",
                "lexical candidate_id",
            ],
        ),
    ]
    return {
        "ticket": "T27-11",
        "schema_version": "ticket27-slice-registry.v1",
        "route_complexity_penalty_by_candidate_kind": dict(ROUTE_COMPLEXITY_PENALTY),
        "slices": slices,
    }


def build_ticket27_candidate_observation_ledger_smoke(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    intrinsic_baseline = _load_json(resolved_repo_root / LIFT_INTRINSIC_BASELINE_ARTIFACT)
    lift_summary = _load_json(resolved_repo_root / LIFT_SELECTION_SUMMARY_ARTIFACT)
    lift_registry = _load_json(resolved_repo_root / LIFT_SELECTION_REGISTRY_ARTIFACT)
    gate_payload = _load_json(resolved_repo_root / R2_GATE_DECISION_ARTIFACT)

    rows = []
    best_envelope = intrinsic_baseline["best_intrinsic_envelope"]
    if best_envelope is not None:
        rows.append(
            _make_candidate_row(
                candidate_id="candidate.intrinsic_baseline.best_envelope",
                candidate_kind="intrinsic_baseline_envelope",
                route_class="intrinsic_surface_coarsening",
                strategy_id=None,
                proposal_id=best_envelope["proposal_id"],
                family_id=None,
                flattening_mode=None,
                source_artifacts=[
                    LIFT_INTRINSIC_BASELINE_ARTIFACT,
                    R2_GATE_DECISION_ARTIFACT,
                ],
                flagship_gate_supported_count=2,
                flagship_non_fallback_supported_count=2,
                preserved_required_control_contrast_count=best_envelope[
                    "preserved_required_control_contrast_count"
                ],
                nearby_positive_supported_count=best_envelope["nearby_positive_supported_count"],
                best_common_flagship_burden=best_envelope["coarsening_burden"],
                target_package_size=best_envelope["flagship_target_package_size"],
                fallback_involved=False,
                representative_selection_effective=False,
                selection_basis_summary=(
                    "Best intrinsic envelope ranked from the full qualifying r2 proposal set using the "
                    "T27-10 lexicographic rule."
                ),
            )
        )

    for proposal in intrinsic_baseline["qualifying_proposals"]:
        rows.append(
            _make_candidate_row(
                candidate_id=f"candidate.intrinsic_proposal.{proposal['proposal_id']}",
                candidate_kind="intrinsic_proposal",
                route_class="intrinsic_surface_coarsening",
                strategy_id=None,
                proposal_id=proposal["proposal_id"],
                family_id=None,
                flattening_mode=None,
                source_artifacts=[
                    LIFT_INTRINSIC_BASELINE_ARTIFACT,
                    R2_SECOND_STAGE_REGISTRY_ARTIFACT,
                    R2_SECOND_STAGE_SUMMARY_ARTIFACT,
                ],
                flagship_gate_supported_count=2,
                flagship_non_fallback_supported_count=2,
                preserved_required_control_contrast_count=proposal[
                    "preserved_required_control_contrast_count"
                ],
                nearby_positive_supported_count=proposal["nearby_positive_supported_count"],
                best_common_flagship_burden=proposal["coarsening_burden"],
                target_package_size=proposal["flagship_target_package_size"],
                fallback_involved=False,
                representative_selection_effective=False,
                selection_basis_summary=(
                    "Qualifying intrinsic proposal from the repaired r2 second-stage registry."
                ),
            )
        )

    route_class_row = _build_lift_route_class_row(
        lift_summary=lift_summary,
        lift_registry=lift_registry,
    )
    rows.append(route_class_row)

    for strategy_summary in lift_summary["strategies"]:
        rows.append(
            _build_lift_strategy_row(
                strategy_summary=strategy_summary,
                lift_registry=lift_registry,
            )
        )

    return {
        "ticket": "T27-11",
        "schema_version": "ticket27-candidate-observation-ledger-smoke.v1",
        "canonical_input_artifacts": [
            R2_GATE_DECISION_ARTIFACT,
            R2_SECOND_STAGE_REGISTRY_ARTIFACT,
            R2_SECOND_STAGE_SUMMARY_ARTIFACT,
            LIFT_INTRINSIC_BASELINE_ARTIFACT,
            LIFT_SELECTION_SUMMARY_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
        ],
        "current_gate_decision": gate_payload["gate_decision"],
        "route_complexity_penalty_by_candidate_kind": dict(ROUTE_COMPLEXITY_PENALTY),
        "rows": rows,
    }


def build_ticket27_slice_frontier_smoke(
    *,
    ledger_payload: dict[str, Any],
    slice_registry: dict[str, Any],
) -> dict[str, Any]:
    candidate_index = {row["candidate_id"]: row for row in ledger_payload["rows"]}
    frontier_ledger = _to_frontier_candidate_observation_ledger(ledger_payload["rows"])

    frontier_results = []
    for slice_payload in slice_registry["slices"]:
        config = FrozenSliceConfig.model_validate(slice_payload["frozen_slice_config"])
        validate_frozen_slice_metric_names(config)
        result = evaluate_frozen_slice(config, frontier_ledger)
        rows = []
        for result_row in result.rows:
            candidate_row = candidate_index[result_row.candidate_id]
            rows.append(
                {
                    "candidate_id": result_row.candidate_id,
                    "candidate_kind": candidate_row["candidate_kind"],
                    "route_class": candidate_row["route_class"],
                    "strategy_id": candidate_row["strategy_id"],
                    "proposal_id": candidate_row["proposal_id"],
                    "frontier_member": result_row.frontier_member,
                    "dominated_by": result_row.dominated_by,
                    "dominates": result_row.dominates,
                    "aggregated_yield_vector": result_row.aggregated_yield_vector,
                    "aggregated_cost_vector": result_row.aggregated_cost_vector,
                    "representative_selection_effective": candidate_row[
                        "representative_selection_effective"
                    ],
                    "selection_basis_summary": candidate_row["selection_basis_summary"],
                }
            )
        frontier_results.append(
            {
                "slice_id": slice_payload["slice_id"],
                "yield_fields": slice_payload["yield_fields"],
                "cost_fields": slice_payload["cost_fields"],
                "candidate_ids_considered": [row["candidate_id"] for row in ledger_payload["rows"]],
                "non_dominated_candidate_ids": result.frontier_candidate_ids,
                "rows": rows,
            }
        )

    return {
        "ticket": "T27-11",
        "schema_version": "ticket27-slice-frontier-smoke.v1",
        "ledger_artifact": LEDGER_SMOKE_ARTIFACT,
        "slice_registry_artifact": SLICE_REGISTRY_ARTIFACT,
        "frontier_results": frontier_results,
    }


def build_ticket27_slice_smoke_note(
    *,
    slice_registry: dict[str, Any],
    frontier_payload: dict[str, Any],
) -> str:
    coverage_result = next(
        result
        for result in frontier_payload["frontier_results"]
        if result["slice_id"] == "coverage_first"
    )
    lines = [
        "# Ticket27 Slice Smoke Note",
        "",
        "- Slice ids: "
        + ", ".join(f"`{slice_payload['slice_id']}`" for slice_payload in slice_registry["slices"])
        + ".",
        (
            "- Intrinsic baseline on coverage frontier: "
            f"`{'candidate.intrinsic_baseline.best_envelope' in coverage_result['non_dominated_candidate_ids']}`."
        ),
        "- Frontier membership is recomputed from raw smoke-ledger metrics via the generic frontier engine.",
        "",
    ]
    return "\n".join(lines)


def _slice_payload(
    *,
    slice_id: str,
    yield_fields: list[str],
    cost_fields: list[str],
    tie_break_rule: list[str],
) -> dict[str, Any]:
    return {
        "slice_id": slice_id,
        "yield_fields": yield_fields,
        "cost_fields": cost_fields,
        "comparison_rule": "pareto_non_dominance_over_declared_fields",
        "tie_break_rule": tie_break_rule,
        "frozen_slice_config": {
            "schema_version": "recombination-frozen-slice-config.v2",
            "config_kind": "frozen-slice",
            "config_id": f"ticket27.{slice_id}",
            "slice_id": slice_id,
            "benchmark_id": "ticket27.slice.smoke",
            "support_cone": {
                "support_cone_id": "ticket27.slice.smoke.support",
                "support_atom_ids": [SUPPORT_ATOM_ID],
                "notes": ["Single support atom smoke cone over the ticket27 candidate ledger."],
            },
            "yield_terms": [
                {
                    "metric_name": FIELD_TO_METRIC_NAME[field_name],
                    "aggregation_op": "max",
                    "required": True,
                }
                for field_name in yield_fields
            ],
            "cost_terms": [
                {
                    "metric_name": FIELD_TO_METRIC_NAME[field_name],
                    "aggregation_op": "max",
                    "required": True,
                }
                for field_name in cost_fields
            ],
            "comparison_tolerance": 0.0,
            "cone_equivalence_tolerance": 0.0,
            "notes": [
                "Ticket27 slice scaffold smoke config generated from raw lift/intrinsic candidate metrics.",
            ],
            "tags": ["ticket27", "slice_scaffold"],
        },
    }


def _build_lift_route_class_row(
    *,
    lift_summary: dict[str, Any],
    lift_registry: dict[str, Any],
) -> dict[str, Any]:
    strategy_summaries = lift_summary["strategies"]
    family_id = strategy_summaries[0]["best_common_family_id"]
    flattening_mode = strategy_summaries[0]["best_common_flattening_mode"]
    proposal_id = strategy_summaries[0]["best_common_flagship_proposal_id"]
    target_package_size = _find_target_package_size(
        lift_registry=lift_registry,
        strategy_id="identity_reference",
        family_id=family_id,
        flattening_mode=flattening_mode,
        proposal_id=proposal_id,
    )
    return _make_candidate_row(
        candidate_id="candidate.lift_route_class.common_flagship_route",
        candidate_kind="lift_route_class",
        route_class="representative_selected_lift",
        strategy_id=None,
        proposal_id=proposal_id,
        family_id=family_id,
        flattening_mode=flattening_mode,
        source_artifacts=[
            LIFT_SELECTION_SUMMARY_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
            R2_GATE_DECISION_ARTIFACT,
        ],
        flagship_gate_supported_count=2,
        flagship_non_fallback_supported_count=2,
        preserved_required_control_contrast_count=strategy_summaries[0][
            "preserved_required_control_contrast_count"
        ],
        nearby_positive_supported_count=strategy_summaries[0]["nearby_positive_supported_count"],
        best_common_flagship_burden=strategy_summaries[0]["best_common_flagship_burden"],
        target_package_size=target_package_size,
        fallback_involved=False,
        representative_selection_effective=False,
        selection_basis_summary=(
            "Aggregate route-class row for the best common flagship lift route shared across all "
            "five strategies; it records lift mechanics without claiming strategy superiority."
        ),
    )


def _build_lift_strategy_row(
    *,
    strategy_summary: dict[str, Any],
    lift_registry: dict[str, Any],
) -> dict[str, Any]:
    family_id = strategy_summary["best_common_family_id"]
    flattening_mode = strategy_summary["best_common_flattening_mode"]
    proposal_id = strategy_summary["best_common_flagship_proposal_id"]
    target_package_size = _find_target_package_size(
        lift_registry=lift_registry,
        strategy_id=strategy_summary["strategy_id"],
        family_id=family_id,
        flattening_mode=flattening_mode,
        proposal_id=proposal_id,
    )
    effective = _strategy_specific_selection_effective(
        strategy_id=strategy_summary["strategy_id"],
        family_id=family_id,
        flattening_mode=flattening_mode,
        lift_registry=lift_registry,
    )
    return _make_candidate_row(
        candidate_id=f"candidate.lift_strategy.{strategy_summary['strategy_id']}",
        candidate_kind="lift_strategy",
        route_class="representative_selected_lift",
        strategy_id=strategy_summary["strategy_id"],
        proposal_id=proposal_id,
        family_id=family_id,
        flattening_mode=flattening_mode,
        source_artifacts=[
            LIFT_SELECTION_SUMMARY_ARTIFACT,
            LIFT_SELECTION_REGISTRY_ARTIFACT,
        ],
        flagship_gate_supported_count=2 if strategy_summary["both_flagships_gate_supported"] else 0,
        flagship_non_fallback_supported_count=(
            2 if strategy_summary["flagship_core_non_fallback_row_count"] >= 2 else 0
        ),
        preserved_required_control_contrast_count=strategy_summary[
            "preserved_required_control_contrast_count"
        ],
        nearby_positive_supported_count=strategy_summary["nearby_positive_supported_count"],
        best_common_flagship_burden=strategy_summary["best_common_flagship_burden"],
        target_package_size=target_package_size,
        fallback_involved=strategy_summary["flagship_core_non_fallback_row_count"] < 2,
        representative_selection_effective=effective,
        selection_basis_summary=(
            "Best common flagship route is "
            f"{family_id}/{flattening_mode}/{proposal_id}; "
            f"comparison_reason={strategy_summary['comparison_reason']}."
        ),
    )


def _strategy_specific_selection_effective(
    *,
    strategy_id: str,
    family_id: str | None,
    flattening_mode: str | None,
    lift_registry: dict[str, Any],
) -> bool:
    if strategy_id == "identity_reference" or family_id is None or flattening_mode is None:
        return False
    for row in lift_registry["rows"]:
        if row["strategy_id"] != strategy_id:
            continue
        if row["stable_id"] not in {
            "t27.flagship.reference_positive",
            "t27.flagship.completion_partner",
        }:
            continue
        if row["skip_reason"] is not None:
            continue
        if row["family_id"] != family_id or row["flattening_mode"] != flattening_mode:
            continue
        if row["mapping_differs_from_identity_reference"]:
            return True
    return False


def _find_target_package_size(
    *,
    lift_registry: dict[str, Any],
    strategy_id: str,
    family_id: str | None,
    flattening_mode: str | None,
    proposal_id: str | None,
) -> int | None:
    if family_id is None or flattening_mode is None or proposal_id is None:
        return None
    target_sizes = []
    for row in lift_registry["rows"]:
        if row["strategy_id"] != strategy_id:
            continue
        if row["stable_id"] not in {
            "t27.flagship.reference_positive",
            "t27.flagship.completion_partner",
        }:
            continue
        if row["skip_reason"] is not None:
            continue
        if row["family_id"] != family_id or row["flattening_mode"] != flattening_mode:
            continue
        if row["best_second_stage_proposal_id"] != proposal_id:
            continue
        if row["best_second_stage_target_package_size"] is not None:
            target_sizes.append(row["best_second_stage_target_package_size"])
    return min(target_sizes) if target_sizes else None


def _make_candidate_row(
    *,
    candidate_id: str,
    candidate_kind: str,
    route_class: str,
    strategy_id: str | None,
    proposal_id: str | None,
    family_id: str | None,
    flattening_mode: str | None,
    source_artifacts: list[str],
    flagship_gate_supported_count: int,
    flagship_non_fallback_supported_count: int,
    preserved_required_control_contrast_count: int,
    nearby_positive_supported_count: int,
    best_common_flagship_burden: int | None,
    target_package_size: int | None,
    fallback_involved: bool,
    representative_selection_effective: bool,
    selection_basis_summary: str,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "route_class": route_class,
        "strategy_id": strategy_id,
        "proposal_id": proposal_id,
        "family_id": family_id,
        "flattening_mode": flattening_mode,
        "source_artifacts": source_artifacts,
        "flagship_gate_supported_count": flagship_gate_supported_count,
        "flagship_non_fallback_supported_count": flagship_non_fallback_supported_count,
        "preserved_required_control_contrast_count": preserved_required_control_contrast_count,
        "nearby_positive_supported_count": nearby_positive_supported_count,
        "best_common_flagship_burden": best_common_flagship_burden,
        "target_package_size": target_package_size,
        "fallback_involved": fallback_involved,
        "representative_selection_effective": representative_selection_effective,
        "route_complexity_penalty": ROUTE_COMPLEXITY_PENALTY[candidate_kind],
        "selection_basis_summary": selection_basis_summary,
    }


def _to_frontier_candidate_observation_ledger(
    rows: list[dict[str, Any]],
) -> CandidateObservationLedger:
    frontier_rows = []
    for row in rows:
        metric_results = {}
        for field_name, metric_name in FIELD_TO_METRIC_NAME.items():
            value = row.get(field_name)
            if isinstance(value, bool):
                numeric_value = 1.0 if value else 0.0
            else:
                numeric_value = float(value)
            metric_results[metric_name] = CandidateMetricObservation(
                metric_name=metric_name,
                status=CandidateMetricStatus.OK,
                scope_status="stable",
                value=numeric_value,
                details={"source_field": field_name},
            )
        frontier_rows.append(
            CandidateObservationRow(
                candidate_id=row["candidate_id"],
                support_atom_id=SUPPORT_ATOM_ID,
                benchmark_id="ticket27.slice.smoke",
                source_kind=row["route_class"],
                control_mode=row["flattening_mode"],
                phase_mode=row["candidate_kind"],
                strategy_id=row["strategy_id"],
                comparison_group=row["candidate_kind"],
                tags=[row["candidate_kind"], row["route_class"]],
                metric_results=metric_results,
                provenance={
                    "candidate_kind": row["candidate_kind"],
                    "source_artifacts": ",".join(row["source_artifacts"]),
                },
                notes=[row["selection_basis_summary"]],
            )
        )
    return CandidateObservationLedger(
        ledger_id="ticket27.slice.scaffold.smoke",
        rows=frontier_rows,
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
