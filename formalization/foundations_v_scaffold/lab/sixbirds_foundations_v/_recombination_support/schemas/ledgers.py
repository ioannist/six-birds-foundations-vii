from __future__ import annotations

from pydantic import Field, model_validator

from .common import (
    SixBirdsRecombinationModel,
    ensure_nonempty_string,
    ensure_optional_nonempty_string,
    ensure_optional_repo_relative_path,
    ensure_unique_strings,
)
from .enums import (
    AuditStatus,
    RecombinationClassLabel,
    ResultLedgerVersion,
    RouteClassificationLedgerVersion,
)


class ResultLedgerEntry(SixBirdsRecombinationModel):
    benchmark_id: str
    branchwise_quotient_size: int = Field(ge=0)
    config_hash_sha256: str
    config_id: str
    derived_summary_path: str
    eta_max_fiber_size: int = Field(ge=0)
    flattening_status: AuditStatus
    interface_id: str
    internalization_status: AuditStatus
    note_path: str
    recombination_quotient_size: int = Field(ge=0)
    reproducibility_manifest_path: str
    result_manifest_path: str
    run_id: str
    validation_passed: bool

    @model_validator(mode="after")
    def validate_entry(self) -> "ResultLedgerEntry":
        ensure_nonempty_string(self.benchmark_id, "benchmark_id")
        ensure_nonempty_string(self.config_hash_sha256, "config_hash_sha256")
        ensure_nonempty_string(self.config_id, "config_id")
        ensure_nonempty_string(self.interface_id, "interface_id")
        ensure_nonempty_string(self.run_id, "run_id")
        ensure_optional_repo_relative_path(self.derived_summary_path, "derived_summary_path")
        ensure_optional_repo_relative_path(
            self.note_path,
            "note_path",
        )
        ensure_optional_repo_relative_path(
            self.reproducibility_manifest_path,
            "reproducibility_manifest_path",
        )
        ensure_optional_repo_relative_path(
            self.result_manifest_path,
            "result_manifest_path",
        )
        return self


class ResultLedger(SixBirdsRecombinationModel):
    schema_version: ResultLedgerVersion = ResultLedgerVersion.V1
    entries: dict[str, ResultLedgerEntry]

    @model_validator(mode="after")
    def validate_ledger(self) -> "ResultLedger":
        for run_id, entry in self.entries.items():
            ensure_nonempty_string(run_id, "entries keys")
            if run_id != entry.run_id:
                raise ValueError("ledger entry keys must match the embedded run_id")
        return self


class RouteClassificationLedgerEntry(SixBirdsRecombinationModel):
    candidate_id: str
    route_label: str
    class_label: RecombinationClassLabel
    source_run_id: str | None = None
    evidence_artifact_path: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_entry(self) -> "RouteClassificationLedgerEntry":
        ensure_nonempty_string(self.candidate_id, "candidate_id")
        ensure_nonempty_string(self.route_label, "route_label")
        ensure_optional_nonempty_string(self.source_run_id, "source_run_id")
        ensure_optional_nonempty_string(self.notes, "notes")
        ensure_optional_repo_relative_path(
            self.evidence_artifact_path,
            "evidence_artifact_path",
        )
        return self


class RouteClassificationLedger(SixBirdsRecombinationModel):
    schema_version: RouteClassificationLedgerVersion = RouteClassificationLedgerVersion.V1
    ledger_id: str
    entries: list[RouteClassificationLedgerEntry] = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_ledger(self) -> "RouteClassificationLedger":
        ensure_nonempty_string(self.ledger_id, "ledger_id")
        ensure_unique_strings([entry.candidate_id for entry in self.entries], "candidate_ids")
        ensure_unique_strings(self.tags, "tags")
        for tag in self.tags:
            ensure_nonempty_string(tag, "tags")
        return self


__all__ = [
    "ResultLedger",
    "ResultLedgerEntry",
    "RouteClassificationLedger",
    "RouteClassificationLedgerEntry",
]
