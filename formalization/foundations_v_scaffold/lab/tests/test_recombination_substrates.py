from __future__ import annotations

from fractions import Fraction

from sixbirds_foundations_v._recombination_support.schemas.enums import (
    AuditStatus,
    RecombinationClassLabel,
)
from sixbirds_foundations_v.budget import (
    BudgetCandidateSelection,
    LowerLayerLedger,
    PROXY_UNIFORM_COST_MODE,
    evaluate_candidate_cost,
)
from sixbirds_foundations_v.classifier import ClassificationInput, classify_case
from sixbirds_foundations_v.extension import (
    BudgetContextStatus,
    ExtensionAuditStatus,
    ExtensionAuditZone,
    ExtensionZoneCategory,
    NEW_OBJECT_MAP,
    NON_FACTORIZATION_CHECK,
    run_extension_harness,
)


def _classification_input(**overrides: object) -> ClassificationInput:
    base = {
        "current_quotient_size": 1,
        "predictive_quotient_size": 1,
        "branchwise_quotient_size": 1,
        "recombination_quotient_size": 1,
        "eta_max_fiber_size": 1,
        "recombination_gap_value": Fraction(0),
        "route_readability_score": Fraction(0),
        "unconditional_visibility": Fraction(0),
        "max_conditional_visibility": Fraction(0),
        "visibility_recovery_gap": Fraction(0),
        "factorization_status": AuditStatus.PASSED,
    }
    base.update(overrides)
    return ClassificationInput(**base)


def test_classifier_canonical_labels_are_deterministic() -> None:
    assert classify_case(_classification_input()).label == RecombinationClassLabel.CLASSICAL_MIXTURE
    assert (
        classify_case(_classification_input(predictive_quotient_size=2)).label
        == RecombinationClassLabel.MEMORY_ONLY
    )
    assert (
        classify_case(_classification_input(route_readability_score=Fraction(1))).label
        == RecombinationClassLabel.MARKED_SUPPRESSION
    )


def test_budget_cost_modes_run_on_toy_ledger() -> None:
    ledger = LowerLayerLedger(
        ledger_id="toy.lower_layer",
        benchmark_id="toy",
        run_ref="config:toy",
        config_path="configs/toy.json",
        phase_mode="toy",
        strategy_id="identity_reference",
        state_count=2,
        edge_count=1,
        rows=[],
    )
    selection = BudgetCandidateSelection(
        candidate_id="candidate",
        benchmark_id="toy",
        runtime_benchmark_id="toy",
        config_id="toy",
        config_path="configs/toy.json",
        source_kind="toy",
        strategy_id="identity_reference",
        phase_mode="toy",
        completion_status="ok",
        selected_candidate_ids=["candidate"],
        selected_history_ids=["h0"],
    )

    summary = evaluate_candidate_cost(selection, ledger, cost_mode=PROXY_UNIFORM_COST_MODE)
    assert summary.status.value == "ok"
    assert summary.aggregated_cost == 1.0


def test_extension_new_object_map_resolves_nonfactorization_toy() -> None:
    zone = ExtensionAuditZone(
        zone_id="toy.nonfactorization",
        zone_category=ExtensionZoneCategory.TOY_OBSTRUCTED_NONFACTORIZABLE,
        source_kind="toy",
        budget_context_status=BudgetContextStatus.NOT_APPLICABLE,
        baseline_semantics={
            "object_map": {"a": "coarse", "b": "coarse"},
            "observable_signatures": {"a": "left", "b": "right"},
        },
        move_payloads={
            NEW_OBJECT_MAP: {
                "object_map": {"a": "left_class", "b": "right_class"},
                "observable_signatures": {"a": "left", "b": "right"},
            }
        },
    )

    bundle = run_extension_harness(zone)
    row = next(
        item
        for item in bundle.rows
        if item.extension_move_id == NEW_OBJECT_MAP
        and item.obstruction_check_id == NON_FACTORIZATION_CHECK
    )
    assert row.status == ExtensionAuditStatus.OK
    assert row.obstruction_flag is True
    assert row.resolution_flag is True
