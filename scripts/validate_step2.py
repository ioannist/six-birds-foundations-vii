#!/usr/bin/env python3
"""Validate the Step-2 claim corpus and bridge atlas.

The validator is intentionally source- and type-aware.  It checks not only
row counts, but also explicit TeX-environment coverage, canonical claim-ID
closure, law/no-go reuse contracts, wishlist evidence links, formalization
boundaries, and the absence of Foundations-VII theorem construction.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from step2_common import (  # noqa: E402
    ROOT,
    collect_simple_macros,
    extract_environments,
    find_expanded_path,
    claim_grade_for,
)
from build_step2_claims import (  # noqa: E402
    ABSTRACT_BOUNDARY_PATTERNS,
    extract_abstract_surface,
)

TODAY = "2026-07-26"
EXPECTED_CLAIMS = 2821
EXPECTED_BRIDGES = 374
EXPECTED_PAPERS = 58
EXPECTED_DEPENDENCY_EDGES = 240
EXPECTED_WISHLIST_ATOMS = 130
EXPECTED_APPLICATIONS = 14
EXPECTED_EXAMPLE_CARRIERS = 24
EXPECTED_VERSION_ROWS = 223
EXPECTED_INVALID_TRANSFERS = 20
EXPECTED_FORMAL_ENVIRONMENTS = 1356
EXPECTED_GRAPH_NODES = 3040
EXPECTED_GRAPH_EDGES = 35276
EXPECTED_NAMED_LAW_CANDIDATES = 2022
EXPECTED_NAMED_LAW_ACCEPTED_OCCURRENCES = 217
EXPECTED_NAMED_LAW_PAIRS = 45


class Validation:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, ok: bool, detail: str) -> None:
        self.rows.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    @property
    def passed(self) -> bool:
        return all(r["status"] == "PASS" for r in self.rows)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_list(value: str) -> list[Any]:
    if not value:
        return []
    obj = json.loads(value)
    return obj if isinstance(obj, list) else [obj]


def all_files_exist(paths: Iterable[str]) -> tuple[bool, list[str]]:
    missing = [p for p in paths if not (ROOT / p).exists()]
    return not missing, missing


def main() -> int:
    v = Validation()

    required = [
        "registry/claims.jsonl", "registry/claims.csv",
        "registry/definitions.jsonl", "registry/theorem_claims.jsonl",
        "registry/nonclaims_withdrawals.jsonl", "registry/open_problems.jsonl",
        "registry/examples_carriers.jsonl", "registry/proof_artifact_lean_coverage.jsonl",
        "registry/source_truth_provenance.csv",
        "bridges/bridge_atlas.jsonl", "bridges/paper_invocation_bridges.jsonl",
        "bridges/imported_law_bridges.jsonl", "bridges/law_reuse_contracts.jsonl",
        "bridges/named_law_occurrence_audit.jsonl",
        "bridges/no_go_scope_matrix.jsonl", "bridges/invalid_transfers.csv",
        "formalization/integration/no_go_prior_scaffold_correspondence.jsonl",
        "bridges/unresolved_conflicts.jsonl", "bridges/VF-SAU-01_claim_delta.csv",
        "synthesis/step2/claim_graph_nodes.csv", "synthesis/step2/claim_graph_edges.csv",
        "synthesis/step2/application_pressure_tests.jsonl",
        "wishlists/step2_evidence_links.jsonl",
        "generated/step2_claim_summary.json", "generated/step2_bridge_summary.json",
        "STEP2_REPORT.md", "docs/STEP2_METHOD.md",
        "reports/STEP2_READING_COMPLETENESS.md", "reports/STEP2_FORMALIZATION_REUSE.md",
        "reports/STEP2_REQUIREMENT_AUDIT.csv", "reports/STEP2_REQUIREMENT_AUDIT.md",
    ]
    ok, missing = all_files_exist(required)
    v.check("required Step-2 products exist", ok, "missing=" + ", ".join(missing) if missing else f"{len(required)} required products present")
    if not ok:
        return finish(v)

    catalog = read_csv(ROOT / "config" / "paper_catalog.csv")
    catalog_ids = [r["paper_id"] for r in catalog]
    v.check("paper catalog is complete and unique", len(catalog) == EXPECTED_PAPERS and len(set(catalog_ids)) == EXPECTED_PAPERS,
            f"papers={len(catalog)} unique={len(set(catalog_ids))}")

    claims = read_jsonl(ROOT / "registry" / "claims.jsonl")
    claim_by_id = {c["claim_id"]: c for c in claims}
    by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in claims:
        by_paper[c["source_paper"]].append(c)
    v.check("canonical claim count and ID uniqueness", len(claims) == EXPECTED_CLAIMS and len(claim_by_id) == EXPECTED_CLAIMS,
            f"claims={len(claims)} unique_ids={len(claim_by_id)}")
    v.check("all 58 papers occur in the canonical claim corpus", set(by_paper) == set(catalog_ids),
            f"represented={len(by_paper)} missing={sorted(set(catalog_ids)-set(by_paper))}")

    # Schema validation.
    claim_schema = json.loads((ROOT / "schemas" / "claim_record.schema.json").read_text(encoding="utf-8"))
    schema_errors: list[str] = []
    validator = jsonschema.Draft202012Validator(claim_schema)
    for c in claims:
        errs = list(validator.iter_errors(c))
        if errs:
            schema_errors.append(f"{c.get('claim_id')}: {errs[0].message}")
            if len(schema_errors) >= 20:
                break
    v.check("every claim satisfies the claim-record schema", not schema_errors,
            "no schema errors" if not schema_errors else "; ".join(schema_errors))

    # Stable per-paper sequential IDs and full dossier/per-paper file closure.
    seq_errors: list[str] = []
    dossier_missing: list[str] = []
    dossier_json_errors: list[str] = []
    per_file_mismatch: list[str] = []
    for pid in catalog_ids:
        rows = by_paper.get(pid, [])
        expected = [f"{pid}-C{i:04d}" for i in range(1, len(rows) + 1)]
        actual = [c["claim_id"] for c in rows]
        if actual != expected:
            seq_errors.append(pid)
        dossier_path = ROOT / "notes" / "dossiers" / f"{pid}.md"
        dossier_json_path = ROOT / "notes" / "dossiers" / f"{pid}.json"
        by_path = ROOT / "claims" / "by_paper" / f"{pid}.jsonl"
        if not dossier_path.exists() or not dossier_json_path.exists() or not by_path.exists():
            dossier_missing.append(pid)
            continue
        local = read_jsonl(by_path)
        if [c["claim_id"] for c in local] != actual:
            per_file_mismatch.append(pid)
        dtext = dossier_path.read_text(encoding="utf-8")
        missing_ids = [cid for cid in actual if cid not in dtext]
        if missing_ids:
            dossier_missing.append(f"{pid}:{len(missing_ids)} IDs")
        dossier_json = json.loads(dossier_json_path.read_text(encoding="utf-8"))
        expected_status = "BLOCKED_FULL_TEXT_WITH_ABSTRACT_BRIDGE_AUDIT" if pid == "P039" else "BRIDGED"
        if (dossier_json.get("paper_id") != pid
                or dossier_json.get("claim_count") != len(actual)
                or dossier_json.get("claim_ids") != actual
                or dossier_json.get("status") != expected_status
                or not isinstance(dossier_json.get("bridge_completion"), dict)):
            dossier_json_errors.append(pid)
    v.check("claim IDs are sequential and stable within each paper", not seq_errors,
            "all sequential" if not seq_errors else f"nonsequential={seq_errors}")
    v.check("per-paper JSONL files exactly match the canonical corpus", not per_file_mismatch,
            "all 58 match" if not per_file_mismatch else f"mismatch={per_file_mismatch}")
    v.check("all 58 Markdown dossiers index every canonical claim", not dossier_missing,
            "all dossiers complete" if not dossier_missing else f"incomplete={dossier_missing[:20]}")
    v.check("all 58 canonical dossier JSON files match claim IDs, status, and bridge completion", not dossier_json_errors,
            "all dossier JSON files canonical" if not dossier_json_errors else f"mismatch={dossier_json_errors[:20]}")

    # Source authority, locations, and source hashes.
    source_errors: list[str] = []
    root_hash_cache: dict[str, str] = {}
    metadata_cache: dict[str, dict[str, Any]] = {}
    for c in claims:
        pid = c["source_paper"]
        source_path = ROOT / "source" / c["source_path"]
        expanded_path = ROOT / c["expanded_path"]
        root_path = ROOT / c["source_root"]
        if not source_path.exists() or not expanded_path.exists() or not root_path.exists():
            source_errors.append(f"{c['claim_id']}:missing source/expanded/root")
            continue
        if int(c["source_start_line"]) < 1 or int(c["source_end_line"]) < int(c["source_start_line"]):
            source_errors.append(f"{c['claim_id']}:bad source range")
        if not c.get("source_wording_tex") or not c.get("expanded_source_wording_tex"):
            source_errors.append(f"{c['claim_id']}:missing exact/expanded TeX wording")
        if int(c["expanded_start_line"]) < 1 or int(c["expanded_end_line"]) < int(c["expanded_start_line"]):
            source_errors.append(f"{c['claim_id']}:bad expanded range")
        if str(root_path) not in root_hash_cache:
            root_hash_cache[str(root_path)] = sha256(root_path)
        if root_hash_cache[str(root_path)] != c["source_root_sha256"]:
            source_errors.append(f"{c['claim_id']}:root hash mismatch")
        if pid not in metadata_cache:
            metadata_cache[pid] = json.loads((ROOT / "derived" / "metadata" / f"{pid}.json").read_text(encoding="utf-8"))
        meta = metadata_cache[pid]
        if c["source_root_sha256"] != meta["root_sha256"] or c["source_tree_sha256"] != meta["tree_sha256"]:
            source_errors.append(f"{c['claim_id']}:metadata hash mismatch")
        if len(source_errors) >= 30:
            break
    v.check("claim provenance resolves to immutable source and expanded TeX", not source_errors,
            "all source paths/ranges/hashes resolve" if not source_errors else "; ".join(source_errors))

    # Every cross-claim boundary pointer must resolve in the canonical ID space.
    bad_nonclaim_refs = [
        f"{c['claim_id']}->{cid}"
        for c in claims for cid in (c.get("nonclaims", []) or [])
        if cid not in claim_by_id
    ]
    v.check("all claim-level nonclaim and scope pointers resolve", not bad_nonclaim_refs,
            "all cross-claim boundaries resolve" if not bad_nonclaim_refs else f"bad_refs={bad_nonclaim_refs[:30]}")

    # Every supported explicit theorem-like environment must have one claim.
    formal_claims = [c for c in claims if c.get("review_status") == "SOURCE_EXTRACTED_FORMAL_SURFACE"]
    env_expected: list[tuple[str, int, int, str]] = []
    env_actual = [(c["source_paper"], int(c["expanded_start_line"]), int(c["expanded_end_line"]), c["claim_type"]) for c in formal_claims]
    for row in catalog:
        pid = row["paper_id"]
        meta = metadata_cache.get(pid) or json.loads((ROOT / "derived" / "metadata" / f"{pid}.json").read_text(encoding="utf-8"))
        expanded_path = find_expanded_path(meta)
        raw = expanded_path.read_text(encoding="utf-8", errors="replace")
        dep = json.loads((ROOT / "corpus" / "dependency_trees.json").read_text(encoding="utf-8"))[pid]
        for env in extract_environments(raw, dep["root"], dep["files"]):
            ctype, _ = claim_grade_for(env.env, env.title_tex, env.body_tex)
            env_expected.append((pid, env.expanded_start_line, env.expanded_end_line, ctype))
    v.check("all explicit formal TeX environments are represented exactly once",
            len(env_expected) == EXPECTED_FORMAL_ENVIRONMENTS and Counter(env_expected) == Counter(env_actual),
            f"expected_envs={len(env_expected)} claim_envs={len(env_actual)} unmatched={sum((Counter(env_expected)-Counter(env_actual)).values())} extra={sum((Counter(env_actual)-Counter(env_expected)).values())}")

    lanes = Counter(c["review_status"] for c in claims)
    expected_lanes = {
        "SOURCE_EXTRACTED_FORMAL_SURFACE": 1356,
        "SOURCE_EXTRACTED_EXPLICIT_PROSE_SURFACE": 875,
        "SOURCE_EXTRACTED_NAMED_SECTION_SURFACE": 532,
        "SOURCE_EXTRACTED_COMPOSITE": 58,
    }
    v.check("claim extraction lanes are complete and non-overlapping", dict(lanes) == expected_lanes,
            f"lanes={dict(lanes)}")

    # Every supplied paper must have one composite abstract thesis, including
    # section-form abstracts, and every explicit abstract-only boundary must
    # have one typed component record.  This closes the P023/P033 edge case
    # that ordinary abstract-environment extraction would miss.
    theses = [c for c in claims if c.get("claim_type") == "paper_thesis"]
    thesis_counts = Counter(c["source_paper"] for c in theses)
    v.check("all 58 papers have exactly one source-located composite abstract thesis",
            len(theses) == EXPECTED_PAPERS and set(thesis_counts) == set(catalog_ids) and set(thesis_counts.values()) == {1},
            f"theses={len(theses)} missing={sorted(set(catalog_ids)-set(thesis_counts))} duplicates={[p for p,n in thesis_counts.items() if n != 1]}")

    expected_abstract_components: list[tuple[str, str]] = []
    missing_abstract_surfaces: list[str] = []
    for row in catalog:
        pid = row["paper_id"]
        meta = metadata_cache.get(pid) or json.loads((ROOT / "derived" / "metadata" / f"{pid}.json").read_text(encoding="utf-8"))
        expanded_path = find_expanded_path(meta)
        raw = expanded_path.read_text(encoding="utf-8", errors="replace")
        surface = extract_abstract_surface(raw, collect_simple_macros(raw), meta.get("abstract", ""))
        if not surface:
            missing_abstract_surfaces.append(pid)
            continue
        for kind, pattern in ABSTRACT_BOUNDARY_PATTERNS.items():
            if pattern.search(surface["abstract_plain"]):
                expected_abstract_components.append((pid, kind))
    actual_abstract_components = [
        (c["source_paper"], c["claim_type"])
        for c in claims
        if c.get("source_title_tex") == "Abstract" and c.get("proof_status") == "ABSTRACT_STATUS_BOUNDARY"
    ]
    v.check("all explicit abstract nonclaims, scope boundaries, and open obligations are component records",
            not missing_abstract_surfaces and Counter(expected_abstract_components) == Counter(actual_abstract_components),
            f"expected_components={len(expected_abstract_components)} actual_components={len(actual_abstract_components)} missing_surfaces={missing_abstract_surfaces} missing={list((Counter(expected_abstract_components)-Counter(actual_abstract_components)).elements())[:20]} extra={list((Counter(actual_abstract_components)-Counter(expected_abstract_components)).elements())[:20]}")

    boilerplate_markers = [
        "answerTODO", "justificationTODO", "Code of ethics", "NeurIPS Paper Checklist",
        "Guidelines", "submission checklist", "paper checklist",
    ]
    boilerplate_hits = [(c["claim_id"], marker) for c in claims for marker in boilerplate_markers if marker.lower() in c["normalized_claim"].lower()]
    v.check("boilerplate and checklist text is excluded from claims", not boilerplate_hits,
            "no boilerplate markers" if not boilerplate_hits else f"hits={boilerplate_hits[:20]}")

    # Source-completeness boundary.
    blocked = [c for c in claims if c["source_completeness"].startswith("BLOCKED")]
    p039 = by_paper.get("P039", [])
    v.check("P039 is the sole source-package blocker and remains abstract-only",
            len(blocked) == len(p039) == 2 and {c["source_paper"] for c in blocked} == {"P039"}
            and {c["claim_type"] for c in p039} == {"paper_thesis", "nonclaim"}
            and all(c["expanded_start_line"] == p039[0]["expanded_start_line"] for c in p039),
            f"blocked_claims={len(blocked)} P039_claims={len(p039)}")

    # Coverage progression.
    coverage = read_csv(ROOT / "corpus" / "coverage.csv")
    states = Counter(r["state"] for r in coverage)
    p039_state = next((r["state"] for r in coverage if r["paper_id"] == "P039"), None)
    v.check("coverage has advanced to 57 BRIDGED papers with P039 blocked", states == Counter({"BRIDGED": 57, "BLOCKED": 1}) and p039_state == "BLOCKED",
            f"states={dict(states)} P039={p039_state}")

    # Formalization posture and Lean scope.
    allowed_formal = {
        "MATCHED_IMPORTED_LAW_DECLARATION",
        "MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION",
        "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "PLAUSIBLE_IMPORTED_MATCH_REQUIRES_STATEMENT_REVIEW",
        "PAPER_DISCLOSED_ASSET_NOT_IMPORTED",
        "NO_MATCH",
    }
    bad_formal: list[str] = []
    for c in claims:
        f = c.get("formalization") or {}
        if f.get("status") not in allowed_formal:
            bad_formal.append(f"{c['claim_id']}:status={f.get('status')}")
        if f.get("status") in {
            "MATCHED_IMPORTED_LAW_DECLARATION",
            "MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION",
            "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        } and (not f.get("modules") or not f.get("declarations")):
            bad_formal.append(f"{c['claim_id']}:matched-or-corresponding-without-module/declaration")
        elaboration = str(f.get("elaboration_status", ""))
        if re.search(r"LOCAL_(?:KERNEL|LEAN).*PASS|KERNEL_VERIFIED|ELABORATED_SUCCESSFULLY", elaboration, re.I):
            bad_formal.append(f"{c['claim_id']}:overclaimed-elaboration={elaboration}")
    v.check("claim-level formalization status preserves statement and kernel boundaries", not bad_formal,
            "all formalization records conservative" if not bad_formal else "; ".join(bad_formal[:30]))

    lean_diff = subprocess.run(
        ["git", "diff", "--name-only", "read-step-01-complete-formal-spine", "--", "formalization/lean"],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    v.check("Step 2 introduces no Foundations VII Lean declarations or Lean-source changes", lean_diff.returncode == 0 and not lean_diff.stdout.strip(),
            "formalization/lean unchanged from Step 1" if not lean_diff.stdout.strip() else lean_diff.stdout.strip())

    # Law/no-go source claims and full reuse contracts.
    F = read_csv(ROOT / "registry" / "F_laws.csv")
    E = read_csv(ROOT / "registry" / "E_laws.csv")
    G = read_csv(ROOT / "registry" / "G_laws.csv")
    NG = read_csv(ROOT / "registry" / "no_go_theorems.csv")
    law_ids = {r["law_id"] for r in F + E + G}
    ng_ids = {r["law_id"] for r in NG}
    claim_law_ids = {c.get("law_id") for c in claims if c.get("law_id")}
    claim_ng_ids = {c.get("no_go_id") for c in claims if c.get("no_go_id")}
    v.check("all 52 F, 16 E, 13 G and 8 no-go rows resolve to canonical claims",
            len(F) == 52 and len(E) == 16 and len(G) == 13 and len(NG) == 8 and law_ids <= claim_law_ids and ng_ids == claim_ng_ids,
            f"registry={len(F)}/{len(E)}/{len(G)}/{len(NG)} resolved_laws={len(law_ids & claim_law_ids)} resolved_ng={len(claim_ng_ids)}")

    bridges = read_jsonl(ROOT / "bridges" / "bridge_atlas.jsonl")
    bridge_by_id = {b["bridge_id"]: b for b in bridges}
    v.check("bridge atlas count and IDs are canonical", len(bridges) == EXPECTED_BRIDGES and len(bridge_by_id) == EXPECTED_BRIDGES,
            f"bridges={len(bridges)} unique_ids={len(bridge_by_id)}")

    bridge_schema = json.loads((ROOT / "schemas" / "bridge_record.schema.json").read_text(encoding="utf-8"))
    bvalidator = jsonschema.Draft202012Validator(bridge_schema)
    bridge_schema_errors: list[str] = []
    bridge_ref_errors: list[str] = []
    allowed_class = {
        "ANALOGY_ONLY_OR_DOMAIN_MAP_REQUIRED", "AVAILABLE_AFTER_EXACT_HYPOTHESIS_AND_STATEMENT_MATCH",
        "BLOCKED_SOURCE", "EXACT_INHERITED_INSTANCE_CLAIMED_BY_TARGET",
        "PARTIAL_BRIDGE_REQUIRES_DOMAIN_MAP", "PARTIAL_BRIDGE_SCOPE_INHERITANCE_REQUIRED",
        "SOURCE_RESULT_AVAILABLE_FORMAL_MATCH_REQUIRES_AUDIT", "UNKNOWN_REQUIRES_PROOF",
        "VALID_AFTER_ADDED_HYPOTHESES", "PAPER_RESULT_AVAILABLE_LOCAL_FORMAL_ASSET_ABSENT_OR_PARTIAL",
    }
    for b in bridges:
        errs = list(bvalidator.iter_errors(b))
        if errs:
            bridge_schema_errors.append(f"{b.get('bridge_id')}:{errs[0].message}")
        if b.get("source_claim") not in claim_by_id:
            bridge_ref_errors.append(f"{b['bridge_id']}:bad source {b.get('source_claim')}")
        target = b.get("target_claim_or_context")
        if b.get("bridge_kind") != "PRIOR_LAW_REUSE_CONTRACT" and target not in claim_by_id:
            bridge_ref_errors.append(f"{b['bridge_id']}:bad target {target}")
        if b.get("classification") not in allowed_class:
            bridge_ref_errors.append(f"{b['bridge_id']}:bad class {b.get('classification')}")
        if not b.get("audit_path") or not b.get("source_of_truth"):
            bridge_ref_errors.append(f"{b['bridge_id']}:missing audit/source truth")
    v.check("every bridge satisfies the bridge schema", not bridge_schema_errors,
            "no schema errors" if not bridge_schema_errors else "; ".join(bridge_schema_errors[:20]))
    v.check("bridge claim references, classes, and audit paths close", not bridge_ref_errors,
            "all bridge references valid" if not bridge_ref_errors else "; ".join(bridge_ref_errors[:30]))

    # Citation bridges equal Step-1 dependency edges.
    dep_edges = read_csv(ROOT / "corpus" / "paper_dependency_edges.csv")
    citation = read_jsonl(ROOT / "bridges" / "paper_invocation_bridges.jsonl")
    citation_sigs = {
        (b["target_paper"], b["source_paper"], tuple(sorted(b.get("citation_keys", [])))) for b in citation
    }
    dep_sigs = {
        (e["source_paper_id"], e["target_paper_id"], tuple(sorted(x for x in e["citation_keys"].split(";") if x))) for e in dep_edges
    }
    v.check("all 240 in-corpus paper invocations have a bridge row", len(dep_edges) == EXPECTED_DEPENDENCY_EDGES and len(citation) == EXPECTED_DEPENDENCY_EDGES and citation_sigs == dep_sigs,
            f"dependency_edges={len(dep_edges)} citation_bridges={len(citation)} signature_delta={len(citation_sigs ^ dep_sigs)}")

    # Every accepted source-level named-law occurrence is covered exactly once
    # by a grouped paper/law bridge.  The claim-level `imported_laws` field is
    # intentionally recall-oriented and is not the precision-controlling set.
    imported = read_jsonl(ROOT / "bridges" / "imported_law_bridges.jsonl")
    occurrence_audit = read_jsonl(ROOT / "bridges" / "named_law_occurrence_audit.jsonl")
    accepted_occurrences = [r for r in occurrence_audit if r.get("decision") == "ACCEPTED_NAMED_PRIOR_LAW_INVOCATION"]
    accepted_ids = {r["occurrence_id"] for r in accepted_occurrences}
    covered_ids = [oid for b in imported for oid in b.get("occurrence_ids", [])]
    accepted_pairs = {(r["target_paper"], r["law_id"]) for r in accepted_occurrences}
    bridge_pairs = {(b["target_paper"], b["source_law"]) for b in imported}
    audit_errors = [
        r.get("occurrence_id", "<missing>") for r in occurrence_audit
        if not r.get("source_path") or not r.get("source_line") or not r.get("decision_basis")
        or r.get("target_claim") not in claim_by_id
        or (r.get("decision") == "ACCEPTED_NAMED_PRIOR_LAW_INVOCATION" and r.get("law_id") not in law_ids)
    ]
    false_pairs = {
        ("P005", "F2"), ("P005", "F3"), ("P040", "G2"), ("P058", "G2"),
        ("P052", "E1"), ("P052", "E2"), ("P010", "E2"),
    }
    v.check("named-law source audit is complete and rejects known local-label collisions",
            len(occurrence_audit) == EXPECTED_NAMED_LAW_CANDIDATES
            and len(accepted_occurrences) == EXPECTED_NAMED_LAW_ACCEPTED_OCCURRENCES
            and len(accepted_pairs) == EXPECTED_NAMED_LAW_PAIRS
            and not audit_errors and not (false_pairs & bridge_pairs),
            f"candidates={len(occurrence_audit)} accepted_occurrences={len(accepted_occurrences)} accepted_pairs={len(accepted_pairs)} audit_errors={audit_errors[:10]} false_bridges={sorted(false_pairs & bridge_pairs)}")
    v.check("every accepted named prior-law occurrence has exactly one grouped bridge",
            len(imported) == EXPECTED_NAMED_LAW_PAIRS and accepted_pairs == bridge_pairs
            and set(covered_ids) == accepted_ids and len(covered_ids) == len(set(covered_ids)),
            f"accepted_occurrences={len(accepted_ids)} grouped_bridges={len(imported)} pair_delta={len(accepted_pairs ^ bridge_pairs)} coverage_delta={len(accepted_ids ^ set(covered_ids))}")

    reuse = read_jsonl(ROOT / "bridges" / "law_reuse_contracts.jsonl")
    reuse_ids = {b["source_law"] for b in reuse}
    v.check("all prior F/E/G/no-go rows have a future-reuse contract", len(reuse) == 89 and reuse_ids == law_ids | ng_ids,
            f"contracts={len(reuse)} expected_ids={len(law_ids | ng_ids)} missing={sorted((law_ids|ng_ids)-reuse_ids)}")

    # No-go matrix exact scope and escape obligations.
    no_go = read_jsonl(ROOT / "bridges" / "no_go_scope_matrix.jsonl")
    no_go_errors: list[str] = []
    for r in no_go:
        if r.get("no_go_id") not in ng_ids or r.get("source_claim") not in claim_by_id:
            no_go_errors.append(f"{r.get('no_go_id')}:bad id/ref")
        for field in ("carrier", "hypotheses", "conclusion", "source_statement_tex", "expanded_statement_tex", "rules_out", "does_not_rule_out", "escape_route"):
            if not r.get(field):
                no_go_errors.append(f"{r.get('no_go_id')}:missing {field}")
    v.check("all eight no-go results retain exact statements, carrier, hypotheses, scope, non-scope, and escape", len(no_go) == 8 and {r["no_go_id"] for r in no_go} == ng_ids and not no_go_errors,
            f"rows={len(no_go)} errors={no_go_errors}")

    no_go_corr = read_jsonl(ROOT / "formalization" / "integration" / "no_go_prior_scaffold_correspondence.jsonl")
    expected_corr = {
        "NG_ARROW_DPI": "NO_MATCH",
        "NG_PROTOCOL_TRAP": "NO_MATCH",
        "NG_FORCE_FOREST": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "NG_FORCE_NULL": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "NG_MACRO_CLOSURE_DEFICIT": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "NG_LADDER_IDEM": "MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION",
        "NG_LADDER_BOUNDED_INTERFACE": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "NG_OBJECT_CONTRACTIVE": "PAPER_DISCLOSED_ASSET_NOT_IMPORTED",
    }
    corr_errors: list[str] = []
    for r in no_go_corr:
        nid = r.get("no_go_id")
        if expected_corr.get(nid) != r.get("correspondence_status") or r.get("source_claim") not in claim_by_id:
            corr_errors.append(f"{nid}:status/ref")
        if r.get("correspondence_status") in {
            "MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION",
            "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        } and (not r.get("prior_modules") or not r.get("prior_declarations")):
            corr_errors.append(f"{nid}:missing module/declaration")
    v.check("no-go results are conservatively aligned to the inherited Lean scaffold", len(no_go_corr) == 8 and {r.get("no_go_id") for r in no_go_corr} == set(expected_corr) and not corr_errors,
            f"rows={len(no_go_corr)} errors={corr_errors}")

    # Invalid-transfer guardrails.
    invalid = read_csv(ROOT / "bridges" / "invalid_transfers.csv")
    collapses = "\n".join(r["forbidden_collapse"].lower() for r in invalid)
    required_fragments = [
        "generic transition", "generic path", "semantics", "p3 holonomy", "strict extension",
        "common source", "shared origin", "structural downward", "enablement", "soundness",
        "reachability", "occurrence",
    ]
    v.check("invalid-transfer report covers recurrent SBT role collapses", len(invalid) == EXPECTED_INVALID_TRANSFERS and all(x in collapses for x in required_fragments),
            f"rows={len(invalid)} missing_fragments={[x for x in required_fragments if x not in collapses]}")

    # Taxonomy matrices.
    taxonomy_expected = {
        "access_state_matrix.csv": 8,
        "access_exposure_recoverability_adequacy_matrix.csv": 6,
        "admission_kind_matrix.csv": 8,
        "soundness_reachability_occurrence_matrix.csv": 5,
        "contact_join_status_matrix.csv": 9,
        "origin_quotient_instrument_commitment_refinement_matrix.csv": 7,
        "parent_child_retention_absorption_matrix.csv": 6,
        "retention_absorption_matrix.csv": 5,
        "enablement_attribution_matrix.csv": 7,
        "enablement_birth_class_matrix.csv": 7,
        "interaction_order_confluence_holonomy_matrix.csv": 7,
        "order_holonomy_matrix.csv": 7,
        "cost_budget_observer_refund_matrix.csv": 8,
        "currency_budget_matrix.csv": 7,
    }
    tax_errors: list[str] = []
    for name, count in taxonomy_expected.items():
        path = ROOT / "synthesis" / "step2" / name
        if not path.exists():
            tax_errors.append(f"{name}:missing")
        else:
            n = len(read_csv(path))
            if n != count:
                tax_errors.append(f"{name}:{n}!={count}")
    v.check("interaction/access/enablement taxonomy is complete", not tax_errors,
            f"{len(taxonomy_expected)} matrices verified" if not tax_errors else "; ".join(tax_errors))

    # Application pressure tests and example/carrier registry.
    apps = read_jsonl(ROOT / "synthesis" / "step2" / "application_pressure_tests.jsonl")
    app_ids = {r["paper_id"] for r in apps}
    app_errors: list[str] = []
    for r in apps:
        if not r.get("concrete_carrier") or not r.get("interface_or_lens") or not r.get("audit_or_certificate") or not r.get("forbidden_back_transfer"):
            app_errors.append(r["paper_id"])
        for cid in r.get("principal_claims", []) + r.get("nonclaims_or_open_boundaries", []):
            if cid not in claim_by_id:
                app_errors.append(f"{r['paper_id']}:{cid}")
    p039_app = next((r for r in apps if r["paper_id"] == "P039"), {})
    v.check("all 14 domain applications have concrete carrier/interface/audit maps or a source block", len(apps) == EXPECTED_APPLICATIONS and len(app_ids) == EXPECTED_APPLICATIONS and not app_errors and p039_app.get("bridge_classification") == "BLOCKED_SOURCE",
            f"applications={len(apps)} errors={app_errors} P039={p039_app.get('bridge_classification')}")

    carriers = read_jsonl(ROOT / "registry" / "examples_carriers.jsonl")
    carrier_errors = [r["record_id"] for r in carriers if r.get("source_claim") not in claim_by_id or not r.get("carrier_or_model") or not r.get("nonclaim_or_boundary")]
    carrier_kinds = Counter(r["record_kind"] for r in carriers)
    v.check("example/carrier registry is populated and source-grounded", len(carriers) == EXPECTED_EXAMPLE_CARRIERS and not carrier_errors and carrier_kinds == Counter({"APPLICATION_PRESSURE_CARRIER": 14, "SOURCE_NAMED_EXAMPLE_OR_MODEL": 10}),
            f"rows={len(carriers)} kinds={dict(carrier_kinds)} errors={carrier_errors}")

    # Wishlist links.
    wish = read_jsonl(ROOT / "wishlists" / "step2_evidence_links.jsonl")
    wish_errors: list[str] = []
    for r in wish:
        support = r.get("supporting_claim_ids", [])
        bounds = r.get("counterclaim_or_boundary_ids", [])
        opens = r.get("open_problem_ids", [])
        if not support and not bounds:
            wish_errors.append(f"{r['request_id']}:no evidence")
        for cid in support + bounds + opens:
            if cid not in claim_by_id:
                wish_errors.append(f"{r['request_id']}:bad claim {cid}")
        for bid in r.get("linked_bridge_ids", []):
            if bid not in bridge_by_id:
                wish_errors.append(f"{r['request_id']}:bad bridge {bid}")
        for lid in r.get("linked_law_or_no_go_ids", []):
            if lid not in law_ids | ng_ids:
                wish_errors.append(f"{r['request_id']}:bad law {lid}")
    v.check("all 130 wishlist atoms link to source claims, boundaries, and bridge obligations", len(wish) == EXPECTED_WISHLIST_ATOMS and len({r["request_id"] for r in wish}) == EXPECTED_WISHLIST_ATOMS and not wish_errors,
            f"atoms={len(wish)} errors={wish_errors[:20]}")

    # Version family and conflicts.
    delta = read_csv(ROOT / "bridges" / "VF-SAU-01_claim_delta.csv")
    delta_errors = [
        r for r in delta
        if (not r.get("p040_claim") and not r.get("p058_claim"))
        or (r.get("p040_claim") and r["p040_claim"] not in claim_by_id)
        or (r.get("p058_claim") and r["p058_claim"] not in claim_by_id)
    ]
    conflicts = read_jsonl(ROOT / "bridges" / "unresolved_conflicts.jsonl")
    version_conflict = next((r for r in conflicts if r["conflict_id"] == "CF-01"), None)
    v.check("P040/P058 claim-level delta is complete and non-independent",
            len(delta) == EXPECTED_VERSION_ROWS and not delta_errors and version_conflict is not None and "NON_INDEPENDENT" in version_conflict.get("status", "") and "do not select" in version_conflict.get("safe_ruling", "").lower(),
            f"delta_rows={len(delta)} bad_refs={len(delta_errors)} conflict_status={version_conflict.get('status') if version_conflict else None}")
    conflict_errors = [r["conflict_id"] for r in conflicts if not r.get("source_grounding") or not r.get("safe_ruling") or not r.get("status")]
    v.check("all unresolved conflicts are typed and source-grounded", len(conflicts) == 6 and not conflict_errors,
            f"conflicts={len(conflicts)} errors={conflict_errors}")

    # Graph closure.
    nodes = read_csv(ROOT / "synthesis" / "step2" / "claim_graph_nodes.csv")
    edges = read_csv(ROOT / "synthesis" / "step2" / "claim_graph_edges.csv")
    node_ids = {r["node_id"] for r in nodes}
    graph_bad = [r["edge_id"] for r in edges if r["source"] not in node_ids or r["target"] not in node_ids]
    lexical_law_edges = [r["edge_id"] for r in edges if r.get("edge_type") == "IMPORTS_NAMED_LAW"]
    v.check("claim/dependency graph is closed and excludes unaudited lexical law edges", len(nodes) == EXPECTED_GRAPH_NODES and len(edges) == EXPECTED_GRAPH_EDGES and not graph_bad and not lexical_law_edges and set(claim_by_id) <= node_ids,
            f"nodes={len(nodes)} edges={len(edges)} bad_endpoints={len(graph_bad)} lexical_law_edges={len(lexical_law_edges)}")

    # Summary consistency and stale-prototype exclusion.
    claim_summary = json.loads((ROOT / "generated" / "step2_claim_summary.json").read_text(encoding="utf-8"))
    bridge_summary = json.loads((ROOT / "generated" / "step2_bridge_summary.json").read_text(encoding="utf-8"))
    v.check("generated summaries match canonical artifacts",
            claim_summary.get("claims") == len(claims)
            and bridge_summary.get("canonical_claims") == len(claims)
            and bridge_summary.get("total_bridge_rows") == len(bridges)
            and bridge_summary.get("example_carrier_rows") == len(carriers)
            and bridge_summary.get("graph_nodes") == len(nodes)
            and bridge_summary.get("graph_edges") == len(edges)
            and bridge_summary.get("named_law_candidate_occurrences") == len(occurrence_audit)
            and bridge_summary.get("named_law_accepted_occurrences") == len(accepted_occurrences),
            f"claim_summary={claim_summary.get('claims')} bridge_summary={bridge_summary.get('total_bridge_rows')} carriers={bridge_summary.get('example_carrier_rows')} graph={bridge_summary.get('graph_nodes')}/{bridge_summary.get('graph_edges')}")

    requirement_rows = read_csv(ROOT / "reports" / "STEP2_REQUIREMENT_AUDIT.csv")
    requirement_errors: list[str] = []
    expected_requirement_ids = {f"S2-R{i:02d}" for i in range(1, 17)}
    actual_requirement_ids = {r.get("requirement_id", "") for r in requirement_rows}
    for r in requirement_rows:
        status = r.get("status", "")
        if not status.startswith("PASS") or "FAIL" in status:
            requirement_errors.append(f"{r.get('requirement_id')}:status={status}")
        for field in ("plan_requirement", "evidence", "finding", "limitation"):
            if not r.get(field, "").strip():
                requirement_errors.append(f"{r.get('requirement_id')}:{field}=empty")
    v.check("Step-2 requirement audit closes every planned delivery obligation",
            len(requirement_rows) == 16 and actual_requirement_ids == expected_requirement_ids and not requirement_errors,
            f"rows={len(requirement_rows)} ids={len(actual_requirement_ids)} errors={requirement_errors}")

    stale = [
        "bridges/citation_context_bridges.csv",
        "generated/step2_claim_corpus_summary.json",
        "corpus/step2_paper_census.csv",
        "registry/step2",
        "generated/step2",
        "notes/claim_dossiers",
        "bridges/NO_GO_SCOPE_MATRIX.md",
    ]
    stale_present = [p for p in stale if (ROOT / p).exists()]
    report_text = (ROOT / "reports" / "step2" / "BUILD_REPORT.md").read_text(encoding="utf-8") if (ROOT / "reports" / "step2" / "BUILD_REPORT.md").exists() else ""
    v.check("obsolete competing-ID/prototype outputs are absent", not stale_present and "3235" not in report_text and "3,235" not in report_text,
            "no stale prototype outputs" if not stale_present else f"stale={stale_present}")

    # Step 3 must remain untouched.
    forbidden_step3 = [
        "synthesis/step3", "reports/step3", "notes/readiness_dossiers",
        "registry/candidate_vii_laws.jsonl", "formalization/lean/FoundationsVII/CandidateLaws.lean",
    ]
    step3_present = [p for p in forbidden_step3 if (ROOT / p).exists()]
    v.check("Step 3 has not started", not step3_present and bridge_summary.get("step3_started") is False,
            "no Step-3 artifacts" if not step3_present else f"present={step3_present}")

    return finish(v)


def finish(v: Validation) -> int:
    summary = {
        "date": TODAY,
        "status": "PASS" if v.passed else "FAIL",
        "checks": len(v.rows),
        "passed": sum(r["status"] == "PASS" for r in v.rows),
        "failed": sum(r["status"] == "FAIL" for r in v.rows),
        "results": v.rows,
    }
    generated = ROOT / "generated"
    reports = ROOT / "reports"
    generated.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)
    (generated / "step2_validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        "# Step-2 validation", "",
        f"- **Status:** `{summary['status']}`.",
        f"- **Checks:** {summary['checks']} total; {summary['passed']} passed; {summary['failed']} failed.",
        f"- **Date:** {TODAY}.", "",
        "| Check | Status | Detail |", "|---|---|---|",
    ]
    for r in v.rows:
        detail = str(r["detail"]).replace("|", "\\|").replace("\n", " ")
        md.append(f"| {r['check']} | `{r['status']}` | {detail} |")
    (reports / "STEP2_VALIDATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if v.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
