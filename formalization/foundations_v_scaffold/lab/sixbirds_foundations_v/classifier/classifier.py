from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sixbirds_foundations_v._recombination_support.schemas.enums import AuditStatus, RecombinationClassLabel


CLASSIFIER_RULE_VERSION = "ticket16.deterministic.v1"


@dataclass(frozen=True)
class ClassificationInput:
    current_quotient_size: int
    predictive_quotient_size: int
    branchwise_quotient_size: int
    recombination_quotient_size: int
    eta_max_fiber_size: int
    recombination_gap_value: Fraction
    route_readability_score: Fraction
    unconditional_visibility: Fraction
    max_conditional_visibility: Fraction
    visibility_recovery_gap: Fraction
    factorization_status: AuditStatus
    search_space_id: str | None = None
    benchmark_id: str | None = None
    protocol_internalization_status: AuditStatus = AuditStatus.SKIPPED
    explicit_paired_erasure_context: bool = False
    explicit_dissipative_context: bool = False


@dataclass(frozen=True)
class ClassificationOutcome:
    label: RecombinationClassLabel
    rule_name: str
    rule_version: str = CLASSIFIER_RULE_VERSION


def classify_case(result: ClassificationInput) -> ClassificationOutcome:
    if _is_artifact(result):
        return ClassificationOutcome(
            label=RecombinationClassLabel.ARTIFACT,
            rule_name="artifact_protocol_failure",
        )
    if _is_dissipative(result):
        return ClassificationOutcome(
            label=RecombinationClassLabel.DISSIPATIVE,
            rule_name="dissipative_exact_collapse",
        )
    if _is_marked_suppression(result):
        return ClassificationOutcome(
            label=RecombinationClassLabel.MARKED_SUPPRESSION,
            rule_name="marked_suppression_factorized",
        )
    if _is_memory_only(result):
        return ClassificationOutcome(
            label=RecombinationClassLabel.MEMORY_ONLY,
            rule_name="memory_only_predictive_without_recombination",
        )
    if _is_classical_mixture(result):
        return ClassificationOutcome(
            label=RecombinationClassLabel.CLASSICAL_MIXTURE,
            rule_name="classical_mixture_factorized",
        )
    if _is_positive_recombination_candidate(result):
        if _is_explicit_erasure_recovery(result):
            return ClassificationOutcome(
                label=RecombinationClassLabel.ERASURE_RECOVERY,
                rule_name="paired_erasure_recovery",
            )
        return ClassificationOutcome(
            label=RecombinationClassLabel.COHERENT_BRANCH_CANDIDATE,
            rule_name="generic_positive_relative_case",
        )
    return ClassificationOutcome(
        label=RecombinationClassLabel.UNCLASSIFIED,
        rule_name="unclassified_fallback",
    )


def _is_factorized_zero_gap(result: ClassificationInput) -> bool:
    return (
        result.branchwise_quotient_size == result.recombination_quotient_size
        and result.eta_max_fiber_size == 1
        and result.recombination_gap_value == 0
        and result.factorization_status == AuditStatus.PASSED
    )


def _is_positive_recombination_candidate(result: ClassificationInput) -> bool:
    return (
        result.recombination_quotient_size > result.branchwise_quotient_size
        and result.eta_max_fiber_size > 1
        and result.recombination_gap_value > 0
        and result.factorization_status == AuditStatus.FAILED
        and result.route_readability_score == 0
        and result.visibility_recovery_gap > 0
        and result.max_conditional_visibility > result.unconditional_visibility
    )


def _is_artifact(result: ClassificationInput) -> bool:
    return (
        result.protocol_internalization_status == AuditStatus.FAILED
        and _is_positive_recombination_candidate(result)
    )


def _is_dissipative(result: ClassificationInput) -> bool:
    return result.explicit_dissipative_context and (
        result.branchwise_quotient_size == result.recombination_quotient_size
        and result.eta_max_fiber_size == 1
        and result.recombination_gap_value == 0
    )


def _is_marked_suppression(result: ClassificationInput) -> bool:
    return (
        _is_factorized_zero_gap(result)
        and result.route_readability_score == 1
        and result.visibility_recovery_gap == 0
    )


def _is_memory_only(result: ClassificationInput) -> bool:
    return _is_factorized_zero_gap(result) and (
        result.predictive_quotient_size > result.current_quotient_size
    )


def _is_classical_mixture(result: ClassificationInput) -> bool:
    return _is_factorized_zero_gap(result) and (
        result.predictive_quotient_size == result.current_quotient_size
    )


def _is_explicit_erasure_recovery(result: ClassificationInput) -> bool:
    return result.explicit_paired_erasure_context or (
        result.benchmark_id == "route_erased_split_recombine"
        and result.search_space_id != "cyclic_relative_carrier_space"
    )


__all__ = [
    "CLASSIFIER_RULE_VERSION",
    "ClassificationInput",
    "ClassificationOutcome",
    "classify_case",
]
