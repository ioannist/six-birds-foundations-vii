from __future__ import annotations

from fractions import Fraction
from typing import Any


def strip_completion_sensitive_signature(
    signature: Any,
) -> Any:
    if isinstance(signature, dict):
        cleaned: dict[str, Any] = {}
        for key, value in signature.items():
            if key in {"family_id", "event_package_id"}:
                continue
            if key == "observable_ids" and isinstance(value, list):
                cleaned[key] = [
                    item for item in value if item != "relative_cycle_completion_bins"
                ]
                continue
            if key == "distributions" and isinstance(value, list):
                cleaned[key] = [
                    strip_completion_sensitive_signature(item)
                    for item in value
                    if not _distribution_is_completion_bins(item)
                ]
                continue
            cleaned[key] = strip_completion_sensitive_signature(value)
        return cleaned
    if isinstance(signature, list):
        return [strip_completion_sensitive_signature(item) for item in signature]
    return signature


def predictive_signature_repr(signature: Any) -> str:
    return repr(signature)


def candidate_weight_profile(candidate: Any) -> tuple[int, Fraction, str]:
    branch_member_count = candidate.branch_member_count or 0
    max_member_weight = Fraction(candidate.max_member_weight or "0")
    return (
        branch_member_count,
        max_member_weight,
        candidate.candidate_id,
    )


def parse_class_reference_parameters(
    strategy_parameters: dict[str, Any],
    *,
    strategy_id: str,
    class_id: str,
) -> dict[str, Any] | None:
    payload = strategy_parameters.get(strategy_id)
    if not isinstance(payload, dict):
        return None
    per_class = payload.get("per_class")
    if not isinstance(per_class, dict):
        return None
    class_payload = per_class.get(class_id)
    if not isinstance(class_payload, dict):
        return None
    return class_payload


def _distribution_is_completion_bins(distribution: Any) -> bool:
    if not isinstance(distribution, dict):
        return False
    probabilities = distribution.get("probabilities")
    if not isinstance(probabilities, dict):
        return False
    keys = set(probabilities)
    return keys == {"completion_high", "completion_low"}


__all__ = [
    "candidate_weight_profile",
    "parse_class_reference_parameters",
    "predictive_signature_repr",
    "strip_completion_sensitive_signature",
]
