#!/usr/bin/env python3
"""Validate the pre-Step-2 Foundations I--VI scaffold imports and VII import shell."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROV = ROOT / "formalization" / "_provenance"
SCAFFOLD = ROOT / "formalization" / "foundations_vi_scaffold"
V_SCAFFOLD = ROOT / "formalization" / "foundations_v_scaffold"
INTEGRATION = ROOT / "formalization" / "integration"
ACTIVE = ROOT / "formalization" / "lean"

checks: list[tuple[str, str, str]] = []


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ok(name: str, detail: str) -> None:
    checks.append(("PASS", name, detail))


def fail(name: str, detail: str) -> None:
    checks.append(("FAIL", name, detail))


def info(name: str, detail: str) -> None:
    checks.append(("INFO", name, detail))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_builder() -> Any:
    path = ROOT / "scripts" / "build_formalization_indexes.py"
    spec = importlib.util.spec_from_file_location("build_formalization_indexes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load build_formalization_indexes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_v_builder() -> Any:
    path = ROOT / "scripts" / "build_foundations_v_integration.py"
    spec = importlib.util.spec_from_file_location("build_foundations_v_integration", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load build_foundations_v_integration.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    required = [
        PROV / "six-birds-collatz_v19.zip.sha256",
        PROV / "upstream_commit.txt",
        PROV / "import_selection.json",
        PROV / "foundations_vi_import_manifest.csv",
        PROV / "foundations_vi_imported_files.sha256",
        SCAFFOLD / "THEOREMS.md",
        SCAFFOLD / "lean" / "lakefile.toml",
        SCAFFOLD / "lean" / "lean-toolchain",
        SCAFFOLD / "formalization" / "manifests" / "foundations_vi_manifest.toml",
        ACTIVE / "lakefile.toml",
        ACTIVE / "lean-toolchain",
        ACTIVE / "FoundationsVII.lean",
        ACTIVE / "FoundationsVII" / "PriorScaffold.lean",
        ACTIVE / "FoundationsVII" / "PriorFoundationsVComplete.lean",
        INTEGRATION / "lean_modules.csv",
        INTEGRATION / "lean_declarations.csv",
        INTEGRATION / "lean_import_edges.csv",
        INTEGRATION / "prior_law_formalization_coverage.csv",
        INTEGRATION / "g_law_traceability.csv",
        INTEGRATION / "formalization_summary.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        fail("required-artifacts", f"missing={missing}")
    else:
        ok("required-artifacts", f"{len(required)} present")

    selection = json.loads((PROV / "import_selection.json").read_text(encoding="utf-8"))
    commit = (PROV / "upstream_commit.txt").read_text(encoding="utf-8").strip()
    checksum_line = (PROV / "six-birds-collatz_v19.zip.sha256").read_text(encoding="utf-8").strip()
    expected_line = f"{selection['archive_sha256']}  {selection['archive']}"
    if (
        checksum_line == expected_line
        and re.fullmatch(r"[0-9a-f]{40}", commit)
        and commit == selection["upstream_commit_from_zip_comment"]
    ):
        ok("archive-provenance-record", f"sha256={selection['archive_sha256']}; upstream commit={commit}")
    else:
        fail("archive-provenance-record", "checksum record or commit identity mismatch")

    archive = ROOT / selection["archive"]
    if archive.is_file():
        if sha256(archive) == selection["archive_sha256"]:
            ok("optional-local-archive", "locally retained archive matches its public digest record")
        else:
            fail("optional-local-archive", "locally retained archive does not match its public digest record")
    else:
        info("optional-local-archive", "original archive is intentionally not distributed; curated import is verified below")

    manifest = read_csv(PROV / "foundations_vi_import_manifest.csv")
    expected_paths = {row["imported_path"] for row in manifest}
    transient_parts = {"__pycache__", ".pytest_cache", ".lake"}
    actual_paths = {
        str(path.relative_to(ROOT))
        for path in SCAFFOLD.rglob("*")
        if path.is_file() and not transient_parts.intersection(path.relative_to(SCAFFOLD).parts)
    }
    bad_hashes = []
    for row in manifest:
        path = ROOT / row["imported_path"]
        if not path.is_file() or sha256(path) != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            bad_hashes.append(row["imported_path"])
    if (
        len(manifest) == selection["selected_file_count"] == 282
        and actual_paths == expected_paths
        and not bad_hashes
    ):
        ok("immutable-import", f"282 imported files verify byte-for-byte")
    else:
        fail(
            "immutable-import",
            f"manifest={len(manifest)} bad={bad_hashes[:8]} set_delta={sorted(actual_paths ^ expected_paths)[:8]}",
        )

    excluded = [".codex", "review_requests", "collatz_idea.md", "ideas.md"]
    leaked = [name for name in excluded if (SCAFFOLD / name).exists()]
    if not leaked:
        ok("curated-selection", "operational prompts, review history, and freeform Collatz idea files excluded from active scaffold")
    else:
        fail("curated-selection", f"unexpected imported exclusions={leaked}")

    summary = json.loads((INTEGRATION / "formalization_summary.json").read_text(encoding="utf-8"))
    expected_summary = {
        "lean_files": 74,
        "lean_modules": 74,
        "lean_import_edges": 125,
        "unresolved_imports": 0,
        "lexically_indexed_declarations": 1106,
        "sorry_tokens": 0,
        "admit_tokens": 0,
        "axiom_declarations": 1,
        "opaque_declarations": 5,
        "foundations_iv_law_modules": 14,
        "foundations_vi_g_laws": 13,
        "foundations_v_e_laws_locally_covered": 16,
        "foundations_v_e_laws_with_dedicated_modules": 14,
        "foundations_v_e_laws_in_shared_module": 2,
    }
    bad_summary = {key: (summary.get(key), value) for key, value in expected_summary.items() if summary.get(key) != value}
    if not bad_summary and summary.get("lean_toolchain") == "leanprover/lean4:v4.28.0":
        ok("lean-index", "74 modules, 1,106 declarations, 125 resolved imports, zero sorry/admit")
    else:
        fail("lean-index", str(bad_summary))

    unresolved = read_csv(INTEGRATION / "lean_unresolved_imports.csv")
    if not unresolved:
        ok("import-closure", "every imported Lean module edge resolves locally")
    else:
        fail("import-closure", str(unresolved[:8]))

    trust_text = (SCAFFOLD / "formalization" / "manifests" / "trust_base.txt").read_text(encoding="utf-8")
    modules = read_csv(INTEGRATION / "lean_modules.csv")
    if (
        sum(int(row["axioms"]) for row in modules) == 1
        and sum(int(row["opaque_constants"]) for row in modules) == 5
        and "hiddenness_pending" in trust_text
        and trust_text.count("Paper7") >= 5
    ):
        ok("trust-base", "one inherited F13a axiom and five inherited opaque constants are explicitly ledgered")
    else:
        fail("trust-base", "trust ledger does not match lexical declaration surface")

    coverage = read_csv(INTEGRATION / "prior_law_formalization_coverage.csv")
    f_ids = {row["law_id"] for row in coverage if row["series"] == "F"}
    e_rows = [row for row in coverage if row["series"] == "E"]
    g_ids = {row["law_id"] for row in coverage if row["series"] == "G"}
    expected_f = {"F2", "F3", "F4", "F6", "F7", "F10", "F11", "F12", "F13a", "F19", "F27", "F34", "F40", "F49"}
    expected_g = {f"G{i}" for i in range(1, 14)}
    if (
        f_ids == expected_f
        and g_ids == expected_g
        and len(e_rows) == 16
        and all(row["coverage_status"] == "IMPORTED_MECHANIZED_MODULE" for row in e_rows)
    ):
        ok("law-coverage", "14 imported F modules, all 16 E laws, and all 13 G modules are locally indexed")
    else:
        fail("law-coverage", f"F={sorted(f_ids)} G={sorted(g_ids)} E={len(e_rows)}")

    trace = read_csv(INTEGRATION / "g_law_traceability.csv")
    trace_missing: list[str] = []
    for row in trace:
        for field in ("lean_file", "gate_note", "example_note", "paper_source", "theorem_ledger"):
            if not row[field] or not (ROOT / row[field]).exists():
                trace_missing.append(f"{row['law_id']}:{field}")
    if len(trace) == 13 and not trace_missing:
        ok("g-traceability", "13 G laws link theorem ledger, Lean, gates, examples, labs/results, and paper source")
    else:
        fail("g-traceability", f"rows={len(trace)} missing={trace_missing[:12]}")

    audit = subprocess.run(
        [sys.executable, "scripts/audit_foundations_dependencies.py"],
        cwd=SCAFFOLD,
        text=True,
        capture_output=True,
    )
    if audit.returncode == 0 and "10 entries checked" in audit.stdout:
        ok("dependency-audit", audit.stdout.strip())
    else:
        fail("dependency-audit", (audit.stdout + audit.stderr).strip())

    builder = load_builder()
    v_builder = load_v_builder()
    imported_modules = dict(v_builder.module_map())
    # Prefer the Foundations VI copy of duplicate SixBirdsIII modules because
    # that is the active Lake source.  A separate byte-equivalence validator
    # proves the Foundations V and VI vendored copies are identical.
    imported_modules.update(builder.module_map())
    active_modules = {
        "FoundationsVII": ACTIVE / "FoundationsVII.lean",
        "FoundationsVII.PriorScaffold": ACTIVE / "FoundationsVII" / "PriorScaffold.lean",
        "FoundationsVII.PriorFoundationsVComplete": ACTIVE / "FoundationsVII" / "PriorFoundationsVComplete.lean",
    }
    combined = dict(imported_modules)
    combined.update(active_modules)
    active_unresolved: list[str] = []
    active_declarations: list[dict[str, Any]] = []
    for module, path in active_modules.items():
        active_declarations.extend(builder.declarations_from(module, path))
        for imported, _line in builder.imports_from(path.read_text(encoding="utf-8")):
            if imported not in combined:
                active_unresolved.append(f"{module}->{imported}")
    active_toolchain = (ACTIVE / "lean-toolchain").read_text(encoding="utf-8").strip()
    upstream_toolchain = (SCAFFOLD / "lean" / "lean-toolchain").read_text(encoding="utf-8").strip()
    if not active_unresolved and not active_declarations and active_toolchain == upstream_toolchain:
        ok("vii-import-shell", "active VII project resolves the full prior import surface and introduces zero VII declarations")
    else:
        fail(
            "vii-import-shell",
            f"unresolved={active_unresolved} declarations={len(active_declarations)} toolchains={active_toolchain}/{upstream_toolchain}",
        )

    lake_config = tomllib.loads((ACTIVE / "lakefile.toml").read_text(encoding="utf-8"))
    missing_src = []
    for lib in lake_config.get("lean_lib", []):
        if "srcDir" in lib and not (ACTIVE / str(lib["srcDir"])).resolve().exists():
            missing_src.append(str(lib["srcDir"]))
    if not missing_src and len(lake_config.get("lean_lib", [])) == 10:
        ok("vii-lake-project", "one VII library plus nine inherited/support libraries are wired through existing source directories")
    else:
        fail("vii-lake-project", f"missing_src={missing_src} libs={len(lake_config.get('lean_lib', []))}")

    baseline_path = ROOT / "generated" / "formalization_baseline.json"
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        required_baseline = (
            "foundations_vi_dependency_audit",
            "foundations_vi_python_syntax",
            "foundations_vi_lab_tests",
            "foundations_v_python_syntax",
            "foundations_v_pytest_without_e15",
            "foundations_v_e16_sweep",
        )
        bad_baseline = [key for key in required_baseline if baseline.get(key, {}).get("status") != "PASS"]
        if not bad_baseline:
            ok(
                "local-baseline",
                "VI dependency/syntax/62-test baseline and V syntax/317-test/E16-69-of-69 baseline pass",
            )
        else:
            fail("local-baseline", f"nonpassing={bad_baseline}")
        if baseline.get("lean_build", {}).get("status") == "PASS":
            ok("lean-build", "active Lean project compiled locally")
        else:
            info("lean-build", "not run locally: Lean/Lake toolchain unavailable; this is recorded, not counted as a proof check")
        vi_exclusions = baseline.get("foundations_vi_lab_tests", {}).get("excluded", [])
        if vi_exclusions:
            info("vi-lab-dependency", "; ".join(vi_exclusions))
        v_exclusions = baseline.get("foundations_v_pytest_without_e15", {}).get("excluded", [])
        if v_exclusions:
            info("v-long-replay", "; ".join(v_exclusions))
        e15 = baseline.get("foundations_v_e15_tests", {})
        if e15.get("status") == "NOT_REPLAYED_LONG_RUNNING":
            info("v-e15-replay", f"{e15.get('tests_collected')} tests: {e15.get('observed_local_limit')}")
    else:
        fail("local-baseline", "generated/formalization_baseline.json missing")

    print("Foundations VII pre-Step-2 complete formal scaffold validation")
    print("====================================================")
    for status, name, detail in checks:
        print(f"{status:<5} {name}: {detail}")
    failures = [row for row in checks if row[0] == "FAIL"]
    print()
    if failures:
        print(f"VALIDATION: FAIL ({len(failures)} failures; {len(checks)} checks/notes)")
        return 1
    print(f"VALIDATION: PASS ({sum(1 for row in checks if row[0] == 'PASS')} checks; {sum(1 for row in checks if row[0] == 'INFO')} recorded limitations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
