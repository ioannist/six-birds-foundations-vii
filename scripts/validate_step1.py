#!/usr/bin/env python3
"""Mechanical acceptance checks for Foundations VII reading program, Step 1."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
checks: list[tuple[str, str]] = []


def ok(name: str, detail: str) -> None:
    checks.append((name, detail))


def fail(name: str, detail: str) -> None:
    errors.append(f"{name}: {detail}")


def read_csv(rel: str) -> list[dict[str, str]]:
    path = ROOT / rel
    if not path.exists():
        fail(rel, "missing")
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


required = [
    "STEP1_REPORT.md",
    "README.md",
    "CONTENTS.md",
    "generated/step1_metrics.json",
    "scripts/build_delivery_manifest.py",
    "scripts/verify_delivery_manifest.py",
    "scripts/rebuild_step1.sh",
    "synthesis/SBT_STEP1_SYNTHESIS.md",
    "synthesis/CANONICAL_GLOSSARY.md",
    "synthesis/canonical_glossary.csv",
    "synthesis/symbol_alias_ledger.csv",
    "synthesis/correction_ambiguity_ledger.csv",
    "synthesis/LAW_ARCHITECTURE.md",
    "synthesis/FOUNDATIONS_VII_GAP_MAP.md",
    "synthesis/concept_graph.graphml",
    "wishlists/WISHLIST_SYNTHESIS_STEP1.md",
    "wishlists/atomic_requests.csv",
    "wishlists/convergence_groups.csv",
    "wishlists/CONVERGENCE_MAP.md",
    "reports/SURVEY_CARD_INDEX.md",
    "reports/VERSION_FAMILY_REPORT.md",
    "reports/SOURCE_EXTRACTION_EXCEPTIONS.md",
    "corpus/paper_manifest.csv",
    "corpus/coverage.csv",
    "corpus/source_hashes.sha256",
    "corpus/dependency_trees.json",
    "corpus/version_families.csv",
    "corpus/source_exceptions.csv",
    "registry/primitive_roles.csv",
    "registry/F_laws.csv",
    "registry/E_laws.csv",
    "registry/G_laws.csv",
    "registry/no_go_theorems.csv",
    "decisions/ADR-0001-canonical-primitive-role-authority.md",
    "decisions/ADR-0002-birdint-domain-tuple.md",
    "decisions/ADR-0003-law-identifier-preservation.md",
    "decisions/ADR-0004-P040-P058-version-family.md",
    "decisions/ADR-0005-source-package-exceptions.md",
]
missing_required = [rel for rel in required if not (ROOT / rel).exists()]
if missing_required:
    fail("required-artifacts", f"missing {missing_required}")
else:
    ok("required-artifacts", f"{len(required)} present")

manifest = read_csv("corpus/paper_manifest.csv")
ids = [r.get("paper_id", "") for r in manifest]
expected_ids = {f"P{i:03d}" for i in range(1, 59)}
if len(manifest) == 58 and len(set(ids)) == 58 and set(ids) == expected_ids:
    ok("paper-manifest", "58 unique roots P001–P058")
else:
    fail("paper-manifest", f"rows={len(manifest)} unique={len(set(ids))} missing={sorted(expected_ids-set(ids))}")

clusters = Counter(r.get("cluster", "") for r in manifest)
expected_clusters = {
    "A_CANONICAL_SPINE": 7,
    "B_VII_NEAR_INTERACTION_ACCESS": 24,
    "C_PHILOSOPHY_METATHEORY": 9,
    "D_COGNITION_SOCIAL": 4,
    "E_DOMAIN_PRESSURE_TESTS": 14,
}
if dict(clusters) == expected_clusters:
    ok("cluster-partition", ", ".join(f"{k}={v}" for k, v in expected_clusters.items()))
else:
    fail("cluster-partition", str(dict(clusters)))

coverage = read_csv("corpus/coverage.csv")
states = Counter(r.get("state", "") for r in coverage)
if len(coverage) == 58 and states == Counter({"SURVEYED": 38, "DEEP_READ": 20}):
    ok("coverage-state", "20 DEEP_READ + 38 SURVEYED")
else:
    fail("coverage-state", f"rows={len(coverage)} states={dict(states)}")

survey_cards = sorted((ROOT / "notes" / "survey").glob("P[0-9][0-9][0-9].md"))
required_survey_headings = {
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
bad_cards: list[str] = []
for card in survey_cards:
    text = card.read_text(encoding="utf-8")
    if not required_survey_headings.issubset(set(re.findall(r"^## .+$", text, flags=re.M))):
        bad_cards.append(card.name)
if len(survey_cards) == 58 and not bad_cards:
    ok("survey-cards", "58 source-located cards with required sections")
else:
    fail("survey-cards", f"count={len(survey_cards)} malformed={bad_cards}")

expected_deep = {"P031", "P027", "P026", "P028", "P030", "P029", "P032", "P006", "P023", "P034", "P053", "P046", "P041", "P040", "P058", "P056", "P005", "P055", "P044", "P013"}
deep_cards = sorted((ROOT / "notes" / "deep").glob("P[0-9][0-9][0-9].md"))
deep_ids = {p.stem for p in deep_cards}
required_deep_headings = {
    "## Provenance and controlling status",
    "## Controlling question",
    "## Reconstructed argument and result architecture",
    "## Material imported into the Step-1 SBT model",
    "## Scope and nonclaim boundary",
    "## Foundations VII consequences",
    "## Source navigation anchors",
    "## Step-2 obligation",
}
bad_deep: list[str] = []
for card in deep_cards:
    text = card.read_text(encoding="utf-8")
    if not required_deep_headings.issubset(set(re.findall(r"^## .+$", text, flags=re.M))):
        bad_deep.append(card.name)
if deep_ids == expected_deep and not bad_deep:
    ok("deep-reads", "20 expected foundational/philosophy/cognition notes")
else:
    fail("deep-reads", f"ids_delta={sorted(deep_ids ^ expected_deep)} malformed={bad_deep}")

for rel, expected in [
    ("registry/primitive_roles.csv", 6),
    ("registry/F_laws.csv", 52),
    ("registry/E_laws.csv", 16),
    ("registry/G_laws.csv", 13),
    ("registry/no_go_theorems.csv", 8),
]:
    rows = read_csv(rel)
    id_col = "role_id" if "primitive" in rel else "law_id"
    ids_here = [r.get(id_col, "") for r in rows]
    if len(rows) == expected and len(set(ids_here)) == expected:
        ok(rel, f"{expected} unique rows")
    else:
        fail(rel, f"rows={len(rows)} unique={len(set(ids_here))} expected={expected}")

f_ids = {r["law_id"] for r in read_csv("registry/F_laws.csv")}
if {"F13a", "F13b", "F15a", "F15b"}.issubset(f_ids) and "F1" not in f_ids:
    ok("F-identifiers", "source numbering and split identifiers preserved")
else:
    fail("F-identifiers", "split/source IDs not preserved")

roles = {r["role_id"]: r for r in read_csv("registry/primitive_roles.csv")}
if set(roles) == {"P1", "P2", "P3", "P4", "P5", "P6"} and "not a directionality" in roles["P3"].get("boundary", "").lower():
    ok("primitive-role-ruling", "Foundations-II typing + P3/P6-drive separation present")
else:
    fail("primitive-role-ruling", "canonical role set or P3 boundary missing")

wish = read_csv("wishlists/atomic_requests.csv")
source_counts = Counter(r.get("source_code", "") for r in wish)
cluster_counts = Counter(r.get("cluster", "") for r in wish)
expected_sources = Counter({"ARC": 40, "CLD": 26, "MM": 19, "MED": 45})
expected_wish_clusters = Counter({
    "ACCESS_BOOTSTRAP": 13,
    "JOIN_CONTACT": 29,
    "ENABLEMENT_BIRTH": 12,
    "DIRECTION_ORDER": 22,
    "NO_GO_ANTI_SMUGGLING": 16,
    "EXPOSURE_OBSERVER": 15,
    "METHOD_BRIDGE": 23,
})
if len(wish) == 130 and source_counts == expected_sources and cluster_counts == expected_wish_clusters:
    ok("wishlist-atoms", "130 atoms; all four lists and seven fronts covered")
else:
    fail("wishlist-atoms", f"rows={len(wish)} sources={dict(source_counts)} clusters={dict(cluster_counts)}")

convergence = read_csv("wishlists/convergence_groups.csv")
conv_groups = {r.get("convergence_group", "") for r in convergence}
if len(convergence) == 130 and len(conv_groups) == 30 and {r.get("request_id", "") for r in convergence} == {r.get("request_id", "") for r in wish}:
    ok("wishlist-convergence", "130 atoms preserved across 30 provisional merge groups")
else:
    fail("wishlist-convergence", f"rows={len(convergence)} groups={len(conv_groups)}")

families = read_csv("corpus/version_families.csv")
if len(families) == 1 and families[0].get("family_id") == "VF-SAU-01" and set(families[0].get("members", "").split(";")) == {"P040", "P058"}:
    ok("version-family", "P040/P058 retained as one unresolved evidence family")
else:
    fail("version-family", str(families))

exceptions = {r["paper_id"]: r for r in read_csv("corpus/source_exceptions.csv")}
exception_json = json.loads((ROOT / "corpus" / "source_exceptions.json").read_text(encoding="utf-8"))
if (
    exceptions.get("P020", {}).get("blocking_status") == "NOT_BLOCKING_STEP1"
    and exceptions.get("P039", {}).get("blocking_status") == "BLOCKED_FULL_TEXT"
    and len(exception_json.get("p039_missing_inputs", [])) == 18
    and "SOURCE-LIMITATION:BEGIN" in (ROOT / "notes" / "survey" / "P039.md").read_text(encoding="utf-8")
):
    ok("source-exceptions", "P020 recovered; P039 18-file full-text block exposed")
else:
    fail("source-exceptions", "exception records incomplete or inconsistent")

hash_lines = (ROOT / "corpus" / "source_hashes.sha256").read_text(encoding="utf-8").splitlines()
source_candidates = sorted(p for p in (ROOT / "source").rglob("*") if p.is_file())
ignored: set[str] = set()
if source_candidates:
    result = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=ROOT,
        input="\n".join(str(p.relative_to(ROOT)) for p in source_candidates),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode in (0, 1):
        ignored = set(result.stdout.splitlines())
source_files = sorted(p for p in source_candidates if str(p.relative_to(ROOT)) not in ignored)
hash_failures: list[str] = []
seen_hash_paths: set[str] = set()
for line in hash_lines:
    if not line.strip():
        continue
    m = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
    if not m:
        hash_failures.append(f"malformed:{line}")
        continue
    expected, rel = m.groups()
    seen_hash_paths.add(rel)
    path = ROOT / rel
    if not path.exists() or sha256(path) != expected:
        hash_failures.append(rel)
expected_hash_paths = {str(p.relative_to(ROOT)) for p in source_files}
if not hash_failures and seen_hash_paths == expected_hash_paths:
    ok("source-freeze", f"{len(source_files)} source files verify against SHA-256 ledger")
else:
    fail("source-freeze", f"bad={hash_failures[:8]} ledger_delta={sorted(seen_hash_paths ^ expected_hash_paths)[:8]}")

archive_checksum = ROOT / "source" / "_provenance" / "archive.sha256"
archive_lines = archive_checksum.read_text(encoding="utf-8").splitlines() if archive_checksum.exists() else []
archive_match = re.fullmatch(r"([0-9a-f]{64})  (.+)", archive_lines[0]) if len(archive_lines) == 1 else None
if archive_match:
    expected_archive_hash, archive_rel = archive_match.groups()
    archive_path = ROOT / archive_rel
    if archive_rel != "source/_provenance/six-birds-foundations-vii_v0.zip":
        fail("source-archive-provenance", f"unexpected archive path={archive_rel}")
    elif archive_path.is_file() and sha256(archive_path) != expected_archive_hash:
        fail("source-archive-provenance", "locally retained archive does not match its public digest record")
    else:
        ok("source-archive-provenance", "archive digest is recorded; optional local archive matches when present")
else:
    fail("source-archive-provenance", "archive.sha256 is missing or malformed")

try:
    ET.parse(ROOT / "synthesis" / "concept_graph.graphml")
    ok("concept-graph", "GraphML parses")
except Exception as exc:
    fail("concept-graph", repr(exc))

synthesis_text = (ROOT / "synthesis" / "SBT_STEP1_SYNTHESIS.md").read_text(encoding="utf-8")
red_line_terms = [
    "Objecthood / stability",
    "Novelty / strictness",
    "Directionality",
    "P3 is not directionality",
    "expressible",
    "common source",
    "enablement",
    "No-go boundaries",
]
missing_terms = [x for x in red_line_terms if x not in synthesis_text]
if not missing_terms:
    ok("canonical-synthesis", "three certificates, typed roles, no-gos, and VII red lines present")
else:
    fail("canonical-synthesis", f"missing markers {missing_terms}")

corrections = read_csv("synthesis/correction_ambiguity_ledger.csv")
if len(corrections) == 7 and {r["id"] for r in corrections} == {f"C{i:03d}" for i in range(1, 8)}:
    ok("correction-ledger", "7 controlled rulings/ambiguities")
else:
    fail("correction-ledger", f"rows={len(corrections)}")

glossary = read_csv("synthesis/canonical_glossary.csv")
if len(glossary) == 44 and len({r["term"] for r in glossary}) == 44:
    ok("canonical-glossary", "44 unique terms with status and noncollapse boundaries")
else:
    fail("canonical-glossary", f"rows={len(glossary)} unique={len({r.get('term','') for r in glossary})}")

report_text = (ROOT / "STEP1_REPORT.md").read_text(encoding="utf-8")
if "read-step-01" in report_text and "COMPLETE WITH ONE RECORDED SOURCE-PACKAGE LIMITATION" in report_text and "P039" in report_text:
    ok("root-report", "delivery tag, completion posture, and source limitation recorded")
else:
    fail("root-report", "delivery identity or qualification missing")

metrics = json.loads((ROOT / "generated" / "step1_metrics.json").read_text(encoding="utf-8"))
if metrics.get("paper_roots") == 58 and metrics.get("wishlist_atoms") == 130 and metrics.get("full_text_blocks") == ["P039"]:
    ok("step1-metrics", "machine-readable delivery metrics are consistent")
else:
    fail("step1-metrics", str(metrics))

# Each manifest dependency path must exist; P039's unresolved includes are separately recorded.
dep = json.loads((ROOT / "corpus" / "dependency_trees.json").read_text(encoding="utf-8"))
missing_deps: list[str] = []
items = dep.items() if isinstance(dep, dict) else ((item.get("paper_id", "?"), item) for item in dep)
for pid, item in items:
    for rel in item.get("files", item.get("dependencies", [])):
        if not (ROOT / "source" / rel).exists():
            missing_deps.append(f"{pid}:{rel}")
if len(dep) == 58 and not missing_deps:
    ok("dependency-closure", "58 recorded source trees; every recorded file exists")
else:
    fail("dependency-closure", f"trees={len(dep)} missing={missing_deps[:8]}")

print("Foundations VII Step 1 validation")
print("=" * 38)
for name, detail in checks:
    print(f"PASS  {name}: {detail}")
if errors:
    print("\nVALIDATION: FAIL")
    for err in errors:
        print(f"FAIL  {err}")
    sys.exit(1)
print(f"\nVALIDATION: PASS ({len(checks)} checks)")
