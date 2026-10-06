from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import replace
from fractions import Fraction

import pytest

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordOccurrence,
    CarriedRecordPolicy,
    CheckRuleRecord,
    DeclaredTrajectory,
    FineSourceTag,
)
from sixbirds_foundations_v.carrier.kernel import FiniteKernel
from sixbirds_foundations_v.e_system import (
    ActiveCarriedInstrument,
    CarriedLedger,
    ESystem,
    RepairMove,
    RepairSort,
    TheoryPackage,
)
from sixbirds_foundations_v.probe_economy import (
    AcquisitionLedgerEvidence,
    ActiveFamily,
    ActiveFamilyClassification,
    AllocationLedgerEvidence,
    AmountEntryWitness,
    ProbeCatalog,
    ProbeEconomy,
    RetirementLedgerEvidence,
)
from sixbirds_foundations_v.worlds.repair_world import (
    AcquisitionAction,
    AllocationAction,
    AmbiguousActionError,
    AuditFlags,
    AuditState,
    ChallengeClass,
    ChallengeProcess,
    CompilationStubAction,
    DeferredActionError,
    ExternalAction,
    LawfulnessStatus,
    MaintenanceStubAction,
    OfflineToggleStubAction,
    RepairAction,
    RepairWorldConfig,
    RepairWorldState,
    RetirementAction,
    UnlawfulActionError,
    budget_vector,
    is_lawful_action,
    repair_world_viability_kernel_history,
    ring_kernel,
    step,
)


REAL_REPAIR_PACKAGE = {"h0": "x", "h1": "y", "h2": "x", "h3": "y"}


def _trajectory() -> DeclaredTrajectory[int]:
    def tau(n: int) -> int:
        return n

    def legitimate_start(candidate_tau, n_start: int) -> bool:
        return n_start == 0 and candidate_tau(n_start) == 0

    return DeclaredTrajectory(
        legitimate_start=legitimate_start,
        supp_k=lambda z, z_next: z_next == z + 1,
        tau=tau,
        step_in_scope=lambda _n: True,
        n_start=0,
    )


def _evidence(n0: int, tag: FineSourceTag = FineSourceTag.committed_state) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=tag,
        generated_by_s=True,
        in_scope=True,
    )


def _string_policy(trajectory: DeclaredTrajectory[int], prefix: str) -> CarriedRecordPolicy[int, str]:
    def rho_of(z: int) -> str:
        return f"{prefix}-{z}"

    def coordinate_declared(readout) -> bool:
        return readout is rho_of

    return CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=coordinate_declared,
        rho_of=rho_of,
        name=prefix,
    )


def _active_policy(
    trajectory: DeclaredTrajectory[int],
    families_by_time: dict[int, ActiveFamily[str, object]],
) -> CarriedRecordPolicy[int, ActiveFamily[str, object]]:
    def rho_of(z: int) -> ActiveFamily[str, object]:
        return families_by_time[z]

    def coordinate_declared(readout) -> bool:
        return readout is rho_of

    return CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=coordinate_declared,
        rho_of=rho_of,
        name="active-family",
    )


def _ledger(trajectory: DeclaredTrajectory[int]) -> CarriedLedger[int, str]:
    entries = [
        "cost-a",
        "cost-b",
        "budget",
        "spend",
        "retire-a",
        "repair-budget",
    ]
    entry_by_time = {time: entry for time, entry in enumerate(entries)}
    time_by_entry = {entry: time for time, entry in entry_by_time.items()}

    def rho_of(z: int) -> str:
        return entry_by_time[z]

    def coordinate_declared(readout) -> bool:
        return readout is rho_of

    policy = CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=coordinate_declared,
        rho_of=rho_of,
        name="ledger",
    )
    return CarriedLedger(
        ledger_policy=policy,
        ledger_entries=entries,
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: _evidence(time_by_entry[entry])
        if entry in time_by_entry
        else None,
    )


def _family(support: list[str], weights: dict[str, int] | None = None) -> ActiveFamily[str, object]:
    defaults = {"a": 0, "b": 0, "c": 0}
    if weights:
        defaults.update(weights)
    return ActiveFamily(support=support, weight=defaults)


def _classification(n0: int) -> ActiveFamilyClassification:
    return ActiveFamilyClassification(
        n0=n0,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )


def _allocation_evidence(probes: list[str]) -> AllocationLedgerEvidence[str, str]:
    return AllocationLedgerEvidence(
        cost_entries=[
            (probe, AmountEntryWitness(entry=f"cost-{probe}", amount=1))
            for probe in probes
        ],
        budget_entry=AmountEntryWitness(entry="budget", amount=10),
        spend_entry=AmountEntryWitness(entry="spend", amount=1),
    )


def _acquisition_evidence(probe: str) -> AcquisitionLedgerEvidence[str]:
    return AcquisitionLedgerEvidence(
        cost_entry=AmountEntryWitness(entry=f"cost-{probe}", amount=1),
        budget_entry=AmountEntryWitness(entry="budget", amount=10),
        spend_entry=AmountEntryWitness(entry="spend", amount=1),
    )


def _world(
    families_by_time: dict[int, ActiveFamily[str, object]],
    *,
    y: int = 0,
    repair_payload=REAL_REPAIR_PACKAGE,
    q_map: dict[str, object] | None = None,
) -> tuple[
    RepairWorldConfig[str, object, str, str, str, str, str, str],
    RepairWorldState[str, int, str, object, str, str, str, str, str, str],
]:
    trajectory = _trajectory()
    ledger = _ledger(trajectory)
    active_policy = _active_policy(trajectory, families_by_time)
    economy = ProbeEconomy(
        catalog=ProbeCatalog(probes=["a", "b", "c"], complete_probe_catalog=True),
        active_family_policy=active_policy,
        same_family_saturated=lambda _active, probe: probe == "c",
        exposure_cost_entry=lambda entry, probe, cost: entry == f"cost-{probe}"
        and cost == 1,
        exposure_budget_entry=lambda entry, budget: entry == "budget" and budget == 10,
        exposure_spend_entry=lambda entry, spend: entry == "spend" and spend == 1,
        retirement_record_entry=lambda entry, probe: entry == f"retire-{probe}",
        budget_admissible=lambda _move: True,
    )

    theory = TheoryPackage(
        trajectory=trajectory,
        f="f",
        sigma_f="sigma",
        residual_family="residuals",
        audit_access="audit",
        formed_package=True,
    )
    defect_policy = _string_policy(trajectory, "defect")
    move_policy = _string_policy(trajectory, "move")
    audit_policy = _string_policy(trajectory, "audit")
    instrument_policy = _string_policy(trajectory, "instrument")
    repair_move = RepairMove(
        sort=RepairSort.P4,
        payload=repair_payload,
        move_record="move-0",
        move_record_evidence=_evidence(0),
        budget_line="repair-budget",
    )
    instrument_occurrence = CarriedRecordOccurrence(
        record="instrument-0",
        evidence=_evidence(0, FineSourceTag.audited_cell_records),
    )
    instrument = ActiveCarriedInstrument(
        instrument="instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=[instrument_occurrence],
        threshold_records=[instrument_occurrence],
        check_rule_records=[CheckRuleRecord(record=instrument_occurrence, audit="passes")],
        detects=lambda z, defect: z == 0 and defect == "defect-0",
        gate_allows=lambda _z, _defect, move: move == repair_move,
        re_audits=lambda _z, _move, _z_next, audit: audit == "audit-1",
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda _defect: repair_move,
        AdmissibleMove=lambda _ledger, _z, _defect, move: move.sort == RepairSort.P4,
    )
    config = RepairWorldConfig(
        kernel=ring_kernel(4),
        probe_economy=economy,
        e_system=system,
        challenge_process=ChallengeProcess(
            recurrence_period=1,
            default_challenge=ChallengeClass("binding"),
            binding_states=frozenset({3}),
        ),
    )
    state = RepairWorldState(
        y=y,
        q=q_map if q_map is not None else {"h0": 0, "h1": 0, "h2": 1, "h3": 1},
        L=families_by_time.get(y, families_by_time[0]),
        r=ledger,
        Lambda={
            "exposure": Fraction(10),
            "repair": Fraction(3),
            "maintenance": Fraction(2),
            "risk": Fraction(1),
        },
        A=AuditState(instrument=instrument, flags=AuditFlags(frozenset({1, 2}))),
    )
    return config, state


def test_constructs_minimal_complete_repair_world_state_and_config() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})

    assert config.e_system.is_well_formed()
    assert state.r.is_carried()
    assert state.A.instrument.is_carried()
    assert budget_vector(state)["exposure"] == Fraction(10)
    assert state.A.flags.levels == frozenset({1, 2})


def test_lawful_external_move_updates_y() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    action = ExternalAction(action_index=1, next_y=1)

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    assert step(config, state, action).y == 1


def test_lawful_stochastic_external_action_without_successor_is_ambiguous() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    stochastic_kernel = FiniteKernel(
        [
            [
                [0.5, 0.5, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        ]
    )
    stochastic_kernel.validate()
    stochastic_config = replace(config, kernel=stochastic_kernel)
    action = ExternalAction(action_index=0)

    assert is_lawful_action(stochastic_config, state, action).status is LawfulnessStatus.lawful
    with pytest.raises(AmbiguousActionError):
        step(stochastic_config, state, action)


def test_lawful_allocation_updates_active_family() -> None:
    active = _family(["a"], {"a": 1})
    reweighted = _family(["a"], {"a": 2})
    config, state = _world({0: active, 1: reweighted})
    action = AllocationAction(
        new_active_family=reweighted,
        pre_classification=_classification(0),
        post_classification=_classification(1),
        ledger_evidence=_allocation_evidence(["a"]),
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    assert step(config, state, action).L == reweighted


def test_lawful_acquisition_updates_active_family() -> None:
    active = _family(["a"], {"a": 1})
    extended = _family(["a", "b"], {"a": 1, "b": 1})
    config, state = _world({0: active, 1: extended})
    action = AcquisitionAction(
        probe="b",
        new_active_family=extended,
        pre_classification=_classification(0),
        post_classification=_classification(1),
        ledger_evidence=_acquisition_evidence("b"),
        strict=True,
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    assert step(config, state, action).L == extended


def test_lawful_retirement_updates_active_family() -> None:
    active = _family(["a"], {"a": 1})
    retired = _family([], {"a": 0})
    config, state = _world({0: active, 1: retired})
    action = RetirementAction(
        probe="a",
        new_active_family=retired,
        pre_classification=_classification(0),
        post_classification=_classification(1),
        ledger_evidence=RetirementLedgerEvidence(retirement_entry="retire-a"),
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    assert step(config, state, action).L == retired


def test_lawful_repair_move_refines_q_by_repair_join() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    action = RepairAction(
        repair_package=REAL_REPAIR_PACKAGE,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    next_state = step(config, state, action)

    assert next_state.q == {
        item: (state.q[item], REAL_REPAIR_PACKAGE[item])
        for item in state.q
    }
    assert next_state.q != state.q


def test_repair_move_rejects_package_not_supplied_by_repair_generator() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    bogus_package = {"h0": "ZZZ", "h1": "ZZZ", "h2": "ZZZ", "h3": "ZZZ"}
    lawful_action = RepairAction(
        repair_package=REAL_REPAIR_PACKAGE,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )
    mismatched_action = RepairAction(
        repair_package=bogus_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert is_lawful_action(config, state, lawful_action).status is LawfulnessStatus.lawful
    assert is_lawful_action(config, state, mismatched_action).status is LawfulnessStatus.unlawful
    with pytest.raises(UnlawfulActionError):
        step(config, state, mismatched_action)


def test_total_callable_repair_package_is_accepted_and_applied() -> None:
    active = _family(["a"], {"a": 1})
    package_values = {"h0": "x", "h1": "y", "h2": "x", "h3": "y"}

    def total_package(item: str) -> str:
        return package_values[item]

    config, state = _world({0: active}, repair_payload=total_package)
    action = RepairAction(
        repair_package=total_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    assert step(config, state, action).q == {
        item: (state.q[item], package_values[item])
        for item in state.q
    }


def test_partial_callable_repair_package_is_rejected_before_step_application() -> None:
    active = _family(["a"], {"a": 1})
    package_values = {"h0": "x", "h1": "y", "h3": "y"}

    def partial_package(item: str) -> str:
        return package_values[item]

    config, state = _world({0: active}, repair_payload=partial_package)
    action = RepairAction(
        repair_package=partial_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.unlawful
    with pytest.raises(UnlawfulActionError):
        step(config, state, action)


def test_stateful_callable_repair_package_is_materialized_once_during_step() -> None:
    active = _family(["a"], {"a": 1})
    package_values = {"h0": "x", "h1": "y", "h2": "x", "h3": "y"}
    call_counts = {item: 0 for item in package_values}

    def stateful_package(item: str) -> str:
        call_counts[item] += 1
        if item == "h2" and call_counts[item] > 1:
            raise KeyError("second-pass h2")
        return package_values[item]

    config, state = _world({0: active}, repair_payload=stateful_package)
    action = RepairAction(
        repair_package=stateful_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    next_state = step(config, state, action)

    assert next_state.q["h2"] == (1, "x")
    assert call_counts == {"h0": 1, "h1": 1, "h2": 1, "h3": 1}


def test_repair_step_uses_original_q_snapshot_if_package_mutates_live_q() -> None:
    active = _family(["a"], {"a": 1})
    mutable_q = {"h0": 0, "h1": 0, "h2": 1, "h3": 1}
    package_values = {"h0": "x", "h1": "y", "h2": "x", "h3": "y"}

    def mutating_package(item: str) -> str:
        if item == "h2":
            mutable_q["h2"] = "EVIL"
        return package_values[item]

    config, state = _world(
        {0: active},
        repair_payload=mutating_package,
        q_map=mutable_q,
    )
    action = RepairAction(
        repair_package=mutating_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
    assert mutable_q["h2"] == "EVIL"

    next_state = step(config, state, action)

    assert next_state.q["h2"] == (1, "x")
    assert next_state.q["h2"] != ("EVIL", "x")


def test_repair_package_cannot_launder_uncarried_ledger_before_d4_gate() -> None:
    active = _family(["a"], {"a": 1})
    honest_config, honest_state = _world({0: active})
    honest_state.r.ledger_entries.append("bad-entry")
    honest_action = RepairAction(
        repair_package=REAL_REPAIR_PACKAGE,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert not honest_state.r.is_carried()
    assert not honest_config.e_system.repair_step(
        honest_state.y,
        honest_action.z_next,
        honest_action.defect,
        honest_action.defect_evidence,
        honest_action.audit_record,
        honest_action.audit_record_evidence,
    )
    assert is_lawful_action(honest_config, honest_state, honest_action).status is LawfulnessStatus.unlawful

    laundering_entries: list[str] = []

    def laundering_package(item: str) -> str:
        if item == "h2" and "bad-entry" in laundering_entries:
            laundering_entries.remove("bad-entry")
        return REAL_REPAIR_PACKAGE[item]

    config, state = _world({0: active}, repair_payload=laundering_package)
    state.r.ledger_entries.append("bad-entry")
    laundering_entries = state.r.ledger_entries
    action = RepairAction(
        repair_package=laundering_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert not state.r.is_carried()
    assert is_lawful_action(config, state, action).status is LawfulnessStatus.unlawful
    with pytest.raises(UnlawfulActionError):
        step(config, state, action)


def test_repair_lawfulness_uses_single_repair_generator_evaluation() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    base_move = config.e_system.R_S("defect-0")
    bad_second_move = replace(base_move, budget_line="missing-ledger-line")
    calls: list[str] = []

    def counted_repair_generator(defect: str):
        calls.append(defect)
        return base_move if len(calls) == 1 else bad_second_move

    counted_system = replace(config.e_system, R_S=counted_repair_generator)
    counted_config = replace(config, e_system=counted_system)
    action = RepairAction(
        repair_package=REAL_REPAIR_PACKAGE,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert is_lawful_action(counted_config, state, action).status is LawfulnessStatus.lawful
    assert calls == ["defect-0"]


def test_repair_step_reuses_single_checked_repair_generator_payload() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    base_move = config.e_system.R_S("defect-0")
    bogus_package = {"h0": "ZZZ", "h1": "ZZZ", "h2": "ZZZ", "h3": "ZZZ"}
    calls: list[str] = []

    def changing_repair_generator(defect: str):
        calls.append(defect)
        payload = REAL_REPAIR_PACKAGE if len(calls) == 1 else bogus_package
        return replace(base_move, payload=payload)

    changing_system = replace(config.e_system, R_S=changing_repair_generator)
    changing_config = replace(config, e_system=changing_system)
    action = RepairAction(
        repair_package=REAL_REPAIR_PACKAGE,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    next_state = step(changing_config, state, action)

    assert next_state.q == {
        item: (state.q[item], REAL_REPAIR_PACKAGE[item])
        for item in state.q
    }
    assert calls == ["defect-0"]


def test_repair_package_match_does_not_call_mapping_eq_before_d4_gate() -> None:
    class LaunderingMapping(Mapping[str, str]):
        def __init__(self, entries: list[str]) -> None:
            self._entries = entries
            self._values = dict(REAL_REPAIR_PACKAGE)
            self.eq_calls = 0

        def __getitem__(self, key: str) -> str:
            return self._values[key]

        def __iter__(self) -> Iterator[str]:
            return iter(self._values)

        def __len__(self) -> int:
            return len(self._values)

        def __eq__(self, other) -> bool:
            self.eq_calls += 1
            if "bad-entry" in self._entries:
                self._entries.remove("bad-entry")
            return dict(self) == dict(other)

    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    state.r.ledger_entries.append("bad-entry")
    laundering_package = LaunderingMapping(state.r.ledger_entries)
    laundering_system = replace(
        config.e_system,
        R_S=lambda _defect: replace(
            config.e_system.R_S("defect-0"),
            payload=laundering_package,
        ),
    )
    laundering_config = replace(config, e_system=laundering_system)
    action = RepairAction(
        repair_package=laundering_package,
        z_next=1,
        defect="defect-0",
        defect_evidence=_evidence(0),
        audit_record="audit-1",
        audit_record_evidence=_evidence(1),
    )

    assert not state.r.is_carried()
    assert is_lawful_action(laundering_config, state, action).status is LawfulnessStatus.unlawful
    assert laundering_package.eq_calls == 0
    assert "bad-entry" in state.r.ledger_entries


def test_deferred_stub_actions_report_deferred_and_do_not_step() -> None:
    active = _family(["a"], {"a": 1})
    config, state = _world({0: active})
    actions = [
        CompilationStubAction(),
        MaintenanceStubAction(),
        OfflineToggleStubAction(),
    ]

    for action in actions:
        result = is_lawful_action(config, state, action)

        assert result.status is LawfulnessStatus.deferred
        assert result.reason == action.deferred_reason
        with pytest.raises(DeferredActionError):
            step(config, state, action)


def test_viability_kernel_history_over_ring_has_expected_fixed_point() -> None:
    active = _family(["a"], {"a": 1})
    config, template_state = _world({0: active})
    registry = {
        y: RepairWorldState(
            y=y,
            q=template_state.q,
            L=template_state.L,
            r=template_state.r,
            Lambda=template_state.Lambda,
            A=template_state.A,
        )
        for y in range(4)
    }
    actions = [ExternalAction(action_index=2)]

    history = repair_world_viability_kernel_history(
        config,
        registry,
        actions,
        safe=lambda state: config.challenge_process.challenge_at(0, state.y) is None,
        state_id_of=lambda state: state.y,
    )

    assert history == [{0, 1, 2}, {0, 1, 2}]
