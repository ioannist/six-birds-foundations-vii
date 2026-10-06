from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from sixbirds_foundations_v._recombination_support.benchmarks.loader import load_benchmark
from sixbirds_foundations_v._recombination_support.carriers import (
    compute_branchwise_quotient,
    compute_current_quotient,
    compute_eta_factor_map,
    compute_predictive_quotient,
    compute_recombination_quotient,
)
from sixbirds_foundations_v._recombination_support.runner import (
    BenchmarkRunArtifacts,
    SearchArtifacts,
    SweepArtifacts,
    load_run_config,
    run_config,
    search_config,
    sweep_config,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_LEDGER_PATH = REPO_ROOT / "results" / "expected" / "interference_expected_invariants.json"

PLAN_PATH_NAME = "ticket6_validation_plan.json"
LEDGER_PATH_NAME = "ticket6_validation_ledger.json"
DISCREPANCY_PATH_NAME = "ticket6_discrepancies.json"

ABS_TOLERANCE = 1e-9

EXACT_CONFIG_PATHS = {
    "interference.classical_mixture.baseline": "configs/recombination/benchmarks/interference/classical_mixture/baseline.json",
    "interference.memory_only.control": "configs/recombination/benchmarks/interference/memory_only/control.json",
    "interference.marked_suppression.baseline": "configs/recombination/benchmarks/interference/marked_suppression/baseline.json",
    "interference.erasure_recovery.anchor": "configs/recombination/benchmarks/interference/erasure_recovery/anchor.json",
    "interference.protocol_artifact.uninternalized": "configs/recombination/benchmarks/interference/protocol_artifact/uninternalized.json",
    "interference.protocol_artifact.internalized": "configs/recombination/benchmarks/interference/protocol_artifact/internalized.json",
    "interference.flattening_control.reference_positive": "configs/recombination/benchmarks/interference/flattening_control/reference_positive.json",
    "interference.flattening_control.completion_partner": "configs/recombination/benchmarks/interference/flattening_control/completion_partner.json",
}

SUMMARY_CONFIG_PATHS = {
    "interference.cyclic_relative_carrier.bounded_space": "configs/recombination/search/interference/cyclic_relative_carrier/bounded_space.json",
    "interference.cyclic_relative_carrier.discovery_grid": "configs/recombination/search/interference/cyclic_relative_carrier/discovery_grid.json",
    "interference.dissipative_washout.anchor_sweep": "configs/recombination/search/interference/dissipative_washout/anchor_sweep.json",
}

EXACT_INTERFERENCE_BENCHMARK_IDS = tuple(EXACT_CONFIG_PATHS)
SUMMARY_INTERFERENCE_BENCHMARK_IDS = tuple(SUMMARY_CONFIG_PATHS)


@dataclass(frozen=True)
class ExactValidationSurface:
    benchmark_id: str
    config_path: Path
    artifacts: BenchmarkRunArtifacts
    diagnostics_summary: dict[str, Any]
    current_quotient_count: int
    predictive_quotient_count: int
    branchwise_quotient_count: int
    recombination_quotient_count: int
    eta_max_fiber_size: int


def generate_ticket6_validation_artifacts(
    *,
    repo_root: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, Path]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    resolved_output_root = (output_root or resolved_repo_root).resolve()
    derived_root = resolved_output_root / "results" / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)

    expected_payload = json.loads(EXPECTED_LEDGER_PATH.read_text(encoding="utf-8"))
    expected_records = expected_payload["records"]

    with TemporaryDirectory(prefix="ticket6-validation-") as tmpdir:
        workspace_root = Path(tmpdir)
        exact_surfaces = _run_exact_validation_surfaces(resolved_repo_root, workspace_root)
        summary_surfaces = _run_summary_validation_surfaces(resolved_repo_root, workspace_root)
        shared_artifacts = _collect_shared_validation_artifacts(exact_surfaces)

        plan_payload = _build_validation_plan(expected_records)
        ledger_entries = []
        for expected_record in expected_records:
            benchmark_id = expected_record["benchmark_id"]
            if benchmark_id in exact_surfaces:
                ledger_entries.append(
                    _validate_exact_record(
                        expected_record,
                        exact_surfaces[benchmark_id],
                        shared_artifacts=shared_artifacts,
                    )
                )
            else:
                ledger_entries.append(
                    _validate_summary_record(
                        expected_record,
                        summary_surfaces[benchmark_id],
                    )
                )

    branch = _compute_branch_decision(ledger_entries)
    discrepancy_payload = _build_discrepancy_payload(ledger_entries)
    ledger_payload = {
        "schema_version": "ticket6-validation-ledger.v1",
        "source_expected_ledger": _repo_relative(EXPECTED_LEDGER_PATH, resolved_repo_root),
        "comparison_policy": {
            "integer_boolean_categorical": "exact equality",
            "rational_numeric": "normalize to exact Fraction when possible",
            "float_absolute_tolerance": ABS_TOLERANCE,
            "summary_family_status": "summary_consistent when aggregate search/sweep outputs match expected family statements",
            "note_like_fields": "summary_consistent when runtime classification artifacts support the same semantic conclusion",
        },
        "branch_decision": branch,
        "entry_count": len(ledger_entries),
        "overall_status_counts": _count_by_key(ledger_entries, "overall_status"),
        "entries": ledger_entries,
    }

    plan_path = derived_root / PLAN_PATH_NAME
    ledger_path = derived_root / LEDGER_PATH_NAME
    discrepancy_path = derived_root / DISCREPANCY_PATH_NAME

    plan_path.write_text(json.dumps(plan_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    discrepancy_path.write_text(
        json.dumps(discrepancy_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return {
        "plan_path": plan_path,
        "ledger_path": ledger_path,
        "discrepancy_path": discrepancy_path,
    }


def _run_exact_validation_surfaces(
    repo_root: Path,
    workspace_root: Path,
) -> dict[str, ExactValidationSurface]:
    ordered_ids = (
        "interference.classical_mixture.baseline",
        "interference.memory_only.control",
        "interference.marked_suppression.baseline",
        "interference.erasure_recovery.anchor",
        "interference.protocol_artifact.uninternalized",
        "interference.protocol_artifact.internalized",
        "interference.flattening_control.reference_positive",
        "interference.flattening_control.completion_partner",
    )
    surfaces: dict[str, ExactValidationSurface] = {}
    for benchmark_id in ordered_ids:
        config_path = repo_root / EXACT_CONFIG_PATHS[benchmark_id]
        artifacts = run_config(
            load_run_config(config_path),
            config_path=config_path,
            output_root=workspace_root,
            command_used=f"python scripts/generate_ticket6_validation_ledger.py --exact {benchmark_id}",
        )
        diagnostics_summary = json.loads(artifacts.diagnostics_summary_path.read_text(encoding="utf-8"))
        loaded = load_benchmark(config_path)
        current = compute_current_quotient(loaded)
        predictive = compute_predictive_quotient(loaded)
        branchwise = compute_branchwise_quotient(loaded)
        recombination = compute_recombination_quotient(loaded)
        eta = compute_eta_factor_map(loaded)
        surfaces[benchmark_id] = ExactValidationSurface(
            benchmark_id=benchmark_id,
            config_path=config_path,
            artifacts=artifacts,
            diagnostics_summary=diagnostics_summary,
            current_quotient_count=current.class_count,
            predictive_quotient_count=predictive.class_count,
            branchwise_quotient_count=branchwise.class_count,
            recombination_quotient_count=recombination.class_count,
            eta_max_fiber_size=eta.max_fiber_size,
        )
    return surfaces


def _run_summary_validation_surfaces(
    repo_root: Path,
    workspace_root: Path,
) -> dict[str, dict[str, Any]]:
    surfaces: dict[str, dict[str, Any]] = {}
    for benchmark_id in (
        "interference.cyclic_relative_carrier.bounded_space",
        "interference.cyclic_relative_carrier.discovery_grid",
    ):
        config_path = repo_root / SUMMARY_CONFIG_PATHS[benchmark_id]
        artifacts = search_config(
            load_run_config(config_path),
            config_path=config_path,
            output_root=workspace_root,
            command_used=f"python scripts/generate_ticket6_validation_ledger.py --summary {benchmark_id}",
        )
        surfaces[benchmark_id] = _load_search_surface(benchmark_id, config_path, artifacts)

    diss_benchmark_id = "interference.dissipative_washout.anchor_sweep"
    diss_config_path = repo_root / SUMMARY_CONFIG_PATHS[diss_benchmark_id]
    diss_artifacts = sweep_config(
        load_run_config(diss_config_path),
        config_path=diss_config_path,
        output_root=workspace_root,
        command_used=f"python scripts/generate_ticket6_validation_ledger.py --summary {diss_benchmark_id}",
    )
    surfaces[diss_benchmark_id] = _load_sweep_surface(
        diss_benchmark_id,
        diss_config_path,
        diss_artifacts,
    )
    return surfaces


def _load_search_surface(
    benchmark_id: str,
    config_path: Path,
    artifacts: SearchArtifacts,
) -> dict[str, Any]:
    payload = {
        "benchmark_id": benchmark_id,
        "config_path": config_path.as_posix(),
        "summary_table": json.loads(artifacts.summary_table_json_path.read_text(encoding="utf-8")),
        "smoke_summary": json.loads(artifacts.smoke_summary_path.read_text(encoding="utf-8")),
    }
    if artifacts.promoted_candidates_path is not None:
        payload["promoted_candidates"] = json.loads(
            artifacts.promoted_candidates_path.read_text(encoding="utf-8")
        )
    return payload


def _load_sweep_surface(
    benchmark_id: str,
    config_path: Path,
    artifacts: SweepArtifacts,
) -> dict[str, Any]:
    return {
        "benchmark_id": benchmark_id,
        "config_path": config_path.as_posix(),
        "summary_table": json.loads(artifacts.summary_table_json_path.read_text(encoding="utf-8")),
        "collapse_summary": json.loads(artifacts.collapse_summary_path.read_text(encoding="utf-8"))
        if artifacts.collapse_summary_path is not None
        else None,
    }


def _collect_shared_validation_artifacts(
    exact_surfaces: dict[str, ExactValidationSurface],
) -> dict[str, Any]:
    shared: dict[str, Any] = {}
    protocol_artifacts = exact_surfaces["interference.protocol_artifact.internalized"].artifacts
    if protocol_artifacts.pairwise_comparison_path is not None:
        shared["protocol_internalization_comparison"] = json.loads(
            protocol_artifacts.pairwise_comparison_path.read_text(encoding="utf-8")
        )
    flattening_artifacts = exact_surfaces["interference.flattening_control.completion_partner"].artifacts
    if flattening_artifacts.pairwise_comparison_path is not None:
        shared["flattening_completion_comparison"] = json.loads(
            flattening_artifacts.pairwise_comparison_path.read_text(encoding="utf-8")
        )
    erasure_artifacts = exact_surfaces["interference.erasure_recovery.anchor"].artifacts
    if erasure_artifacts.pairwise_comparison_path is not None:
        shared["paired_marked_comparison"] = json.loads(
            erasure_artifacts.pairwise_comparison_path.read_text(encoding="utf-8")
        )
    return shared


def _build_validation_plan(expected_records: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for record in expected_records:
        benchmark_id = record["benchmark_id"]
        if benchmark_id in EXACT_CONFIG_PATHS:
            validation_mode = "exact_runnable"
            config_path = EXACT_CONFIG_PATHS[benchmark_id]
        elif benchmark_id in SUMMARY_CONFIG_PATHS:
            validation_mode = "family_summary"
            config_path = SUMMARY_CONFIG_PATHS[benchmark_id]
        else:
            validation_mode = "unresolved"
            config_path = None
        entries.append(
            {
                "benchmark_id": benchmark_id,
                "expectation_status": record["expectation_status"],
                "validation_mode": validation_mode,
                "config_path": config_path,
                "field_sources": _field_source_plan(record),
            }
        )
    return {
        "schema_version": "ticket6-validation-plan.v1",
        "source_expected_ledger": _repo_relative(EXPECTED_LEDGER_PATH, REPO_ROOT),
        "entries": entries,
    }


def _field_source_plan(record: dict[str, Any]) -> dict[str, str]:
    benchmark_id = record["benchmark_id"]
    plan: dict[str, str] = {}
    for family_name, invariants in record["expected_invariants"].items():
        for key, value in invariants.items() if isinstance(invariants, dict) else []:
            field_path = f"{family_name}.{key}"
            if field_path.startswith("cardinalities."):
                plan[field_path] = "carrier_library"
            elif key in {
                "eta_max",
                "recombination_gap",
                "route_readability",
                "raw_route_recovery_success",
                "unconditional_visibility",
                "maximal_conditional_visibility",
                "visibility_recovery_gap",
            }:
                plan[field_path] = "existing_runtime_metric"
            elif key == "artifact_flag":
                plan[field_path] = "existing_result_manifest"
            elif key == "classification_note":
                plan[field_path] = "summary_comparison"
            elif key == "survives_flattening_completion":
                plan[field_path] = "summary_comparison"
            else:
                plan[field_path] = "summary_comparison"
        if not isinstance(invariants, dict):
            plan[family_name] = "summary_comparison"
    if benchmark_id.startswith("interference.cyclic_relative_carrier") or benchmark_id.startswith(
        "interference.dissipative_washout"
    ):
        for key in record["expected_invariants"]:
            if key not in plan:
                plan[key] = "summary_comparison"
    return plan


def _validate_exact_record(
    expected_record: dict[str, Any],
    surface: ExactValidationSurface,
    *,
    shared_artifacts: dict[str, Any],
) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    computed = _computed_exact_values(surface, shared_artifacts=shared_artifacts)
    for family_name, invariants in expected_record["expected_invariants"].items():
        if not isinstance(invariants, dict):
            continue
        for key, expected_value in invariants.items():
            field_path = f"{family_name}.{key}"
            comparison = _compare_exact_field(
                benchmark_id=expected_record["benchmark_id"],
                field_path=field_path,
                expected_value=expected_value,
                computed_values=computed,
            )
            comparisons.append(comparison)
    overall_status = _overall_status_for_exact(comparisons)
    return {
        "benchmark_id": expected_record["benchmark_id"],
        "family": expected_record["family"],
        "variant": expected_record["variant"],
        "validation_mode": "exact_runnable",
        "expectation_status": expected_record["expectation_status"],
        "overall_status": overall_status,
        "config_path": _repo_relative(surface.config_path, REPO_ROOT),
        "comparison_count": len(comparisons),
        "status_counts": _count_by_key(comparisons, "status"),
        "comparisons": comparisons,
    }


def _computed_exact_values(
    surface: ExactValidationSurface,
    *,
    shared_artifacts: dict[str, Any],
) -> dict[str, Any]:
    record = surface.artifacts.manifest.records[0]
    summary = surface.diagnostics_summary
    values = {
        "cardinalities.Q": surface.current_quotient_count,
        "cardinalities.M": surface.predictive_quotient_count,
        "cardinalities.K": surface.branchwise_quotient_count,
        "cardinalities.R": surface.recombination_quotient_count,
        "metrics.eta_max": surface.eta_max_fiber_size,
        "metrics.recombination_gap": summary["recombination_gap"]["metric_value"],
        "metrics.route_readability": summary["route_readability"]["score_value"],
        "metrics.raw_route_recovery_success": summary["route_readability"]["raw_success_probability"],
        "metrics.unconditional_visibility": summary["conditional_visibility"]["unconditional_visibility"],
        "metrics.maximal_conditional_visibility": summary["conditional_visibility"]["max_conditional_visibility"],
        "metrics.visibility_recovery_gap": summary["conditional_visibility"]["visibility_recovery_gap"],
        "metrics.artifact_flag": record.class_label.value == "artifact",
    }
    protocol_payload = shared_artifacts.get("protocol_internalization_comparison")
    if protocol_payload is not None:
        values["metrics.classification_note"] = {
            "class_label_internalized": protocol_payload["class_label_internalized"],
            "verdict": protocol_payload["verdict"],
        }
    flattening_payload = shared_artifacts.get("flattening_completion_comparison")
    if flattening_payload is not None:
        values["metrics.survives_flattening_completion"] = bool(
            flattening_payload["survives_flattening_completion"]
        )
    return values


def _compare_exact_field(
    *,
    benchmark_id: str,
    field_path: str,
    expected_value: Any,
    computed_values: dict[str, Any],
) -> dict[str, Any]:
    source_kind = _source_kind_for_field(field_path)
    if field_path not in computed_values:
        return {
            "field_path": field_path,
            "source_kind": source_kind,
            "expected_value": expected_value,
            "computed_value": None,
            "status": "not_computed",
            "detail": "no current code path exposes this invariant",
        }
    computed_value = computed_values[field_path]
    if field_path == "metrics.classification_note":
        payload = dict(computed_value)
        status = (
            "summary_consistent"
            if payload["class_label_internalized"] == "memory_only"
            and payload["verdict"] == "artifact_exposed_by_internalization"
            else "mismatch"
        )
        return {
            "field_path": field_path,
            "source_kind": source_kind,
            "expected_value": expected_value,
            "computed_value": payload,
            "status": status,
            "detail": "validated semantically through the protocol internalization comparison",
        }
    status = _comparison_status(expected_value, computed_value, summary_mode=False)
    return {
        "field_path": field_path,
        "source_kind": source_kind,
        "expected_value": expected_value,
        "computed_value": computed_value,
        "status": status,
    }


def _validate_summary_record(
    expected_record: dict[str, Any],
    surface: dict[str, Any],
) -> dict[str, Any]:
    comparisons: list[dict[str, Any]] = []
    computed = _computed_summary_values(expected_record["benchmark_id"], surface)
    for key, expected_value in expected_record["expected_invariants"].items():
        if isinstance(expected_value, dict):
            for nested_key, nested_expected in expected_value.items():
                field_path = f"{key}.{nested_key}"
                comparisons.append(
                    {
                        "field_path": field_path,
                        "source_kind": "summary_comparison",
                        "expected_value": nested_expected,
                        "computed_value": computed.get(field_path),
                        "status": _comparison_status(
                            nested_expected,
                            computed.get(field_path),
                            summary_mode=True,
                        ),
                    }
                )
        else:
            field_path = key
            comparisons.append(
                {
                    "field_path": field_path,
                    "source_kind": "summary_comparison",
                    "expected_value": expected_value,
                    "computed_value": computed.get(field_path),
                    "status": _comparison_status(
                        expected_value,
                        computed.get(field_path),
                        summary_mode=True,
                    ),
                }
            )
    overall_status = (
        "validated_summary_only"
        if all(item["status"] == "summary_consistent" for item in comparisons)
        else "blocked_by_spec_ambiguity"
    )
    return {
        "benchmark_id": expected_record["benchmark_id"],
        "family": expected_record["family"],
        "variant": expected_record["variant"],
        "validation_mode": "family_summary",
        "expectation_status": expected_record["expectation_status"],
        "overall_status": overall_status,
        "config_path": _repo_relative(Path(surface["config_path"]), REPO_ROOT),
        "comparison_count": len(comparisons),
        "status_counts": _count_by_key(comparisons, "status"),
        "comparisons": comparisons,
    }


def _computed_summary_values(
    benchmark_id: str,
    surface: dict[str, Any],
) -> dict[str, Any]:
    if benchmark_id == "interference.cyclic_relative_carrier.bounded_space":
        smoke = surface["smoke_summary"]
        return {
            "case_count": surface["summary_table"]["case_count"],
            "positive_regime_cases": smoke["label_counts"].get("coherent_branch_candidate", 0),
            "unclassified_cases": smoke["label_counts"].get("unclassified", 0),
            "representative_case_id": smoke["representative_case_ids"].get("coherent_branch_candidate"),
            "unclassified_case_id": smoke["representative_case_ids"].get("unclassified"),
        }
    if benchmark_id == "interference.cyclic_relative_carrier.discovery_grid":
        smoke = surface["smoke_summary"]
        promoted_candidates = surface.get("promoted_candidates", {}).get("promoted_candidates", [])
        return {
            "case_count": surface["summary_table"]["case_count"],
            "coherent_branch_candidate_cases": smoke["label_counts"].get("coherent_branch_candidate", 0),
            "unclassified_cases": smoke["label_counts"].get("unclassified", 0),
            "promoted_candidate_count": len(promoted_candidates),
            "representative_case_id": smoke["representative_case_ids"].get("coherent_branch_candidate"),
            "unclassified_case_id": smoke["representative_case_ids"].get("unclassified"),
        }
    rows = surface["summary_table"]["rows"]
    full_noise_row = rows[-1]
    return {
        "noise_strengths": [row["noise_strength"] for row in rows],
        "recombination_gap_sequence": [row["recombination_gap_value"] for row in rows],
        "maximal_conditional_visibility_sequence": [row["max_conditional_visibility"] for row in rows],
        "full_noise_endpoint.K": full_noise_row["branchwise_quotient_size"],
        "full_noise_endpoint.R": full_noise_row["recombination_quotient_size"],
        "full_noise_endpoint.eta_max": full_noise_row["eta_max_fiber_size"],
        "full_noise_endpoint.recombination_gap": full_noise_row["recombination_gap_value"],
    }


def _source_kind_for_field(field_path: str) -> str:
    if field_path.startswith("cardinalities."):
        return "carrier_library"
    if field_path in {
        "metrics.eta_max",
        "metrics.recombination_gap",
        "metrics.route_readability",
        "metrics.raw_route_recovery_success",
        "metrics.unconditional_visibility",
        "metrics.maximal_conditional_visibility",
        "metrics.visibility_recovery_gap",
    }:
        return "existing_runtime_metric"
    if field_path == "metrics.artifact_flag":
        return "existing_result_manifest"
    if field_path in {"metrics.classification_note", "metrics.survives_flattening_completion"}:
        return "summary_comparison"
    return "not_currently_computable"


def _comparison_status(
    expected_value: Any,
    computed_value: Any,
    *,
    summary_mode: bool,
) -> str:
    if computed_value is None:
        return "summary_only" if summary_mode else "not_computed"
    if _values_match(expected_value, computed_value):
        return "summary_consistent" if summary_mode else "exact_match"
    if _values_near_match(expected_value, computed_value):
        return "near_match"
    return "mismatch"


def _values_match(expected_value: Any, computed_value: Any) -> bool:
    if isinstance(expected_value, bool):
        return isinstance(computed_value, bool) and expected_value is computed_value
    if isinstance(expected_value, int) and not isinstance(expected_value, bool):
        return int(computed_value) == expected_value
    if isinstance(expected_value, list):
        if not isinstance(computed_value, list) or len(expected_value) != len(computed_value):
            return False
        return all(_values_match(left, right) for left, right in zip(expected_value, computed_value, strict=True))
    if isinstance(expected_value, dict):
        if not isinstance(computed_value, dict):
            return False
        return all(
            key in computed_value and _values_match(value, computed_value[key])
            for key, value in expected_value.items()
        )
    expected_fraction = _maybe_fraction(expected_value)
    computed_fraction = _maybe_fraction(computed_value)
    if expected_fraction is not None and computed_fraction is not None:
        return expected_fraction == computed_fraction
    return str(expected_value) == str(computed_value)


def _values_near_match(expected_value: Any, computed_value: Any) -> bool:
    expected_fraction = _maybe_fraction(expected_value)
    computed_fraction = _maybe_fraction(computed_value)
    if expected_fraction is None or computed_fraction is None:
        return False
    return abs(float(expected_fraction - computed_fraction)) <= ABS_TOLERANCE


def _maybe_fraction(value: Any) -> Fraction | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        return Fraction(str(value))
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError):
            return None
    return None


def _overall_status_for_exact(comparisons: list[dict[str, Any]]) -> str:
    statuses = {item["status"] for item in comparisons}
    if statuses <= {"exact_match", "near_match", "summary_consistent"}:
        return "validated_with_near_matches" if "near_match" in statuses else "validated_exact"
    if "mismatch" in statuses:
        return "validated_with_discrepancies"
    if {"not_computed", "unresolved_spec"} & statuses:
        return "blocked_by_spec_ambiguity"
    return "validated_with_discrepancies"


def _compute_branch_decision(entries: list[dict[str, Any]]) -> str:
    exact_entries = [entry for entry in entries if entry["validation_mode"] == "exact_runnable"]
    if any(entry["overall_status"] == "blocked_by_spec_ambiguity" for entry in exact_entries):
        return "BLOCKED_BY_SPEC_AMBIGUITY"
    if any(entry["overall_status"] == "validated_with_discrepancies" for entry in exact_entries):
        return "REPRODUCED_WITH_DISCREPANCIES"
    return "REPRODUCED"


def _build_discrepancy_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    discrepancies = []
    for entry in entries:
        for comparison in entry["comparisons"]:
            if comparison["status"] in {"exact_match", "near_match", "summary_consistent"}:
                continue
            discrepancies.append(
                {
                    "benchmark_id": entry["benchmark_id"],
                    "field_path": comparison["field_path"],
                    "expected_value": comparison["expected_value"],
                    "computed_value": comparison.get("computed_value"),
                    "comparison_status": comparison["status"],
                    "likely_cause_category": _likely_cause_category(entry, comparison),
                }
            )
    return {
        "schema_version": "ticket6-discrepancies.v1",
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
        "note": (
            "none beyond summary/spec limitations"
            if not discrepancies
            else "see discrepancy rows"
        ),
    }


def _likely_cause_category(entry: dict[str, Any], comparison: dict[str, Any]) -> str:
    if entry["validation_mode"] == "family_summary":
        return "summary_only"
    if comparison["status"] == "not_computed":
        return "runtime_gap"
    if comparison["status"] == "summary_only":
        return "summary_only"
    if comparison["status"] == "unresolved_spec":
        return "spec_gap"
    return "semantic_mismatch"


def _count_by_key(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item[key])
        counts[value] = counts.get(value, 0) + 1
    return counts


def _repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


__all__ = [
    "EXACT_INTERFERENCE_BENCHMARK_IDS",
    "SUMMARY_INTERFERENCE_BENCHMARK_IDS",
    "generate_ticket6_validation_artifacts",
]
