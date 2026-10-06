from __future__ import annotations

from pydantic import Field, model_validator

from .common import (
    SixBirdsRecombinationModel,
    ensure_finite_nonnegative_number,
    ensure_nonempty_string,
    ensure_optional_nonempty_string,
    ensure_optional_repo_relative_path,
    ensure_unique_strings,
)
from .enums import (
    AuditStatus,
    RecombinationClassLabel,
    RecombinationGapMetricName,
    RecombinationResultManifestVersion,
    RobustnessStatus,
)


class AuditSummaryBase(SixBirdsRecombinationModel):
    status: AuditStatus
    evidence_summary: list[str] = Field(min_length=1)
    artifact_ref: str | None = None
    failure_code: str | None = None
    failure_detail: str | None = None

    @model_validator(mode="after")
    def validate_audit_summary(self) -> "AuditSummaryBase":
        ensure_optional_repo_relative_path(self.artifact_ref, "artifact_ref")
        ensure_optional_nonempty_string(self.failure_code, "failure_code")
        ensure_optional_nonempty_string(self.failure_detail, "failure_detail")
        for item in self.evidence_summary:
            ensure_nonempty_string(item, "evidence_summary")
        if self.status == AuditStatus.FAILED:
            if self.failure_code is None or self.failure_detail is None:
                raise ValueError(
                    "failed audits must record both failure_code and failure_detail"
                )
        return self


class SameSupportCertificateSummary(AuditSummaryBase):
    certificate_id: str | None = None
    same_support_required: bool = True

    @model_validator(mode="after")
    def validate_same_support(self) -> "SameSupportCertificateSummary":
        ensure_optional_nonempty_string(self.certificate_id, "certificate_id")
        return self


class FactorizationCertificateSummary(AuditSummaryBase):
    certificate_id: str | None = None
    eta_surjective: bool | None = None

    @model_validator(mode="after")
    def validate_factorization(self) -> "FactorizationCertificateSummary":
        ensure_optional_nonempty_string(self.certificate_id, "certificate_id")
        return self


class RouteAuditSummary(AuditSummaryBase):
    route_labels_marked: bool | None = None
    route_labels_erased: bool | None = None


class ProtocolAuditSummary(AuditSummaryBase):
    protocol_internalized: bool | None = None


class FlatteningAuditSummary(AuditSummaryBase):
    completion_applied: bool | None = None
    flattening_detected: bool | None = None


class RobustnessSummary(SixBirdsRecombinationModel):
    status: RobustnessStatus
    evidence_summary: list[str] = Field(min_length=1)
    robustness_fraction: float | None = Field(default=None, ge=0, le=1)
    trial_count: int | None = Field(default=None, ge=0)
    threshold: float | None = Field(default=None, ge=0, le=1)
    artifact_ref: str | None = None
    failure_code: str | None = None
    failure_detail: str | None = None

    @model_validator(mode="after")
    def validate_robustness(self) -> "RobustnessSummary":
        ensure_optional_repo_relative_path(self.artifact_ref, "artifact_ref")
        ensure_optional_nonempty_string(self.failure_code, "failure_code")
        ensure_optional_nonempty_string(self.failure_detail, "failure_detail")
        for item in self.evidence_summary:
            ensure_nonempty_string(item, "evidence_summary")
        if self.robustness_fraction is not None:
            ensure_finite_nonnegative_number(
                self.robustness_fraction,
                "robustness_fraction",
            )
        if self.threshold is not None:
            ensure_finite_nonnegative_number(self.threshold, "threshold")
        if self.status == RobustnessStatus.FAILED:
            if self.failure_code is None or self.failure_detail is None:
                raise ValueError(
                    "failed robustness summaries must record failure details"
                )
        return self


class RecombinationInterfaceResultRecord(SixBirdsRecombinationModel):
    run_id: str
    benchmark_id: str
    interface_id: str
    seed: int
    history_count: int = Field(ge=0)
    current_quotient_size: int = Field(ge=0)
    predictive_quotient_size: int = Field(ge=0)
    branch_assemblage_count: int = Field(ge=0)
    branchwise_quotient_size: int = Field(ge=0)
    recombination_quotient_size: int = Field(ge=0)
    eta_max_fiber_size: int = Field(ge=0)
    recombination_gap_metric_name: RecombinationGapMetricName
    recombination_gap_value: float
    route_readability_score: float = Field(ge=0, le=1)
    unconditional_visibility: float = Field(ge=0)
    conditional_visibility: float = Field(ge=0)
    same_support_status: AuditStatus
    factorization_status: AuditStatus
    internalization_status: AuditStatus
    flattening_status: AuditStatus
    erasure_status: AuditStatus
    robustness_status: RobustnessStatus = RobustnessStatus.UNTESTED
    robustness_fraction: float | None = Field(default=None, ge=0, le=1)
    class_label: RecombinationClassLabel
    runtime_seconds: float = Field(ge=0)
    same_support_certificate: SameSupportCertificateSummary
    factorization_certificate: FactorizationCertificateSummary
    route_audit: RouteAuditSummary
    protocol_audit: ProtocolAuditSummary
    flattening_audit: FlatteningAuditSummary
    robustness_summary: RobustnessSummary

    @model_validator(mode="after")
    def validate_record(self) -> "RecombinationInterfaceResultRecord":
        ensure_nonempty_string(self.run_id, "run_id")
        ensure_nonempty_string(self.benchmark_id, "benchmark_id")
        ensure_nonempty_string(self.interface_id, "interface_id")
        ensure_finite_nonnegative_number(
            self.recombination_gap_value,
            "recombination_gap_value",
        )
        ensure_finite_nonnegative_number(
            self.route_readability_score,
            "route_readability_score",
        )
        ensure_finite_nonnegative_number(
            self.unconditional_visibility,
            "unconditional_visibility",
        )
        ensure_finite_nonnegative_number(
            self.conditional_visibility,
            "conditional_visibility",
        )
        ensure_finite_nonnegative_number(self.runtime_seconds, "runtime_seconds")
        if self.robustness_fraction is not None:
            ensure_finite_nonnegative_number(
                self.robustness_fraction,
                "robustness_fraction",
            )
        if (
            self.robustness_fraction is not None
            and self.robustness_summary.robustness_fraction is not None
            and self.robustness_fraction != self.robustness_summary.robustness_fraction
        ):
            raise ValueError(
                "robustness_fraction must match robustness_summary.robustness_fraction"
            )
        if self.same_support_status != self.same_support_certificate.status:
            raise ValueError(
                "same_support_status must match same_support_certificate.status"
            )
        if self.factorization_status != self.factorization_certificate.status:
            raise ValueError(
                "factorization_status must match factorization_certificate.status"
            )
        if self.internalization_status != self.protocol_audit.status:
            raise ValueError(
                "internalization_status must match protocol_audit.status"
            )
        if self.flattening_status != self.flattening_audit.status:
            raise ValueError(
                "flattening_status must match flattening_audit.status"
            )
        if self.erasure_status != self.route_audit.status:
            raise ValueError("erasure_status must match route_audit.status")
        if self.robustness_status != self.robustness_summary.status:
            raise ValueError("robustness_status must match robustness_summary.status")
        return self


class RecombinationResultManifest(SixBirdsRecombinationModel):
    schema_version: RecombinationResultManifestVersion = (
        RecombinationResultManifestVersion.V1
    )
    manifest_id: str
    run_id: str
    benchmark_id: str
    records: list[RecombinationInterfaceResultRecord] = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    raw_artifact_path: str | None = None
    derived_note_path: str | None = None

    @model_validator(mode="after")
    def validate_manifest(self) -> "RecombinationResultManifest":
        ensure_nonempty_string(self.manifest_id, "manifest_id")
        ensure_nonempty_string(self.run_id, "run_id")
        ensure_nonempty_string(self.benchmark_id, "benchmark_id")
        ensure_optional_repo_relative_path(
            self.raw_artifact_path,
            "raw_artifact_path",
        )
        ensure_optional_repo_relative_path(
            self.derived_note_path,
            "derived_note_path",
        )
        ensure_unique_strings(
            [record.interface_id for record in self.records],
            "interface_ids",
        )
        for tag in self.tags:
            ensure_nonempty_string(tag, "tags")
        for record in self.records:
            if record.run_id != self.run_id:
                raise ValueError("all records must match manifest run_id")
            if record.benchmark_id != self.benchmark_id:
                raise ValueError("all records must match benchmark_id")
        return self


__all__ = [
    "FactorizationCertificateSummary",
    "FlatteningAuditSummary",
    "ProtocolAuditSummary",
    "RecombinationInterfaceResultRecord",
    "RecombinationResultManifest",
    "RobustnessSummary",
    "RouteAuditSummary",
    "SameSupportCertificateSummary",
]
