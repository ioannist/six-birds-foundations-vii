from __future__ import annotations

import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

from .intrinsic import DEFAULT_INTRINSIC_REGISTRY_OUTPUT
from .models import (
    IntrinsicCandidateRegistryArtifact,
    IntrinsicRegistryCaseRecord,
    SecondStageEvaluationRecord,
    SecondStageProposalRecord,
    SecondStageRegistryArtifact,
    SecondStageRegistryCaseRecord,
    SecondStageSmokeArtifact,
    SecondStageSmokeCaseRecord,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SECOND_STAGE_SMOKE_OUTPUT = "results/derived/ticket27r1_second_stage_smoke.json"
DEFAULT_SECOND_STAGE_REGISTRY_OUTPUT = "results/derived/ticket27r1_second_stage_registry.json"
DEFAULT_SECOND_STAGE_SUMMARY_OUTPUT = (
    "results/derived/ticket27r1_second_stage_stability_summary.json"
)
DEFAULT_SECOND_STAGE_NOTE_OUTPUT = "results/notes/ticket27r1_second_stage_note.md"
DEFAULT_SECOND_STAGE_SMOKE_IDS = (
    "t27.flagship.reference_positive",
    "t27.control.null_baseline",
)
FLAGSHIP_IDS = (
    "t27.flagship.reference_positive",
    "t27.flagship.completion_partner",
)


def build_second_stage_smoke_artifact(
    *,
    repo_root: Path | None = None,
    stable_ids: Sequence[str] = DEFAULT_SECOND_STAGE_SMOKE_IDS,
) -> SecondStageSmokeArtifact:
    registry = load_intrinsic_registry_artifact(repo_root=repo_root)
    by_id = {case.stable_id: case for case in registry.cases}
    cases = [
        evaluate_second_stage_smoke_case(
            by_id[stable_id],
            control_reference=_control_reference_for_case(
                case=by_id[stable_id],
                cases_by_id=by_id,
            ),
        )
        for stable_id in stable_ids
    ]
    return SecondStageSmokeArtifact(
        generated_from=[
            "plan.md",
            DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
            "T27-08R review repair path",
        ],
        intrinsic_registry_artifact=DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
        cases=cases,
    )


def build_second_stage_registry_artifact(
    *,
    repo_root: Path | None = None,
) -> SecondStageRegistryArtifact:
    intrinsic_registry = load_intrinsic_registry_artifact(repo_root=repo_root)
    by_id = {case.stable_id: case for case in intrinsic_registry.cases}
    cases = [
        evaluate_second_stage_registry_case(
            case,
            control_reference=_control_reference_for_case(case=case, cases_by_id=by_id),
        )
        for case in intrinsic_registry.cases
    ]
    status_counts = Counter(case.status for case in cases)
    return SecondStageRegistryArtifact(
        generated_from=[
            "plan.md",
            DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
            "T27-08R review repair path",
        ],
        intrinsic_registry_artifact=DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
        case_count=len(cases),
        status_counts=dict(sorted(status_counts.items())),
        cases=cases,
    )


def build_second_stage_stability_summary(
    registry: SecondStageRegistryArtifact,
) -> dict[str, Any]:
    counts_by_category = Counter(case.category for case in registry.cases)
    status_counts_by_category: dict[str, dict[str, int]] = {}
    by_id = {case.stable_id: case for case in registry.cases}
    for category in sorted(counts_by_category):
        category_cases = [case for case in registry.cases if case.category == category]
        status_counts_by_category[category] = dict(
            sorted(Counter(case.status for case in category_cases).items())
        )

    flagship_outcomes = {
        stable_id: _case_outcome_summary(by_id[stable_id]) for stable_id in FLAGSHIP_IDS
    }
    control_cases = [case for case in registry.cases if case.category == "required_control"]
    control_outcomes = {
        case.stable_id: _case_outcome_summary(case) for case in control_cases
    }
    flagship_reference = by_id["t27.flagship.reference_positive"]
    most_important_control_contrast = _most_important_control_contrast(
        flagship_reference=flagship_reference,
        controls=control_cases,
    )
    accepted_non_identity_total = sum(case.accepted_non_identity_count for case in registry.cases)
    real_cases_all_rigid = all(case.status == "rigid_minimal" for case in registry.cases)
    branch_outcome = _branch_outcome(
        flagship_outcomes=flagship_outcomes,
        accepted_non_identity_total=accepted_non_identity_total,
        real_cases_all_rigid=real_cases_all_rigid,
    )

    return {
        "ticket": "T27-08R",
        "schema_version": "ticket27r1-second-stage-stability-summary.v1",
        "registry_artifact": DEFAULT_SECOND_STAGE_REGISTRY_OUTPUT,
        "status_counts": registry.status_counts,
        "counts_by_category": dict(sorted(counts_by_category.items())),
        "status_counts_by_category": status_counts_by_category,
        "flagship_outcomes": flagship_outcomes,
        "control_outcomes": control_outcomes,
        "most_important_control_contrast": most_important_control_contrast,
        "accepted_non_identity_total": accepted_non_identity_total,
        "evidence_quality": "vacuous_all_rigid" if real_cases_all_rigid else "non_vacuous",
        "branch_outcome": branch_outcome,
        "invalidates_prior_survival_reading": branch_outcome == "INCONCLUSIVE_VACUOUS",
    }


def build_second_stage_note(
    registry: SecondStageRegistryArtifact,
    summary: dict[str, Any],
) -> str:
    flagship_outcomes = summary["flagship_outcomes"]
    lines = [
        "# Ticket27 R1 Second-Stage Note",
        "",
        "## Flagship Outcomes",
    ]
    for stable_id in FLAGSHIP_IDS:
        outcome = flagship_outcomes[stable_id]
        lines.append(
            f"- `{stable_id}`: status `{outcome['status']}`, "
            f"accepted_non_identity_count `{outcome['accepted_non_identity_count']}`, "
            f"best_admissible_target_size `{outcome['best_admissible_target_size']}`."
        )
    lines.extend(
        [
            "",
            "## Overall Status Counts",
            f"- `{summary['status_counts']}`",
            "",
            "## Branch Outcome",
            f"- `{summary['branch_outcome']}` with evidence quality `{summary['evidence_quality']}`.",
            "",
            "## Most Important Control Contrast",
        ]
    )
    contrast = summary["most_important_control_contrast"]
    if contrast is None:
        lines.append("- None.")
    else:
        lines.append(
            f"- `{contrast['control_id']}` versus `t27.flagship.reference_positive`: "
            f"status `{contrast['status']}`, "
            f"accepted_non_identity_delta `{contrast['accepted_non_identity_delta']}`, "
            f"proposal_count_delta `{contrast['proposal_count_delta']}`."
        )
    lines.append("")
    return "\n".join(lines)


def write_second_stage_smoke_artifact(
    *,
    repo_root: Path | None = None,
    stable_ids: Sequence[str] = DEFAULT_SECOND_STAGE_SMOKE_IDS,
    output_path: str = DEFAULT_SECOND_STAGE_SMOKE_OUTPUT,
) -> Path:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    artifact = build_second_stage_smoke_artifact(
        repo_root=resolved_repo_root,
        stable_ids=stable_ids,
    )
    return _write_json_artifact(
        resolved_repo_root / output_path,
        artifact.model_dump(mode="json"),
    )


def write_second_stage_registry_outputs(
    *,
    repo_root: Path | None = None,
    registry_output_path: str = DEFAULT_SECOND_STAGE_REGISTRY_OUTPUT,
    summary_output_path: str = DEFAULT_SECOND_STAGE_SUMMARY_OUTPUT,
    note_output_path: str = DEFAULT_SECOND_STAGE_NOTE_OUTPUT,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    registry = build_second_stage_registry_artifact(repo_root=resolved_repo_root)
    summary = build_second_stage_stability_summary(registry)
    note = build_second_stage_note(registry, summary)

    registry_path = _write_json_artifact(
        resolved_repo_root / registry_output_path,
        registry.model_dump(mode="json"),
    )
    summary_path = _write_json_artifact(resolved_repo_root / summary_output_path, summary)
    note_path = resolved_repo_root / note_output_path
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")
    return {
        "registry_path": registry_path,
        "summary_path": summary_path,
        "note_path": note_path,
        "case_count": registry.case_count,
        "status_counts": registry.status_counts,
        "branch_outcome": summary["branch_outcome"],
    }


def generate_ticket27_second_stage_smoke_artifact(
    *,
    repo_root: Path | None = None,
    stable_ids: Sequence[str] = DEFAULT_SECOND_STAGE_SMOKE_IDS,
    output_path: str = DEFAULT_SECOND_STAGE_SMOKE_OUTPUT,
) -> dict[str, Any]:
    output = write_second_stage_smoke_artifact(
        repo_root=repo_root,
        stable_ids=stable_ids,
        output_path=output_path,
    )
    return {
        "output_path": output,
        "case_count": len(stable_ids),
        "stable_ids": list(stable_ids),
    }


def generate_ticket27_second_stage_registry_artifacts(
    *,
    repo_root: Path | None = None,
    registry_output_path: str = DEFAULT_SECOND_STAGE_REGISTRY_OUTPUT,
    summary_output_path: str = DEFAULT_SECOND_STAGE_SUMMARY_OUTPUT,
    note_output_path: str = DEFAULT_SECOND_STAGE_NOTE_OUTPUT,
) -> dict[str, Any]:
    return write_second_stage_registry_outputs(
        repo_root=repo_root,
        registry_output_path=registry_output_path,
        summary_output_path=summary_output_path,
        note_output_path=note_output_path,
    )


def load_intrinsic_registry_artifact(
    *,
    repo_root: Path | None = None,
    path: str = DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
) -> IntrinsicCandidateRegistryArtifact:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    payload = json.loads((resolved_repo_root / path).read_text(encoding="utf-8"))
    return IntrinsicCandidateRegistryArtifact.model_validate(payload)


def generate_second_stage_proposals(
    case: IntrinsicRegistryCaseRecord,
) -> list[SecondStageProposalRecord]:
    class_ids = [package_class.class_id for package_class in case.package_classes]
    proposals = [_proposal_record(case, "identity", [[class_id] for class_id in class_ids])]
    for left_index, right_index in combinations(range(len(class_ids)), 2):
        merged = [class_ids[left_index], class_ids[right_index]]
        blocks: list[list[str]] = [sorted(merged)]
        for index, class_id in enumerate(class_ids):
            if index in {left_index, right_index}:
                continue
            blocks.append([class_id])
        proposals.append(
            _proposal_record(
                case,
                proposal_id=f"merge_{merged[0]}__{merged[1]}",
                blocks=blocks,
            )
        )
    if len(class_ids) > 1:
        proposals.append(_proposal_record(case, "full_collapse", [sorted(class_ids)]))
    deduped: dict[str, SecondStageProposalRecord] = {proposal.proposal_id: proposal for proposal in proposals}
    return sorted(
        deduped.values(),
        key=lambda proposal: (proposal.target_package_size, proposal.proposal_id),
    )


def evaluate_second_stage_smoke_case(
    case: IntrinsicRegistryCaseRecord,
    *,
    control_reference: IntrinsicRegistryCaseRecord,
) -> SecondStageSmokeCaseRecord:
    evaluations = _evaluate_second_stage_case(case, control_reference=control_reference)
    accepted = [evaluation for evaluation in evaluations if evaluation.admissibility_status == "accepted"]
    rejected = [evaluation for evaluation in evaluations if evaluation.admissibility_status == "rejected"]
    best_admissible_target_size = (
        min(evaluation.proposal.target_package_size for evaluation in accepted)
        if accepted
        else None
    )
    return SecondStageSmokeCaseRecord(
        stable_id=case.stable_id,
        source_package_size=case.package_size,
        proposal_count=len(evaluations),
        accepted_proposal_count=len(accepted),
        rejected_proposal_count=len(rejected),
        best_admissible_target_size=best_admissible_target_size,
        accepted_proposals=accepted,
        rejected_proposals=rejected,
    )


def evaluate_second_stage_registry_case(
    case: IntrinsicRegistryCaseRecord,
    *,
    control_reference: IntrinsicRegistryCaseRecord,
) -> SecondStageRegistryCaseRecord:
    if case.package_status != "supported":
        return SecondStageRegistryCaseRecord(
            stable_id=case.stable_id,
            category=case.category,
            source_package_size=case.package_size,
            proposal_count=0,
            accepted_proposal_count=0,
            rejected_proposal_count=0,
            best_admissible_target_size=None,
            accepted_non_identity_count=0,
            status="unsupported",
            accepted_proposals=[],
            rejected_proposals=[],
            skip_reason=case.skip_reason or f"intrinsic package status is {case.package_status}",
        )

    evaluations = _evaluate_second_stage_case(case, control_reference=control_reference)
    accepted = [evaluation for evaluation in evaluations if evaluation.admissibility_status == "accepted"]
    rejected = [evaluation for evaluation in evaluations if evaluation.admissibility_status == "rejected"]
    best_admissible_target_size = (
        min(evaluation.proposal.target_package_size for evaluation in accepted)
        if accepted
        else None
    )
    accepted_non_identity_count = sum(
        1 for evaluation in accepted if evaluation.proposal.proposal_id != "identity"
    )
    status = _classify_second_stage_case(
        source_package_size=case.package_size,
        best_admissible_target_size=best_admissible_target_size,
        accepted_non_identity_count=accepted_non_identity_count,
        skip_reason=None,
    )
    return SecondStageRegistryCaseRecord(
        stable_id=case.stable_id,
        category=case.category,
        source_package_size=case.package_size,
        proposal_count=len(evaluations),
        accepted_proposal_count=len(accepted),
        rejected_proposal_count=len(rejected),
        best_admissible_target_size=best_admissible_target_size,
        accepted_non_identity_count=accepted_non_identity_count,
        status=status,
        accepted_proposals=accepted,
        rejected_proposals=rejected,
        skip_reason=None,
    )


def evaluate_second_stage_proposal(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
    *,
    control_reference: IntrinsicRegistryCaseRecord,
) -> SecondStageEvaluationRecord:
    merge_only = _proposal_respects_merge_only(case, proposal)
    observable_compatibility = _observable_compatibility(case, proposal)
    closure_retention = _closure_retention(case, proposal)
    witness_retention = _witness_retention(case, proposal)
    control_separation_retention = _control_separation_retention(
        case,
        proposal,
        control_reference=control_reference,
    )
    rejection_reasons = []
    if not merge_only:
        rejection_reasons.append("merge_only_rule_failed")
    if not observable_compatibility:
        rejection_reasons.append("observable_compatibility_failed")
    if not closure_retention:
        rejection_reasons.append("closure_rule_failed")
    if not witness_retention:
        rejection_reasons.append("witness_retention_failed")
    if not control_separation_retention:
        rejection_reasons.append("control_separation_failed")
    return SecondStageEvaluationRecord(
        proposal=proposal,
        admissibility_status="accepted" if not rejection_reasons else "rejected",
        rejection_reasons=rejection_reasons,
        merge_only=merge_only,
        observable_compatibility=observable_compatibility,
        witness_retention=witness_retention,
        closure_retention=closure_retention,
        control_separation_retention=control_separation_retention,
        collapse_pattern=proposal.collapse_pattern,
        notes=_evaluation_notes(
            case,
            proposal,
            control_reference=control_reference,
            observable_compatibility=observable_compatibility,
            closure_retention=closure_retention,
            witness_retention=witness_retention,
            control_separation_retention=control_separation_retention,
        ),
    )


def _evaluate_second_stage_case(
    case: IntrinsicRegistryCaseRecord,
    *,
    control_reference: IntrinsicRegistryCaseRecord,
) -> list[SecondStageEvaluationRecord]:
    proposals = generate_second_stage_proposals(case)
    return [
        evaluate_second_stage_proposal(case, proposal, control_reference=control_reference)
        for proposal in proposals
    ]


def _proposal_record(
    case: IntrinsicRegistryCaseRecord,
    proposal_id: str,
    blocks: list[list[str]],
) -> SecondStageProposalRecord:
    canonical_blocks = [sorted(block) for block in blocks]
    canonical_blocks.sort(key=lambda block: (len(block), block))
    retained_observable_ids = sorted(
        {
            observable_id
            for package_class in case.package_classes
            for observable_id in _observable_ids(package_class.observation_signature)
        }
    )
    return SecondStageProposalRecord(
        proposal_id=proposal_id,
        stable_id=case.stable_id,
        source_package_size=case.package_size,
        target_package_size=len(canonical_blocks),
        merged_blocks=canonical_blocks,
        retained_observable_ids=retained_observable_ids,
        collapse_pattern=_collapse_pattern(canonical_blocks, case.package_size),
    )


def _proposal_respects_merge_only(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
) -> bool:
    proposal_members = sorted(class_id for block in proposal.merged_blocks for class_id in block)
    source_members = sorted(package_class.class_id for package_class in case.package_classes)
    return proposal_members == source_members and len(set(proposal_members)) == len(proposal_members)


def _observable_compatibility(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
) -> bool:
    signatures_by_class = {
        package_class.class_id: _canonical_key(package_class.observation_signature)
        for package_class in case.package_classes
    }
    return all(
        len({signatures_by_class[class_id] for class_id in block}) == 1
        for block in proposal.merged_blocks
    )


def _closure_retention(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
) -> bool:
    target_by_class = _target_class_by_source_class(proposal)
    transition_by_class = {
        package_class.class_id: package_class.transition_signature
        for package_class in case.package_classes
    }
    for block in proposal.merged_blocks:
        merged_signatures = {
            tuple(
                sorted(
                    (
                        continuation_id,
                        target_by_class[target_class_id],
                    )
                    for continuation_id, target_class_id in transition_by_class[class_id].items()
                )
            )
            for class_id in block
        }
        if len(merged_signatures) > 1:
            return False
    return True


def _witness_retention(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
) -> bool:
    if case.category == "toy_validation":
        return True
    return proposal.target_package_size > 1


def _control_separation_retention(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
    *,
    control_reference: IntrinsicRegistryCaseRecord,
) -> bool:
    if case.category == "toy_validation":
        return True
    if proposal.proposal_id == "identity":
        return True
    if control_reference.package_size == proposal.target_package_size:
        return False
    return True


def _classify_second_stage_case(
    *,
    source_package_size: int,
    best_admissible_target_size: int | None,
    accepted_non_identity_count: int,
    skip_reason: str | None,
) -> str:
    if skip_reason is not None or best_admissible_target_size is None:
        return "unsupported"
    if accepted_non_identity_count == 0:
        return "rigid_minimal"
    if best_admissible_target_size <= 1:
        return "rapid_collapse"
    if best_admissible_target_size < source_package_size:
        return "plateau"
    return "rigid_minimal"


def _target_class_by_source_class(proposal: SecondStageProposalRecord) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for index, block in enumerate(proposal.merged_blocks):
        target_class_id = f"M{index}"
        for class_id in block:
            mapping[class_id] = target_class_id
    return mapping


def _observable_ids(observation_signature: dict[str, Any]) -> list[str]:
    observable_distributions = observation_signature.get("observable_distributions")
    if isinstance(observable_distributions, dict):
        return sorted(observable_distributions)
    event_distribution = observation_signature.get("event_distribution")
    if isinstance(event_distribution, dict):
        return sorted(event_distribution)
    return []


def _collapse_pattern(blocks: list[list[str]], source_package_size: int) -> str:
    if len(blocks) == source_package_size:
        return "identity"
    if len(blocks) == 1:
        return "full_collapse"
    return "partial_merge"


def _case_outcome_summary(case: SecondStageRegistryCaseRecord) -> dict[str, Any]:
    return {
        "status": case.status,
        "source_package_size": case.source_package_size,
        "proposal_count": case.proposal_count,
        "accepted_non_identity_count": case.accepted_non_identity_count,
        "best_admissible_target_size": case.best_admissible_target_size,
    }


def _most_important_control_contrast(
    *,
    flagship_reference: SecondStageRegistryCaseRecord,
    controls: list[SecondStageRegistryCaseRecord],
) -> dict[str, Any] | None:
    if not controls:
        return None
    ranked = sorted(
        controls,
        key=lambda case: (
            abs(case.proposal_count - flagship_reference.proposal_count),
            abs(case.source_package_size - flagship_reference.source_package_size),
            abs(case.accepted_non_identity_count - flagship_reference.accepted_non_identity_count),
        ),
        reverse=True,
    )
    control = ranked[0]
    return {
        "control_id": control.stable_id,
        "status": control.status,
        "accepted_non_identity_delta": (
            control.accepted_non_identity_count - flagship_reference.accepted_non_identity_count
        ),
        "proposal_count_delta": control.proposal_count - flagship_reference.proposal_count,
        "source_package_size_delta": (
            control.source_package_size - flagship_reference.source_package_size
        ),
    }


def _branch_outcome(
    *,
    flagship_outcomes: dict[str, dict[str, Any]],
    accepted_non_identity_total: int,
    real_cases_all_rigid: bool,
) -> str:
    flagship_statuses = {outcome["status"] for outcome in flagship_outcomes.values()}
    if real_cases_all_rigid or accepted_non_identity_total == 0:
        return "INCONCLUSIVE_VACUOUS"
    if flagship_statuses.intersection({"rapid_collapse", "unsupported"}):
        return "NON_VACUOUS_FAILURE"
    return "NON_VACUOUS_STABLE"


def _control_reference_for_case(
    *,
    case: IntrinsicRegistryCaseRecord,
    cases_by_id: dict[str, IntrinsicRegistryCaseRecord],
) -> IntrinsicRegistryCaseRecord:
    if case.stable_id == "t27.control.null_baseline":
        return cases_by_id["t27.flagship.reference_positive"]
    if case.category == "required_control":
        return cases_by_id["t27.flagship.reference_positive"]
    return cases_by_id["t27.control.null_baseline"]


def _evaluation_notes(
    case: IntrinsicRegistryCaseRecord,
    proposal: SecondStageProposalRecord,
    *,
    control_reference: IntrinsicRegistryCaseRecord,
    observable_compatibility: bool,
    closure_retention: bool,
    witness_retention: bool,
    control_separation_retention: bool,
) -> list[str]:
    notes = [
        f"review proposal `{proposal.proposal_id}` on `{case.stable_id}`",
        f"control reference `{control_reference.stable_id}`",
    ]
    if not observable_compatibility:
        notes.append("merged classes did not preserve identical observable signatures")
    if not closure_retention:
        notes.append("merged classes induced inconsistent continuation-labeled successor patterns")
    if not witness_retention:
        notes.append("proposal collapses the real corpus below the review witness floor")
    if not control_separation_retention:
        notes.append("proposal does not preserve a coarse separation from the control reference")
    if observable_compatibility and closure_retention and witness_retention and control_separation_retention:
        notes.append("proposal satisfies the review admissibility checks")
    return notes


def _canonical_key(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((key, _canonical_key(item)) for key, item in sorted(value.items()))
    if isinstance(value, list):
        return tuple(_canonical_key(item) for item in value)
    return value


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


__all__ = [
    "DEFAULT_SECOND_STAGE_NOTE_OUTPUT",
    "DEFAULT_SECOND_STAGE_REGISTRY_OUTPUT",
    "DEFAULT_SECOND_STAGE_SMOKE_IDS",
    "DEFAULT_SECOND_STAGE_SMOKE_OUTPUT",
    "DEFAULT_SECOND_STAGE_SUMMARY_OUTPUT",
    "build_second_stage_note",
    "build_second_stage_registry_artifact",
    "build_second_stage_smoke_artifact",
    "build_second_stage_stability_summary",
    "evaluate_second_stage_proposal",
    "evaluate_second_stage_registry_case",
    "evaluate_second_stage_smoke_case",
    "generate_second_stage_proposals",
    "generate_ticket27_second_stage_registry_artifacts",
    "generate_ticket27_second_stage_smoke_artifact",
    "load_intrinsic_registry_artifact",
    "write_second_stage_registry_outputs",
    "write_second_stage_smoke_artifact",
]
