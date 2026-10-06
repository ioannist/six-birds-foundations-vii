#!/usr/bin/env python3
"""Create source-located Step-1 reconnaissance cards for all catalogued papers.

The Step-1 contract requires every card to inspect the paper's own
artifact/formalization disclosure.  This generator therefore records a
paper-side disclosure classification and source anchors without promoting that
classification into a local-availability, kernel-build, or theorem-fidelity
claim.  Exact declaration-level matching remains Step 2, except for the
canonical spine reconciliation maintained separately under formalization/.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "derived" / "metadata"
OUT = ROOT / "notes" / "survey"
OUT.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader((ROOT / "config" / "paper_catalog.csv").open(encoding="utf-8")))
version_family = {"P040": "VF-SAU-01", "P058": "VF-SAU-01"}

DEPENDENCY_SUMMARY_PATH = ROOT / "corpus" / "paper_dependency_summary.csv"
DEPENDENCY_EDGES_PATH = ROOT / "corpus" / "paper_dependency_edges.csv"
if not DEPENDENCY_SUMMARY_PATH.is_file() or not DEPENDENCY_EDGES_PATH.is_file():
    raise SystemExit(
        "Dependency reconnaissance is missing. Run scripts/build_paper_dependency_reconnaissance.py before build_survey_cards.py."
    )
with DEPENDENCY_SUMMARY_PATH.open(encoding="utf-8", newline="") as handle:
    dependency_summary = {row["source_paper_id"]: row for row in csv.DictReader(handle)}
with DEPENDENCY_EDGES_PATH.open(encoding="utf-8", newline="") as handle:
    dependency_edges_raw = list(csv.DictReader(handle))
dependency_edges: dict[str, list[dict[str, str]]] = {}
for edge in dependency_edges_raw:
    dependency_edges.setdefault(edge["source_paper_id"], []).append(edge)

DISCLOSURE_TITLE_RE = re.compile(
    r"(?i)(formal|lean|artifact|reproduc|data availability|data and code|"
    r"code availability|supporting evidence|verification|theorem inventory|"
    r"evidence map|repository|mechaniz|proof inventory)"
)
FORMAL_TEXT_RE = re.compile(
    r"(?i)(Lean(?:\s*4)?\s+(?:formal|mechan|theorem|proof|anchor|appendix)|"
    r"Lean[- ](?:backed|checked|side)|formalization\s+(?:for|of|is|in)|"
    r"proof assistant|machine[- ]checked proof|mechanized theorem|"
    r"theorem-track implementation)"
)
ARTIFACT_TEXT_RE = re.compile(
    r"(?i)(artifact source map|artifact pipeline|computational laboratory|"
    r"finite recomputation|frozen audit artifacts|evidence harness|"
    r"supporting evidence|validator(?:s| discipline)?|build outputs)"
)
REPRO_TEXT_RE = re.compile(
    r"(?i)(reproducibility|data and code availability|code availability|"
    r"data availability|github\.com|companion repository|project repository)"
)

# These are Step-1 summaries of unusually easy-to-overread disclosure
# boundaries.  They do not replace claim-level extraction.
DISCLOSURE_OVERRIDES: dict[str, dict[str, str]] = {
    "P003": {
        "formalization_status": "CONDITIONAL_LEAN_SCHEMAS_EMPIRICAL_PREMISES_EXTERNAL",
        "artifact_status": "AUDITED_MACHINE_READABLE_ARTIFACT_PIPELINE",
        "repository_reproducibility_status": "REPRODUCIBILITY_CONTRACT_AND_SOURCE_MAP",
        "finding": (
            "The paper reports typed Lean schemas and conditional proofs, while explicitly "
            "placing empirical premises and witness existence in the audited artifact pipeline; "
            "the type theory does not derive those empirical premises."
        ),
    },
    "P013": {
        "formalization_status": "FINITE_RECOMPUTATION_EXPLICITLY_NOT_PROOF_ASSISTANT",
        "artifact_status": "EXACT_FINITE_COMPUTATION_AND_VALIDATOR_EVIDENCE",
        "repository_reproducibility_status": "PROJECT_REPOSITORY_AND_ARTIFACT_TREE_DISCLOSED",
        "finding": (
            "The paper distinguishes exact reproducible finite computations from machine-checked "
            "proofs in a proof assistant; imported framework theorems and computational verdicts "
            "must remain separate evidence lanes."
        ),
    },
    "P034": {
        "formalization_status": "IN_HOUSE_LEAN_LADDER_PLUS_CONDITIONAL_EXTERNAL_CONTRACT",
        "artifact_status": "SUPPORTING_EMPIRICAL_PERIMETER_DOES_NOT_CARRY_PROOF",
        "repository_reproducibility_status": "LEAN_AND_THEOREM_TRACK_REPOSITORY_DISCLOSED",
        "finding": (
            "The paper reports an in-house Lean ladder for fixed-package and frozen-slice results, "
            "but the arithmetic summit remains conditional on an explicit external dependency "
            "contract; supporting vendor artifacts constrain scope rather than carry the theorem."
        ),
    },
    "P038": {
        "formalization_status": "NO_DEDICATED_PROOF_ASSISTANT_COMPONENT_LOCATED",
        "artifact_status": "SUPPORTING_COMPUTATIONAL_AND_AUDIT_EVIDENCE_ONLY",
        "repository_reproducibility_status": "COMPANION_REPOSITORY_DISCLOSED",
        "finding": (
            "The supporting-evidence appendix says the diagnostics are supportive rather than "
            "foundational and do not enlarge the closed theorem package; the companion repository "
            "therefore cannot be cited as a substitute for the theorem statements."
        ),
    },
    "P047": {
        "formalization_status": "NO_DEDICATED_PROOF_ASSISTANT_COMPONENT_LOCATED",
        "artifact_status": "CODE_CONFIGURATIONS_AND_PROCESSED_RUN_ARTIFACTS_DISCLOSED",
        "repository_reproducibility_status": "CODE_REPOSITORY_AND_PLANNED_DATA_PACKAGE",
        "finding": (
            "The data-availability section names the code repository and a planned reproducibility "
            "package; Step 1 located no dedicated Lean/proof-assistant appendix for this paper."
        ),
    },
    "P056": {
        "formalization_status": "CORPUS_EVIDENCE_DISCUSSION_ONLY_NO_OWN_FORMALIZATION_APPENDIX",
        "artifact_status": "NO_DEDICATED_PAPER_SPECIFIC_ARTIFACT_APPENDIX_LOCATED",
        "repository_reproducibility_status": "UNDERLYING_CORPUS_REPOSITORIES_CITED_ONLY",
        "finding": (
            "This philosophy synthesis discusses the grades and artifacts of the underlying corpus "
            "but does not present a new paper-specific formalization or reproducibility package. "
            "Its claims must inherit the cited papers' grades one source at a time."
        ),
    },
    "P039": {
        "formalization_status": "SOURCE_PACKAGE_BLOCKED",
        "artifact_status": "SOURCE_PACKAGE_BLOCKED",
        "repository_reproducibility_status": "SOURCE_PACKAGE_BLOCKED",
        "finding": (
            "Only the root stub, abstract-level declarations, and include map were supplied; 18 "
            "included TeX files and the bibliography are missing, so the paper's full disclosure "
            "cannot be audited from this archive."
        ),
    },
}



def dependency_section(pid: str) -> str:
    summary = dependency_summary[pid]
    edges = sorted(
        dependency_edges.get(pid, []),
        key=lambda edge: (int(edge["target_paper_id"][1:]), edge["target_paper_id"]),
    )
    lines: list[str] = []
    if edges:
        for edge in edges:
            source_lines = ", ".join(f"L{x}" for x in edge["source_lines"].split(";") if x)
            lines.append(
                f"- **{edge['target_paper_id']} — {edge['target_title']}**; "
                f"citation key(s) `{edge['citation_keys'].replace(';', '`, `')}`; "
                f"source-root {source_lines}."
            )
    elif summary["status"] == "SOURCE_PACKAGE_BLOCKED":
        lines.append(
            "- No in-corpus paper dependency can be recovered from the supplied root stub; "
            "the missing includes and bibliography make this a source-package limitation, not evidence of independence."
        )
    else:
        lines.append(
            "- No in-corpus citation was resolved at survey depth. This is not evidence that the paper is logically or historically independent."
        )

    if summary["out_of_corpus_keys"]:
        lines.append(f"- **Named corpus-like work outside the 58-paper catalog:** {summary['out_of_corpus_keys']}.")
    if summary["unresolved_internal_keys"]:
        lines.append(f"- **Unresolved internal-looking citation:** {summary['unresolved_internal_keys']}.")
    if summary["non_paper_internal_keys"]:
        lines.append(f"- **Internal non-paper citation:** {summary['non_paper_internal_keys']}.")
    if summary["self_reference_keys"]:
        lines.append(f"- **Self/family key suppressed as an edge:** `{summary['self_reference_keys'].replace(';', '`, `')}`.")

    lines.append(
        "- **Inference boundary:** these are citation/navigation signals only. They do not establish theorem inheritance, statement equivalence, bridge validity, or evidentiary independence; those are Step-2 questions."
    )
    return "\n".join(lines)

def sentences(s: str, n: int = 3) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return "No abstract was recoverable automatically; use the source outline and formal inventory below."
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"`])", s)
    return " ".join(parts[:n])


def clean(s: str, limit: int = 700) -> str:
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def keyword(meta: dict[str, Any], key: str, limit: int = 3) -> list[dict[str, Any]]:
    vals = meta.get("keyword_paragraphs", {}).get(key, [])
    return vals[:limit]


def formal_rows(meta: dict[str, Any]) -> list[dict[str, Any]]:
    allowed = {"theorem", "proposition", "lemma", "corollary"}
    return [
        h
        for h in meta.get("environment_headers", [])
        if h.get("kind") in allowed and h.get("name_plain", "").strip()
    ]


def defs(meta: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        h
        for h in meta.get("environment_headers", [])
        if h.get("kind") == "definition" and h.get("name_plain", "").strip()
    ]


def source_grade(meta: dict[str, Any]) -> list[str]:
    text = " ".join(
        [meta.get("abstract", "")]
        + [
            v.get("text", "")
            for k in meta.get("keyword_paragraphs", {}).values()
            for v in k
        ]
    ).lower()
    labels: list[str] = []
    count = Counter(h.get("kind") for h in meta.get("environment_headers", []))
    if count["theorem"] or count["lemma"] or count["proposition"] or count["corollary"]:
        labels.append(
            f"formal prose inventory: {count['theorem']} theorem(s), {count['proposition']} "
            f"proposition(s), {count['lemma']} lemma(s), {count['corollary']} "
            "corollary/corollaries detected"
        )
    if "lean" in text or "mechaniz" in text or "machine-check" in text:
        labels.append(
            "paper reports a Lean/mechanized or machine-checked component; exact coverage remains paper-scoped"
        )
    if any(
        w in text
        for w in (
            "exact-finite",
            "exact finite",
            "exhaustively enumerated",
            "deterministic python",
            "computational",
        )
    ):
        labels.append("paper reports finite/computational evidence or exact-finite enumeration")
    if any(w in text for w in ("conditional", "schema", "conjectur")):
        labels.append("paper contains conditional/schema-grade boundaries that must be retained")
    return labels or [
        "status must be read from the source claim lanes; no uniform theorem grade inferred from the title"
    ]


def disclosure_for(row: dict[str, str], meta: dict[str, Any]) -> dict[str, str]:
    pid = row["paper_id"]
    source_path = ROOT / "source" / row["source_path"]
    raw = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else ""
    anchors = [
        s
        for s in meta.get("sections", [])
        if DISCLOSURE_TITLE_RE.search(s.get("title_plain", ""))
    ]
    anchor_text = "; ".join(
        f"expanded-source L{s['line']} {s['level']} “{clean(s['title_plain'], 100)}”"
        for s in anchors[:12]
    )
    if len(anchors) > 12:
        anchor_text += f"; … {len(anchors) - 12} more disclosure-related headings"
    if not anchor_text:
        anchor_text = "no dedicated disclosure heading located in the supplied source surface"

    if pid in DISCLOSURE_OVERRIDES:
        status = dict(DISCLOSURE_OVERRIDES[pid])
    else:
        formal = bool(FORMAL_TEXT_RE.search(raw)) or any(
            re.search(r"(?i)(lean|formalization|mechaniz|formal core|theorem inventory)", s.get("title_plain", ""))
            for s in anchors
        )
        artifact = bool(ARTIFACT_TEXT_RE.search(raw)) or any(
            re.search(r"(?i)(artifact|supporting evidence|evidence map|verification)", s.get("title_plain", ""))
            for s in anchors
        )
        repro = bool(REPRO_TEXT_RE.search(raw)) or any(
            re.search(r"(?i)(reproduc|availability|repository)", s.get("title_plain", ""))
            for s in anchors
        )
        status = {
            "formalization_status": (
                "FORMAL_OR_PROOF_ASSISTANT_COMPONENT_DISCLOSED"
                if formal
                else "NO_DEDICATED_FORMAL_COMPONENT_LOCATED_AT_SURVEY_DEPTH"
            ),
            "artifact_status": (
                "COMPUTATIONAL_AUDIT_OR_SUPPORT_ARTIFACTS_DISCLOSED"
                if artifact
                else "NO_DEDICATED_ARTIFACT_COMPONENT_LOCATED_AT_SURVEY_DEPTH"
            ),
            "repository_reproducibility_status": (
                "REPOSITORY_OR_REPRODUCIBILITY_ROUTE_DISCLOSED"
                if repro
                else "NO_DEDICATED_REPOSITORY_OR_REPRODUCIBILITY_ROUTE_LOCATED"
            ),
            "finding": (
                "The paper contains the located disclosure surface. Step 1 records its existence "
                "and scope anchors only; exact theorem-to-file fidelity, ownership versus import, "
                "trust assumptions, and executable availability remain declaration-level work."
            ),
        }

    status.update(
        {
            "paper_id": pid,
            "source_path": row["source_path"],
            "reading_state": "DEEP_READ" if meta.get("step_1_depth") == "DEEP_READ" else "SURVEYED",
            "disclosure_anchor_count": str(len(anchors)),
            "disclosure_anchors": anchor_text,
            "card_path": f"notes/survey/{pid}.md",
            "local_reuse_boundary": (
                "PAPER_SIDE_ONLY_UNLESS_EXPLICITLY_RECONCILED_IN_FORMALIZATION_INTEGRATION; "
                "NO_LOCAL_BUILD_OR_AVAILABILITY_INFERENCE"
            ),
        }
    )
    return status


cluster_role = {
    "A_CANONICAL_SPINE": "Canonical source: definitions and theorem scope constrain any Foundations VII construction.",
    "B_VII_NEAR_INTERACTION_ACCESS": "Direct precursor/near-neighbor: likely supplies objects, countermodels, or bridge obligations for access, interaction, promotion, memory, or directionality.",
    "C_PHILOSOPHY_METATHEORY": "Metatheory/philosophy control: clarifies what SBT licenses ontologically and how cross-layer usefulness or realization must be audited.",
    "D_COGNITION_SOCIAL": "Endogenous/cognition/social pressure test: distinguishes carried structure, agency/enablement, language, institutions, and observer/theorist contribution.",
    "E_DOMAIN_PRESSURE_TESTS": "Domain pressure test only: useful for counterexamples and bridge stress, but application-specific conclusions may not be promoted into VII without an explicit map.",
}

index: list[dict[str, Any]] = []
disclosure_rows: list[dict[str, str]] = []
for row in sorted(rows, key=lambda r: int(r["reading_order"])):
    pid = row["paper_id"]
    meta = json.load((META / f"{pid}.json").open(encoding="utf-8"))
    state = "DEEP_READ" if meta.get("step_1_depth") == "DEEP_READ" else "SURVEYED"
    frows = formal_rows(meta)
    drows = defs(meta)
    problem = sentences(meta.get("abstract", ""), 3)

    result_lines: list[str] = []
    for h in frows[:12]:
        label = f" (`{h['label']}`)" if h.get("label") else ""
        result_lines.append(
            f"- **{h['kind'].title()}**, expanded-source L{h['line']}: "
            f"{clean(h['name_plain'], 220)}{label}."
        )
    if not result_lines:
        for v in keyword(meta, "contribution", 3):
            result_lines.append(
                f"- Result/contribution passage, expanded-source L{v['line']}: {clean(v['text'], 520)}"
            )
    if not result_lines:
        result_lines = [
            "- No named standard theorem environment was recovered; the abstract and section map are the Step-1 authority, and the paper is flagged for manual claim-macro extraction in Step 2."
        ]

    obj_lines: list[str] = []
    for h in drows[:10]:
        label = f" (`{h['label']}`)" if h.get("label") else ""
        obj_lines.append(
            f"- {clean(h['name_plain'], 180)} — expanded-source L{h['line']}{label}."
        )
    if not obj_lines:
        obj_lines = [
            f"- Objects named by the abstract/title and catalog hook: {row['foundations_vii_hooks']}.",
            "- No standard `definition` environment was recovered; inspect custom macros in Step 2.",
        ]

    scope: list[str] = []
    for key in ("limitation", "nonclaim"):
        for v in keyword(meta, key, 3):
            item = f"- Expanded-source L{v['line']}: {clean(v['text'], 650)}"
            if item not in scope:
                scope.append(item)
    if not scope:
        scope = [
            "- No explicit scope paragraph was recovered automatically; do not infer universality. Re-open the conclusion/nonclaim section in Step 2."
        ]

    future = [
        f"- Expanded-source L{v['line']}: {clean(v['text'], 600)}"
        for v in keyword(meta, "future", 3)
    ]
    if not future:
        future = [
            "- No explicit future-work paragraph was recovered automatically; open questions remain those stated in the paper’s conclusion/limitations."
        ]

    outline = [
        f"- L{s['line']} `{s['level']}` — {clean(s['title_plain'], 180)}"
        for s in meta.get("sections", [])[:18]
    ]
    if len(meta.get("sections", [])) > 18:
        outline.append(
            f"- … {len(meta['sections']) - 18} additional section/subsection headings in `derived/metadata/{pid}.json`."
        )

    grades = "\n".join(f"- {g}." for g in source_grade(meta))
    vf = version_family.get(pid, "—")
    uncertainties: list[str] = []
    if pid in version_family:
        uncertainties.append(
            "This paper belongs to unresolved version family `VF-SAU-01`; filename and internal title are crossed. Cite by paper ID and hash."
        )
    if pid == "P020":
        uncertainties.append(
            "The standard converter failed on malformed verbatim markup; the committed conservative full-TeX fallback is the Step-1 reading surface."
        )
    if pid == "P039":
        uncertainties.append(
            "The supplied root declares 18 absent input/include files and a missing bibliography; only the root-stub surface is available, so claim-level extraction is blocked."
        )
    if not frows:
        uncertainties.append(
            "Custom theorem macros or prose-form claims were not captured by the generic environment parser; Step 2 must enumerate them manually."
        )
    if not uncertainties:
        uncertainties.append(
            "Step 1 records scope and navigation only; theorem hypotheses/proofs still require Step-2 claim extraction."
        )

    rel = cluster_role[row["cluster"]] + " Specific hook: " + row["foundations_vii_hooks"] + "."
    disclosure = disclosure_for(row, meta)
    disclosure_rows.append(disclosure)

    card = f"""# {pid} — {row['title']}

## Provenance and reading status

- **Catalog order:** {row['reading_order']}.
- **Reading state after Step 1:** `{state}`.
- **Cluster:** `{row['cluster']}`.
- **Source:** `{row['source_path']}`.
- **Root SHA-256:** `{meta['root_sha256']}`.
- **Dependency-tree SHA-256:** `{meta['tree_sha256']}`.
- **Version family:** `{vf}`.
- **Recovered date:** {meta.get('date') or 'not declared/recovered'}.
- **Recovered plain-text word count:** {meta.get('plain_word_count', 0)}.
- **Review basis:** abstract; introduction/section map; named definition/result inventory; scope/nonclaim passages; future-work passages; citation-level corpus dependencies; artifact/formalization disclosure. TeX remains authoritative.

## Problem and thesis

{problem}

## Core objects and definitions located

{chr(10).join(obj_lines)}

## Principal result inventory

{chr(10).join(result_lines)}

## Claim/evidence class visible at survey depth

{grades}

No result is upgraded beyond the paper’s own theorem/schema/model/calibration/interpretation lane merely because it appears in this inventory.

## Artifact and formalization disclosure

- **Formalization status:** `{disclosure['formalization_status']}`.
- **Artifact/evidence status:** `{disclosure['artifact_status']}`.
- **Repository/reproducibility status:** `{disclosure['repository_reproducibility_status']}`.
- **Located anchors:** {disclosure['disclosure_anchors']}.
- **Step-1 finding:** {disclosure['finding']}
- **Local-reuse boundary:** paper-side disclosure is not evidence that the asset is present, import-compatible, kernel-checked here, or statement-equivalent. Consult `formalization/integration/` and `synthesis/FORMALIZATION_EVIDENCE_LADDER.md` before any reuse.

## Assumptions, scope, and nonclaims

{chr(10).join(scope)}

## Open questions / deferred work

{chr(10).join(future)}

## Corpus-paper dependencies visible at survey depth

{dependency_section(pid)}

## Foundations VII relevance

{rel}

The Step-1 use is reconnaissance and dependency control. Any theorem imported later needs a bridge record identifying the exact source object, target object, map, inherited hypotheses, and nonclaims.

## Source map

{chr(10).join(outline) if outline else '- No section headings recovered; inspect source directly.'}

## Reader uncertainties and Step-2 revisit

{chr(10).join('- ' + u for u in uncertainties)}
"""
    (OUT / f"{pid}.md").write_text(card, encoding="utf-8")
    index.append(
        dict(
            paper_id=pid,
            reading_order=row["reading_order"],
            title=row["title"],
            state=state,
            cluster=row["cluster"],
            source_path=row["source_path"],
            root_sha256=meta["root_sha256"],
            version_family=vf,
            card=f"notes/survey/{pid}.md",
            definitions_detected=len(drows),
            formal_results_detected=len(frows),
            section_headings=len(meta.get("sections", [])),
            disclosure_anchor_count=disclosure["disclosure_anchor_count"],
            resolved_dependency_count=dependency_summary[pid]["resolved_target_count"],
            unresolved_internal_dependency_keys=dependency_summary[pid]["unresolved_internal_key_count"],
            out_of_corpus_dependency_keys=dependency_summary[pid]["out_of_corpus_key_count"],
        )
    )

with (ROOT / "corpus" / "survey_index.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(index[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(index)

with (ROOT / "corpus" / "survey_artifact_formalization.csv").open(
    "w", newline="", encoding="utf-8"
) as f:
    fields = [
        "paper_id",
        "source_path",
        "reading_state",
        "formalization_status",
        "artifact_status",
        "repository_reproducibility_status",
        "disclosure_anchor_count",
        "disclosure_anchors",
        "finding",
        "local_reuse_boundary",
        "card_path",
    ]
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(disclosure_rows)

summary = [
    "# Step-1 survey-card index",
    "",
    f"Generated {len(index)} source-located cards. Every card includes an explicit citation-level corpus-dependency section and an artifact/formalization disclosure section. Dependency products are under `corpus/paper_dependency_*.csv`; the 58-row disclosure audit is `corpus/survey_artifact_formalization.csv`.",
    "",
    "| ID | Order | State | Cluster | Resolved dependencies | Disclosure anchors | Card |",
    "|---|---:|---|---|---:|---:|---|",
]
for r in index:
    summary.append(
        f"| {r['paper_id']} | {r['reading_order']} | {r['state']} | {r['cluster']} | "
        f"{r['resolved_dependency_count']} | {r['disclosure_anchor_count']} | [`{r['paper_id']}.md`](../notes/survey/{r['paper_id']}.md) |"
    )
(ROOT / "reports" / "SURVEY_CARD_INDEX.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

formal_counts = Counter(row["formalization_status"] for row in disclosure_rows)
artifact_counts = Counter(row["artifact_status"] for row in disclosure_rows)
no_anchor = [row["paper_id"] for row in disclosure_rows if row["disclosure_anchor_count"] == "0"]
audit_md = [
    "# Survey artifact/formalization disclosure audit",
    "",
    "## Result",
    "",
    f"All **{len(disclosure_rows)}** paper cards now contain a dedicated, source-located disclosure section. This is a Step-1 paper-side audit, not a declaration-level equivalence or local build claim.",
    "",
    "- Formalization-status distribution: "
    + ", ".join(f"`{k}`={v}" for k, v in sorted(formal_counts.items()))
    + ".",
    "- Artifact-status distribution: "
    + ", ".join(f"`{k}`={v}" for k, v in sorted(artifact_counts.items()))
    + ".",
    f"- Papers without a dedicated disclosure heading: {', '.join(no_anchor) if no_anchor else 'none'}. Their card findings state the exact limitation.",
    "",
    "## Anti-overread controls",
    "",
    "- P003: conditional Lean schemas do not derive empirical artifact premises.",
    "- P013: exact finite recomputation is explicitly not proof-assistant verification.",
    "- P034: the in-house Lean ladder is separated from the conditional arithmetic contract and empirical perimeter.",
    "- P038: support diagnostics do not enlarge the theorem package.",
    "- P056: a philosophy synthesis inherits evidence grades from cited papers; it does not create a new formal artifact.",
    "- P039: the full disclosure remains unauditable because the supplied source package is incomplete.",
    "",
    "## Step-2 boundary",
    "",
    "The audit records disclosure surfaces and high-risk status boundaries only. Exact theorem/declaration mappings, hypotheses, trust dependencies, imported-versus-owned status, execution results, and bridge judgments remain Step-2 records.",
]
(ROOT / "reports" / "SURVEY_ARTIFACT_FORMALIZATION_AUDIT.md").write_text(
    "\n".join(audit_md) + "\n", encoding="utf-8"
)
print(
    f"survey_cards={len(index)} deep_marked={sum(r['state'] == 'DEEP_READ' for r in index)} "
    f"disclosure_rows={len(disclosure_rows)} no_anchor={len(no_anchor)}"
)
