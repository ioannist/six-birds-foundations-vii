from __future__ import annotations

from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel


class IntrinsicPackageClassRecord(SixBirdsRecombinationModel):
    class_id: str
    member_state_ids: list[str]
    representative_state_id: str
    observation_signature: dict[str, Any]
    transition_signature: dict[str, str]


class IntrinsicPackageProvenance(SixBirdsRecombinationModel):
    seed_corpus_artifact: str
    seed_corpus_entry_id: str
    source_case_id: str
    source_kind: str | None = None
    selected_config_path: str
    execution_mode: str = "config_file"
    alternate_config_paths: list[str] = Field(default_factory=list)
    selected_config_hash: str | None = None
    synthetic_config_payload: dict[str, Any] | None = None
    prior_artifact_refs: list[str] = Field(default_factory=list)
    note_refs: list[str] = Field(default_factory=list)


class IntrinsicPackageCaseRecord(SixBirdsRecombinationModel):
    stable_id: str
    category: str
    source_case_id: str
    benchmark_id: str | None = None
    runtime_benchmark_id: str | None = None
    config_path: str
    package_status: str
    package_size: int
    reachable_state_count: int
    initial_state_ids: list[str] = Field(default_factory=list)
    transition_update_signature: dict[str, dict[str, str]] = Field(default_factory=dict)
    observable_signature: dict[str, dict[str, Any]] = Field(default_factory=dict)
    state_to_package_class_id: dict[str, str] = Field(default_factory=dict)
    package_classes: list[IntrinsicPackageClassRecord] = Field(default_factory=list)
    provenance: IntrinsicPackageProvenance
    notes: list[str] = Field(default_factory=list)


class IntrinsicSmokeArtifact(SixBirdsRecombinationModel):
    ticket: str = "T27-08R"
    schema_version: str = "ticket27r1-intrinsic-smoke.v1"
    generated_from: list[str]
    seed_corpus_artifact: str
    case_count: int
    cases: list[IntrinsicPackageCaseRecord]


class IntrinsicBaselineProfile(SixBirdsRecombinationModel):
    k_class_count: int | None = None
    r_class_count: int | None = None
    eta_max_fiber_size: int | None = None
    factorization_status: str | None = None
    comparison_status: str
    reproduction_mode: str
    package_size_minus_k: int | None = None
    package_size_minus_r: int | None = None
    closer_profile: str | None = None
    paired_verdict: str | None = None


class IntrinsicRegistryCaseRecord(IntrinsicPackageCaseRecord):
    baseline_profile: IntrinsicBaselineProfile | None = None
    skip_reason: str | None = None


class IntrinsicCandidateRegistryArtifact(SixBirdsRecombinationModel):
    ticket: str = "T27-08R"
    schema_version: str = "ticket27r1-intrinsic-candidate-registry.v1"
    generated_from: list[str]
    seed_corpus_artifact: str
    baseline_artifact: str
    case_count: int
    processed_count: int
    skipped_count: int
    cases: list[IntrinsicRegistryCaseRecord]


class SecondStageProposalRecord(SixBirdsRecombinationModel):
    proposal_id: str
    stable_id: str
    source_package_size: int
    target_package_size: int
    merged_blocks: list[list[str]] = Field(default_factory=list)
    retained_observable_ids: list[str] = Field(default_factory=list)
    collapse_pattern: str


class SecondStageEvaluationRecord(SixBirdsRecombinationModel):
    proposal: SecondStageProposalRecord
    admissibility_status: str
    rejection_reasons: list[str] = Field(default_factory=list)
    merge_only: bool = True
    observable_compatibility: bool
    witness_retention: bool
    closure_retention: bool
    control_separation_retention: bool
    collapse_pattern: str
    notes: list[str] = Field(default_factory=list)


class SecondStageSmokeCaseRecord(SixBirdsRecombinationModel):
    stable_id: str
    source_package_size: int
    proposal_count: int
    accepted_proposal_count: int
    rejected_proposal_count: int
    best_admissible_target_size: int | None = None
    accepted_proposals: list[SecondStageEvaluationRecord] = Field(default_factory=list)
    rejected_proposals: list[SecondStageEvaluationRecord] = Field(default_factory=list)


class SecondStageSmokeArtifact(SixBirdsRecombinationModel):
    ticket: str = "T27-08R"
    schema_version: str = "ticket27r1-second-stage-smoke.v1"
    generated_from: list[str]
    intrinsic_registry_artifact: str
    cases: list[SecondStageSmokeCaseRecord]


class SecondStageRegistryCaseRecord(SixBirdsRecombinationModel):
    stable_id: str
    category: str
    source_package_size: int
    proposal_count: int
    accepted_proposal_count: int
    rejected_proposal_count: int
    best_admissible_target_size: int | None = None
    accepted_non_identity_count: int = 0
    status: str
    accepted_proposals: list[SecondStageEvaluationRecord] = Field(default_factory=list)
    rejected_proposals: list[SecondStageEvaluationRecord] = Field(default_factory=list)
    skip_reason: str | None = None


class SecondStageRegistryArtifact(SixBirdsRecombinationModel):
    ticket: str = "T27-08R"
    schema_version: str = "ticket27r1-second-stage-registry.v1"
    generated_from: list[str]
    intrinsic_registry_artifact: str
    case_count: int
    status_counts: dict[str, int]
    cases: list[SecondStageRegistryCaseRecord]


__all__ = [
    "IntrinsicBaselineProfile",
    "IntrinsicCandidateRegistryArtifact",
    "IntrinsicPackageCaseRecord",
    "IntrinsicPackageClassRecord",
    "IntrinsicPackageProvenance",
    "IntrinsicRegistryCaseRecord",
    "IntrinsicSmokeArtifact",
    "SecondStageEvaluationRecord",
    "SecondStageProposalRecord",
    "SecondStageRegistryArtifact",
    "SecondStageRegistryCaseRecord",
    "SecondStageSmokeArtifact",
    "SecondStageSmokeCaseRecord",
]
