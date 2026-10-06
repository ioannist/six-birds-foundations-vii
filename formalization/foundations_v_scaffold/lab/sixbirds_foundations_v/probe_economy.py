"""D6 probe-economy checks for the Repair-World lab.

This module ports the landed ``ProbeEconomy.lean`` surface as structural
runtime checkers.  Catalog completeness, same-family saturation, ledger-entry
semantics, and budget admissibility remain host-supplied certificates.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from sixbirds_foundations_v.carried_records import (
    CarriedRecordPolicy,
    FineSourceTag,
    carried_record_at,
)
from sixbirds_foundations_v.e_system import CarriedLedger
from sixbirds_foundations_v.xi import is_same_family_saturated as xi_is_same_family_saturated
from sixbirds_foundations_v.xi.matrix import Mat


Probe = TypeVar("Probe")
XiFamily = TypeVar("XiFamily")
LedgerEntry = TypeVar("LedgerEntry")


WeightSpec = Callable[[Probe], Any] | Mapping[Probe, Any]


@dataclass(frozen=True)
class ProbeCatalog(Generic[Probe]):
    probes: Sequence[Probe]
    complete_probe_catalog: bool

    def contains(self, probe: Probe) -> bool:
        return _contains(self.probes, probe)


@dataclass(frozen=True)
class ActiveFamily(Generic[Probe, XiFamily]):
    support: Sequence[Probe]
    weight: WeightSpec[Probe]
    as_xi_family: XiFamily | None = None

    def contains(self, probe: Probe) -> bool:
        return _contains(self.support, probe)

    def weight_of(self, probe: Probe) -> Any:
        if callable(self.weight):
            return self.weight(probe)
        return self.weight.get(probe, 0)


@dataclass(frozen=True)
class ActiveFamilyClassification:
    n0: int
    source_tag: FineSourceTag
    generated_by_s: bool
    in_scope: bool

    def __post_init__(self) -> None:
        if self.n0 < 0:
            raise ValueError("n0 must be nonnegative")


class ProbeMoveKind(str, Enum):
    allocation = "allocation"
    acquisition = "acquisition"
    retirement = "retirement"


@dataclass(frozen=True)
class ProbeMove(Generic[Probe, XiFamily]):
    kind: ProbeMoveKind
    active_family: ActiveFamily[Probe, XiFamily]
    new_active_family: ActiveFamily[Probe, XiFamily]
    probe: Probe | None = None


@dataclass(frozen=True)
class AmountEntryWitness(Generic[LedgerEntry]):
    entry: LedgerEntry
    amount: Any


@dataclass(frozen=True)
class AllocationLedgerEvidence(Generic[Probe, LedgerEntry]):
    cost_entries: Sequence[tuple[Probe, AmountEntryWitness[LedgerEntry]]]
    budget_entry: AmountEntryWitness[LedgerEntry]
    spend_entry: AmountEntryWitness[LedgerEntry]


@dataclass(frozen=True)
class AcquisitionLedgerEvidence(Generic[LedgerEntry]):
    cost_entry: AmountEntryWitness[LedgerEntry]
    budget_entry: AmountEntryWitness[LedgerEntry]
    spend_entry: AmountEntryWitness[LedgerEntry]


@dataclass(frozen=True)
class RetirementLedgerEvidence(Generic[LedgerEntry]):
    retirement_entry: LedgerEntry


@dataclass(frozen=True)
class ProbeEconomy(Generic[Probe, XiFamily, LedgerEntry]):
    catalog: ProbeCatalog[Probe]
    active_family_policy: CarriedRecordPolicy[Any, ActiveFamily[Probe, XiFamily]]
    same_family_saturated: Callable[[ActiveFamily[Probe, XiFamily], Probe], bool]
    exposure_cost_entry: Callable[[LedgerEntry, Probe, Any], bool]
    exposure_budget_entry: Callable[[LedgerEntry, Any], bool]
    exposure_spend_entry: Callable[[LedgerEntry, Any], bool]
    retirement_record_entry: Callable[[LedgerEntry, Probe], bool]
    budget_admissible: Callable[[ProbeMove[Probe, XiFamily]], bool]

    def is_valid(self) -> bool:
        return self.catalog.complete_probe_catalog is True


def _contains(items: Sequence[Any], value: Any) -> bool:
    return any(item == value for item in items)


def _unique(items: Sequence[Any]) -> list[Any]:
    unique: list[Any] = []
    for item in items:
        if not _contains(unique, item):
            unique.append(item)
    return unique


def _same_members(left: Sequence[Any], right: Sequence[Any]) -> bool:
    return all(_contains(right, item) for item in left) and all(
        _contains(left, item) for item in right
    )


def _entry_in_ledger(ledger: CarriedLedger[Any, LedgerEntry], entry: LedgerEntry) -> bool:
    return _contains(ledger.ledger_entries, entry)


def _ledger_uses_economy_trajectory(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
) -> bool:
    return ledger.ledger_policy.trajectory is economy.active_family_policy.trajectory


def _weight_probe_universe(
    catalog: ProbeCatalog[Probe],
    active_family: ActiveFamily[Probe, XiFamily],
    new_active_family: ActiveFamily[Probe, XiFamily],
) -> list[Probe]:
    return _unique([*catalog.probes, *active_family.support, *new_active_family.support])


def active_support_in_catalog(
    catalog: ProbeCatalog[Probe],
    active_family: ActiveFamily[Probe, XiFamily],
) -> bool:
    return all(catalog.contains(probe) for probe in active_family.support)


def active_family_carried_at(
    policy: CarriedRecordPolicy[Any, ActiveFamily[Probe, XiFamily]],
    active_family: ActiveFamily[Probe, XiFamily],
    n0: int,
    source_tag: FineSourceTag,
    generated_by_s: bool,
    in_scope: bool,
) -> bool:
    return carried_record_at(
        policy,
        active_family,
        n0,
        source_tag,
        generated_by_s,
        in_scope,
    )


def lawful_active_family_at(
    catalog: ProbeCatalog[Probe],
    active_family: ActiveFamily[Probe, XiFamily],
    policy: CarriedRecordPolicy[Any, ActiveFamily[Probe, XiFamily]],
    n0: int,
    source_tag: FineSourceTag,
    generated_by_s: bool,
    in_scope: bool,
) -> bool:
    return active_support_in_catalog(catalog, active_family) and active_family_carried_at(
        policy,
        active_family,
        n0,
        source_tag,
        generated_by_s,
        in_scope,
    )


def same_family_saturated(
    saturated_predicate: Callable[[ActiveFamily[Probe, XiFamily], Probe], bool],
    active_family: ActiveFamily[Probe, XiFamily],
    probe: Probe,
) -> bool:
    return saturated_predicate(active_family, probe)


def acquisition_strict(
    saturated_predicate: Callable[[ActiveFamily[Probe, XiFamily], Probe], bool],
    active_family: ActiveFamily[Probe, XiFamily],
    probe: Probe,
) -> bool:
    return not same_family_saturated(saturated_predicate, active_family, probe)


def support_adds_probe(
    active_family: ActiveFamily[Probe, XiFamily],
    probe: Probe,
    new_active_family: ActiveFamily[Probe, XiFamily],
) -> bool:
    if active_family.contains(probe):
        return False
    universe = _unique([*active_family.support, *new_active_family.support, probe])
    return all(
        new_active_family.contains(candidate)
        == (candidate == probe or active_family.contains(candidate))
        for candidate in universe
    )


def support_removes_probe(
    active_family: ActiveFamily[Probe, XiFamily],
    probe: Probe,
    new_active_family: ActiveFamily[Probe, XiFamily],
) -> bool:
    if not active_family.contains(probe):
        return False
    universe = _unique([*active_family.support, *new_active_family.support, probe])
    return all(
        new_active_family.contains(candidate)
        == (active_family.contains(candidate) and candidate != probe)
        for candidate in universe
    )


def _weights_only_on_shared_support(
    catalog: ProbeCatalog[Probe],
    active_family: ActiveFamily[Probe, XiFamily],
    new_active_family: ActiveFamily[Probe, XiFamily],
) -> bool:
    return all(
        new_active_family.weight_of(probe) == active_family.weight_of(probe)
        for probe in _weight_probe_universe(catalog, active_family, new_active_family)
        if not active_family.contains(probe)
    )


def _cost_entry_exists(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
    probe: Probe,
    witness: AmountEntryWitness[LedgerEntry],
) -> bool:
    return _entry_in_ledger(ledger, witness.entry) and economy.exposure_cost_entry(
        witness.entry,
        probe,
        witness.amount,
    )


def _budget_entry_exists(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
    witness: AmountEntryWitness[LedgerEntry],
) -> bool:
    return _entry_in_ledger(ledger, witness.entry) and economy.exposure_budget_entry(
        witness.entry,
        witness.amount,
    )


def _spend_entry_exists(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
    witness: AmountEntryWitness[LedgerEntry],
) -> bool:
    return _entry_in_ledger(ledger, witness.entry) and economy.exposure_spend_entry(
        witness.entry,
        witness.amount,
    )


def _allocation_cost_witness(
    evidence: AllocationLedgerEvidence[Probe, LedgerEntry],
    probe: Probe,
) -> AmountEntryWitness[LedgerEntry] | None:
    for candidate, witness in evidence.cost_entries:
        if candidate == probe:
            return witness
    return None


def lawful_allocation(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
    active_family: ActiveFamily[Probe, XiFamily],
    new_active_family: ActiveFamily[Probe, XiFamily],
    pre_classification: ActiveFamilyClassification,
    post_classification: ActiveFamilyClassification,
    ledger_evidence: AllocationLedgerEvidence[Probe, LedgerEntry],
) -> bool:
    move = ProbeMove(
        kind=ProbeMoveKind.allocation,
        active_family=active_family,
        new_active_family=new_active_family,
    )
    return (
        economy.is_valid()
        and ledger.is_carried()
        and _ledger_uses_economy_trajectory(economy, ledger)
        and lawful_active_family_at(
            economy.catalog,
            active_family,
            economy.active_family_policy,
            pre_classification.n0,
            pre_classification.source_tag,
            pre_classification.generated_by_s,
            pre_classification.in_scope,
        )
        and _same_members(new_active_family.support, active_family.support)
        and _weights_only_on_shared_support(economy.catalog, active_family, new_active_family)
        and all(
            (witness := _allocation_cost_witness(ledger_evidence, probe)) is not None
            and _cost_entry_exists(economy, ledger, probe, witness)
            for probe in _unique(list(active_family.support))
        )
        and _budget_entry_exists(economy, ledger, ledger_evidence.budget_entry)
        and _spend_entry_exists(economy, ledger, ledger_evidence.spend_entry)
        and economy.budget_admissible(move)
        and lawful_active_family_at(
            economy.catalog,
            new_active_family,
            economy.active_family_policy,
            post_classification.n0,
            post_classification.source_tag,
            post_classification.generated_by_s,
            post_classification.in_scope,
        )
    )


def lawful_acquisition(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
    active_family: ActiveFamily[Probe, XiFamily],
    probe: Probe,
    new_active_family: ActiveFamily[Probe, XiFamily],
    pre_classification: ActiveFamilyClassification,
    post_classification: ActiveFamilyClassification,
    ledger_evidence: AcquisitionLedgerEvidence[LedgerEntry],
    *,
    strict: bool,
) -> bool:
    move = ProbeMove(
        kind=ProbeMoveKind.acquisition,
        active_family=active_family,
        new_active_family=new_active_family,
        probe=probe,
    )
    return (
        economy.is_valid()
        and ledger.is_carried()
        and _ledger_uses_economy_trajectory(economy, ledger)
        and lawful_active_family_at(
            economy.catalog,
            active_family,
            economy.active_family_policy,
            pre_classification.n0,
            pre_classification.source_tag,
            pre_classification.generated_by_s,
            pre_classification.in_scope,
        )
        and economy.catalog.contains(probe)
        and not active_family.contains(probe)
        and support_adds_probe(active_family, probe, new_active_family)
        and strict is True
        and acquisition_strict(economy.same_family_saturated, active_family, probe)
        and _cost_entry_exists(economy, ledger, probe, ledger_evidence.cost_entry)
        and _budget_entry_exists(economy, ledger, ledger_evidence.budget_entry)
        and _spend_entry_exists(economy, ledger, ledger_evidence.spend_entry)
        and economy.budget_admissible(move)
        and lawful_active_family_at(
            economy.catalog,
            new_active_family,
            economy.active_family_policy,
            post_classification.n0,
            post_classification.source_tag,
            post_classification.generated_by_s,
            post_classification.in_scope,
        )
    )


def lawful_retirement(
    economy: ProbeEconomy[Probe, XiFamily, LedgerEntry],
    ledger: CarriedLedger[Any, LedgerEntry],
    active_family: ActiveFamily[Probe, XiFamily],
    probe: Probe,
    new_active_family: ActiveFamily[Probe, XiFamily],
    pre_classification: ActiveFamilyClassification,
    post_classification: ActiveFamilyClassification,
    ledger_evidence: RetirementLedgerEvidence[LedgerEntry],
) -> bool:
    move = ProbeMove(
        kind=ProbeMoveKind.retirement,
        active_family=active_family,
        new_active_family=new_active_family,
        probe=probe,
    )
    return (
        economy.is_valid()
        and ledger.is_carried()
        and _ledger_uses_economy_trajectory(economy, ledger)
        and lawful_active_family_at(
            economy.catalog,
            active_family,
            economy.active_family_policy,
            pre_classification.n0,
            pre_classification.source_tag,
            pre_classification.generated_by_s,
            pre_classification.in_scope,
        )
        and active_family.contains(probe)
        and support_removes_probe(active_family, probe, new_active_family)
        and _entry_in_ledger(ledger, ledger_evidence.retirement_entry)
        and economy.retirement_record_entry(ledger_evidence.retirement_entry, probe)
        and economy.budget_admissible(move)
        and lawful_active_family_at(
            economy.catalog,
            new_active_family,
            economy.active_family_policy,
            post_classification.n0,
            post_classification.source_tag,
            post_classification.generated_by_s,
            post_classification.in_scope,
        )
    )


def xi_same_family_saturated_adapter(
    active_family: ActiveFamily[Any, Mat],
    probe: Any,
    *,
    C: Mat,
    D: Mat,
    KLLdagger: Mat,
    B: Mat,
    probe_xi_family: Mat | None = None,
) -> bool:
    """Optional Xi-backed same-family-saturation predicate."""

    if active_family.as_xi_family is None:
        raise ValueError("active_family.as_xi_family is required for Xi saturation")
    M = probe_xi_family if probe_xi_family is not None else getattr(probe, "as_xi_family", None)
    if M is None:
        raise ValueError("probe_xi_family is required for Xi saturation")
    return xi_is_same_family_saturated(C, active_family.as_xi_family, D, M, KLLdagger, B)


__all__ = [
    "AcquisitionLedgerEvidence",
    "ActiveFamily",
    "ActiveFamilyClassification",
    "AllocationLedgerEvidence",
    "AmountEntryWitness",
    "ProbeCatalog",
    "ProbeEconomy",
    "ProbeMove",
    "ProbeMoveKind",
    "RetirementLedgerEvidence",
    "acquisition_strict",
    "active_family_carried_at",
    "active_support_in_catalog",
    "lawful_acquisition",
    "lawful_active_family_at",
    "lawful_allocation",
    "lawful_retirement",
    "same_family_saturated",
    "support_adds_probe",
    "support_removes_probe",
    "xi_same_family_saturated_adapter",
]
