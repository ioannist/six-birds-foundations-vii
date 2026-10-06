from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from sixbirds_foundations_v._recombination_support.schemas.enums import AuditStatus
from sixbirds_foundations_v._recombination_support.schemas.results import (
    FactorizationCertificateSummary,
    FlatteningAuditSummary,
    ProtocolAuditSummary,
    SameSupportCertificateSummary,
)

from .recombination import RecombinationQuotientResult
from .substrate import InheritedBenchmarkContext


ALLOWED_RUNTIME_AUDIT_STATUSES = {
    AuditStatus.PASSED,
    AuditStatus.FAILED,
    AuditStatus.SKIPPED,
}


@dataclass(frozen=True)
class SameSupportAuditResult:
    status: AuditStatus
    failure_code: str | None
    detail: str
    history_ids: tuple[str, ...]
    interface_id: str
    benchmark_id: str

    def to_schema_summary(self) -> SameSupportCertificateSummary:
        return SameSupportCertificateSummary(
            status=self.status,
            evidence_summary=[self.detail],
            failure_code=self.failure_code,
            failure_detail=self.detail if self.status == AuditStatus.FAILED else None,
            same_support_required=True,
        )


@dataclass(frozen=True)
class FactorizationAuditResult:
    status: AuditStatus
    failure_code: str | None
    detail: str
    all_observables_branchwise_mixing: bool
    k_class_count: int
    r_class_count: int
    eta_max_fiber_size: int

    def to_schema_summary(self) -> FactorizationCertificateSummary:
        return FactorizationCertificateSummary(
            status=self.status,
            evidence_summary=[self.detail],
            failure_code=self.failure_code,
            failure_detail=self.detail if self.status == AuditStatus.FAILED else None,
            eta_surjective=self.eta_max_fiber_size >= 1 if self.k_class_count > 0 else True,
        )


@dataclass(frozen=True)
class ProtocolInternalizationAuditResult:
    status: AuditStatus
    failure_code: str | None
    detail: str
    uninternalized_entities: tuple[str, ...]
    evidence_refs: tuple[str, ...]

    def to_schema_summary(self) -> ProtocolAuditSummary:
        return ProtocolAuditSummary(
            status=self.status,
            evidence_summary=[self.detail],
            failure_code=self.failure_code,
            failure_detail=self.detail if self.status == AuditStatus.FAILED else None,
            protocol_internalized=not self.uninternalized_entities if self.status == AuditStatus.PASSED else None,
        )


@dataclass(frozen=True)
class FlatteningCompletionAuditResult:
    status: AuditStatus
    failure_code: str | None
    detail: str
    comparison_artifact_refs: tuple[str, ...]

    def to_schema_summary(self) -> FlatteningAuditSummary:
        return FlatteningAuditSummary(
            status=self.status,
            evidence_summary=[self.detail],
            failure_code=self.failure_code,
            failure_detail=self.detail if self.status == AuditStatus.FAILED else None,
            completion_applied=None,
            flattening_detected=None,
        )


def certify_same_support(
    context: InheritedBenchmarkContext,
    interface_id: str,
    history_ids: tuple[str, ...] | list[str],
    *,
    support_ids_by_history_id: Mapping[str, str] | None = None,
) -> SameSupportAuditResult:
    ordered_history_ids = tuple(history_ids)
    if not ordered_history_ids:
        return SameSupportAuditResult(
            status=AuditStatus.FAILED,
            failure_code="empty_history_selection",
            detail="same-support certification requires at least one history",
            history_ids=(),
            interface_id=interface_id,
            benchmark_id=context.benchmark_id,
        )
    if not context.runtime_package.support.same_support_required:
        return SameSupportAuditResult(
            status=AuditStatus.SKIPPED,
            failure_code=None,
            detail="benchmark support does not require same-support certification",
            history_ids=ordered_history_ids,
            interface_id=interface_id,
            benchmark_id=context.benchmark_id,
        )
    seen_support_ids: set[str] = set()
    for history_id in ordered_history_ids:
        history = context.runtime_package.history_by_id.get(history_id)
        if history is None:
            return SameSupportAuditResult(
                status=AuditStatus.FAILED,
                failure_code="unknown_history_id",
                detail=f"history {history_id} is not declared in benchmark {context.benchmark_id}",
                history_ids=ordered_history_ids,
                interface_id=interface_id,
                benchmark_id=context.benchmark_id,
            )
        if history.target_interface_id != interface_id:
            return SameSupportAuditResult(
                status=AuditStatus.FAILED,
                failure_code="history_interface_mismatch",
                detail=(
                    f"history {history_id} targets interface {history.target_interface_id}, "
                    f"expected {interface_id}"
                ),
                history_ids=ordered_history_ids,
                interface_id=interface_id,
                benchmark_id=context.benchmark_id,
            )
        if support_ids_by_history_id is None:
            support_id = context.runtime_package.support.support_id
        else:
            support_id = support_ids_by_history_id.get(history_id)
            if support_id is None:
                return SameSupportAuditResult(
                    status=AuditStatus.FAILED,
                    failure_code="missing_support_id",
                    detail=f"no support id was provided for history {history_id}",
                    history_ids=ordered_history_ids,
                    interface_id=interface_id,
                    benchmark_id=context.benchmark_id,
                )
        seen_support_ids.add(support_id)
    if len(seen_support_ids) != 1:
        return SameSupportAuditResult(
            status=AuditStatus.FAILED,
            failure_code="support_mismatch",
            detail=(
                "histories do not share a single support id: "
                + ", ".join(sorted(seen_support_ids))
            ),
            history_ids=ordered_history_ids,
            interface_id=interface_id,
            benchmark_id=context.benchmark_id,
        )
    return SameSupportAuditResult(
        status=AuditStatus.PASSED,
        failure_code=None,
        detail=f"all histories share support {next(iter(seen_support_ids))}",
        history_ids=ordered_history_ids,
        interface_id=interface_id,
        benchmark_id=context.benchmark_id,
    )


def evaluate_factorization_hook(
    quotient: RecombinationQuotientResult,
) -> FactorizationAuditResult:
    all_branchwise_mixing = all(
        observable.is_certified_branchwise_mixing
        for observable in quotient.observable_family.observables
    )
    k_class_count = quotient.branchwise_quotient.class_count
    r_class_count = quotient.class_count
    eta_max_fiber_size = quotient.eta.eta_max_fiber_size
    factors_on_tested_family = (
        k_class_count == r_class_count and eta_max_fiber_size == 1
    )
    if factors_on_tested_family:
        detail = "observable family factors through branchwise summaries on the tested family"
        if not all_branchwise_mixing:
            detail += "; global branchwise-mixing certification is not required for this local check"
        return FactorizationAuditResult(
            status=AuditStatus.PASSED,
            failure_code=None,
            detail=detail,
            all_observables_branchwise_mixing=all_branchwise_mixing,
            k_class_count=k_class_count,
            r_class_count=r_class_count,
            eta_max_fiber_size=eta_max_fiber_size,
        )
    if r_class_count != k_class_count:
        failure_code = "recombination_refines_branchwise"
        detail = "recombination quotient refines the branchwise quotient on the tested family"
    else:
        failure_code = "eta_fiber_not_singleton"
        detail = "eta has a non-singleton fiber on the tested family"
    return FactorizationAuditResult(
        status=AuditStatus.FAILED,
        failure_code=failure_code,
        detail=detail,
        all_observables_branchwise_mixing=all_branchwise_mixing,
        k_class_count=k_class_count,
        r_class_count=r_class_count,
        eta_max_fiber_size=eta_max_fiber_size,
    )


def build_protocol_internalization_audit(
    *,
    status: AuditStatus,
    detail: str,
    uninternalized_entities: tuple[str, ...] | list[str] = (),
    evidence_refs: tuple[str, ...] | list[str] = (),
    failure_code: str | None = None,
) -> ProtocolInternalizationAuditResult:
    _validate_runtime_audit_status(status, failure_code, detail)
    normalized_uninternalized = tuple(uninternalized_entities)
    normalized_refs = tuple(evidence_refs)
    if status == AuditStatus.PASSED and normalized_uninternalized:
        raise ValueError("passed protocol/internalization audits must not list uninternalized entities")
    return ProtocolInternalizationAuditResult(
        status=status,
        failure_code=failure_code,
        detail=detail,
        uninternalized_entities=normalized_uninternalized,
        evidence_refs=normalized_refs,
    )


def build_flattening_completion_audit(
    *,
    status: AuditStatus,
    detail: str,
    comparison_artifact_refs: tuple[str, ...] | list[str] = (),
    failure_code: str | None = None,
) -> FlatteningCompletionAuditResult:
    _validate_runtime_audit_status(status, failure_code, detail)
    return FlatteningCompletionAuditResult(
        status=status,
        failure_code=failure_code,
        detail=detail,
        comparison_artifact_refs=tuple(comparison_artifact_refs),
    )


def same_support_audit_payload(result: SameSupportAuditResult) -> dict[str, object]:
    return {
        "status": result.status.value,
        "failure_code": result.failure_code,
        "detail": result.detail,
        "history_ids": list(result.history_ids),
        "interface_id": result.interface_id,
        "benchmark_id": result.benchmark_id,
    }


def factorization_audit_payload(result: FactorizationAuditResult) -> dict[str, object]:
    return {
        "status": result.status.value,
        "failure_code": result.failure_code,
        "detail": result.detail,
        "all_observables_branchwise_mixing": result.all_observables_branchwise_mixing,
        "k_class_count": result.k_class_count,
        "r_class_count": result.r_class_count,
        "eta_max_fiber_size": result.eta_max_fiber_size,
    }


def protocol_internalization_audit_payload(
    result: ProtocolInternalizationAuditResult,
) -> dict[str, object]:
    return {
        "status": result.status.value,
        "failure_code": result.failure_code,
        "detail": result.detail,
        "uninternalized_entities": list(result.uninternalized_entities),
        "evidence_refs": list(result.evidence_refs),
    }


def flattening_completion_audit_payload(
    result: FlatteningCompletionAuditResult,
) -> dict[str, object]:
    return {
        "status": result.status.value,
        "failure_code": result.failure_code,
        "detail": result.detail,
        "comparison_artifact_refs": list(result.comparison_artifact_refs),
    }


def _validate_runtime_audit_status(
    status: AuditStatus,
    failure_code: str | None,
    detail: str,
) -> None:
    if status not in ALLOWED_RUNTIME_AUDIT_STATUSES:
        raise ValueError(
            "runtime audit hooks only support passed, failed, or skipped statuses"
        )
    if not detail:
        raise ValueError("audit detail must be non-empty")
    if status == AuditStatus.FAILED and not failure_code:
        raise ValueError("failed audit hooks must record a stable failure_code")
    if status == AuditStatus.PASSED and failure_code is not None:
        raise ValueError("passed audit hooks must not record a failure_code")


__all__ = [
    "FactorizationAuditResult",
    "FlatteningCompletionAuditResult",
    "ProtocolInternalizationAuditResult",
    "SameSupportAuditResult",
    "build_flattening_completion_audit",
    "build_protocol_internalization_audit",
    "certify_same_support",
    "evaluate_factorization_hook",
    "factorization_audit_payload",
    "flattening_completion_audit_payload",
    "protocol_internalization_audit_payload",
    "same_support_audit_payload",
]
