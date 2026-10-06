from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PairedRunComparison:
    payload: dict[str, Any]

    @property
    def supports_erasure_recovery(self) -> bool:
        return bool(self.payload["supports_erasure_recovery"])

    @property
    def viable_flagship_example(self) -> bool:
        return bool(self.payload["viable_flagship_example"])

    @property
    def verdict(self) -> str:
        return str(self.payload["verdict"])


@dataclass(frozen=True)
class ProtocolInternalizationComparison:
    payload: dict[str, Any]

    @property
    def artifact_exposed(self) -> bool:
        return bool(self.payload["artifact_exposed"])

    @property
    def verdict(self) -> str:
        return str(self.payload["verdict"])


@dataclass(frozen=True)
class ProtocolRecoveryComparison:
    payload: dict[str, Any]

    @property
    def supports_protocol_recovery(self) -> bool:
        return bool(self.payload["supports_protocol_recovery"])

    @property
    def verdict(self) -> str:
        return str(self.payload["verdict"])


@dataclass(frozen=True)
class FlatteningCompletionComparison:
    payload: dict[str, Any]

    @property
    def survives_flattening_completion(self) -> bool:
        return bool(self.payload["survives_flattening_completion"])

    @property
    def verdict(self) -> str:
        return str(self.payload["verdict"])


def build_paired_marked_comparison(
    *,
    marked_run_id: str,
    erased_run_id: str,
    marked_summary_path: Path,
    erased_summary_path: Path,
) -> PairedRunComparison:
    marked = _load_recovery_metrics(marked_run_id, marked_summary_path)
    erased = _load_recovery_metrics(erased_run_id, erased_summary_path)

    supports_erasure_recovery = (
        erased["route_readability_score"] < marked["route_readability_score"]
        and erased["visibility_recovery_gap"] > 0
        and erased["max_conditional_visibility"] > erased["unconditional_visibility"]
    )
    viable_flagship_example = (
        supports_erasure_recovery
        and erased["recombination_quotient_size"] > erased["branchwise_quotient_size"]
        and erased["eta_max_fiber_size"] > 1
        and erased["recombination_gap_value"] > 0
        and erased["factorization_status"] == "failed"
    )
    if viable_flagship_example:
        verdict = "strong_erasure_recovery_flagship"
    elif supports_erasure_recovery:
        verdict = "partial_erasure_recovery_not_flagship"
    else:
        verdict = "no_erasure_recovery"

    return PairedRunComparison(
        payload={
            "marked_run_id": marked_run_id,
            "erased_run_id": erased_run_id,
            "marked_benchmark_id": marked["benchmark_id"],
            "erased_benchmark_id": erased["benchmark_id"],
            "route_readability_score_marked": str(marked["route_readability_score"]),
            "route_readability_score_erased": str(erased["route_readability_score"]),
            "route_readability_delta": str(
                erased["route_readability_score"] - marked["route_readability_score"]
            ),
            "raw_success_probability_marked": str(marked["raw_success_probability"]),
            "raw_success_probability_erased": str(erased["raw_success_probability"]),
            "unconditional_visibility_marked": str(marked["unconditional_visibility"]),
            "unconditional_visibility_erased": str(erased["unconditional_visibility"]),
            "max_conditional_visibility_marked": str(marked["max_conditional_visibility"]),
            "max_conditional_visibility_erased": str(erased["max_conditional_visibility"]),
            "visibility_recovery_gap_marked": str(marked["visibility_recovery_gap"]),
            "visibility_recovery_gap_erased": str(erased["visibility_recovery_gap"]),
            "branchwise_quotient_size_marked": marked["branchwise_quotient_size"],
            "branchwise_quotient_size_erased": erased["branchwise_quotient_size"],
            "recombination_quotient_size_marked": marked["recombination_quotient_size"],
            "recombination_quotient_size_erased": erased["recombination_quotient_size"],
            "eta_max_fiber_size_marked": marked["eta_max_fiber_size"],
            "eta_max_fiber_size_erased": erased["eta_max_fiber_size"],
            "recombination_gap_value_marked": str(marked["recombination_gap_value"]),
            "recombination_gap_value_erased": str(erased["recombination_gap_value"]),
            "factorization_status_marked": marked["factorization_status"],
            "factorization_status_erased": erased["factorization_status"],
            "class_label_marked": marked["class_label"],
            "class_label_erased": erased["class_label"],
            "supports_erasure_recovery": supports_erasure_recovery,
            "viable_flagship_example": viable_flagship_example,
            "verdict": verdict,
        }
    )


def build_protocol_internalization_comparison(
    *,
    uninternalized_run_id: str,
    internalized_run_id: str,
    uninternalized_summary_path: Path,
    internalized_summary_path: Path,
) -> ProtocolInternalizationComparison:
    uninternalized_summary = _load_json(uninternalized_summary_path)
    internalized_summary = _load_json(internalized_summary_path)
    uninternalized_manifest = _load_manifest(uninternalized_run_id, uninternalized_summary_path)
    internalized_manifest = _load_manifest(internalized_run_id, internalized_summary_path)
    uninternalized_record = _first_record(uninternalized_manifest)
    internalized_record = _first_record(internalized_manifest)

    recombination_gap_value_uninternalized = _fraction_from_path(
        uninternalized_summary,
        "recombination_gap",
        "metric_value",
    )
    recombination_gap_value_internalized = _fraction_from_path(
        internalized_summary,
        "recombination_gap",
        "metric_value",
    )
    branchwise_quotient_size_uninternalized = int(
        uninternalized_summary["branchwise_quotient"]["class_count"]
    )
    branchwise_quotient_size_internalized = int(
        internalized_summary["branchwise_quotient"]["class_count"]
    )
    recombination_quotient_size_uninternalized = int(
        uninternalized_summary["recombination_quotient"]["r_class_count"]
    )
    recombination_quotient_size_internalized = int(
        internalized_summary["recombination_quotient"]["r_class_count"]
    )
    eta_max_fiber_size_uninternalized = int(
        uninternalized_summary["eta_fiber"]["eta_max_fiber_size"]
    )
    eta_max_fiber_size_internalized = int(
        internalized_summary["eta_fiber"]["eta_max_fiber_size"]
    )
    protocol_internalization_status_uninternalized = str(
        uninternalized_record["internalization_status"]
    )
    protocol_internalization_status_internalized = str(
        internalized_record["internalization_status"]
    )
    class_label_uninternalized = str(uninternalized_record["class_label"])
    class_label_internalized = str(internalized_record["class_label"])

    apparent_positive_uninternalized = (
        recombination_quotient_size_uninternalized > branchwise_quotient_size_uninternalized
        and eta_max_fiber_size_uninternalized > 1
        and recombination_gap_value_uninternalized > 0
    )
    removed_or_reclassified = (
        recombination_gap_value_internalized < recombination_gap_value_uninternalized
        or recombination_quotient_size_internalized < recombination_quotient_size_uninternalized
        or class_label_internalized != class_label_uninternalized
    )
    artifact_exposed = (
        protocol_internalization_status_uninternalized == "failed"
        and protocol_internalization_status_internalized == "passed"
        and apparent_positive_uninternalized
        and removed_or_reclassified
    )
    verdict = (
        "artifact_exposed_by_internalization"
        if artifact_exposed
        else "artifact_not_exposed_by_internalization"
    )

    return ProtocolInternalizationComparison(
        payload={
            "uninternalized_run_id": uninternalized_run_id,
            "internalized_run_id": internalized_run_id,
            "benchmark_id_uninternalized": uninternalized_summary["benchmark_id"],
            "benchmark_id_internalized": internalized_summary["benchmark_id"],
            "current_quotient_size_uninternalized": int(
                uninternalized_summary["inherited_analysis"]["current_quotient_size"]
            ),
            "predictive_quotient_size_uninternalized": int(
                uninternalized_summary["inherited_analysis"]["predictive_quotient_size"]
            ),
            "branchwise_quotient_size_uninternalized": branchwise_quotient_size_uninternalized,
            "recombination_quotient_size_uninternalized": recombination_quotient_size_uninternalized,
            "eta_max_fiber_size_uninternalized": eta_max_fiber_size_uninternalized,
            "recombination_gap_value_uninternalized": str(recombination_gap_value_uninternalized),
            "class_label_uninternalized": class_label_uninternalized,
            "protocol_internalization_status_uninternalized": protocol_internalization_status_uninternalized,
            "current_quotient_size_internalized": int(
                internalized_summary["inherited_analysis"]["current_quotient_size"]
            ),
            "predictive_quotient_size_internalized": int(
                internalized_summary["inherited_analysis"]["predictive_quotient_size"]
            ),
            "branchwise_quotient_size_internalized": branchwise_quotient_size_internalized,
            "recombination_quotient_size_internalized": recombination_quotient_size_internalized,
            "eta_max_fiber_size_internalized": eta_max_fiber_size_internalized,
            "recombination_gap_value_internalized": str(recombination_gap_value_internalized),
            "class_label_internalized": class_label_internalized,
            "protocol_internalization_status_internalized": protocol_internalization_status_internalized,
            "artifact_exposed": artifact_exposed,
            "verdict": verdict,
        }
    )


def build_protocol_recovery_comparison(
    *,
    uninternalized_run_id: str,
    internalized_run_id: str,
    erased_run_id: str,
    uninternalized_summary_path: Path,
    internalized_summary_path: Path,
    erased_summary_path: Path,
) -> ProtocolRecoveryComparison:
    uninternalized = _load_recovery_metrics(uninternalized_run_id, uninternalized_summary_path)
    internalized = _load_recovery_metrics(internalized_run_id, internalized_summary_path)
    erased = _load_recovery_metrics(erased_run_id, erased_summary_path)

    apparent_positive_uninternalized = _is_positive_signal(uninternalized)
    suppressed_internalized = (
        internalized["recombination_gap_value"] < uninternalized["recombination_gap_value"]
        or internalized["recombination_quotient_size"] < uninternalized["recombination_quotient_size"]
        or internalized["class_label"] != uninternalized["class_label"]
    )
    readability_erased_again = (
        internalized["protocol_internalization_status"] == "passed"
        and erased["route_readability_score"] == 0
        and erased["visibility_recovery_gap"] > 0
        and erased["max_conditional_visibility"] > erased["unconditional_visibility"]
    )
    recovered_erased = _is_positive_signal(erased)
    supports_protocol_recovery = (
        apparent_positive_uninternalized and suppressed_internalized and readability_erased_again and recovered_erased
    )
    if supports_protocol_recovery:
        verdict = "protocol_recovery_present"
    elif apparent_positive_uninternalized and suppressed_internalized and not recovered_erased:
        verdict = "artifact_only"
    elif suppressed_internalized:
        verdict = "suppressed_without_recovery"
    else:
        verdict = "no_protocol_recovery_signal"

    payload = {
        "uninternalized_run_id": uninternalized_run_id,
        "internalized_run_id": internalized_run_id,
        "erased_run_id": erased_run_id,
        "benchmark_id_uninternalized": uninternalized["benchmark_id"],
        "benchmark_id_internalized": internalized["benchmark_id"],
        "benchmark_id_erased": erased["benchmark_id"],
        "supports_protocol_recovery": supports_protocol_recovery,
        "apparent_positive_uninternalized": apparent_positive_uninternalized,
        "suppressed_internalized": suppressed_internalized,
        "readability_erased_again": readability_erased_again,
        "recovered_erased": recovered_erased,
        "verdict": verdict,
    }
    for stage_name, stage_metrics in (
        ("uninternalized", uninternalized),
        ("internalized", internalized),
        ("erased", erased),
    ):
        for field_name, value in stage_metrics.items():
            if field_name in {"benchmark_id"}:
                continue
            payload[f"{field_name}_{stage_name}"] = str(value) if isinstance(value, Fraction) else value
    return ProtocolRecoveryComparison(payload=payload)


def build_flattening_completion_comparison(
    *,
    reference_positive_run_id: str,
    completion_partner_run_id: str,
    reference_summary_path: Path,
    completion_partner_summary_path: Path,
    candidate_case_id: str,
) -> FlatteningCompletionComparison:
    reference_summary = _load_json(reference_summary_path)
    completion_summary = _load_json(completion_partner_summary_path)
    reference_manifest = _load_manifest(reference_positive_run_id, reference_summary_path)
    completion_manifest = _load_manifest(
        completion_partner_run_id,
        completion_partner_summary_path,
    )
    reference_record = _first_record(reference_manifest)
    completion_record = _first_record(completion_manifest)

    branchwise_quotient_size_reference = int(reference_summary["branchwise_quotient"]["class_count"])
    branchwise_quotient_size_completion = int(completion_summary["branchwise_quotient"]["class_count"])
    recombination_quotient_size_reference = int(
        reference_summary["recombination_quotient"]["r_class_count"]
    )
    recombination_quotient_size_completion = int(
        completion_summary["recombination_quotient"]["r_class_count"]
    )
    eta_max_fiber_size_reference = int(reference_summary["eta_fiber"]["eta_max_fiber_size"])
    eta_max_fiber_size_completion = int(completion_summary["eta_fiber"]["eta_max_fiber_size"])
    recombination_gap_value_reference = _fraction_from_path(
        reference_summary,
        "recombination_gap",
        "metric_value",
    )
    recombination_gap_value_completion = _fraction_from_path(
        completion_summary,
        "recombination_gap",
        "metric_value",
    )
    flattening_status_reference = str(reference_record["flattening_status"])
    flattening_status_completion = str(completion_record["flattening_status"])
    class_label_reference = str(reference_record["class_label"])
    class_label_completion = str(completion_record["class_label"])

    survives_flattening_completion = (
        recombination_quotient_size_reference > branchwise_quotient_size_reference
        and eta_max_fiber_size_reference > 1
        and recombination_gap_value_reference > 0
        and recombination_quotient_size_completion > branchwise_quotient_size_completion
        and eta_max_fiber_size_completion > 1
        and recombination_gap_value_completion > 0
    )
    verdict = (
        "candidate_survives_flattening_completion"
        if survives_flattening_completion
        else "candidate_does_not_survive_flattening_completion"
    )
    return FlatteningCompletionComparison(
        payload={
            "candidate_case_id": candidate_case_id,
            "reference_positive_run_id": reference_positive_run_id,
            "completion_partner_run_id": completion_partner_run_id,
            "branchwise_quotient_size_reference": branchwise_quotient_size_reference,
            "recombination_quotient_size_reference": recombination_quotient_size_reference,
            "eta_max_fiber_size_reference": eta_max_fiber_size_reference,
            "recombination_gap_value_reference": str(recombination_gap_value_reference),
            "class_label_reference": class_label_reference,
            "flattening_status_reference": flattening_status_reference,
            "branchwise_quotient_size_completion_partner": branchwise_quotient_size_completion,
            "recombination_quotient_size_completion_partner": recombination_quotient_size_completion,
            "eta_max_fiber_size_completion_partner": eta_max_fiber_size_completion,
            "recombination_gap_value_completion_partner": str(recombination_gap_value_completion),
            "class_label_completion_partner": class_label_completion,
            "flattening_status_completion_partner": flattening_status_completion,
            "survives_flattening_completion": survives_flattening_completion,
            "verdict": verdict,
        }
    )


def _is_positive_signal(metrics: dict[str, Any]) -> bool:
    return (
        metrics["recombination_quotient_size"] > metrics["branchwise_quotient_size"]
        and metrics["eta_max_fiber_size"] > 1
        and metrics["recombination_gap_value"] > 0
        and metrics["factorization_status"] == "failed"
    )


def _load_recovery_metrics(run_id: str, summary_path: Path) -> dict[str, Any]:
    summary = _load_json(summary_path)
    manifest = _load_manifest(run_id, summary_path)
    record = _first_record(manifest)
    return {
        "benchmark_id": str(summary["benchmark_id"]),
        "route_readability_score": _fraction_from_path(summary, "route_readability", "score_value"),
        "raw_success_probability": _fraction_from_path(
            summary,
            "route_readability",
            "raw_success_probability",
        ),
        "unconditional_visibility": _fraction_from_path(
            summary,
            "conditional_visibility",
            "unconditional_visibility",
        ),
        "max_conditional_visibility": _fraction_from_path(
            summary,
            "conditional_visibility",
            "max_conditional_visibility",
        ),
        "visibility_recovery_gap": _fraction_from_path(
            summary,
            "conditional_visibility",
            "visibility_recovery_gap",
        ),
        "current_quotient_size": int(summary["inherited_analysis"]["current_quotient_size"]),
        "predictive_quotient_size": int(summary["inherited_analysis"]["predictive_quotient_size"]),
        "branchwise_quotient_size": int(summary["branchwise_quotient"]["class_count"]),
        "recombination_quotient_size": int(summary["recombination_quotient"]["r_class_count"]),
        "eta_max_fiber_size": int(summary["eta_fiber"]["eta_max_fiber_size"]),
        "recombination_gap_value": _fraction_from_path(summary, "recombination_gap", "metric_value"),
        "factorization_status": str(summary["factorization"]["status"]),
        "protocol_internalization_status": str(record["internalization_status"]),
        "class_label": str(record["class_label"]),
    }


def _load_class_label(run_id: str, summary_path: Path) -> str:
    manifest = _load_manifest(run_id, summary_path)
    records = manifest.get("records", [])
    if not records:
        raise ValueError(f"result manifest for {run_id} does not contain any records")
    return str(records[0]["class_label"])


def _load_manifest(run_id: str, summary_path: Path) -> dict[str, Any]:
    output_root = summary_path.parents[3]
    manifest_path = output_root / "results" / "raw" / run_id / "result_manifest.json"
    return _load_json(manifest_path)


def _first_record(manifest: dict[str, Any]) -> dict[str, Any]:
    records = manifest.get("records", [])
    if not records:
        raise ValueError("result manifest does not contain any records")
    return records[0]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fraction_from_path(payload: dict[str, Any], *keys: str) -> Fraction:
    value: Any = payload
    for key in keys:
        value = value[key]
    return Fraction(str(value))


__all__ = [
    "FlatteningCompletionComparison",
    "PairedRunComparison",
    "ProtocolRecoveryComparison",
    "ProtocolInternalizationComparison",
    "build_flattening_completion_comparison",
    "build_paired_marked_comparison",
    "build_protocol_recovery_comparison",
    "build_protocol_internalization_comparison",
]
