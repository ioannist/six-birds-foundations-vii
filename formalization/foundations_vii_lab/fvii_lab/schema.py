from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from .model import FixtureError

SCHEMA_VERSION = "FVII-SCI-01.3"
ALL_FLAGS = (
    "anti_product", "budget_ok", "closed_family", "common_refinement", "compatible",
    "composite", "contact", "detector_power", "drive", "fired", "generator_reachable",
    "holonomy", "join_destroyed", "neutral_seed", "new_residual", "observer_priced",
    "observer_used", "order_residue", "parent_refined", "partial_domain", "prospective",
    "reachable", "relabel_only", "resemblance_only", "retention", "retrospective",
    "same_source", "scheduling_only", "seed", "sound", "source_independent",
    "total_lens_only",
)
ALLOWED_ASSERTIONS = (
    "bridge_valid", "certified_noninteraction", "contact", "directionality", "endogenous",
    "first_extension", "holonomy", "new_residual", "occurred", "prospective_credit",
    "reachable", "strict_join",
)
ALLOWED_STATUSES = (
    "BOOTSTRAP_BLOCKED", "BUDGET_OBSTRUCTION", "CERTIFIED_NONINTERACTION",
    "COMMON_REFINEMENT_NONSTRICT", "CONTACT_WITHOUT_JOIN", "DRIVEN_ARROW",
    "FAKE_JOIN_RELABELING", "FAKE_JOIN_SCHEDULING", "HOLONOMY_ZERO_ARROW",
    "INDEPENDENCE_GATE_FAILED", "LAWFUL_FIRST_EXTENSION", "NO_EVIDENCED_CONTACT",
    "OCCURRENT_EVENT", "ORDER_RESIDUE", "PROSPECTIVE_ADMISSION",
    "REACHABLE_NONOCCURRENT", "REFINEMENT_DESTROYS_JOIN", "RETENTION_OBSTRUCTION",
    "RETROSPECTIVE_SELF_CERTIFICATION_REJECTED", "SOUND_UNREACHABLE",
    "SOURCE_OBSTRUCTION", "STRICT_JOIN", "UNLICENSED_TOTALITY_TRANSFER",
    "UNPRICED_OBSERVER",
)
REQUIRED_STRUCTURAL_SECTIONS = (
    "domain_state", "admission_transition", "prospective_commitment", "source_ledger",
    "budget_ledger", "contact_surface", "contact_witness", "interaction_record",
    "join_candidate", "join_certificate", "join_obstruction", "noninteraction_certificate",
    "enablement_record", "reachability_witness", "observer_occupancy_record", "audit_record",
)
REQUIRED_SCENARIO_KEYS = (
    "schema_version", "fixture_kind", "fixture_id", "name", "expected_status", "flags",
    "assertions", "candidate_ids", "falsifier", "structural_record", "source_trace",
)
REQUIRED_COUNTERMODEL_KEYS = (
    "schema_version", "fixture_kind", "fixture_id", "name", "scenario_id",
    "expected_status", "shows", "candidate_ids", "escape_route", "scenario_sha256",
    "source_trace",
)
DOMAIN_KEYS = (
    "theory_id", "interface_id", "scope_id", "timestamp", "expressible", "present",
    "exposed", "recoverable", "admissible", "reachable", "occurrent",
)
STRUCTURAL_KEYS: dict[str, tuple[str, ...]] = {
    "domain_state": DOMAIN_KEYS,
    "admission_transition": (
        "transition_id", "source", "target", "source_id", "guard_description",
        "guard_satisfied", "cost", "effect_description", "executable", "fired",
    ),
    "prospective_commitment": (
        "commitment_id", "active", "registered_at", "valid_from", "expires_at",
        "future_transition", "reserved_budget", "source_id", "permitted_source_kinds",
        "preregistered", "disposition",
    ),
    "source_ledger": (
        "seed", "neutral_seed", "generator_reachable", "same_source",
        "source_independent", "observer_used", "entries",
    ),
    "budget_ledger": ("budget_ok", "observer_priced", "entries"),
    "contact_surface": (
        "surface_id", "left_theory", "right_theory", "left_interface", "right_interface",
        "crossing_relation", "compatible", "admissible", "scope_id",
    ),
    "contact_witness": (
        "witness_id", "present", "surface_id", "event_id", "source_id", "crossed",
        "source_typed", "payload_description",
    ),
    "interaction_record": (
        "interaction_id", "parents", "contact_witness_present", "transition_ids", "status",
        "timestamp",
    ),
    "join_candidate": (
        "candidate_id", "present", "composite_theory", "comparison_baseline", "composite",
        "common_refinement",
    ),
    "join_certificate": (
        "certificate_id", "present", "objecthood_witness", "retention_witnesses",
        "source_witnesses", "budget_witnesses", "strictness_witness",
    ),
    "join_obstruction": (
        "obstruction_id", "present", "kind", "witness_description", "escape_routes",
    ),
    "noninteraction_certificate": (
        "certificate_id", "present", "covered_family", "family_closed", "detector_id",
        "detector_power", "budget", "horizon", "observed_contact", "escape_routes",
    ),
    "enablement_record": (
        "enablement_id", "enabled_operation", "source_id", "executed",
        "target_before_timestamp", "target_after_timestamp", "attribution",
    ),
    "reachability_witness": (
        "witness_id", "present", "initial_timestamp", "terminal_timestamp",
        "transition_ids", "trace_timestamps", "guards_satisfied", "resources_available",
        "executable",
    ),
    "observer_occupancy_record": (
        "occupancy_id", "observer_id", "used", "source_kind", "visible_interfaces",
        "capacity", "occupied", "charged", "disposition",
    ),
    "audit_record": ("append_only", "frozen_expected_status", "entries"),
}
SOURCE_ENTRY_KEYS = (
    "source_id", "kind", "parent_sources", "generated_by_system", "in_scope", "disposition",
)
BUDGET_ENTRY_KEYS = (
    "resource_id", "kind", "allocated", "spent", "refunded", "occupied", "disposition",
)
AUDIT_ENTRY_KEYS = ("audit_id", "disposition", "subject", "message", "source_location")
SCENARIO_TRACE_KEYS = ("source_path", "source_id", "migration")
COUNTERMODEL_TRACE_KEYS = (
    "source_path", "source_id", "scenario_source_id", "evidence_grade",
)


def _require_keys(value: Mapping[str, Any], keys: Sequence[str], where: str) -> None:
    missing = sorted(set(keys) - set(value))
    if missing:
        raise FixtureError(f"{where}: missing required keys {missing}")


def _require_exact_keys(value: Mapping[str, Any], keys: Sequence[str], where: str) -> None:
    _require_keys(value, keys, where)
    extra = sorted(set(value) - set(keys))
    if extra:
        raise FixtureError(f"{where}: unexpected keys {extra}")


def _require_type(value: Any, kind: type | tuple[type, ...], where: str) -> None:
    if not isinstance(value, kind):
        raise FixtureError(f"{where}: expected {kind}, got {type(value).__name__}")


def _require_bool(value: Any, where: str) -> None:
    if type(value) is not bool:
        raise FixtureError(f"{where}: expected bool")


def _require_int(value: Any, where: str) -> None:
    if type(value) is not int or value < 0:
        raise FixtureError(f"{where}: expected nonnegative integer")


def _require_nonempty_text(value: Any, where: str) -> None:
    if not isinstance(value, str) or not value:
        raise FixtureError(f"{where}: expected nonempty string")


def _require_list(value: Any, where: str, *, nonempty: bool = False) -> list[Any]:
    _require_type(value, list, where)
    if nonempty and not value:
        raise FixtureError(f"{where}: expected nonempty list")
    return value


def _validate_domain_state(state: Any, where: str) -> None:
    _require_type(state, Mapping, where)
    _require_exact_keys(state, DOMAIN_KEYS, where)
    for key in ("theory_id", "interface_id", "timestamp"):
        _require_int(state[key], f"{where}.{key}")
    _require_nonempty_text(state["scope_id"], f"{where}.scope_id")
    for key in ("expressible", "present", "exposed", "recoverable", "admissible", "reachable", "occurrent"):
        _require_bool(state[key], f"{where}.{key}")
    implications = (
        ("occurrent", "reachable"), ("reachable", "admissible"),
        ("admissible", "present"), ("recoverable", "exposed"),
        ("exposed", "present"), ("present", "expressible"),
    )
    for left, right in implications:
        if state[left] and not state[right]:
            raise FixtureError(f"{where}: {left} requires {right}")


def _validate_structure_shapes(structural: Mapping[str, Any]) -> None:
    _require_exact_keys(structural, REQUIRED_STRUCTURAL_SECTIONS, "scenario.structural_record")
    for section, keys in STRUCTURAL_KEYS.items():
        value = structural[section]
        _require_type(value, Mapping, f"scenario.structural_record.{section}")
        _require_exact_keys(value, keys, f"scenario.structural_record.{section}")
    _validate_domain_state(structural["domain_state"], "scenario.domain_state")
    transition = structural["admission_transition"]
    _validate_domain_state(transition["source"], "scenario.admission_transition.source")
    _validate_domain_state(transition["target"], "scenario.admission_transition.target")
    for entry in _require_list(structural["source_ledger"]["entries"], "scenario.source_ledger.entries", nonempty=True):
        _require_type(entry, Mapping, "scenario.source_ledger.entry")
        _require_exact_keys(entry, SOURCE_ENTRY_KEYS, "scenario.source_ledger.entry")
    for entry in _require_list(structural["budget_ledger"]["entries"], "scenario.budget_ledger.entries", nonempty=True):
        _require_type(entry, Mapping, "scenario.budget_ledger.entry")
        _require_exact_keys(entry, BUDGET_ENTRY_KEYS, "scenario.budget_ledger.entry")
    for entry in _require_list(structural["audit_record"]["entries"], "scenario.audit_record.entries", nonempty=True):
        _require_type(entry, Mapping, "scenario.audit_record.entry")
        _require_exact_keys(entry, AUDIT_ENTRY_KEYS, "scenario.audit_record.entry")


def _validate_transition(structural: Mapping[str, Any]) -> None:
    transition = structural["admission_transition"]
    for key in ("transition_id", "source_id", "guard_description", "effect_description"):
        _require_nonempty_text(transition[key], f"scenario.admission_transition.{key}")
    for key in ("guard_satisfied", "executable", "fired"):
        _require_bool(transition[key], f"scenario.admission_transition.{key}")
    _require_int(transition["cost"], "scenario.admission_transition.cost")
    if transition["fired"] and not transition["executable"]:
        raise FixtureError("scenario.admission_transition: fired requires executable")
    if transition["executable"] and not transition["guard_satisfied"]:
        raise FixtureError("scenario.admission_transition: executable requires satisfied guard")
    if transition["source"]["theory_id"] != transition["target"]["theory_id"]:
        raise FixtureError("scenario.admission_transition: theory identity mismatch")
    if transition["target"]["timestamp"] < transition["source"]["timestamp"]:
        raise FixtureError("scenario.admission_transition: time reversal")


def _validate_ledgers(structural: Mapping[str, Any]) -> None:
    source = structural["source_ledger"]
    for key in ("seed", "neutral_seed", "generator_reachable", "same_source", "source_independent", "observer_used"):
        _require_bool(source[key], f"scenario.source_ledger.{key}")
    source_ids: list[str] = []
    for entry in source["entries"]:
        _require_nonempty_text(entry["source_id"], "scenario.source_ledger.entry.source_id")
        source_ids.append(entry["source_id"])
        _require_nonempty_text(entry["kind"], "scenario.source_ledger.entry.kind")
        parents = _require_list(entry["parent_sources"], "scenario.source_ledger.entry.parent_sources")
        if any(not isinstance(parent, str) or not parent for parent in parents):
            raise FixtureError("scenario.source_ledger.entry.parent_sources: invalid source id")
        if entry["source_id"] in parents:
            raise FixtureError("scenario.source_ledger.entry: source cannot parent itself")
        _require_bool(entry["generated_by_system"], "scenario.source_ledger.entry.generated_by_system")
        _require_bool(entry["in_scope"], "scenario.source_ledger.entry.in_scope")
        _require_nonempty_text(entry["disposition"], "scenario.source_ledger.entry.disposition")
    if len(source_ids) != len(set(source_ids)):
        raise FixtureError("scenario.source_ledger: duplicate source ids")

    budget = structural["budget_ledger"]
    for key in ("budget_ok", "observer_priced"):
        _require_bool(budget[key], f"scenario.budget_ledger.{key}")
    for entry in budget["entries"]:
        _require_nonempty_text(entry["resource_id"], "scenario.budget_ledger.entry.resource_id")
        _require_nonempty_text(entry["kind"], "scenario.budget_ledger.entry.kind")
        for key in ("allocated", "spent", "refunded", "occupied"):
            _require_int(entry[key], f"scenario.budget_ledger.entry.{key}")
        _require_nonempty_text(entry["disposition"], "scenario.budget_ledger.entry.disposition")
        if entry["disposition"] == "ACCEPTED":
            if (
                entry["spent"] > entry["allocated"]
                or entry["refunded"] > entry["allocated"]
                or entry["occupied"] > entry["allocated"]
                or entry["spent"] + entry["occupied"] > entry["allocated"] + entry["refunded"]
            ):
                raise FixtureError("scenario.budget_ledger: accepted entry is infeasible")


def _validate_relations(value: Mapping[str, Any]) -> None:
    structural = value["structural_record"]
    flags = value["flags"]
    transition = structural["admission_transition"]
    if transition["target"] != structural["domain_state"]:
        raise FixtureError("scenario.admission_transition: target must equal domain_state")
    if transition["fired"] != flags["fired"]:
        raise FixtureError("scenario.admission_transition: firing mismatch")
    if structural["domain_state"]["reachable"] != flags["reachable"]:
        raise FixtureError("scenario.domain_state: reachability mismatch")
    if structural["domain_state"]["occurrent"] != flags["fired"]:
        raise FixtureError("scenario.domain_state: occurrence mismatch")

    audit = structural["audit_record"]
    _require_bool(audit["append_only"], "scenario.audit_record.append_only")
    if not audit["append_only"]:
        raise FixtureError("scenario.audit_record: append_only must be true")
    if audit["frozen_expected_status"] != value["expected_status"]:
        raise FixtureError("scenario.audit_record: frozen status mismatch")
    for entry in audit["entries"]:
        for key in AUDIT_ENTRY_KEYS:
            _require_nonempty_text(entry[key], f"scenario.audit_record.entry.{key}")

    contact = structural["contact_witness"]
    if contact["present"] != flags["contact"] or contact["crossed"] != flags["contact"]:
        raise FixtureError("scenario.contact_witness: contact/crossing mismatch")
    if contact["source_typed"] != flags["contact"]:
        raise FixtureError("scenario.contact_witness: source-typing mismatch")
    surface = structural["contact_surface"]
    if surface["left_theory"] == surface["right_theory"]:
        raise FixtureError("scenario.contact_surface: theories must be distinct")
    if contact["surface_id"] != surface["surface_id"]:
        raise FixtureError("scenario.contact_witness: surface id mismatch")

    if structural["source_ledger"]["seed"] != flags["seed"]:
        raise FixtureError("scenario.source_ledger: seed mismatch")
    if structural["source_ledger"]["source_independent"] != flags["source_independent"]:
        raise FixtureError("scenario.source_ledger: independence mismatch")
    if structural["budget_ledger"]["budget_ok"] != flags["budget_ok"]:
        raise FixtureError("scenario.budget_ledger: budget mismatch")

    observer = structural["observer_occupancy_record"]
    if observer["used"] != flags["observer_used"]:
        raise FixtureError("scenario.observer_occupancy_record: observer mismatch")
    for key in ("capacity", "occupied", "charged"):
        _require_int(observer[key], f"scenario.observer_occupancy_record.{key}")
    if observer["used"] != (observer["occupied"] > 0):
        raise FixtureError("scenario.observer_occupancy_record: used/occupied mismatch")
    if observer["disposition"] == "ACCEPTED" and observer["occupied"] > observer["capacity"]:
        raise FixtureError("scenario.observer_occupancy_record: accepted occupancy exceeds capacity")

    reachability = structural["reachability_witness"]
    if reachability["present"] != flags["reachable"]:
        raise FixtureError("scenario.reachability_witness: reachability mismatch")
    if reachability["present"]:
        if not (reachability["guards_satisfied"] and reachability["resources_available"] and reachability["executable"]):
            raise FixtureError("scenario.reachability_witness: present witness must be executable")
        _require_list(reachability["transition_ids"], "scenario.reachability_witness.transition_ids", nonempty=True)
        _require_list(reachability["trace_timestamps"], "scenario.reachability_witness.trace_timestamps", nonempty=True)

    join = structural["join_certificate"]
    expected_strict = all(
        (flags["contact"], flags["source_independent"], flags["composite"], flags["retention"],
         flags["anti_product"], flags["budget_ok"], not flags["scheduling_only"], not flags["relabel_only"])
    )
    if join["present"] != expected_strict:
        raise FixtureError("scenario.join_certificate: strict-join mismatch")
    if join["present"]:
        if not join["objecthood_witness"] or not join["strictness_witness"]:
            raise FixtureError("scenario.join_certificate: missing objecthood/strictness witness")
        for field in ("retention_witnesses", "source_witnesses", "budget_witnesses"):
            _require_list(join[field], f"scenario.join_certificate.{field}", nonempty=True)

    noninteraction = structural["noninteraction_certificate"]
    expected_noninteraction = not flags["contact"] and flags["closed_family"] and flags["detector_power"]
    if noninteraction["present"] != expected_noninteraction:
        raise FixtureError("scenario.noninteraction_certificate: presence mismatch")
    if noninteraction["present"] and (
        noninteraction["observed_contact"] or not noninteraction["family_closed"] or not noninteraction["detector_power"]
    ):
        raise FixtureError("scenario.noninteraction_certificate: invalid coverage certificate")

    if structural["enablement_record"]["executed"] != flags["fired"]:
        raise FixtureError("scenario.enablement_record: execution mismatch")
    if structural["interaction_record"]["status"] != value["expected_status"]:
        raise FixtureError("scenario.interaction_record: status mismatch")


def _validate_candidate_ids(value: Any, where: str) -> None:
    ids = _require_list(value, where)
    if len(set(ids)) != len(ids):
        raise FixtureError(f"{where}: duplicates")
    for candidate_id in ids:
        if not isinstance(candidate_id, str) or not re.fullmatch(r"VII-C\d{3}", candidate_id):
            raise FixtureError(f"{where}: invalid candidate id {candidate_id!r}")


def validate_scenario_dict(value: Any) -> None:
    _require_type(value, Mapping, "scenario")
    _require_exact_keys(value, REQUIRED_SCENARIO_KEYS, "scenario")
    if value["schema_version"] != SCHEMA_VERSION:
        raise FixtureError("scenario: unsupported schema_version")
    if value["fixture_kind"] != "scenario":
        raise FixtureError("scenario: fixture_kind must be 'scenario'")
    if not isinstance(value["fixture_id"], str) or not re.fullmatch(r"TTW-S\d{2}", value["fixture_id"]):
        raise FixtureError("scenario.fixture_id: invalid id")
    for key in ("name", "falsifier"):
        _require_nonempty_text(value[key], f"scenario.{key}")
    if value["expected_status"] not in ALLOWED_STATUSES:
        raise FixtureError("scenario.expected_status: unknown status")
    _require_type(value["flags"], Mapping, "scenario.flags")
    _require_exact_keys(value["flags"], ALL_FLAGS, "scenario.flags")
    for key, flag in value["flags"].items():
        _require_bool(flag, f"scenario.flags.{key}")
    _require_type(value["assertions"], Mapping, "scenario.assertions")
    if not value["assertions"]:
        raise FixtureError("scenario.assertions: expected at least one assertion")
    unknown_assertions = sorted(set(value["assertions"]) - set(ALLOWED_ASSERTIONS))
    if unknown_assertions:
        raise FixtureError(f"scenario.assertions: unknown keys {unknown_assertions}")
    for key, expected in value["assertions"].items():
        _require_bool(expected, f"scenario.assertions.{key}")
    _validate_candidate_ids(value["candidate_ids"], "scenario.candidate_ids")
    _require_type(value["source_trace"], Mapping, "scenario.source_trace")
    _require_exact_keys(value["source_trace"], SCENARIO_TRACE_KEYS, "scenario.source_trace")
    for key in SCENARIO_TRACE_KEYS:
        _require_nonempty_text(value["source_trace"][key], f"scenario.source_trace.{key}")
    if value["source_trace"]["source_id"] != value["fixture_id"]:
        raise FixtureError("scenario.source_trace: source id mismatch")
    _require_type(value["structural_record"], Mapping, "scenario.structural_record")
    _validate_structure_shapes(value["structural_record"])
    _validate_transition(value["structural_record"])
    _validate_ledgers(value["structural_record"])
    _validate_relations(value)


def validate_countermodel_dict(value: Any) -> None:
    _require_type(value, Mapping, "countermodel")
    _require_exact_keys(value, REQUIRED_COUNTERMODEL_KEYS, "countermodel")
    if value["schema_version"] != SCHEMA_VERSION:
        raise FixtureError("countermodel: unsupported schema_version")
    if value["fixture_kind"] != "countermodel":
        raise FixtureError("countermodel: fixture_kind must be 'countermodel'")
    if not isinstance(value["fixture_id"], str) or not re.fullmatch(r"CM-\d{2}", value["fixture_id"]):
        raise FixtureError("countermodel.fixture_id: invalid id")
    if not isinstance(value["scenario_id"], str) or not re.fullmatch(r"TTW-S\d{2}", value["scenario_id"]):
        raise FixtureError("countermodel.scenario_id: invalid id")
    for key in ("name", "shows", "escape_route"):
        _require_nonempty_text(value[key], f"countermodel.{key}")
    if value["expected_status"] not in ALLOWED_STATUSES:
        raise FixtureError("countermodel.expected_status: unknown status")
    if not isinstance(value["scenario_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", value["scenario_sha256"]):
        raise FixtureError("countermodel.scenario_sha256: invalid digest")
    _validate_candidate_ids(value["candidate_ids"], "countermodel.candidate_ids")
    _require_type(value["source_trace"], Mapping, "countermodel.source_trace")
    _require_exact_keys(value["source_trace"], COUNTERMODEL_TRACE_KEYS, "countermodel.source_trace")
    for key in COUNTERMODEL_TRACE_KEYS:
        _require_nonempty_text(value["source_trace"][key], f"countermodel.source_trace.{key}")
    if value["source_trace"]["source_id"] != value["fixture_id"]:
        raise FixtureError("countermodel.source_trace: source id mismatch")
    if value["source_trace"]["scenario_source_id"] != value["scenario_id"]:
        raise FixtureError("countermodel.source_trace: scenario source id mismatch")
