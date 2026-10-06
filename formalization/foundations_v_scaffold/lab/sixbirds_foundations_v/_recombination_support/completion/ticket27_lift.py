from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._recombination_support.benchmarks.loader import load_benchmark

from .framework import (
    CompletionFamilyId,
    CompletionInputKind,
    CompletionRequest,
    CompletionSourceKind,
    FlatteningControlMode,
    apply_completion_request,
    build_completion_source_surface,
)
from .ticket27_support import strip_completion_sensitive_signature


REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_GATE_ARTIFACT_PATH = "results/derived/ticket27r2_gate_decision.json"
FLAGSHIP_SMOKE_CONFIG_PATH = (
    "configs/recombination/benchmarks/interference/flattening_control/completion_partner.json"
)
CONTROL_SMOKE_CONFIG_PATH = (
    "configs/recombination/benchmarks/interference/memory_only/control.json"
)
SMOKE_CASES = (
    {
        "case_id": "ticket27.flagship.completion_partner",
        "config_path": FLAGSHIP_SMOKE_CONFIG_PATH,
    },
    {
        "case_id": "ticket27.control.memory_only",
        "config_path": CONTROL_SMOKE_CONFIG_PATH,
    },
)
REQUIRED_STRATEGY_IDS = (
    "identity_reference",
    "max_weight_representative",
    "predictive_signature_canonical",
    "completion_preserving",
    "control_matched",
)


def build_lift_smoke_payload(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    gate_payload = json.loads(
        (resolved_repo_root / CANONICAL_GATE_ARTIFACT_PATH).read_text(encoding="utf-8")
    )
    rows = []
    benchmarks = {
        case["config_path"]: load_benchmark(resolved_repo_root / case["config_path"])
        for case in SMOKE_CASES
    }
    parameters_by_case = _build_strategy_parameters_by_case(resolved_repo_root)

    identity_rows_by_case: dict[str, dict[str, Any]] = {}
    for case in SMOKE_CASES:
        identity_row = _run_strategy_row(
            case=case,
            strategy_id="identity_reference",
            benchmark=benchmarks[case["config_path"]],
            family_id=CompletionFamilyId.DECLARED_COMPLETION_FAMILY,
            strategy_parameters={},
            flattening_mode=FlatteningControlMode.NONE,
        )
        identity_rows_by_case[case["config_path"]] = identity_row
        rows.append(identity_row)

    for case in SMOKE_CASES:
        for strategy_id in REQUIRED_STRATEGY_IDS[1:]:
            row = _run_strategy_row(
                case=case,
                strategy_id=strategy_id,
                benchmark=benchmarks[case["config_path"]],
                family_id=parameters_by_case[case["config_path"]][strategy_id]["family_id"],
                strategy_parameters=parameters_by_case[case["config_path"]][strategy_id][
                    "strategy_parameters"
                ],
                flattening_mode=parameters_by_case[case["config_path"]][strategy_id][
                    "flattening_mode"
                ],
            )
            row["selection_differs_from_identity_reference"] = (
                row["representative_mapping"]
                != identity_rows_by_case[case["config_path"]]["representative_mapping"]
            )
            rows.append(row)

    strategy_summary = {}
    for strategy_id in REQUIRED_STRATEGY_IDS:
        strategy_rows = [row for row in rows if row["strategy_id"] == strategy_id]
        strategy_summary[strategy_id] = {
            "row_count": len(strategy_rows),
            "non_fallback_case_ids": [
                row["case_id"] for row in strategy_rows if not row["fallback_used"]
            ],
            "differs_from_identity_case_ids": [
                row["case_id"]
                for row in strategy_rows
                if row["selection_differs_from_identity_reference"]
            ],
        }

    return {
        "ticket": "T27-09",
        "schema_version": "ticket27-lift-smoke.v1",
        "canonical_gate_artifact": CANONICAL_GATE_ARTIFACT_PATH,
        "canonical_gate_decision": gate_payload["gate_decision"],
        "canonical_gate_allows_t27_09": gate_payload["t27_09_allowed"],
        "source_kind": CompletionSourceKind.RECOMBINATION_QUOTIENT.value,
        "required_strategy_ids": list(REQUIRED_STRATEGY_IDS),
        "smoke_case_config_paths": [case["config_path"] for case in SMOKE_CASES],
        "strategy_summary": strategy_summary,
        "rows": rows,
    }


def build_lift_smoke_note(payload: dict[str, Any]) -> str:
    lines = [
        "# Ticket27 Lift Smoke Note",
        "",
        f"- Canonical gate artifact: `{payload['canonical_gate_artifact']}`.",
        f"- Canonical gate decision: `{payload['canonical_gate_decision']}`.",
        f"- Source kind: `{payload['source_kind']}`.",
        "",
        "## New Strategy Coverage",
    ]
    for strategy_id in ("completion_preserving", "control_matched"):
        summary = payload["strategy_summary"][strategy_id]
        lines.append(
            f"- `{strategy_id}`: non-fallback on `{summary['non_fallback_case_ids']}`, differs from identity on `{summary['differs_from_identity_case_ids']}`."
        )
    lines.append("")
    return "\n".join(lines)


def write_lift_smoke_outputs(
    *,
    repo_root: Path | None = None,
    artifact_path: str = "results/derived/ticket27_lift_smoke.json",
    note_path: str = "results/notes/ticket27_lift_smoke_note.md",
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    payload = build_lift_smoke_payload(repo_root=resolved_repo_root)
    note = build_lift_smoke_note(payload)
    artifact_output_path = resolved_repo_root / artifact_path
    artifact_output_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    note_output_path = resolved_repo_root / note_path
    note_output_path.parent.mkdir(parents=True, exist_ok=True)
    note_output_path.write_text(note, encoding="utf-8")
    return {
        "artifact_path": artifact_output_path,
        "note_path": note_output_path,
        "row_count": len(payload["rows"]),
    }


def _run_strategy_row(
    *,
    case: dict[str, str],
    strategy_id: str,
    benchmark: Any,
    family_id: CompletionFamilyId,
    strategy_parameters: dict[str, Any],
    flattening_mode: FlatteningControlMode,
) -> dict[str, Any]:
    request = CompletionRequest(
        input_kind=CompletionInputKind.BENCHMARK_REQUEST,
        source_kind=CompletionSourceKind.RECOMBINATION_QUOTIENT,
        strategy_id=strategy_id,
        family_id=family_id,
        config_path=case["config_path"],
        strategy_parameters=strategy_parameters,
        flattening_mode=flattening_mode,
    )
    first = apply_completion_request(request, benchmark=benchmark)
    second = apply_completion_request(request, benchmark=benchmark)
    strategy_payload = strategy_parameters.get(strategy_id, {})
    return {
        "case_id": case["case_id"],
        "config_path": case["config_path"],
        "source_kind": CompletionSourceKind.RECOMBINATION_QUOTIENT.value,
        "strategy_id": strategy_id,
        "family_id": family_id.value,
        "representative_mapping": first.representative_mapping,
        "representative_candidate_counts": first.representative_candidate_counts,
        "class_selections": [selection.model_dump(mode="json") for selection in first.class_selections],
        "deterministic_repeat_match": (
            first.representative_mapping == second.representative_mapping
            and first.class_selections == second.class_selections
        ),
        "selection_differs_from_identity_reference": False,
        "fallback_used": first.provenance.fallback_used is not None,
        "fallback_reason": first.provenance.fallback_used,
        "reference_config_path": strategy_payload.get("reference_config_path"),
        "reference_config_id": strategy_payload.get("reference_config_id"),
        "selection_basis": [
            selection.score_summary.get("selection_basis") for selection in first.class_selections
        ],
        "score_summary_by_class": {
            selection.class_id: selection.score_summary for selection in first.class_selections
        },
    }


def _build_strategy_parameters_by_case(repo_root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    flagship_path = FLAGSHIP_SMOKE_CONFIG_PATH
    control_path = CONTROL_SMOKE_CONFIG_PATH
    partner_path = (
        "configs/recombination/benchmarks/interference/flattening_control/reference_positive.json"
    )

    partner_reference = _build_identity_reference_payload(
        repo_root,
        config_path=partner_path,
    )
    control_reference = _build_identity_reference_payload(
        repo_root,
        config_path=control_path,
    )
    flagship_reference = _build_identity_reference_payload(
        repo_root,
        config_path=flagship_path,
    )

    return {
        flagship_path: {
            "max_weight_representative": _plain_strategy_request(),
            "predictive_signature_canonical": _plain_strategy_request(),
            "completion_preserving": {
                "family_id": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
                "flattening_mode": FlatteningControlMode.PAIRED_FLATTENING_CONTROL,
                "strategy_parameters": {
                    "completion_preserving": {
                        "reference_config_path": partner_path,
                        "reference_config_id": partner_reference["config_id"],
                        "per_class": partner_reference["per_class"],
                    }
                },
            },
            "control_matched": {
                "family_id": CompletionFamilyId.DECLARED_COMPLETION_FAMILY,
                "flattening_mode": FlatteningControlMode.NONE,
                "strategy_parameters": {
                    "control_matched": {
                        "reference_config_path": control_path,
                        "reference_config_id": control_reference["config_id"],
                        "per_class": control_reference["per_class"],
                    }
                },
            },
        },
        control_path: {
            "max_weight_representative": _plain_strategy_request(),
            "predictive_signature_canonical": _plain_strategy_request(),
            "completion_preserving": _plain_strategy_request(),
            "control_matched": {
                "family_id": CompletionFamilyId.DECLARED_COMPLETION_FAMILY,
                "flattening_mode": FlatteningControlMode.NONE,
                "strategy_parameters": {
                    "control_matched": {
                        "reference_config_path": flagship_path,
                        "reference_config_id": flagship_reference["config_id"],
                        "per_class": flagship_reference["per_class"],
                    }
                },
            },
        },
    }


def _plain_strategy_request() -> dict[str, Any]:
    return {
        "family_id": CompletionFamilyId.DECLARED_COMPLETION_FAMILY,
        "flattening_mode": FlatteningControlMode.NONE,
        "strategy_parameters": {},
    }


def _build_identity_reference_payload(
    repo_root: Path,
    *,
    config_path: str,
) -> dict[str, Any]:
    benchmark = load_benchmark(repo_root / config_path)
    return {
        "config_id": benchmark.config_id,
        "per_class": _reference_payload_by_class(benchmark, config_path),
    }


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
    payload: dict[str, dict[str, Any]] = {}
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


__all__ = [
    "CANONICAL_GATE_ARTIFACT_PATH",
    "CONTROL_SMOKE_CONFIG_PATH",
    "FLAGSHIP_SMOKE_CONFIG_PATH",
    "REQUIRED_STRATEGY_IDS",
    "SMOKE_CASES",
    "build_lift_smoke_note",
    "build_lift_smoke_payload",
    "write_lift_smoke_outputs",
]
