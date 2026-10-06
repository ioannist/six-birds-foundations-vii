from __future__ import annotations

from dataclasses import replace

import pytest

from sixbirds_foundations_v.carried_records import FineSourceTag
from sixbirds_foundations_v.sweeps.e13_repair_transport_sweep import (
    RepairTransportStatus,
    ResponseMode,
    TransportClaimKind,
    TransportClaimRef,
    _actual_scope_discipline,
    _no_hardcoded_status_discipline,
    _status_rows,
    b_committed_repair_in_a_absence,
    bridge_defects_paid,
    build_fixture,
    classify_repair_transport_status,
    communication_transport_evidence,
    coercion_null_certified,
    computed_response_mode,
    different_class_influence_evidence,
    inter_carrier_bridge,
    role_preserving_transport,
    run_e13_repair_transport_sweep,
    scaffolded_or_primed_case,
    same_transport_challenge_class,
    symbol_falsifier_linked,
    symbolic_case,
    symbolic_repair_evidence,
    taught_case,
    transport_delta_reduction,
    transport_status_record_matches_claim,
)


def test_e13_sweep_confirms_all_registered_predictions() -> None:
    results = run_e13_repair_transport_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 19
    assert len(results.rows) == 15
    assert len(results.controls) == 4
    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True


@pytest.mark.parametrize(
    ("claim", "expected"),
    (
        ("claim_comm_clean", RepairTransportStatus.communicated),
        ("claim_teach_absent_capacity", RepairTransportStatus.taught),
        ("claim_force_null", RepairTransportStatus.coercion_null),
        ("claim_symbol_stable", RepairTransportStatus.symbolic),
        ("claim_scaffolded_no_capacity", RepairTransportStatus.scaffolded_or_primed),
        ("claim_primed_no_capacity", RepairTransportStatus.scaffolded_or_primed),
        ("claim_influence_different_class", RepairTransportStatus.influence_only),
        ("reject_unpaid_bridge", RepairTransportStatus.transport_rejected),
        ("reject_uncarried_target_repair", RepairTransportStatus.transport_rejected),
        ("reject_role_preservation_failure", RepairTransportStatus.transport_rejected),
        ("reject_symbol_context_instability", RepairTransportStatus.transport_rejected),
        ("reject_symbol_role_drift", RepairTransportStatus.transport_rejected),
        ("reject_saturation_relabel", RepairTransportStatus.transport_rejected),
        ("reject_parameter_channel_only", RepairTransportStatus.transport_rejected),
        ("reject_flow_crossing_no_bridge", RepairTransportStatus.transport_rejected),
    ),
)
def test_e13_registered_status_rows(claim: str, expected: RepairTransportStatus) -> None:
    fixture = build_fixture()
    status, truths, record = classify_repair_transport_status(fixture, claim)

    assert status is expected
    assert record is not None
    assert sum(truths.values()) == 1


@pytest.mark.parametrize(
    "control_name",
    (
        "ctrl_shared_comparator_bundle_nontrivial",
        "ctrl_transport_claim_kind_scoping",
        "ctrl_claim_independence",
        "ctrl_falsifier_claim_linkage",
    ),
)
def test_e13_registered_controls(control_name: str) -> None:
    results = run_e13_repair_transport_sweep()

    assert results.controls[control_name].passed_control is True


def test_e13_transport_status_record_matches_claim_is_kind_and_reference_aware() -> None:
    fixture = build_fixture()
    record = fixture.status_records["status_comm_clean"]
    communication_claim = fixture.claims["claim_comm_clean"]
    teaching_same_refs = TransportClaimRef(
        "teaching_same_refs",
        TransportClaimKind.teaching,
        "tok_nav_comm",
        "pkg_nav_comm",
        "bridge_paid_ab",
        target_class="C_navigation",
    )
    symbol_same_refs = TransportClaimRef(
        "symbol_same_refs",
        TransportClaimKind.symbol,
        "tok_nav_comm",
        "pkg_nav_comm",
        "bridge_paid_ab",
        family="family_language",
    )

    assert transport_status_record_matches_claim(fixture, communication_claim, record) is True
    assert transport_status_record_matches_claim(fixture, teaching_same_refs, record) is False
    assert transport_status_record_matches_claim(fixture, symbol_same_refs, record) is False


def test_e13_influence_claim_target_class_must_match_target_repair() -> None:
    fixture = build_fixture()
    record = fixture.status_records["status_influence_different_class"]
    valid_claim = fixture.claims["claim_influence_different_class"]
    stale_claim = replace(valid_claim, target_class="C_navigation")

    assert transport_status_record_matches_claim(fixture, valid_claim, record) is True
    assert transport_status_record_matches_claim(fixture, stale_claim, record) is False
    assert different_class_influence_evidence(
        fixture,
        "bridge_paid_ab",
        "pkg_nav_influence",
        "tok_nav_influence",
        "repair_power_influence",
    ) is True
    assert same_transport_challenge_class(fixture, "C_navigation", "C_power") is False


def test_e13_taught_case_uses_record_target_repair_not_hardcoded_literal() -> None:
    fixture = build_fixture()
    claim = fixture.claims["claim_teach_absent_capacity"]
    record = fixture.status_records["status_teach_absent_capacity"]
    wrong_initial = replace(record, target_repair_record="repair_nav_clean")

    assert transport_status_record_matches_claim(fixture, claim, wrong_initial) is True
    assert taught_case(fixture, claim, record) is True
    assert taught_case(fixture, claim, wrong_initial) is False


def test_e13_shared_context_comparators_compute_both_accept_and_reject() -> None:
    fixture = build_fixture()

    assert computed_response_mode(fixture, "force_full_nav") is ResponseMode.fully_forced_response
    assert computed_response_mode(fixture, "force_scaffold_nav") is ResponseMode.scaffolded_response
    assert computed_response_mode(fixture, "force_prime_nav") is ResponseMode.primed_response
    assert role_preserving_transport(fixture, "pkg_nav_comm", "repair_nav_clean") is True
    assert role_preserving_transport(fixture, "pkg_nav_role_drift", "repair_nav_role_drift") is False
    assert bridge_defects_paid(fixture, "bridge_paid_ab") is True
    assert bridge_defects_paid(fixture, "bridge_unpaid_ab") is False


def test_e13_bridge_discharge_is_computed_from_ledger_values() -> None:
    fixture = build_fixture()
    weakened_source = replace(
        fixture.source_ledgers["ledger_A_paid"],
        amount=fixture.source_ledgers["ledger_A_unpaid"].amount,
    )
    mutated = replace(
        fixture,
        source_ledgers={**fixture.source_ledgers, "ledger_A_paid": weakened_source},
    )

    assert bridge_defects_paid(fixture, "bridge_paid_ab") is True
    assert bridge_defects_paid(mutated, "bridge_paid_ab") is False
    assert communication_transport_evidence(
        mutated,
        "bridge_paid_ab",
        "pkg_nav_comm",
        "tok_nav_comm",
        "repair_nav_clean",
    ) is False


def test_e13_transport_delta_reduction_is_tied_to_target_repair_move() -> None:
    fixture = build_fixture()
    bad_repair = replace(
        fixture.target_repairs["repair_nav_clean"],
        q_after_installed_move="mv_unrelated",
    )
    mutated = replace(
        fixture,
        target_repairs={**fixture.target_repairs, "repair_nav_clean": bad_repair},
    )

    assert transport_delta_reduction(fixture, "repair_nav_clean") is True
    assert transport_delta_reduction(mutated, "repair_nav_clean") is False
    assert communication_transport_evidence(
        mutated,
        "bridge_paid_ab",
        "pkg_nav_comm",
        "tok_nav_comm",
        "repair_nav_clean",
    ) is False


def test_e13_uncarried_target_repair_rejected_despite_raw_delta_reduction() -> None:
    fixture = build_fixture()
    target = fixture.target_repairs["repair_nav_uncarried"]

    assert target.post_splits < target.pre_splits
    assert target.carried is False
    assert transport_delta_reduction(fixture, "repair_nav_uncarried") is True
    assert communication_transport_evidence(
        fixture,
        "bridge_paid_ab",
        "pkg_nav_uncarried",
        "tok_nav_uncarried",
        "repair_nav_uncarried",
    ) is False
    assert classify_repair_transport_status(fixture, "reject_uncarried_target_repair")[0] is RepairTransportStatus.transport_rejected


def test_e13_uncarried_repairs_do_not_count_as_a_absent_committed_capacity() -> None:
    fixture = build_fixture()

    assert b_committed_repair_in_a_absence(
        fixture,
        "schedule_A_absent_nav",
        "repair_nav_later_capacity",
    ) is True
    assert b_committed_repair_in_a_absence(
        fixture,
        "schedule_A_absent_nav",
        "repair_nav_uncarried",
    ) is False


def test_e13_uncarried_committed_like_repair_does_not_defeat_coercion_null() -> None:
    fixture = build_fixture()
    committed_like_but_uncarried = replace(
        fixture.target_repairs["repair_nav_force_placeholder"],
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
        carried=False,
    )
    mutated = replace(
        fixture,
        target_repairs={
            **fixture.target_repairs,
            "repair_nav_force_placeholder": committed_like_but_uncarried,
        },
    )

    assert coercion_null_certified(mutated, "force_full_nav", "tok_nav_force") is True


def test_e13_scaffolded_or_primed_case_requires_record_forcing_link() -> None:
    fixture = build_fixture()
    claim = fixture.claims["claim_scaffolded_no_capacity"]
    record = fixture.status_records["status_scaffolded_no_capacity"]
    wrong_forcing = replace(record, forcing_record="force_prime_nav")

    assert scaffolded_or_primed_case(fixture, claim, record) is True
    assert scaffolded_or_primed_case(fixture, claim, wrong_forcing) is False


def test_e13_falsifier_claim_linkage_rejects_mismatched_token_and_bridge() -> None:
    fixture = build_fixture()

    assert symbol_falsifier_linked(
        fixture,
        "claim_symbol_stable",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "bridge_paid_ab",
        "family_language",
    ) is True
    assert symbol_falsifier_linked(
        fixture,
        "claim_comm_clean",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "bridge_unpaid_ab",
        "family_language",
    ) is False


def test_e13_symbolic_repair_rejects_uncarried_unlawful_target_repair() -> None:
    fixture = build_fixture()
    claim = fixture.claims["claim_symbol_stable"]
    record = fixture.status_records["status_symbol_stable"]
    bad_target = replace(
        fixture.target_repairs["repair_symbol_ctx1"],
        carried=False,
        lawful=False,
        source_tag=FineSourceTag.fallback,
        generated_by_s=False,
        in_scope=False,
    )
    mutated = replace(
        fixture,
        target_repairs={**fixture.target_repairs, "repair_symbol_ctx1": bad_target},
    )

    assert symbolic_repair_evidence(
        fixture,
        "bridge_paid_ab",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "family_language",
    ) is True
    assert symbolic_case(fixture, claim, record) is True
    assert symbolic_repair_evidence(
        mutated,
        "bridge_paid_ab",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "family_language",
    ) is False
    assert symbolic_case(mutated, claim, record) is False


def test_e13_symbolic_repair_rejects_uncarried_token_and_source_package() -> None:
    fixture = build_fixture()
    claim = fixture.claims["claim_symbol_stable"]
    record = fixture.status_records["status_symbol_stable"]
    bad_token = replace(
        fixture.tokens["tok_symbol_stable"],
        source_tag=FineSourceTag.fallback,
        generated_by_s=False,
        in_scope=False,
    )
    bad_package = replace(
        fixture.source_packages["pkg_lang_stable"],
        source_tag=FineSourceTag.fallback,
        generated_by_s=False,
        in_scope=False,
    )
    mutated = replace(
        fixture,
        tokens={**fixture.tokens, "tok_symbol_stable": bad_token},
        source_packages={**fixture.source_packages, "pkg_lang_stable": bad_package},
    )

    assert symbolic_repair_evidence(
        mutated,
        "bridge_paid_ab",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "family_language",
    ) is False
    assert symbolic_case(mutated, claim, record) is False


def test_e13_symbolic_repair_rejects_source_package_emitted_for_different_token() -> None:
    fixture = build_fixture()
    claim = fixture.claims["claim_symbol_stable"]
    record = fixture.status_records["status_symbol_stable"]
    wrong_package = replace(
        fixture.source_packages["pkg_lang_stable"],
        emitted_token="tok_symbol_role_drift",
    )
    mutated = replace(
        fixture,
        source_packages={**fixture.source_packages, "pkg_lang_stable": wrong_package},
    )

    assert symbolic_repair_evidence(
        mutated,
        "bridge_paid_ab",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "family_language",
    ) is False
    assert symbolic_case(mutated, claim, record) is False


def test_e13_flow_crossing_control_uses_nonconstructible_bridge_reference() -> None:
    fixture = build_fixture()

    assert "flow_boundary_crossing_1" in fixture.flow_crossings
    assert inter_carrier_bridge(fixture, "bridge_flow_unlinked_ab") is False
    assert classify_repair_transport_status(fixture, "reject_flow_crossing_no_bridge")[0] is RepairTransportStatus.transport_rejected


def test_e13_discipline_flags_are_computed_from_scope_and_case_truths() -> None:
    fixture = build_fixture()
    results = run_e13_repair_transport_sweep()
    rows = _status_rows(fixture)
    bad_record = replace(
        fixture.status_records["status_comm_clean"],
        token_record="tok_nav_teach",
    )
    bad_fixture = replace(
        fixture,
        status_records={
            **fixture.status_records,
            "status_comm_clean": bad_record,
        },
    )
    bad_rows = _status_rows(bad_fixture)
    bad_truths = {key: False for key in results.rows["claim_comm_clean"].truths}
    bad_result_row = replace(results.rows["claim_comm_clean"], truths=bad_truths)
    bad_results = replace(
        results,
        rows={**results.rows, "claim_comm_clean": bad_result_row},
    )

    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True
    assert _actual_scope_discipline(fixture, rows) is True
    assert _actual_scope_discipline(bad_fixture, bad_rows) is False
    assert _no_hardcoded_status_discipline(bad_results) is False


def test_e13_no_floats_or_randomness_in_numeric_fixture_values() -> None:
    fixture = build_fixture()

    assert all(not isinstance(entry.amount, float) for entry in fixture.source_ledgers.values())
    assert all(not isinstance(entry.amount, float) for entry in fixture.target_ledgers.values())
    assert all(
        entry.source_tag is not FineSourceTag.unknown
        for entry in (*fixture.source_ledgers.values(), *fixture.target_ledgers.values())
    )
