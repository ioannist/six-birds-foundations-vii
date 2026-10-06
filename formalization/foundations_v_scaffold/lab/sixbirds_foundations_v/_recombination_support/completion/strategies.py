from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Protocol

from .framework import (
    CompletionCandidate,
    CompletionClassSurface,
    CompletionRequest,
)
from .ticket27_support import (
    candidate_weight_profile,
    parse_class_reference_parameters,
    predictive_signature_repr,
    strip_completion_sensitive_signature,
)


@dataclass(frozen=True)
class StrategySelection:
    selected_candidate_id: str
    tie_break_rule: str
    score_summary: dict[str, Any]
    fallback_used: str | None = None


class CompletionStrategy(Protocol):
    def __call__(
        self,
        completion_class: CompletionClassSurface,
        request: CompletionRequest,
    ) -> StrategySelection: ...


def identity_reference_strategy(
    completion_class: CompletionClassSurface,
    request: CompletionRequest,
) -> StrategySelection:
    del request
    selected_candidate_id = completion_class.default_representative_id
    return StrategySelection(
        selected_candidate_id=selected_candidate_id,
        tie_break_rule="use the canonical representative already exposed by the source result",
        score_summary={
            "selection_basis": "source_default_representative",
            "default_representative_id": selected_candidate_id,
        },
    )


def max_weight_representative_strategy(
    completion_class: CompletionClassSurface,
    request: CompletionRequest,
) -> StrategySelection:
    del request
    weighted_candidates: list[tuple[Fraction, Fraction, str, CompletionCandidate]] = []
    for candidate in completion_class.candidates:
        if candidate.max_member_weight is None:
            raise ValueError(
                f"class {completion_class.class_id} does not expose max_member_weight"
            )
        max_weight = Fraction(candidate.max_member_weight)
        total_weight = Fraction(candidate.total_weight or candidate.max_member_weight)
        weighted_candidates.append(
            (
                max_weight,
                total_weight,
                candidate.candidate_id,
                candidate,
            )
        )
    if not weighted_candidates:
        raise ValueError(f"class {completion_class.class_id} has no candidates")

    weighted_candidates.sort(
        key=lambda item: (
            -item[0],
            -item[1],
            item[2],
        )
    )
    max_weight, total_weight, _, candidate = weighted_candidates[0]
    return StrategySelection(
        selected_candidate_id=candidate.candidate_id,
        tie_break_rule=(
            "maximize max_member_weight, then total_weight, then candidate_id"
        ),
        score_summary={
            "selection_basis": "max_member_weight",
            "max_member_weight": str(max_weight),
            "total_weight": str(total_weight),
        },
    )


def predictive_signature_canonical_strategy(
    completion_class: CompletionClassSurface,
    request: CompletionRequest,
) -> StrategySelection:
    del request
    if not completion_class.candidates:
        raise ValueError(f"class {completion_class.class_id} has no candidates")

    ranked = sorted(completion_class.candidates, key=_predictive_canonical_sort_key)
    chosen = ranked[0]
    return StrategySelection(
        selected_candidate_id=chosen.candidate_id,
        tie_break_rule=(
            "prefer the richest lower-state predictive decomposition, then canonical signature, then candidate_id"
        ),
        score_summary={
            "selection_basis": "predictive_signature_canonical",
            "candidate_id": chosen.candidate_id,
            "signature_key": chosen.predictive_signature_key,
            "branch_member_count": chosen.branch_member_count,
        },
    )


def completion_preserving_strategy(
    completion_class: CompletionClassSurface,
    request: CompletionRequest,
) -> StrategySelection:
    class_reference = parse_class_reference_parameters(
        request.strategy_parameters,
        strategy_id="completion_preserving",
        class_id=completion_class.class_id,
    )
    if class_reference is None:
        fallback = predictive_signature_canonical_strategy(completion_class, request)
        return StrategySelection(
            selected_candidate_id=fallback.selected_candidate_id,
            tie_break_rule=fallback.tie_break_rule,
            score_summary={
                **fallback.score_summary,
                "selection_basis": "completion_preserving_fallback",
                "completion_signal_used": False,
                "fallback_reason": "no_partner_completion_reference",
            },
            fallback_used="no_partner_completion_reference",
        )

    partner_signature = class_reference.get("partner_normalized_signature")
    ranked = []
    for candidate in completion_class.candidates:
        normalized_signature = strip_completion_sensitive_signature(
            candidate.candidate_signature
        )
        exact_match = normalized_signature == partner_signature
        ranked.append(
            (
                0 if exact_match else 1,
                -(candidate.branch_member_count or 0),
                -Fraction(candidate.max_member_weight or "0"),
                predictive_signature_repr(candidate.predictive_signature_key),
                candidate.candidate_id,
                candidate,
                exact_match,
                normalized_signature,
            )
        )
    ranked.sort(key=lambda item: item[:-3])
    _, _, _, _, _, chosen, exact_match, normalized_signature = ranked[0]
    return StrategySelection(
        selected_candidate_id=chosen.candidate_id,
        tie_break_rule=(
            "prefer exact normalized paired-partner signature match, then richer predictive decomposition, then max_member_weight, then canonical signature, then candidate_id"
        ),
        score_summary={
            "selection_basis": "completion_preserving",
            "completion_signal_used": True,
            "partner_config_path": class_reference.get("partner_config_path"),
            "partner_config_id": class_reference.get("partner_config_id"),
            "partner_selected_candidate_id": class_reference.get(
                "partner_selected_candidate_id"
            ),
            "normalized_signature_exact_match": exact_match,
            "selected_candidate_branch_member_count": chosen.branch_member_count,
            "selected_candidate_max_member_weight": chosen.max_member_weight,
            "selected_candidate_normalized_signature": normalized_signature,
        },
    )


def control_matched_strategy(
    completion_class: CompletionClassSurface,
    request: CompletionRequest,
) -> StrategySelection:
    class_reference = parse_class_reference_parameters(
        request.strategy_parameters,
        strategy_id="control_matched",
        class_id=completion_class.class_id,
    )
    if class_reference is None:
        fallback = predictive_signature_canonical_strategy(completion_class, request)
        return StrategySelection(
            selected_candidate_id=fallback.selected_candidate_id,
            tie_break_rule=fallback.tie_break_rule,
            score_summary={
                **fallback.score_summary,
                "selection_basis": "control_matched_fallback",
                "control_signal_used": False,
                "fallback_reason": "no_matched_control_reference",
            },
            fallback_used="no_matched_control_reference",
        )

    reference_branch_member_count = int(class_reference.get("reference_branch_member_count", 0))
    reference_max_member_weight = Fraction(
        class_reference.get("reference_max_member_weight", "0")
    )
    ranked = []
    for candidate in completion_class.candidates:
        branch_member_count, max_member_weight, candidate_id = candidate_weight_profile(candidate)
        ranked.append(
            (
                abs(branch_member_count - reference_branch_member_count),
                abs(max_member_weight - reference_max_member_weight),
                predictive_signature_repr(candidate.predictive_signature_key),
                candidate_id,
                candidate,
                branch_member_count,
                max_member_weight,
            )
        )
    ranked.sort(key=lambda item: item[:-3])
    _, _, _, _, chosen, branch_member_count, max_member_weight = ranked[0]
    return StrategySelection(
        selected_candidate_id=chosen.candidate_id,
        tie_break_rule=(
            "minimize branch_member_count distance to matched control, then max_member_weight distance, then canonical predictive signature, then candidate_id"
        ),
        score_summary={
            "selection_basis": "control_matched",
            "control_signal_used": True,
            "matched_control_config_path": class_reference.get("matched_control_config_path"),
            "matched_control_config_id": class_reference.get("matched_control_config_id"),
            "matched_control_candidate_id": class_reference.get("reference_candidate_id"),
            "reference_branch_member_count": reference_branch_member_count,
            "reference_max_member_weight": str(reference_max_member_weight),
            "selected_candidate_branch_member_count": branch_member_count,
            "selected_candidate_max_member_weight": str(max_member_weight),
        },
    )


def _predictive_canonical_sort_key(
    candidate: CompletionCandidate,
) -> tuple[int, str, str]:
    signature_key = repr(candidate.predictive_signature_key)
    branch_member_count = candidate.branch_member_count or 0
    return (-branch_member_count, signature_key, candidate.candidate_id)


__all__ = [
    "CompletionStrategy",
    "StrategySelection",
    "completion_preserving_strategy",
    "control_matched_strategy",
    "identity_reference_strategy",
    "max_weight_representative_strategy",
    "predictive_signature_canonical_strategy",
]
