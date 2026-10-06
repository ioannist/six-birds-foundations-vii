from __future__ import annotations

from typing import Any

from .models import ExtensionAuditRow, ExtensionAuditStatus, ExtensionAuditZone
from .moves import apply_extension_move


NON_FACTORIZATION_CHECK = "non_factorization_check"
MACRO_ADMISSIBILITY_OBSTRUCTION_CHECK = "macro_admissibility_obstruction_check"
INTERNAL_CARRIER_FAILURE_ZONE_CHECK = "internal_carrier_failure_zone_check"


def list_obstruction_check_ids() -> list[str]:
    return [
        NON_FACTORIZATION_CHECK,
        MACRO_ADMISSIBILITY_OBSTRUCTION_CHECK,
        INTERNAL_CARRIER_FAILURE_ZONE_CHECK,
    ]


def evaluate_obstruction_check(
    zone: ExtensionAuditZone,
    *,
    extension_move_id: str,
    obstruction_check_id: str,
) -> ExtensionAuditRow:
    if zone.artifact_excluded:
        return ExtensionAuditRow(
            zone_id=zone.zone_id,
            source_kind=zone.source_kind,
            extension_move_id=extension_move_id,
            obstruction_check_id=obstruction_check_id,
            status=ExtensionAuditStatus.ARTIFACT_CONTEXT_EXCLUDED,
            baseline_status="artifact_context_excluded",
            extended_status="artifact_context_excluded",
            obstruction_flag=None,
            resolution_flag=None,
            evidence={},
            provenance={"artifact_exclusion_reason": zone.artifact_exclusion_reason},
            warnings=[],
            details={
                "budget_context_status": zone.budget_context_status.value,
                "extension_surface_id": zone.extension_surface_id,
            },
        )

    baseline = dict(zone.baseline_semantics)
    extended, move_warnings = apply_extension_move(zone, extension_move_id)
    move_alignment = str((extended or {}).get("move_alignment", "unspecified"))
    if extended is None:
        return ExtensionAuditRow(
            zone_id=zone.zone_id,
            source_kind=zone.source_kind,
            extension_move_id=extension_move_id,
            obstruction_check_id=obstruction_check_id,
            status=ExtensionAuditStatus.UNSUPPORTED,
            baseline_status="baseline_available",
            extended_status="move_unsupported",
            obstruction_flag=None,
            resolution_flag=None,
            evidence={},
            provenance={"move_supported": False},
            warnings=move_warnings,
            details={
                "budget_context_status": zone.budget_context_status.value,
                "move_alignment": "unsupported",
                "extension_surface_id": zone.extension_surface_id,
            },
        )

    if obstruction_check_id == NON_FACTORIZATION_CHECK:
        return _evaluate_non_factorization(zone, extension_move_id, baseline, extended, move_warnings)
    if obstruction_check_id == MACRO_ADMISSIBILITY_OBSTRUCTION_CHECK:
        return _evaluate_macro_obstruction(zone, extension_move_id, baseline, extended, move_warnings)
    if obstruction_check_id == INTERNAL_CARRIER_FAILURE_ZONE_CHECK:
        return _evaluate_internal_carrier_failure(zone, extension_move_id, baseline, extended, move_warnings)
    raise KeyError(obstruction_check_id)


def _evaluate_non_factorization(
    zone: ExtensionAuditZone,
    extension_move_id: str,
    baseline: dict[str, Any],
    extended: dict[str, Any],
    move_warnings: list[str],
) -> ExtensionAuditRow:
    baseline_inputs = _resolve_factorization_inputs(baseline)
    extended_inputs = _resolve_factorization_inputs(extended)
    move_alignment = str(extended.get("move_alignment", "unspecified"))
    extension_surface_id = str(extended.get("extension_surface_id", zone.extension_surface_id))
    if not _has_factorization_inputs(baseline_inputs) or not _has_factorization_inputs(extended_inputs):
        return ExtensionAuditRow(
            zone_id=zone.zone_id,
            source_kind=zone.source_kind,
            extension_move_id=extension_move_id,
            obstruction_check_id=NON_FACTORIZATION_CHECK,
            status=ExtensionAuditStatus.UNSUPPORTED,
            baseline_status="missing_factorization_inputs",
            extended_status="missing_factorization_inputs",
            obstruction_flag=None,
            resolution_flag=None,
            evidence={},
            provenance={"support_cone_id": zone.support_cone_id},
            warnings=move_warnings + ["non-factorization check requires object_map and observable_signatures"],
            details={
                "budget_context_status": zone.budget_context_status.value,
                "move_alignment": move_alignment,
                "extension_surface_id": extension_surface_id,
            },
        )
    baseline_ok, baseline_evidence = _factors_through_object_map(baseline_inputs)
    extended_ok, extended_evidence = _factors_through_object_map(extended_inputs)
    return ExtensionAuditRow(
        zone_id=zone.zone_id,
        source_kind=zone.source_kind,
        extension_move_id=extension_move_id,
        obstruction_check_id=NON_FACTORIZATION_CHECK,
        status=ExtensionAuditStatus.OK,
        baseline_status="factorable" if baseline_ok else "nonfactorizable",
        extended_status="factorable" if extended_ok else "nonfactorizable",
        obstruction_flag=not baseline_ok,
        resolution_flag=(not baseline_ok) and extended_ok,
        evidence={
            "baseline": baseline_evidence,
            "extended": extended_evidence,
        },
        provenance={"support_cone_id": zone.support_cone_id},
        warnings=move_warnings,
        details={
            "budget_context_status": zone.budget_context_status.value,
            "move_alignment": move_alignment,
            "extension_surface_id": extension_surface_id,
        },
    )


def _evaluate_macro_obstruction(
    zone: ExtensionAuditZone,
    extension_move_id: str,
    baseline: dict[str, Any],
    extended: dict[str, Any],
    move_warnings: list[str],
) -> ExtensionAuditRow:
    baseline_inputs = _resolve_macro_inputs(baseline)
    extended_inputs = _resolve_macro_inputs(extended)
    move_alignment = str(extended.get("move_alignment", "unspecified"))
    extension_surface_id = str(extended.get("extension_surface_id", zone.extension_surface_id))
    if not _has_macro_inputs(baseline_inputs) or not _has_macro_inputs(extended_inputs):
        return ExtensionAuditRow(
            zone_id=zone.zone_id,
            source_kind=zone.source_kind,
            extension_move_id=extension_move_id,
            obstruction_check_id=MACRO_ADMISSIBILITY_OBSTRUCTION_CHECK,
            status=ExtensionAuditStatus.UNSUPPORTED,
            baseline_status="missing_macro_inputs",
            extended_status="missing_macro_inputs",
            obstruction_flag=None,
            resolution_flag=None,
            evidence={},
            provenance={"support_cone_id": zone.support_cone_id},
            warnings=move_warnings + ["macro-admissibility check requires object_map and successor_labels"],
            details={
                "budget_context_status": zone.budget_context_status.value,
                "move_alignment": move_alignment,
                "extension_surface_id": extension_surface_id,
            },
        )
    baseline_ok, baseline_evidence = _admits_macro_successor_law(baseline_inputs)
    extended_ok, extended_evidence = _admits_macro_successor_law(extended_inputs)
    return ExtensionAuditRow(
        zone_id=zone.zone_id,
        source_kind=zone.source_kind,
        extension_move_id=extension_move_id,
        obstruction_check_id=MACRO_ADMISSIBILITY_OBSTRUCTION_CHECK,
        status=ExtensionAuditStatus.OK,
        baseline_status="macro_admissible" if baseline_ok else "macro_obstructed",
        extended_status="macro_admissible" if extended_ok else "macro_obstructed",
        obstruction_flag=not baseline_ok,
        resolution_flag=(not baseline_ok) and extended_ok,
        evidence={
            "baseline": baseline_evidence,
            "extended": extended_evidence,
        },
        provenance={"support_cone_id": zone.support_cone_id},
        warnings=move_warnings,
        details={
            "budget_context_status": zone.budget_context_status.value,
            "move_alignment": move_alignment,
            "extension_surface_id": extension_surface_id,
        },
    )


def _evaluate_internal_carrier_failure(
    zone: ExtensionAuditZone,
    extension_move_id: str,
    baseline: dict[str, Any],
    extended: dict[str, Any],
    move_warnings: list[str],
) -> ExtensionAuditRow:
    baseline_signal = str(baseline.get("internal_carrier_signal", "unknown"))
    extended_signal = str(extended.get("internal_carrier_signal", baseline_signal))
    move_alignment = str(extended.get("move_alignment", "unspecified"))
    extension_surface_id = str(extended.get("extension_surface_id", zone.extension_surface_id))

    if baseline_signal == "unknown" and zone.zone_category.value == "benchmark_context":
        return ExtensionAuditRow(
            zone_id=zone.zone_id,
            source_kind=zone.source_kind,
            extension_move_id=extension_move_id,
            obstruction_check_id=INTERNAL_CARRIER_FAILURE_ZONE_CHECK,
            status=ExtensionAuditStatus.INSUFFICIENT_SUPPORT,
            baseline_status="unknown",
            extended_status="unknown",
            obstruction_flag=None,
            resolution_flag=None,
            evidence={"upstream_evidence": zone.upstream_evidence},
            provenance={"support_cone_id": zone.support_cone_id},
            warnings=move_warnings + ["benchmark context lacks explicit internal-carrier failure signal"],
            details={
                "budget_context_status": zone.budget_context_status.value,
                "move_alignment": move_alignment,
                "extension_surface_id": extension_surface_id,
            },
        )

    baseline_obstruction = baseline_signal in {"weak", "unsupported"}
    extended_resolved = extended_signal in {"adequate", "resolved"}
    return ExtensionAuditRow(
        zone_id=zone.zone_id,
        source_kind=zone.source_kind,
        extension_move_id=extension_move_id,
        obstruction_check_id=INTERNAL_CARRIER_FAILURE_ZONE_CHECK,
        status=ExtensionAuditStatus.OK,
        baseline_status=baseline_signal,
        extended_status=extended_signal,
        obstruction_flag=baseline_obstruction,
        resolution_flag=baseline_obstruction and extended_resolved,
        evidence={"upstream_evidence": zone.upstream_evidence},
        provenance={"support_cone_id": zone.support_cone_id},
        warnings=move_warnings,
        details={
            "budget_context_status": zone.budget_context_status.value,
            "move_alignment": move_alignment,
            "extension_surface_id": extension_surface_id,
        },
    )


def _factors_through_object_map(semantics: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    object_map = dict(semantics.get("object_map", {}))
    observable_signatures = dict(semantics.get("observable_signatures", {}))
    if not object_map or not observable_signatures:
        return False, {"reason": "missing_object_map_or_observable_signatures"}
    signatures_by_class: dict[str, set[str]] = {}
    for object_id, class_id in object_map.items():
        signature = observable_signatures.get(object_id)
        if signature is None:
            return False, {"reason": "missing_signature", "object_id": object_id}
        signatures_by_class.setdefault(class_id, set()).add(signature)
    witness_classes = {
        class_id: sorted(signatures)
        for class_id, signatures in signatures_by_class.items()
        if len(signatures) > 1
    }
    return not witness_classes, {
        "signature_classes": {
            class_id: sorted(signatures)
            for class_id, signatures in sorted(signatures_by_class.items())
        },
        "witness_classes": witness_classes,
    }


def _admits_macro_successor_law(semantics: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    object_map = dict(semantics.get("object_map", {}))
    successor_labels = dict(semantics.get("successor_labels", {}))
    successor_signatures = dict(semantics.get("successor_signatures", {}))
    if not object_map or (not successor_labels and not successor_signatures):
        return False, {"reason": "missing_object_map_or_successor_structure"}
    if successor_signatures:
        successor_classes_by_class: dict[str, set[str]] = {}
        for object_id, class_id in object_map.items():
            signature = successor_signatures.get(object_id)
            if signature is None:
                return False, {"reason": "missing_successor_signature", "object_id": object_id}
            successor_classes_by_class.setdefault(class_id, set()).add(repr(signature))
        witness_classes = {
            class_id: sorted(targets)
            for class_id, targets in successor_classes_by_class.items()
            if len(targets) > 1
        }
        return not witness_classes, {
            "successor_signatures_by_class": {
                class_id: sorted(targets)
                for class_id, targets in sorted(successor_classes_by_class.items())
            },
            "witness_classes": witness_classes,
            "mode": "successor_signatures",
        }
    successor_classes_by_class: dict[str, set[str]] = {}
    for object_id, class_id in object_map.items():
        successor_object = successor_labels.get(object_id)
        if successor_object is None:
            return False, {"reason": "missing_successor_label", "object_id": object_id}
        successor_class = object_map.get(successor_object)
        if successor_class is None:
            return False, {"reason": "successor_outside_object_map", "object_id": object_id}
        successor_classes_by_class.setdefault(class_id, set()).add(successor_class)
    witness_classes = {
        class_id: sorted(targets)
        for class_id, targets in successor_classes_by_class.items()
        if len(targets) > 1
    }
    return not witness_classes, {
        "successor_classes_by_class": {
            class_id: sorted(targets)
            for class_id, targets in sorted(successor_classes_by_class.items())
        },
        "witness_classes": witness_classes,
        "mode": "successor_labels",
    }


def _has_factorization_inputs(semantics: dict[str, Any]) -> bool:
    return bool(semantics.get("object_map")) and bool(semantics.get("observable_signatures"))


def _has_macro_inputs(semantics: dict[str, Any]) -> bool:
    return bool(semantics.get("object_map")) and bool(
        semantics.get("successor_labels") or semantics.get("successor_signatures")
    )


def _resolve_factorization_inputs(semantics: dict[str, Any]) -> dict[str, Any]:
    nested = semantics.get("factorization_inputs")
    if isinstance(nested, dict):
        return dict(nested)
    return {
        "object_map": semantics.get("object_map", {}),
        "observable_signatures": semantics.get("observable_signatures", {}),
    }


def _resolve_macro_inputs(semantics: dict[str, Any]) -> dict[str, Any]:
    nested = semantics.get("macro_inputs")
    if isinstance(nested, dict):
        return dict(nested)
    return {
        "object_map": semantics.get("object_map", {}),
        "successor_labels": semantics.get("successor_labels", {}),
        "successor_signatures": semantics.get("successor_signatures", {}),
    }


__all__ = [
    "INTERNAL_CARRIER_FAILURE_ZONE_CHECK",
    "MACRO_ADMISSIBILITY_OBSTRUCTION_CHECK",
    "NON_FACTORIZATION_CHECK",
    "evaluate_obstruction_check",
    "list_obstruction_check_ids",
]
