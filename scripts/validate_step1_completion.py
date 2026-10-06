#!/usr/bin/env python3
"""Validate the formalization-aware completion of Step 1.

The validator explicitly rejects Step-2 work in this pass.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks: list[tuple[str, str, str]] = []


def ok(name: str, detail: str) -> None:
    checks.append(("PASS", name, detail))


def fail(name: str, detail: str) -> None:
    checks.append(("FAIL", name, detail))


def info(name: str, detail: str) -> None:
    checks.append(("INFO", name, detail))


def rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


required = [
    "reports/STEP1_REQUIREMENT_AUDIT.md",
    "reports/STEP1_REQUIREMENT_AUDIT.csv",
    "reports/FORMALIZATION_AWARE_FOUNDATIONS_AUDIT.md",
    "reports/P040_P058_SECTION_DELTA.md",
    "reports/P040_P058_SECTION_DELTA.csv",
    "reports/P040_P058_LINE_DELTA.md",
    "reports/P040_P058_LINE_DELTA.csv",
    "reports/P040_P058_RAW_TEX_DIFF.patch",
    "generated/p040_p058_line_delta.json",
    "reports/SURVEY_ARTIFACT_FORMALIZATION_AUDIT.md",
    "corpus/survey_artifact_formalization.csv",
    "reports/PAPER_DEPENDENCY_RECONNAISSANCE.md",
    "corpus/paper_dependency_edges.csv",
    "corpus/paper_dependency_summary.csv",
    "corpus/paper_citation_key_audit.csv",
    "generated/paper_dependency_reconnaissance.json",
    "synthesis/FORMALIZATION_EVIDENCE_LADDER.md",
    "formalization/integration/foundations_spine_formalization_coverage.csv",
    "formalization/integration/FOUNDATIONS_SPINE_FORMALIZATION_COVERAGE.md",
    "formalization/integration/f_law_formalization_disclosure.csv",
    "formalization/integration/e_law_formalization_disclosure.csv",
    "formalization/integration/g_law_formalization_disclosure.csv",
    "generated/step1_formal_completion_summary.json",
]
missing = [rel for rel in required if not (ROOT / rel).is_file()]
if missing:
    fail("required-artifacts", f"missing={missing}")
else:
    ok("required-artifacts", f"{len(required)} formal-aware artifacts present")

spine = rows("formalization/integration/foundations_spine_formalization_coverage.csv")
expected_spine = {"P031", "P027", "P026", "P028", "P030", "P029", "P032"}
if len(spine) == 7 and {row["paper_id"] for row in spine} == expected_spine:
    ok("spine-coverage", "seven canonical/no-go papers reconciled")
else:
    fail("spine-coverage", f"rows={len(spine)} ids={sorted(row.get('paper_id', '') for row in spine)}")

spine_by_id = {row["paper_id"]: row for row in spine}
if (
    "no claim" in spine_by_id["P027"]["paper_reported_fidelity"].lower()
    and "harness" in spine_by_id["P027"]["paper_reported_scope"].lower()
    and "1261" in spine_by_id["P030"]["local_assets"]
    and "e16" in spine_by_id["P030"]["trust_or_fidelity_boundary"].lower()
    and "no dedicated no-go" in spine_by_id["P032"]["local_assets"].lower()
):
    ok("load-bearing-fidelity", "P027 typed-harness, complete P030 theorem base with E16 repair, and P032 narrow formalization are explicit")
else:
    fail("load-bearing-fidelity", "one or more formal-scope corrections missing")

f = rows("formalization/integration/f_law_formalization_disclosure.csv")
f_status = Counter(row["paper_formalization_status"] for row in f)
f_local = {row["law_id"] for row in f if row["local_import_status"] == "IMPORTED_SUBSET_MODULE"}
expected_f_local = {"F2", "F3", "F4", "F6", "F7", "F10", "F11", "F12", "F13a", "F19", "F27", "F34", "F40", "F49"}
expected_f_status = Counter({"direct theorem row": 46, "substrate-delegated anchor": 2, "partial theorem wrapper": 2, "obligation-guarded wrapper": 2})
if len(f) == 52 and f_status == expected_f_status and f_local == expected_f_local:
    ok("f-disclosure", "52 paper rows separated from exact 14-row local subset")
else:
    fail("f-disclosure", f"rows={len(f)} statuses={dict(f_status)} local={sorted(f_local)}")
f4 = next((row for row in f if row["law_id"] == "F4"), {})
if "finite" in f4.get("caveat", "").lower() and "abstract" in f4.get("caveat", "").lower():
    ok("f4-statement-delta", "paper finiteness versus local abstract-family caveat retained")
else:
    fail("f4-statement-delta", f4.get("caveat", "missing"))

e = rows("formalization/integration/e_law_formalization_disclosure.csv")
if (
    len(e) == 16
    and {row["law_id"] for row in e} == {f"E{i}" for i in range(1, 17)}
    and all(row["paper_lean_status"] == "full core" for row in e)
    and Counter(row["local_import_status"] for row in e)
    == Counter({"PRESENT_DEDICATED_MODULE": 13, "PRESENT_SHARED_MODULE": 2, "PRESENT_MODULE_WITH_VII_ROOT_COMPLETION": 1})
    and all(row["local_verification_state"] == "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED" for row in e)
):
    ok("e-disclosure", "16 paper-reported full-core rows; all local E laws present with shared-module and E16-wrapper distinctions")
else:
    fail("e-disclosure", f"rows={len(e)} local={Counter(row.get('local_import_status', '') for row in e)}")
if "unformalized" in next(row for row in e if row["law_id"] == "E7")["paper_certified_or_open_boundary"].lower() and "open" in next(row for row in e if row["law_id"] == "E12")["paper_certified_or_open_boundary"].lower():
    ok("e-open-boundaries", "E7.1/E12.1 and open bridges remain visible")
else:
    fail("e-open-boundaries", "interpretive/open E boundaries missing")

g = rows("formalization/integration/g_law_formalization_disclosure.csv")
g_reg = {row["law_id"]: row for row in rows("registry/G_laws.csv")}
expected_g_grades = {
    "G1": "theorem (Part a) / schema (Part b)",
    "G2": "theorem",
    "G3": "theorem",
    "G4": "schema",
    "G5": "calibration-anchored schema",
    "G6": "schema",
    "G7": "calibration-anchored schema",
    "G8": "theorem",
    "G9": "calibration-anchored schema",
    "G10": "theorem",
    "G11": "theorem",
    "G12": "theorem",
    "G13": "schema",
}
if len(g) == 13 and all(g_reg[k]["paper_grade"] == v for k, v in expected_g_grades.items()) and all(row["local_import_status"] == "IMPORTED_COMPLETE_G_SERIES" for row in g):
    ok("g-grades-and-locality", "all 13 G grades preserved and all 13 modules locally supplied")
else:
    fail("g-grades-and-locality", f"rows={len(g)} grades={ {k:g_reg.get(k,{}).get('paper_grade') for k in expected_g_grades} }")

ladder = (ROOT / "synthesis" / "FORMALIZATION_EVIDENCE_LADDER.md").read_text(encoding="utf-8")
ladder_markers = ["R0_PAPER_REPORTED", "R1_ASSET_PRESENT", "R2_STATIC_INDEXED", "R3_IMPORT_RESOLVED", "R4_KERNEL_COMPILED", "R5_RUNTIME_VALIDATED", "TYPED_MIRROR", "DIRECT_DERIVATION"]
missing_markers = [x for x in ladder_markers if x not in ladder]
if not missing_markers and "not reached in the current environment" in ladder:
    ok("evidence-ladder", "paper grade, fidelity, local asset, kernel, and runtime states separated")
else:
    fail("evidence-ladder", f"missing={missing_markers}")

deep_dir = ROOT / "notes" / "deep_formalization"
deep = sorted(deep_dir.glob("P*.md"))
if len(deep) == 7 and {p.stem for p in deep} == expected_spine and all("VII reuse boundary" in p.read_text(encoding="utf-8") for p in deep):
    ok("formal-rereads", "seven formalization-aware Step-1 deep supplements present")
else:
    fail("formal-rereads", f"files={[p.name for p in deep]}")

survey_disclosure = rows("corpus/survey_artifact_formalization.csv")
survey_cards = sorted((ROOT / "notes" / "survey").glob("P*.md"))
by_pid_disclosure = {row["paper_id"]: row for row in survey_disclosure}
expected_papers = {f"P{i:03d}" for i in range(1, 59)}
required_survey_sections = {
    "## Provenance and reading status",
    "## Problem and thesis",
    "## Core objects and definitions located",
    "## Principal result inventory",
    "## Claim/evidence class visible at survey depth",
    "## Artifact and formalization disclosure",
    "## Assumptions, scope, and nonclaims",
    "## Open questions / deferred work",
    "## Corpus-paper dependencies visible at survey depth",
    "## Foundations VII relevance",
    "## Source map",
    "## Reader uncertainties and Step-2 revisit",
}
missing_card_sections = []
for path in survey_cards:
    card_sections = set(re.findall(r"^## .+$", path.read_text(encoding="utf-8"), flags=re.M))
    missing = sorted(required_survey_sections - card_sections)
    if missing:
        missing_card_sections.append(f"{path.stem}:{'|'.join(missing)}")
if (
    len(survey_disclosure) == 58
    and set(by_pid_disclosure) == expected_papers
    and len(survey_cards) == 58
    and not missing_card_sections
    and all(row.get("formalization_status") and row.get("artifact_status") and row.get("finding") for row in survey_disclosure)
):
    ok("all-paper-disclosure-audit", "58/58 cards carry all 12 planned survey fields plus source-located artifact/formalization status and anti-overread boundary")
else:
    fail(
        "all-paper-disclosure-audit",
        f"rows={len(survey_disclosure)} ids={len(set(by_pid_disclosure))} cards={len(survey_cards)} missing_sections={missing_card_sections}",
    )
if (
    by_pid_disclosure.get("P003", {}).get("formalization_status") == "CONDITIONAL_LEAN_SCHEMAS_EMPIRICAL_PREMISES_EXTERNAL"
    and by_pid_disclosure.get("P013", {}).get("formalization_status") == "FINITE_RECOMPUTATION_EXPLICITLY_NOT_PROOF_ASSISTANT"
    and by_pid_disclosure.get("P034", {}).get("formalization_status") == "IN_HOUSE_LEAN_LADDER_PLUS_CONDITIONAL_EXTERNAL_CONTRACT"
    and by_pid_disclosure.get("P038", {}).get("artifact_status") == "SUPPORTING_COMPUTATIONAL_AND_AUDIT_EVIDENCE_ONLY"
    and by_pid_disclosure.get("P039", {}).get("formalization_status") == "SOURCE_PACKAGE_BLOCKED"
):
    ok("survey-disclosure-boundaries", "load-bearing paper-specific artifact/formalization boundaries retained")
else:
    fail("survey-disclosure-boundaries", "one or more high-risk survey disclosure classifications changed")

# Original Step-1 cards promised dependency papers.  This pass supplies a
# citation/navigation graph without crossing into Step-2 theorem bridges.
dep_summary = rows("corpus/paper_dependency_summary.csv")
dep_edges = rows("corpus/paper_dependency_edges.csv")
citation_audit = rows("corpus/paper_citation_key_audit.csv")
dep_by_pid = {row["source_paper_id"]: row for row in dep_summary}
missing_dependency_sections = [
    path.stem for path in survey_cards
    if "## Corpus-paper dependencies visible at survey depth" not in path.read_text(encoding="utf-8")
]
edge_pairs = [(row["source_paper_id"], row["target_paper_id"]) for row in dep_edges]
if (
    len(dep_summary) == 58
    and set(dep_by_pid) == expected_papers
    and len(dep_edges) == 240
    and len(set(edge_pairs)) == len(edge_pairs)
    and all(src in expected_papers and dst in expected_papers and src != dst for src, dst in edge_pairs)
    and not missing_dependency_sections
    and all(row["inference_boundary"] == "CITATION_NAVIGATION_ONLY_NOT_THEOREM_DEPENDENCY_OR_BRIDGE_ADJUDICATION" for row in dep_summary)
    and all("NO_THEOREM_INHERITANCE" in row["inference_boundary"] for row in dep_edges)
):
    ok("paper-dependency-reconnaissance", "58/58 cards; 240 unique source-located in-corpus citation edges; no self edges; Step-2 inference boundary explicit")
else:
    fail(
        "paper-dependency-reconnaissance",
        f"summary={len(dep_summary)} edges={len(dep_edges)} pairs={len(set(edge_pairs))} missing_sections={missing_dependency_sections}",
    )

status_counts = Counter(row["status"] for row in dep_summary)
unresolved_count = sum(int(row["unresolved_internal_key_count"]) for row in dep_summary)
out_of_corpus_papers = sum(int(row["out_of_corpus_key_count"]) > 0 for row in dep_summary)
classification_counts = Counter(row["classification"] for row in citation_audit)
if (
    status_counts == Counter({
        "RESOLVED_IN_CORPUS_REFERENCES": 53,
        "NO_IN_CORPUS_REFERENCE_RESOLVED_AT_SURVEY_DEPTH": 4,
        "SOURCE_PACKAGE_BLOCKED": 1,
    })
    and unresolved_count == 2
    and out_of_corpus_papers == 5
    and classification_counts["UNRESOLVED_INTERNAL"] == 2
    and classification_counts["OUT_OF_CORPUS"] == 7
    and dep_by_pid["P039"]["status"] == "SOURCE_PACKAGE_BLOCKED"
):
    ok("paper-dependency-limitations", "two unresolved internal keys, seven out-of-corpus key uses across five papers, and P039 source block are explicit")
else:
    fail(
        "paper-dependency-limitations",
        f"statuses={dict(status_counts)} unresolved={unresolved_count} out_papers={out_of_corpus_papers} classes={dict(classification_counts)}",
    )

wish = rows("wishlists/atomic_requests.csv")
allowed = {"existing", "partially existing", "new", "blocked by no-go", "needs countermodel", "unclear"}
used = Counter(row.get("prior_coverage_status", "") for row in wish)
if len(wish) == 130 and set(used).issubset(allowed) and "" not in used and sum(used.values()) == 130:
    ok("wishlist-required-classification", f"130 atoms classified with exact vocabulary: {dict(used)}")
else:
    fail("wishlist-required-classification", f"rows={len(wish)} used={dict(used)}")
if sum(row.get("countermodel_requirement") == "YES" for row in wish) == used["needs countermodel"]:
    ok("wishlist-countermodels", f"{used['needs countermodel']} explicit countermodel obligations")
else:
    fail("wishlist-countermodels", "classification/flag mismatch")

version = rows("reports/P040_P058_SECTION_DELTA.csv")
relations = Counter(row["heading_relation"] for row in version)
if len(version) == 73 and not relations["STRUCTURE_MISMATCH"] and relations["IDENTICAL_HEADING"] == 64 and relations["RENAMED_HEADING"] == 9:
    ok("version-section-delta", "P040/P058 aligned across 73 slots: 64 identical headings, 9 renamed")
else:
    fail("version-section-delta", f"rows={len(version)} relations={dict(relations)}")
line_delta = rows("reports/P040_P058_LINE_DELTA.csv")
line_summary = json.loads((ROOT / "generated" / "p040_p058_line_delta.json").read_text(encoding="utf-8"))
line_ops = Counter(row["operation"] for row in line_delta)
patch_lines = (ROOT / "reports" / "P040_P058_RAW_TEX_DIFF.patch").read_text(encoding="utf-8").splitlines()
if (
    len(line_delta) == 505
    and line_ops == Counter({"EQUAL": 253, "REPLACE": 221, "DELETE": 18, "INSERT": 13})
    and line_summary["p040_line_count"] == 5775
    and line_summary["p058_line_count"] == 5758
    and line_summary["changed_p040_lines"] == 994
    and line_summary["changed_p058_lines"] == 977
    and line_summary["canonical_member"] is None
    and line_summary["step2_started"] is False
    and len(patch_lines) == 3240
    and all(row["status"] == "RAW_TEX_ALIGNMENT_ONLY" for row in line_delta)
):
    ok("version-line-delta", "P040/P058 exact raw-TeX control: 505 alignment blocks and 3,240-line unified diff; no canonical member selected")
else:
    fail("version-line-delta", f"rows={len(line_delta)} ops={dict(line_ops)} summary={line_summary} patch_lines={len(patch_lines)}")
families = rows("corpus/version_families.csv")
if len(families) == 1 and families[0]["status"] == "UNRESOLVED_VERSION_FAMILY" and not families[0]["canonical_member"]:
    ok("version-nonpromotion", "section reconciliation does not pre-empt Step-2 claim canonicalization")
else:
    fail("version-nonpromotion", str(families))

coverage = rows("corpus/coverage.csv")
states = Counter(row["state"] for row in coverage)
step2_states = {"CLAIM_EXTRACTED", "BRIDGED", "VII_ADJUDICATED", "CLOSED"}
if len(coverage) == 58 and states == Counter({"SURVEYED": 38, "DEEP_READ": 20}) and not step2_states.intersection(states):
    ok("step2-not-started", "coverage remains 20 DEEP_READ / 38 SURVEYED")
else:
    fail("step2-not-started", f"states={dict(states)}")
forbidden_record_roots = [ROOT / "claims", ROOT / "bridges", ROOT / "records" / "claims", ROOT / "records" / "bridges"]
created = [str(path.relative_to(ROOT)) for path in forbidden_record_roots if path.exists()]
if not created:
    ok("no-step2-records", "no claim or bridge record corpus created")
else:
    fail("no-step2-records", f"unexpected={created}")

# Conservative lexical check: active VII files may contain imports/comments only.
active_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "formalization" / "lean").rglob("*.lean"))
active_no_comments = re.sub(r"/-.*?-/", " ", active_text, flags=re.S)
active_no_comments = re.sub(r"--.*$", " ", active_no_comments, flags=re.M)
decl = re.findall(r"(?m)^\s*(?:noncomputable\s+|private\s+|protected\s+)*(def|theorem|lemma|structure|inductive|class|axiom|opaque|instance|abbrev)\s+", active_no_comments)
if not decl:
    ok("zero-vii-declarations", "active VII Lean shell still contains imports only")
else:
    fail("zero-vii-declarations", f"declaration kinds={decl}")

exceptions = {row["paper_id"]: row for row in rows("corpus/source_exceptions.csv")}
if exceptions.get("P039", {}).get("blocking_status") == "BLOCKED_FULL_TEXT" and exceptions.get("P020", {}).get("blocking_status") == "NOT_BLOCKING_STEP1":
    ok("source-limitations", "P039 block and P020 recovery remain explicit")
else:
    fail("source-limitations", str(exceptions))

req = rows("reports/STEP1_REQUIREMENT_AUDIT.csv")
if len(req) == 15 and all(not row["status"].startswith("FAIL") for row in req):
    ok("requirement-audit", "15 Step-1 contract rows carry no failure status")
else:
    fail("requirement-audit", f"rows={len(req)} failures={[row for row in req if row.get('status','').startswith('FAIL')]}")

synthesis = (ROOT / "synthesis" / "SBT_STEP1_SYNTHESIS.md").read_text(encoding="utf-8")
if (
    "## 11. Formalization-aware authority rule" in synthesis
    and "Foundations V supplies the complete local D1-D6 / E1-E16 theorem base" in synthesis
    and "only 14" in synthesis
):
    ok("canonical-synthesis-integration", "formalization authority rule and complete Foundations V boundary integrated into controlling synthesis")
else:
    fail("canonical-synthesis-integration", "formal-aware control section missing or incomplete")

summary = json.loads((ROOT / "generated" / "step1_formal_completion_summary.json").read_text(encoding="utf-8"))
expected_summary = {
    "spine_papers": 7,
    "f_rows": 52,
    "f_local_modules": 14,
    "e_rows": 16,
    "e_local_modules": 16,
    "g_rows": 13,
    "g_local_modules": 13,
    "formal_deep_supplements": 7,
    "survey_disclosure_rows": 58,
    "dependency_summary_rows": 58,
    "dependency_edges": 240,
    "dependency_unresolved_internal_keys": 2,
    "version_slots": 73,
    "version_line_alignment_blocks": 505,
    "step2_started": False,
}
if summary == expected_summary:
    ok("completion-summary", "machine-readable completion metrics exact")
else:
    fail("completion-summary", str(summary))

print("Foundations VII Step 1 formal-aware completion validation")
print("=========================================================")
for status, name, detail in checks:
    print(f"{status:<5} {name}: {detail}")
failures = [item for item in checks if item[0] == "FAIL"]
print()
if failures:
    print(f"VALIDATION: FAIL ({len(failures)} failures; {len(checks)} checks/notes)")
    sys.exit(1)
print(f"VALIDATION: PASS ({sum(item[0] == 'PASS' for item in checks)} checks; {sum(item[0] == 'INFO' for item in checks)} notes)")
