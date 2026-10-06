from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
from typing import Any, Callable, Iterable, Mapping, Sequence

from .phase2 import EnvelopeResult


BOOLS: tuple[bool, bool] = (False, True)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


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
        raw_cardinality=len(rows) if raw_cardinality is None else raw_cardinality,
        canonical_cardinality=len(rows),
        accepted_cardinality=len(accepted),
        rejected_cardinality=len(rejected),
        accepted_sha256=digest(accepted),
        rejected_sha256=digest(rejected),
        nonclaim=nonclaim,
    )
    return result, accepted, rejected


def contact_transport_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "compatible",
        "contact",
        "payload_certified",
        "destination_owned",
        "provenance_preserved",
        "transport_credit",
        "composite",
        "strict_join",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        return (
            (
                not r["transport_credit"]
                or (
                    r["contact"]
                    and r["payload_certified"]
                    and r["destination_owned"]
                    and r["provenance_preserved"]
                )
            )
            and (not r["composite"] or r["contact"])
            and (
                not r["strict_join"]
                or (r["transport_credit"] and r["composite"])
            )
        )

    return _partition(
        "P3-E01",
        "Compatibility, evidenced contact, peer transport, composite formation, and strict-join claims.",
        rows,
        law,
        nonclaim=(
            "This envelope checks the contact/transport spine only. Full strictness also "
            "requires the independent objecthood, retention, novelty, source, and budget gates."
        ),
    )


def join_status_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "contact",
        "common_refinement",
        "composite",
        "objecthood",
        "retention",
        "novelty",
        "source_gate",
        "budget_gate",
        "obstruction",
        "certified_noninteraction",
        "strict_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        strict_ok = not r["strict_credit"] or (
            r["contact"]
            and r["composite"]
            and r["objecthood"]
            and r["retention"]
            and r["novelty"]
            and r["source_gate"]
            and r["budget_gate"]
            and not r["obstruction"]
            and not r["certified_noninteraction"]
        )
        return (
            strict_ok
            and (not r["composite"] or r["contact"])
            and (not r["objecthood"] or r["composite"])
            and (not r["retention"] or r["composite"])
            and (not r["novelty"] or r["composite"])
            and (not r["certified_noninteraction"] or not r["contact"])
            and not (r["obstruction"] and r["certified_noninteraction"])
        )

    return _partition(
        "P3-E02",
        "Declared-family join evidence profiles, canonicalized under left/right parent exchange.",
        rows,
        law,
        raw_cardinality=len(rows) * 2,
        nonclaim=(
            "The terminal classifier is total only over this declared Boolean evidence family. "
            "Underlying evidence axes may overlap."
        ),
    )


def join_status(row: Mapping[str, Any]) -> str:
    """Exclusive display status for an accepted P3-E02 evidence profile."""
    if row["certified_noninteraction"]:
        return "CERTIFIED_NONINTERACTION"
    if row["obstruction"]:
        return "OBSTRUCTED"
    if row["strict_credit"]:
        return "STRICT_JOIN"
    if row["composite"]:
        return "LAWFUL_COMPOSITE"
    if row["common_refinement"]:
        return "COMMON_REFINEMENT"
    if row["contact"]:
        return "EVIDENCED_CONTACT"
    return "NO_EVIDENCED_CONTACT"


def status_partitions() -> dict[str, list[dict[str, Any]]]:
    accepted = join_status_envelope()[1]
    names = (
        "NO_EVIDENCED_CONTACT",
        "EVIDENCED_CONTACT",
        "COMMON_REFINEMENT",
        "LAWFUL_COMPOSITE",
        "STRICT_JOIN",
        "OBSTRUCTED",
        "CERTIFIED_NONINTERACTION",
    )
    return {name: [row for row in accepted if join_status(row) == name] for name in names}


def strictness_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "contact",
        "composite",
        "objecthood",
        "left_retention",
        "right_retention",
        "nonfactor_left",
        "nonfactor_right",
        "nonfactor_product",
        "source_independent",
        "budget_paid",
        "relabel_only",
        "scheduling_only",
        "coarsening_only",
        "common_refinement_only",
        "direction_certified",
        "strict_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        return not r["strict_credit"] or (
            r["contact"]
            and r["composite"]
            and r["objecthood"]
            and r["left_retention"]
            and r["right_retention"]
            and r["nonfactor_left"]
            and r["nonfactor_right"]
            and r["nonfactor_product"]
            and r["source_independent"]
            and r["budget_paid"]
            and not r["relabel_only"]
            and not r["scheduling_only"]
            and not r["coarsening_only"]
            and not r["common_refinement_only"]
        )

    return _partition(
        "P3-E03",
        "Strict-join omission attacks over independently represented certificate axes.",
        rows,
        law,
        raw_cardinality=len(rows) * 2,
        nonclaim="Directionality is intentionally not a strictness premise and remains separately certified.",
    )


def source_lineage_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "same_lineage",
        "resemblance",
        "contact",
        "source_witness",
        "behavioral_novelty",
        "causal_independence",
        "independence_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        return not r["independence_credit"] or (
            not r["same_lineage"] and r["contact"] and r["source_witness"]
        )

    return _partition(
        "P3-E04",
        "Source-lineage and independence-sensitive credit assignments.",
        rows,
        law,
        nonclaim="Source independence is neither behavioral novelty nor causal independence.",
    )


def payment_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    rows = _rows(
        (
            "amount",
            "paid",
            "refunded",
            "zero_cost_certified",
            "observer_used",
            "observer_priced",
            "credit",
        ),
        [(0, 1, 2), (0, 1, 2), (0, 1, 2), BOOLS, BOOLS, BOOLS, BOOLS],
    )

    def law(r: Mapping[str, Any]) -> bool:
        settlement_ok = r["refunded"] <= r["paid"]
        observer_ok = not r["observer_used"] or r["observer_priced"]
        payment_ok = (
            (r["amount"] == 0 and r["zero_cost_certified"])
            or (r["amount"] > 0 and r["paid"] >= r["amount"])
        )
        return settlement_ok and (not r["credit"] or (observer_ok and payment_ok))

    return _partition(
        "P3-E05",
        "Typed join payment, refund, observer occupancy, and certified-zero-cost assignments.",
        rows,
        law,
        nonclaim="The bounded amounts test accounting discipline and do not identify a universal currency.",
    )


def capacity_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    rows = _rows(
        ("capacity", "live_join_count", "minimum_positive_cost", "feasible"),
        [range(5), range(5), range(4), BOOLS],
    )

    def law(r: Mapping[str, Any]) -> bool:
        actual = (
            r["minimum_positive_cost"] > 0
            and r["live_join_count"] * r["minimum_positive_cost"] <= r["capacity"]
        )
        return r["feasible"] == actual

    return _partition(
        "P3-E06",
        "Finite live-join capacity profiles over capacities and positive unit costs up to four.",
        rows,
        law,
        nonclaim="The bound is conditional on a declared positive minimum cost per simultaneously live join.",
    )


def retention_refinement_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    ranks = ("ERASED", "PARTIAL", "FULL")
    effects = ("PRESERVES", "STRENGTHENS", "WEAKENS", "DESTROYS")
    rows = _rows(
        (
            "join_before",
            "join_after",
            "novelty_before",
            "novelty_after",
            "retention_before",
            "retention_after",
            "effect",
        ),
        [BOOLS, BOOLS, BOOLS, BOOLS, ranks, ranks, effects],
    )

    rank = {"ERASED": 0, "PARTIAL": 1, "FULL": 2}

    def law(r: Mapping[str, Any]) -> bool:
        before = (r["join_before"], r["novelty_before"], rank[r["retention_before"]])
        after = (r["join_after"], r["novelty_after"], rank[r["retention_after"]])
        if r["effect"] == "PRESERVES":
            return before == after
        if r["effect"] == "STRENGTHENS":
            return (not r["join_before"] and r["join_after"]) or (
                r["join_before"] == r["join_after"]
                and (
                    (not r["novelty_before"] and r["novelty_after"])
                    or rank[r["retention_after"]] > rank[r["retention_before"]]
                )
            )
        if r["effect"] == "WEAKENS":
            return (
                r["join_before"]
                and r["join_after"]
                and (
                    (r["novelty_before"] and not r["novelty_after"])
                    or rank[r["retention_after"]] < rank[r["retention_before"]]
                )
            )
        return r["join_before"] and not r["join_after"]

    return _partition(
        "P3-E07",
        "Parent-retention and refinement effects with preserving, strengthening, weakening, and destroying cases.",
        rows,
        law,
        nonclaim="The family exhibits all four effects and therefore supports no unconditional refinement monotonicity.",
    )


def residual_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    origins = (
        "INHERITED_LEFT",
        "INHERITED_RIGHT",
        "DISSOLVED_BY_JOIN",
        "CREATED_CROSS_TERM",
    )
    rows = _rows(
        (
            "origin",
            "active",
            "cross_term",
            "relabel_only",
            "source_accounted",
            "parent_count",
        ),
        [origins, BOOLS, BOOLS, BOOLS, BOOLS, (0, 1, 2)],
    )

    def law(r: Mapping[str, Any]) -> bool:
        if r["origin"] == "CREATED_CROSS_TERM":
            return (
                r["active"]
                and r["cross_term"]
                and not r["relabel_only"]
                and r["source_accounted"]
                and r["parent_count"] >= 2
            )
        if r["origin"] == "DISSOLVED_BY_JOIN":
            return (
                not r["active"]
                and not r["cross_term"]
                and not r["relabel_only"]
                and r["source_accounted"]
                and r["parent_count"] >= 1
            )
        return (
            not r["cross_term"]
            and not r["relabel_only"]
            and r["source_accounted"]
            and r["parent_count"] >= 1
        )

    return _partition(
        "P3-E08",
        "Inherited, dissolved, and join-created residual assignments with typed cross-term provenance.",
        rows,
        law,
        nonclaim="A lawful join may dissolve a parent residual and create a new cross-term in the same transition.",
    )


def noninteraction_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "contact",
        "family_closed",
        "detector_power",
        "budget_sufficient",
        "horizon_complete",
        "all_examined",
        "outside_channel",
        "certificate_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        actual = (
            not r["contact"]
            and r["family_closed"]
            and r["detector_power"]
            and r["budget_sufficient"]
            and r["horizon_complete"]
            and r["all_examined"]
            and not r["outside_channel"]
        )
        return r["certificate_credit"] == actual

    return _partition(
        "P3-E09",
        "Coverage-qualified non-interaction profiles with an explicit outside-family escape marker.",
        rows,
        law,
        nonclaim="Certification excludes contact only inside the exact closed family, detector, budget, and horizon.",
    )


def categorical_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "strict_join",
        "category_declared",
        "morphisms_declared",
        "universal_checked",
        "parents_preserved",
        "anti_product",
        "product_universal",
        "pullback_universal",
        "pushout_universal",
        "categorical_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        any_universal = (
            r["product_universal"]
            or r["pullback_universal"]
            or r["pushout_universal"]
        )
        universal_well_typed = not any_universal or (
            r["category_declared"]
            and r["morphisms_declared"]
            and r["universal_checked"]
            and r["parents_preserved"]
        )
        credit_ok = not r["categorical_credit"] or (
            r["strict_join"]
            and any_universal
            and r["category_declared"]
            and r["morphisms_declared"]
            and r["universal_checked"]
            and r["parents_preserved"]
            and r["anti_product"]
        )
        return universal_well_typed and credit_ok

    return _partition(
        "P3-E10",
        "Conditional product, pullback, and pushout representations of strict join.",
        rows,
        law,
        nonclaim="Strict join need not be any listed universal construction; categorical credit is special-case only.",
    )


def measure_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    kinds = (
        "CONTACTS",
        "LIVE_JOINS",
        "PAID_COST",
        "ACTIVE_RESIDUALS",
        "RETAINED_PARENTS",
    )
    rows = _rows(
        (
            "measure_kind",
            "before",
            "after",
            "observer_included",
            "instrument_included",
            "residual_included",
            "exact_checked",
            "lawful",
            "conservation_credit",
        ),
        [kinds, (0, 1, 2), (0, 1, 2), BOOLS, BOOLS, BOOLS, BOOLS, BOOLS, BOOLS],
    )

    def law(r: Mapping[str, Any]) -> bool:
        complete = (
            r["observer_included"]
            and r["instrument_included"]
            and r["residual_included"]
            and r["exact_checked"]
        )
        lawful_ok = not r["lawful"] or complete
        conservation_ok = not r["conservation_credit"] or (
            r["lawful"] and complete and r["before"] == r["after"]
        )
        return lawful_ok and conservation_ok

    return _partition(
        "P3-E11",
        "Candidate contact/join quantities over bounded values with exact scoped conservation credit.",
        rows,
        law,
        nonclaim="The family supplies nonconservation controls for every listed quantity and names no universal scalar degree.",
    )


def all_envelopes() -> list[tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]]:
    return [
        contact_transport_envelope(),
        join_status_envelope(),
        strictness_envelope(),
        source_lineage_envelope(),
        payment_envelope(),
        capacity_envelope(),
        retention_refinement_envelope(),
        residual_envelope(),
        noninteraction_envelope(),
        categorical_envelope(),
        measure_envelope(),
    ]


def _minimal(
    rows: Iterable[Mapping[str, Any]],
    required: Callable[[Mapping[str, Any]], bool],
) -> dict[str, Any]:
    matches = [dict(row) for row in rows if required(row)]
    if not matches:
        raise AssertionError("no witness in declared Phase-3 finite family")

    def weight(row: Mapping[str, Any]) -> tuple[int, bytes]:
        count = sum(
            1
            for value in row.values()
            if value is True or (isinstance(value, int) and not isinstance(value, bool) and value > 0)
        )
        return count, canonical_bytes(row)

    return min(matches, key=weight)


def canonical_witnesses() -> list[dict[str, Any]]:
    contact_ok, contact_bad = contact_transport_envelope()[1:]
    status_ok, status_bad = join_status_envelope()[1:]
    strict_ok, strict_bad = strictness_envelope()[1:]
    source_ok, source_bad = source_lineage_envelope()[1:]
    payment_ok, payment_bad = payment_envelope()[1:]
    capacity_ok, _capacity_bad = capacity_envelope()[1:]
    refine_ok, _refine_bad = retention_refinement_envelope()[1:]
    residual_ok, residual_bad = residual_envelope()[1:]
    nonint_ok, _nonint_bad = noninteraction_envelope()[1:]
    categorical_ok, _categorical_bad = categorical_envelope()[1:]
    measure_ok, measure_bad = measure_envelope()[1:]

    specs: list[tuple[str, str, str, Mapping[str, Any]]] = [
        ("P3-W01", "VII-C016", "Compatibility without evidenced contact.", _minimal(contact_ok, lambda r: r["compatible"] and not r["contact"])),
        ("P3-W02", "VII-C016", "Certified peer transport without composite or join.", _minimal(contact_ok, lambda r: r["transport_credit"] and not r["composite"])),
        ("P3-W03", "VII-C007", "A transport-credit omission attack is rejected.", _minimal(contact_bad, lambda r: r["transport_credit"] and not r["destination_owned"])),
        ("P3-W04", "VII-C008", "Evidenced contact without a composite.", _minimal(status_ok, lambda r: r["contact"] and not r["composite"])),
        ("P3-W05", "VII-C008", "Common refinement without strict join.", _minimal(status_ok, lambda r: r["common_refinement"] and not r["strict_credit"])),
        ("P3-W06", "VII-C009", "Complete strict evidence with directionality absent.", _minimal(strict_ok, lambda r: r["strict_credit"] and not r["direction_certified"])),
        ("P3-W07", "VII-C009", "Relabel-only strictness credit is rejected.", _minimal(strict_bad, lambda r: r["strict_credit"] and r["relabel_only"])),
        ("P3-W08", "VII-C009", "Scheduling-only strictness credit is rejected.", _minimal(strict_bad, lambda r: r["strict_credit"] and r["scheduling_only"])),
        ("P3-W09", "VII-C009", "Mere common-refinement strictness credit is rejected.", _minimal(strict_bad, lambda r: r["strict_credit"] and r["common_refinement_only"])),
        ("P3-W10", "VII-C010", "Same-lineage independence-sensitive credit is rejected.", _minimal(source_bad, lambda r: r["same_lineage"] and r["independence_credit"])),
        ("P3-W11", "VII-C010", "Source independence need not be behavioral novelty or causal independence.", _minimal(source_ok, lambda r: r["independence_credit"] and not r["behavioral_novelty"] and not r["causal_independence"])),
        ("P3-W12", "VII-C011", "Positive unpaid join credit is rejected.", _minimal(payment_bad, lambda r: r["amount"] > 0 and r["paid"] == 0 and r["credit"])),
        ("P3-W13", "VII-C035", "A certified zero-cost channel is a positive escape.", _minimal(payment_ok, lambda r: r["amount"] == 0 and r["zero_cost_certified"] and r["credit"])),
        ("P3-W14", "VII-C011", "Unpriced observer use invalidates join credit.", _minimal(payment_bad, lambda r: r["observer_used"] and not r["observer_priced"] and r["credit"])),
        ("P3-W15", "VII-C011", "A feasible positive-cost live-join capacity profile.", _minimal(capacity_ok, lambda r: r["feasible"] and r["live_join_count"] > 0)),
        ("P3-W16", "VII-C030", "A refinement preserves join evidence.", _minimal(refine_ok, lambda r: r["effect"] == "PRESERVES" and r["join_before"])),
        ("P3-W17", "VII-C030", "A refinement strengthens into a join.", _minimal(refine_ok, lambda r: r["effect"] == "STRENGTHENS" and not r["join_before"] and r["join_after"])),
        ("P3-W18", "VII-C030", "A refinement weakens novelty while retaining a join.", _minimal(refine_ok, lambda r: r["effect"] == "WEAKENS" and r["novelty_before"] and not r["novelty_after"])),
        ("P3-W19", "VII-C030", "A refinement destroys join evidence.", _minimal(refine_ok, lambda r: r["effect"] == "DESTROYS")),
        ("P3-W20", "VII-C036", "A lawful join-created cross-term needle.", _minimal(residual_ok, lambda r: r["origin"] == "CREATED_CROSS_TERM")),
        ("P3-W21", "VII-C036", "A relabel-only claimed cross-term is rejected.", _minimal(residual_bad, lambda r: r["origin"] == "CREATED_CROSS_TERM" and r["relabel_only"])),
        ("P3-W22", "VII-C033", "No contact under open coverage is not certified non-interaction.", _minimal(nonint_ok, lambda r: not r["contact"] and not r["family_closed"] and not r["certificate_credit"])),
        ("P3-W23", "VII-C033", "Exact closed coverage yields scoped non-interaction credit.", _minimal(nonint_ok, lambda r: r["certificate_credit"])),
        ("P3-W24", "VII-C033", "An outside-family channel is an explicit escape.", _minimal(nonint_ok, lambda r: r["outside_channel"] and not r["certificate_credit"])),
        ("P3-W25", "VII-C026", "A checked product without anti-product evidence lacks strict categorical credit.", _minimal(categorical_ok, lambda r: r["product_universal"] and not r["anti_product"] and not r["categorical_credit"])),
        ("P3-W26", "VII-C026", "Strict join need not reduce to product, pullback, or pushout.", _minimal(categorical_ok, lambda r: r["strict_join"] and not r["product_universal"] and not r["pullback_universal"] and not r["pushout_universal"])),
        ("P3-W27", "VII-C031", "A proposed contact quantity has a lawful nonconservation control.", _minimal(measure_ok, lambda r: r["lawful"] and r["before"] != r["after"] and not r["conservation_credit"])),
    ]
    # Retain an explicit false-positive measure witness in the rejected partition
    # through the generated partitions; it is not one of the 27 canonical science witnesses.
    assert any(r["conservation_credit"] and r["before"] != r["after"] for r in measure_bad)
    assert any(r["strict_credit"] and not r["source_gate"] for r in status_bad)

    return [
        {
            "witness_id": witness_id,
            "candidate_id": candidate_id,
            "shows": shows,
            "assignment": dict(assignment),
            "assignment_sha256": digest(assignment),
            "grade": "CANONICAL_BOUNDED_COUNTERMODEL_OR_CONTROL",
            "nonclaim": "Minimality is only within the declared finite family and deterministic ordering.",
        }
        for witness_id, candidate_id, shows, assignment in specs
    ]


def no_go_controls() -> list[dict[str, Any]]:
    return [
        {
            "no_go_id": "NGVII-02",
            "failure_scenarios": ["TTW-S05", "TTW-S15"],
            "escape_scenarios": ["TTW-S08"],
            "theorem_asset": "FoundationsVII.NoGo.NGVII_02_no_resemblance_only_independence_join",
        },
        {
            "no_go_id": "NGVII-06",
            "failure_scenarios": ["TTW-S06"],
            "escape_scenarios": ["TTW-S08"],
            "theorem_asset": "FoundationsVII.NoGo.NGVII_06_no_join_from_contact_alone",
        },
        {
            "no_go_id": "NGVII-07",
            "failure_scenarios": ["TTW-S07", "TTW-S14", "TTW-S15"],
            "escape_scenarios": ["TTW-S08"],
            "theorem_asset": "FoundationsVII.NoGo.NGVII_07_no_product_common_refinement_strictness_credit",
        },
        {
            "no_go_id": "NGVII-08",
            "failure_scenarios": ["TTW-S05", "TTW-S11"],
            "escape_scenarios": ["TTW-S08"],
            "theorem_asset": "FoundationsVII.NoGo.NGVII_08_no_one_lineage_source_independence_credit",
        },
        {
            "no_go_id": "NGVII-09",
            "failure_scenarios": ["TTW-S10"],
            "escape_scenarios": ["TTW-S08"],
            "theorem_asset": "FoundationsVII.NoGo.NGVII_09_no_positive_cost_join_credit_without_payment",
        },
    ]


# Frozen Phase-3 fixture slice.  CM-21 points to TTW-S22, which is evaluated
# on demand as a source control but is not counted among the twelve primary
# Phase-3 scenario assignments.
PRIMARY_SCENARIOS: tuple[str, ...] = tuple(
    [f"TTW-S{i:02d}" for i in range(5, 16)] + ["TTW-S24"]
)
PRIMARY_COUNTERMODELS: tuple[str, ...] = (
    "CM-01",
    "CM-02",
    "CM-03",
    "CM-04",
    "CM-05",
    "CM-13",
    "CM-14",
    "CM-15",
    "CM-16",
    "CM-21",
    "CM-22",
    "CM-25",
    "CM-26",
    "CM-27",
)


def _evaluate_scenario_row(row: Mapping[str, Any]) -> dict[str, Any]:
    # Import here to keep the finite-envelope module independent from the
    # general reference evaluator at import time.
    from .evaluator import evaluate

    flags = dict(row.get("flags", {}))
    observed_status, facts = evaluate(flags)
    derived = facts.as_mapping()
    declared_assertions = dict(row.get("assertions", {}))
    assertion_results = {
        key: derived.get(key) == expected
        for key, expected in sorted(declared_assertions.items())
    }
    core: dict[str, Any] = {
        "fixture_id": str(row["scenario_id"]),
        "expected_status": str(row["expected_status"]),
        "observed_status": observed_status,
        "status_pass": observed_status == row["expected_status"],
        "assertion_results": assertion_results,
        "all_pass": observed_status == row["expected_status"]
        and all(assertion_results.values()),
        "derived": derived,
        "canonical_input_sha256": digest(row),
    }
    core["canonical_result_sha256"] = digest(core)
    return core


def evaluate_primary_scenarios(
    scenarios: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {str(row["scenario_id"]): row for row in scenarios}
    missing = sorted(set(PRIMARY_SCENARIOS) - set(by_id))
    if missing:
        raise AssertionError(f"missing Phase-3 scenarios: {missing}")
    return [_evaluate_scenario_row(by_id[scenario_id]) for scenario_id in PRIMARY_SCENARIOS]


def evaluate_primary_countermodels(
    countermodels: Sequence[Mapping[str, Any]],
    scenario_results: Sequence[Mapping[str, Any]],
    scenarios: Sequence[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_countermodel = {
        str(row["countermodel_id"]): row for row in countermodels
    }
    missing = sorted(set(PRIMARY_COUNTERMODELS) - set(by_countermodel))
    if missing:
        raise AssertionError(f"missing Phase-3 countermodels: {missing}")

    observed_by = {
        str(row["fixture_id"]): str(row["observed_status"])
        for row in scenario_results
    }
    scenario_rows = (
        {str(row["scenario_id"]): row for row in scenarios}
        if scenarios is not None
        else {}
    )

    results: list[dict[str, Any]] = []
    for countermodel_id in PRIMARY_COUNTERMODELS:
        row = by_countermodel[countermodel_id]
        scenario_id = str(row["scenario_id"])
        if scenario_id not in observed_by:
            # CM-21 is intentionally a source control outside the twelve primary
            # scenarios.  Evaluate it directly when the full scenario corpus is
            # supplied by the builder.
            if scenario_id not in scenario_rows:
                raise AssertionError(
                    f"countermodel {countermodel_id} needs unavailable scenario {scenario_id}"
                )
            source_result = _evaluate_scenario_row(scenario_rows[scenario_id])
            observed_by[scenario_id] = str(source_result["observed_status"])
        expected_status = str(
            scenario_rows.get(scenario_id, {}).get(
                "expected_status", observed_by[scenario_id]
            )
        )
        result: dict[str, Any] = {
            "fixture_id": countermodel_id,
            "scenario_id": scenario_id,
            "expected_status": expected_status,
            "observed_status": observed_by[scenario_id],
            "status_pass": observed_by[scenario_id] == expected_status,
            "scenario_link_pass": True,
        }
        result["all_pass"] = bool(result["status_pass"] and result["scenario_link_pass"])
        result["canonical_result_sha256"] = digest(result)
        results.append(result)
    return results
