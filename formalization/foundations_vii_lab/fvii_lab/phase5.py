from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
from typing import Any, Callable, Mapping, Sequence

from .phase2 import EnvelopeResult

BOOLS: tuple[bool, bool] = (False, True)
SMALL: tuple[int, int, int] = (0, 1, 2)
DOMAIN_COUNTS: tuple[int, int] = (2, 3)
REFINEMENT_EFFECTS: tuple[str, ...] = (
    "PRESERVES",
    "STRENGTHENS",
    "WEAKENS",
    "DESTROYS",
)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def _rows(names: Sequence[str], domains: Sequence[Sequence[Any]]) -> list[dict[str, Any]]:
    return [dict(zip(names, values, strict=True)) for values in product(*domains)]


def _identity(row: Mapping[str, Any]) -> dict[str, Any]:
    return dict(row)


def _partition(
    family_id: str,
    description: str,
    raw_rows: list[dict[str, Any]],
    predicate: Callable[[Mapping[str, Any]], bool],
    *,
    nonclaim: str,
    canonicalizer: Callable[[Mapping[str, Any]], dict[str, Any]] = _identity,
    symmetry_rule: str = "NONE",
) -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    canonical_by_key: dict[str, dict[str, Any]] = {}
    for raw in raw_rows:
        canonical = canonicalizer(raw)
        key = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        canonical_by_key[key] = canonical
    rows = [canonical_by_key[key] for key in sorted(canonical_by_key)]
    accepted = [row for row in rows if predicate(row)]
    rejected = [row for row in rows if not predicate(row)]
    result = EnvelopeResult(
        family_id=family_id,
        description=description,
        raw_cardinality=len(raw_rows),
        canonical_cardinality=len(rows),
        accepted_cardinality=len(accepted),
        rejected_cardinality=len(rejected),
        accepted_sha256=digest(accepted),
        rejected_sha256=digest(rejected),
        nonclaim=nonclaim,
    )
    return result, accepted, rejected, symmetry_rule


def prospective_join_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "preregistered",
        "precedes",
        "retrospective",
        "lawful_admission",
        "source_aligned",
        "contact",
        "composite",
        "retention",
        "anti_product",
        "source_independent",
        "budget_settled",
        "payment_fully_credited",
        "integrated_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        exact = all(
            (
                r["preregistered"],
                r["precedes"],
                not r["retrospective"],
                r["lawful_admission"],
                r["source_aligned"],
                r["contact"],
                r["composite"],
                r["retention"],
                r["anti_product"],
                r["source_independent"],
                r["budget_settled"],
                r["payment_fully_credited"],
            )
        )
        return bool(r["integrated_credit"]) == exact

    return _partition(
        "P5-E01",
        "Prospective commitment, lawful admission, strict-join, source, and payment integration.",
        rows,
        law,
        nonclaim=(
            "The envelope checks the declared certificate conjunction; it does not "
            "collapse the component certificates into one primitive fact."
        ),
    )


def source_budget_capacity_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "source_independent",
        "budget_settled",
        "ledger_nonempty",
        "all_entries_credited",
        "observer_priced",
        "strict_join_credit",
        "capacity_credit",
        "capacity",
        "live_join_count",
        "minimum_positive_cost",
    )
    rows = _rows(names, [BOOLS] * 7 + [SMALL] * 3)

    def law(r: Mapping[str, Any]) -> bool:
        strict_exact = all(
            (
                r["source_independent"],
                r["budget_settled"],
                r["ledger_nonempty"],
                r["all_entries_credited"],
                r["observer_priced"],
            )
        )
        feasible = bool(
            r["minimum_positive_cost"] > 0
            and r["live_join_count"] * r["minimum_positive_cost"] <= r["capacity"]
        )
        return (
            bool(r["strict_join_credit"]) == strict_exact
            and bool(r["capacity_credit"]) == feasible
        )

    return _partition(
        "P5-E02",
        "Source-independent, observer-priced strict-join credit and finite live-capacity assignments.",
        rows,
        law,
        nonclaim=(
            "The finite capacity coordinate is a local declared bound, not a universal "
            "scalar currency or conservation law for interaction."
        ),
    )


def certified_noninteraction_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "no_contact",
        "exact_coverage",
        "family_closed",
        "detector_power",
        "budget_sufficient",
        "horizon_complete",
        "escape_routes_recorded",
        "certified_noninteraction",
        "strict_join_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        certificate = all(
            (
                r["no_contact"],
                r["exact_coverage"],
                r["family_closed"],
                r["detector_power"],
                r["budget_sufficient"],
                r["horizon_complete"],
                r["escape_routes_recorded"],
            )
        )
        return (
            bool(r["certified_noninteraction"]) == certificate
            and not (certificate and r["strict_join_credit"])
        )

    return _partition(
        "P5-E03",
        "Coverage-qualified certified non-interaction and strict-join exclusion.",
        rows,
        law,
        nonclaim=(
            "The exclusion is only for the exact covered channel family; recorded "
            "outside-family escape routes remain live."
        ),
    )


def residual_enablement_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "first_executed",
        "second_executed",
        "source_compatible",
        "budget_compatible",
        "residual_compatible",
        "audit_compatible",
        "old_residual_retained",
        "cross_term_created",
        "relabel_only",
        "composed_credit",
        "zero_residual_claim",
        "debt_a",
        "debt_b",
    )
    rows = _rows(names, [BOOLS] * 11 + [SMALL] * 2)

    def law(r: Mapping[str, Any]) -> bool:
        composable = all(
            (
                r["first_executed"],
                r["second_executed"],
                r["source_compatible"],
                r["budget_compatible"],
                r["residual_compatible"],
                r["audit_compatible"],
            )
        )
        debt = r["debt_a"] + r["debt_b"]
        retention_ok = not composable or r["old_residual_retained"]
        needle_ok = not (r["cross_term_created"] and not r["relabel_only"]) or (
            debt > 0 and not r["zero_residual_claim"]
        )
        zero_claim_ok = not r["zero_residual_claim"] or debt == 0
        return (
            bool(r["composed_credit"]) == composable
            and retention_ok
            and needle_ok
            and zero_claim_ok
        )

    return _partition(
        "P5-E04",
        "Residual-aware two-link enablement composition with append-only retention and cross-term debt.",
        rows,
        law,
        nonclaim=(
            "The debt coordinate is declared bookkeeping for this envelope, not a "
            "claim that all residuals are additive scalars."
        ),
    )


def refinement_descent_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "effect",
        "refinement_well_formed",
        "transmission_valid",
        "compatibility_preserved",
        "strictness_preserved",
        "source_preserved",
        "budget_preserved",
        "square_commutes",
        "preservation_credit",
        "unconditional_monotonicity_claim",
    )
    rows = _rows(names, [REFINEMENT_EFFECTS] + [BOOLS] * 9)

    def law(r: Mapping[str, Any]) -> bool:
        preserving = r["effect"] in {"PRESERVES", "STRENGTHENS"}
        exact_credit = all(
            (
                preserving,
                r["refinement_well_formed"],
                r["transmission_valid"],
                r["compatibility_preserved"],
                r["strictness_preserved"],
                r["source_preserved"],
                r["budget_preserved"],
                r["square_commutes"],
            )
        )
        destroying_ok = not (
            r["effect"] == "DESTROYS" and r["refinement_well_formed"]
        ) or (not r["compatibility_preserved"] or not r["strictness_preserved"])
        return (
            bool(r["preservation_credit"]) == exact_credit
            and not r["unconditional_monotonicity_claim"]
            and destroying_ok
        )

    return _partition(
        "P5-E05",
        "Parent-refinement effects composed with source-, budget-, and square-preserving descent fidelity.",
        rows,
        law,
        nonclaim=(
            "The accepted cases preserve descent only under explicit refinement and "
            "transmission certificates; no unconditional refinement monotonicity is asserted."
        ),
    )


def no_free_join_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "closed_family",
        "seed",
        "generator",
        "external_provision",
        "permitted",
        "positive_cost",
        "paid",
        "zero_cost_certified",
        "first_extension",
        "payment_credit",
        "join_credit",
        "free_join_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        extension = bool(
            r["permitted"]
            and (
                r["seed"]
                or r["generator"]
                or (not r["closed_family"] and r["external_provision"])
            )
        )
        payment = bool(
            (r["positive_cost"] and r["paid"])
            or (not r["positive_cost"] and r["zero_cost_certified"])
        )
        join = extension and payment
        free = bool(
            join
            and not r["seed"]
            and not r["generator"]
            and not r["external_provision"]
            and not r["paid"]
            and not r["zero_cost_certified"]
        )
        return (
            bool(r["first_extension"]) == extension
            and bool(r["payment_credit"]) == payment
            and bool(r["join_credit"]) == join
            and bool(r["free_join_credit"]) == free
            and not free
        )

    return _partition(
        "P5-E06",
        "Combined bootstrap and payment assignments for first-join credit.",
        rows,
        law,
        nonclaim=(
            "The no-free-join conclusion is relative to the declared seed, generator, "
            "external-provision, payment, and certified zero-cost channels."
        ),
    )


def holonomy_arrow_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "strict_join",
        "holonomy",
        "drive",
        "path_asymmetry",
        "reversal_fails",
        "budgeted",
        "audited",
        "arrow_credit",
        "join_only_arrow_claim",
        "holonomy_only_arrow_claim",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        arrow = all(
            (
                r["drive"],
                r["path_asymmetry"],
                r["reversal_fails"],
                r["budgeted"],
                r["audited"],
            )
        )
        join_only = bool(
            r["strict_join"] and not r["drive"] and r["join_only_arrow_claim"]
        )
        holonomy_only = bool(
            r["holonomy"] and not r["drive"] and r["holonomy_only_arrow_claim"]
        )
        return bool(r["arrow_credit"]) == arrow and not join_only and not holonomy_only

    return _partition(
        "P5-E07",
        "Strict-join, route-holonomy, and independently driven arrow assignments.",
        rows,
        law,
        nonclaim=(
            "Strictness and holonomy remain compatible with zero arrow; directionality "
            "requires the independent drive package."
        ),
    )


def negative_force_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "sound",
        "executable",
        "guard_active",
        "reachable",
        "fired",
        "occurrent",
        "complete_horizon",
        "family_closed",
        "detector_power",
        "no_occurrence_within",
        "no_occurrence_after",
        "global_negative_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        coherent = (
            (not r["executable"] or r["sound"])
            and (not r["reachable"] or (r["executable"] and r["guard_active"]))
            and (not r["fired"] or r["reachable"])
            and (not r["occurrent"] or r["fired"])
        )
        global_negative = all(
            (
                r["complete_horizon"],
                r["family_closed"],
                r["detector_power"],
                r["no_occurrence_within"],
                r["no_occurrence_after"],
            )
        )
        return coherent and bool(r["global_negative_credit"]) == global_negative

    return _partition(
        "P5-E08",
        "Operational reachability plus horizon-, closure-, and detector-qualified negative force.",
        rows,
        law,
        nonclaim=(
            "Reachability alone never licenses occurrence, and a bounded null remains "
            "bounded unless family closure, detector power, and no-later-occurrence are certified."
        ),
    )


def observer_endogeny_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "native_source",
        "carried",
        "reachable",
        "executed",
        "audited",
        "budgeted",
        "boundary_closed",
        "hidden_observer",
        "native_credit",
        "endogenous_credit",
        "joint_credit",
        "occupied",
        "charged",
    )
    rows = _rows(names, [BOOLS] * 11 + [SMALL] * 2)

    def law(r: Mapping[str, Any]) -> bool:
        native = bool(r["native_source"] and r["charged"] == r["occupied"])
        endogenous = all(
            (
                r["carried"],
                r["reachable"],
                r["executed"],
                r["audited"],
                r["budgeted"],
                r["boundary_closed"],
                not r["hidden_observer"],
            )
        )
        return (
            bool(r["native_credit"]) == native
            and bool(r["endogenous_credit"]) == endogenous
            and bool(r["joint_credit"]) == (native and endogenous)
        )

    return _partition(
        "P5-E09",
        "Observer-pricing and declared-boundary endogeny assignments.",
        rows,
        law,
        nonclaim=(
            "Endogenous credit does not mean environmentally isolated or uncaused, and "
            "equal charge/occupancy is only one local accounting condition."
        ),
    )


def _canonicalize_three_domain(row: Mapping[str, Any]) -> dict[str, Any]:
    canonical = dict(row)
    pair = sorted((bool(canonical["pair_ab_resolved"]), bool(canonical["pair_bc_resolved"])))
    canonical["pair_ab_resolved"], canonical["pair_bc_resolved"] = pair
    return canonical


def three_domain_confluence_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "same_rules",
        "same_seed_partition",
        "pair_ab_resolved",
        "pair_bc_resolved",
        "pair_ac_resolved",
        "all_pairs_checked",
        "family_closed",
        "audit_equivalent",
        "terminal_equal",
        "order_residue",
        "holonomy",
        "global_confluence_credit",
        "seed_dependence_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        confluence = all(
            (
                r["all_pairs_checked"],
                r["family_closed"],
                r["audit_equivalent"],
                r["pair_ab_resolved"],
                r["pair_bc_resolved"],
                r["pair_ac_resolved"],
            )
        )
        seed_dep = bool(
            r["same_rules"]
            and not r["same_seed_partition"]
            and not r["terminal_equal"]
        )
        holonomy_ok = not r["holonomy"] or r["order_residue"]
        return (
            bool(r["global_confluence_credit"]) == confluence
            and bool(r["seed_dependence_credit"]) == seed_dep
            and holonomy_ok
        )

    return _partition(
        "P5-E10",
        "Three-domain critical-pair, seed-partition, and interaction-order assignments.",
        rows,
        law,
        nonclaim=(
            "Pairwise finite closure is scoped to the enumerated three-domain system "
            "and does not establish general confluence."
        ),
        canonicalizer=_canonicalize_three_domain,
        symmetry_rule="QUOTIENT_BY_AB_BC_PAIR_LABEL_SWAP",
    )


def integrated_domain_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]:
    names = (
        "domain_count",
        "all_domains_admissible",
        "contact_graph_closed",
        "witnesses_complete",
        "sources_typed",
        "budgeted",
        "observer_priced",
        "residuals_accounted",
        "all_joins_certified",
        "all_negatives_scoped",
        "system_credit",
        "join_count",
        "residual_count",
    )
    rows = _rows(names, [DOMAIN_COUNTS] + [BOOLS] * 10 + [SMALL] * 2)

    def law(r: Mapping[str, Any]) -> bool:
        joins_ok = r["join_count"] == 0 or r["all_joins_certified"]
        residual_ok = r["residual_count"] == 0 or r["residuals_accounted"]
        exact = all(
            (
                r["all_domains_admissible"],
                r["contact_graph_closed"],
                r["witnesses_complete"],
                r["sources_typed"],
                r["budgeted"],
                r["observer_priced"],
                residual_ok,
                joins_ok,
                r["all_negatives_scoped"],
            )
        )
        return bool(r["system_credit"]) == exact and residual_ok

    return _partition(
        "P5-E11",
        "Integrated two- and three-domain release profiles with typed sources, budgets, observers, joins, residuals, and scoped negatives.",
        rows,
        law,
        nonclaim=(
            "This bounded system assay is not a universal normal form for arbitrary "
            "multi-theory interaction."
        ),
    )


ENVELOPES = (
    prospective_join_envelope,
    source_budget_capacity_envelope,
    certified_noninteraction_envelope,
    residual_enablement_envelope,
    refinement_descent_envelope,
    no_free_join_envelope,
    holonomy_arrow_envelope,
    negative_force_envelope,
    observer_endogeny_envelope,
    three_domain_confluence_envelope,
    integrated_domain_envelope,
)

COROLLARY_MAP: dict[str, list[str]] = {
    "P5-E01": ["FVII-COR-001", "FVII-COR-002", "FVII-COR-003"],
    "P5-E02": ["FVII-COR-004", "FVII-COR-005"],
    "P5-E03": ["FVII-COR-006", "FVII-COR-007"],
    "P5-E04": ["FVII-COR-008", "FVII-COR-009"],
    "P5-E05": ["FVII-COR-010", "FVII-COR-011", "FVII-COR-012"],
    "P5-E06": ["FVII-COR-013", "FVII-COR-014"],
    "P5-E07": ["FVII-COR-015", "FVII-COR-016"],
    "P5-E08": ["FVII-COR-017", "FVII-COR-018"],
    "P5-E09": ["FVII-COR-019", "FVII-COR-020", "FVII-COR-021"],
    "P5-E10": ["FVII-COR-010", "FVII-COR-015", "FVII-COR-017"],
    "P5-E11": ["FVII-COR-001", "FVII-COR-004", "FVII-COR-008", "FVII-COR-019"],
}

CANDIDATE_MAP: dict[str, list[str]] = {
    "P5-E01": ["VII-C002", "VII-C006", "VII-C009", "VII-C011"],
    "P5-E02": ["VII-C009", "VII-C010", "VII-C011", "VII-C029"],
    "P5-E03": ["VII-C008", "VII-C033"],
    "P5-E04": ["VII-C019", "VII-C027", "VII-C036"],
    "P5-E05": ["VII-C015", "VII-C030", "VII-C034"],
    "P5-E06": ["VII-C003", "VII-C011", "VII-C035"],
    "P5-E07": ["VII-C009", "VII-C017", "VII-C032"],
    "P5-E08": ["VII-C021", "VII-C023"],
    "P5-E09": ["VII-C013", "VII-C029"],
    "P5-E10": ["VII-C017", "VII-C018", "VII-C032"],
    "P5-E11": ["VII-C001", "VII-C008", "VII-C012", "VII-C019", "VII-C025"],
}

POSITIVE_CREDIT_KEYS: dict[str, str] = {
    "P5-E01": "integrated_credit",
    "P5-E02": "strict_join_credit",
    "P5-E03": "certified_noninteraction",
    "P5-E04": "composed_credit",
    "P5-E05": "preservation_credit",
    "P5-E06": "join_credit",
    "P5-E07": "arrow_credit",
    "P5-E08": "global_negative_credit",
    "P5-E09": "joint_credit",
    "P5-E10": "global_confluence_credit",
    "P5-E11": "system_credit",
}


def all_envelopes() -> list[
    tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]], str]
]:
    return [builder() for builder in ENVELOPES]


def _score(row: Mapping[str, Any]) -> tuple[int, str]:
    score = 0
    for value in row.values():
        if isinstance(value, bool):
            score += int(value)
        elif isinstance(value, int):
            score += value
        elif isinstance(value, str):
            score += 0 if value in {"PRESERVES"} else 1
    return score, json.dumps(dict(row), sort_keys=True, separators=(",", ":"))


def canonical_witnesses() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    index = 1
    for result, accepted, rejected, _symmetry in all_envelopes():
        positive_key = POSITIVE_CREDIT_KEYS[result.family_id]
        positive_rows = [row for row in accepted if bool(row[positive_key])]
        null_rows = [row for row in accepted if not bool(row[positive_key])]
        selections = (
            ("POSITIVE_CREDIT_MINIMAL", min(positive_rows, key=_score)),
            ("LAWFUL_NULL_MINIMAL", min(null_rows, key=_score)),
            ("INVALID_ASSIGNMENT_MINIMAL", min(rejected, key=_score)),
        )
        for role, chosen in selections:
            rows.append(
                {
                    "witness_id": f"F5-W{index:02d}",
                    "family_id": result.family_id,
                    "role": role,
                    "assignment": chosen,
                    "assignment_sha256": digest(chosen),
                    "corollary_ids": COROLLARY_MAP[result.family_id],
                    "candidate_ids": CANDIDATE_MAP[result.family_id],
                    "evidence_grade": "MINIMIZED_WITHIN_DECLARED_FINITE_FAMILY",
                }
            )
            index += 1
    return rows


def cross_family_controls() -> list[dict[str, Any]]:
    controls = [
        (
            "F5-CONTROL-01",
            "prospective_join",
            ["FVII-COR-001", "FVII-COR-002", "FVII-COR-003"],
            "Temporal precedence, lawful admission, strictness, source, and payment remain separate required certificates.",
            "Retrospective registration blocks integrated credit even if later join evidence is present.",
        ),
        (
            "F5-CONTROL-02",
            "source_budget_capacity",
            ["FVII-COR-004", "FVII-COR-005"],
            "Independent source and fully paid finite capacity jointly bound live credited joins.",
            "Payment does not substitute for source independence and source independence does not substitute for payment.",
        ),
        (
            "F5-CONTROL-03",
            "certified_noninteraction",
            ["FVII-COR-006", "FVII-COR-007"],
            "Closed exact coverage excludes contact-dependent strict join within the covered family.",
            "A point null or an open family does not establish certified non-interaction.",
        ),
        (
            "F5-CONTROL-04",
            "enablement_residual",
            ["FVII-COR-008", "FVII-COR-009"],
            "Composable enablement accumulates declared cost and debt while preserving append-only residual evidence.",
            "A valid sourced cross-term needle defeats a zero-residual reading.",
        ),
        (
            "F5-CONTROL-05",
            "refinement_descent",
            ["FVII-COR-010", "FVII-COR-011", "FVII-COR-012"],
            "Preserving refinement plus valid descent preserves explicit gates.",
            "A destroying refinement is a constructive counterexample to unconditional monotonicity.",
        ),
        (
            "F5-CONTROL-06",
            "no_free_join",
            ["FVII-COR-013", "FVII-COR-014"],
            "First-join credit requires an authorized bootstrap path and a paid or certified zero-cost channel.",
            "A join cannot manufacture its own seed and payment channel.",
        ),
        (
            "F5-CONTROL-07",
            "holonomy_arrow",
            ["FVII-COR-015", "FVII-COR-016"],
            "Holonomy may coexist with an arrow only when the drive package is independently certified.",
            "Strict join or holonomy alone carries zero directionality credit.",
        ),
        (
            "F5-CONTROL-08",
            "negative_force",
            ["FVII-COR-017", "FVII-COR-018"],
            "Closed family, complete horizon, detector power, and explicit nulls license only the declared negative scope.",
            "Reachability alone does not establish occurrence, and a bounded null does not become global automatically.",
        ),
        (
            "F5-CONTROL-09",
            "observer_endogeny",
            ["FVII-COR-019", "FVII-COR-020", "FVII-COR-021"],
            "Native/endogenous credit requires priced occupancy plus the full endogeny criterion.",
            "Positive hidden occupancy blocks native credit; genuine zero occupancy is only an accounting escape.",
        ),
        (
            "F5-CONTROL-10",
            "three_domain_order",
            ["FVII-COR-010", "FVII-COR-015", "FVII-COR-017"],
            "Three-domain order, confluence, and negative-force claims retain their own finite scopes.",
            "Pairwise closure and one commuting square do not establish unrestricted global confluence.",
        ),
        (
            "F5-CONTROL-11",
            "integrated_release",
            ["FVII-COR-001", "FVII-COR-004", "FVII-COR-008", "FVII-COR-019"],
            "Integrated system credit requires all declared source, budget, observer, residual, join, and negative-scope gates.",
            "A single system-credit flag cannot substitute for the component records.",
        ),
        (
            "F5-CONTROL-12",
            "grade_discipline",
            ["VII-C020", "VII-C023", "VII-C024", "VII-C025"],
            "Formal theorem, finite assay, bridge authorization, and normative specification grades remain separate.",
            "Executed finite coverage does not upgrade a structural schema to an unrestricted theorem.",
        ),
    ]
    return [
        {
            "control_id": control_id,
            "family": family,
            "asset_ids": asset_ids,
            "positive_control": positive,
            "failure_control": failure,
            "status": "CLOSED_SOURCE_AND_EXECUTED_PYTHON_FINITE_CONTROL",
        }
        for control_id, family, asset_ids, positive, failure in controls
    ]
