from __future__ import annotations

from fractions import Fraction

import pytest

import sixbirds_foundations_v.sweeps.e14_reconsolidation_sweep as e14


REGISTERED_STATUS_EXPECTATIONS = (
    ("claim_record_repaired", e14.ReconsolidationStatus.record_repaired),
    ("claim_record_coarsened", e14.ReconsolidationStatus.record_coarsened),
    ("claim_statused_unresolved", e14.ReconsolidationStatus.statused_unresolved),
    ("claim_outcome_collision", e14.ReconsolidationStatus.outcome_collision),
    ("claim_unrealized_direct_reference", e14.ReconsolidationStatus.unrealized_disposition),
    ("claim_silent_rewrite", e14.ReconsolidationStatus.silent_rewrite),
    ("claim_provenance_defect", e14.ReconsolidationStatus.provenance_defect),
    ("claim_ordinary_read", e14.ReconsolidationStatus.ordinary_read),
    ("claim_unstatused_conflict", e14.ReconsolidationStatus.unstatused_conflict),
    ("ctrl_coarsening_audited_pair_mismatch", e14.ReconsolidationStatus.unrealized_disposition),
    ("ctrl_unresolved_provenance_root_mismatch", e14.ReconsolidationStatus.unrealized_disposition),
    ("ctrl_non_strict_coarsening", e14.ReconsolidationStatus.unrealized_disposition),
    ("ctrl_wrong_direction_refinement", e14.ReconsolidationStatus.unrealized_disposition),
    ("ctrl_uncarried_post_retrieval_record", e14.ReconsolidationStatus.unrealized_disposition),
    ("ctrl_ledger_charge_label_only", e14.ReconsolidationStatus.unrealized_disposition),
    ("ctrl_unrelated_mutation_evidence", e14.ReconsolidationStatus.unrealized_disposition),
)


REGISTERED_CONTROL_NAMES = (
    "ctrl_transport_single_valued_same_context",
    "ctrl_no_conflict_after_transport",
    "ctrl_conflict_for_other_claim",
    "ctrl_per_retrieval_claim_scoping",
    "strata_budget_memory_fate_direction",
)


def test_e14_sweep_confirms_all_registered_predictions() -> None:
    results = e14.run_e14_reconsolidation_sweep()

    assert len(results.comparisons) == 21
    assert tuple(row.name for row in results.comparisons) == e14.REGISTERED_COMPARISON_ORDER
    assert [row.name for row in results.comparisons if not row.passed] == []
    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True


@pytest.mark.parametrize(("claim_name", "expected"), REGISTERED_STATUS_EXPECTATIONS)
def test_e14_registered_status_comparisons(
    claim_name: str, expected: e14.ReconsolidationStatus
) -> None:
    fixture = e14.build_fixture()
    observed, truths, record = e14.classify_reconsolidation_status(
        fixture, claim_name
    )

    assert observed is expected
    assert record is not None
    assert record.status is expected
    assert sum(truths.values()) == 1
    assert truths[expected] is True
    assert e14.complete_reconsolidation_status(fixture, claim_name) is True


@pytest.mark.parametrize("control_name", REGISTERED_CONTROL_NAMES)
def test_e14_registered_nonstatus_comparisons(control_name: str) -> None:
    results = e14.run_e14_reconsolidation_sweep()
    control = results.controls[control_name]

    assert control.passed_control is True
    assert next(
        comparison for comparison in results.comparisons if comparison.name == control_name
    ).passed is True


def test_e14_same_context_transport_inventory_fails_only_single_valuedness() -> None:
    fixture = e14.build_fixture()
    inventory = fixture.retrieval_inventories["inventory_bad_same_context"]
    checks = e14.retrieval_inventory_checks(fixture, inventory)

    assert checks == {
        "completeForClaim": True,
        "soundForClaim": True,
        "everyContextCovered": True,
        "transportSingleValuedPerContext": False,
    }
    assert e14.complete_retrieval_transport_inventory(fixture, inventory) is False


def test_e14_direct_record_reference_rejects_numeric_id_coincidence() -> None:
    fixture = e14.build_fixture()
    disposition_inventory = fixture.disposition_inventories["trigger_unrealized"]
    outcome_inventory = fixture.outcome_inventories["trigger_unrealized"]
    disposition = fixture.dispositions["disp_detached"]
    realized = outcome_inventory.repair_mutation_records[0]

    assert disposition.supporting_mutation is not None
    assert disposition.supporting_mutation.mutation_id == realized.mutation_id == 400
    assert disposition.supporting_mutation != realized
    assert e14.complete_outcome_inventory(fixture, outcome_inventory) is True
    assert (
        e14.disposition_realized_by_inventory(
            fixture, disposition_inventory, outcome_inventory
        )
        is False
    )


def test_e14_coarsening_uses_the_pair_owned_by_the_support_audit() -> None:
    fixture = e14.build_fixture()
    valid = fixture.coarsening_candidates["coarsening_evidence_coarsen"]
    mismatch = fixture.coarsening_candidates[
        "coarsening_evidence_pair_mismatch"
    ]

    assert (valid.support_audit.merged_left, valid.support_audit.merged_right) == (
        "a",
        "b",
    )
    assert e14.record_coarsening_evidence(fixture, valid) is True
    assert (mismatch.support_audit.merged_left, mismatch.support_audit.merged_right) == (
        "c",
        "d",
    )
    assert (
        fixture.ctx.distinction_no_longer_supportable(
            fixture, mismatch.support_audit, mismatch.trigger.source_record.claim_record
        )
        is False
    )
    assert e14.record_coarsening_evidence(fixture, mismatch) is False


def test_e14_statused_unresolved_preserves_the_provenance_root() -> None:
    fixture = e14.build_fixture()
    valid = fixture.unresolved_candidates["unresolved_evidence_unresolved"]
    drift = fixture.unresolved_candidates["unresolved_evidence_root_drift"]

    assert valid.current_record_at_status.provenance_root_id == 700
    assert e14.statused_unresolved_evidence(fixture, valid) is True
    assert drift.current_record_at_status.record_value == drift.trigger.source_record.record_value
    assert drift.current_record_at_status.provenance_root_id == 701
    assert drift.trigger.source_record.provenance_root_id == 700
    assert e14.statused_unresolved_evidence(fixture, drift) is False
    assert (
        e14.classify_reconsolidation_status(
            fixture, "ctrl_unresolved_provenance_root_mismatch"
        )[0]
        is e14.ReconsolidationStatus.unrealized_disposition
    )


def test_e14_collision_requires_two_valid_outcomes_for_the_same_trigger() -> None:
    fixture = e14.build_fixture()
    trigger = fixture.triggers["trigger_collision"]
    repair = fixture.repair_candidates["repair_evidence_collision_repair"]
    coarsening = fixture.coarsening_candidates[
        "coarsening_evidence_collision_coarsen"
    ]

    assert repair.trigger == trigger == coarsening.trigger
    assert repair.trigger.conflict_record == fixture.conflicts["conflict_collision"]
    assert e14.record_repair_evidence(fixture, repair) is True
    assert e14.record_coarsening_evidence(fixture, coarsening) is True
    assert e14.reconsolidation_outcome_collision(fixture, trigger) is True


@pytest.mark.parametrize(
    ("claim_name", "expected_delta", "expected_trigger_count"),
    (
        ("ctrl_no_conflict_after_transport", frozenset(), 0),
        ("ctrl_conflict_for_other_claim", frozenset(), 0),
    ),
)
def test_e14_no_conflict_controls_fail_before_trigger_construction(
    claim_name: str,
    expected_delta: frozenset[frozenset[str]],
    expected_trigger_count: int,
) -> None:
    fixture = e14.build_fixture()
    claim = fixture.reconsolidation_claims[claim_name]

    assert e14.delta_set(claim.transport_record, claim.claim_record) == expected_delta
    assert len(e14._matching_triggers(fixture, claim)) == expected_trigger_count


@pytest.mark.parametrize(
    "candidate_name",
    (
        "coarsening_evidence_non_strict",
        "coarsening_evidence_wrong_direction",
    ),
)
def test_e14_invalid_quotient_transitions_do_not_count_as_coarsening(
    candidate_name: str,
) -> None:
    fixture = e14.build_fixture()

    assert e14.record_coarsening_evidence(
        fixture, fixture.coarsening_candidates[candidate_name]
    ) is False


def test_e14_uncarried_successor_and_label_only_charge_are_rejected() -> None:
    fixture = e14.build_fixture()
    uncarried = fixture.repair_candidates["repair_evidence_uncarried"]
    label_only = fixture.unresolved_candidates["unresolved_evidence_missing_label"]

    assert e14.record_repair_evidence(fixture, uncarried) is False
    assert label_only.ledger_entry.charged_metadata is True
    assert label_only.ledger_entry not in fixture.carrier.lambda_entries
    assert label_only.ledger_entry.amount == Fraction(1, 2)
    assert label_only.residual_record.residual_amount == Fraction(1, 3)
    assert e14.statused_unresolved_evidence(fixture, label_only) is False


def test_e14_full_claim_key_keeps_two_retrievals_independent() -> None:
    fixture = e14.build_fixture()
    home = fixture.reconsolidation_claims["scope_home"]
    shift = fixture.reconsolidation_claims["scope_shift"]

    assert home.source_record == shift.source_record
    assert home.family == shift.family
    assert home.transport_record != shift.transport_record
    assert home.context_record != shift.context_record
    assert (
        e14.classify_reconsolidation_status(fixture, "scope_home")[0]
        is e14.ReconsolidationStatus.record_repaired
    )
    assert (
        e14.classify_reconsolidation_status(fixture, "scope_shift")[0]
        is e14.ReconsolidationStatus.statused_unresolved
    )


def test_e14_budget_strata_group_computed_statuses_after_classification() -> None:
    fixture = e14.build_fixture()
    counts = e14._stratum_counts(fixture)

    assert counts["loose"][e14.ReconsolidationStatus.record_repaired] == 6
    assert counts["tight"][e14.ReconsolidationStatus.record_repaired] == 1
    assert counts["loose"][e14.ReconsolidationStatus.record_coarsened] == 1
    assert counts["tight"][e14.ReconsolidationStatus.record_coarsened] == 6
    assert counts["loose"][e14.ReconsolidationStatus.statused_unresolved] == 1
    assert counts["tight"][e14.ReconsolidationStatus.statused_unresolved] == 1
    assert all(
        e14.complete_reconsolidation_status(fixture, episode.claim_name)
        for episode in fixture.strata
    )
