from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
from typing import Any, Callable, Iterable, Mapping, Sequence

from .phase2 import EnvelopeResult

BOOLS: tuple[bool, bool] = (False, True)
SMALL: tuple[int, int, int] = (0, 1, 2)


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
        raw_cardinality=raw_cardinality if raw_cardinality is not None else len(rows),
        canonical_cardinality=len(rows),
        accepted_cardinality=len(accepted),
        rejected_cardinality=len(rejected),
        accepted_sha256=digest(accepted),
        rejected_sha256=digest(rejected),
        nonclaim=nonclaim,
    )
    return result, accepted, rejected


def attribution_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    sources = (
        "THEORIST", "CARRIER", "PEER", "OBSERVER", "ENVIRONMENT",
        "ENDOGENOUS_SYSTEM", "MIXED",
    )
    names = (
        "source_kind", "executed", "audited", "budgeted", "source_typed",
        "bridge_refined", "root_preserved", "hidden_executor", "attribution_credit",
    )
    rows = _rows(names, [sources] + [BOOLS] * 8)

    def law(r: Mapping[str, Any]) -> bool:
        credit_ok = not r["attribution_credit"] or (
            r["executed"] and r["audited"] and r["budgeted"]
            and r["source_typed"] and not r["hidden_executor"]
        )
        refinement_ok = not (
            r["bridge_refined"] and r["attribution_credit"]
        ) or r["root_preserved"]
        return credit_ok and refinement_ok

    return _partition(
        "P4-E01",
        "Source-typed enablement attribution profiles with honest bridge-refinement stability.",
        rows,
        law,
        nonclaim="Attribution credit records provenance; it does not establish descent, sufficiency, causation, or endogeny.",
    )


def endogenous_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "carried", "reachable", "executed", "audited", "budgeted",
        "boundary_closed", "theorist_hidden", "observer_hidden",
        "environmental_input", "environment_accounted", "endogenous_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def exact(r: Mapping[str, Any]) -> bool:
        return bool(
            r["carried"] and r["reachable"] and r["executed"]
            and r["audited"] and r["budgeted"] and r["boundary_closed"]
            and not r["theorist_hidden"] and not r["observer_hidden"]
            and (not r["environmental_input"] or r["environment_accounted"])
        )

    return _partition(
        "P4-E02",
        "Exact carried/reachable/executed/audited/budgeted endogenous-credit profiles.",
        rows,
        lambda r: bool(r["endogenous_credit"]) == exact(r),
        nonclaim="Endogenous means internally carried and executed within the declared boundary, not uncaused or environmentally isolated.",
    )


def birth_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    agencies = ("SYSTEM_PERFORMS", "SYSTEM_UNDERGOES", "PEER", "ENVIRONMENT", "MIXED")
    outcomes = ("RELATION_ONLY", "NEW_LAYER", "NEW_PARTICIPANT", "REFINEMENT_ONLY")
    names = (
        "agency", "outcome", "contact_present", "survives_closure",
        "objecthood", "performed_by_system", "participant_credit", "birth_credit",
    )
    rows = _rows(names, [agencies, outcomes] + [BOOLS] * 6)

    def law(r: Mapping[str, Any]) -> bool:
        agency_ok = bool(r["performed_by_system"]) == (r["agency"] == "SYSTEM_PERFORMS")
        participant_exact = bool(
            r["outcome"] == "NEW_PARTICIPANT"
            and r["contact_present"] and r["survives_closure"] and r["objecthood"]
        )
        birth_exact = bool(
            r["outcome"] in {"NEW_LAYER", "NEW_PARTICIPANT"}
            and r["survives_closure"] and r["objecthood"]
        )
        relation_ok = r["outcome"] != "RELATION_ONLY" or not r["participant_credit"]
        return (
            agency_ok
            and bool(r["participant_credit"]) == participant_exact
            and bool(r["birth_credit"]) == birth_exact
            and relation_ok
        )

    return _partition(
        "P4-E03",
        "Closure-agency and relation/layer/participant-birth profiles with objecthood gates.",
        rows,
        law,
        nonclaim="Contact may remain relation-only; participant creation receives credit only after objecthood and closure survival are witnessed.",
    )


def transmission_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    directions = ("UPWARD", "DOWNWARD", "PEER")
    names = (
        "direction", "payload_present", "source_typed", "budgeted",
        "loss_recorded", "ambiguity_recorded", "lower_fact_before",
        "lower_fact_after", "external_insertion", "fidelity_credit",
        "causal_certificate", "causal_credit",
    )
    rows = _rows(names, [directions] + [BOOLS] * 11)

    def law(r: Mapping[str, Any]) -> bool:
        fidelity_ok = not r["fidelity_credit"] or (
            r["payload_present"] and r["source_typed"] and r["budgeted"]
            and r["loss_recorded"] and r["ambiguity_recorded"]
        )
        downward_ok = not (
            r["direction"] == "DOWNWARD" and r["fidelity_credit"]
            and r["lower_fact_after"] and not r["external_insertion"]
        ) or r["lower_fact_before"]
        causal_ok = not r["causal_credit"] or (
            r["fidelity_credit"] and r["causal_certificate"]
        )
        return fidelity_ok and downward_ok and causal_ok

    return _partition(
        "P4-E04",
        "Upward/downward/peer transmission profiles with payload, loss, ambiguity, source, budget, and causal-certificate gates.",
        rows,
        law,
        nonclaim="A faithful downward selection is not automatically a top-down causal channel and cannot create an absent lower-carrier fact without an explicit insertion source.",
    )


def separation_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "enabled", "load_bearing", "descent_factorization", "necessary",
        "sufficient", "alternative_determinants", "causal_channel",
        "enablement_without_descent_credit", "necessary_insufficient_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        separation = bool(r["enabled"] and r["load_bearing"] and not r["descent_factorization"])
        necessary_insufficient = bool(
            r["enabled"] and r["necessary"] and not r["sufficient"]
            and r["alternative_determinants"]
        )
        return (
            bool(r["enablement_without_descent_credit"]) == separation
            and bool(r["necessary_insufficient_credit"]) == necessary_insufficient
        )

    return _partition(
        "P4-E05",
        "Constructive enablement/descent and necessary/sufficient separation profiles.",
        rows,
        law,
        nonclaim="The separations do not deny that some enablement also descends or participates in a separately certified causal channel.",
    )


def composition_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "first_executed", "second_executed", "source_compatible",
        "budget_compatible", "residual_compatible", "audit_compatible",
        "causal_chain_certified", "composed_credit", "transitive_causal_credit",
        "cost_a", "cost_b", "debt_a", "debt_b",
    )
    rows = _rows(names, [BOOLS] * 9 + [SMALL] * 4)

    def law(r: Mapping[str, Any]) -> bool:
        composable = bool(
            r["first_executed"] and r["second_executed"]
            and r["source_compatible"] and r["budget_compatible"]
            and r["residual_compatible"] and r["audit_compatible"]
        )
        causal_ok = not r["transitive_causal_credit"] or (
            composable and r["causal_chain_certified"]
        )
        return bool(r["composed_credit"]) == composable and causal_ok

    return _partition(
        "P4-E06",
        "Two-link enablement composition with source/budget/residual/audit compatibility and accumulated cost/debt coordinates.",
        rows,
        law,
        nonclaim="Composed enablement does not imply transitive causation without a separate causal-chain certificate.",
    )


def confluence_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "both_legal", "joinable", "audit_equivalent", "terminal_equal",
        "predictive_equivalent", "confluence_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        exact = bool(not r["both_legal"] or (r["joinable"] and r["audit_equivalent"]))
        return bool(r["confluence_credit"]) == exact

    return _partition(
        "P4-E07",
        "Finite critical-pair profiles distinguishing joinability, audit equivalence, terminal equality, and predictive equivalence.",
        rows,
        law,
        nonclaim="A single commuting pair or terminal equality does not establish global confluence outside the declared finite closed system.",
    )


def seed_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "same_rules", "same_seed_partition", "terminal_equal",
        "predictive_equivalent", "presentation_only", "seed_dependence_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        deterministic_same_seed = not (
            r["same_rules"] and r["same_seed_partition"]
        ) or r["terminal_equal"]
        presentation_ok = not r["presentation_only"] or r["predictive_equivalent"]
        seed_dep = bool(
            r["same_rules"] and not r["same_seed_partition"]
            and not r["terminal_equal"]
        )
        return (
            deterministic_same_seed and presentation_ok
            and bool(r["seed_dependence_credit"]) == seed_dep
        )

    return _partition(
        "P4-E08",
        "Seed-partition dependence profiles separated from presentation-only route differences.",
        rows,
        law,
        nonclaim="Seed dependence is established only within the declared deterministic finite rule family and does not imply universal nonconfluence.",
    )


def holonomy_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "legal_a", "legal_b", "same_target", "same_members", "same_order",
        "same_bracketing", "same_predictive", "audit_equivalent",
        "route_residue", "holonomy_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        changed_route = not r["same_order"] or not r["same_bracketing"]
        residue = bool(
            r["legal_a"] and r["legal_b"] and r["same_target"]
            and r["same_members"] and changed_route
            and (not r["same_predictive"] or not r["audit_equivalent"])
        )
        holonomy = bool(residue and not r["same_predictive"])
        return bool(r["route_residue"]) == residue and bool(r["holonomy_credit"]) == holonomy

    return _partition(
        "P4-E09",
        "Typed order/bracketing comparison profiles defining route residue and predictive holonomy on one target.",
        rows,
        law,
        nonclaim="Nonzero route residue or holonomy is a P3-style route effect and carries no directionality credit by itself.",
    )


def arrow_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "holonomy", "drive", "path_asymmetry", "reversal_fails",
        "budgeted", "audited", "arrow_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        exact = bool(
            r["drive"] and r["path_asymmetry"] and r["reversal_fails"]
            and r["budgeted"] and r["audited"]
        )
        return bool(r["arrow_credit"]) == exact

    return _partition(
        "P4-E10",
        "Holonomy/drive/path-asymmetry/reversal profiles with an independent arrow certificate.",
        rows,
        law,
        nonclaim="The finite profile establishes no arrow from holonomy alone; arrow credit is tied to an independent drive/asymmetry/reversal certificate.",
    )


def cross_time_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    witnesses = ("SYNC", "PARTIAL_ORDER", "NONE")
    names = (
        "witness_kind", "common_order", "order_comparable",
        "payload_crossed", "assumed_simultaneity", "admissible_reparameterization",
        "contact_credit", "invariance_credit",
    )
    rows = _rows(names, [witnesses] + [BOOLS] * 7)

    def law(r: Mapping[str, Any]) -> bool:
        witnessed = bool(
            (r["witness_kind"] == "SYNC" and r["common_order"])
            or (r["witness_kind"] == "PARTIAL_ORDER" and r["order_comparable"])
        )
        contact = bool(witnessed and r["payload_crossed"] and not r["assumed_simultaneity"])
        invariant = bool(contact and r["admissible_reparameterization"])
        return bool(r["contact_credit"]) == contact and bool(r["invariance_credit"]) == invariant

    return _partition(
        "P4-E11",
        "Cross-time contact via synchronization or partial-order witnesses with admissible reparameterization controls.",
        rows,
        law,
        nonclaim="No universal simultaneity or common physical clock is assumed for incommensurable internal times.",
    )


def algebra_envelope() -> tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]:
    names = (
        "generators_declared", "equivalence_declared", "domains_declared",
        "nonredundancy_proved", "semantics_declared", "laws_proved",
        "full_algebra_credit", "resource_fragment_credit",
    )
    rows = _rows(names, [BOOLS] * len(names))

    def law(r: Mapping[str, Any]) -> bool:
        full = bool(
            r["generators_declared"] and r["equivalence_declared"]
            and r["domains_declared"] and r["nonredundancy_proved"]
            and r["semantics_declared"] and r["laws_proved"]
        )
        fragment = bool(r["domains_declared"] and r["laws_proved"])
        return (
            bool(r["full_algebra_credit"]) == full
            and (not r["resource_fragment_credit"] or fragment)
        )

    return _partition(
        "P4-E12",
        "Primitive-operation algebra readiness profiles plus a separately scoped resource-delta fragment.",
        rows,
        law,
        nonclaim="Failure of the full readiness gate defers the generators-and-relations program; it does not preclude small proved algebraic fragments.",
    )


def all_envelopes() -> list[tuple[EnvelopeResult, list[dict[str, Any]], list[dict[str, Any]]]]:
    return [
        attribution_envelope(),
        endogenous_envelope(),
        birth_envelope(),
        transmission_envelope(),
        separation_envelope(),
        composition_envelope(),
        confluence_envelope(),
        seed_envelope(),
        holonomy_envelope(),
        arrow_envelope(),
        cross_time_envelope(),
        algebra_envelope(),
    ]


def _minimal(rows: Iterable[Mapping[str, Any]], required: Callable[[Mapping[str, Any]], bool]) -> dict[str, Any]:
    matches = [dict(row) for row in rows if required(row)]
    if not matches:
        raise AssertionError("no witness in declared Phase-4 finite family")

    def weight(row: Mapping[str, Any]) -> tuple[int, bytes]:
        count = sum(
            1 for value in row.values()
            if value is True or (isinstance(value, int) and not isinstance(value, bool) and value > 0)
        )
        return count, canonical_bytes(row)

    return min(matches, key=weight)


def canonical_witnesses() -> list[dict[str, Any]]:
    a_ok, a_bad = attribution_envelope()[1:]
    e_ok, e_bad = endogenous_envelope()[1:]
    b_ok, b_bad = birth_envelope()[1:]
    t_ok, t_bad = transmission_envelope()[1:]
    s_ok, _s_bad = separation_envelope()[1:]
    c_ok, c_bad = composition_envelope()[1:]
    f_ok, _f_bad = confluence_envelope()[1:]
    seed_ok, _seed_bad = seed_envelope()[1:]
    h_ok, _h_bad = holonomy_envelope()[1:]
    ar_ok, _ar_bad = arrow_envelope()[1:]
    x_ok, _x_bad = cross_time_envelope()[1:]
    alg_ok, _alg_bad = algebra_envelope()[1:]

    specs: list[tuple[str, str, str, Mapping[str, Any]]] = [
        ("P4-W01", "VII-C012", "A fully recorded theorist-attributed enablement.", _minimal(a_ok, lambda r: r["source_kind"] == "THEORIST" and r["attribution_credit"])),
        ("P4-W02", "VII-C012", "A mixed-provenance enablement with typed attribution.", _minimal(a_ok, lambda r: r["source_kind"] == "MIXED" and r["attribution_credit"])),
        ("P4-W03", "VII-C012", "Honest bridge refinement preserves the source root.", _minimal(a_ok, lambda r: r["bridge_refined"] and r["root_preserved"] and r["attribution_credit"])),
        ("P4-W04", "VII-C012", "Hidden execution invalidates attribution credit.", _minimal(a_bad, lambda r: r["hidden_executor"] and r["attribution_credit"])),
        ("P4-W05", "VII-C013", "The exact endogenous criterion has a positive witness.", _minimal(e_ok, lambda r: r["endogenous_credit"])),
        ("P4-W06", "VII-C013", "Hidden theorist execution defeats endogenous credit.", _minimal(e_bad, lambda r: r["theorist_hidden"] and r["endogenous_credit"])),
        ("P4-W07", "VII-C013", "Hidden observer execution defeats endogenous credit.", _minimal(e_bad, lambda r: r["observer_hidden"] and r["endogenous_credit"])),
        ("P4-W08", "VII-C013", "Accounted environmental input is compatible with endogenous execution.", _minimal(e_ok, lambda r: r["environmental_input"] and r["environment_accounted"] and r["endogenous_credit"])),
        ("P4-W09", "VII-C014", "System-performed closure creates an objecthood-certified layer.", _minimal(b_ok, lambda r: r["agency"] == "SYSTEM_PERFORMS" and r["outcome"] == "NEW_LAYER" and r["birth_credit"])),
        ("P4-W10", "VII-C014", "A system may undergo externally performed closure.", _minimal(b_ok, lambda r: r["agency"] == "SYSTEM_UNDERGOES" and r["outcome"] == "NEW_LAYER" and r["birth_credit"])),
        ("P4-W11", "VII-C014", "Contact may remain relation-only with no participant credit.", _minimal(b_ok, lambda r: r["outcome"] == "RELATION_ONLY" and r["contact_present"] and not r["participant_credit"])),
        ("P4-W12", "VII-C014", "Participant credit without objecthood is rejected.", _minimal(b_bad, lambda r: r["outcome"] == "NEW_PARTICIPANT" and r["participant_credit"] and not r["objecthood"])),
        ("P4-W13", "VII-C015", "A faithful upward transmission profile.", _minimal(t_ok, lambda r: r["direction"] == "UPWARD" and r["fidelity_credit"])),
        ("P4-W14", "VII-C015", "Pure downward selection preserves lower-fact provenance.", _minimal(t_ok, lambda r: r["direction"] == "DOWNWARD" and r["fidelity_credit"] and r["lower_fact_after"] and r["lower_fact_before"] and not r["external_insertion"])),
        ("P4-W15", "VII-C015", "External insertion is the explicit escape for a new lower fact.", _minimal(t_ok, lambda r: r["direction"] == "DOWNWARD" and r["fidelity_credit"] and r["lower_fact_after"] and not r["lower_fact_before"] and r["external_insertion"])),
        ("P4-W16", "VII-C015", "A faithful peer transmission profile.", _minimal(t_ok, lambda r: r["direction"] == "PEER" and r["fidelity_credit"])),
        ("P4-W17", "VII-C015", "Faithful structural selection need not receive causal credit.", _minimal(t_ok, lambda r: r["direction"] == "DOWNWARD" and r["fidelity_credit"] and not r["causal_credit"])),
        ("P4-W18", "VII-C034", "Enablement can be load-bearing without descent factorization.", _minimal(s_ok, lambda r: r["enablement_without_descent_credit"])),
        ("P4-W19", "VII-C034", "Enablement can be necessary but insufficient.", _minimal(s_ok, lambda r: r["necessary_insufficient_credit"])),
        ("P4-W20", "VII-C027", "A source/budget/residual/audit-compatible chain composes.", _minimal(c_ok, lambda r: r["composed_credit"] and r["debt_a"] + r["debt_b"] > 0)),
        ("P4-W21", "VII-C027", "Composition without a causal-chain certificate carries no transitive-causation credit.", _minimal(c_ok, lambda r: r["composed_credit"] and not r["causal_chain_certified"] and not r["transitive_causal_credit"])),
        ("P4-W22", "VII-C018", "A joinable audit-equivalent critical pair receives confluence credit.", _minimal(f_ok, lambda r: r["both_legal"] and r["joinable"] and r["audit_equivalent"] and r["confluence_credit"])),
        ("P4-W23", "VII-C018", "A legal nonjoinable critical pair witnesses nonconfluence.", _minimal(f_ok, lambda r: r["both_legal"] and not r["joinable"] and not r["confluence_credit"])),
        ("P4-W24", "VII-C018", "Different seed partitions can yield different terminal packages under the same rules.", _minimal(seed_ok, lambda r: r["seed_dependence_credit"])),
        ("P4-W25", "VII-C018", "Presentation-only differences remain predictively equivalent.", _minimal(seed_ok, lambda r: r["presentation_only"] and r["predictive_equivalent"] and not r["seed_dependence_credit"])),
        ("P4-W26", "VII-C017", "Legal reordering on one target can leave a route residue.", _minimal(h_ok, lambda r: r["route_residue"])),
        ("P4-W27", "VII-C032", "Holonomy can occur with zero arrow credit.", _minimal(ar_ok, lambda r: r["holonomy"] and not r["arrow_credit"])),
        ("P4-W28", "VII-C032", "Independent drive, asymmetry, reversal, budget, and audit support an arrow.", _minimal(ar_ok, lambda r: r["holonomy"] and r["arrow_credit"])),
        ("P4-W29", "VII-C032", "Synchronized-order contact does not assume equality of local clock readings.", _minimal(x_ok, lambda r: r["witness_kind"] == "SYNC" and r["contact_credit"])),
        ("P4-W30", "VII-C032", "Partial-order contact is invariant under an admissible reparameterization.", _minimal(x_ok, lambda r: r["witness_kind"] == "PARTIAL_ORDER" and r["invariance_credit"])),
        ("P4-W31", "VII-C028", "The full algebra remains deferred when readiness fields are missing.", _minimal(alg_ok, lambda r: not r["full_algebra_credit"] and not r["nonredundancy_proved"])),
        ("P4-W32", "VII-C028", "A small resource-delta fragment may be credited under scoped laws.", _minimal(alg_ok, lambda r: r["resource_fragment_credit"] and not r["full_algebra_credit"])),
    ]
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
            "no_go_id": "NGVII-10",
            "failure_scenarios": ["TTW-S17"],
            "escape_scenarios": ["TTW-S18"],
            "theorem_asset": "FoundationsVII.NoGo.NGVII_10_no_arrow_from_holonomy_alone",
            "nonclaim": "The no-go blocks an arrow inference from holonomy alone; it permits a separately certified driven arrow.",
        }
    ]


PRIMARY_SCENARIOS: tuple[str, ...] = (
    "TTW-S02", "TTW-S03", "TTW-S06", "TTW-S16", "TTW-S17",
    "TTW-S18", "TTW-S20", "TTW-S21", "TTW-S24",
)
PRIMARY_COUNTERMODELS: tuple[str, ...] = (
    "CM-06", "CM-07", "CM-10", "CM-17", "CM-22", "CM-23", "CM-24", "CM-25",
)


def phase4_facts(flags: Mapping[str, Any]) -> dict[str, bool]:
    enabled = bool(flags.get("fired") or flags.get("generator_reachable") or flags.get("prospective"))
    endogenous = bool(
        flags.get("generator_reachable") and flags.get("fired")
        and not flags.get("neutral_seed") and not flags.get("observer_used")
    )
    return {
        "enabled": enabled,
        "endogenous": endogenous,
        "relation_only_contact": bool(flags.get("contact") and not flags.get("composite")),
        "enablement_without_descent": bool(flags.get("prospective") and flags.get("fired") and not flags.get("composite")),
        "necessary_but_insufficient": bool(flags.get("prospective") and flags.get("fired") and not flags.get("source_independent")),
        "order_residue": bool(flags.get("order_residue")),
        "holonomy": bool(flags.get("holonomy")),
        "arrow": bool(flags.get("holonomy") and flags.get("drive")),
        "reachable_nonoccurrent": bool(flags.get("reachable") and not flags.get("fired")),
        "occurrent": bool(flags.get("reachable") and flags.get("fired")),
        "seed_dependence": bool(flags.get("parent_refined") and flags.get("join_destroyed")),
        "join_created_residual": bool(flags.get("new_residual")),
    }


EXPECTED_PHASE4_FACTS: dict[str, dict[str, bool]] = {
    "TTW-S02": {"enabled": True, "endogenous": False},
    "TTW-S03": {"enablement_without_descent": True, "necessary_but_insufficient": True},
    "TTW-S06": {"relation_only_contact": True},
    "TTW-S16": {"order_residue": True},
    "TTW-S17": {"holonomy": True, "arrow": False},
    "TTW-S18": {"holonomy": True, "arrow": True},
    "TTW-S20": {"reachable_nonoccurrent": True},
    "TTW-S21": {"occurrent": True},
    "TTW-S24": {"seed_dependence": True, "join_created_residual": True},
}


def _evaluate_scenario_row(row: Mapping[str, Any]) -> dict[str, Any]:
    from .evaluator import evaluate

    flags = dict(row.get("flags", {}))
    observed_status, base_facts = evaluate(flags)
    derived = phase4_facts(flags)
    expected = EXPECTED_PHASE4_FACTS[str(row["scenario_id"])]
    phase4_assertions = {key: derived.get(key) == value for key, value in sorted(expected.items())}
    base_assertions = {
        key: base_facts.as_mapping().get(key) == value
        for key, value in sorted(dict(row.get("assertions", {})).items())
    }
    result: dict[str, Any] = {
        "fixture_id": str(row["scenario_id"]),
        "expected_status": str(row["expected_status"]),
        "observed_status": observed_status,
        "status_pass": observed_status == row["expected_status"],
        "phase4_assertion_results": phase4_assertions,
        "base_assertion_results": base_assertions,
        "derived_phase4": derived,
        "all_pass": observed_status == row["expected_status"]
        and all(phase4_assertions.values()) and all(base_assertions.values()),
        "canonical_input_sha256": digest(row),
    }
    result["canonical_result_sha256"] = digest(result)
    return result


def evaluate_primary_scenarios(scenarios: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_id = {str(row["scenario_id"]): row for row in scenarios}
    missing = sorted(set(PRIMARY_SCENARIOS) - set(by_id))
    if missing:
        raise AssertionError(f"missing Phase-4 scenarios: {missing}")
    return [_evaluate_scenario_row(by_id[scenario_id]) for scenario_id in PRIMARY_SCENARIOS]


def evaluate_primary_countermodels(
    countermodels: Sequence[Mapping[str, Any]],
    scenario_results: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_countermodel = {str(row["countermodel_id"]): row for row in countermodels}
    missing = sorted(set(PRIMARY_COUNTERMODELS) - set(by_countermodel))
    if missing:
        raise AssertionError(f"missing Phase-4 countermodels: {missing}")
    scenario_by_id = {str(row["fixture_id"]): row for row in scenario_results}
    scenario_expected = {str(row["fixture_id"]): str(row["expected_status"]) for row in scenario_results}
    required_fact = {
        "CM-06": ("enablement_without_descent", True),
        "CM-07": ("necessary_but_insufficient", True),
        "CM-10": ("arrow", False),
        "CM-17": ("endogenous", False),
        "CM-22": ("seed_dependence", True),
        "CM-23": ("seed_dependence", True),
        "CM-24": ("order_residue", True),
        "CM-25": ("join_created_residual", True),
    }
    results: list[dict[str, Any]] = []
    for countermodel_id in PRIMARY_COUNTERMODELS:
        row = by_countermodel[countermodel_id]
        scenario_id = str(row["scenario_id"])
        source = scenario_by_id[scenario_id]
        key, expected = required_fact[countermodel_id]
        observed = bool(source["derived_phase4"][key])
        result: dict[str, Any] = {
            "fixture_id": countermodel_id,
            "scenario_id": scenario_id,
            "expected_status": scenario_expected[scenario_id],
            "observed_status": str(source["observed_status"]),
            "status_pass": bool(source["status_pass"]),
            "required_phase4_fact": key,
            "required_fact_expected": expected,
            "required_fact_observed": observed,
            "countermodel_fact_pass": observed == expected,
            "scenario_link_pass": True,
        }
        result["all_pass"] = bool(
            result["status_pass"] and result["countermodel_fact_pass"] and result["scenario_link_pass"]
        )
        result["canonical_result_sha256"] = digest(result)
        results.append(result)
    return results
