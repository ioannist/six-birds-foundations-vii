from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from sixbirds_foundations_v._recombination_support.core.audits import (
    build_flattening_completion_audit,
    build_protocol_internalization_audit,
    certify_same_support,
    factorization_audit_payload,
    evaluate_factorization_hook,
    flattening_completion_audit_payload,
    protocol_internalization_audit_payload,
    same_support_audit_payload,
)
from sixbirds_foundations_v._recombination_support.core.branchwise import branchwise_quotient_payload
from sixbirds_foundations_v._recombination_support.core.catalog import (
    resolve_assemblage_family,
    resolve_observable_family,
    resolve_route_readability_scenario,
    resolve_visibility_scenario,
    validate_search_space_id,
)
from sixbirds_foundations_v._recombination_support.core.classifier import (
    ClassificationInput,
    classify_case,
)
from sixbirds_foundations_v._recombination_support.core.comparisons import (
    build_flattening_completion_comparison,
    build_paired_marked_comparison,
    build_protocol_internalization_comparison,
)
from sixbirds_foundations_v._recombination_support.core.diagnostics import (
    compute_conditional_visibility,
    compute_recombination_gap,
    compute_route_readability,
    conditional_visibility_payload,
    eta_fiber_payload,
    extract_eta_fiber_diagnostics,
    recombination_gap_payload,
    route_readability_payload,
)
from sixbirds_foundations_v._recombination_support.core.promotion import (
    build_open_issues_payload,
    build_promoted_candidates_payload,
    build_ranked_candidates_payload,
    rank_candidates,
    write_promoted_benchmark_config,
)
from sixbirds_foundations_v._recombination_support.core.relative_cycle import (
    DEFAULT_DISSIPATIVE_NOISE_STRENGTHS,
    build_dissipative_relative_cycle_case,
    DEFAULT_WEIGHT_PAIRS,
    build_relative_cycle_completion_observable_family,
    build_relative_cycle_case,
    enumerate_relative_cycle_parameters,
    load_relative_cycle_context,
    noise_strength_strings,
    normalize_relative_cycle_parameters,
    RELATIVE_CYCLE_BENCHMARK_ID,
    weight_pair_strings,
)
from sixbirds_foundations_v._recombination_support.core.robustness import (
    build_candidate_robustness_record,
    build_cases_to_demote_payload,
    build_robustness_summary_rows,
    build_top_stable_cases_payload,
    default_candidate_carrier_sizes,
    enumerate_candidate_neighborhood,
    evaluate_threshold_profiles,
    load_promoted_candidate_references,
    threshold_profiles_from_config,
)
from sixbirds_foundations_v._recombination_support.core.search_spaces import (
    CYCLIC_SPACE_SEARCH_ID,
    NULL_SPACE_SEARCH_ID,
    SearchCaseSpec,
    enumerate_search_space,
)
from sixbirds_foundations_v._recombination_support.core.predictive import analyze_inherited_interface
from sixbirds_foundations_v._recombination_support.core.recombination import recombination_quotient_payload
from sixbirds_foundations_v._recombination_support.core.substrate import load_inherited_benchmark_context
from sixbirds_foundations_v._recombination_support.schemas import (
    AuditStatus,
    RecombinationClassLabel,
    RecombinationGapMetricName,
    RecombinationResultManifest,
    RobustnessStatus,
    export_all_schemas,
    validate_artifact_summary,
)
from sixbirds_foundations_v._recombination_support.schemas.configs import (
    BenchmarkRunConfig,
    RunConfig,
    SearchRunConfig,
)
from sixbirds_foundations_v._recombination_support.schemas.results import (
    RecombinationInterfaceResultRecord,
    RobustnessSummary,
    RouteAuditSummary,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = REPO_ROOT / "results" / "derived" / "run_ledger.json"


class SearchExecutionDeferredError(RuntimeError):
    pass


class UnsupportedSweepExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class BenchmarkRunArtifacts:
    run_id: str
    config_path: Path
    result_manifest_path: Path
    normalized_config_path: Path
    reproducibility_manifest_path: Path
    diagnostics_summary_path: Path
    ledger_entry_path: Path
    plot_manifest_path: Path
    note_path: Path
    ledger_path: Path
    pairwise_comparison_path: Path | None
    diagnosis_path: Path | None
    manifest: RecombinationResultManifest


@dataclass(frozen=True)
class SweepArtifacts:
    sweep_id: str
    config_path: Path
    resolved_config_path: Path
    reproducibility_manifest_path: Path
    summary_table_json_path: Path
    summary_table_csv_path: Path
    top_candidates_path: Path
    collapse_summary_path: Path | None
    note_path: Path
    raw_cases_dir: Path


@dataclass(frozen=True)
class SearchArtifacts:
    search_id: str
    config_path: Path
    resolved_config_path: Path
    reproducibility_manifest_path: Path
    summary_table_json_path: Path
    summary_table_csv_path: Path
    smoke_summary_path: Path
    note_path: Path
    raw_cases_dir: Path
    ranked_candidates_path: Path | None = None
    promoted_candidates_path: Path | None = None
    open_issues_path: Path | None = None


@dataclass(frozen=True)
class RobustnessArtifacts:
    robustness_id: str
    config_path: Path
    resolved_config_path: Path
    reproducibility_manifest_path: Path
    summary_table_json_path: Path
    summary_table_csv_path: Path
    top_stable_cases_path: Path
    cases_to_demote_path: Path
    note_path: Path
    raw_candidates_dir: Path


def load_run_config(path: str | Path) -> RunConfig:
    config_path = Path(path)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    config_kind = payload.get("config_kind")
    if config_kind == "benchmark-run":
        return BenchmarkRunConfig.model_validate(payload)
    if config_kind == "search-run":
        return SearchRunConfig.model_validate(payload)
    raise ValueError(f"unknown config_kind {config_kind!r}")


def validate_run_config(config: RunConfig) -> RunConfig:
    if isinstance(config, SearchRunConfig):
        validate_search_space_id(config.search_space_id)
        if config.search_space_id == NULL_SPACE_SEARCH_ID:
            enumerate_search_space(config, repo_root=REPO_ROOT)
        if config.search_space_id == CYCLIC_SPACE_SEARCH_ID:
            enumerate_search_space(config, repo_root=REPO_ROOT)
        if config.search_space_id == "promoted_candidates_robustness":
            references = load_promoted_candidate_references(REPO_ROOT)
            if not config.promoted_candidate_ids:
                raise ValueError(
                    "promoted_candidates_robustness requires promoted_candidate_ids"
                )
            for candidate_id in config.promoted_candidate_ids:
                if candidate_id not in references:
                    raise ValueError(f"unknown promoted candidate id {candidate_id!r}")
            if not config.local_weight_lefts:
                raise ValueError(
                    "promoted_candidates_robustness requires local_weight_lefts"
                )
            if not config.local_route_shift_deltas:
                raise ValueError(
                    "promoted_candidates_robustness requires local_route_shift_deltas"
                )
            if not config.threshold_profiles:
                raise ValueError(
                    "promoted_candidates_robustness requires threshold_profiles"
                )
            threshold_profiles_from_config(config.threshold_profiles)
        if config.search_space_id == "relative_cycle_positive_family":
            enumerate_relative_cycle_parameters(
                carrier_sizes=config.carrier_sizes,
                route_shift_deltas=config.route_shift_deltas,
                weight_pairs=_search_weight_pairs(config),
            )
        if config.search_space_id == "relative_cycle_dissipative_collapse":
            normalize_relative_cycle_parameters(
                carrier_size=config.anchor_carrier_size or 0,
                route_shift_delta=config.anchor_route_shift_delta or 0,
                weight_left=config.anchor_weight_left or "",
                weight_right=config.anchor_weight_right or "",
            )
            _search_noise_strengths(config)
        return config

    if _uses_dynamic_relative_cycle_case(config):
        normalize_relative_cycle_parameters(
            carrier_size=config.carrier_size or 0,
            route_shift_delta=config.route_shift_delta or 0,
            weight_left=config.weight_left or "",
            weight_right=config.weight_right or "",
        )
        load_relative_cycle_context()
        return config

    context = load_inherited_benchmark_context(config.benchmark_id)
    resolve_assemblage_family(context, config.assemblage_family_id, config.interface_id)
    resolve_observable_family(context, config.observable_family_id, config.interface_id)
    if config.route_readability_scenario_id is not None:
        resolve_route_readability_scenario(config.route_readability_scenario_id)
    if config.visibility_scenario_id is not None:
        resolve_visibility_scenario(config.visibility_scenario_id)
    return config


def normalize_config_payload(config: RunConfig) -> dict[str, object]:
    return config.model_dump(mode="json", exclude_none=True)


def compute_config_hash(config: RunConfig) -> str:
    payload = normalize_config_payload(config)
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def run_config(
    config: RunConfig,
    *,
    config_path: str | Path,
    output_root: str | Path | None = None,
    command_used: str | None = None,
) -> BenchmarkRunArtifacts:
    validated = validate_run_config(config)
    if isinstance(validated, SearchRunConfig):
        raise SearchExecutionDeferredError(
            "search-run execution is deferred in Ticket 8; use validate-config only"
        )
    return _run_benchmark_config(
        validated,
        config_path=Path(config_path),
        output_root=Path(output_root) if output_root is not None else REPO_ROOT,
        command_used=command_used,
    )


def validate_config_file(path: str | Path) -> RunConfig:
    return validate_run_config(load_run_config(path))


def sweep_config(
    config: RunConfig,
    *,
    config_path: str | Path,
    output_root: str | Path | None = None,
    command_used: str | None = None,
) -> SweepArtifacts:
    validated = validate_run_config(config)
    if not isinstance(validated, SearchRunConfig):
        raise UnsupportedSweepExecutionError(
            "sweep execution requires a search-run config"
        )
    resolved_output_root = Path(output_root) if output_root is not None else REPO_ROOT
    if validated.search_space_id == "relative_cycle_positive_family":
        return _run_relative_cycle_sweep(
            validated,
            config_path=Path(config_path),
            output_root=resolved_output_root,
            command_used=command_used,
        )
    if validated.search_space_id == "relative_cycle_dissipative_collapse":
        return _run_dissipative_collapse_sweep(
            validated,
            config_path=Path(config_path),
            output_root=resolved_output_root,
            command_used=command_used,
        )
    raise UnsupportedSweepExecutionError(
        f"unsupported sweep search_space_id {validated.search_space_id}"
    )


def search_config(
    config: RunConfig,
    *,
    config_path: str | Path,
    output_root: str | Path | None = None,
    command_used: str | None = None,
) -> SearchArtifacts:
    validated = validate_run_config(config)
    if not isinstance(validated, SearchRunConfig):
        raise UnsupportedSweepExecutionError(
            "search execution requires a search-run config"
        )
    resolved_output_root = Path(output_root) if output_root is not None else REPO_ROOT
    if validated.search_space_id not in {NULL_SPACE_SEARCH_ID, CYCLIC_SPACE_SEARCH_ID}:
        raise UnsupportedSweepExecutionError(
            f"unsupported search search_space_id {validated.search_space_id}"
        )
    return _run_bounded_search(
        validated,
        config_path=Path(config_path),
        output_root=resolved_output_root,
        command_used=command_used,
    )


def robustness_config(
    config: RunConfig,
    *,
    config_path: str | Path,
    output_root: str | Path | None = None,
    command_used: str | None = None,
) -> RobustnessArtifacts:
    validated = validate_run_config(config)
    if not isinstance(validated, SearchRunConfig):
        raise UnsupportedSweepExecutionError(
            "robustness execution requires a search-run config"
        )
    resolved_output_root = Path(output_root) if output_root is not None else REPO_ROOT
    if validated.search_space_id != "promoted_candidates_robustness":
        raise UnsupportedSweepExecutionError(
            f"unsupported robustness search_space_id {validated.search_space_id}"
        )
    return _run_promoted_candidate_robustness(
        validated,
        config_path=Path(config_path),
        output_root=resolved_output_root,
        command_used=command_used,
    )


def _run_benchmark_config(
    config: BenchmarkRunConfig,
    *,
    config_path: Path,
    output_root: Path,
    command_used: str | None,
) -> BenchmarkRunArtifacts:
    started = perf_counter()
    context = load_inherited_benchmark_context(config.benchmark_id)
    analysis = analyze_inherited_interface(context, config.interface_id)
    if _uses_dynamic_relative_cycle_case(config):
        parameters = normalize_relative_cycle_parameters(
            carrier_size=config.carrier_size or 0,
            route_shift_delta=config.route_shift_delta or 0,
            weight_left=config.weight_left or "",
            weight_right=config.weight_right or "",
        )
        case = build_relative_cycle_case(parameters, context=context)
        assemblages = case.assemblages
        observable_family = (
            build_relative_cycle_completion_observable_family(parameters)
            if "completion_partner" in config.tags
            else case.observable_family
        )
        route_readability_scenario = case.route_readability_scenario
        unconditional_distribution = case.unconditional_visibility_distribution
        conditional_distributions = case.conditional_visibility_distributions
    else:
        assemblages = resolve_assemblage_family(
            context,
            config.assemblage_family_id,
            config.interface_id,
        )
        observable_family = resolve_observable_family(
            context,
            config.observable_family_id,
            config.interface_id,
        )
        route_readability_scenario = resolve_route_readability_scenario(
            config.route_readability_scenario_id or "perfect_binary_route_recovery"
        )
        unconditional_distribution, conditional_distributions = resolve_visibility_scenario(
            config.visibility_scenario_id or "binary_visibility_recovery"
        )
    from sixbirds_foundations_v._recombination_support.core.recombination import compute_recombination_quotient

    quotient = compute_recombination_quotient(
        context,
        config.interface_id,
        assemblages,
        observable_family,
    )
    recombination_gap = compute_recombination_gap(quotient)
    eta_fiber = extract_eta_fiber_diagnostics(quotient)

    route_readability = compute_route_readability(route_readability_scenario)
    visibility = compute_conditional_visibility(
        unconditional_distribution,
        conditional_distributions,
    )

    history_ids = tuple(
        sorted(
            {
                member.history_id
                for assemblage in assemblages.values()
                for member in assemblage.members
            }
        )
    )
    same_support = certify_same_support(context, config.interface_id, history_ids)
    factorization = evaluate_factorization_hook(quotient)
    protocol_audit = _build_protocol_audit(config)
    flattening_audit = _build_flattening_audit(
        config,
        quotient_class_count=quotient.class_count,
        branchwise_class_count=quotient.branchwise_quotient.class_count,
        eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
        recombination_gap_value=recombination_gap.metric_value,
        factorization_status=factorization.status,
    )
    if _uses_dynamic_relative_cycle_case(config):
        class_label = classify_case(
            ClassificationInput(
                current_quotient_size=analysis.current_quotient_size,
                predictive_quotient_size=analysis.predictive_quotient_size,
                branchwise_quotient_size=quotient.branchwise_quotient.class_count,
                recombination_quotient_size=quotient.class_count,
                eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
                recombination_gap_value=recombination_gap.metric_value,
                route_readability_score=route_readability.score_value,
                unconditional_visibility=visibility.unconditional_visibility,
                max_conditional_visibility=visibility.max_conditional_visibility,
                visibility_recovery_gap=visibility.visibility_recovery_gap,
                factorization_status=factorization.status,
                search_space_id=CYCLIC_SPACE_SEARCH_ID,
                benchmark_id=config.benchmark_id,
            )
        ).label
    else:
        class_label = _classify_run_label(
            quotient,
            factorization.status,
            current_quotient_size=analysis.current_quotient_size,
            predictive_quotient_size=analysis.predictive_quotient_size,
            route_readability_score=route_readability.score_value,
            visibility_recovery_gap=visibility.visibility_recovery_gap,
        )
    if (
        protocol_audit.status == AuditStatus.FAILED
        and quotient.class_count > quotient.branchwise_quotient.class_count
    ):
        class_label = RecombinationClassLabel.ARTIFACT

    runtime_seconds = perf_counter() - started
    run_id = config.run_id or f"run_{config.config_id}_seed{config.seed}"
    raw_dir = output_root / "results" / "raw" / run_id
    derived_dir = output_root / "results" / "derived" / run_id
    notes_dir = output_root / "results" / "notes" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    result_manifest_path = raw_dir / "result_manifest.json"
    normalized_config_path = raw_dir / "resolved_config.json"
    reproducibility_manifest_path = raw_dir / "reproducibility_manifest.json"
    diagnostics_summary_path = derived_dir / "diagnostics_summary.json"
    ledger_entry_path = derived_dir / "ledger_entry.json"
    plot_manifest_path = derived_dir / "plot_manifest.json"
    note_path = notes_dir / "run_note.md"
    ledger_path = output_root / "results" / "derived" / "run_ledger.json"
    comparison_artifact_name = _comparison_artifact_name(config)
    comparison_artifact_path = (
        derived_dir / comparison_artifact_name
        if comparison_artifact_name is not None
        else None
    )
    diagnosis_path = derived_dir / "erasure_recovery_diagnosis.json"

    relative_result_manifest_path = _repo_relative_path(result_manifest_path, output_root)
    relative_note_path = _repo_relative_path(note_path, output_root)

    record = RecombinationInterfaceResultRecord(
        run_id=run_id,
        benchmark_id=config.benchmark_id,
        interface_id=config.interface_id,
        seed=config.seed,
        history_count=analysis.history_count,
        current_quotient_size=analysis.current_quotient_size,
        predictive_quotient_size=analysis.predictive_quotient_size,
        branch_assemblage_count=len(assemblages),
        branchwise_quotient_size=quotient.branchwise_quotient.class_count,
        recombination_quotient_size=quotient.class_count,
        eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
        recombination_gap_metric_name=RecombinationGapMetricName.EXACT_RECOMBINATION_GAP,
        recombination_gap_value=float(recombination_gap.metric_value),
        route_readability_score=float(route_readability.score_value),
        unconditional_visibility=float(visibility.unconditional_visibility),
        conditional_visibility=float(visibility.max_conditional_visibility),
        same_support_status=same_support.status,
        factorization_status=factorization.status,
        internalization_status=protocol_audit.status,
        flattening_status=flattening_audit.status,
        erasure_status=AuditStatus.SKIPPED,
        robustness_status=RobustnessStatus.UNTESTED,
        robustness_fraction=0.0,
        class_label=class_label,
        runtime_seconds=runtime_seconds,
        same_support_certificate=same_support.to_schema_summary(),
        factorization_certificate=factorization.to_schema_summary(),
        route_audit=RouteAuditSummary(
            status=AuditStatus.SKIPPED,
            evidence_summary=["route erasure audit is deferred in Ticket 8 runner integration"],
            route_labels_marked=None,
            route_labels_erased=True,
        ),
        protocol_audit=protocol_audit.to_schema_summary(),
        flattening_audit=flattening_audit.to_schema_summary(),
        robustness_summary=RobustnessSummary(
            status=RobustnessStatus.UNTESTED,
            evidence_summary=["robustness sweeps are deferred in Ticket 8 runner integration"],
            robustness_fraction=0.0,
            trial_count=0,
            threshold=1.0,
        ),
    )
    manifest = RecombinationResultManifest(
        manifest_id=f"{run_id}.result",
        run_id=run_id,
        benchmark_id=config.benchmark_id,
        records=[record],
        tags=config.tags,
        raw_artifact_path=relative_result_manifest_path,
        derived_note_path=relative_note_path,
    )

    normalized_config = normalize_config_payload(config)
    config_hash = compute_config_hash(config)
    command = command_used or f"python -m sixbirds_foundations_v._recombination_support.runner run --config {config_path}"
    reproducibility_manifest = {
        "run_id": run_id,
        "config_path": _repo_relative_path(config_path, output_root),
        "config_hash_sha256": config_hash,
        "command_used": command,
        "benchmark_id": config.benchmark_id,
        "interface_id": config.interface_id,
        "assemblage_family_id": config.assemblage_family_id,
        "observable_family_id": config.observable_family_id,
        "output_paths": {
            "raw_dir": _repo_relative_path(raw_dir, output_root),
            "derived_dir": _repo_relative_path(derived_dir, output_root),
            "notes_dir": _repo_relative_path(notes_dir, output_root),
        },
        "result_manifest_path": relative_result_manifest_path,
        "validation_passed": True,
    }
    diagnostics_summary = {
        "run_id": run_id,
        "benchmark_id": config.benchmark_id,
        "interface_id": config.interface_id,
        "inherited_analysis": {
            "history_count": analysis.history_count,
            "current_quotient_size": analysis.current_quotient_size,
            "predictive_quotient_size": analysis.predictive_quotient_size,
            "predictive_refines_current": (
                analysis.predictive_quotient_size > analysis.current_quotient_size
            ),
        },
        "branchwise_quotient": branchwise_quotient_payload(quotient.branchwise_quotient),
        "recombination_quotient": recombination_quotient_payload(quotient),
        "recombination_gap": recombination_gap_payload(recombination_gap),
        "eta_fiber": eta_fiber_payload(eta_fiber),
        "route_readability": route_readability_payload(route_readability),
        "conditional_visibility": conditional_visibility_payload(visibility),
        "same_support": same_support_audit_payload(same_support),
        "factorization": factorization_audit_payload(factorization),
        "protocol_internalization": protocol_internalization_audit_payload(protocol_audit),
        "flattening_completion": flattening_completion_audit_payload(flattening_audit),
    }
    plot_manifest = {
        "generated": False,
        "reason": "Ticket 8 runner writes an explicit plot manifest; deterministic plot generation is deferred",
    }

    result_manifest_path.write_text(
        manifest.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    normalized_config_path.write_text(
        json.dumps(normalized_config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reproducibility_manifest_path.write_text(
        json.dumps(reproducibility_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    diagnostics_summary_path.write_text(
        json.dumps(diagnostics_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    plot_manifest_path.write_text(
        json.dumps(plot_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    erasure_assessment: dict[str, object] | None = None
    protocol_assessment: dict[str, object] | None = None
    flattening_assessment: dict[str, object] | None = None
    realized_pairwise_comparison_path: Path | None = None
    realized_diagnosis_path: Path | None = None
    if comparison_artifact_path is not None:
        reference_summary_path = (
            output_root
            / "results"
            / "derived"
            / config.comparison_run_id
            / "diagnostics_summary.json"
        )
        if _is_protocol_internalization_partner(config):
            comparison = build_protocol_internalization_comparison(
                uninternalized_run_id=config.comparison_run_id or "",
                internalized_run_id=run_id,
                uninternalized_summary_path=reference_summary_path,
                internalized_summary_path=diagnostics_summary_path,
            )
            comparison_artifact_path.write_text(
                json.dumps(comparison.payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            realized_pairwise_comparison_path = comparison_artifact_path
            protocol_assessment = {
                "comparison_run_id": config.comparison_run_id,
                "artifact_exposed": comparison.artifact_exposed,
                "verdict": comparison.verdict,
                "protocol_internalization_comparison_path": _repo_relative_path(
                    comparison_artifact_path,
                    output_root,
                ),
            }
            diagnostics_summary["protocol_internalization_assessment"] = protocol_assessment
            diagnostics_summary["protocol_internalization_comparison"] = comparison.payload
            diagnostics_summary_path.write_text(
                json.dumps(diagnostics_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        elif _is_flattening_completion_partner(config):
            comparison = build_flattening_completion_comparison(
                reference_positive_run_id=config.comparison_run_id or "",
                completion_partner_run_id=run_id,
                reference_summary_path=reference_summary_path,
                completion_partner_summary_path=diagnostics_summary_path,
                candidate_case_id="n5_d1_w1of3_2of3",
            )
            comparison_artifact_path.write_text(
                json.dumps(comparison.payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            realized_pairwise_comparison_path = comparison_artifact_path
            flattening_assessment = {
                "comparison_run_id": config.comparison_run_id,
                "survives_flattening_completion": comparison.survives_flattening_completion,
                "verdict": comparison.verdict,
                "flattening_completion_comparison_path": _repo_relative_path(
                    comparison_artifact_path,
                    output_root,
                ),
            }
            diagnostics_summary["flattening_completion_assessment"] = flattening_assessment
            diagnostics_summary["flattening_completion_comparison"] = comparison.payload
            diagnostics_summary_path.write_text(
                json.dumps(diagnostics_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        else:
            comparison = build_paired_marked_comparison(
                marked_run_id=config.comparison_run_id or "",
                erased_run_id=run_id,
                marked_summary_path=reference_summary_path,
                erased_summary_path=diagnostics_summary_path,
            )
            comparison_artifact_path.write_text(
                json.dumps(comparison.payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            realized_pairwise_comparison_path = comparison_artifact_path
            erasure_assessment = {
                "comparison_run_id": config.comparison_run_id,
                "supports_erasure_recovery": comparison.supports_erasure_recovery,
                "viable_flagship_example": comparison.viable_flagship_example,
                "verdict": comparison.verdict,
                "pairwise_comparison_path": _repo_relative_path(
                    comparison_artifact_path,
                    output_root,
                ),
            }
            diagnostics_summary["erasure_assessment"] = erasure_assessment
            diagnostics_summary_path.write_text(
                json.dumps(diagnostics_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            if comparison.verdict != "strong_erasure_recovery_flagship":
                diagnosis_payload = {
                    "expected_qualitative_property": (
                        "lower route readability than marked partner with positive conditional "
                        "recovery, and ideally recombination refinement"
                    ),
                    "observed_route_readability_score": str(route_readability.score_value),
                    "observed_unconditional_visibility": str(visibility.unconditional_visibility),
                    "observed_max_conditional_visibility": str(
                        visibility.max_conditional_visibility
                    ),
                    "observed_visibility_recovery_gap": str(visibility.visibility_recovery_gap),
                    "observed_branchwise_quotient_size": quotient.branchwise_quotient.class_count,
                    "observed_recombination_quotient_size": quotient.class_count,
                    "observed_eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
                    "observed_recombination_gap": str(recombination_gap.metric_value),
                    "observed_factorization_status": factorization.status.value,
                    "supports_erasure_recovery": comparison.supports_erasure_recovery,
                    "viable_flagship_example": comparison.viable_flagship_example,
                    "likely_source_of_discrepancy": (
                        "observable family recovered some conditional structure but did not meet "
                        "the stronger flagship threshold"
                        if comparison.supports_erasure_recovery
                        else "route readability did not fall enough or conditional recovery did not reappear"
                    ),
                }
                diagnosis_path.write_text(
                    json.dumps(diagnosis_payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                realized_diagnosis_path = diagnosis_path

    ledger_entry = {
        "run_id": run_id,
        "config_id": config.config_id,
        "benchmark_id": config.benchmark_id,
        "interface_id": config.interface_id,
        "config_hash_sha256": config_hash,
        "result_manifest_path": relative_result_manifest_path,
        "reproducibility_manifest_path": _repo_relative_path(
            reproducibility_manifest_path,
            output_root,
        ),
        "derived_summary_path": _repo_relative_path(diagnostics_summary_path, output_root),
        "note_path": relative_note_path,
        "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
        "recombination_quotient_size": quotient.class_count,
        "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
        "internalization_status": protocol_audit.status.value,
        "flattening_status": flattening_audit.status.value,
        "validation_passed": True,
    }
    ledger_entry_path.write_text(
        json.dumps(ledger_entry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _update_run_ledger(ledger_path, ledger_entry)
    note_path.write_text(
        _build_run_note(
            run_id=run_id,
            config=config,
            record=record,
            result_manifest_path=relative_result_manifest_path,
            diagnostics_summary_path=_repo_relative_path(diagnostics_summary_path, output_root),
            route_readability=route_readability,
            visibility=visibility,
            erasure_assessment=erasure_assessment,
            protocol_assessment=protocol_assessment,
            flattening_assessment=flattening_assessment,
        ),
        encoding="utf-8",
    )
    _refresh_ticket15_artifact_controls_summary(output_root)

    return BenchmarkRunArtifacts(
        run_id=run_id,
        config_path=config_path,
        result_manifest_path=result_manifest_path,
        normalized_config_path=normalized_config_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
        diagnostics_summary_path=diagnostics_summary_path,
        ledger_entry_path=ledger_entry_path,
        plot_manifest_path=plot_manifest_path,
        note_path=note_path,
        ledger_path=ledger_path,
        pairwise_comparison_path=realized_pairwise_comparison_path,
        diagnosis_path=realized_diagnosis_path,
        manifest=manifest,
    )


def _run_relative_cycle_sweep(
    config: SearchRunConfig,
    *,
    config_path: Path,
    output_root: Path,
    command_used: str | None,
) -> SweepArtifacts:
    started = perf_counter()
    context = load_relative_cycle_context()
    analysis = analyze_inherited_interface(context, "mid")
    parameters = enumerate_relative_cycle_parameters(
        carrier_sizes=config.carrier_sizes,
        route_shift_deltas=config.route_shift_deltas,
        weight_pairs=_search_weight_pairs(config),
    )
    sweep_id = f"sweep_{config.config_id}_seed{config.seed}"
    raw_dir = output_root / "results" / "raw" / sweep_id
    raw_cases_dir = raw_dir / "cases"
    derived_dir = output_root / "results" / "derived" / sweep_id
    notes_dir = output_root / "results" / "notes" / sweep_id
    raw_cases_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    resolved_config_path = raw_dir / "resolved_config.json"
    reproducibility_manifest_path = raw_dir / "reproducibility_manifest.json"
    summary_table_json_path = derived_dir / "summary_table.json"
    summary_table_csv_path = derived_dir / "summary_table.csv"
    top_candidates_path = derived_dir / "top_candidates.json"
    note_path = notes_dir / "sweep_note.md"

    rows: list[dict[str, object]] = []
    for case_parameters in parameters:
        case = build_relative_cycle_case(case_parameters, context=context)
        from sixbirds_foundations_v._recombination_support.core.recombination import compute_recombination_quotient

        quotient = compute_recombination_quotient(
            context,
            case.interface_id,
            case.assemblages,
            case.observable_family,
        )
        recombination_gap = compute_recombination_gap(quotient)
        eta_fiber = extract_eta_fiber_diagnostics(quotient)
        route_readability = compute_route_readability(case.route_readability_scenario)
        visibility = compute_conditional_visibility(
            case.unconditional_visibility_distribution,
            case.conditional_visibility_distributions,
        )
        history_ids = tuple(
            sorted(
                {
                    member.history_id
                    for assemblage in case.assemblages.values()
                    for member in assemblage.members
                }
            )
        )
        same_support = certify_same_support(context, case.interface_id, history_ids)
        factorization = evaluate_factorization_hook(quotient)
        class_label = _classify_run_label(
            quotient,
            factorization.status,
            current_quotient_size=analysis.current_quotient_size,
            predictive_quotient_size=analysis.predictive_quotient_size,
            route_readability_score=route_readability.score_value,
            visibility_recovery_gap=visibility.visibility_recovery_gap,
        ).value
        supports_erasure_recovery = (
            route_readability.score_value < Fraction(1, 1)
            and visibility.max_conditional_visibility > visibility.unconditional_visibility
            and visibility.visibility_recovery_gap > 0
        )
        viable_flagship_example = (
            supports_erasure_recovery
            and quotient.class_count > quotient.branchwise_quotient.class_count
            and eta_fiber.eta_max_fiber_size > 1
            and recombination_gap.metric_value > 0
            and factorization.status == AuditStatus.FAILED
        )
        case_id = case.parameters.case_id
        case_payload = {
            "case_id": case_id,
            "benchmark_id": case.benchmark_id,
            "interface_id": case.interface_id,
            "carrier_size": case.parameters.carrier_size,
            "route_shift_left": case.parameters.route_shift_left,
            "route_shift_right": case.parameters.route_shift_right,
            "route_shift_delta": case.parameters.route_shift_delta,
            "weight_left": str(case.parameters.weight_left),
            "weight_right": str(case.parameters.weight_right),
            "current_quotient_size": analysis.current_quotient_size,
            "predictive_quotient_size": analysis.predictive_quotient_size,
            "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
            "recombination_quotient_size": quotient.class_count,
            "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
            "route_readability_score": str(route_readability.score_value),
            "unconditional_visibility": str(visibility.unconditional_visibility),
            "max_conditional_visibility": str(visibility.max_conditional_visibility),
            "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
            "recombination_gap_value": str(recombination_gap.metric_value),
            "factorization_status": factorization.status.value,
            "class_label": class_label,
            "supports_erasure_recovery": supports_erasure_recovery,
            "viable_flagship_example": viable_flagship_example,
            "same_support_status": same_support.status.value,
            "branchwise_quotient": branchwise_quotient_payload(quotient.branchwise_quotient),
            "recombination_quotient": recombination_quotient_payload(quotient),
            "recombination_gap": recombination_gap_payload(recombination_gap),
            "eta_fiber": eta_fiber_payload(eta_fiber),
            "route_readability": route_readability_payload(route_readability),
            "conditional_visibility": conditional_visibility_payload(visibility),
            "factorization": factorization_audit_payload(factorization),
            "same_support": same_support_audit_payload(same_support),
        }
        case_artifact_path = raw_cases_dir / f"{case_id}.json"
        case_artifact_path.write_text(
            json.dumps(case_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        row = {
            "case_id": case_id,
            "carrier_size": case.parameters.carrier_size,
            "route_shift_left": case.parameters.route_shift_left,
            "route_shift_right": case.parameters.route_shift_right,
            "route_shift_delta": case.parameters.route_shift_delta,
            "weight_left": str(case.parameters.weight_left),
            "weight_right": str(case.parameters.weight_right),
            "current_quotient_size": analysis.current_quotient_size,
            "predictive_quotient_size": analysis.predictive_quotient_size,
            "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
            "recombination_quotient_size": quotient.class_count,
            "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
            "route_readability_score": str(route_readability.score_value),
            "unconditional_visibility": str(visibility.unconditional_visibility),
            "max_conditional_visibility": str(visibility.max_conditional_visibility),
            "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
            "recombination_gap_value": str(recombination_gap.metric_value),
            "factorization_status": factorization.status.value,
            "class_label": class_label,
            "supports_erasure_recovery": supports_erasure_recovery,
            "viable_flagship_example": viable_flagship_example,
            "artifact_path": _repo_relative_path(case_artifact_path, output_root),
        }
        rows.append(row)

    rows.sort(key=lambda row: row["case_id"])
    top_candidates = _promote_relative_cycle_candidates(rows, config)
    verdict = (
        "generalizes_ticket12_flagship"
        if top_candidates
        else "no_positive_regime_found"
    )
    summary_payload = {
        "sweep_id": sweep_id,
        "search_space_id": config.search_space_id,
        "case_count": len(rows),
        "rows": rows,
        "verdict": verdict,
    }
    summary_table_json_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_summary_csv(summary_table_csv_path, rows)
    top_candidates_payload = {
        "sweep_id": sweep_id,
        "verdict": verdict,
        "comparison_reference_run_id": config.comparison_run_id,
        "promoted_candidates": top_candidates,
    }
    top_candidates_path.write_text(
        json.dumps(top_candidates_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    normalized_config = normalize_config_payload(config)
    config_hash = compute_config_hash(config)
    reproducibility_manifest = {
        "sweep_id": sweep_id,
        "config_path": _repo_relative_path(config_path, output_root),
        "config_hash_sha256": config_hash,
        "command_used": command_used
        or f"python -m sixbirds_foundations_v._recombination_support.runner sweep --config {config_path}",
        "search_space_id": config.search_space_id,
        "case_count": len(rows),
        "output_paths": {
            "raw_dir": _repo_relative_path(raw_dir, output_root),
            "derived_dir": _repo_relative_path(derived_dir, output_root),
            "notes_dir": _repo_relative_path(notes_dir, output_root),
        },
        "validation_passed": True,
        "runtime_seconds": perf_counter() - started,
    }
    resolved_config_path.write_text(
        json.dumps(normalized_config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reproducibility_manifest_path.write_text(
        json.dumps(reproducibility_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    note_path.write_text(
        _build_relative_cycle_sweep_note(
            sweep_id=sweep_id,
            rows=rows,
            top_candidates=top_candidates,
            verdict=verdict,
        ),
        encoding="utf-8",
    )
    return SweepArtifacts(
        sweep_id=sweep_id,
        config_path=config_path,
        resolved_config_path=resolved_config_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
        summary_table_json_path=summary_table_json_path,
        summary_table_csv_path=summary_table_csv_path,
        top_candidates_path=top_candidates_path,
        collapse_summary_path=None,
        note_path=note_path,
        raw_cases_dir=raw_cases_dir,
    )


def _run_dissipative_collapse_sweep(
    config: SearchRunConfig,
    *,
    config_path: Path,
    output_root: Path,
    command_used: str | None,
) -> SweepArtifacts:
    started = perf_counter()
    context = load_relative_cycle_context()
    analysis = analyze_inherited_interface(context, "mid")
    anchor_parameters = normalize_relative_cycle_parameters(
        carrier_size=config.anchor_carrier_size or 0,
        route_shift_delta=config.anchor_route_shift_delta or 0,
        weight_left=config.anchor_weight_left or "",
        weight_right=config.anchor_weight_right or "",
    )
    noise_schedule = tuple(Fraction(noise) for noise in _search_noise_strengths(config))
    sweep_id = f"sweep_{config.config_id}_seed{config.seed}"
    raw_dir = output_root / "results" / "raw" / sweep_id
    raw_cases_dir = raw_dir / "cases"
    derived_dir = output_root / "results" / "derived" / sweep_id
    notes_dir = output_root / "results" / "notes" / sweep_id
    raw_cases_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    resolved_config_path = raw_dir / "resolved_config.json"
    reproducibility_manifest_path = raw_dir / "reproducibility_manifest.json"
    summary_table_json_path = derived_dir / "summary_table.json"
    summary_table_csv_path = derived_dir / "summary_table.csv"
    collapse_summary_path = derived_dir / "collapse_summary.json"
    note_path = notes_dir / "sweep_note.md"
    top_candidates_path = derived_dir / "top_candidates.json"

    rows: list[dict[str, object]] = []
    anchor_case_id = anchor_parameters.case_id
    for noise_strength in noise_schedule:
        case = build_dissipative_relative_cycle_case(
            anchor_parameters,
            noise_strength=noise_strength,
            context=context,
        )
        from sixbirds_foundations_v._recombination_support.core.recombination import compute_recombination_quotient

        quotient = compute_recombination_quotient(
            context,
            case.interface_id,
            case.assemblages,
            case.observable_family,
        )
        recombination_gap = compute_recombination_gap(quotient)
        eta_fiber = extract_eta_fiber_diagnostics(quotient)
        route_readability = compute_route_readability(case.route_readability_scenario)
        visibility = compute_conditional_visibility(
            case.unconditional_visibility_distribution,
            case.conditional_visibility_distributions,
        )
        history_ids = tuple(
            sorted(
                {
                    member.history_id
                    for assemblage in case.assemblages.values()
                    for member in assemblage.members
                }
            )
        )
        same_support = certify_same_support(context, case.interface_id, history_ids)
        factorization = evaluate_factorization_hook(quotient)
        exact_collapse = (
            quotient.branchwise_quotient.class_count == quotient.class_count
            and eta_fiber.eta_max_fiber_size == 1
            and recombination_gap.metric_value == 0
        )
        class_label = (
            RecombinationClassLabel.DISSIPATIVE.value
            if exact_collapse
            else _classify_run_label(
                quotient,
                factorization.status,
                current_quotient_size=analysis.current_quotient_size,
                predictive_quotient_size=analysis.predictive_quotient_size,
                route_readability_score=route_readability.score_value,
                visibility_recovery_gap=visibility.visibility_recovery_gap,
            ).value
        )
        collapse_status = (
            "exact_collapse"
            if exact_collapse
            else "attenuated"
            if noise_strength > 0
            else "signal"
        )
        case_id = f"{anchor_case_id}_lambda_{_fraction_token(noise_strength)}"
        case_payload = {
            "case_id": case_id,
            "anchor_case_id": anchor_case_id,
            "noise_strength": str(noise_strength),
            "carrier_size": anchor_parameters.carrier_size,
            "route_shift_left": anchor_parameters.route_shift_left,
            "route_shift_right": anchor_parameters.route_shift_right,
            "route_shift_delta": anchor_parameters.route_shift_delta,
            "weight_left": str(anchor_parameters.weight_left),
            "weight_right": str(anchor_parameters.weight_right),
            "current_quotient_size": analysis.current_quotient_size,
            "predictive_quotient_size": analysis.predictive_quotient_size,
            "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
            "recombination_quotient_size": quotient.class_count,
            "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
            "route_readability_score": str(route_readability.score_value),
            "unconditional_visibility": str(visibility.unconditional_visibility),
            "max_conditional_visibility": str(visibility.max_conditional_visibility),
            "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
            "recombination_gap_value": str(recombination_gap.metric_value),
            "factorization_status": factorization.status.value,
            "class_label": class_label,
            "collapse_status": collapse_status,
            "exact_collapse_observed_at_or_before_this_case": False,
            "same_support_status": same_support.status.value,
            "branchwise_quotient": branchwise_quotient_payload(quotient.branchwise_quotient),
            "recombination_quotient": recombination_quotient_payload(quotient),
            "recombination_gap": recombination_gap_payload(recombination_gap),
            "eta_fiber": eta_fiber_payload(eta_fiber),
            "route_readability": route_readability_payload(route_readability),
            "conditional_visibility": conditional_visibility_payload(visibility),
            "factorization": factorization_audit_payload(factorization),
            "same_support": same_support_audit_payload(same_support),
        }
        case_artifact_path = raw_cases_dir / f"{case_id}.json"
        case_artifact_path.write_text(
            json.dumps(case_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        rows.append(
            {
                "case_id": case_id,
                "anchor_case_id": anchor_case_id,
                "noise_strength": str(noise_strength),
                "carrier_size": anchor_parameters.carrier_size,
                "route_shift_delta": anchor_parameters.route_shift_delta,
                "weight_left": str(anchor_parameters.weight_left),
                "weight_right": str(anchor_parameters.weight_right),
                "current_quotient_size": analysis.current_quotient_size,
                "predictive_quotient_size": analysis.predictive_quotient_size,
                "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
                "recombination_quotient_size": quotient.class_count,
                "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
                "route_readability_score": str(route_readability.score_value),
                "unconditional_visibility": str(visibility.unconditional_visibility),
                "max_conditional_visibility": str(visibility.max_conditional_visibility),
                "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
                "recombination_gap_value": str(recombination_gap.metric_value),
                "factorization_status": factorization.status.value,
                "class_label": class_label,
                "collapse_status": collapse_status,
                "exact_collapse_observed_at_or_before_this_case": False,
                "artifact_path": _repo_relative_path(case_artifact_path, output_root),
            }
        )

    rows.sort(key=lambda row: Fraction(str(row["noise_strength"])))
    seen_collapse = False
    for row in rows:
        exact_collapse = (
            row["branchwise_quotient_size"] == row["recombination_quotient_size"]
            and row["eta_max_fiber_size"] == 1
            and Fraction(str(row["recombination_gap_value"])) == 0
        )
        seen_collapse = seen_collapse or exact_collapse
        row["exact_collapse_observed_at_or_before_this_case"] = seen_collapse

    summary_payload = {
        "sweep_id": sweep_id,
        "search_space_id": config.search_space_id,
        "case_count": len(rows),
        "rows": rows,
        "verdict": None,
    }
    collapse_summary = _build_dissipative_collapse_summary(anchor_case_id, rows)
    summary_payload["verdict"] = collapse_summary["verdict"]
    summary_table_json_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_dissipative_summary_csv(summary_table_csv_path, rows)
    collapse_summary_path.write_text(
        json.dumps(collapse_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    top_candidates_path.write_text(
        json.dumps(
            {
                "sweep_id": sweep_id,
                "verdict": collapse_summary["verdict"],
                "promoted_candidates": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    normalized_config = normalize_config_payload(config)
    config_hash = compute_config_hash(config)
    reproducibility_manifest = {
        "sweep_id": sweep_id,
        "config_path": _repo_relative_path(config_path, output_root),
        "config_hash_sha256": config_hash,
        "command_used": command_used
        or f"python -m sixbirds_foundations_v._recombination_support.runner sweep --config {config_path}",
        "search_space_id": config.search_space_id,
        "case_count": len(rows),
        "output_paths": {
            "raw_dir": _repo_relative_path(raw_dir, output_root),
            "derived_dir": _repo_relative_path(derived_dir, output_root),
            "notes_dir": _repo_relative_path(notes_dir, output_root),
        },
        "validation_passed": True,
        "runtime_seconds": perf_counter() - started,
    }
    resolved_config_path.write_text(
        json.dumps(normalized_config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reproducibility_manifest_path.write_text(
        json.dumps(reproducibility_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    note_path.write_text(
        _build_dissipative_sweep_note(sweep_id=sweep_id, collapse_summary=collapse_summary),
        encoding="utf-8",
    )
    return SweepArtifacts(
        sweep_id=sweep_id,
        config_path=config_path,
        resolved_config_path=resolved_config_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
        summary_table_json_path=summary_table_json_path,
        summary_table_csv_path=summary_table_csv_path,
        top_candidates_path=top_candidates_path,
        collapse_summary_path=collapse_summary_path,
        note_path=note_path,
        raw_cases_dir=raw_cases_dir,
    )


def _run_bounded_search(
    config: SearchRunConfig,
    *,
    config_path: Path,
    output_root: Path,
    command_used: str | None,
) -> SearchArtifacts:
    started = perf_counter()
    search_id = f"search_{config.config_id}_seed{config.seed}"
    raw_dir = output_root / "results" / "raw" / search_id
    raw_cases_dir = raw_dir / "cases"
    derived_dir = output_root / "results" / "derived" / search_id
    notes_dir = output_root / "results" / "notes" / search_id
    raw_cases_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    resolved_config_path = raw_dir / "resolved_config.json"
    reproducibility_manifest_path = raw_dir / "reproducibility_manifest.json"
    summary_table_json_path = derived_dir / "summary_table.json"
    summary_table_csv_path = derived_dir / "summary_table.csv"
    smoke_summary_path = derived_dir / "smoke_summary.json"
    note_path = notes_dir / "search_note.md"
    ranked_candidates_path = derived_dir / "ranked_candidates.json"
    promoted_candidates_path = derived_dir / "promoted_candidates.json"
    open_issues_path = derived_dir / "open_issues.json"

    case_specs = enumerate_search_space(config, repo_root=REPO_ROOT)
    rows: list[dict[str, object]] = []
    for case_spec in case_specs:
        case_payload = _evaluate_search_case(case_spec)
        case_artifact_path = raw_cases_dir / f"{case_spec.case_id}.json"
        case_artifact_path.write_text(
            json.dumps(case_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        row = {
            key: case_payload[key]
            for key in (
                "case_id",
                "search_space_id",
                "benchmark_id",
                "config_ref",
                "family_identifier",
                "carrier_size",
                "route_shift_left",
                "route_shift_right",
                "route_shift_delta",
                "weight_left",
                "weight_right",
                "current_quotient_size",
                "predictive_quotient_size",
                "branchwise_quotient_size",
                "recombination_quotient_size",
                "eta_max_fiber_size",
                "route_readability_score",
                "unconditional_visibility",
                "max_conditional_visibility",
                "visibility_recovery_gap",
                "recombination_gap_value",
                "factorization_status",
                "protocol_internalization_status",
                "flattening_status",
                "class_label",
                "classifier_rule_version",
                "classifier_rule_name",
            )
            if key in case_payload
        }
        row["artifact_path"] = _repo_relative_path(case_artifact_path, output_root)
        rows.append(row)

    rows.sort(key=lambda row: str(row["case_id"]))
    ranked_cases = rank_candidates(rows) if config.search_space_id == CYCLIC_SPACE_SEARCH_ID else []
    if ranked_cases:
        rows = []
        for ranked_case in ranked_cases:
            row = dict(ranked_case.row)
            row["promotion_rank"] = ranked_case.rank
            row["promotion_eligible"] = ranked_case.eligible
            rows.append(row)
    else:
        for row in rows:
            row["promotion_rank"] = None
            row["promotion_eligible"] = False

    summary_payload = {
        "search_id": search_id,
        "search_space_id": config.search_space_id,
        "case_count": len(rows),
        "rows": rows,
    }
    summary_table_json_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_search_summary_csv(summary_table_csv_path, rows)
    smoke_summary = _build_search_smoke_summary(
        search_id=search_id,
        search_space_id=config.search_space_id,
        rows=rows,
    )
    smoke_summary_path.write_text(
        json.dumps(smoke_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    realized_ranked_candidates_path: Path | None = None
    realized_promoted_candidates_path: Path | None = None
    realized_open_issues_path: Path | None = None
    if ranked_cases:
        promotion_limit = config.promotion_limit or 0
        ranked_candidates_payload = build_ranked_candidates_payload(
            search_id=search_id,
            search_space_id=config.search_space_id,
            ranked_cases=ranked_cases,
            promotion_limit=promotion_limit,
        )
        ranked_candidates_path.write_text(
            json.dumps(ranked_candidates_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        realized_ranked_candidates_path = ranked_candidates_path

        open_issues_payload = build_open_issues_payload(
            search_id=search_id,
            ranked_cases=ranked_cases,
            promotion_limit=promotion_limit,
        )
        open_issues_path.write_text(
            json.dumps(open_issues_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        realized_open_issues_path = open_issues_path

        promoted_candidates = _materialize_promoted_candidates(
            search_id=search_id,
            ranked_cases=ranked_cases,
            promotion_limit=promotion_limit,
            output_root=output_root,
            config_root=(REPO_ROOT if output_root.resolve() == REPO_ROOT.resolve() else output_root),
        )
        promoted_candidates_payload = build_promoted_candidates_payload(
            search_id=search_id,
            promoted_candidates=promoted_candidates,
        )
        promoted_candidates_path.write_text(
            json.dumps(promoted_candidates_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        realized_promoted_candidates_path = promoted_candidates_path

    normalized_config = normalize_config_payload(config)
    config_hash = compute_config_hash(config)
    reproducibility_manifest = {
        "search_id": search_id,
        "config_path": _repo_relative_path(config_path, output_root),
        "config_hash_sha256": config_hash,
        "command_used": command_used
        or f"python -m sixbirds_foundations_v._recombination_support.runner search --config {config_path}",
        "search_space_id": config.search_space_id,
        "case_count": len(rows),
        "output_paths": {
            "raw_dir": _repo_relative_path(raw_dir, output_root),
            "derived_dir": _repo_relative_path(derived_dir, output_root),
            "notes_dir": _repo_relative_path(notes_dir, output_root),
        },
        "validation_passed": True,
        "runtime_seconds": perf_counter() - started,
    }
    resolved_config_path.write_text(
        json.dumps(normalized_config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reproducibility_manifest_path.write_text(
        json.dumps(reproducibility_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    note_path.write_text(
        _build_search_note(
            search_id=search_id,
            smoke_summary=smoke_summary,
            promoted_candidates=json.loads(
                realized_promoted_candidates_path.read_text(encoding="utf-8")
            )
            if realized_promoted_candidates_path is not None
            else None,
            open_issues=json.loads(realized_open_issues_path.read_text(encoding="utf-8"))
            if realized_open_issues_path is not None
            else None,
        ),
        encoding="utf-8",
    )
    return SearchArtifacts(
        search_id=search_id,
        config_path=config_path,
        resolved_config_path=resolved_config_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
        summary_table_json_path=summary_table_json_path,
        summary_table_csv_path=summary_table_csv_path,
        smoke_summary_path=smoke_summary_path,
        note_path=note_path,
        raw_cases_dir=raw_cases_dir,
        ranked_candidates_path=realized_ranked_candidates_path,
        promoted_candidates_path=realized_promoted_candidates_path,
        open_issues_path=realized_open_issues_path,
    )


def _evaluate_search_case(case_spec: SearchCaseSpec) -> dict[str, object]:
    if case_spec.kind == "benchmark-config":
        return _evaluate_benchmark_search_case(case_spec)
    if case_spec.kind == "relative-cycle-parameter":
        return _evaluate_relative_cycle_search_case(case_spec)
    raise ValueError(f"unsupported search case kind {case_spec.kind}")


def _evaluate_benchmark_search_case(case_spec: SearchCaseSpec) -> dict[str, object]:
    if case_spec.benchmark_config_path is None:
        raise ValueError("benchmark-config search cases require a config path")
    config = BenchmarkRunConfig.model_validate_json(
        case_spec.benchmark_config_path.read_text(encoding="utf-8")
    )
    context = load_inherited_benchmark_context(config.benchmark_id)
    analysis = analyze_inherited_interface(context, config.interface_id)
    assemblages = resolve_assemblage_family(
        context,
        config.assemblage_family_id,
        config.interface_id,
    )
    observable_family = resolve_observable_family(
        context,
        config.observable_family_id,
        config.interface_id,
    )
    from sixbirds_foundations_v._recombination_support.core.recombination import compute_recombination_quotient

    quotient = compute_recombination_quotient(
        context,
        config.interface_id,
        assemblages,
        observable_family,
    )
    recombination_gap = compute_recombination_gap(quotient)
    eta_fiber = extract_eta_fiber_diagnostics(quotient)
    route_readability = compute_route_readability(
        resolve_route_readability_scenario(
            config.route_readability_scenario_id or "perfect_binary_route_recovery"
        )
    )
    unconditional_distribution, conditional_distributions = resolve_visibility_scenario(
        config.visibility_scenario_id or "binary_visibility_recovery"
    )
    visibility = compute_conditional_visibility(
        unconditional_distribution,
        conditional_distributions,
    )
    factorization = evaluate_factorization_hook(quotient)
    protocol_audit = _build_protocol_audit(config)
    flattening_audit = _build_flattening_audit(
        config,
        quotient_class_count=quotient.class_count,
        branchwise_class_count=quotient.branchwise_quotient.class_count,
        eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
        recombination_gap_value=recombination_gap.metric_value,
        factorization_status=factorization.status,
    )
    outcome = classify_case(
        ClassificationInput(
            current_quotient_size=analysis.current_quotient_size,
            predictive_quotient_size=analysis.predictive_quotient_size,
            branchwise_quotient_size=quotient.branchwise_quotient.class_count,
            recombination_quotient_size=quotient.class_count,
            eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
            recombination_gap_value=recombination_gap.metric_value,
            route_readability_score=route_readability.score_value,
            unconditional_visibility=visibility.unconditional_visibility,
            max_conditional_visibility=visibility.max_conditional_visibility,
            visibility_recovery_gap=visibility.visibility_recovery_gap,
            factorization_status=factorization.status,
            search_space_id=case_spec.search_space_id,
            benchmark_id=config.benchmark_id,
            protocol_internalization_status=protocol_audit.status,
        )
    )
    return {
        "case_id": case_spec.case_id,
        "search_space_id": case_spec.search_space_id,
        "benchmark_id": config.benchmark_id,
        "config_ref": _repo_relative_path(case_spec.benchmark_config_path, REPO_ROOT),
        "family_identifier": config.assemblage_family_id,
        "current_quotient_size": analysis.current_quotient_size,
        "predictive_quotient_size": analysis.predictive_quotient_size,
        "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
        "recombination_quotient_size": quotient.class_count,
        "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
        "route_readability_score": str(route_readability.score_value),
        "unconditional_visibility": str(visibility.unconditional_visibility),
        "max_conditional_visibility": str(visibility.max_conditional_visibility),
        "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
        "recombination_gap_value": str(recombination_gap.metric_value),
        "factorization_status": factorization.status.value,
        "protocol_internalization_status": protocol_audit.status.value,
        "flattening_status": flattening_audit.status.value,
        "class_label": outcome.label.value,
        "classifier_rule_version": outcome.rule_version,
        "classifier_rule_name": outcome.rule_name,
    }


def _evaluate_relative_cycle_search_case(case_spec: SearchCaseSpec) -> dict[str, object]:
    parameters = normalize_relative_cycle_parameters(
        carrier_size=int(case_spec.parameters["carrier_size"]),
        route_shift_delta=int(case_spec.parameters["route_shift_delta"]),
        weight_left=str(case_spec.parameters["weight_left"]),
        weight_right=str(case_spec.parameters["weight_right"]),
    )
    context = load_relative_cycle_context()
    analysis = analyze_inherited_interface(context, "mid")
    case = build_relative_cycle_case(parameters, context=context)
    from sixbirds_foundations_v._recombination_support.core.recombination import compute_recombination_quotient

    quotient = compute_recombination_quotient(
        context,
        case.interface_id,
        case.assemblages,
        case.observable_family,
    )
    recombination_gap = compute_recombination_gap(quotient)
    eta_fiber = extract_eta_fiber_diagnostics(quotient)
    route_readability = compute_route_readability(case.route_readability_scenario)
    visibility = compute_conditional_visibility(
        case.unconditional_visibility_distribution,
        case.conditional_visibility_distributions,
    )
    factorization = evaluate_factorization_hook(quotient)
    outcome = classify_case(
        ClassificationInput(
            current_quotient_size=analysis.current_quotient_size,
            predictive_quotient_size=analysis.predictive_quotient_size,
            branchwise_quotient_size=quotient.branchwise_quotient.class_count,
            recombination_quotient_size=quotient.class_count,
            eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
            recombination_gap_value=recombination_gap.metric_value,
            route_readability_score=route_readability.score_value,
            unconditional_visibility=visibility.unconditional_visibility,
            max_conditional_visibility=visibility.max_conditional_visibility,
            visibility_recovery_gap=visibility.visibility_recovery_gap,
            factorization_status=factorization.status,
            search_space_id=case_spec.search_space_id,
            benchmark_id=case_spec.benchmark_id,
        )
    )
    return {
        "case_id": case_spec.case_id,
        "search_space_id": case_spec.search_space_id,
        "benchmark_id": case_spec.benchmark_id,
        "config_ref": None,
        "family_identifier": "relative_cycle_positive_family",
        "carrier_size": parameters.carrier_size,
        "route_shift_left": parameters.route_shift_left,
        "route_shift_right": parameters.route_shift_right,
        "route_shift_delta": parameters.route_shift_delta,
        "weight_left": str(parameters.weight_left),
        "weight_right": str(parameters.weight_right),
        "current_quotient_size": analysis.current_quotient_size,
        "predictive_quotient_size": analysis.predictive_quotient_size,
        "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
        "recombination_quotient_size": quotient.class_count,
        "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
        "route_readability_score": str(route_readability.score_value),
        "unconditional_visibility": str(visibility.unconditional_visibility),
        "max_conditional_visibility": str(visibility.max_conditional_visibility),
        "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
        "recombination_gap_value": str(recombination_gap.metric_value),
        "factorization_status": factorization.status.value,
        "protocol_internalization_status": AuditStatus.SKIPPED.value,
        "flattening_status": AuditStatus.SKIPPED.value,
        "class_label": outcome.label.value,
        "classifier_rule_version": outcome.rule_version,
        "classifier_rule_name": outcome.rule_name,
    }


def _evaluate_relative_cycle_parameter_row(
    parameters,
    *,
    candidate_id: str,
    reference_run_id: str,
) -> dict[str, object]:
    context = load_relative_cycle_context()
    analysis = analyze_inherited_interface(context, "mid")
    case = build_relative_cycle_case(parameters, context=context)
    from sixbirds_foundations_v._recombination_support.core.recombination import compute_recombination_quotient

    quotient = compute_recombination_quotient(
        context,
        case.interface_id,
        case.assemblages,
        case.observable_family,
    )
    recombination_gap = compute_recombination_gap(quotient)
    eta_fiber = extract_eta_fiber_diagnostics(quotient)
    route_readability = compute_route_readability(case.route_readability_scenario)
    visibility = compute_conditional_visibility(
        case.unconditional_visibility_distribution,
        case.conditional_visibility_distributions,
    )
    factorization = evaluate_factorization_hook(quotient)
    outcome = classify_case(
        ClassificationInput(
            current_quotient_size=analysis.current_quotient_size,
            predictive_quotient_size=analysis.predictive_quotient_size,
            branchwise_quotient_size=quotient.branchwise_quotient.class_count,
            recombination_quotient_size=quotient.class_count,
            eta_max_fiber_size=eta_fiber.eta_max_fiber_size,
            recombination_gap_value=recombination_gap.metric_value,
            route_readability_score=route_readability.score_value,
            unconditional_visibility=visibility.unconditional_visibility,
            max_conditional_visibility=visibility.max_conditional_visibility,
            visibility_recovery_gap=visibility.visibility_recovery_gap,
            factorization_status=factorization.status,
            search_space_id=CYCLIC_SPACE_SEARCH_ID,
            benchmark_id=RELATIVE_CYCLE_BENCHMARK_ID,
        )
    )
    return {
        "candidate_id": candidate_id,
        "reference_run_id": reference_run_id,
        "case_id": parameters.case_id,
        "carrier_size": parameters.carrier_size,
        "route_shift_delta": parameters.route_shift_delta,
        "weight_left": str(parameters.weight_left),
        "weight_right": str(parameters.weight_right),
        "current_quotient_size": analysis.current_quotient_size,
        "predictive_quotient_size": analysis.predictive_quotient_size,
        "branchwise_quotient_size": quotient.branchwise_quotient.class_count,
        "recombination_quotient_size": quotient.class_count,
        "eta_max_fiber_size": eta_fiber.eta_max_fiber_size,
        "route_readability_score": str(route_readability.score_value),
        "unconditional_visibility": str(visibility.unconditional_visibility),
        "max_conditional_visibility": str(visibility.max_conditional_visibility),
        "visibility_recovery_gap": str(visibility.visibility_recovery_gap),
        "recombination_gap_value": str(recombination_gap.metric_value),
        "factorization_status": factorization.status.value,
        "class_label": outcome.label.value,
        "classifier_rule_version": outcome.rule_version,
        "classifier_rule_name": outcome.rule_name,
    }


def _run_promoted_candidate_robustness(
    config: SearchRunConfig,
    *,
    config_path: Path,
    output_root: Path,
    command_used: str | None,
) -> RobustnessArtifacts:
    started = perf_counter()
    robustness_id = f"robustness_{config.config_id}_seed{config.seed}"
    raw_dir = output_root / "results" / "raw" / robustness_id
    raw_candidates_dir = raw_dir / "candidates"
    derived_dir = output_root / "results" / "derived" / robustness_id
    per_candidate_dir = derived_dir / "per_candidate"
    notes_dir = output_root / "results" / "notes" / robustness_id
    raw_candidates_dir.mkdir(parents=True, exist_ok=True)
    per_candidate_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    resolved_config_path = raw_dir / "resolved_config.json"
    reproducibility_manifest_path = raw_dir / "reproducibility_manifest.json"
    summary_table_json_path = derived_dir / "robustness_summary_table.json"
    summary_table_csv_path = derived_dir / "robustness_summary_table.csv"
    top_stable_cases_path = derived_dir / "top_stable_cases.json"
    cases_to_demote_path = derived_dir / "cases_to_demote.json"
    note_path = notes_dir / "robustness_note.md"

    references = load_promoted_candidate_references(REPO_ROOT)
    threshold_profiles = threshold_profiles_from_config(config.threshold_profiles)
    records: list[dict[str, object]] = []
    for candidate_id in config.promoted_candidate_ids or ():
        candidate = references[candidate_id]
        carrier_sizes = tuple(
            (config.candidate_carrier_sizes or {}).get(
                candidate_id,
                default_candidate_carrier_sizes(candidate),
            )
        )
        parameters = enumerate_candidate_neighborhood(
            candidate,
            carrier_sizes=carrier_sizes,
            route_shift_deltas=tuple(config.local_route_shift_deltas or ()),
            weight_lefts=tuple(config.local_weight_lefts or ()),
        )
        candidate_cases_dir = raw_candidates_dir / candidate_id / "cases"
        candidate_cases_dir.mkdir(parents=True, exist_ok=True)
        case_rows: list[dict[str, object]] = []
        for parameter in parameters:
            row = _evaluate_relative_cycle_parameter_row(
                parameter,
                candidate_id=candidate_id,
                reference_run_id=candidate.reference_run_id,
            )
            case_path = candidate_cases_dir / f"{parameter.case_id}.json"
            case_path.write_text(
                json.dumps(row, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            case_rows.append(row)
        case_rows.sort(
            key=lambda row: (
                int(row["carrier_size"]),
                int(row["route_shift_delta"]),
                Fraction(str(row["weight_left"])),
                str(row["case_id"]),
            )
        )
        profile_results = evaluate_threshold_profiles(case_rows, threshold_profiles)
        record = build_candidate_robustness_record(
            candidate=candidate,
            case_rows=case_rows,
            profile_results=profile_results,
        )
        record["candidate_cases_dir"] = _repo_relative_path(candidate_cases_dir, output_root)
        (per_candidate_dir / f"{candidate_id}.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        records.append(record)

    summary_rows = build_robustness_summary_rows(records)
    summary_payload = {
        "robustness_id": robustness_id,
        "robustness_rule_version": "ticket18.robustness.v1",
        "candidate_count": len(summary_rows),
        "rows": summary_rows,
    }
    summary_table_json_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_robustness_summary_csv(summary_table_csv_path, summary_rows)

    top_stable_payload = build_top_stable_cases_payload(
        robustness_id=robustness_id,
        records=records,
    )
    top_stable_cases_path.write_text(
        json.dumps(top_stable_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    cases_to_demote_payload = build_cases_to_demote_payload(
        robustness_id=robustness_id,
        records=records,
    )
    cases_to_demote_path.write_text(
        json.dumps(cases_to_demote_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    normalized_config = normalize_config_payload(config)
    config_hash = compute_config_hash(config)
    reproducibility_manifest = {
        "robustness_id": robustness_id,
        "config_path": _repo_relative_path(config_path, output_root),
        "config_hash_sha256": config_hash,
        "command_used": command_used
        or f"python -m sixbirds_foundations_v._recombination_support.runner robustness --config {config_path}",
        "search_space_id": config.search_space_id,
        "candidate_count": len(records),
        "output_paths": {
            "raw_dir": _repo_relative_path(raw_dir, output_root),
            "derived_dir": _repo_relative_path(derived_dir, output_root),
            "notes_dir": _repo_relative_path(notes_dir, output_root),
        },
        "validation_passed": True,
        "runtime_seconds": perf_counter() - started,
    }
    resolved_config_path.write_text(
        json.dumps(normalized_config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reproducibility_manifest_path.write_text(
        json.dumps(reproducibility_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    note_path.write_text(
        _build_robustness_note(
            robustness_id=robustness_id,
            summary_rows=summary_rows,
            cases_to_demote_payload=cases_to_demote_payload,
        ),
        encoding="utf-8",
    )
    return RobustnessArtifacts(
        robustness_id=robustness_id,
        config_path=config_path,
        resolved_config_path=resolved_config_path,
        reproducibility_manifest_path=reproducibility_manifest_path,
        summary_table_json_path=summary_table_json_path,
        summary_table_csv_path=summary_table_csv_path,
        top_stable_cases_path=top_stable_cases_path,
        cases_to_demote_path=cases_to_demote_path,
        note_path=note_path,
        raw_candidates_dir=raw_candidates_dir,
    )


def _update_run_ledger(ledger_path: Path, entry: dict[str, object]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    else:
        ledger = {"schema_version": "recombination-run-ledger.v1", "entries": {}}
    ledger["entries"][entry["run_id"]] = entry
    ordered_entries = {
        run_id: ledger["entries"][run_id]
        for run_id in sorted(ledger["entries"])
    }
    ledger["entries"] = ordered_entries
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _promote_relative_cycle_candidates(
    rows: list[dict[str, object]],
    config: SearchRunConfig,
) -> list[dict[str, object]]:
    promotion_limit = config.promotion_limit or config.limit
    viable_rows = [row for row in rows if row["viable_flagship_example"]]
    viable_rows.sort(
        key=lambda row: (
            -int(bool(row["viable_flagship_example"])),
            -Fraction(str(row["recombination_gap_value"])),
            -int(row["eta_max_fiber_size"]),
            -Fraction(str(row["visibility_recovery_gap"])),
            str(row["case_id"]),
        )
    )
    promoted = viable_rows[:promotion_limit]
    return [
        {
            "case_id": row["case_id"],
            "carrier_size": row["carrier_size"],
            "route_shift_left": row["route_shift_left"],
            "route_shift_right": row["route_shift_right"],
            "route_shift_delta": row["route_shift_delta"],
            "weight_left": row["weight_left"],
            "weight_right": row["weight_right"],
            "branchwise_quotient_size": row["branchwise_quotient_size"],
            "recombination_quotient_size": row["recombination_quotient_size"],
            "eta_max_fiber_size": row["eta_max_fiber_size"],
            "route_readability_score": row["route_readability_score"],
            "unconditional_visibility": row["unconditional_visibility"],
            "max_conditional_visibility": row["max_conditional_visibility"],
            "visibility_recovery_gap": row["visibility_recovery_gap"],
            "recombination_gap_value": row["recombination_gap_value"],
            "factorization_status": row["factorization_status"],
            "class_label": row["class_label"],
            "verdict": "viable_flagship_example",
            "artifact_paths": {
                "case_artifact_path": row["artifact_path"],
            },
        }
        for row in promoted
    ]


def _build_dissipative_collapse_summary(
    anchor_case_id: str,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    exact_collapse_noise: str | None = None
    last_positive_noise: str | None = None
    gap_values = [Fraction(str(row["recombination_gap_value"])) for row in rows]
    eta_values = [int(row["eta_max_fiber_size"]) for row in rows]
    for row in rows:
        noise_strength = str(row["noise_strength"])
        exact_collapse = (
            row["branchwise_quotient_size"] == row["recombination_quotient_size"]
            and row["eta_max_fiber_size"] == 1
            and Fraction(str(row["recombination_gap_value"])) == 0
        )
        if exact_collapse and exact_collapse_noise is None:
            exact_collapse_noise = noise_strength
        if Fraction(str(row["recombination_gap_value"])) > 0:
            last_positive_noise = noise_strength
    gap_monotone_nonincreasing = all(
        left >= right for left, right in zip(gap_values, gap_values[1:], strict=False)
    )
    eta_monotone_nonincreasing = all(
        left >= right for left, right in zip(eta_values, eta_values[1:], strict=False)
    )
    recommended_noise_regime = {
        "signal_noise": str(rows[0]["noise_strength"]),
        "near_collapse_noise": _highest_attenuated_noise(rows),
        "exact_collapse_noise": exact_collapse_noise,
    }
    verdict = (
        "exact_dissipative_collapse_observed"
        if exact_collapse_noise is not None
        else "attenuation_without_exact_collapse"
        if gap_values[-1] < gap_values[0] or eta_values[-1] < eta_values[0]
        else "no_meaningful_attenuation_observed"
    )
    return {
        "anchor_case_id": anchor_case_id,
        "noise_schedule": [str(row["noise_strength"]) for row in rows],
        "exact_collapse_observed": exact_collapse_noise is not None,
        "first_exact_collapse_noise": exact_collapse_noise,
        "last_positive_noise": last_positive_noise,
        "max_recombination_gap_at_noise0": str(gap_values[0]),
        "min_recombination_gap_at_noise1": str(gap_values[-1]),
        "gap_monotone_nonincreasing": gap_monotone_nonincreasing,
        "eta_monotone_nonincreasing": eta_monotone_nonincreasing,
        "recommended_noise_regime": recommended_noise_regime,
        "verdict": verdict,
    }


def _write_summary_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "case_id",
        "carrier_size",
        "route_shift_left",
        "route_shift_right",
        "route_shift_delta",
        "weight_left",
        "weight_right",
        "current_quotient_size",
        "predictive_quotient_size",
        "branchwise_quotient_size",
        "recombination_quotient_size",
        "eta_max_fiber_size",
        "route_readability_score",
        "unconditional_visibility",
        "max_conditional_visibility",
        "visibility_recovery_gap",
        "recombination_gap_value",
        "factorization_status",
        "class_label",
        "supports_erasure_recovery",
        "viable_flagship_example",
        "artifact_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fieldnames})


def _write_dissipative_summary_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "case_id",
        "anchor_case_id",
        "noise_strength",
        "carrier_size",
        "route_shift_delta",
        "weight_left",
        "weight_right",
        "current_quotient_size",
        "predictive_quotient_size",
        "branchwise_quotient_size",
        "recombination_quotient_size",
        "eta_max_fiber_size",
        "route_readability_score",
        "unconditional_visibility",
        "max_conditional_visibility",
        "visibility_recovery_gap",
        "recombination_gap_value",
        "factorization_status",
        "class_label",
        "collapse_status",
        "exact_collapse_observed_at_or_before_this_case",
        "artifact_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fieldnames})


def _write_search_summary_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "case_id",
        "search_space_id",
        "benchmark_id",
        "config_ref",
        "family_identifier",
        "carrier_size",
        "route_shift_left",
        "route_shift_right",
        "route_shift_delta",
        "weight_left",
        "weight_right",
        "current_quotient_size",
        "predictive_quotient_size",
        "branchwise_quotient_size",
        "recombination_quotient_size",
        "eta_max_fiber_size",
        "route_readability_score",
        "unconditional_visibility",
        "max_conditional_visibility",
        "visibility_recovery_gap",
        "recombination_gap_value",
        "factorization_status",
        "protocol_internalization_status",
        "flattening_status",
        "class_label",
        "classifier_rule_version",
        "classifier_rule_name",
        "promotion_rank",
        "promotion_eligible",
        "artifact_path",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def _write_robustness_summary_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "candidate_id",
        "reference_run_id",
        "physical_case_count",
        "lenient_survival_fraction",
        "default_survival_fraction",
        "strict_survival_fraction",
        "min_recombination_gap_value",
        "min_visibility_recovery_gap",
        "max_route_readability_score",
        "min_eta_max_fiber_size",
        "recommended_status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def _materialize_promoted_candidates(
    *,
    search_id: str,
    ranked_cases,
    promotion_limit: int,
    output_root: Path,
    config_root: Path,
) -> list[dict[str, object]]:
    promoted = [
        case
        for case in ranked_cases
        if case.eligible and case.rank <= promotion_limit
    ]
    promoted_payloads: list[dict[str, object]] = []
    for case in promoted:
        row = dict(case.row)
        config_path = write_promoted_benchmark_config(
            row,
            rank=case.rank,
            config_root=config_root,
        )
        config = load_run_config(config_path)
        artifacts = run_config(
            config,
            config_path=config_path,
            output_root=output_root,
            command_used=(
                "python -m sixbirds_foundations_v._recombination_support.runner search "
                f"--config configs/recombination/search/{search_id.removeprefix('search_').removesuffix('_seed0')}.json"
            ),
        )
        promoted_payloads.append(
            {
                "case_id": row["case_id"],
                "promotion_rank": case.rank,
                "carrier_size": row["carrier_size"],
                "route_shift_left": row["route_shift_left"],
                "route_shift_right": row["route_shift_right"],
                "route_shift_delta": row["route_shift_delta"],
                "weight_left": row["weight_left"],
                "weight_right": row["weight_right"],
                "branchwise_quotient_size": row["branchwise_quotient_size"],
                "recombination_quotient_size": row["recombination_quotient_size"],
                "eta_max_fiber_size": row["eta_max_fiber_size"],
                "route_readability_score": row["route_readability_score"],
                "unconditional_visibility": row["unconditional_visibility"],
                "max_conditional_visibility": row["max_conditional_visibility"],
                "visibility_recovery_gap": row["visibility_recovery_gap"],
                "recombination_gap_value": row["recombination_gap_value"],
                "factorization_status": row["factorization_status"],
                "class_label": row["class_label"],
                "promotion_eligible": True,
                "config_path": _repo_relative_path(config_path, output_root),
                "artifact_paths": {
                    "result_manifest_path": _repo_relative_path(
                        artifacts.result_manifest_path,
                        output_root,
                    ),
                    "reproducibility_manifest_path": _repo_relative_path(
                        artifacts.reproducibility_manifest_path,
                        output_root,
                    ),
                    "diagnostics_summary_path": _repo_relative_path(
                        artifacts.diagnostics_summary_path,
                        output_root,
                    ),
                    "note_path": _repo_relative_path(artifacts.note_path, output_root),
                },
                "run_id": artifacts.run_id,
            }
        )
    return promoted_payloads


def _build_search_smoke_summary(
    *,
    search_id: str,
    search_space_id: str,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    label_counts: dict[str, int] = {}
    representative_cases: dict[str, str] = {}
    for row in rows:
        label = str(row["class_label"])
        label_counts[label] = label_counts.get(label, 0) + 1
        representative_cases.setdefault(label, str(row["case_id"]))
    if search_space_id == NULL_SPACE_SEARCH_ID:
        allowed_labels = {
            RecombinationClassLabel.CLASSICAL_MIXTURE.value,
            RecombinationClassLabel.MEMORY_ONLY.value,
            RecombinationClassLabel.MARKED_SUPPRESSION.value,
        }
        verdict = (
            "branchwise_factorized_null_space_classifies_cleanly"
            if set(label_counts).issubset(allowed_labels)
            else "branchwise_factorized_null_space_emitted_unexpected_label"
        )
    else:
        verdict = (
            "coherent_positive_regime_found"
            if RecombinationClassLabel.COHERENT_BRANCH_CANDIDATE.value in label_counts
            else "no_coherent_positive_regime_found"
        )
    return {
        "search_id": search_id,
        "search_space_id": search_space_id,
        "case_count": len(rows),
        "label_counts": label_counts,
        "representative_case_ids": representative_cases,
        "verdict": verdict,
    }


def _build_search_note(
    *,
    search_id: str,
    smoke_summary: dict[str, object],
    promoted_candidates: dict[str, object] | None,
    open_issues: dict[str, object] | None,
) -> str:
    label_counts = smoke_summary["label_counts"]
    representatives = smoke_summary["representative_case_ids"]
    promoted_count = (
        len(promoted_candidates["promoted_candidates"])
        if promoted_candidates is not None
        else 0
    )
    unclassified_count = (
        len(open_issues["unclassified_cases"])
        if open_issues is not None
        else 0
    )
    return "\n".join(
        [
            f"# Search {search_id}",
            "",
            f"- search space id: `{smoke_summary['search_space_id']}`",
            f"- case count: `{smoke_summary['case_count']}`",
            f"- label counts: `{label_counts}`",
            f"- representative case ids: `{representatives}`",
            f"- verdict: `{smoke_summary['verdict']}`",
            f"- promoted candidate count: `{promoted_count}`",
            f"- unclassified case count: `{unclassified_count}`",
            "",
            "## Interpretation",
            "",
            (
                "The bounded search space classified cleanly with deterministic labels and produced a usable promoted shortlist."
                if promoted_count > 0
                else "The bounded search completed and classified deterministically, but it did not materialize a promoted shortlist."
            ),
            "",
        ]
    )


def _build_robustness_note(
    *,
    robustness_id: str,
    summary_rows: list[dict[str, object]],
    cases_to_demote_payload: dict[str, object],
) -> str:
    stable_candidates = [
        row["candidate_id"] for row in summary_rows if row["recommended_status"] == "stable"
    ]
    demotions = [case["candidate_id"] for case in cases_to_demote_payload["cases_to_demote"]]
    return "\n".join(
        [
            f"# Robustness {robustness_id}",
            "",
            f"- candidate count: `{len(summary_rows)}`",
            f"- stable candidates: `{stable_candidates}`",
            f"- cases to demote: `{demotions}`",
            f"- demotion verdict: `{cases_to_demote_payload['verdict']}`",
            "",
            "## Interpretation",
            "",
            (
                "The promoted shortlist was screened under comparable local perturbations and explicit threshold profiles."
            ),
            "",
        ]
    )


def _build_relative_cycle_sweep_note(
    *,
    sweep_id: str,
    rows: list[dict[str, object]],
    top_candidates: list[dict[str, object]],
    verdict: str,
) -> str:
    positive_case_count = sum(1 for row in rows if row["viable_flagship_example"])
    if top_candidates:
        interpretation = (
            "The relative-cycle family generalizes the Ticket 12 success: the sweep found "
            f"{positive_case_count} viable flagship cases, and the top promoted regime(s) "
            "show unreadable route channels together with positive conditional recovery and "
            "strict recombination refinement."
        )
    else:
        interpretation = (
            "The sweep completed, but no viable flagship regime was promoted. The relative-cycle "
            "family does not currently generalize Ticket 12 strongly enough to support a broader "
            "positive-family claim."
        )
    return "\n".join(
        [
            f"# Sweep {sweep_id}",
            "",
            f"- case count: `{len(rows)}`",
            f"- promoted candidate count: `{len(top_candidates)}`",
            f"- verdict: `{verdict}`",
            "",
            "## Interpretation",
            "",
            interpretation,
            "",
        ]
    )


def _build_dissipative_sweep_note(
    *,
    sweep_id: str,
    collapse_summary: dict[str, object],
) -> str:
    recommended = collapse_summary["recommended_noise_regime"]
    return "\n".join(
        [
            f"# Sweep {sweep_id}",
            "",
            f"- anchor case id: `{collapse_summary['anchor_case_id']}`",
            f"- exact collapse observed: `{collapse_summary['exact_collapse_observed']}`",
            f"- first exact collapse noise: `{collapse_summary['first_exact_collapse_noise']}`",
            f"- last positive noise: `{collapse_summary['last_positive_noise']}`",
            f"- verdict: `{collapse_summary['verdict']}`",
            f"- recommended noise regime: `{recommended}`",
            "",
            "## Interpretation",
            "",
            (
                "The dissipative schedule shows explicit washout all the way to exact collapse."
                if collapse_summary["exact_collapse_observed"]
                else "The dissipative schedule attenuates the recombination signal but does not reach exact collapse on the tested schedule."
            ),
            "",
        ]
    )


def _search_weight_pairs(
    config: SearchRunConfig,
) -> tuple[tuple[str, str], ...] | None:
    if config.weight_pairs is not None:
        return tuple(config.weight_pairs)
    return tuple(weight_pair_strings(DEFAULT_WEIGHT_PAIRS))


def _search_noise_strengths(config: SearchRunConfig) -> tuple[str, ...]:
    if config.noise_strengths is not None:
        return tuple(config.noise_strengths)
    return tuple(noise_strength_strings(DEFAULT_DISSIPATIVE_NOISE_STRENGTHS))


def _uses_dynamic_relative_cycle_case(config: BenchmarkRunConfig) -> bool:
    return (
        config.benchmark_id == "relative_cycle_carrier_base"
        and config.carrier_size is not None
        and config.route_shift_delta is not None
        and config.weight_left is not None
        and config.weight_right is not None
    )


def _highest_attenuated_noise(rows: list[dict[str, object]]) -> str | None:
    attenuated = [
        str(row["noise_strength"])
        for row in rows
        if row["collapse_status"] == "attenuated"
    ]
    return attenuated[-1] if attenuated else None


def _fraction_token(value: Fraction) -> str:
    return f"{value.numerator}of{value.denominator}"


def _comparison_artifact_name(config: BenchmarkRunConfig) -> str | None:
    if config.comparison_run_id is None:
        return None
    if _is_protocol_internalization_partner(config):
        return "protocol_internalization_comparison.json"
    if _is_flattening_completion_partner(config):
        return "flattening_completion_comparison.json"
    return "paired_marked_comparison.json"


def _is_protocol_internalization_partner(config: BenchmarkRunConfig) -> bool:
    protocol_tags = {"protocol_trap", "protocol_artifact"}
    return bool(protocol_tags.intersection(config.tags)) and "internalized" in config.tags


def _is_flattening_completion_partner(config: BenchmarkRunConfig) -> bool:
    return "flattening_control" in config.tags and "completion_partner" in config.tags


def _is_positive_signal(
    *,
    quotient_class_count: int,
    branchwise_class_count: int,
    eta_max_fiber_size: int,
    recombination_gap_value: Fraction,
    factorization_status: AuditStatus,
) -> bool:
    return (
        quotient_class_count > branchwise_class_count
        and eta_max_fiber_size > 1
        and recombination_gap_value > 0
        and factorization_status == AuditStatus.FAILED
    )


def _build_protocol_audit(
    config: BenchmarkRunConfig,
):
    if not {"protocol_trap", "protocol_artifact"}.intersection(config.tags):
        return build_protocol_internalization_audit(
            status=AuditStatus.SKIPPED,
            detail="protocol/internalization audit is not active for this benchmark run",
            evidence_refs=(),
        )
    if "uninternalized" in config.tags:
        return build_protocol_internalization_audit(
            status=AuditStatus.FAILED,
            detail=(
                "a scheduler bit remains external to the declared support/current record, "
                "so the apparent recombination signal is treated as a protocol artifact"
            ),
            uninternalized_entities=("scheduler_bit",),
            failure_code="uninternalized_scheduler_state",
        )
    return build_protocol_internalization_audit(
        status=AuditStatus.PASSED,
        detail=(
            "the scheduler bit is explicitly internalized in the paired benchmark, so "
            "the protocol artifact is no longer external to the declared structure"
        ),
        evidence_refs=(),
    )


def _build_flattening_audit(
    config: BenchmarkRunConfig,
    *,
    quotient_class_count: int,
    branchwise_class_count: int,
    eta_max_fiber_size: int,
    recombination_gap_value: Fraction,
    factorization_status: AuditStatus,
):
    if "flattening_control" not in config.tags:
        return build_flattening_completion_audit(
            status=AuditStatus.SKIPPED,
            detail="flattening/completion audit is not active for this benchmark run",
            comparison_artifact_refs=(),
        )
    survives = _is_positive_signal(
        quotient_class_count=quotient_class_count,
        branchwise_class_count=branchwise_class_count,
        eta_max_fiber_size=eta_max_fiber_size,
        recombination_gap_value=recombination_gap_value,
        factorization_status=factorization_status,
    )
    if survives:
        detail = (
            "the promoted candidate remains recombination-positive under the selected "
            "flattening/completion control"
            if "completion_partner" in config.tags
            else "the promoted candidate was materialized as the reference positive anchor for the flattening/completion check"
        )
        return build_flattening_completion_audit(
            status=AuditStatus.PASSED,
            detail=detail,
            comparison_artifact_refs=(),
        )
    failure_code = (
        "completion_removes_positive_effect"
        if "completion_partner" in config.tags
        else "reference_positive_not_reproduced"
    )
    detail = (
        "the selected completion partner removes or reclassifies the promoted positive effect"
        if "completion_partner" in config.tags
        else "the reference positive candidate did not reproduce the promoted positive regime"
    )
    return build_flattening_completion_audit(
        status=AuditStatus.FAILED,
        detail=detail,
        comparison_artifact_refs=(),
        failure_code=failure_code,
    )


def _refresh_ticket15_artifact_controls_summary(output_root: Path) -> None:
    protocol_path = _first_existing_path(
        output_root,
        (
            Path("results")
            / "derived"
            / "run_interference_protocol_artifact_internalized_seed0"
            / "protocol_internalization_comparison.json",
            Path("results")
            / "derived"
            / "run_protocol_trap_internalized_seed0"
            / "protocol_internalization_comparison.json",
        ),
    )
    flattening_path = _first_existing_path(
        output_root,
        (
            Path("results")
            / "derived"
            / "run_interference_flattening_control_completion_partner_seed0"
            / "flattening_completion_comparison.json",
            Path("results")
            / "derived"
            / "run_relative_cycle_anchor_completion_partner_seed0"
            / "flattening_completion_comparison.json",
        ),
    )
    if not protocol_path.exists() or not flattening_path.exists():
        return
    protocol_payload = json.loads(protocol_path.read_text(encoding="utf-8"))
    flattening_payload = json.loads(flattening_path.read_text(encoding="utf-8"))
    checked_candidates = [str(flattening_payload["candidate_case_id"])]
    surviving_candidates = (
        checked_candidates if flattening_payload["survives_flattening_completion"] else []
    )
    non_surviving_candidates = (
        []
        if flattening_payload["survives_flattening_completion"]
        else checked_candidates
    )
    verdict = (
        "artifact_exposed_and_promoted_candidate_survives"
        if protocol_payload["artifact_exposed"] and surviving_candidates
        else "artifact_exposed_but_no_promoted_candidate_survives"
        if protocol_payload["artifact_exposed"]
        else "artifact_controls_inconclusive"
    )
    summary_payload = {
        "protocol_trap_exposed": bool(protocol_payload["artifact_exposed"]),
        "protocol_trap_comparison_artifact": _repo_relative_path(protocol_path, output_root),
        "flattening_completion_checked": True,
        "flattening_completion_comparison_artifact": _repo_relative_path(
            flattening_path,
            output_root,
        ),
        "promoted_candidates_checked": checked_candidates,
        "surviving_promoted_candidates": surviving_candidates,
        "non_surviving_promoted_candidates": non_surviving_candidates,
        "verdict": verdict,
    }
    summary_path = output_root / "results" / "derived" / "ticket15_artifact_controls_summary.json"
    summary_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _first_existing_path(output_root: Path, candidates: tuple[Path, ...]) -> Path:
    for candidate in candidates:
        resolved = output_root / candidate
        if resolved.exists():
            return resolved
    return output_root / candidates[0]


def _classify_run_label(
    quotient,
    factorization_status: AuditStatus,
    *,
    current_quotient_size: int,
    predictive_quotient_size: int,
    route_readability_score,
    visibility_recovery_gap,
) -> RecombinationClassLabel:
    if (
        quotient.class_count > quotient.branchwise_quotient.class_count
        and factorization_status == AuditStatus.FAILED
        and route_readability_score < 1
        and visibility_recovery_gap > 0
    ):
        return RecombinationClassLabel.ERASURE_RECOVERY
    if quotient.class_count == quotient.branchwise_quotient.class_count:
        if (
            factorization_status == AuditStatus.PASSED
            and route_readability_score > 0
            and visibility_recovery_gap == 0
        ):
            return RecombinationClassLabel.MARKED_SUPPRESSION
        if predictive_quotient_size > current_quotient_size:
            return RecombinationClassLabel.MEMORY_ONLY
        if factorization_status == AuditStatus.PASSED:
            return RecombinationClassLabel.CLASSICAL_MIXTURE
        return RecombinationClassLabel.UNCLASSIFIED
    return RecombinationClassLabel.COHERENT_BRANCH_CANDIDATE


def _build_run_note(
    *,
    run_id: str,
    config: BenchmarkRunConfig,
    record: RecombinationInterfaceResultRecord,
    result_manifest_path: str,
    diagnostics_summary_path: str,
    route_readability,
    visibility,
    erasure_assessment: dict[str, object] | None,
    protocol_assessment: dict[str, object] | None,
    flattening_assessment: dict[str, object] | None,
) -> str:
    interpretation_lines = [
        "## Interpretation",
        "",
    ]
    handled = False
    predictive_memory_present = (
        record.predictive_quotient_size > record.current_quotient_size
    )
    if (
        record.class_label == RecombinationClassLabel.ARTIFACT
        and record.internalization_status == AuditStatus.FAILED
    ):
        interpretation_lines.extend(
            [
                "The run is an explicit fake-positive protocol trap: a scheduler bit remains external to the declared support/current record while the observable family reads it out.",
                "The protocol/internalization audit failed, so the apparent recombination-positive signal is classified as an artifact rather than a genuine branch-family effect.",
            ]
        )
        handled = True
    elif (
        protocol_assessment is not None
        and record.internalization_status == AuditStatus.PASSED
    ):
        interpretation_lines.extend(
            [
                "The scheduler/protocol variable is explicitly internalized in this paired benchmark.",
                "Relative to the uninternalized partner, the apparent effect is removed or reclassified, so this run serves as the honest internalization control rather than as a positive recombination example.",
            ]
        )
        handled = True
    elif (
        flattening_assessment is not None
        and flattening_assessment["survives_flattening_completion"]
    ):
        interpretation_lines.extend(
            [
                "A coarse completion channel was added while retaining the original screen-sensitive observable structure.",
                "The promoted candidate still shows strict recombination refinement after that completion step, so it currently survives the available flattening/completion control.",
            ]
        )
        handled = True
    elif flattening_assessment is not None:
        interpretation_lines.extend(
            [
                "A completion/flattening partner was applied to the promoted candidate.",
                "The promoted effect does not survive that control as currently instantiated, so this run should not be treated as a surviving positive exemplar.",
            ]
        )
        handled = True
    if (
        not handled
        and
        record.class_label == RecombinationClassLabel.ERASURE_RECOVERY
        and erasure_assessment is not None
        and erasure_assessment["viable_flagship_example"]
    ):
        interpretation_lines.extend(
            [
                "Route readability fell relative to the marked partner while conditional screen structure reappeared under the designated erasure scenario.",
                "The run matches the preferred erasure-recovery case: `R_i` strictly refines `K_i`, the recombination gap is positive, the factorization hook failed, and this benchmark is a viable flagship example.",
            ]
        )
        handled = True
    elif (
        not handled
        and
        erasure_assessment is not None
        and erasure_assessment["supports_erasure_recovery"]
    ):
        interpretation_lines.extend(
            [
                "Route readability fell relative to the marked partner and conditional screen structure reappeared under the designated erasure scenario.",
                "This is a partial erasure-recovery case: the benchmark is useful, but it does not yet clear the stronger flagship threshold.",
            ]
        )
        handled = True
    elif (
        not handled
        and
        record.class_label == RecombinationClassLabel.MARKED_SUPPRESSION
        and record.branchwise_quotient_size == record.recombination_quotient_size
        and record.eta_max_fiber_size == 1
        and record.recombination_gap_value == 0
        and record.factorization_status == AuditStatus.PASSED
    ):
        interpretation_lines.extend(
            [
                "The benchmark is explicitly route-marked and the marker channel is highly readable at terminal readout.",
                "The run matches the marked-suppression expectation: `K_i` and `R_i` coincide, the recombination gap is zero, the factorization hook passed, and the designated screen/pattern contrast shows no erasure-style recovery.",
            ]
        )
        handled = True
    elif (
        not handled
        and
        record.branchwise_quotient_size == record.recombination_quotient_size
        and record.eta_max_fiber_size == 1
        and record.recombination_gap_value == 0
        and record.factorization_status == AuditStatus.PASSED
        and predictive_memory_present
    ):
        interpretation_lines.extend(
            [
                "Inherited predictive memory is reproduced on the inherited side: `M_i` strictly refines `Q_i` on the tested interface.",
                "The branch-family computation is nontrivial, but the run still matches the memory-only expectation: `K_i` and `R_i` coincide, the recombination gap is zero, and the factorization hook passed.",
            ]
        )
        handled = True
    elif (
        not handled
        and
        record.branchwise_quotient_size == record.recombination_quotient_size
        and record.eta_max_fiber_size == 1
        and record.recombination_gap_value == 0
        and record.factorization_status == AuditStatus.PASSED
    ):
        interpretation_lines.extend(
            [
                "Observables factored through branchwise summaries on the tested family.",
                "The run matched the classical-mixture expectation: `K_i` and `R_i` coincide, the recombination gap is zero, and the factorization hook passed.",
            ]
        )
        handled = True
    else:
        interpretation_lines.extend(
            [
                "The run did not match the classical-mixture expectation.",
                "Check the recorded quotient sizes, recombination gap, and factorization status before treating this family as a valid branchwise-factorized baseline.",
            ]
        )
    lines = [
        f"# Run {run_id}",
        "",
        f"- config id: `{config.config_id}`",
        f"- benchmark id: `{config.benchmark_id}`",
        f"- interface id: `{config.interface_id}`",
        f"- assemblage family id: `{config.assemblage_family_id}`",
        f"- observable family id: `{config.observable_family_id}`",
        f"- current quotient size: `{record.current_quotient_size}`",
        f"- predictive quotient size: `{record.predictive_quotient_size}`",
        f"- branchwise quotient size: `{record.branchwise_quotient_size}`",
        f"- recombination quotient size: `{record.recombination_quotient_size}`",
        f"- eta max fiber size: `{record.eta_max_fiber_size}`",
        f"- route readability score: `{float(route_readability.score_value)}`",
        f"- raw route-recovery success probability: `{str(route_readability.raw_success_probability)}`",
        f"- unconditional visibility: `{str(visibility.unconditional_visibility)}`",
        f"- conditional visibility by condition: `{dict((condition_id, str(value)) for condition_id, value in visibility.conditional_visibility_by_condition.items())}`",
        f"- max conditional visibility: `{str(visibility.max_conditional_visibility)}`",
        f"- visibility recovery gap: `{str(visibility.visibility_recovery_gap)}`",
        f"- result manifest: `{result_manifest_path}`",
        f"- diagnostics summary: `{diagnostics_summary_path}`",
    ]
    if erasure_assessment is not None:
        lines.append(f"- erasure assessment: `{erasure_assessment}`")
    if protocol_assessment is not None:
        lines.append(f"- protocol/internalization assessment: `{protocol_assessment}`")
    if flattening_assessment is not None:
        lines.append(f"- flattening/completion assessment: `{flattening_assessment}`")
    lines.extend(
        [
            "",
            *interpretation_lines,
            "",
        ]
    )
    return "\n".join(lines)


def _repo_relative_path(path: Path, output_root: Path) -> str:
    resolved = path.resolve()
    for root in (output_root.resolve(), REPO_ROOT.resolve()):
        try:
            return resolved.relative_to(root).as_posix()
        except ValueError:
            continue
    return resolved.as_posix()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sixbirds_foundations_v._recombination_support.runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--config", required=True)
    run_parser.add_argument("--output-root", default=str(REPO_ROOT))

    export_parser = subparsers.add_parser("export-schemas")
    export_parser.add_argument("--skip-compatibility-copies", action="store_true")

    validate_artifact_parser = subparsers.add_parser("validate")
    validate_artifact_parser.add_argument(
        "--kind",
        required=True,
        choices=[
            "benchmark-manifest",
            "route-transport-package",
            "benchmark-run-config",
            "search-run-config",
            "frozen-slice",
            "result-manifest",
            "result-ledger",
            "route-classification-ledger",
        ],
    )
    validate_artifact_parser.add_argument("--path", required=True)

    validate_parser = subparsers.add_parser("validate-config")
    validate_parser.add_argument("--config", required=True)

    sweep_parser = subparsers.add_parser("sweep")
    sweep_parser.add_argument("--config", required=True)
    sweep_parser.add_argument("--output-root", default=str(REPO_ROOT))

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--config", required=True)
    search_parser.add_argument("--output-root", default=str(REPO_ROOT))

    robustness_parser = subparsers.add_parser("robustness")
    robustness_parser.add_argument("--config", required=True)
    robustness_parser.add_argument("--output-root", default=str(REPO_ROOT))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "export-schemas":
        for path in export_all_schemas(
            include_compatibility_copies=not args.skip_compatibility_copies
        ):
            print(path.relative_to(REPO_ROOT))
        return 0

    if args.command == "validate":
        summary = validate_artifact_summary(args.kind, args.path)
        print(json.dumps(summary, sort_keys=True))
        return 0

    if args.command == "validate-config":
        config = validate_config_file(args.config)
        print(
            json.dumps(
                {
                    "validated": True,
                    "config_kind": config.config_kind,
                    "config_id": config.config_id,
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "sweep":
        config = load_run_config(args.config)
        try:
            artifacts = sweep_config(
                config,
                config_path=args.config,
                output_root=args.output_root,
                command_used="python -m sixbirds_foundations_v._recombination_support.runner "
                + " ".join(sys.argv[1:]),
            )
        except UnsupportedSweepExecutionError as exc:
            print(
                json.dumps(
                    {
                        "error": "unsupported_sweep_execution",
                        "detail": str(exc),
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 2
        print(
            json.dumps(
                {
                    "sweep_id": artifacts.sweep_id,
                    "summary_table_path": _repo_relative_path(
                        artifacts.summary_table_json_path,
                        Path(args.output_root),
                    ),
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "search":
        config = load_run_config(args.config)
        try:
            artifacts = search_config(
                config,
                config_path=args.config,
                output_root=args.output_root,
                command_used="python -m sixbirds_foundations_v._recombination_support.runner "
                + " ".join(sys.argv[1:]),
            )
        except UnsupportedSweepExecutionError as exc:
            print(
                json.dumps(
                    {
                        "error": "unsupported_search_execution",
                        "detail": str(exc),
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 2
        print(
            json.dumps(
                {
                    "search_id": artifacts.search_id,
                    "smoke_summary_path": _repo_relative_path(
                        artifacts.smoke_summary_path,
                        Path(args.output_root),
                    ),
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "robustness":
        config = load_run_config(args.config)
        try:
            artifacts = robustness_config(
                config,
                config_path=args.config,
                output_root=args.output_root,
                command_used="python -m sixbirds_foundations_v._recombination_support.runner "
                + " ".join(sys.argv[1:]),
            )
        except UnsupportedSweepExecutionError as exc:
            print(
                json.dumps(
                    {
                        "error": "unsupported_robustness_execution",
                        "detail": str(exc),
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 2
        print(
            json.dumps(
                {
                    "robustness_id": artifacts.robustness_id,
                    "robustness_summary_path": _repo_relative_path(
                        artifacts.summary_table_json_path,
                        Path(args.output_root),
                    ),
                },
                sort_keys=True,
            )
        )
        return 0

    config = load_run_config(args.config)
    try:
        artifacts = run_config(
            config,
            config_path=args.config,
            output_root=args.output_root,
            command_used="python -m sixbirds_foundations_v._recombination_support.runner "
            + " ".join(sys.argv[1:]),
        )
    except SearchExecutionDeferredError as exc:
        print(
            json.dumps(
                {
                    "error": "search_execution_deferred",
                    "detail": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {
                "run_id": artifacts.run_id,
                "result_manifest_path": _repo_relative_path(
                    artifacts.result_manifest_path,
                    Path(args.output_root),
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
