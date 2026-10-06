#!/usr/bin/env python3
"""Build an exact raw-TeX line delta for version family VF-SAU-01 (P040/P058).

The output is version-control reconnaissance only. It does not adjudicate claim identity,
mathematical equivalence, evidence independence, or canonical membership; those remain
Step-2 tasks.
"""
from __future__ import annotations

import csv
import difflib
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
GENERATED = ROOT / "generated"
P040 = ROOT / "source" / "papers" / "Tsiokos_2026_The_Usefulness_of_Non_Descending_Objects_A_Six_Birds_Theory_of_Mathematical_Applicability.tex"
P058 = ROOT / "source" / "papers" / "Tsiokos_2026_Why_Mathematics_Even_Works.tex"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def excerpt(lines: list[str], start: int, end: int, limit: int = 240) -> str:
    if start == end:
        return ""
    text = " ".join(line.strip() for line in lines[start:end] if line.strip())
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def range_text(start: int, end: int) -> str:
    """Convert zero-based half-open range to human one-based inclusive form."""
    if start == end:
        return "EMPTY"
    if end == start + 1:
        return str(start + 1)
    return f"{start + 1}-{end}"


def main() -> None:
    p040_text = P040.read_text(encoding="utf-8", errors="strict")
    p058_text = P058.read_text(encoding="utf-8", errors="strict")
    p040_lines = p040_text.splitlines()
    p058_lines = p058_text.splitlines()

    matcher = difflib.SequenceMatcher(None, p040_lines, p058_lines, autojunk=False)
    opcodes = matcher.get_opcodes()
    counts = Counter(tag for tag, *_ in opcodes)

    rows: list[dict[str, str]] = []
    for idx, (tag, i1, i2, j1, j2) in enumerate(opcodes, start=1):
        rows.append(
            {
                "block_id": f"VF-SAU-01-L{idx:04d}",
                "operation": tag.upper(),
                "p040_line_range": range_text(i1, i2),
                "p058_line_range": range_text(j1, j2),
                "p040_start_1based": str(i1 + 1) if i1 != i2 else "",
                "p040_end_1based_inclusive": str(i2) if i1 != i2 else "",
                "p058_start_1based": str(j1 + 1) if j1 != j2 else "",
                "p058_end_1based_inclusive": str(j2) if j1 != j2 else "",
                "p040_line_count": str(i2 - i1),
                "p058_line_count": str(j2 - j1),
                "p040_excerpt": excerpt(p040_lines, i1, i2),
                "p058_excerpt": excerpt(p058_lines, j1, j2),
                "status": "RAW_TEX_ALIGNMENT_ONLY",
                "inference_boundary": "NO_CLAIM_EQUIVALENCE_CANONICAL_MEMBER_OR_EVIDENCE_INDEPENDENCE_INFERRED",
            }
        )

    fields = list(rows[0])
    with (REPORTS / "P040_P058_LINE_DELTA.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    diff_lines = difflib.unified_diff(
        p040_text.splitlines(keepends=True),
        p058_text.splitlines(keepends=True),
        fromfile="P040/source/Tsiokos_2026_The_Usefulness_of_Non_Descending_Objects_A_Six_Birds_Theory_of_Mathematical_Applicability.tex",
        tofile="P058/source/Tsiokos_2026_Why_Mathematics_Even_Works.tex",
        n=3,
    )
    patch = "".join(diff_lines)
    (REPORTS / "P040_P058_RAW_TEX_DIFF.patch").write_text(patch, encoding="utf-8")

    equal_p040 = sum(i2 - i1 for tag, i1, i2, _, _ in opcodes if tag == "equal")
    equal_p058 = sum(j2 - j1 for tag, _, _, j1, j2 in opcodes if tag == "equal")
    changed_p040 = len(p040_lines) - equal_p040
    changed_p058 = len(p058_lines) - equal_p058
    summary = {
        "version_family": "VF-SAU-01",
        "p040_path": str(P040.relative_to(ROOT)),
        "p058_path": str(P058.relative_to(ROOT)),
        "p040_sha256": sha256(P040),
        "p058_sha256": sha256(P058),
        "p040_line_count": len(p040_lines),
        "p058_line_count": len(p058_lines),
        "sequence_match_ratio": matcher.ratio(),
        "alignment_block_count": len(opcodes),
        "equal_blocks": counts["equal"],
        "replace_blocks": counts["replace"],
        "delete_blocks": counts["delete"],
        "insert_blocks": counts["insert"],
        "equal_p040_lines": equal_p040,
        "equal_p058_lines": equal_p058,
        "changed_p040_lines": changed_p040,
        "changed_p058_lines": changed_p058,
        "unified_diff_line_count": len(patch.splitlines()),
        "canonical_member": None,
        "step2_started": False,
        "inference_boundary": "raw source delta only; claim-level equivalence and canonicalization deferred to Step 2",
    }
    (GENERATED / "p040_p058_line_delta.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    md = [
        "# P040/P058 exact raw-TeX line delta",
        "",
        "## Scope",
        "",
        "This is the line-by-line version-control artifact required by Step 1 for unresolved near-duplicates. It aligns the immutable raw TeX sources exactly and emits a standard unified diff. It does **not** decide whether corresponding theorems are mathematically equivalent, which paper is canonical, or whether either paper supplies independent evidence.",
        "",
        "## Source identity",
        "",
        f"- P040: `{summary['p040_path']}`; SHA-256 `{summary['p040_sha256']}`; {summary['p040_line_count']} lines.",
        f"- P058: `{summary['p058_path']}`; SHA-256 `{summary['p058_sha256']}`; {summary['p058_line_count']} lines.",
        "",
        "## Alignment census",
        "",
        f"- Exact raw-line SequenceMatcher ratio: **{summary['sequence_match_ratio']:.12f}**.",
        f"- Alignment blocks: **{summary['alignment_block_count']}**.",
        f"- Equal / replace / delete / insert blocks: **{counts['equal']} / {counts['replace']} / {counts['delete']} / {counts['insert']}**.",
        f"- Equal raw lines: P040 **{equal_p040}**, P058 **{equal_p058}**.",
        f"- Non-equal raw lines: P040 **{changed_p040}**, P058 **{changed_p058}**.",
        f"- Unified diff length: **{summary['unified_diff_line_count']}** lines.",
        "",
        "## Products",
        "",
        "- `reports/P040_P058_LINE_DELTA.csv` — all alignment blocks, including equal blocks, with exact one-based source ranges and bounded excerpts.",
        "- `reports/P040_P058_RAW_TEX_DIFF.patch` — exact standard unified diff over the immutable raw TeX files.",
        "- `generated/p040_p058_line_delta.json` — machine-readable source hashes and census.",
        "- `reports/P040_P058_SECTION_DELTA.csv` — complementary 73-slot structural heading alignment.",
        "",
        "## Step-2 boundary",
        "",
        "The family remains `UNRESOLVED_VERSION_FAMILY`, with no canonical member. Step 2 must compare definitions, theorem statements, hypotheses, proof/evidence grades, nonclaims, and formalization references before any canonicalization or evidence deduplication beyond the existing family-level control.",
    ]
    (REPORTS / "P040_P058_LINE_DELTA.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
