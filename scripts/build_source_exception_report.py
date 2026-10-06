#!/usr/bin/env python3
"""Record source/extraction exceptions without weakening source-grounding claims."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
CORPUS = ROOT / "corpus"
REPORTS = ROOT / "reports"
DECISIONS = ROOT / "decisions"
P039_CARD = ROOT / "notes" / "survey" / "P039.md"


def catalog_row(pid: str) -> dict[str, str]:
    with (ROOT / "config" / "paper_catalog.csv").open(newline="", encoding="utf-8") as f:
        return next(r for r in csv.DictReader(f) if r["paper_id"] == pid)


def missing_inputs(root: Path) -> list[str]:
    text = root.read_text(encoding="utf-8", errors="replace")
    out: list[str] = []
    for m in re.finditer(r"\\(?:input|include)\s*\{([^}]+)\}", text):
        raw = m.group(1).strip()
        candidate = root.parent / raw
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".tex")
        if not candidate.exists():
            out.append(str(candidate.relative_to(SOURCE)))
    return out


p020 = catalog_row("P020")
p039 = catalog_row("P039")
p039_root = SOURCE / p039["source_path"]
missing = missing_inputs(p039_root)
if len(missing) != 18:
    raise SystemExit(f"Expected 18 missing P039 input/include files, found {len(missing)}")
references = p039_root.parent / "references.bib"
reference_status = "missing" if not references.exists() else "present"

rows = [
    {
        "paper_id": "P020",
        "exception_type": "CONVERTER_FAILURE_RECOVERED",
        "source_completeness": "COMPLETE_IN_SUPPLIED_ARCHIVE",
        "step1_reading_scope": "SURVEY_FROM_FULL_TEX_AND_RECOVERED_PLAIN_TEXT",
        "details": "Malformed verbatim markup prevents standard Pandoc/detex conversion. The repository conservative TeX stripper recovered 11,741 words, 83 section headings, and 24 standard environments. Frozen TeX remains authoritative.",
        "blocking_status": "NOT_BLOCKING_STEP1",
        "required_follow_up": "Retain fallback path; inspect the malformed verbatim site before any publication-source rebuild.",
    },
    {
        "paper_id": "P039",
        "exception_type": "INCOMPLETE_SOURCE_PACKAGE",
        "source_completeness": "ROOT_STUB_ONLY_18_DECLARED_INPUTS_MISSING",
        "step1_reading_scope": "ABSTRACT_ROOT_DECLARATIONS_AND_INCLUDE_MAP_ONLY",
        "details": f"The frozen root is 6,071 bytes and declares 18 input/include files that are absent. references.bib is {reference_status}. No PDF or alternate full-text copy was supplied in the archive.",
        "blocking_status": "BLOCKED_FULL_TEXT",
        "required_follow_up": "Supply the 18 included TeX files and bibliography, or an authoritatively matched full source/PDF, before claim-level extraction.",
    },
]
CORPUS.mkdir(parents=True, exist_ok=True)
with (CORPUS / "source_exceptions.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
(CORPUS / "source_exceptions.json").write_text(json.dumps({"exceptions": rows, "p039_missing_inputs": missing}, indent=2) + "\n", encoding="utf-8")

report = [
    "# Source extraction and package exceptions",
    "",
    "Step 1 treats frozen TeX as authoritative and records any limitation that changes the evidentiary depth of a paper. No OCR, web replacement, or silently substituted edition was used.",
    "",
    "## P020 — converter failure, recovered",
    "",
    "The supplied paper source is present, but malformed verbatim markup breaks the standard conversion path. A conservative repository TeX stripper recovered **11,741 words**, **83 section headings**, and **24 standard theorem/definition environments**. Its survey card therefore uses the full supplied TeX tree plus the recovered plain text. This is not a Step-1 coverage blocker.",
    "",
    "## P039 — incomplete supplied source package",
    "",
    "The supplied root contains its title, abstract, preamble, and document assembly map, but all **18** declared `\\input`/`\\include` files are absent. `references.bib` is also absent. Consequently the P039 card is limited to the root abstract, declarations, and the names/order of the missing sections and appendices. It is **not** represented as a full-paper read.",
    "",
    "Missing declared files:",
    "",
]
report.extend(f"- `{path}`" for path in missing)
report += [
    "",
    "**Status:** `BLOCKED_FULL_TEXT`. Step 2 may not create a claim/proof/nonclaim dossier for P039 until a complete, authoritatively matched source package or PDF is supplied. P039 remains useful only as a clearly scoped domain-pressure-test stub.",
    "",
    "## Consequence for Step-1 completion",
    "",
    "The exception does not invalidate the canonical SBT spine, law registries, wish-list synthesis, or the other 57 paper cards. It does qualify the statement ‘all papers’: Step 1 has complete source-located coverage for 57 papers and root-stub-level coverage for P039, with the deficit mechanically exposed here and in its survey card.",
]
REPORTS.mkdir(parents=True, exist_ok=True)
(REPORTS / "SOURCE_EXTRACTION_EXCEPTIONS.md").write_text("\n".join(report) + "\n", encoding="utf-8")

adr = """# ADR-0005 — Incomplete source packages and converter failures

**Status:** accepted for Step 1.

A failed converter does not reduce a complete TeX source to an unread paper, and an incomplete source package must not be made to look complete by inference. P020 is read from its full frozen TeX with a conservative plain-text fallback. P039 is represented only at the depth supported by its root stub: abstract, declarations, and include map. The missing 18 included files and bibliography are an explicit `BLOCKED_FULL_TEXT` condition for Step 2. No web copy, OCR reconstruction, or guessed section content may be substituted without a separate provenance decision.
"""
DECISIONS.mkdir(parents=True, exist_ok=True)
(DECISIONS / "ADR-0005-source-package-exceptions.md").write_text(adr, encoding="utf-8")

# Add an idempotent warning to the P039 card after the title.
card = P039_CARD.read_text(encoding="utf-8")
card = re.sub(r"\n<!-- SOURCE-LIMITATION:BEGIN -->.*?<!-- SOURCE-LIMITATION:END -->\n", "\n", card, flags=re.S)
warning = """
<!-- SOURCE-LIMITATION:BEGIN -->
> **Source-package limitation — `BLOCKED_FULL_TEXT`:** the supplied archive contains only this paper's 6,071-byte root stub. All 18 declared section/appendix/macro inputs and `references.bib` are absent. This card is grounded only in the root title, abstract, declarations, and include map; it is not a full-paper read.
<!-- SOURCE-LIMITATION:END -->
"""
first_nl = card.find("\n")
card = card[:first_nl+1] + warning + card[first_nl+1:]
card = card.replace(
    "- **Review basis:** abstract; introduction/section map; named definition/result inventory; scope/nonclaim passages; future-work passages. TeX remains authoritative.",
    "- **Review basis:** root title and abstract; preamble declarations; declared section/appendix include map. The 18 included files are absent, so no body claims, proofs, scope passages, or future-work passages were available. TeX remains authoritative.",
)
card = card.replace(
    "the abstract and section map are the Step-1 authority",
    "the root abstract and declared include map are the Step-1 authority",
)
card = card.replace(
    "- No section headings recovered; inspect source directly.",
    "- The root declares 13 section files and 4 appendix files, but those files and the shared macro include are absent from the supplied package; see `reports/SOURCE_EXTRACTION_EXCEPTIONS.md`.",
)
card = card.replace(
    "- Imported plain-text word count is anomalously small; TeX abstract/outline are intact. Rebuild extraction before Step 2.",
    "- Full-text extraction is blocked by a source-package deficit, not merely a converter defect. Obtain the 18 missing includes and bibliography before Step-2 claim extraction.",
)
P039_CARD.write_text(card, encoding="utf-8")

print(f"exceptions={len(rows)} p039_missing_inputs={len(missing)} references={reference_status}")
