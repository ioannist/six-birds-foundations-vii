from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from typing import Any, Callable, Iterable, Mapping, Sequence


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class EnvelopeResult:
    family_id: str
    description: str
    raw_cardinality: int
    canonical_cardinality: int
    accepted_cardinality: int
    rejected_cardinality: int
    accepted_sha256: str
    rejected_sha256: str
    nonclaim: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "description": self.description,
            "raw_cardinality": self.raw_cardinality,
            "canonical_cardinality": self.canonical_cardinality,
            "accepted_cardinality": self.accepted_cardinality,
            "rejected_cardinality": self.rejected_cardinality,
            "accepted_sha256": self.accepted_sha256,
            "rejected_sha256": self.rejected_sha256,
            "nonclaim": self.nonclaim,
        }


def _rows(names: Sequence[str], domains: Sequence[Sequence[Any]]) -> list[dict[str, Any]]:
    return [dict(zip(names, values, strict=True)) for values in product(*domains)]


def _partition(
    family_id: str,
    description: str,
    rows: list[dict[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
    *,
    raw_cardinality: int | None = None,
    nonclaim: str,
) -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    accepted = [row for row in rows if predicate(row)]
    rejected = [row for row in rows if not predicate(row)]
    result = EnvelopeResult(
        family_id=family_id,
        description=description,
        raw_cardinality=raw_cardinality if raw_cardinality is not None else len(rows),
        canonical_cardinality=len(rows),
        accepted_cardinality=len(accepted),
        rejected_cardinality=len(rejected),
        accepted_sha256=digest(accepted),
        rejected_sha256=digest(rejected),
        nonclaim=nonclaim,
    )
    return result, accepted, rejected


def access_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = ("expressible", "present", "exposed", "recoverable", "admissible", "reachable", "occurrent")
    rows = _rows(names, [(False, True)] * len(names))

    def coherent(r: Mapping[str, Any]) -> bool:
        return (
            (not r["occurrent"] or r["reachable"])
            and (not r["reachable"] or r["admissible"])
            and (not r["admissible"] or r["present"])
            and (not r["recoverable"] or r["exposed"])
            and (not r["exposed"] or r["present"])
            and (not r["present"] or r["expressible"])
        )

    return _partition(
        "P2-E01",
        "Seven-coordinate access normal forms satisfying only the declared implication spine.",
        rows,
        coherent,
        nonclaim="The finite Boolean carrier does not impose a total order or identify SBT access with seven bits universally.",
    )


def transition_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = ("sound", "executable", "guard_active", "resources_available", "reachable", "fired", "occurrent")
    rows = _rows(names, [(False, True)] * len(names))

    def coherent(r: Mapping[str, Any]) -> bool:
        return (
            (not r["executable"] or (r["sound"] and r["guard_active"] and r["resources_available"]))
            and (not r["reachable"] or (r["executable"] and r["guard_active"] and r["resources_available"]))
            and (not r["fired"] or r["reachable"])
            and (not r["occurrent"] or r["fired"])
        )

    return _partition(
        "P2-E02",
        "Operational profiles separating rule soundness, execution, reachability, firing, and occurrence.",
        rows,
        coherent,
        nonclaim="Accepted profiles encode the Phase-2 transition contract; they do not prove a domain-specific rule sound.",
    )


def bootstrap_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = ("closed_family", "seed", "generator_reachable", "external_provision", "first_extension")
    rows = _rows(names, [(False, True)] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        authorized = (
            r["seed"]
            or r["generator_reachable"]
            or (not r["closed_family"] and r["external_provision"])
        )
        return not r["first_extension"] or authorized

    return _partition(
        "P2-E03",
        "Bootstrap assignments with admitted-seed, reachable-generator, and open-family external-provision authorization.",
        rows,
        law,
        nonclaim="The obstruction is scoped to closed families; an open family may admit an explicitly recorded external provision.",
    )


def commitment_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "preregistered", "precedes_evidence", "retrospective", "task_blind",
        "outcome_independent", "symmetry_certified", "control_matched",
        "prospective_credit",
    )
    rows = _rows(names, [(False, True)] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        return not r["prospective_credit"] or (
            r["preregistered"]
            and r["precedes_evidence"]
            and not r["retrospective"]
            and r["task_blind"]
            and r["outcome_independent"]
            and r["symmetry_certified"]
            and r["control_matched"]
        )

    return _partition(
        "P2-E04",
        "Prospective-credit assignments with preregistration, precedence, task blindness, outcome independence, symmetry, and matched controls.",
        rows,
        law,
        nonclaim="Boolean certificate coordinates are a finite assay, not a universal clock, symmetry theory, or causal order.",
    )


def origin_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = ("same_origin", "common_carrier", "common_instrument", "left_access", "right_access", "left_peer", "right_peer", "source_independent")
    canonical = _rows(names, [(False, True)] * len(names))

    # Four labeled source pairs (0,0),(0,1),(1,0),(1,1) collapse to two
    # lineage types: same and distinct.  The other seven coordinates are fixed.
    raw_cardinality = len(canonical) * 2

    def coherent(r: Mapping[str, Any]) -> bool:
        return r["source_independent"] != r["same_origin"]

    return _partition(
        "P2-E05",
        "Two-package provenance/access profiles normalized by source-ID renaming.",
        canonical,
        coherent,
        raw_cardinality=raw_cardinality,
        nonclaim="Common origin, carrier, or instrument is not itself a peer-transport certificate.",
    )


def totality_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = ("source_total", "target_partial", "target_self_owned", "adapter_certified", "transfer_licensed")
    rows = _rows(names, [(False, True)] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        return not r["transfer_licensed"] or (
            r["source_total"]
            and r["target_self_owned"]
            and (not r["target_partial"] or r["adapter_certified"])
        )

    return _partition(
        "P2-E06",
        "Total-lens transfer assignments with self-owned targets and explicit partial-target adapter licensing.",
        rows,
        law,
        nonclaim="Self-ownership and an adapter theorem are independent obligations; the adapter must still prove the concrete notions coincide where used.",
    )


def horizon_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = ("complete", "family_closed", "detector_power", "occurrence_within", "occurrence_after", "universal_negative_credit")
    rows = _rows(names, [(False, True)] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        return not r["universal_negative_credit"] or (
            r["complete"]
            and r["family_closed"]
            and r["detector_power"]
            and not r["occurrence_within"]
            and not r["occurrence_after"]
        )

    return _partition(
        "P2-E07",
        "Finite-horizon negative-force assignments with family closure and detector-power gates.",
        rows,
        law,
        nonclaim="Finite-horizon nulls without closure and detector power remain bounded evidence only.",
    )


def observer_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    rows = _rows(("occupied", "charged", "native_credit"), [(0, 1, 2), (0, 1, 2), (False, True)])

    def law(r: Mapping[str, Any]) -> bool:
        return not r["native_credit"] or r["occupied"] <= r["charged"]

    return _partition(
        "P2-E08",
        "Observer occupancy/pricing assignments over costs 0,1,2.",
        rows,
        law,
        nonclaim="The bounded costs test ledger discipline; they do not calibrate physical observer cost.",
    )


def settlement_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    rows = _rows(
        ("allocated", "spent", "occupied", "refunded", "settled"),
        [(0, 1, 2), (0, 1, 2), (0, 1, 2), (0, 1, 2), (False, True)],
    )

    def law(r: Mapping[str, Any]) -> bool:
        return not r["settled"] or r["spent"] + r["occupied"] + r["refunded"] == r["allocated"]

    return _partition(
        "P2-E09",
        "Failed-admission settlement assignments over costs 0,1,2.",
        rows,
        law,
        nonclaim="Conservation is with respect to the declared ledger; omitted resources remain a falsifier.",
    )


def all_envelopes() -> list[tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]]:
    return [
        access_envelope(),
        transition_envelope(),
        bootstrap_envelope(),
        commitment_envelope(),
        origin_envelope(),
        totality_envelope(),
        horizon_envelope(),
        observer_envelope(),
        settlement_envelope(),
    ]


def _minimal(rows: Iterable[Mapping[str, Any]], required: Callable[[Mapping[str, Any]], bool]) -> dict[str, Any]:
    matches = [dict(row) for row in rows if required(row)]
    if not matches:
        raise AssertionError("no witness in declared finite family")
    return min(matches, key=lambda row: (sum(bool(v) for v in row.values()), canonical_bytes(row)))


def canonical_witnesses() -> list[dict[str, Any]]:
    access = access_envelope()[1]
    transition = transition_envelope()[1]
    origin = origin_envelope()[1]
    horizon = horizon_envelope()[1]
    bootstrap_rejected = bootstrap_envelope()[2]
    commitment_rejected = commitment_envelope()[2]
    totality_rejected = totality_envelope()[2]
    observer_rejected = observer_envelope()[2]

    specs: list[tuple[str, str, str, Mapping[str, Any]]] = [
        ("P2-W01", "VII-C001", "Expressibility does not imply presence.", _minimal(access, lambda r: r["expressible"] and not r["present"])),
        ("P2-W02", "VII-C001", "Presence does not imply exposure.", _minimal(access, lambda r: r["present"] and not r["exposed"])),
        ("P2-W03", "VII-C022", "Exposure does not imply recoverability.", _minimal(access, lambda r: r["exposed"] and not r["recoverable"])),
        ("P2-W04", "VII-C022", "Recoverability does not imply admissibility.", _minimal(access, lambda r: r["recoverable"] and not r["admissible"])),
        ("P2-W05", "VII-C022", "Admissibility does not imply recoverability.", _minimal(access, lambda r: r["admissible"] and not r["recoverable"])),
        ("P2-W06", "VII-C001", "Admissibility does not imply reachability.", _minimal(access, lambda r: r["admissible"] and not r["reachable"])),
        ("P2-W07", "VII-C021", "Reachability does not imply occurrence.", _minimal(transition, lambda r: r["reachable"] and not r["occurrent"])),
        ("P2-W08", "VII-C021", "Soundness does not imply reachability.", _minimal(transition, lambda r: r["sound"] and not r["reachable"])),
        ("P2-W09", "VII-C005", "Common origin does not imply shared access.", _minimal(origin, lambda r: r["same_origin"] and not (r["left_access"] and r["right_access"] and r["left_peer"] and r["right_peer"]))),
        ("P2-W10", "VII-C005", "Shared access does not imply source independence.", _minimal(origin, lambda r: r["same_origin"] and r["left_access"] and r["right_access"] and r["left_peer"] and r["right_peer"])),
        ("P2-W11", "VII-C021", "A bounded open-family null does not license unrestricted non-occurrence.", _minimal(horizon, lambda r: r["complete"] and not r["family_closed"] and not r["occurrence_within"] and r["occurrence_after"] and not r["universal_negative_credit"])),
        ("P2-W12", "VII-C003", "Closed bootstrap with no seed or generator rejects a claimed first extension.", _minimal(bootstrap_rejected, lambda r: True)),
        ("P2-W13", "VII-C006", "Retrospective credit is rejected even when every other neutral-provisioning coordinate is certified.", _minimal(commitment_rejected, lambda r: r["preregistered"] and r["precedes_evidence"] and r["retrospective"] and r["task_blind"] and r["outcome_independent"] and r["symmetry_certified"] and r["control_matched"] and r["prospective_credit"])),
        ("P2-W14", "VII-C005", "Self-owned partial-target totality transfer without adapter is rejected.", _minimal(totality_rejected, lambda r: r["target_partial"] and r["target_self_owned"] and not r["adapter_certified"] and r["transfer_licensed"])),
        ("P2-W15", "VII-C029", "Unpriced positive occupancy rejects native credit.", _minimal(observer_rejected, lambda r: r["occupied"] > r["charged"] and r["native_credit"])),
    ]
    return [
        {
            "witness_id": witness_id,
            "candidate_id": candidate_id,
            "shows": shows,
            "assignment": dict(assignment),
            "assignment_sha256": digest(assignment),
            "grade": "CANONICAL_BOUNDED_COUNTERMODEL_OR_CONTROL",
            "nonclaim": "Minimality is within the declared finite family and lexicographic canonicalization only.",
        }
        for witness_id, candidate_id, shows, assignment in specs
    ]


def no_go_controls() -> list[dict[str, Any]]:
    return [
        {"no_go_id": "NGVII-01", "failure_scenario": "TTW-S01", "escape_scenarios": ["TTW-S02"], "theorem_asset": "FoundationsVII.NoGo.NGVII_01_no_first_extension_without_seed_or_generator"},
        {"no_go_id": "NGVII-03", "failure_scenario": "TTW-S04", "escape_scenarios": ["TTW-S03"], "theorem_asset": "FoundationsVII.NoGo.NGVII_03_no_retrospective_self_certification"},
        {"no_go_id": "NGVII-04", "failure_scenario": "TTW-S23", "escape_scenarios": ["TTW-S08"], "theorem_asset": "FoundationsVII.NoGo.NGVII_04_no_automatic_total_lens_transfer"},
        {"no_go_id": "NGVII-05", "failure_scenario": "TTW-S22", "escape_scenarios": ["TTW-S02"], "theorem_asset": "FoundationsVII.NoGo.NGVII_05_no_unpriced_observer_native_credit"},
        {"no_go_id": "NGVII-11", "failure_scenario": "TTW-S20", "escape_scenarios": ["TTW-S21"], "theorem_asset": "FoundationsVII.NoGo.NGVII_11_no_occurrence_from_reachability_alone"},
    ]
