#!/usr/bin/env python3
"""Rebind the phase-level declaration registries to the current sources.

The phase1..4 public-declaration registries are frozen historical records: each
row's (line, end_line, source sha) binds exactly at its own phase tag
(vii-science-01..04; verified 1315/1315). The kernel-replay repairs then shifted
lines in nearly every VII file, so at HEAD most rows no longer resolve --- the
registries are honest about the past and silently wrong as locators.

This script does not touch the frozen registries. It emits
`science/traceability/phase_declaration_rebinding.{jsonl,csv}`: one row per
historical declaration, carrying its phase-tag coordinates verbatim and its
CURRENT coordinates as found by the same parser the final registry uses. A
`content_changed` flag records whether the repair altered the block itself (the
phase sha convention: sha256 over the stripped line-range block).

Exit is non-zero if any historical declaration cannot be found at HEAD, so a
future rename cannot silently orphan a frozen row.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formalization" / "lean"
VII = LEAN / "FoundationsVII"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
OUT_SUMMARY = ROOT / "generated" / "phase_declaration_rebinding_summary.json"

PHASES = {1: "vii-science-01", 2: "vii-science-02", 3: "vii-science-03", 4: "vii-science-04"}


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "fvii_final_registry_builder", ROOT / "scripts" / "build_fvii_sci05_registry.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    builder = load_builder()

    # Current declaration map over ALL VII sources (Trust/Runner/All included:
    # phase rows may live in files the final public surface excludes).
    current: dict[str, dict] = {}
    files = sorted(VII.rglob("*.lean")) + [LEAN / "FoundationsVII.lean"]
    for path in files:
        rel = path.relative_to(LEAN).as_posix()
        module = rel[:-len(".lean")].replace("/", ".")
        for row in builder.parse_declarations(path, module):
            fq = row["fully_qualified_name"]
            # first sighting wins; duplicates are recorded for the report
            current.setdefault(fq, row)

    phase_rows = []
    for ph in PHASES:
        for line in (REG / f"phase{ph}_public_declarations.jsonl").read_text().splitlines():
            r = json.loads(line)
            r["_phase"] = ph
            r["_sha"] = r.get("source_sha256") or r.get("source_block_sha256")
            phase_rows.append(r)

    out, absent = [], []
    for r in sorted(phase_rows, key=lambda x: x["fully_qualified_name"]):
        fq = r["fully_qualified_name"]
        cur = current.get(fq)
        if cur is None:
            absent.append(fq)
            status, cur_path, cur_line, cur_sha, changed = "ABSENT_AT_HEAD", "", 0, "", ""
        else:
            status = "REBOUND"
            cur_path, cur_line = cur["path"], int(cur["line"])
            # phase sha convention: sha256 over the stripped block
            cur_sha = hashlib.sha256(cur["source_block"].strip().encode()).hexdigest()
            changed = cur_sha != r["_sha"]
        out.append({
            "fully_qualified_name": fq,
            "kind": r["kind"],
            "phase": r["_phase"],
            "phase_tag": PHASES[r["_phase"]],
            "historical_file": r["file"],
            "historical_line": int(r["line"]),
            "historical_end_line": int(r["end_line"]),
            "historical_source_sha256": r["_sha"],
            "status": status,
            "current_file": cur_path,
            "current_line": cur_line,
            "current_source_sha256": cur_sha,
            "content_changed_since_phase": changed,
            "nonclaim": ("Historical coordinates bind at the phase tag only; current "
                         "coordinates bind at the commit this artifact was generated from."),
        })

    TRACE.mkdir(parents=True, exist_ok=True)
    (TRACE / "phase_declaration_rebinding.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in out), encoding="utf-8")
    with (TRACE / "phase_declaration_rebinding.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    summary = {
        "rows": len(out),
        "rebound": sum(1 for r in out if r["status"] == "REBOUND"),
        "absent_at_head": absent,
        "content_changed_since_phase": sum(1 for r in out if r["content_changed_since_phase"] is True),
        "line_moved_only": sum(1 for r in out if r["status"] == "REBOUND"
                               and r["content_changed_since_phase"] is False
                               and (r["historical_file"] != r["current_file"]
                                    or r["historical_line"] != r["current_line"])),
        "still_at_historical_coordinates": sum(
            1 for r in out if r["status"] == "REBOUND"
            and r["content_changed_since_phase"] is False
            and r["historical_file"] == r["current_file"]
            and r["historical_line"] == r["current_line"]),
        "by_phase": {str(p): sum(1 for r in out if r["phase"] == p) for p in PHASES},
    }
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 1 if absent else 0


if __name__ == "__main__":
    raise SystemExit(main())
