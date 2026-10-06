#!/usr/bin/env python3
"""Validate the Foundations VII Step-3 pre-authoring readiness dossier.

The gate checks source closure, typed references, finite assays, prior-proof
reuse, explicit nonclaims, and the stage boundary.  It deliberately does not
claim that any Foundations VII candidate has been proved or kernel checked.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE_TAG = "read-step-02"

EXPECTED = {
    "papers": 58,
    "claims": 2821,
    "bridges": 374,
    "scope": 30,
    "objects": 18,
    "candidates": 36,
    "wishlist": 130,
    "scenarios": 24,
    "countermodels": 27,
    "no_gos": 11,
    "formal_targets": 20,
    "reuse_links": 30,
    "chapters": 12,
    "red_lines": 30,
    "decisions": 15,
    "source_trace": 3166,
    "graph_nodes": 1851,
    "graph_edges": 5969,
    "assertions": 29,
}


class Validation:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, ok: bool, detail: str) -> None:
        self.rows.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def schema_errors(data_path: Path, schema_path: Path) -> list[str]:
    schema = read_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[str] = []
    for i, row in enumerate(read_jsonl(data_path), 1):
        row_errors = list(validator.iter_errors(row))
        if row_errors:
            err = row_errors[0]
            errors.append(f"row {i} path={list(err.path)}: {err.message}")
            if len(errors) >= 20:
                break
    return errors


def is_acyclic(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> bool:
    node_set = set(nodes)
    outgoing: dict[str, set[str]] = {n: set() for n in node_set}
    indegree = {n: 0 for n in node_set}
    for source, target in edges:
        if source not in node_set or target not in node_set:
            return False
        if target not in outgoing[source]:
            outgoing[source].add(target)
            indegree[target] += 1
    queue = deque(sorted(n for n, degree in indegree.items() if degree == 0))
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for target in sorted(outgoing[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    return seen == len(node_set)


def contains_all_topics(rows: list[dict[str, Any]], field: str, topic_groups: dict[str, tuple[str, ...]]) -> tuple[bool, list[str]]:
    corpus = "\n".join(str(row.get(field, "")) for row in rows).lower()
    missing = [name for name, words in topic_groups.items() if not all(word.lower() in corpus for word in words)]
    return not missing, missing


def main() -> int:
    v = Validation()

    required = [
        "STEP3_REPORT.md", "docs/STEP3_METHOD.md", "docs/PLAN.md", "docs/REPO_CONTRACT.md",
        "docs/ACCEPTANCE_GATES.md", "reports/STEP3_READING_COMPLETENESS.md",
        "reports/STEP3_FORMALIZATION_READINESS.md", "reports/STEP3_REQUIREMENT_AUDIT.csv",
        "readiness/READINESS_DOSSIER.md", "readiness/CLAIMABLE_BOUNDARY.md",
        "readiness/SCOPE_INHERITANCE.md", "readiness/OBJECT_MODEL.md",
        "readiness/CANDIDATE_INDEX.md", "readiness/COUNTERMODEL_ATLAS.md",
        "readiness/NO_GO_PROGRAM.md", "readiness/CHAPTER_DAG.md", "readiness/RED_LINES.md",
        "readiness/DECISION_POINTS.md", "readiness/PAPER_REREAD_MATRIX.md",
        "readiness/candidate_index.jsonl", "readiness/object_model.jsonl",
        "readiness/scope_inheritance.jsonl", "readiness/countermodel_atlas.jsonl",
        "readiness/no_go_program.jsonl", "readiness/chapter_dag.jsonl",
        "readiness/red_lines.jsonl", "readiness/decision_points.jsonl",
        "readiness/paper_reread_matrix.jsonl", "readiness/candidate_source_trace.jsonl",
        "readiness/candidate_dependency_nodes.csv", "readiness/candidate_dependency_edges.csv",
        "readiness/candidate_dependency_graph.graphml",
        "readiness/two_theory_world/SPECIFICATION.md",
        "readiness/two_theory_world/scenarios.jsonl",
        "readiness/two_theory_world/reference_model_results.jsonl",
        "readiness/two_theory_world/REFERENCE_MODEL_RESULTS.md",
        "formalization/step3/formalization_targets.jsonl",
        "formalization/step3/prior_reuse_matrix.jsonl",
        "formalization/step3/FORMALIZATION_TARGETS.md",
        "wishlists/step3_adjudication.jsonl", "wishlists/WISHLIST_ADJUDICATION_STEP3.md",
        "generated/step3_summary.json", "generated/step3_reference_model_results.json",
        "schemas/vii_candidate.schema.json", "schemas/vii_object.schema.json",
        "schemas/countermodel.schema.json", "schemas/wishlist_adjudication.schema.json",
        "scripts/build_step3_readiness.py", "scripts/step3_reference_model.py",
        "scripts/rebuild_step3.sh", "scripts/validate_step3.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    v.check("required Step-3 products exist", not missing,
            f"{len(required)} products present" if not missing else f"missing={missing}")
    if missing:
        return finish(v)

    claims = read_jsonl(ROOT / "registry/claims.jsonl")
    bridges = read_jsonl(ROOT / "bridges/bridge_atlas.jsonl")
    claim_by = {row["claim_id"]: row for row in claims}
    bridge_by = {row["bridge_id"]: row for row in bridges}
    catalog = read_csv(ROOT / "config/paper_catalog.csv")
    papers = {row["paper_id"] for row in catalog}
    atoms = read_jsonl(ROOT / "wishlists/atomic_requests.jsonl")
    atom_ids = {row["request_id"] for row in atoms}
    groups = read_csv(ROOT / "wishlists/convergence_groups.csv")
    group_ids = {row["convergence_group"] for row in groups}

    candidates = read_jsonl(ROOT / "readiness/candidate_index.jsonl")
    objects = read_jsonl(ROOT / "readiness/object_model.jsonl")
    scope = read_jsonl(ROOT / "readiness/scope_inheritance.jsonl")
    adjud = read_jsonl(ROOT / "wishlists/step3_adjudication.jsonl")
    scenarios = read_jsonl(ROOT / "readiness/two_theory_world/scenarios.jsonl")
    results = read_jsonl(ROOT / "readiness/two_theory_world/reference_model_results.jsonl")
    cms = read_jsonl(ROOT / "readiness/countermodel_atlas.jsonl")
    nogos = read_jsonl(ROOT / "readiness/no_go_program.jsonl")
    formal = read_jsonl(ROOT / "formalization/step3/formalization_targets.jsonl")
    reuse = read_jsonl(ROOT / "formalization/step3/prior_reuse_matrix.jsonl")
    chapters = read_jsonl(ROOT / "readiness/chapter_dag.jsonl")
    red_lines = read_jsonl(ROOT / "readiness/red_lines.jsonl")
    decisions = read_jsonl(ROOT / "readiness/decision_points.jsonl")
    rereads = read_jsonl(ROOT / "readiness/paper_reread_matrix.jsonl")
    traces = read_jsonl(ROOT / "readiness/candidate_source_trace.jsonl")
    graph_nodes = read_csv(ROOT / "readiness/candidate_dependency_nodes.csv")
    graph_edges = read_csv(ROOT / "readiness/candidate_dependency_edges.csv")
    summary = read_json(ROOT / "generated/step3_summary.json")
    ref_summary = read_json(ROOT / "generated/step3_reference_model_results.json")

    v.check("Step-2 claim corpus remains complete", len(claims) == EXPECTED["claims"] and len(claim_by) == len(claims),
            f"claims={len(claims)} unique={len(claim_by)}")
    v.check("Step-2 bridge atlas remains complete", len(bridges) == EXPECTED["bridges"] and len(bridge_by) == len(bridges),
            f"bridges={len(bridges)} unique={len(bridge_by)}")
    v.check("all 58 paper roots remain represented", len(papers) == EXPECTED["papers"] and {c["source_paper"] for c in claims} == papers,
            f"catalog={len(papers)} claim_papers={len({c['source_paper'] for c in claims})}")

    count_checks = [
        ("scope-inheritance groups", len(scope), "scope"),
        ("minimal object records", len(objects), "objects"),
        ("candidate dossiers", len(candidates), "candidates"),
        ("wishlist adjudications", len(adjud), "wishlist"),
        ("finite reference scenarios", len(scenarios), "scenarios"),
        ("countermodels", len(cms), "countermodels"),
        ("candidate no-go fronts", len(nogos), "no_gos"),
        ("formalization targets", len(formal), "formal_targets"),
        ("exact prior-declaration reuse links", len(reuse), "reuse_links"),
        ("chapter nodes", len(chapters), "chapters"),
        ("red lines", len(red_lines), "red_lines"),
        ("decision points", len(decisions), "decisions"),
        ("candidate/source trace rows", len(traces), "source_trace"),
        ("dependency graph nodes", len(graph_nodes), "graph_nodes"),
        ("dependency graph edges", len(graph_edges), "graph_edges"),
    ]
    for label, actual, key in count_checks:
        v.check(f"expected {label}", actual == EXPECTED[key], f"actual={actual} expected={EXPECTED[key]}")

    # JSON-schema gates.
    schema_jobs = [
        ("candidate dossiers satisfy schema", ROOT / "readiness/candidate_index.jsonl", ROOT / "schemas/vii_candidate.schema.json"),
        ("object records satisfy schema", ROOT / "readiness/object_model.jsonl", ROOT / "schemas/vii_object.schema.json"),
        ("countermodels satisfy schema", ROOT / "readiness/countermodel_atlas.jsonl", ROOT / "schemas/countermodel.schema.json"),
        ("wishlist adjudications satisfy schema", ROOT / "wishlists/step3_adjudication.jsonl", ROOT / "schemas/wishlist_adjudication.schema.json"),
    ]
    for label, data_path, schema_path in schema_jobs:
        errors = schema_errors(data_path, schema_path)
        v.check(label, not errors, "no schema errors" if not errors else "; ".join(errors))

    candidate_ids = {row["candidate_id"] for row in candidates}
    object_ids = {row["object_id"] for row in objects}
    scenario_ids = {row["scenario_id"] for row in scenarios}
    cm_ids = {row["countermodel_id"] for row in cms}
    ft_ids = {row["target_id"] for row in formal}
    chapter_ids = {row["chapter_id"] for row in chapters}
    no_go_ids = {row["no_go_id"] for row in nogos}
    expected_candidate_ids = {f"VII-C{i:03d}" for i in range(1, EXPECTED["candidates"] + 1)}
    v.check("candidate IDs are complete and unique", candidate_ids == expected_candidate_ids,
            f"unique={len(candidate_ids)} missing={sorted(expected_candidate_ids-candidate_ids)}")

    bad_candidate_refs: list[str] = []
    for c in candidates:
        checks = [
            ("object", set(c["typed_objects"]), object_ids),
            ("scenario", set(c["positive_model"] + c["null_models"]), scenario_ids),
            ("countermodel", set(c["countermodels"]), cm_ids),
            ("formal target", set(c["formalization_targets"]), ft_ids),
            ("chapter", {c["recommended_chapter"]}, chapter_ids),
            ("convergence group", set(c["convergence_groups"]), group_ids),
            ("wishlist atom", set(c["wishlist_atoms"]), atom_ids),
        ]
        for kind, used, allowed in checks:
            extra = used - allowed
            if extra:
                bad_candidate_refs.append(f"{c['candidate_id']} {kind}: {sorted(extra)}")
    v.check("candidate references close over all typed registries", not bad_candidate_refs,
            "all references close" if not bad_candidate_refs else "; ".join(bad_candidate_refs[:20]))

    missing_candidate_contract = [
        c["candidate_id"] for c in candidates
        if not c["typed_objects"] or not c["proof_obligations"] or not c["positive_model"]
        or not c["null_models"] or not c["countermodels"] or not c["formalization_targets"]
        or not all(c.get("detector", {}).get(k) for k in ("signal", "null", "falsifier"))
        or c.get("step3_ruling") != "READINESS_ONLY_NO_NEW_THEOREM_ASSERTED"
        or not c.get("nonclaims")
    ]
    v.check("every candidate has typing, proof, detector, model, countermodel, formalization, and nonclaim obligations",
            not missing_candidate_contract,
            "all 36 complete" if not missing_candidate_contract else f"incomplete={missing_candidate_contract}")

    # Exact source trace and prior-reference closure.
    law_ids: set[str] = set()
    for name in ("F_laws", "E_laws", "G_laws", "no_go_theorems"):
        for row in read_jsonl(ROOT / f"registry/{name}.jsonl"):
            law_ids.add(row.get("law_id") or row.get("no_go_id") or row.get("id"))
    trace_errors: list[str] = []
    for row in traces:
        claim = claim_by.get(row["claim_id"])
        if not claim:
            trace_errors.append(f"missing claim {row['claim_id']}")
            continue
        if row["candidate_id"] not in candidate_ids:
            trace_errors.append(f"missing candidate {row['candidate_id']}")
        for key in ("source_paper", "source_location", "claim_grade"):
            if row.get(key) != claim.get(key):
                trace_errors.append(f"{row['candidate_id']}/{row['claim_id']} {key} mismatch")
    for c in candidates:
        st = c["source_trace"]
        if not st["resolved_source_locations"]:
            trace_errors.append(f"{c['candidate_id']} no source trace")
        trace_claims = {x["claim_id"] for x in st["resolved_source_locations"]}
        if not trace_claims <= set(claim_by):
            trace_errors.append(f"{c['candidate_id']} unknown trace claims")
        if not set(st["bridge_ids"]) <= set(bridge_by):
            trace_errors.append(f"{c['candidate_id']} unknown bridges")
        if not set(st["law_or_no_go_ids"]) <= law_ids:
            trace_errors.append(f"{c['candidate_id']} unknown laws/no-gos")
    v.check("candidate/source traces resolve exactly to Step-2 claims, bridges, and laws", not trace_errors,
            "all source dependencies resolve" if not trace_errors else "; ".join(trace_errors[:20]))

    # Object dependency graph.
    object_edges = [(parent, row["object_id"]) for row in objects for parent in row["defined_from"]]
    object_ref_errors = [(a, b) for a, b in object_edges if a not in object_ids or b not in object_ids]
    v.check("minimal object model is closed and acyclic", not object_ref_errors and is_acyclic(object_ids, object_edges),
            f"objects={len(object_ids)} definition_edges={len(object_edges)} bad={object_ref_errors[:10]}")

    # Wishlist closure.
    adjud_ids = [row["request_id"] for row in adjud]
    statuses = Counter(row["final_status"] for row in adjud)
    bad_adjud_refs = [
        row["request_id"] for row in adjud
        if not set(row["candidate_ids"]) <= candidate_ids
        or not set(row["supporting_claim_ids"] + row["boundary_claim_ids"] + row["open_problem_ids"]) <= set(claim_by)
        or not set(row["bridge_ids"]) <= set(bridge_by)
        or not row["rationale"] or not row["scope_modifier"] or not row["acceptance_or_red_line"]
    ]
    v.check("all 130 wishlist atoms are adjudicated exactly once", len(adjud_ids) == len(set(adjud_ids)) == EXPECTED["wishlist"] and set(adjud_ids) == atom_ids,
            f"rows={len(adjud_ids)} unique={len(set(adjud_ids))} source_atoms={len(atom_ids)}")
    v.check("wishlist adjudication uses all seven final dispositions", len(statuses) == 7 and min(statuses.values()) > 0,
            f"statuses={dict(sorted(statuses.items()))}")
    v.check("wishlist evidence and candidate references are closed", not bad_adjud_refs,
            "all references and rationales present" if not bad_adjud_refs else f"bad={bad_adjud_refs[:20]}")

    # Finite reference assay.
    result_by = {row["scenario_id"]: row for row in results}
    assertion_count = sum(len(row.get("assertions", {})) for row in scenarios)
    v.check("reference evaluator covers every declared scenario", len(result_by) == EXPECTED["scenarios"] and set(result_by) == scenario_ids,
            f"results={len(result_by)} scenarios={len(scenario_ids)}")
    v.check("all scenario statuses and assertions pass", ref_summary.get("all_pass") is True
            and ref_summary.get("scenario_count") == EXPECTED["scenarios"]
            and ref_summary.get("status_matches") == EXPECTED["scenarios"]
            and ref_summary.get("assertion_count") == EXPECTED["assertions"] == assertion_count
            and ref_summary.get("assertions_passing") == EXPECTED["assertions"]
            and all(row.get("all_pass") for row in results),
            f"summary={ref_summary}")
    required_statuses = {
        "BOOTSTRAP_BLOCKED", "PROSPECTIVE_ADMISSION", "STRICT_JOIN", "CONTACT_WITHOUT_JOIN",
        "CERTIFIED_NONINTERACTION", "HOLONOMY_ZERO_ARROW", "DRIVEN_ARROW", "SOUND_UNREACHABLE",
        "REACHABLE_NONOCCURRENT", "OCCURRENT_EVENT", "UNPRICED_OBSERVER",
        "UNLICENSED_TOTALITY_TRANSFER", "REFINEMENT_DESTROYS_JOIN",
    }
    present_statuses = {row["expected_status"] for row in scenarios}
    v.check("finite assay includes all required positive, null, obstruction, arrow, observer, and reachability controls",
            required_statuses <= present_statuses,
            f"statuses={len(present_statuses)} missing={sorted(required_statuses-present_statuses)}")

    # Countermodels and scoped no-gos.
    bad_cm_refs = [row["countermodel_id"] for row in cms if row["scenario_id"] not in scenario_ids or not set(row["candidate_ids"]) <= candidate_ids]
    cm_topics = {
        "source/access": ("source", "access"),
        "contact/join": ("contact", "join"),
        "enablement/descent": ("enablement", "descent"),
        "sound/reachable": ("sound", "reach"),
        "reachable/occurrence": ("reachable", "occur"),
        "holonomy/arrow": ("holonomy", "arrow"),
        "observer occupancy": ("observer", "occup"),
        "total/partial": ("total", "partial"),
    }
    cm_text = [{"text": f"{row['name']} {row['shows']}"} for row in cms]
    cm_ok, cm_missing = contains_all_topics(cm_text, "text", cm_topics)
    v.check("countermodel atlas references close and covers all required non-implications", not bad_cm_refs and cm_ok,
            f"bad_refs={bad_cm_refs[:10]} missing_topics={cm_missing}")
    bad_nogo_refs = [row["no_go_id"] for row in nogos if not set(row["candidate_ids"]) <= candidate_ids or row["failure_scenario"] not in scenario_ids or row["escape_or_positive_scenario"] not in scenario_ids]
    v.check("candidate no-go program is scoped and has failure/escape assays", not bad_nogo_refs and all("NOT_YET_PROVED" in row["conclusion_grade"] and row["nonclaims"] for row in nogos),
            "all 11 are scoped candidate no-gos" if not bad_nogo_refs else f"bad={bad_nogo_refs}")

    # Formalization reuse and stage boundary.
    lean_rows = read_csv(ROOT / "formalization/integration/cumulative_lean_declarations.csv")
    lean_by = {row["fully_qualified_name"]: row for row in lean_rows}
    bad_formal_refs = [
        f"{row['target_id']}:{decl}" for row in formal for decl in row["prior_declarations"] if decl not in lean_by
    ]
    reuse_names = {row["fully_qualified_name"] for row in reuse}
    all_declared_reuse = {decl for row in formal for decl in row["prior_declarations"]}
    v.check("all Step-3 formal targets name exact inherited Lean declarations", not bad_formal_refs and reuse_names == all_declared_reuse,
            f"exact_declarations={len(reuse_names)} bad={bad_formal_refs[:20]}")
    v.check("formal-target candidate references close", all(set(row["candidate_ids"]) <= candidate_ids for row in formal),
            f"targets={len(formal)}")
    foundations_vii_decls = [row for row in lean_rows if row.get("fully_qualified_name", "").startswith("FoundationsVII.") or row.get("namespace", "").startswith("FoundationsVII")]
    v.check("inherited formal spine still contains zero Foundations VII declarations", not foundations_vii_decls,
            f"foundations_vii_declarations={len(foundations_vii_decls)}")

    lean_diff = git("diff", "--name-only", BASE_TAG, "--", "*.lean")
    lean_untracked = git("ls-files", "--others", "--exclude-standard", "--", "*.lean")
    tex_diff = git("diff", "--name-only", BASE_TAG, "--", "*.tex")
    tex_untracked = git("ls-files", "--others", "--exclude-standard", "--", "*.tex")
    v.check("Step 3 adds or modifies no Lean source", lean_diff.returncode == 0 and not lean_diff.stdout.strip() and not lean_untracked.stdout.strip(),
            f"tracked_diff={lean_diff.stdout.strip() or 'none'} untracked={lean_untracked.stdout.strip() or 'none'}")
    v.check("Step 3 adds or modifies no paper TeX source", tex_diff.returncode == 0 and not tex_diff.stdout.strip() and not tex_untracked.stdout.strip(),
            f"tracked_diff={tex_diff.stdout.strip() or 'none'} untracked={tex_untracked.stdout.strip() or 'none'}")

    # Chapter/DAG and complete assignment.
    chapter_edges = [(dep, row["chapter_id"]) for row in chapters for dep in row["depends_on"]]
    assigned = [cid for row in chapters for cid in row["candidate_ids"]]
    v.check("chapter dependency graph is closed and acyclic", is_acyclic(chapter_ids, chapter_edges),
            f"chapters={len(chapter_ids)} edges={len(chapter_edges)}")
    v.check("every candidate is assigned to exactly one later chapter", Counter(assigned) == Counter({cid: 1 for cid in candidate_ids}),
            f"assignments={len(assigned)} unique={len(set(assigned))}")

    red_topics = {
        "contact not join": ("contact", "join"),
        "source not access": ("source", "access"),
        "enablement not descent": ("enablement", "descent"),
        "holonomy not arrow": ("holonomy", "directionality"),
        "reachability not occurrence": ("reachability", "occurrence"),
        "total lens": ("total-lens", "partial"),
        "observer occupancy": ("observer", "occupancy"),
        "P039": ("p039", "missing"),
        "P040/P058": ("p040", "p058"),
        "Lean replay": ("lean", "4.28.0"),
        "categorical deferral": ("categorical", "universal"),
        "primitive algebra": ("generators-and-relations", "algebra"),
    }
    red_ok, red_missing = contains_all_topics(red_lines, "rule", red_topics)
    v.check("red-line register preserves all required anti-overread boundaries", red_ok,
            "all required boundaries present" if red_ok else f"missing={red_missing}")

    decision_topics = {
        "categorical": ("categorical",),
        "source": ("source",),
        "time": ("time",),
        "observer/contact degree": ("contact degree", "observer"),
        "version family": ("p040", "p058"),
        "P039": ("p039",),
        "primitive algebra": ("primitive", "relations"),
    }
    decision_ok, decision_missing = contains_all_topics(decisions, "question", decision_topics)
    v.check("decision register exposes the remaining foundational choices", decision_ok,
            "all decision classes present" if decision_ok else f"missing={decision_missing}")

    # Paper reread and version/source boundaries.
    reread_by = {row["paper_id"]: row for row in rereads}
    reread_ref_errors = [
        row["paper_id"] for row in rereads
        if row["paper_id"] not in papers
        or not set(row["relevant_claim_ids"] + row["boundary_claim_ids"] + row["open_problem_ids"]) <= set(claim_by)
        or any(claim_by[cid]["source_paper"] != row["paper_id"] for cid in row["relevant_claim_ids"] + row["boundary_claim_ids"] + row["open_problem_ids"])
        or not set(row["candidate_ids"]) <= candidate_ids
    ]
    v.check("all 58 paper rereads are source-local and candidate-linked", len(reread_by) == EXPECTED["papers"] and not reread_ref_errors,
            f"rereads={len(reread_by)} bad={reread_ref_errors[:20]}")
    p039 = reread_by.get("P039", {})
    p040 = reread_by.get("P040", {})
    p058 = reread_by.get("P058", {})
    v.check("P039 remains abstract-only and body-level blocked", "ABSTRACT_ONLY" in p039.get("source_status", "") and p039.get("all_claims_reconsidered") == 2,
            f"status={p039.get('source_status')} claims={p039.get('all_claims_reconsidered')}")
    v.check("P040/P058 remain one unresolved non-independent family", p040.get("version_family_ruling") == p058.get("version_family_ruling") == "UNRESOLVED_NONINDEPENDENT_VF-SAU-01",
            f"P040={p040.get('version_family_ruling')} P058={p058.get('version_family_ruling')}")

    # Graph closure.
    node_ids = [row["node_id"] for row in graph_nodes]
    node_set = set(node_ids)
    bad_edges = [row for row in graph_edges if row["source"] not in node_set or row["target"] not in node_set]
    v.check("candidate dependency graph IDs are unique and every edge closes", len(node_ids) == len(node_set) and not bad_edges,
            f"nodes={len(node_ids)} unique={len(node_set)} bad_edges={len(bad_edges)}")

    # Protect immutable/canonical Step-2 bodies.
    protected = [
        "claims", "registry", "bridges", "source", "synthesis/step2",
        "formalization/foundations_v_scaffold", "formalization/foundations_vi_scaffold",
        "formalization/integration", "formalization/lean",
    ]
    protected_diff = git("diff", "--name-only", BASE_TAG, "--", *protected)
    protected_untracked = git("ls-files", "--others", "--exclude-standard", "--", *protected)
    v.check("canonical Step-2 claims, bridges, sources, synthesis, and inherited formalization are unchanged",
            protected_diff.returncode == 0 and not protected_diff.stdout.strip() and not protected_untracked.stdout.strip(),
            f"tracked_diff={protected_diff.stdout.strip() or 'none'} untracked={protected_untracked.stdout.strip() or 'none'}")

    # Stage summary, coverage, prose boundary, and script syntax.
    expected_summary_fields = {
        "papers_reread": EXPECTED["papers"], "scope_groups": EXPECTED["scope"],
        "object_model_records": EXPECTED["objects"], "candidate_dossiers": EXPECTED["candidates"],
        "wishlist_atoms_adjudicated": EXPECTED["wishlist"], "finite_scenarios": EXPECTED["scenarios"],
        "countermodels": EXPECTED["countermodels"], "candidate_no_gos": EXPECTED["no_gos"],
        "formalization_targets": EXPECTED["formal_targets"], "prior_lean_declaration_reuse_links": EXPECTED["reuse_links"],
        "chapters": EXPECTED["chapters"], "red_lines": EXPECTED["red_lines"],
        "decision_points": EXPECTED["decisions"], "candidate_source_trace_rows": EXPECTED["source_trace"],
        "candidate_dependency_nodes": EXPECTED["graph_nodes"], "candidate_dependency_edges": EXPECTED["graph_edges"],
        "new_foundations_vii_lean_declarations": 0,
    }
    summary_bad = {key: (summary.get(key), expected) for key, expected in expected_summary_fields.items() if summary.get(key) != expected}
    v.check("Step-3 summary matches the rebuilt repositories", not summary_bad and summary.get("stage") == "STEP3_READINESS_COMPLETE_NO_PAPER_DRAFT" and summary.get("critical_blockers") == [],
            f"mismatches={summary_bad or 'none'} stage={summary.get('stage')} blockers={summary.get('critical_blockers')}")

    coverage = read_csv(ROOT / "corpus/coverage.csv")
    state_counts = Counter(row["state"] for row in coverage)
    v.check("paper coverage closes at 57 CLOSED plus P039 BLOCKED", len(coverage) == EXPECTED["papers"] and state_counts == Counter({"CLOSED": 57, "BLOCKED": 1}) and next(row for row in coverage if row["paper_id"] == "P039")["state"] == "BLOCKED",
            f"states={dict(state_counts)}")

    boundary_text = "\n".join((ROOT / path).read_text(encoding="utf-8").lower() for path in [
        "README.md", "STEP3_REPORT.md", "readiness/READINESS_DOSSIER.md", "readiness/CLAIMABLE_BOUNDARY.md"
    ])
    v.check("repository explicitly marks Step 3 as readiness, not theorem proof or paper drafting",
            "not a paper draft" in boundary_text and "not a proof" in boundary_text and "step 3" in boundary_text,
            "stage boundary statements present")

    compile_errors: list[str] = []
    for path in sorted((ROOT / "scripts").glob("*step3*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            compile_errors.append(f"{path.name}:{exc}")
    v.check("all Step-3 Python programs compile", not compile_errors,
            "all compile" if not compile_errors else "; ".join(compile_errors))

    return finish(v)


def finish(v: Validation) -> int:
    out_json = ROOT / "generated" / "step3_validation.json"
    out_txt = ROOT / "generated" / "step3_validation.txt"
    report = ROOT / "reports" / "STEP3_VALIDATION.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": "STEP3_READINESS_EXIT_GATE",
        "passed": v.passed,
        "check_count": len(v.rows),
        "pass_count": sum(row["status"] == "PASS" for row in v.rows),
        "fail_count": sum(row["status"] == "FAIL" for row in v.rows),
        "checks": v.rows,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [f"{'PASS' if v.passed else 'FAIL'} — {payload['pass_count']}/{payload['check_count']} checks passed"]
    lines.extend(f"[{row['status']}] {row['check']}: {row['detail']}" for row in v.rows)
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    md = [
        "# Step 3 validation",
        "",
        f"**Overall:** {'PASS' if v.passed else 'FAIL'} — {payload['pass_count']}/{payload['check_count']} checks passed.",
        "",
        "This gate validates the readiness dossier and its stage boundaries. It does not promote any candidate to theorem grade and does not claim fresh Lean kernel verification.",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for row in v.rows:
        detail = row["detail"].replace("|", "\\|").replace("\n", " ")
        md.append(f"| {row['check']} | {row['status']} | {detail} |")
    report.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out_txt.read_text(encoding="utf-8"), end="")
    return 0 if v.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
