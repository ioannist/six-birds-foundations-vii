from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from sixbirds_foundations_v._recombination_support.schemas.configs import BenchmarkRunConfig

from .models import (
    IntrinsicBaselineProfile,
    IntrinsicCandidateRegistryArtifact,
    IntrinsicPackageCaseRecord,
    IntrinsicPackageClassRecord,
    IntrinsicPackageProvenance,
    IntrinsicRegistryCaseRecord,
    IntrinsicSmokeArtifact,
)
from .runtime_surface import (
    compute_review_minimal_behavioral_carrier,
    load_review_benchmark,
    load_review_benchmark_from_config,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
SEED_CORPUS_ARTIFACT = "results/derived/ticket27_seed_corpus.json"
BASELINE_ARTIFACT = "results/derived/ticket27_baseline_reproduction_summary.json"
DEFAULT_INTRINSIC_SMOKE_OUTPUT = "results/derived/ticket27r1_intrinsic_smoke.json"
DEFAULT_INTRINSIC_REGISTRY_OUTPUT = (
    "results/derived/ticket27r1_intrinsic_candidate_registry.json"
)
DEFAULT_INTRINSIC_SUMMARY_OUTPUT = "results/derived/ticket27r1_intrinsic_family_summary.json"
DEFAULT_INTRINSIC_NOTE_OUTPUT = "results/notes/ticket27r1_intrinsic_note.md"
DEFAULT_SMOKE_STABLE_IDS = (
    "t27.flagship.reference_positive",
    "t27.control.null_baseline",
)
CASE_ID_PATTERN = re.compile(
    r"^n(?P<carrier_size>\d+)_d(?P<route_shift_delta>\d+)_"
    r"w(?P<left_num>\d+)of(?P<left_den>\d+)_(?P<right_num>\d+)of(?P<right_den>\d+)$"
)
NEARBY_POSITIVE_EXECUTION_MODE = "synthetic_relative_cycle_benchmark_from_search_case_r1"


def build_intrinsic_case_record(
    seed_entry: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> IntrinsicPackageCaseRecord:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    execution = _prepare_intrinsic_execution(seed_entry, repo_root=resolved_repo_root)
    carrier = compute_review_minimal_behavioral_carrier(execution["benchmark"])

    package_classes = [
        IntrinsicPackageClassRecord(
            class_id=carrier_class.class_id,
            member_state_ids=list(carrier_class.member_state_ids),
            representative_state_id=carrier_class.representative_state_id,
            observation_signature=dict(carrier_class.observation_signature),
            transition_signature=dict(carrier_class.transition_signature),
        )
        for carrier_class in carrier.classes
    ]
    observable_signature = {
        carrier_class.class_id: dict(carrier_class.observation_signature)
        for carrier_class in package_classes
    }
    transition_update_signature = {
        class_id: dict(transitions)
        for class_id, transitions in sorted(carrier.transport_by_class_id.items())
    }
    provenance = IntrinsicPackageProvenance(
        seed_corpus_artifact=SEED_CORPUS_ARTIFACT,
        seed_corpus_entry_id=seed_entry["stable_id"],
        source_case_id=seed_entry["source_case_id"],
        source_kind=seed_entry.get("source_kind"),
        selected_config_path=execution["config_path"],
        execution_mode=execution["execution_mode"],
        alternate_config_paths=execution["alternate_config_paths"],
        selected_config_hash=seed_entry.get("content_hashes", {}).get(execution["config_path"]),
        synthetic_config_payload=execution["synthetic_config_payload"],
        prior_artifact_refs=list(seed_entry.get("prior_artifact_refs", [])),
        note_refs=list(seed_entry.get("note_refs", [])),
    )
    return IntrinsicPackageCaseRecord(
        stable_id=seed_entry["stable_id"],
        category=seed_entry["category"],
        source_case_id=seed_entry["source_case_id"],
        benchmark_id=seed_entry.get("benchmark_id"),
        runtime_benchmark_id=execution["benchmark"].benchmark_id,
        config_path=execution["config_path"],
        package_status=carrier.status.value,
        package_size=carrier.class_count,
        reachable_state_count=carrier.state_count,
        initial_state_ids=list(carrier.initial_state_ids),
        transition_update_signature=transition_update_signature,
        observable_signature=observable_signature,
        state_to_package_class_id=dict(carrier.state_to_class_id),
        package_classes=package_classes,
        provenance=provenance,
        notes=list(carrier.notes),
    )


def build_intrinsic_smoke_artifact(
    *,
    repo_root: Path | None = None,
    stable_ids: Sequence[str] = DEFAULT_SMOKE_STABLE_IDS,
) -> IntrinsicSmokeArtifact:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    seed_corpus = _load_seed_corpus(resolved_repo_root)
    entries_by_id = {entry["stable_id"]: entry for entry in seed_corpus["entries"]}
    cases = [
        build_intrinsic_case_record(entries_by_id[stable_id], repo_root=resolved_repo_root)
        for stable_id in stable_ids
    ]
    return IntrinsicSmokeArtifact(
        generated_from=[
            "plan.md",
            "results/derived/ticket27_seed_corpus.json",
            "T27-08R review repair path",
        ],
        seed_corpus_artifact=SEED_CORPUS_ARTIFACT,
        case_count=len(cases),
        cases=cases,
    )


def build_intrinsic_candidate_registry_artifact(
    *,
    repo_root: Path | None = None,
) -> IntrinsicCandidateRegistryArtifact:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    seed_corpus = _load_seed_corpus(resolved_repo_root)
    baseline_summary = _load_baseline_summary(resolved_repo_root)
    baseline_by_id = {entry["stable_id"]: entry for entry in baseline_summary["entries"]}

    cases: list[IntrinsicRegistryCaseRecord] = []
    for seed_entry in seed_corpus["entries"]:
        baseline_entry = baseline_by_id.get(seed_entry["stable_id"])
        cases.append(
            _build_intrinsic_registry_case(
                seed_entry,
                baseline_entry=baseline_entry,
                repo_root=resolved_repo_root,
            )
        )

    processed_count = sum(1 for case in cases if case.package_status == "supported")
    skipped_count = len(cases) - processed_count
    return IntrinsicCandidateRegistryArtifact(
        generated_from=[
            "plan.md",
            SEED_CORPUS_ARTIFACT,
            BASELINE_ARTIFACT,
            "T27-08R review repair path",
        ],
        seed_corpus_artifact=SEED_CORPUS_ARTIFACT,
        baseline_artifact=BASELINE_ARTIFACT,
        case_count=len(cases),
        processed_count=processed_count,
        skipped_count=skipped_count,
        cases=cases,
    )


def build_intrinsic_family_summary(
    registry: IntrinsicCandidateRegistryArtifact,
) -> dict[str, Any]:
    counts_by_category = Counter(case.category for case in registry.cases)
    processed_cases = [case for case in registry.cases if case.package_status == "supported"]
    processed_counts_by_category = Counter(case.category for case in processed_cases)

    by_category: dict[str, list[IntrinsicRegistryCaseRecord]] = {}
    for case in registry.cases:
        by_category.setdefault(case.category, []).append(case)

    package_size_profile_by_category = {
        category: _package_size_profile(rows)
        for category, rows in sorted(by_category.items())
    }
    runtime_benchmark_ids_by_category = {
        category: sorted(
            {
                case.runtime_benchmark_id
                for case in rows
                if case.runtime_benchmark_id is not None
            }
        )
        for category, rows in sorted(by_category.items())
    }

    flagship_rows = by_category.get("flagship_anchor", [])
    nearby_rows = by_category.get("nearby_positive", [])
    control_rows = by_category.get("required_control", [])
    support_rows = by_category.get("support_only_surface", [])

    flagship_reference = next(
        (case for case in registry.cases if case.stable_id == "t27.flagship.reference_positive"),
        None,
    )
    strongest_contrasts = _strongest_control_contrasts(flagship_reference, control_rows)
    nearby_sizes = sorted(
        case.package_size for case in nearby_rows if case.package_status == "supported"
    )
    nearby_uniform = len(set(nearby_sizes)) == 1 if nearby_sizes else False
    nearby_case_profiles = {
        case.stable_id: {
            "package_size": case.package_size,
            "reachable_state_count": case.reachable_state_count,
            "initial_state_count": len(case.initial_state_ids),
            "screen_event_support_size": _max_screen_event_support_size(case),
        }
        for case in nearby_rows
        if case.package_status == "supported"
    }
    nearby_pair_contrast = _nearby_pair_contrast(
        registry,
        left_id="t27.nearby.n3_d1_w1of3_2of3",
        right_id="t27.nearby.n5_d2_w1of3_2of3",
    )
    spuriously_identical_nearby_positives = (
        nearby_pair_contrast is not None
        and nearby_pair_contrast["same_package_size"]
        and nearby_pair_contrast["same_reachable_state_count"]
        and nearby_pair_contrast["same_screen_event_support_size"]
        and nearby_pair_contrast["same_transition_signature"]
    )

    return {
        "ticket": "T27-08R",
        "schema_version": "ticket27r1-intrinsic-family-summary.v1",
        "seed_corpus_artifact": registry.seed_corpus_artifact,
        "registry_artifact": DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
        "counts_by_category": dict(sorted(counts_by_category.items())),
        "processed_counts_by_category": dict(sorted(processed_counts_by_category.items())),
        "package_size_profile_by_category": package_size_profile_by_category,
        "runtime_benchmark_ids_by_category": runtime_benchmark_ids_by_category,
        "flagship_summary": {
            "processed_count": len(
                [case for case in flagship_rows if case.package_status == "supported"]
            ),
            "stable_ids": [case.stable_id for case in flagship_rows],
            "package_sizes": [case.package_size for case in flagship_rows],
        },
        "nearby_positive_summary": {
            "processed_count": len(
                [case for case in nearby_rows if case.package_status == "supported"]
            ),
            "stable_ids": [case.stable_id for case in nearby_rows],
            "package_sizes": nearby_sizes,
            "uniform_package_size": nearby_uniform,
            "case_profiles": nearby_case_profiles,
            "n3_vs_n5_d2_contrast": nearby_pair_contrast,
            "spuriously_identical_nearby_positives": spuriously_identical_nearby_positives,
        },
        "control_summary": {
            "processed_count": len(
                [case for case in control_rows if case.package_status == "supported"]
            ),
            "stable_ids": [case.stable_id for case in control_rows],
            "package_sizes": [
                case.package_size for case in control_rows if case.package_status == "supported"
            ],
        },
        "support_only_summary": {
            "processed_count": len(
                [case for case in support_rows if case.package_status == "supported"]
            ),
            "stable_ids": [case.stable_id for case in support_rows],
            "package_sizes": [
                case.package_size for case in support_rows if case.package_status == "supported"
            ],
        },
        "strongest_contrasts": strongest_contrasts,
    }


def build_intrinsic_note(
    registry: IntrinsicCandidateRegistryArtifact,
    family_summary: dict[str, Any],
) -> str:
    by_id = {case.stable_id: case for case in registry.cases}
    nearby = family_summary["nearby_positive_summary"]
    lines = [
        "# Ticket27 R1 Intrinsic Note",
        "",
        "## Flagship Counts",
    ]
    for stable_id in (
        "t27.flagship.reference_positive",
        "t27.flagship.completion_partner",
    ):
        case = by_id[stable_id]
        lines.append(
            f"- `{stable_id}`: package_size `{case.package_size}`, "
            f"reachable_state_count `{case.reachable_state_count}`, "
            f"runtime benchmark `{case.runtime_benchmark_id}`."
        )

    lines.extend(
        [
            "",
            "## Nearby-Positive Pattern",
            (
                f"- Processed `{nearby['processed_count']}` nearby positives with package sizes "
                f"`{nearby['package_sizes']}`; uniform package size "
                f"`{nearby['uniform_package_size']}`; spuriously identical "
                f"`{nearby['spuriously_identical_nearby_positives']}`."
            ),
        ]
    )
    contrast = nearby["n3_vs_n5_d2_contrast"]
    if contrast is not None:
        lines.append(
            f"- `t27.nearby.n3_d1_w1of3_2of3` versus `t27.nearby.n5_d2_w1of3_2of3`: "
            f"initial-state delta `{contrast['initial_state_count_delta']}`, "
            f"screen-support delta `{contrast['screen_event_support_size_delta']}`, "
            f"same transition signature `{contrast['same_transition_signature']}`."
        )

    lines.extend(["", "## Strongest Control Contrasts"])
    contrasts = family_summary["strongest_contrasts"]
    if not contrasts:
        lines.append("- None.")
    else:
        for contrast in contrasts:
            lines.append(
                f"- `{contrast['control_id']}` versus `t27.flagship.reference_positive`: "
                f"package-size delta `{contrast['package_size_delta']}`, "
                f"same transition signature `{contrast['same_transition_signature']}`."
            )
    lines.append("")
    return "\n".join(lines)


def write_intrinsic_smoke_artifact(
    *,
    repo_root: Path | None = None,
    stable_ids: Sequence[str] = DEFAULT_SMOKE_STABLE_IDS,
    output_path: str = DEFAULT_INTRINSIC_SMOKE_OUTPUT,
) -> Path:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    artifact = build_intrinsic_smoke_artifact(
        repo_root=resolved_repo_root,
        stable_ids=stable_ids,
    )
    return _write_json_artifact(resolved_repo_root / output_path, artifact.model_dump(mode="json"))


def write_intrinsic_registry_outputs(
    *,
    repo_root: Path | None = None,
    registry_output_path: str = DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
    summary_output_path: str = DEFAULT_INTRINSIC_SUMMARY_OUTPUT,
    note_output_path: str = DEFAULT_INTRINSIC_NOTE_OUTPUT,
) -> dict[str, Path | int]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    registry = build_intrinsic_candidate_registry_artifact(repo_root=resolved_repo_root)
    family_summary = build_intrinsic_family_summary(registry)
    note = build_intrinsic_note(registry, family_summary)

    registry_path = _write_json_artifact(
        resolved_repo_root / registry_output_path,
        registry.model_dump(mode="json"),
    )
    summary_path = _write_json_artifact(resolved_repo_root / summary_output_path, family_summary)
    note_path = resolved_repo_root / note_output_path
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(note, encoding="utf-8")
    return {
        "registry_path": registry_path,
        "summary_path": summary_path,
        "note_path": note_path,
        "case_count": registry.case_count,
        "processed_count": registry.processed_count,
        "skipped_count": registry.skipped_count,
    }


def generate_ticket27_intrinsic_smoke_artifact(
    *,
    repo_root: Path | None = None,
    stable_ids: Sequence[str] = DEFAULT_SMOKE_STABLE_IDS,
    output_path: str = DEFAULT_INTRINSIC_SMOKE_OUTPUT,
) -> dict[str, Any]:
    resolved_output_path = write_intrinsic_smoke_artifact(
        repo_root=repo_root,
        stable_ids=stable_ids,
        output_path=output_path,
    )
    return {
        "output_path": resolved_output_path,
        "case_count": len(stable_ids),
        "stable_ids": list(stable_ids),
    }


def generate_ticket27_intrinsic_registry_artifacts(
    *,
    repo_root: Path | None = None,
    registry_output_path: str = DEFAULT_INTRINSIC_REGISTRY_OUTPUT,
    summary_output_path: str = DEFAULT_INTRINSIC_SUMMARY_OUTPUT,
    note_output_path: str = DEFAULT_INTRINSIC_NOTE_OUTPUT,
) -> dict[str, Any]:
    result = write_intrinsic_registry_outputs(
        repo_root=repo_root,
        registry_output_path=registry_output_path,
        summary_output_path=summary_output_path,
        note_output_path=note_output_path,
    )
    return {
        "registry_path": result["registry_path"],
        "summary_path": result["summary_path"],
        "note_path": result["note_path"],
        "case_count": result["case_count"],
        "processed_count": result["processed_count"],
        "skipped_count": result["skipped_count"],
    }


def _build_intrinsic_registry_case(
    seed_entry: dict[str, Any],
    *,
    baseline_entry: dict[str, Any] | None,
    repo_root: Path,
) -> IntrinsicRegistryCaseRecord:
    try:
        case = build_intrinsic_case_record(seed_entry, repo_root=repo_root)
        baseline_profile = _build_baseline_profile(
            baseline_entry,
            package_size=case.package_size,
        )
        return IntrinsicRegistryCaseRecord(
            **case.model_dump(mode="json"),
            baseline_profile=baseline_profile,
            skip_reason=None,
        )
    except Exception as exc:
        execution = _planned_execution_metadata(seed_entry)
        baseline_profile = _build_baseline_profile(baseline_entry, package_size=None)
        provenance = IntrinsicPackageProvenance(
            seed_corpus_artifact=SEED_CORPUS_ARTIFACT,
            seed_corpus_entry_id=seed_entry["stable_id"],
            source_case_id=seed_entry["source_case_id"],
            source_kind=seed_entry.get("source_kind"),
            selected_config_path=execution["config_path"],
            execution_mode=execution["execution_mode"],
            alternate_config_paths=execution["alternate_config_paths"],
            selected_config_hash=seed_entry.get("content_hashes", {}).get(execution["config_path"]),
            synthetic_config_payload=execution["synthetic_config_payload"],
            prior_artifact_refs=list(seed_entry.get("prior_artifact_refs", [])),
            note_refs=list(seed_entry.get("note_refs", [])),
        )
        return IntrinsicRegistryCaseRecord(
            stable_id=seed_entry["stable_id"],
            category=seed_entry["category"],
            source_case_id=seed_entry["source_case_id"],
            benchmark_id=seed_entry.get("benchmark_id"),
            runtime_benchmark_id=None,
            config_path=execution["config_path"],
            package_status="blocked",
            package_size=0,
            reachable_state_count=0,
            initial_state_ids=[],
            transition_update_signature={},
            observable_signature={},
            state_to_package_class_id={},
            package_classes=[],
            provenance=provenance,
            notes=[],
            baseline_profile=baseline_profile,
            skip_reason=str(exc),
        )


def _build_baseline_profile(
    baseline_entry: dict[str, Any] | None,
    *,
    package_size: int | None,
) -> IntrinsicBaselineProfile | None:
    if baseline_entry is None:
        return None
    headline = baseline_entry["headline_diagnostics"]
    k_class_count = headline.get("k_class_count")
    r_class_count = headline.get("r_class_count")
    eta_max_fiber_size = headline.get("eta_max_fiber_size")
    factorization_status = headline.get("factorization_status")
    paired_verdict = headline.get("paired_verdict")
    if k_class_count is None and "uninternalized" in headline:
        uninternalized = headline["uninternalized"]
        k_class_count = uninternalized.get("k_class_count")
        r_class_count = uninternalized.get("r_class_count")
        eta_max_fiber_size = uninternalized.get("eta_max_fiber_size")
        factorization_status = uninternalized.get("factorization_status")
        paired_verdict = headline.get("paired_verdict")
    package_size_minus_k = (
        package_size - k_class_count
        if package_size is not None and k_class_count is not None
        else None
    )
    package_size_minus_r = (
        package_size - r_class_count
        if package_size is not None and r_class_count is not None
        else None
    )
    closer_profile = None
    if package_size is not None and k_class_count is not None and r_class_count is not None:
        distance_to_k = abs(package_size - k_class_count)
        distance_to_r = abs(package_size - r_class_count)
        if distance_to_k < distance_to_r:
            closer_profile = "branchwise"
        elif distance_to_r < distance_to_k:
            closer_profile = "recombination"
        else:
            closer_profile = "equidistant"
    return IntrinsicBaselineProfile(
        k_class_count=k_class_count,
        r_class_count=r_class_count,
        eta_max_fiber_size=eta_max_fiber_size,
        factorization_status=factorization_status,
        comparison_status=baseline_entry["comparison_status"],
        reproduction_mode=baseline_entry["reproduction_mode"],
        package_size_minus_k=package_size_minus_k,
        package_size_minus_r=package_size_minus_r,
        closer_profile=closer_profile,
        paired_verdict=paired_verdict,
    )


def _package_size_profile(rows: list[IntrinsicRegistryCaseRecord]) -> dict[str, Any]:
    processed = [row for row in rows if row.package_status == "supported"]
    sizes = sorted(row.package_size for row in processed)
    histogram = Counter(sizes)
    closer_counts = Counter(
        row.baseline_profile.closer_profile
        for row in processed
        if row.baseline_profile is not None and row.baseline_profile.closer_profile is not None
    )
    return {
        "row_count": len(rows),
        "processed_count": len(processed),
        "skipped_count": len(rows) - len(processed),
        "package_sizes": sizes,
        "package_size_histogram": {str(size): count for size, count in sorted(histogram.items())},
        "closer_profile_counts": dict(sorted(closer_counts.items())),
    }


def _strongest_control_contrasts(
    flagship_reference: IntrinsicRegistryCaseRecord | None,
    control_rows: list[IntrinsicRegistryCaseRecord],
) -> list[dict[str, Any]]:
    if flagship_reference is None or flagship_reference.package_status != "supported":
        return []
    contrasts = []
    for control in control_rows:
        if control.package_status != "supported":
            continue
        contrasts.append(
            {
                "control_id": control.stable_id,
                "package_size": control.package_size,
                "package_size_delta": control.package_size - flagship_reference.package_size,
                "same_transition_signature": (
                    control.transition_update_signature
                    == flagship_reference.transition_update_signature
                ),
                "runtime_benchmark_id": control.runtime_benchmark_id,
            }
        )
    contrasts.sort(
        key=lambda row: (abs(row["package_size_delta"]), row["same_transition_signature"]),
        reverse=True,
    )
    return contrasts


def _nearby_pair_contrast(
    registry: IntrinsicCandidateRegistryArtifact,
    *,
    left_id: str,
    right_id: str,
) -> dict[str, Any] | None:
    by_id = {case.stable_id: case for case in registry.cases}
    left = by_id.get(left_id)
    right = by_id.get(right_id)
    if left is None or right is None:
        return None
    return {
        "left_id": left_id,
        "right_id": right_id,
        "left_package_size": left.package_size,
        "right_package_size": right.package_size,
        "left_reachable_state_count": left.reachable_state_count,
        "right_reachable_state_count": right.reachable_state_count,
        "left_initial_state_count": len(left.initial_state_ids),
        "right_initial_state_count": len(right.initial_state_ids),
        "left_screen_event_support_size": _max_screen_event_support_size(left),
        "right_screen_event_support_size": _max_screen_event_support_size(right),
        "package_size_delta": right.package_size - left.package_size,
        "reachable_state_count_delta": right.reachable_state_count - left.reachable_state_count,
        "initial_state_count_delta": len(right.initial_state_ids) - len(left.initial_state_ids),
        "screen_event_support_size_delta": (
            _max_screen_event_support_size(right) - _max_screen_event_support_size(left)
        ),
        "same_package_size": left.package_size == right.package_size,
        "same_reachable_state_count": left.reachable_state_count == right.reachable_state_count,
        "same_screen_event_support_size": (
            _max_screen_event_support_size(left) == _max_screen_event_support_size(right)
        ),
        "same_transition_signature": (
            left.transition_update_signature == right.transition_update_signature
        ),
    }


def _max_screen_event_support_size(case: IntrinsicRegistryCaseRecord | IntrinsicPackageCaseRecord) -> int:
    screen_event_ids: set[str] = set()
    for signature in case.observable_signature.values():
        event_distribution = signature.get("event_distribution")
        if not isinstance(event_distribution, dict):
            observable_distributions = signature.get("observable_distributions")
            if isinstance(observable_distributions, dict):
                for observable_payload in observable_distributions.values():
                    if not isinstance(observable_payload, dict):
                        continue
                    screen_event_ids.update(
                        event_id
                        for event_id, value in observable_payload.items()
                        if event_id.startswith("screen_") and value != "0"
                    )
            continue
        screen_event_ids.update(
            event_id
            for event_id, value in event_distribution.items()
            if event_id.startswith("screen_") and value != "0"
        )
    return len(screen_event_ids)


def _prepare_intrinsic_execution(
    seed_entry: dict[str, Any],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    execution = _planned_execution_metadata(seed_entry)
    if execution["execution_mode"] == NEARBY_POSITIVE_EXECUTION_MODE:
        benchmark = load_review_benchmark_from_config(
            execution["synthetic_config"],
            config_path=execution["config_path"],
        )
    else:
        benchmark = load_review_benchmark(repo_root / execution["config_path"])
    return {
        **execution,
        "benchmark": benchmark,
    }


def _planned_execution_metadata(seed_entry: dict[str, Any]) -> dict[str, Any]:
    config_path = _select_benchmark_config_path(seed_entry)
    alternate_config_paths = [
        ref for ref in seed_entry.get("config_refs", []) if ref != config_path
    ]
    if seed_entry["category"] == "nearby_positive" and config_path.startswith(
        "configs/recombination/search/"
    ):
        synthetic_config = _build_relative_cycle_case_config(seed_entry)
        return {
            "config_path": config_path,
            "execution_mode": NEARBY_POSITIVE_EXECUTION_MODE,
            "alternate_config_paths": alternate_config_paths,
            "synthetic_config_payload": synthetic_config.model_dump(mode="json"),
            "synthetic_config": synthetic_config,
        }
    return {
        "config_path": config_path,
        "execution_mode": "config_file",
        "alternate_config_paths": alternate_config_paths,
        "synthetic_config_payload": None,
        "synthetic_config": None,
    }


def _build_relative_cycle_case_config(seed_entry: dict[str, Any]) -> BenchmarkRunConfig:
    parameters = _parse_relative_cycle_case_id(seed_entry["source_case_id"])
    case_id = seed_entry["source_case_id"]
    return BenchmarkRunConfig(
        schema_version="recombination-benchmark-run-config.v1",
        config_kind="benchmark-run",
        config_id=f"ticket27r1.intrinsic.{case_id}",
        benchmark_id=seed_entry.get("benchmark_id") or "relative_cycle_carrier_base",
        interface_id="mid",
        assemblage_family_id="ticket27_relative_cycle_candidate_family",
        observable_family_id="ticket27_relative_cycle_candidate_observable_family",
        route_readability_scenario_id="relative_cycle_anchor_readability",
        visibility_scenario_id="relative_cycle_anchor_screen_visibility",
        carrier_size=parameters["carrier_size"],
        route_shift_delta=parameters["route_shift_delta"],
        weight_left=parameters["weight_left"],
        weight_right=parameters["weight_right"],
        seed=0,
        run_id=f"run_ticket27r1_intrinsic_{case_id}",
        generate_plot_artifacts=False,
        tags=["ticket27", "ticket27_review", "intrinsic_r1", "nearby_positive"],
    )


def _parse_relative_cycle_case_id(case_id: str) -> dict[str, Any]:
    match = CASE_ID_PATTERN.match(case_id)
    if match is None:
        raise ValueError(f"unsupported nearby-positive case id {case_id!r}")
    groups = match.groupdict()
    return {
        "carrier_size": int(groups["carrier_size"]),
        "route_shift_delta": int(groups["route_shift_delta"]),
        "weight_left": f"{groups['left_num']}/{groups['left_den']}",
        "weight_right": f"{groups['right_num']}/{groups['right_den']}",
    }


def _load_seed_corpus(repo_root: Path) -> dict[str, Any]:
    return json.loads((repo_root / SEED_CORPUS_ARTIFACT).read_text(encoding="utf-8"))


def _load_baseline_summary(repo_root: Path) -> dict[str, Any]:
    return json.loads((repo_root / BASELINE_ARTIFACT).read_text(encoding="utf-8"))


def _select_benchmark_config_path(seed_entry: dict[str, Any]) -> str:
    config_refs = list(seed_entry.get("config_refs", []))
    benchmark_refs = [
        ref
        for ref in config_refs
        if ref.startswith("configs/recombination/benchmarks/")
    ]
    if benchmark_refs:
        return benchmark_refs[0]
    if config_refs:
        return config_refs[0]
    raise ValueError(f"seed entry {seed_entry['stable_id']} has no config refs")


def _write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


__all__ = [
    "BASELINE_ARTIFACT",
    "DEFAULT_INTRINSIC_NOTE_OUTPUT",
    "DEFAULT_INTRINSIC_REGISTRY_OUTPUT",
    "DEFAULT_INTRINSIC_SMOKE_OUTPUT",
    "DEFAULT_INTRINSIC_SUMMARY_OUTPUT",
    "DEFAULT_SMOKE_STABLE_IDS",
    "SEED_CORPUS_ARTIFACT",
    "build_intrinsic_candidate_registry_artifact",
    "build_intrinsic_case_record",
    "build_intrinsic_family_summary",
    "build_intrinsic_note",
    "build_intrinsic_smoke_artifact",
    "generate_ticket27_intrinsic_registry_artifacts",
    "generate_ticket27_intrinsic_smoke_artifact",
    "write_intrinsic_registry_outputs",
    "write_intrinsic_smoke_artifact",
]
