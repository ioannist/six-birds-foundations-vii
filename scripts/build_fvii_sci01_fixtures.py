#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "formalization" / "foundations_vii_lab"
SCENARIO_SRC = ROOT / "readiness" / "two_theory_world" / "scenarios.jsonl"
COUNTERMODEL_SRC = ROOT / "readiness" / "countermodel_atlas.jsonl"
SCHEMA_VERSION = "FVII-SCI-01.3"

ALL_FLAGS = [
    "anti_product", "budget_ok", "closed_family", "common_refinement", "compatible",
    "composite", "contact", "detector_power", "drive", "fired", "generator_reachable",
    "holonomy", "join_destroyed", "neutral_seed", "new_residual", "observer_priced",
    "observer_used", "order_residue", "parent_refined", "partial_domain", "prospective",
    "reachable", "relabel_only", "resemblance_only", "retention", "retrospective",
    "same_source", "scheduling_only", "seed", "sound", "source_independent",
    "total_lens_only",
]
ALLOWED_ASSERTIONS = [
    "bridge_valid", "certified_noninteraction", "contact", "directionality", "endogenous",
    "first_extension", "holonomy", "new_residual", "occurred", "prospective_credit",
    "reachable", "strict_join",
]
ALLOWED_STATUSES = [
    "BOOTSTRAP_BLOCKED", "BUDGET_OBSTRUCTION", "CERTIFIED_NONINTERACTION",
    "COMMON_REFINEMENT_NONSTRICT", "CONTACT_WITHOUT_JOIN", "DRIVEN_ARROW",
    "FAKE_JOIN_RELABELING", "FAKE_JOIN_SCHEDULING", "HOLONOMY_ZERO_ARROW",
    "INDEPENDENCE_GATE_FAILED", "LAWFUL_FIRST_EXTENSION", "NO_EVIDENCED_CONTACT",
    "OCCURRENT_EVENT", "ORDER_RESIDUE", "PROSPECTIVE_ADMISSION",
    "REACHABLE_NONOCCURRENT", "REFINEMENT_DESTROYS_JOIN", "RETENTION_OBSTRUCTION",
    "RETROSPECTIVE_SELF_CERTIFICATION_REJECTED", "SOUND_UNREACHABLE",
    "SOURCE_OBSTRUCTION", "STRICT_JOIN", "UNLICENSED_TOTALITY_TRANSFER",
    "UNPRICED_OBSERVER",
]


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def hash_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def strict_join(flags: dict[str, bool]) -> bool:
    return all(
        (
            flags["contact"], flags["source_independent"], flags["composite"],
            flags["retention"], flags["anti_product"], flags["budget_ok"],
            not flags["scheduling_only"], not flags["relabel_only"],
        )
    )


def source_kind(flags: dict[str, bool]) -> str:
    if flags["observer_used"]:
        return "OBSERVER"
    if flags["seed"]:
        return "EXTERNAL_PROVISION"
    if flags["generator_reachable"] and flags["fired"]:
        return "ENDOGENOUS"
    if flags["contact"]:
        return "BRIDGED"
    return "NATIVE"


def obstruction_kind(flags: dict[str, bool]) -> str:
    if flags["contact"] and flags["composite"] and flags["anti_product"] and not flags["source_independent"]:
        return "SOURCE"
    if flags["contact"] and flags["composite"] and flags["anti_product"] and not flags["budget_ok"]:
        return "BUDGET"
    if flags["contact"] and flags["composite"] and not flags["retention"]:
        return "RETENTION"
    if flags["compatible"] and not flags["contact"]:
        return "GLUING"
    if flags["relabel_only"] or flags["scheduling_only"]:
        return "NOVELTY"
    return "NONE"


def structural_record(scenario: dict[str, Any], flags: dict[str, bool]) -> dict[str, Any]:
    sid = scenario["scenario_id"]
    n = int(sid.split("S", 1)[1])
    exposed = bool(flags["contact"] or flags["compatible"] or flags["observer_used"] or flags["sound"] or flags["reachable"])
    recoverable = bool(flags["sound"] or flags["reachable"] or flags["contact"])
    admissible = bool(flags["prospective"] or flags["seed"] or flags["contact"] or flags["reachable"])
    present = bool(exposed or admissible)
    executable = bool(flags["reachable"] or flags["generator_reachable"] or flags["contact"])
    has_strict_join = strict_join(flags)
    certified_noninteraction = bool(not flags["contact"] and flags["closed_family"] and flags["detector_power"])
    s_kind = source_kind(flags)
    obstruction = obstruction_kind(flags)
    domain = {
        "theory_id": 1,
        "interface_id": 101,
        "scope_id": "TTW-FROZEN-FAMILY",
        "timestamp": n,
        "expressible": True,
        "present": present,
        "exposed": exposed,
        "recoverable": recoverable,
        "admissible": admissible,
        "reachable": flags["reachable"],
        "occurrent": flags["fired"],
    }
    source_domain = dict(domain)
    source_domain.update({"timestamp": max(0, n - 1), "occurrent": False})
    if flags["fired"]:
        source_domain["reachable"] = True
        source_domain["admissible"] = True
        source_domain["present"] = True
    return {
        "domain_state": domain,
        "admission_transition": {
            "transition_id": f"{sid}-TRANSITION",
            "source": source_domain,
            "target": domain,
            "source_id": f"{sid}-SOURCE",
            "guard_description": "Frozen finite-world guard",
            "guard_satisfied": executable,
            "cost": 1 if (flags["contact"] or flags["fired"] or flags["observer_used"]) else 0,
            "effect_description": "Advance to the frozen target state",
            "executable": executable,
            "fired": flags["fired"],
        },
        "prospective_commitment": {
            "commitment_id": f"{sid}-COMMITMENT",
            "active": flags["prospective"],
            "registered_at": max(0, n - 1),
            "valid_from": n,
            "expires_at": n + 1,
            "future_transition": f"{sid}-TRANSITION",
            "reserved_budget": 1 if flags["prospective"] else 0,
            "source_id": f"{sid}-SOURCE",
            "permitted_source_kinds": [s_kind],
            "preregistered": flags["prospective"],
            "disposition": "ACCEPTED" if flags["prospective"] else "FAILED",
        },
        "source_ledger": {
            "seed": flags["seed"],
            "neutral_seed": flags["neutral_seed"],
            "generator_reachable": flags["generator_reachable"],
            "same_source": flags["same_source"],
            "source_independent": flags["source_independent"],
            "observer_used": flags["observer_used"],
            "entries": [{
                "source_id": f"{sid}-SOURCE",
                "kind": s_kind,
                "parent_sources": [] if not flags["same_source"] else ["SHARED-PARENT"],
                "generated_by_system": s_kind == "ENDOGENOUS",
                "in_scope": True,
                "disposition": "ACCEPTED",
            }],
        },
        "budget_ledger": {
            "budget_ok": flags["budget_ok"],
            "observer_priced": flags["observer_priced"],
            "entries": [{
                "resource_id": f"{sid}-RESOURCE",
                "kind": "OCCUPANCY" if flags["observer_used"] else "CROSS_COST",
                "allocated": 1 if flags["budget_ok"] or flags["observer_priced"] else 0,
                "spent": 1 if (flags["budget_ok"] and (flags["contact"] or flags["fired"])) else 0,
                "refunded": 0,
                "occupied": 1 if flags["observer_used"] else 0,
                "disposition": "ACCEPTED" if flags["budget_ok"] or not (flags["contact"] or flags["observer_used"]) else "FAILED",
            }],
        },
        "contact_surface": {
            "surface_id": f"{sid}-SURFACE",
            "left_theory": 1,
            "right_theory": 2,
            "left_interface": 101,
            "right_interface": 201,
            "crossing_relation": "TTW_DECLARED_CROSSING",
            "compatible": flags["compatible"],
            "admissible": bool(flags["compatible"] or flags["contact"]),
            "scope_id": "TTW-FROZEN-FAMILY",
        },
        "contact_witness": {
            "witness_id": f"{sid}-CONTACT",
            "present": flags["contact"],
            "surface_id": f"{sid}-SURFACE",
            "event_id": f"{sid}-EVENT",
            "source_id": f"{sid}-SOURCE",
            "crossed": flags["contact"],
            "source_typed": flags["contact"],
            "payload_description": "Frozen contact payload" if flags["contact"] else "NO_CONTACT_PAYLOAD",
        },
        "interaction_record": {
            "interaction_id": f"{sid}-INTERACTION",
            "parents": [1, 2],
            "contact_witness_present": flags["contact"],
            "transition_ids": [f"{sid}-TRANSITION"],
            "status": scenario["expected_status"],
            "timestamp": n,
        },
        "join_candidate": {
            "candidate_id": f"{sid}-JOIN-CANDIDATE",
            "present": bool(flags["contact"] or flags["composite"] or flags["common_refinement"]),
            "composite_theory": 3,
            "comparison_baseline": "PARENT_PRODUCT_BASELINE",
            "composite": flags["composite"],
            "common_refinement": flags["common_refinement"],
        },
        "join_certificate": {
            "certificate_id": f"{sid}-JOIN-CERTIFICATE",
            "present": has_strict_join,
            "objecthood_witness": bool(flags["composite"]),
            "retention_witnesses": ["LEFT", "RIGHT"] if flags["retention"] else [],
            "source_witnesses": [f"{sid}-SOURCE"] if flags["source_independent"] else [],
            "budget_witnesses": [f"{sid}-RESOURCE"] if flags["budget_ok"] else [],
            "strictness_witness": flags["anti_product"],
        },
        "join_obstruction": {
            "obstruction_id": f"{sid}-OBSTRUCTION",
            "present": obstruction != "NONE",
            "kind": obstruction,
            "witness_description": "Frozen missing or defeated join obligation" if obstruction != "NONE" else "NO_DECLARED_OBSTRUCTION",
            "escape_routes": ["Add the missing typed witness or narrow the claim."],
        },
        "noninteraction_certificate": {
            "certificate_id": f"{sid}-NONINTERACTION",
            "present": certified_noninteraction,
            "covered_family": "TTW-FROZEN-FAMILY",
            "family_closed": flags["closed_family"],
            "detector_id": "FVII-DETECTOR-25",
            "detector_power": flags["detector_power"],
            "budget": 1,
            "horizon": 1,
            "observed_contact": flags["contact"],
            "escape_routes": ["Expand the carrier, horizon, budget, or detector family."],
        },
        "enablement_record": {
            "enablement_id": f"{sid}-ENABLEMENT",
            "enabled_operation": "FROZEN_TRANSITION",
            "source_id": f"{sid}-SOURCE",
            "executed": flags["fired"],
            "target_before_timestamp": max(0, n - 1),
            "target_after_timestamp": n,
            "attribution": s_kind,
        },
        "reachability_witness": {
            "witness_id": f"{sid}-REACHABILITY",
            "present": flags["reachable"],
            "initial_timestamp": max(0, n - 1),
            "terminal_timestamp": n,
            "transition_ids": [f"{sid}-TRANSITION"] if flags["reachable"] else [],
            "trace_timestamps": [max(0, n - 1), n] if flags["reachable"] else [],
            "guards_satisfied": flags["reachable"],
            "resources_available": bool(flags["budget_ok"] or not flags["contact"]),
            "executable": flags["reachable"],
        },
        "observer_occupancy_record": {
            "occupancy_id": f"{sid}-OBSERVER",
            "observer_id": "TTW-OBSERVER",
            "used": flags["observer_used"],
            "source_kind": "OBSERVER",
            "visible_interfaces": [101, 201] if flags["observer_used"] else [101],
            "capacity": 1,
            "occupied": 1 if flags["observer_used"] else 0,
            "charged": 1 if flags["observer_priced"] else 0,
            "disposition": "ACCEPTED" if not flags["observer_used"] or flags["observer_priced"] else "FAILED",
        },
        "audit_record": {
            "append_only": True,
            "frozen_expected_status": scenario["expected_status"],
            "entries": [{
                "audit_id": f"{sid}-FREEZE",
                "disposition": "ACCEPTED",
                "subject": sid,
                "message": "Step-3 expected status frozen before Phase-1 implementation.",
                "source_location": "readiness/two_theory_world/scenarios.jsonl",
            }],
        },
    }


def write_json_schema() -> None:
    schema_dir = LAB / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)

    text = {"type": "string", "minLength": 1}
    nonnegative = {"type": "integer", "minimum": 0}
    boolean = {"type": "boolean"}
    string_array = {"type": "array", "items": text}

    def closed(properties: dict[str, Any], *, required: list[str] | None = None) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": properties,
            "required": required if required is not None else list(properties),
            "additionalProperties": False,
        }

    domain = closed({
        "theory_id": nonnegative, "interface_id": nonnegative, "scope_id": text,
        "timestamp": nonnegative, "expressible": boolean, "present": boolean,
        "exposed": boolean, "recoverable": boolean, "admissible": boolean,
        "reachable": boolean, "occurrent": boolean,
    })
    source_entry = closed({
        "source_id": text, "kind": text, "parent_sources": string_array,
        "generated_by_system": boolean, "in_scope": boolean, "disposition": text,
    })
    budget_entry = closed({
        "resource_id": text, "kind": text, "allocated": nonnegative, "spent": nonnegative,
        "refunded": nonnegative, "occupied": nonnegative, "disposition": text,
    })
    audit_entry = closed({
        "audit_id": text, "disposition": text, "subject": text, "message": text,
        "source_location": text,
    })
    structural = closed({
        "domain_state": domain,
        "admission_transition": closed({
            "transition_id": text, "source": domain, "target": domain, "source_id": text,
            "guard_description": text, "guard_satisfied": boolean, "cost": nonnegative,
            "effect_description": text, "executable": boolean, "fired": boolean,
        }),
        "prospective_commitment": closed({
            "commitment_id": text, "active": boolean, "registered_at": nonnegative,
            "valid_from": nonnegative, "expires_at": nonnegative, "future_transition": text,
            "reserved_budget": nonnegative, "source_id": text,
            "permitted_source_kinds": {"type": "array", "items": text, "minItems": 1},
            "preregistered": boolean, "disposition": text,
        }),
        "source_ledger": closed({
            "seed": boolean, "neutral_seed": boolean, "generator_reachable": boolean,
            "same_source": boolean, "source_independent": boolean, "observer_used": boolean,
            "entries": {"type": "array", "items": source_entry, "minItems": 1},
        }),
        "budget_ledger": closed({
            "budget_ok": boolean, "observer_priced": boolean,
            "entries": {"type": "array", "items": budget_entry, "minItems": 1},
        }),
        "contact_surface": closed({
            "surface_id": text, "left_theory": nonnegative, "right_theory": nonnegative,
            "left_interface": nonnegative, "right_interface": nonnegative,
            "crossing_relation": text, "compatible": boolean, "admissible": boolean,
            "scope_id": text,
        }),
        "contact_witness": closed({
            "witness_id": text, "present": boolean, "surface_id": text, "event_id": text,
            "source_id": text, "crossed": boolean, "source_typed": boolean,
            "payload_description": text,
        }),
        "interaction_record": closed({
            "interaction_id": text,
            "parents": {"type": "array", "items": nonnegative, "minItems": 1},
            "contact_witness_present": boolean,
            "transition_ids": {"type": "array", "items": text},
            "status": {"type": "string", "enum": ALLOWED_STATUSES},
            "timestamp": nonnegative,
        }),
        "join_candidate": closed({
            "candidate_id": text, "present": boolean, "composite_theory": nonnegative,
            "comparison_baseline": text, "composite": boolean, "common_refinement": boolean,
        }),
        "join_certificate": closed({
            "certificate_id": text, "present": boolean, "objecthood_witness": boolean,
            "retention_witnesses": string_array, "source_witnesses": string_array,
            "budget_witnesses": string_array, "strictness_witness": boolean,
        }),
        "join_obstruction": closed({
            "obstruction_id": text, "present": boolean, "kind": text,
            "witness_description": text,
            "escape_routes": {"type": "array", "items": text, "minItems": 1},
        }),
        "noninteraction_certificate": closed({
            "certificate_id": text, "present": boolean, "covered_family": text,
            "family_closed": boolean, "detector_id": text, "detector_power": boolean,
            "budget": nonnegative, "horizon": nonnegative, "observed_contact": boolean,
            "escape_routes": {"type": "array", "items": text, "minItems": 1},
        }),
        "enablement_record": closed({
            "enablement_id": text, "enabled_operation": text, "source_id": text,
            "executed": boolean, "target_before_timestamp": nonnegative,
            "target_after_timestamp": nonnegative, "attribution": text,
        }),
        "reachability_witness": closed({
            "witness_id": text, "present": boolean, "initial_timestamp": nonnegative,
            "terminal_timestamp": nonnegative, "transition_ids": string_array,
            "trace_timestamps": {"type": "array", "items": nonnegative},
            "guards_satisfied": boolean, "resources_available": boolean,
            "executable": boolean,
        }),
        "observer_occupancy_record": closed({
            "occupancy_id": text, "observer_id": text, "used": boolean,
            "source_kind": text,
            "visible_interfaces": {"type": "array", "items": nonnegative, "minItems": 1},
            "capacity": nonnegative, "occupied": nonnegative, "charged": nonnegative,
            "disposition": text,
        }),
        "audit_record": closed({
            "append_only": boolean,
            "frozen_expected_status": {"type": "string", "enum": ALLOWED_STATUSES},
            "entries": {"type": "array", "items": audit_entry, "minItems": 1},
        }),
    })
    scenario_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://six-birds.local/fvii-sci-01/scenario.schema.json",
        "title": "Foundations VII Phase-1 scenario fixture",
        **closed({
            "schema_version": {"const": SCHEMA_VERSION},
            "fixture_kind": {"const": "scenario"},
            "fixture_id": {"type": "string", "pattern": "^TTW-S[0-9]{2}$"},
            "name": text,
            "expected_status": {"type": "string", "enum": ALLOWED_STATUSES},
            "flags": closed({name: boolean for name in ALL_FLAGS}),
            "assertions": {
                "type": "object",
                "properties": {name: boolean for name in ALLOWED_ASSERTIONS},
                "minProperties": 1,
                "additionalProperties": False,
            },
            "candidate_ids": {
                "type": "array", "items": {"type": "string", "pattern": "^VII-C[0-9]{3}$"},
                "uniqueItems": True,
            },
            "falsifier": text,
            "structural_record": structural,
            "source_trace": closed({
                "source_path": text, "source_id": text, "migration": text,
            }),
        }),
    }
    countermodel_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://six-birds.local/fvii-sci-01/countermodel.schema.json",
        "title": "Foundations VII Phase-1 countermodel fixture",
        **closed({
            "schema_version": {"const": SCHEMA_VERSION},
            "fixture_kind": {"const": "countermodel"},
            "fixture_id": {"type": "string", "pattern": "^CM-[0-9]{2}$"},
            "name": text,
            "scenario_id": {"type": "string", "pattern": "^TTW-S[0-9]{2}$"},
            "expected_status": {"type": "string", "enum": ALLOWED_STATUSES},
            "shows": text,
            "candidate_ids": {
                "type": "array", "items": {"type": "string", "pattern": "^VII-C[0-9]{3}$"},
                "uniqueItems": True,
            },
            "escape_route": text,
            "scenario_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            "source_trace": closed({
                "source_path": text, "source_id": text, "scenario_source_id": text,
                "evidence_grade": text,
            }),
        }),
    }
    (schema_dir / "scenario.schema.json").write_bytes(canonical_bytes(scenario_schema))
    (schema_dir / "countermodel.schema.json").write_bytes(canonical_bytes(countermodel_schema))


def main() -> int:
    scenario_out = LAB / "fixtures" / "scenarios"
    countermodel_out = LAB / "fixtures" / "countermodels"
    scenario_out.mkdir(parents=True, exist_ok=True)
    countermodel_out.mkdir(parents=True, exist_ok=True)
    for path in list(scenario_out.glob("*.json")) + list(countermodel_out.glob("*.json")):
        path.unlink()

    scenarios = read_jsonl(SCENARIO_SRC)
    scenario_hashes: dict[str, str] = {}
    scenario_statuses: dict[str, str] = {}
    manifest_rows: list[dict[str, Any]] = []
    for source in scenarios:
        flags = {name: bool(source.get("flags", {}).get(name, False)) for name in ALL_FLAGS}
        record = {
            "schema_version": SCHEMA_VERSION,
            "fixture_kind": "scenario",
            "fixture_id": source["scenario_id"],
            "name": source["name"],
            "expected_status": source["expected_status"],
            "flags": flags,
            "assertions": {k: bool(v) for k, v in sorted(source["assertions"].items())},
            "candidate_ids": sorted(source["candidate_ids"]),
            "falsifier": source["falsifier"],
            "structural_record": structural_record(source, flags),
            "source_trace": {
                "source_path": str(SCENARIO_SRC.relative_to(ROOT)),
                "source_id": source["scenario_id"],
                "migration": "LOSSLESS_FLAGS_AND_EXPECTATIONS_PLUS_15_OBJECT_TYPED_ENVELOPE",
            },
        }
        data = canonical_bytes(record)
        out = scenario_out / f"{source['scenario_id']}.json"
        out.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        scenario_hashes[source["scenario_id"]] = digest
        scenario_statuses[source["scenario_id"]] = source["expected_status"]
        manifest_rows.append({"fixture_id": source["scenario_id"], "kind": "scenario", "path": str(out.relative_to(LAB)), "sha256": digest})

    for source in read_jsonl(COUNTERMODEL_SRC):
        sid = source["scenario_id"]
        record = {
            "schema_version": SCHEMA_VERSION,
            "fixture_kind": "countermodel",
            "fixture_id": source["countermodel_id"],
            "name": source["name"],
            "scenario_id": sid,
            "expected_status": scenario_statuses[sid],
            "shows": source["shows"],
            "candidate_ids": sorted(source["candidate_ids"]),
            "escape_route": source["escape_route"],
            "scenario_sha256": scenario_hashes[sid],
            "source_trace": {
                "source_path": str(COUNTERMODEL_SRC.relative_to(ROOT)),
                "source_id": source["countermodel_id"],
                "scenario_source_id": sid,
                "evidence_grade": "FINITE_COUNTERMODEL_FIXTURE_NOT_UNIVERSAL_THEOREM",
            },
        }
        data = canonical_bytes(record)
        out = countermodel_out / f"{source['countermodel_id']}.json"
        out.write_bytes(data)
        manifest_rows.append({"fixture_id": source["countermodel_id"], "kind": "countermodel", "path": str(out.relative_to(LAB)), "sha256": hashlib.sha256(data).hexdigest()})

    write_json_schema()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "scenario_count": len(scenarios),
        "countermodel_count": len(manifest_rows) - len(scenarios),
        "canonicalization": "UTF-8; sorted keys; compact separators; one trailing newline",
        "evidence_grade": "FINITE_REFERENCE_ASSAY_NOT_UNIVERSAL_PROOF",
        "structural_object_sections": 15,
        "fixtures": sorted(manifest_rows, key=lambda row: row["fixture_id"]),
    }
    (LAB / "fixtures" / "manifest.json").write_bytes(canonical_bytes(manifest))
    print(json.dumps({"scenarios": len(scenarios), "countermodels": len(manifest_rows) - len(scenarios), "manifest_sha256": hash_value(manifest)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
