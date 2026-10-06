from __future__ import annotations

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordPolicy,
    DeclaredTrajectory,
    FineSourceTag,
)
from sixbirds_foundations_v.e_system import CarriedLedger
from sixbirds_foundations_v.probe_economy import (
    AcquisitionLedgerEvidence,
    ActiveFamily,
    ActiveFamilyClassification,
    AllocationLedgerEvidence,
    AmountEntryWitness,
    ProbeCatalog,
    ProbeEconomy,
    RetirementLedgerEvidence,
    active_support_in_catalog,
    lawful_acquisition,
    lawful_active_family_at,
    lawful_allocation,
    lawful_retirement,
    support_adds_probe,
    support_removes_probe,
    xi_same_family_saturated_adapter,
)
from sixbirds_foundations_v.xi import mat


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
        "cost-rogue",
        "budget",
        "spend",
        "retire-a",
        "retire-b",
        "retire-rogue",
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
        ledger_evidence=lambda entry: CarriedRecordEvidence(
            n0=time_by_entry[entry],
            source_tag=FineSourceTag.committed_state,
            generated_by_s=True,
            in_scope=True,
        )
        if entry in time_by_entry
        else None,
    )


def _classification(
    n0: int,
    *,
    tag: FineSourceTag = FineSourceTag.committed_state,
) -> ActiveFamilyClassification:
    return ActiveFamilyClassification(
        n0=n0,
        source_tag=tag,
        generated_by_s=True,
        in_scope=True,
    )


def _family(support: list[str], weights: dict[str, int] | None = None) -> ActiveFamily[str, object]:
    default_weights = {"a": 0, "b": 0, "c": 0, "rogue": 0}
    if weights:
        default_weights.update(weights)
    return ActiveFamily(support=support, weight=default_weights)


def _economy(
    families_by_time: dict[int, ActiveFamily[str, object]],
    *,
    saturated: set[str] | None = None,
    ledger_trajectory: DeclaredTrajectory[int] | None = None,
) -> tuple[ProbeEconomy[str, object, str], CarriedLedger[int, str]]:
    trajectory = _trajectory()
    policy = _active_policy(trajectory, families_by_time)
    ledger = _ledger(ledger_trajectory or trajectory)
    saturated = saturated or set()
    economy = ProbeEconomy(
        catalog=ProbeCatalog(probes=["a", "b", "c"], complete_probe_catalog=True),
        active_family_policy=policy,
        same_family_saturated=lambda _active, probe: probe in saturated,
        exposure_cost_entry=lambda entry, probe, cost: entry == f"cost-{probe}"
        and cost == 1,
        exposure_budget_entry=lambda entry, budget: entry == "budget" and budget == 10,
        exposure_spend_entry=lambda entry, spend: entry == "spend" and spend == 1,
        retirement_record_entry=lambda entry, probe: entry == f"retire-{probe}",
        budget_admissible=lambda _move: True,
    )
    return economy, ledger


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


def test_genuinely_lawful_allocation_passes() -> None:
    active = _family(["a"], {"a": 1})
    reweighted = _family(["a"], {"a": 2})
    economy, ledger = _economy({0: active, 1: reweighted})

    assert lawful_allocation(
        economy,
        ledger,
        active,
        reweighted,
        _classification(0),
        _classification(1),
        _allocation_evidence(["a"]),
    )


def test_genuinely_lawful_acquisition_passes() -> None:
    active = _family(["a"], {"a": 1})
    extended = _family(["a", "b"], {"a": 1, "b": 1})
    economy, ledger = _economy({0: active, 1: extended})

    assert support_adds_probe(active, "b", extended)
    assert lawful_acquisition(
        economy,
        ledger,
        active,
        "b",
        extended,
        _classification(0),
        _classification(1),
        _acquisition_evidence("b"),
        strict=True,
    )


def test_genuinely_lawful_retirement_passes() -> None:
    active = _family(["a"], {"a": 1})
    retired = _family([], {"a": 0})
    economy, ledger = _economy({0: active, 1: retired})

    assert support_removes_probe(active, "a", retired)
    assert lawful_retirement(
        economy,
        ledger,
        active,
        "a",
        retired,
        _classification(0),
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-a"),
    )


def test_same_family_saturated_candidate_cannot_be_lawful_acquisition() -> None:
    active = _family(["a"], {"a": 1})
    extended = _family(["a", "b"], {"a": 1, "b": 1})
    economy, ledger = _economy({0: active, 1: extended}, saturated={"b"})

    assert support_adds_probe(active, "b", extended)
    assert lawful_active_family_at(
        economy.catalog,
        active,
        economy.active_family_policy,
        0,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert lawful_active_family_at(
        economy.catalog,
        extended,
        economy.active_family_policy,
        1,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert not lawful_acquisition(
        economy,
        ledger,
        active,
        "b",
        extended,
        _classification(0),
        _classification(1),
        _acquisition_evidence("b"),
        strict=True,
    )


def test_allocation_cannot_smuggle_new_active_probe() -> None:
    active = _family(["a"], {"a": 1, "b": 0})
    smuggled = _family(["a", "b"], {"a": 2, "b": 0})
    economy, ledger = _economy({0: active, 1: smuggled})

    assert active_support_in_catalog(economy.catalog, smuggled)
    assert lawful_active_family_at(
        economy.catalog,
        active,
        economy.active_family_policy,
        0,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert lawful_active_family_at(
        economy.catalog,
        smuggled,
        economy.active_family_policy,
        1,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert not active.contains("b")
    assert smuggled.contains("b")
    assert not lawful_allocation(
        economy,
        ledger,
        active,
        smuggled,
        _classification(0),
        _classification(1),
        _allocation_evidence(["a"]),
    )


def test_pre_state_carriedness_is_required_for_all_three_moves() -> None:
    active = _family(["a"], {"a": 1})
    reweighted = _family(["a"], {"a": 2})
    extended = _family(["a", "b"], {"a": 1, "b": 1})
    retired = _family([], {"a": 0})
    pre_bad = _classification(0, tag=FineSourceTag.fallback)

    allocation_economy, allocation_ledger = _economy({0: active, 1: reweighted})
    acquisition_economy, acquisition_ledger = _economy({0: active, 1: extended})
    retirement_economy, retirement_ledger = _economy({0: active, 1: retired})

    assert not lawful_active_family_at(
        allocation_economy.catalog,
        active,
        allocation_economy.active_family_policy,
        pre_bad.n0,
        pre_bad.source_tag,
        pre_bad.generated_by_s,
        pre_bad.in_scope,
    )
    assert not lawful_allocation(
        allocation_economy,
        allocation_ledger,
        active,
        reweighted,
        pre_bad,
        _classification(1),
        _allocation_evidence(["a"]),
    )
    assert not lawful_acquisition(
        acquisition_economy,
        acquisition_ledger,
        active,
        "b",
        extended,
        pre_bad,
        _classification(1),
        _acquisition_evidence("b"),
        strict=True,
    )
    assert not lawful_retirement(
        retirement_economy,
        retirement_ledger,
        active,
        "a",
        retired,
        pre_bad,
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-a"),
    )


def test_pre_state_catalog_validity_is_checked_before_retirement() -> None:
    malformed = _family(["a", "rogue"], {"a": 1, "rogue": 1})
    retired_rogue = _family(["a"], {"a": 1, "rogue": 0})
    economy, ledger = _economy({0: malformed, 1: retired_rogue})

    assert not active_support_in_catalog(economy.catalog, malformed)
    assert not lawful_retirement(
        economy,
        ledger,
        malformed,
        "rogue",
        retired_rogue,
        _classification(0),
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-rogue"),
    )


def test_non_catalog_pre_support_is_rejected_by_all_three_move_types() -> None:
    malformed = _family(["a", "rogue"], {"a": 1, "rogue": 1})
    reweighted = _family(["a", "rogue"], {"a": 2, "rogue": 1})
    extended = _family(["a", "rogue", "b"], {"a": 1, "rogue": 1, "b": 1})
    retired_rogue = _family(["a"], {"a": 1, "rogue": 0})

    allocation_economy, allocation_ledger = _economy({0: malformed, 1: reweighted})
    acquisition_economy, acquisition_ledger = _economy({0: malformed, 1: extended})
    retirement_economy, retirement_ledger = _economy({0: malformed, 1: retired_rogue})

    assert not active_support_in_catalog(allocation_economy.catalog, malformed)
    assert not lawful_allocation(
        allocation_economy,
        allocation_ledger,
        malformed,
        reweighted,
        _classification(0),
        _classification(1),
        _allocation_evidence(["a", "rogue"]),
    )
    assert not lawful_acquisition(
        acquisition_economy,
        acquisition_ledger,
        malformed,
        "b",
        extended,
        _classification(0),
        _classification(1),
        _acquisition_evidence("b"),
        strict=True,
    )
    assert not lawful_retirement(
        retirement_economy,
        retirement_ledger,
        malformed,
        "rogue",
        retired_rogue,
        _classification(0),
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-rogue"),
    )


def test_allocation_rejects_ledger_policy_with_mismatched_trajectory() -> None:
    active = _family(["a"], {"a": 1})
    reweighted = _family(["a"], {"a": 2})
    economy, ledger = _economy({0: active, 1: reweighted}, ledger_trajectory=_trajectory())

    assert economy.active_family_policy.trajectory is not ledger.ledger_policy.trajectory
    assert ledger.is_carried()
    assert lawful_active_family_at(
        economy.catalog,
        active,
        economy.active_family_policy,
        0,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert lawful_active_family_at(
        economy.catalog,
        reweighted,
        economy.active_family_policy,
        1,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert not lawful_allocation(
        economy,
        ledger,
        active,
        reweighted,
        _classification(0),
        _classification(1),
        _allocation_evidence(["a"]),
    )


def test_acquisition_rejects_ledger_policy_with_mismatched_trajectory() -> None:
    active = _family(["a"], {"a": 1})
    extended = _family(["a", "b"], {"a": 1, "b": 1})
    economy, ledger = _economy({0: active, 1: extended}, ledger_trajectory=_trajectory())

    assert economy.active_family_policy.trajectory is not ledger.ledger_policy.trajectory
    assert ledger.is_carried()
    assert support_adds_probe(active, "b", extended)
    assert not lawful_acquisition(
        economy,
        ledger,
        active,
        "b",
        extended,
        _classification(0),
        _classification(1),
        _acquisition_evidence("b"),
        strict=True,
    )


def test_retirement_rejects_ledger_policy_with_mismatched_trajectory() -> None:
    active = _family(["a"], {"a": 1})
    retired = _family([], {"a": 0})
    economy, ledger = _economy({0: active, 1: retired}, ledger_trajectory=_trajectory())

    assert economy.active_family_policy.trajectory is not ledger.ledger_policy.trajectory
    assert ledger.is_carried()
    assert support_removes_probe(active, "a", retired)
    assert not lawful_retirement(
        economy,
        ledger,
        active,
        "a",
        retired,
        _classification(0),
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-a"),
    )


def test_retirement_of_inactive_probe_fails() -> None:
    active = _family(["a"], {"a": 1, "b": 0})
    unchanged = _family(["a"], {"a": 1, "b": 0})
    economy, ledger = _economy({0: active, 1: unchanged})

    assert not lawful_retirement(
        economy,
        ledger,
        active,
        "b",
        unchanged,
        _classification(0),
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-b"),
    )


def test_retirement_record_must_reference_the_specific_probe() -> None:
    active = _family(["a"], {"a": 1})
    retired = _family([], {"a": 0})
    economy, ledger = _economy({0: active, 1: retired})

    assert not lawful_retirement(
        economy,
        ledger,
        active,
        "a",
        retired,
        _classification(0),
        _classification(1),
        RetirementLedgerEvidence(retirement_entry="retire-b"),
    )


def test_xi_same_family_saturation_adapter_uses_optional_xi_hook() -> None:
    C = mat([[1, 0], [0, 2]])
    L = mat([[1, 1]])
    D = mat([[1, 0]])
    KLLdagger = mat([["2/3"]])
    active = ActiveFamily(support=["a"], weight={"a": 1}, as_xi_family=L)
    M = mat([[2, 2]])

    assert xi_same_family_saturated_adapter(
        active,
        "b",
        C=C,
        D=D,
        KLLdagger=KLLdagger,
        B=mat([[2]]),
        probe_xi_family=M,
    )
