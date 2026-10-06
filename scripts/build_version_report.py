#!/usr/bin/env python3
"""Build Step-1 duplicate/version-family diagnostics for the frozen paper corpus."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
CATALOG = ROOT / "config" / "paper_catalog.csv"
OUT_CSV = ROOT / "corpus" / "version_families.csv"
OUT_PAIRS = ROOT / "corpus" / "similarity_pairs.csv"
OUT_MD = ROOT / "reports" / "VERSION_FAMILY_REPORT.md"

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")
TITLE_RE = re.compile(r"\\title\{(.*?)\}\s*\\author", re.S)


def normalize_tex(text: str) -> list[str]:
    # Preserve theorem/definition vocabulary but discard TeX boilerplate and comments.
    text = re.sub(r"(?m)%.*$", " ", text)
    text = re.sub(r"\\(?:usepackage|documentclass|hypersetup|bibliography|bibliographystyle)\b.*", " ", text)
    return [t.lower() for t in TOKEN_RE.findall(text)]


def internal_title(text: str) -> str:
    m = TITLE_RE.search(text)
    if not m:
        return ""
    raw = m.group(1)
    raw = re.sub(r"\\(?:textbf|emph|ensuremath)\{([^{}]*)\}", r"\1", raw)
    raw = raw.replace("\\\\", ": ")
    raw = re.sub(r"\\[A-Za-z]+", "", raw)
    raw = raw.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", raw).strip()


def shingle_jaccard(docs: dict[str, list[str]], width: int = 5) -> dict[tuple[str, str], float]:
    """Use long lexical shingles so shared SBT boilerplate does not dominate."""
    shingles: dict[str, set[tuple[str, ...]]] = {}
    for pid, toks in docs.items():
        shingles[pid] = set(zip(*(toks[i:] for i in range(width)))) if len(toks) >= width else set()
    out: dict[tuple[str, str], float] = {}
    ids = sorted(docs)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            union = shingles[a] | shingles[b]
            out[(a, b)] = len(shingles[a] & shingles[b]) / (len(union) or 1)
    return out


def main() -> None:
    rows = list(csv.DictReader(CATALOG.open(encoding="utf-8")))
    by_id = {r["paper_id"]: r for r in rows}
    docs: dict[str, list[str]] = {}
    metadata: dict[str, dict[str, str]] = {}
    sha_to_ids: dict[str, list[str]] = {}
    for r in rows:
        p = SOURCE / r["source_path"]
        text = p.read_text(encoding="utf-8", errors="replace")
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        sha_to_ids.setdefault(sha, []).append(r["paper_id"])
        docs[r["paper_id"]] = normalize_tex(text)
        metadata[r["paper_id"]] = {
            "catalog_title": r["title"],
            "internal_title": internal_title(text),
            "source_path": r["source_path"],
            "sha256": sha,
        }

    sims = shingle_jaccard(docs)
    ranked = sorted(sims.items(), key=lambda kv: kv[1], reverse=True)
    with OUT_PAIRS.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["paper_a", "paper_b", "five_word_shingle_jaccard", "classification", "note"])
        for (a, b), score in ranked[:30]:
            if {a, b} == {"P040", "P058"}:
                cls = "version-family"
                note = "near-duplicate architecture; filenames and internal titles are crossed"
            elif score >= 0.10:
                cls = "manual-review"
                note = "high textual similarity; inspect before treating as independent"
            elif score >= 0.01:
                cls = "thematically-related"
                note = "shared vocabulary or source/application relation; not a version on Step-1 evidence"
            else:
                cls = "background"
                note = "reported only as next-nearest context"
            w.writerow([a, b, f"{score:.6f}", cls, note])

    families = [
        {
            "family_id": "VF-SAU-01",
            "members": "P040;P058",
            "status": "UNRESOLVED_VERSION_FAMILY",
            "canonical_member": "",
            "evidence": f"five-word-shingle Jaccard {sims[tuple(sorted(('P040','P058')))]:.6f}; same 73-section architecture; exact raw-TeX line alignment and unified diff recorded; distinct root hashes; filenames and internal titles crossed",
            "step1_ruling": "retain both stable IDs and hashes; do not double-count claims; structural delta is recorded in reports/P040_P058_SECTION_DELTA.* and exact source-line control in reports/P040_P058_LINE_DELTA.* plus reports/P040_P058_RAW_TEX_DIFF.patch; defer theorem/claim canonicalization to Step 2",
        }
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(families[0]), lineterminator="\n")
        w.writeheader(); w.writerows(families)

    exact_dups = [ids for ids in sha_to_ids.values() if len(ids) > 1]
    top = ranked[:12]
    md = []
    md.append("# Version-family and duplicate report\n")
    md.append("## Decision\n")
    md.append(
        "Step 1 found **no byte-identical paper roots** and one material near-duplicate/version family: "
        "`VF-SAU-01 = {P040, P058}`. Both files are retained. Their claims must not be counted as two independent results until Step 2 completes a claim-level comparison.\n"
    )
    md.append("## VF-SAU-01 — mathematical-applicability / SAU family\n")
    for pid in ("P040", "P058"):
        m = metadata[pid]
        md.append(f"- **{pid} catalog title:** {m['catalog_title']}.")
        md.append(f"  - Internal `\\title`: **{m['internal_title']}**.")
        md.append(f"  - Root SHA-256: `{m['sha256']}`.")
        md.append(f"  - Source: `{m['source_path']}`.")
    score = sims[tuple(sorted(("P040", "P058")))]
    md.append(f"\nThe normalized source-text five-word-shingle Jaccard is **{score:.4f}**. Both expose the same 73-section architecture and the same Strict Audited Utility theorem family, while differing substantively in editorial organization and theorem presentation. The archive filenames and internal titles are crossed: the file catalogued as P040 internally calls itself *Why Mathematics Even Works*, while the file catalogued as P058 internally calls itself *The Usefulness of Non-Descending Objects*. This is a provenance defect, not grounds for silently renaming either frozen source.\n")
    md.append("**Ruling:** preserve the supplied filenames, stable IDs, and hashes; mark both `VF-SAU-01`; use one family-level evidence source in Step-1 synthesis. Step 1 records the 73-slot structural delta in `reports/P040_P058_SECTION_DELTA.*` and exact raw-TeX line alignment in `reports/P040_P058_LINE_DELTA.*` plus `reports/P040_P058_RAW_TEX_DIFF.patch`; a canonical member and theorem/claim-level delta remain deferred to Step 2.\n")
    md.append("## Exact duplicates\n")
    md.append("None among the 58 root TeX files.\n" if not exact_dups else "- " + "\n- ".join("; ".join(x) for x in exact_dups) + "\n")
    md.append("## Nearest textual neighbors\n")
    md.append("The long-shingle similarity scan is a triage instrument, not a semantic identity test. The top pairs are:\n")
    md.append("| Pair | Jaccard | Step-1 classification |\n|---|---:|---|")
    for (a,b), score in top:
        if {a,b} == {"P040","P058"}:
            c = "unresolved version family"
        elif score >= .10:
            c = "manual review"
        elif score >= .01:
            c = "thematically related; not versions"
        else:
            c = "background"
        md.append(f"| {a} / {b} | {score:.4f} | {c} |")
    md.append("\nExamples below the version threshold include source/application pairs and papers sharing a problem family. Their overlap does not license claim duplication, claim transfer, or replacement of one source by another.\n")
    md.append("## Step-2 obligation\n")
    md.append("Build the theorem/claim-level delta for P040/P058 on top of the completed 73-slot structural alignment and exact raw-source line ledger, identify the later/controlling statement for each theorem, and record whether differences are editorial, hypothesis-level, proof-level, or status-level. The line ledger is navigation and provenance control, not a semantic equivalence judgment. Until then, all citations remain member-specific.\n")
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"families={len(families)} exact_duplicate_groups={len(exact_dups)} family_score={sims[tuple(sorted(("P040", "P058")))]:.6f}")

if __name__ == "__main__":
    main()
