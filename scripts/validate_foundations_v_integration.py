#!/usr/bin/env python3
"""Validate the imported Foundations V theorem base and its VII-owned completion surface.

The checks distinguish immutable upstream assets, VII-owned import/manifest
completion, static Lean indexing, local runtime evidence, and unavailable
kernel replay.  They do not create or validate any Foundations VII theorem.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROV = ROOT / "formalization" / "_provenance"
V = ROOT / "formalization" / "foundations_v_scaffold"
INTEGRATION = ROOT / "formalization" / "integration"
ACTIVE = ROOT / "formalization" / "lean"

checks: list[tuple[str, str, str]] = []


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def ok(name: str, detail: str) -> None:
    checks.append(("PASS", name, detail))


def fail(name: str, detail: str) -> None:
    checks.append(("FAIL", name, detail))


def info(name: str, detail: str) -> None:
    checks.append(("INFO", name, detail))


def main() -> int:
    required = [
        PROV / "six-birds-cognition_v45_2.zip.sha256",
        PROV / "foundations_v_upstream_commit.txt",
        PROV / "foundations_v_import_selection.json",
        PROV / "foundations_v_import_manifest.csv",
        PROV / "foundations_v_imported_files.sha256",
        V / "THEOREMS.md",
        V / "LANDING_PLAN.md",
        V / "lean" / "lakefile.toml",
        V / "lean" / "lean-toolchain",
        V / "formalization" / "manifests" / "foundations_v_manifest.toml",
        ACTIVE / "FoundationsVII" / "PriorFoundationsVComplete.lean",
        INTEGRATION / "foundations_v_lean_modules.csv",
        INTEGRATION / "foundations_v_lean_declarations.csv",
        INTEGRATION / "foundations_v_lean_import_edges.csv",
        INTEGRATION / "foundations_v_lean_unresolved_imports.csv",
        INTEGRATION / "foundations_v_authored_declarations.csv",
        INTEGRATION / "foundations_v_authored_theorems.csv",
        INTEGRATION / "foundations_v_formalization_summary.json",
        INTEGRATION / "foundations_v_manifest_reconciliation.csv",
        INTEGRATION / "foundations_v_manifest_reconciliation.json",
        INTEGRATION / "foundations_v_completed_manifest.toml",
        INTEGRATION / "foundations_v_root_import_audit.csv",
        INTEGRATION / "foundations_v_root_import_audit.json",
        INTEGRATION / "foundations_v_e_law_traceability.csv",
        INTEGRATION / "foundations_v_vi_vendor_equivalence.csv",
        INTEGRATION / "foundations_v_dependency_relocation.csv",
        INTEGRATION / "foundations_v_dependency_relocation.json",
        INTEGRATION / "cumulative_lean_modules.csv",
        INTEGRATION / "cumulative_lean_declarations.csv",
        INTEGRATION / "cumulative_lean_theorems.csv",
        INTEGRATION / "cumulative_lean_import_edges.csv",
        INTEGRATION / "cumulative_lean_unresolved_imports.csv",
        INTEGRATION / "cumulative_formalization_summary.json",
        ROOT / "reports" / "FOUNDATIONS_V_INTEGRATION_REPORT.md",
        ROOT / "generated" / "formalization_baseline.json",
        ROOT / "generated" / "foundations_v_long_replay_record.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail("required-artifacts", f"missing={missing}")
    else:
        ok("required-artifacts", f"{len(required)} Foundations V integration artifacts present")

    selection = json.loads((PROV / "foundations_v_import_selection.json").read_text(encoding="utf-8"))
    checksum = (PROV / "six-birds-cognition_v45_2.zip.sha256").read_text(encoding="utf-8").strip()
    commit = (PROV / "foundations_v_upstream_commit.txt").read_text(encoding="utf-8").strip()
    expected_checksum = f"{selection['archive_sha256']}  {selection['archive']}"
    if (
        checksum == expected_checksum
        and commit == selection["upstream_commit_from_zip_comment"]
        and re.fullmatch(r"[0-9a-f]{40}", commit)
    ):
        ok("archive-provenance-record", f"sha256={selection['archive_sha256']}; upstream commit={commit}")
    else:
        fail("archive-provenance-record", "checksum sidecar or upstream commit record mismatch")

    archive = ROOT / selection["archive"]
    if archive.is_file():
        if sha256(archive) == selection["archive_sha256"]:
            ok("optional-local-archive", "locally retained archive matches its public digest record")
        else:
            fail("optional-local-archive", "locally retained archive does not match its public digest record")
    else:
        info("optional-local-archive", "original archive is intentionally not distributed; curated import is verified below")

    manifest = rows(PROV / "foundations_v_import_manifest.csv")
    expected_paths = {row["imported_path"] for row in manifest}
    transient = {"__pycache__", ".pytest_cache", ".lake"}
    actual_paths = {
        str(path.relative_to(ROOT))
        for path in V.rglob("*")
        if path.is_file() and not transient.intersection(path.relative_to(V).parts)
    }
    bad_hashes: list[str] = []
    for row in manifest:
        path = ROOT / row["imported_path"]
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256(path) != row["sha256"]
        ):
            bad_hashes.append(row["imported_path"])
    if (
        selection.get("all_lean_sources_included") is True
        and len(manifest) == selection["selected_file_count"] == 372
        and sum(int(row["bytes"]) for row in manifest) == selection["selected_bytes"] == 10_693_226
        and actual_paths == expected_paths
        and not bad_hashes
    ):
        ok("immutable-import", "372 curated upstream files (including every Lean source) verify byte-for-byte")
    else:
        fail(
            "immutable-import",
            f"manifest={len(manifest)} bytes={sum(int(r['bytes']) for r in manifest)} "
            f"bad={bad_hashes[:8]} set_delta={sorted(actual_paths ^ expected_paths)[:8]}",
        )

    excluded = [V / "review_requests", V / "scripts" / "make_review_zip.sh", V / "six-birds-papers"]
    leaked = [str(path.relative_to(ROOT)) for path in excluded if path.exists() or path.is_symlink()]
    if not leaked:
        ok("curated-selection", "review correspondence, packaging-only script, and external symlink excluded from active scaffold")
    else:
        fail("curated-selection", f"unexpected active imports={leaked}")

    summary = json.loads((INTEGRATION / "foundations_v_formalization_summary.json").read_text(encoding="utf-8"))
    exact = {
        "lean_files": 70,
        "lean_modules": 70,
        "lean_import_edges": 196,
        "unresolved_imports": 0,
        "lexically_indexed_declarations": 1758,
        "authored_foundations_v_declarations": 1261,
        "authored_foundations_v_theorems": 187,
        "sorry_tokens": 0,
        "admit_tokens": 0,
        "axiom_declarations": 0,
        "opaque_declarations": 0,
        "foundations_v_definition_modules": 6,
        "foundations_v_law_modules": 15,
        "foundations_v_e_laws_covered": 16,
    }
    mismatches = {key: (summary.get(key), value) for key, value in exact.items() if summary.get(key) != value}
    expected_kinds = {"abbrev": 6, "def": 550, "inductive": 42, "structure": 476, "theorem": 187}
    expected_layers = {"FOUNDATIONS_III": 24, "FOUNDATIONS_V": 22, "HOLONOMY_SUPPORT": 10, "XI_SUPPORT": 14}
    if (
        not mismatches
        and summary.get("authored_declaration_kinds") == expected_kinds
        and summary.get("module_layers") == expected_layers
        and summary.get("lean_toolchain") == "leanprover/lean4:v4.28.0"
    ):
        ok("lean-index", "70 modules; 1,758 declarations; exact 1,261/187 authored V declaration/theorem census; no placeholders or new trust")
    else:
        fail("lean-index", f"mismatches={mismatches} kinds={summary.get('authored_declaration_kinds')} layers={summary.get('module_layers')}")

    authored_theorems = rows(INTEGRATION / "foundations_v_authored_theorems.csv")
    if (
        len(authored_theorems) == 187
        and all(row.get("kind") in {"theorem", "lemma"} for row in authored_theorems)
        and len({row.get("fully_qualified_name") for row in authored_theorems}) == 187
    ):
        ok("theorem-index", "187 unique authored Foundations V theorem declarations are available as direct Step-2 lookup rows")
    else:
        fail(
            "theorem-index",
            f"rows={len(authored_theorems)} kinds={dict(Counter(r.get('kind', '') for r in authored_theorems))} "
            f"unique={len({r.get('fully_qualified_name') for r in authored_theorems})}",
        )

    unresolved = rows(INTEGRATION / "foundations_v_lean_unresolved_imports.csv")
    if not unresolved:
        ok("import-closure", "all 196 Foundations V archive import edges resolve locally")
    else:
        fail("import-closure", str(unresolved[:8]))

    reconciliation = json.loads((INTEGRATION / "foundations_v_manifest_reconciliation.json").read_text(encoding="utf-8"))
    reconciliation_rows = rows(INTEGRATION / "foundations_v_manifest_reconciliation.csv")
    status_counts = Counter(row["upstream_manifest_status"] for row in reconciliation_rows)
    if (
        reconciliation.get("actual_authored_declarations") == 1261
        and reconciliation.get("upstream_manifest_rows") == 1141
        and reconciliation.get("actual_rows_missing_from_upstream_manifest") == 120
        and reconciliation.get("actual_only_law_ids") == ["E16"]
        and reconciliation.get("upstream_rows_missing_from_lean") == []
        and reconciliation.get("completed_manifest_rows") == 1261
        and len(reconciliation_rows) == 1261
        and status_counts == Counter({"UPSTREAM_MANIFEST_MATCH": 1141, "VII_E16_MANIFEST_COMPLETION": 120})
    ):
        ok("manifest-completion", "upstream 1,141-row manifest reconciled; all 120 existing E16 declarations added to a 1,261-row VII completion manifest")
    else:
        fail("manifest-completion", f"summary={reconciliation} statuses={dict(status_counts)} rows={len(reconciliation_rows)}")

    completed = tomllib.loads((INTEGRATION / "foundations_v_completed_manifest.toml").read_text(encoding="utf-8"))
    completed_rows = completed.get("declarations", [])
    if len(completed_rows) == 1261 and len({row.get("name") for row in completed_rows}) == 1261:
        ok("completed-manifest", "completed TOML manifest contains 1,261 unique authored declarations")
    else:
        fail("completed-manifest", f"rows={len(completed_rows)} unique={len({row.get('name') for row in completed_rows})}")

    root_summary = json.loads((INTEGRATION / "foundations_v_root_import_audit.json").read_text(encoding="utf-8"))
    root_rows = rows(INTEGRATION / "foundations_v_root_import_audit.csv")
    e16 = next((row for row in root_rows if row["module"].endswith("E16Adaptability")), {})
    wrapper_text = (ACTIVE / "FoundationsVII" / "PriorFoundationsVComplete.lean").read_text(encoding="utf-8")
    wrapper_decl_text = re.sub(r"/-.*?-\//|--.*$", " ", wrapper_text, flags=re.S | re.M)
    wrapper_decls = re.findall(r"(?m)^\s*(?:def|theorem|lemma|structure|inductive|axiom|opaque|abbrev|instance|class)\s+", wrapper_decl_text)
    if (
        root_summary.get("expected_authored_submodules") == 21
        and root_summary.get("upstream_root_imported") == 20
        and root_summary.get("upstream_root_missing") == ["SixBirdsFoundationsV.Laws.E16Adaptability"]
        and root_summary.get("vii_wrapper_complete") is True
        and len(root_rows) == 21
        and e16.get("imported_by_upstream_root") == "NO"
        and e16.get("imported_by_vii_complete_wrapper") == "YES"
        and "import SixBirdsFoundationsV" in wrapper_text
        and "import SixBirdsFoundationsV.Laws.E16Adaptability" in wrapper_text
        and not wrapper_decls
    ):
        ok("complete-import-surface", "VII-owned declaration-free wrapper repairs the upstream root's sole omission: existing E16")
    else:
        fail("complete-import-surface", f"summary={root_summary} e16={e16} wrapper_decls={wrapper_decls}")

    trace = rows(INTEGRATION / "foundations_v_e_law_traceability.csv")
    trace_missing: list[str] = []
    for row in trace:
        required_fields = [
            "theorem_ledger", "lean_file", "gate_note", "example_note",
            "sweep_predictions", "sweep_results",
        ]
        if row["law_id"] == "E16":
            required_fields.append("standalone_sweep")
        else:
            required_fields.append("pytest_file")
        for field in required_fields:
            value = row.get(field, "")
            if not value or not (ROOT / value).is_file():
                trace_missing.append(f"{row['law_id']}:{field}")
    if (
        len(trace) == 16
        and {row["law_id"] for row in trace} == {f"E{i}" for i in range(1, 17)}
        and sum(int(row["declaration_count"]) for row in {r["lean_module"]: r for r in trace}.values()) == 1125
        and not trace_missing
        and next(row for row in trace if row["law_id"] == "E16")["root_import_status"] == "VII_COMPLETE_WRAPPER"
    ):
        ok("e-law-traceability", "E1--E16 link paper grade, theorem ledger, Lean, gates, examples, predictions, results, and executable evidence")
    else:
        fail("e-law-traceability", f"rows={len(trace)} missing={trace_missing[:12]}")

    equivalence = rows(INTEGRATION / "foundations_v_vi_vendor_equivalence.csv")
    if len(equivalence) == 27 and all(row["status"] == "BYTE_IDENTICAL" for row in equivalence):
        ok("shared-foundations-iii", "all 27 shared vendored Foundations III files are byte-identical across the V and VI archives")
    else:
        fail("shared-foundations-iii", f"rows={len(equivalence)} statuses={dict(Counter(r['status'] for r in equivalence))}")

    e_disclosure = rows(INTEGRATION / "e_law_formalization_disclosure.csv")
    prior_coverage = rows(INTEGRATION / "prior_law_formalization_coverage.csv")
    e_prior = [row for row in prior_coverage if row["series"] == "E"]
    if (
        len(e_disclosure) == 16
        and Counter(row["local_import_status"] for row in e_disclosure)
        == Counter({"PRESENT_DEDICATED_MODULE": 13, "PRESENT_SHARED_MODULE": 2, "PRESENT_MODULE_WITH_VII_ROOT_COMPLETION": 1})
        and all(row["local_verification_state"] == "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED" for row in e_disclosure)
        and len(e_prior) == 16
        and all(row["coverage_status"] == "IMPORTED_MECHANIZED_MODULE" for row in e_prior)
    ):
        ok("coverage-reconciliation", "all 16 E laws are now represented as locally present, statically indexed, import-resolved modules without upgrading paper grades")
    else:
        fail("coverage-reconciliation", f"disclosure={Counter(r['local_import_status'] for r in e_disclosure)} prior={Counter(r['coverage_status'] for r in e_prior)}")

    relocation = json.loads((INTEGRATION / "foundations_v_dependency_relocation.json").read_text(encoding="utf-8"))
    if relocation == {
        "ALL_IDENTIFIERS_RELOCATED": 46,
        "NO_EXACT_IDENTIFIER_RELOCATED": 1,
        "PARTIAL_IDENTIFIERS_RELOCATED": 4,
        "inventory_entries": 51,
    }:
        info("dependency-relocation", "51 upstream absolute-path inventory entries mapped locally at exact-string reconnaissance depth: 46 full, 4 partial, 1 none")
    else:
        fail("dependency-relocation", str(relocation))

    baseline = json.loads((ROOT / "generated" / "formalization_baseline.json").read_text(encoding="utf-8"))
    baseline_pass = {
        "foundations_v_python_syntax": ("PASS", 202),
        "foundations_v_pytest_without_e15": ("PASS", None),
        "foundations_v_e16_sweep": ("PASS", None),
    }
    bad_baseline = []
    for key, (status, files) in baseline_pass.items():
        if baseline.get(key, {}).get("status") != status:
            bad_baseline.append(key)
        if files is not None and baseline.get(key, {}).get("files_checked") != files:
            bad_baseline.append(f"{key}:files")
    pytest_stdout = baseline.get("foundations_v_pytest_without_e15", {}).get("stdout", "")
    e16_stdout = baseline.get("foundations_v_e16_sweep", {}).get("stdout", "")
    if not bad_baseline and "317 passed" in pytest_stdout and "69/69 comparisons PASS" in e16_stdout:
        ok("runtime-baseline", "202 Python files compile; 317 non-E15 tests pass; E16 sweep reports 69/69 comparisons passing")
    else:
        fail("runtime-baseline", f"bad={bad_baseline} pytest={pytest_stdout[-80:]} e16={e16_stdout}")

    e15 = baseline.get("foundations_v_e15_tests", {})
    if e15.get("status") == "NOT_REPLAYED_LONG_RUNNING" and e15.get("tests_collected") == 74:
        info("e15-replay-limit", f"74 tests collected; {e15.get('observed_local_limit')}")
    else:
        fail("e15-replay-limit", str(e15))

    lean_build = baseline.get("lean_build", {})
    if lean_build.get("status") == "PASS":
        ok("lean-kernel-replay", "active cumulative project kernel-compiled locally")
    elif lean_build.get("status") == "NOT_RUN_TOOLCHAIN_UNAVAILABLE":
        info("lean-kernel-replay", "Lean/Lake 4.28.0 unavailable locally; R1--R3 static checks pass, but no R4 kernel replay is claimed")
    else:
        fail("lean-kernel-replay", str(lean_build))

    cumulative = json.loads((INTEGRATION / "cumulative_formalization_summary.json").read_text(encoding="utf-8"))
    cumulative_modules = rows(INTEGRATION / "cumulative_lean_modules.csv")
    cumulative_decls = rows(INTEGRATION / "cumulative_lean_declarations.csv")
    cumulative_theorems = rows(INTEGRATION / "cumulative_lean_theorems.csv")
    cumulative_edges = rows(INTEGRATION / "cumulative_lean_import_edges.csv")
    cumulative_unresolved = rows(INTEGRATION / "cumulative_lean_unresolved_imports.csv")
    expected_cumulative = {
        "unique_active_modules": 123,
        "unique_inherited_modules": 120,
        "v_archive_modules": 70,
        "vi_archive_modules": 74,
        "duplicate_module_names": 24,
        "active_vii_import_shell_modules": 3,
        "unique_active_declarations": 2587,
        "unique_active_theorems": 793,
        "active_vii_declarations": 0,
        "import_edges": 297,
        "unresolved_imports": 0,
        "sorry_tokens": 0,
        "admit_tokens": 0,
        "axiom_declarations": 1,
        "opaque_declarations": 5,
    }
    cumulative_bad = {key: (cumulative.get(key), value) for key, value in expected_cumulative.items() if cumulative.get(key) != value}
    expected_origins = {
        "FOUNDATIONS_VII_IMPORT_SHELL": 3,
        "FOUNDATIONS_VI_ARCHIVE": 50,
        "FOUNDATIONS_V_AND_VI_IDENTICAL_ACTIVE_VI_COPY": 24,
        "FOUNDATIONS_V_ARCHIVE": 46,
    }
    if (
        not cumulative_bad
        and cumulative.get("module_origins") == expected_origins
        and len(cumulative_modules) == 123
        and len(cumulative_decls) == 2587
        and len(cumulative_theorems) == 793
        and all(row.get("kind") in {"theorem", "lemma"} for row in cumulative_theorems)
        and len(cumulative_edges) == 297
        and not cumulative_unresolved
    ):
        ok("cumulative-lean-index", "123 unique active modules / 2,587 declarations / 793 theorem declarations across V, VI, prior dependencies, and the declaration-free VII shell; 297 imports resolve")
    else:
        fail("cumulative-lean-index", f"mismatches={cumulative_bad} origins={cumulative.get('module_origins')} rows={len(cumulative_modules)}/{len(cumulative_decls)}/{len(cumulative_theorems)}/{len(cumulative_edges)} unresolved={len(cumulative_unresolved)}")

    lake = tomllib.loads((ACTIVE / "lakefile.toml").read_text(encoding="utf-8"))
    libs = lake.get("lean_lib", [])
    names = {row["name"] for row in libs}
    expected_names = {
        "FoundationsVII", "SixBirdsFoundationsV", "Xi", "Main", "HolonomyMemory",
        "SixBirdsFoundationsVI", "ClosureLadder", "SixBirds", "SixBirdsIII", "SixBirdsMetaMath",
    }
    missing_src = [row.get("srcDir", "") for row in libs if row.get("srcDir") and not (ACTIVE / row["srcDir"]).resolve().exists()]
    if names == expected_names and not missing_src:
        ok("cumulative-lake-wiring", "active VII project exposes complete V and VI libraries plus their prior/support dependencies")
    else:
        fail("cumulative-lake-wiring", f"names={sorted(names)} missing_src={missing_src}")

    print("Foundations V theorem-base integration validation")
    print("=================================================")
    for status, name, detail in checks:
        print(f"{status:<5} {name}: {detail}")
    failures = [item for item in checks if item[0] == "FAIL"]
    print()
    if failures:
        print(f"VALIDATION: FAIL ({len(failures)} failures; {len(checks)} checks/notes)")
        return 1
    print(f"VALIDATION: PASS ({sum(s == 'PASS' for s, _, _ in checks)} checks; {sum(s == 'INFO' for s, _, _ in checks)} recorded limitations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
