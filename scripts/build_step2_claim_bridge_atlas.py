#!/usr/bin/env python3
"""Build Step-2 bridges, no-go scopes, interaction taxonomies, application
pressure tests, wish-list evidence links, and the canonical claim graph.

This script consumes the canonical claim corpus produced by
``build_step2_claims.py``.  It never re-extracts claims, so every downstream
artifact uses one stable claim-ID space.
"""
from __future__ import annotations

import csv
import difflib
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from step2_common import (
    ROOT, METADATA, find_expanded_path, json_load, lexical_similarity, normalize_tokens,
    read_csv, source_line_map, strip_comments_preserve_lines, tex_to_plain, write_csv, write_jsonl,
)

TODAY = "2026-07-26"
BRIDGE_DIR = ROOT / "bridges"
SYNTH_DIR = ROOT / "synthesis" / "step2"
REPORT_DIR = ROOT / "reports"
WISH_DIR = ROOT / "wishlists"
GENERATED = ROOT / "generated"

for p in (BRIDGE_DIR, SYNTH_DIR, REPORT_DIR, WISH_DIR, GENERATED):
    p.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def compact(text: Any, limit: int = 700) -> str:
    if text is None:
        return ""
    if isinstance(text, (dict, list)):
        text = json.dumps(text, ensure_ascii=False, sort_keys=True)
    s = re.sub(r"\s+", " ", str(text)).strip()
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def hypothesis_texts(claim: dict[str, Any], limit: int = 16) -> list[str]:
    out: list[str] = []
    for h in claim.get("hypotheses", []) or []:
        if isinstance(h, dict):
            t = h.get("text") or h.get("hypothesis") or compact(h)
        else:
            t = str(h)
        t = compact(t, 500)
        if t and t not in out:
            out.append(t)
    return out[:limit]


def typed_object_text(claim: dict[str, Any]) -> str:
    vals: list[str] = []
    for obj in claim.get("typed_objects", []) or []:
        if isinstance(obj, dict):
            symbol = compact(obj.get("symbol_or_phrase", ""), 100)
            role = compact(obj.get("declared_type_or_role", ""), 180)
            val = f"{symbol}: {role}" if symbol and role else symbol or role
        else:
            val = compact(obj, 180)
        if val and val not in vals:
            vals.append(val)
    if vals:
        return "; ".join(vals[:12])
    return compact(claim.get("normalized_claim", ""), 360)


def transform_formalization(claim: dict[str, Any]) -> dict[str, Any]:
    f = claim.get("formalization") or {}
    decls = f.get("declarations", []) or []
    names: list[Any] = []
    for d in decls:
        if isinstance(d, dict):
            names.append(d.get("name") or d)
        else:
            names.append(d)
    return {
        "source_modules": f.get("modules", []) or [],
        "source_declarations": names,
        "paper_reported_declarations": f.get("paper_reported_declarations", []) or [],
        "target_declarations": [],
        "adapter_declarations": [],
        "statement_delta": f.get("statement_delta", []) or [],
        "inherited_trust_base": f.get("trust_base", []) or [],
        "added_trust_base": [],
        "machine_check_status": f.get("elaboration_status", "NOT_APPLICABLE_OR_NO_LOCAL_MATCH"),
        "source_match_status": f.get("status", "NO_MATCH"),
        "exact_hypothesis_match": f.get("exact_hypothesis_match"),
        "exact_conclusion_match": f.get("exact_conclusion_match"),
        "caveats": f.get("caveats", []) or [],
    }


def load_claims() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    claims = read_jsonl(ROOT / "registry" / "claims.jsonl")
    by_id = {c["claim_id"]: c for c in claims}
    by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in claims:
        by_paper[c["source_paper"]].append(c)
    for rows in by_paper.values():
        rows.sort(key=lambda c: (int(c.get("expanded_start_line", 0)), c["claim_id"]))
    return claims, by_id, by_paper


CLAIMS, CLAIM_BY_ID, BY_PAPER = load_claims()
CATALOG_ROWS = read_csv(ROOT / "config" / "paper_catalog.csv")
CATALOG = {r["paper_id"]: r for r in CATALOG_ROWS}
DEPENDENCY_EDGES = read_csv(ROOT / "corpus" / "paper_dependency_edges.csv")
DEPS = json_load(ROOT / "corpus" / "dependency_trees.json")
F_ROWS = read_csv(ROOT / "registry" / "F_laws.csv")
E_ROWS = read_csv(ROOT / "registry" / "E_laws.csv")
G_ROWS = read_csv(ROOT / "registry" / "G_laws.csv")
NG_ROWS = read_csv(ROOT / "registry" / "no_go_theorems.csv")
LAW_ROWS = F_ROWS + E_ROWS + G_ROWS
LAW_BY_ID = {r["law_id"]: r for r in LAW_ROWS}
NG_BY_ID = {r["law_id"]: r for r in NG_ROWS}

APP_PAPERS = {
    "P001", "P002", "P017", "P018", "P019", "P020", "P024",
    "P035", "P036", "P039", "P047", "P049", "P052", "P057",
}
CANONICAL_PAPERS = {"P031", "P027", "P026", "P028", "P030", "P029", "P032"}
PHILOSOPHY_PAPERS = {"P006", "P023", "P034", "P053", "P046", "P041", "P040", "P058", "P056"}


def thesis_claim(pid: str) -> dict[str, Any]:
    rows = BY_PAPER[pid]
    for c in rows:
        if c["claim_type"] == "paper_thesis":
            return c
    return rows[0]


def law_claim_map() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for law in LAW_ROWS:
        lid = law["law_id"]
        candidates = [c for c in CLAIMS if c.get("law_id") == lid]
        if candidates:
            source_line = int(law.get("source_line", "0") or 0)
            candidates.sort(key=lambda c: (
                0 if c["claim_type"] in {"theorem", "proposition", "lemma", "corollary", "schema"} else 1,
                abs(int(c.get("source_start_line", 0)) - source_line),
                c["claim_id"],
            ))
            out[lid] = candidates[0]
    for ng in NG_ROWS:
        nid = ng["law_id"]
        candidates = [c for c in CLAIMS if c.get("no_go_id") == nid]
        if candidates:
            source_line = int(ng.get("source_line", "0") or 0)
            candidates.sort(key=lambda c: (
                0 if c["claim_type"] in {"theorem", "proposition", "lemma", "corollary"} else 1,
                abs(int(c.get("source_start_line", 0)) - source_line),
                c["claim_id"],
            ))
            out[nid] = candidates[0]
    return out


LAW_CLAIM = law_claim_map()


def source_lines_context(pid: str, line_spec: str) -> tuple[str, list[int]]:
    path = ROOT / "source" / CATALOG[pid]["source_path"]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
    nums = sorted({int(x) for x in re.findall(r"\d+", line_spec)})
    chunks: list[str] = []
    for n in nums[:18]:
        if not lines:
            break
        lo, hi = max(1, n - 2), min(len(lines), n + 2)
        snippet = " ".join(lines[lo - 1 : hi])
        snippet = re.sub(r"\s+", " ", snippet).strip()
        chunks.append(f"L{n}: {snippet}")
    return compact(" || ".join(chunks), 5000), nums


def claim_score(claim: dict[str, Any], query: str, line: int | None = None) -> float:
    text = " ".join([
        claim.get("normalized_claim", ""),
        claim.get("conclusion", ""),
        " ".join(str(x) for x in claim.get("source_labels", []) or []),
        str(claim.get("law_id", "")),
        str(claim.get("no_go_id", "")),
    ])
    score = lexical_similarity(text[:8000], query[:8000])
    if claim["claim_type"] in {"theorem", "proposition", "lemma", "corollary", "schema", "definition"}:
        score += 0.035
    if line is not None:
        dist = abs(int(claim.get("source_start_line", 0)) - line)
        score += max(0.0, 0.15 - min(dist, 300) / 2000)
    return score


def best_claim(pid: str, query: str, line: int | None = None, exclude_boundaries: bool = True) -> dict[str, Any]:
    rows = BY_PAPER[pid]
    pool = rows
    if exclude_boundaries:
        filtered = [c for c in rows if c["claim_type"] not in {"nonclaim", "scope_boundary", "open_problem", "remark"}]
        if filtered:
            pool = filtered
    return max(pool, key=lambda c: (claim_score(c, query, line), -int(c.get("expanded_start_line", 0))))


def top_claim_ids(query: str, pids: Iterable[str] | None = None, kinds: set[str] | None = None, k: int = 6) -> list[str]:
    pool = CLAIMS
    if pids is not None:
        pset = set(pids)
        pool = [c for c in pool if c["source_paper"] in pset]
    if kinds is not None:
        pool = [c for c in pool if c["claim_type"] in kinds]
    scored = sorted(((claim_score(c, query), c["claim_id"]) for c in pool), reverse=True)
    out: list[str] = []
    for score, cid in scored:
        if score <= 0 and out:
            break
        if cid not in out:
            out.append(cid)
        if len(out) >= k:
            break
    return out


def infer_interface(text: str) -> str:
    t = text.lower()
    rules = [
        (("quotient", "descend", "coarse"), "explicit quotient/descent map with fiber and residual audit"),
        (("lens", "readout", "observable"), "declared lens/readout interface with adequacy and visibility audit"),
        (("bridge", "translation", "transport"), "typed translation/transport bridge with statement-fidelity audit"),
        (("event", "record", "admissib"), "event/record admission interface with provenance and occurrence audit"),
        (("promotion", "strict", "layer"), "promotion/exactification interface with separate objecthood, novelty, and directionality certificates"),
        (("markov", "kernel", "dynamics"), "stochastic-kernel/coarse-graining interface with path-space and closure diagnostics"),
        (("join", "contact", "interaction"), "contact/join surface requiring retention, anti-product novelty, and source audits"),
        (("proof", "theorem", "lemma"), "theorem-instantiation map with exact hypothesis discharge"),
        (("language", "model", "semantic"), "linguistic/semantic interface with source, access, and provenance controls"),
    ]
    for keys, desc in rules:
        if any(k in t for k in keys):
            return desc
    return "explicit typed carrier/interface map; citation alone does not supply it"


def nearest_countermodel(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("common source", "shared origin", "same source")):
        return "Two packages share an origin but expose disjoint quotients, so shared origin yields no shared access."
    if any(k in t for k in ("holonomy", "route", "order")):
        return "A protocol loop has nonzero route residue while the lifted dynamics is stationary and reversible, so holonomy exists with zero sustained arrow."
    if any(k in t for k in ("strict", "extension", "novel")):
        return "A nonfactoring candidate distinction is proposed but fails closure/objecthood or never fires, so strictness alone yields neither objecthood nor directionality."
    if any(k in t for k in ("sound", "reachable", "occur")):
        return "A sound rule is present but no executable finite path reaches it; or a reachable rule never fires in the recorded run."
    if any(k in t for k in ("enable", "descent")):
        return "An upper object enables a lower construction without factoring through the lower interface, so enablement is not descent."
    if any(k in t for k in ("contact", "join", "interaction")):
        return "Two packages exchange a record through a shared surface but the composite factors as their product; contact occurs without a strict join."
    if any(k in t for k in ("endogenous", "internal")):
        return "The theorist or environment supplies the generator; the resulting extension is externally seeded rather than endogenous."
    return "A verbal resemblance or citation exists while the source hypotheses and carrier/interface map are not discharged."


def classify_citation(target_pid: str, source_pid: str, context: str) -> str:
    t = context.lower()
    if "P039" in {target_pid, source_pid}:
        return "BLOCKED_SOURCE"
    if {target_pid, source_pid} == {"P040", "P058"}:
        return "NON_INDEPENDENT_VERSION_FAMILY"
    if target_pid in APP_PAPERS:
        if re.search(r"\b(?:apply|applying|instantiate|instantiation|speciali[sz]e|translation theorem|under the hypotheses|corollary of)\b", t):
            return "VALID_AFTER_ADDED_HYPOTHESES"
        return "ANALOGY_ONLY_OR_DOMAIN_MAP_REQUIRED"
    if source_pid == "P032":
        if re.search(r"\b(?:no[- ]?go|theorem|impossib|rules out|cannot)\b", t):
            return "VALID_AFTER_ADDED_HYPOTHESES"
        return "PARTIAL_BRIDGE_SCOPE_INHERITANCE_REQUIRED"
    if re.search(r"\b(?:verbatim|exact instance|direct corollary|same hypotheses|by theorem\s+[A-Za-z0-9])\b", t):
        return "EXACT_INHERITED_INSTANCE_CLAIMED_BY_TARGET"
    if re.search(r"\b(?:apply|applying|instantiate|instantiation|special case|under the hypotheses|corollary|translation theorem)\b", t):
        return "VALID_AFTER_ADDED_HYPOTHESES"
    if re.search(r"\b(?:builds? on|adopts?|following|extends?|framework|formalism|in the sense of|as in)\b", t):
        return "PARTIAL_BRIDGE_SCOPE_INHERITANCE_REQUIRED"
    if target_pid in CANONICAL_PAPERS and source_pid in CANONICAL_PAPERS:
        return "PARTIAL_BRIDGE_SCOPE_INHERITANCE_REQUIRED"
    return "UNKNOWN_REQUIRES_PROOF"


def build_citation_bridges() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, edge in enumerate(sorted(DEPENDENCY_EDGES, key=lambda r: (r["source_paper_id"], r["target_paper_id"])), 1):
        target_pid = edge["source_paper_id"]   # citing paper / target context
        source_pid = edge["target_paper_id"]   # cited paper / source result
        context, nums = source_lines_context(target_pid, edge["source_lines"])
        line = nums[0] if nums else None
        target_claim = best_claim(target_pid, context, line=line)
        source_claim = best_claim(source_pid, context)
        classification = classify_citation(target_pid, source_pid, context)
        source_h = hypothesis_texts(source_claim)
        target_h = hypothesis_texts(target_claim)
        added = list(target_h)
        if target_pid in APP_PAPERS:
            added += ["A concrete domain carrier, interface, and audit must instantiate every source type and hypothesis."]
        added += ["The citation context must be checked against the exact source statement; citation identity alone is not a theorem bridge."]
        licensed = compact(source_claim.get("conclusion", ""), 1200)
        if classification in {"ANALOGY_ONLY_OR_DOMAIN_MAP_REQUIRED", "UNKNOWN_REQUIRES_PROOF", "BLOCKED_SOURCE", "NON_INDEPENDENT_VERSION_FAMILY"}:
            licensed = "No theorem transfer is licensed by this row; it records orientation, version relation, or a blocked/undischarged invocation."
        rows.append({
            "bridge_id": f"BR-CITE-{i:04d}",
            "bridge_kind": "PAPER_INVOCATION",
            "source_claim": source_claim["claim_id"],
            "source_law": source_claim.get("law_id") or source_claim.get("no_go_id") or "",
            "source_paper": source_pid,
            "target_claim_or_context": target_claim["claim_id"],
            "target_paper": target_pid,
            "source_object": typed_object_text(source_claim),
            "target_object": typed_object_text(target_claim),
            "map_or_interface": infer_interface(context + " " + source_claim.get("normalized_claim", "")),
            "inherited_hypotheses": source_h,
            "added_hypotheses": added,
            "lost_hypotheses": ["No source hypothesis is treated as discharged merely by the citation; any unverified source premise remains a blocking obligation."],
            "source_of_truth": f"{source_claim['source_location']} | citation context source/{CATALOG[target_pid]['source_path']}:L{edge['source_lines']}",
            "audit_path": [
                source_claim["source_location"],
                f"source/{CATALOG[target_pid]['source_path']}:L{edge['source_lines']}",
                "corpus/paper_dependency_edges.csv",
            ],
            "formalization": transform_formalization(source_claim),
            "licensed_conclusion": licensed,
            "classification": classification,
            "nonclaims": list(source_claim.get("nonclaims", []) or [])[:40] + ["The citation is not evidence of statement identity, bridge validity, or evidentiary independence."],
            "nearest_countermodel": nearest_countermodel(context + " " + source_claim.get("normalized_claim", "")),
            "review_status": "STEP2_CONTEXT_CLASSIFIED; EXACT_REUSE_REQUIRES_SOURCE_STATEMENT_AUDIT" if classification != "BLOCKED_SOURCE" else "BLOCKED_BY_MISSING_SUPPLIED_SOURCE",
            "citation_keys": [x for x in edge["citation_keys"].split(";") if x],
            "citation_lines": nums,
            "citation_context": context,
        })
    return rows


NAMED_LAW_ACCEPTED: dict[str, set[str]] = {
    # P005's import table explicitly names these Foundations IV laws. Its F1--F6
    # tokens elsewhere are figure/local labels and are rejected by the audit.
    "P005": {"F13a", "F13b", "F42"},
    # P010 explicitly invokes F-IV F12. E2 is a Foundations-II item and F1--F5
    # are local preregistration/workflow labels.
    "P010": {"F12"},
    # Foundations VI's comparison table and law sections explicitly compare
    # the G-series against these Foundations IV cousins.
    "P029": {"F2", "F3", "F4", "F6", "F13a", "F19", "F27", "F34", "F40"},
    # Foundations V's import table, proof spines, and certification ledger
    # explicitly reuse these Foundations IV laws. F53 occurs only as a range
    # endpoint (F2--F53), not as a specific invocation.
    "P030": {"F2", "F3", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13a",
             "F17", "F19", "F20", "F21", "F22", "F25", "F29", "F30", "F31", "F37"},
    # P049 explicitly uses these F-laws as its cross-domain grammar. F1--F4
    # are figure numbers and remain rejected even though the paper uses many
    # other F-law identifiers substantively.
    "P049": {"F23", "F26", "F27", "F34", "F37", "F39", "F43", "F47", "F48", "F49", "F50", "F51"},
}

NAMED_LAW_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?P<law>F(?:[1-9]|[1-4][0-9]|5[0-3])(?:[ab])?|"
    r"E(?:[1-9]|1[0-6])|G(?:[1-9]|1[0-3]))(?![A-Za-z0-9])"
)


def named_law_rejection_reason(pid: str, law: str, context_tex: str) -> tuple[str, str]:
    lower = context_tex.lower()
    if (pid == "P028" and law.startswith("F")) or (pid == "P030" and law.startswith("E")) or (pid == "P029" and law.startswith("G")):
        return "REJECTED_OWN_SERIES", "The identifier belongs to the target paper's own law series, not an imported prior-law invocation."
    if pid in {"P040", "P058"} and law == "G2":
        return "REJECTED_MATHEMATICAL_SYMBOL_OR_LOCAL_LABEL", "The token is the PDF-string/local label for the mathematical expression G^2, not Foundations VI law G2."
    if pid == "P052" and law.startswith("E"):
        return "REJECTED_LOCAL_EXHIBIT_LABEL", "E1--E5 are this paper's local exhibit labels, not Foundations V laws."
    if pid == "P023" and law in {"F1", "F2", "F3"}:
        return "REJECTED_LOCAL_FUTURE_ITEM_LABEL", "F1--F3 are locally numbered future-work items."
    if pid == "P046" and law == "F1":
        return "REJECTED_LOCAL_TABLE_CELL", "F1 is a local matrix/table identifier with no Foundations IV attribution."
    if pid == "P047" and law.startswith("F"):
        return "REJECTED_LOCAL_FIGURE_OR_EXPERIMENT_LABEL", "F-identifiers are local figure, QA, or experiment labels."
    if pid == "P005" and law in {"F1", "F2", "F3", "F4", "F5", "F6"}:
        return "REJECTED_LOCAL_FIGURE_OR_RESULT_LABEL", "The occurrence is a local figure/result label, not a Foundations IV import."
    if pid == "P010" and law == "E2":
        return "REJECTED_OTHER_SERIES_ITEM", "The source explicitly calls this a Foundations-II item E2, not Foundations V law E2."
    if pid == "P010" and law in {"F1", "F2", "F3", "F4", "F5"}:
        return "REJECTED_LOCAL_WORKFLOW_LABEL", "The identifier is a local freeze/preregistration workflow item."
    if pid == "P049" and law in {"F1", "F2", "F3", "F4"}:
        return "REJECTED_LOCAL_FIGURE_LABEL", "F1--F4 are figure numbers in this paper."
    if pid == "P030" and law == "F53":
        return "REJECTED_SERIES_RANGE_ENDPOINT", "F53 appears only as the endpoint of the range F2--F53, not as a specific imported-law use."
    if re.search(r"\\(?:caption|label|includegraphics)|\bfigure\b|\bfig\.?(?:ure)?\b", lower):
        return "REJECTED_LOCAL_FIGURE_OR_LABEL", "The context is a local figure/label reference without source-series attribution."
    return "REJECTED_AMBIGUOUS_LOCAL_IDENTIFIER", "No source-series attribution or reviewed substantive prior-law use was established."


def scan_named_law_occurrences() -> list[dict[str, Any]]:
    """Audit every F/E/G-shaped token before creating any named-law bridge.

    The lexical candidate field on claims is deliberately recall-oriented. This
    source-level audit is the controlling precision layer: every occurrence is
    accepted or rejected with a reason, and only reviewed accepted paper/law
    pairs can enter the bridge atlas.
    """
    rows: list[dict[str, Any]] = []
    seq = 0
    for pid in sorted(CATALOG, key=lambda x: int(x[1:])):
        meta = json_load(METADATA / f"{pid}.json")
        expanded_path = find_expanded_path(meta)
        raw = expanded_path.read_text(encoding="utf-8", errors="replace")
        clean = strip_comments_preserve_lines(raw)
        doc_start = clean.find(r"\begin{document}")
        if doc_start < 0:
            doc_start = 0
        ends = [x for x in (clean.find(r"\bibliography", doc_start), clean.find(r"\begin{thebibliography}", doc_start)) if x >= 0]
        body_end = min(ends) if ends else len(clean)
        dep = DEPS[pid]
        line_map = source_line_map(raw, dep["root"], dep["files"])
        lines = clean.splitlines()
        start_line = clean.count("\n", 0, doc_start) + 1
        end_line = clean.count("\n", 0, body_end) + 1
        for line_no in range(start_line, min(end_line, len(lines)) + 1):
            line = lines[line_no - 1]
            matches = list(NAMED_LAW_PATTERN.finditer(line))
            if not matches:
                continue
            lo, hi = max(1, line_no - 1), min(len(lines), line_no + 1)
            context_tex = "\n".join(lines[lo - 1 : hi])
            context_plain = tex_to_plain(context_tex)
            idx = min(max(line_no - 1, 0), len(line_map) - 1) if line_map else 0
            source_path, source_line = line_map[idx] if line_map else (dep["root"], line_no)
            for law in dict.fromkeys(m.group("law") for m in matches):
                seq += 1
                if law in NAMED_LAW_ACCEPTED.get(pid, set()):
                    decision = "ACCEPTED_NAMED_PRIOR_LAW_INVOCATION"
                    basis = "Reviewed source occurrence belongs to the paper/law reuse set and is not a local numbering collision."
                else:
                    decision, basis = named_law_rejection_reason(pid, law, context_tex)
                target_claim = best_claim(pid, context_plain, line=source_line)
                rows.append({
                    "occurrence_id": f"NLO-{seq:05d}",
                    "target_paper": pid,
                    "law_id": law,
                    "expanded_path": f"derived/expanded/{expanded_path.name}",
                    "expanded_line": line_no,
                    "source_path": source_path,
                    "source_line": source_line,
                    "target_claim": target_claim["claim_id"],
                    "context_tex": compact(context_tex, 5000),
                    "context_plain": compact(context_plain, 2500),
                    "decision": decision,
                    "decision_basis": basis,
                })
    write_csv(BRIDGE_DIR / "named_law_occurrence_audit.csv", rows, list(rows[0]))
    write_jsonl(BRIDGE_DIR / "named_law_occurrence_audit.jsonl", rows)
    counts = Counter(r["decision"] for r in rows)
    accepted_pairs = sorted({(r["target_paper"], r["law_id"]) for r in rows if r["decision"].startswith("ACCEPTED")})
    md = [
        "# Named-law occurrence audit", "",
        "Every F/E/G-shaped token in the supplied paper bodies was reviewed before bridge creation. The claim-level `imported_laws` field is a lexical recall aid; this occurrence audit is the precision-controlling surface.", "",
        f"- Candidate occurrences: **{len(rows)}**.",
        f"- Accepted prior-law paper/law pairs: **{len(accepted_pairs)}**.",
        f"- Decision census: `{dict(counts)}`.", "",
        "## Accepted pairs", "",
    ]
    for pid, law in accepted_pairs:
        occs = [r for r in rows if r["target_paper"] == pid and r["law_id"] == law and r["decision"].startswith("ACCEPTED")]
        locs = ", ".join(f"{r['source_path']}:L{r['source_line']}" for r in occs[:8])
        if len(occs) > 8:
            locs += f", … ({len(occs)} occurrences)"
        md.append(f"- `{pid}` imports `{law}`: {locs}")
    md += ["", "## Collision controls", "", "The audit explicitly rejects local figures/workflow labels, local exhibits, local future-item numbering, range endpoints, and mathematical expressions such as `G^2` that resemble prior-law identifiers."]
    (BRIDGE_DIR / "NAMED_LAW_OCCURRENCE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


def build_imported_law_bridges(occurrences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    accepted: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for occ in occurrences:
        if occ["decision"] == "ACCEPTED_NAMED_PRIOR_LAW_INVOCATION":
            accepted[(occ["target_paper"], occ["law_id"])].append(occ)
    for i, ((target_pid, law), occs) in enumerate(sorted(accepted.items(), key=lambda x: (int(x[0][0][1:]), x[0][1])), 1):
        source_claim = LAW_CLAIM[law]
        # Prefer the earliest reviewed source occurrence; all accepted locations
        # remain attached to the grouped bridge row.
        occs.sort(key=lambda r: (int(r["expanded_line"]), r["occurrence_id"]))
        target_claim = CLAIM_BY_ID[occs[0]["target_claim"]]
        target_text = " ".join(o["context_plain"] for o in occs[:12])
        if target_pid in APP_PAPERS:
            classification = "VALID_AFTER_ADDED_HYPOTHESES"
        elif target_pid in {"P029", "P030"}:
            classification = "AVAILABLE_AFTER_EXACT_HYPOTHESIS_AND_STATEMENT_MATCH"
        else:
            classification = "VALID_AFTER_ADDED_HYPOTHESES"
        added = hypothesis_texts(target_claim) + [
            "The target carrier, quotient/lens, audit, and status vocabulary must instantiate the source law's exact types.",
            "Every source hypothesis must be discharged; the law identifier alone is not a proof.",
            "The reviewed source occurrence must retain its local context and may not be generalized beyond the target paper's declared use.",
        ]
        rows.append({
            "bridge_id": f"BR-LAW-{i:04d}",
            "bridge_kind": "NAMED_LAW_IMPORT",
            "source_claim": source_claim["claim_id"],
            "source_law": law,
            "source_paper": source_claim["source_paper"],
            "target_claim_or_context": target_claim["claim_id"],
            "target_paper": target_pid,
            "source_object": typed_object_text(source_claim),
            "target_object": typed_object_text(target_claim),
            "map_or_interface": infer_interface(target_text + " " + source_claim.get("normalized_claim", "")),
            "inherited_hypotheses": hypothesis_texts(source_claim),
            "added_hypotheses": added,
            "lost_hypotheses": ["Any source premise not explicitly witnessed in the target remains undischarged."],
            "source_of_truth": f"{source_claim['source_location']} | reviewed target occurrences: " + "; ".join(f"{o['source_path']}:L{o['source_line']}" for o in occs),
            "audit_path": [source_claim["source_location"], "bridges/named_law_occurrence_audit.csv"] + [f"{o['source_path']}:L{o['source_line']}" for o in occs],
            "formalization": transform_formalization(source_claim),
            "licensed_conclusion": compact(source_claim.get("conclusion", ""), 1400),
            "classification": classification,
            "nonclaims": list(source_claim.get("nonclaims", []) or [])[:40] + ["Named-law mention does not license hypothesis erasure, grade promotion, evidentiary independence, or domain back-transfer."],
            "nearest_countermodel": nearest_countermodel(source_claim.get("normalized_claim", "") + " " + target_text),
            "review_status": "STEP2_SOURCE_OCCURRENCE_AUDITED_NAMED_LAW_BRIDGE",
            "occurrence_ids": [o["occurrence_id"] for o in occs],
            "occurrence_locations": [f"{o['source_path']}:L{o['source_line']}" for o in occs],
            "target_claims": sorted({o["target_claim"] for o in occs}),
        })
    return rows


def build_law_reuse_contracts() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    all_rows = [(r["law_id"], r, "LAW") for r in LAW_ROWS] + [(r["law_id"], r, "NO_GO") for r in NG_ROWS]
    for i, (lid, row, kind) in enumerate(all_rows, 1):
        source_claim = LAW_CLAIM[lid]
        form = transform_formalization(source_claim)
        if form["source_match_status"] == "MATCHED_IMPORTED_LAW_DECLARATION":
            classification = "AVAILABLE_AFTER_EXACT_HYPOTHESIS_AND_STATEMENT_MATCH"
        elif form["source_match_status"] in {"PAPER_DISCLOSED_NOT_IN_LOCAL_IMPORT", "PAPER_DISCLOSED_ASSET_NOT_IMPORTED"}:
            classification = "PAPER_RESULT_AVAILABLE_LOCAL_FORMAL_ASSET_ABSENT_OR_PARTIAL"
        else:
            classification = "SOURCE_RESULT_AVAILABLE_FORMAL_MATCH_REQUIRES_AUDIT"
        rows.append({
            "bridge_id": f"BR-REUSE-{i:04d}",
            "bridge_kind": "PRIOR_LAW_REUSE_CONTRACT",
            "source_claim": source_claim["claim_id"],
            "source_law": lid,
            "source_paper": source_claim["source_paper"],
            "target_claim_or_context": "FOUNDATIONS_VII_REUSE_BOUNDARY",
            "target_paper": "FUTURE_FOUNDATIONS_VII",
            "source_object": typed_object_text(source_claim),
            "target_object": "Any later Foundations VII object that supplies a typed instantiation of the source carrier/interface and all source hypotheses.",
            "map_or_interface": "Exact statement-level adapter; no new VII object or adapter is constructed in Step 2.",
            "inherited_hypotheses": hypothesis_texts(source_claim),
            "added_hypotheses": ["A later reuse must prove type alignment, source fidelity, and all added VII-specific premises."],
            "lost_hypotheses": ["None may be silently dropped."],
            "source_of_truth": source_claim["source_location"],
            "audit_path": [source_claim["source_location"], f"registry/{'no_go_theorems' if kind == 'NO_GO' else lid[0] + '_laws'}.csv:{lid}", "formalization/integration/cumulative_lean_theorems.csv"],
            "formalization": form,
            "licensed_conclusion": compact(source_claim.get("conclusion", row.get("statement_plain", "")), 1600),
            "classification": classification,
            "nonclaims": list(source_claim.get("nonclaims", []) or [])[:40] + ["This inventory contract is not a Foundations VII theorem, bridge proof, or candidate-law endorsement."],
            "nearest_countermodel": nearest_countermodel(source_claim.get("normalized_claim", "")),
            "review_status": "STEP2_REUSE_BOUNDARY_INDEXED",
        })
    return rows


INVALID_TRANSFERS = [
    ("IT-01", "common source → shared access", "Two packages can descend from one source while exposing disjoint quotients.", "Require an explicit common instrument/quotient and a witnessed exposure map."),
    ("IT-02", "shared origin → common refinement", "Genealogy does not construct a carrier projecting lawfully to both descendants.", "Construct the refinement and audit both projections."),
    ("IT-03", "contact → strict join", "A record can cross an interface while the composite remains a product or a relabeling.", "Require parent retention plus an anti-product/nonfactorization witness."),
    ("IT-04", "common refinement → strict join", "A fork or product may refine both parents without creating a new joint distinction.", "Add strict join novelty relative to both parents and the mere product."),
    ("IT-05", "P3 holonomy → P6 directionality", "Route residue can occur in stationary reversible lifted dynamics.", "Supply a drive/affinity or path-space arrow certificate independently."),
    ("IT-06", "strict extension → objecthood", "A new predicate can fail the declared closure or packaging test.", "Supply the objecthood/stability certificate separately."),
    ("IT-07", "strict extension → drive", "Nonfactorization says nothing about sustained asymmetric dynamics.", "Supply the P6/drive certificate separately."),
    ("IT-08", "structural downward influence → top-down causal channel", "Constraint or selection may alter admissible states without a causal message channel.", "Name and test the actual carrier-level intervention/transport map."),
    ("IT-09", "enablement → descent", "An upper object may make a lower operation possible without factoring through the lower quotient.", "Prove the descent/factorization map, not just enabling dependence."),
    ("IT-10", "soundness → reachability", "A correct rule can be absent from every executable finite path.", "Provide a carried operation and reachability witness."),
    ("IT-11", "reachability → occurrence", "An enabled path need not be taken in the run.", "Provide a timestamped firing/event record."),
    ("IT-12", "theorist-triggered → endogenous", "External execution can mimic internal generation.", "Require carried generator, internal provenance, reachability, firing, and budget closure."),
    ("IT-13", "negative instance → universal no-go", "Failure on one carrier/protocol does not quantify over the whole admissible family.", "State the exact carrier family, quantifiers, and escape routes."),
    ("IT-14", "local Booleanity → global package", "Compatible local event algebras may fail gluing or be globally ambiguous.", "Supply compatibility, globalizability, uniqueness, and audit witnesses."),
    ("IT-15", "computational witness → general theorem", "A finite run proves only the encoded instance and checked property.", "Provide a theorem-level generalization with source-code/semantics bridge."),
    ("IT-16", "application success → abstract-law confirmation", "A domain result may depend on domain assumptions or an analogy-only mapping.", "Use a typed instantiation bridge and prohibit back-transfer of domain-specific conclusions."),
    ("IT-17", "formal file present → kernel verified theorem", "Source presence and static import resolution do not equal elaboration by the requested Lean kernel.", "Record declaration, trust base, statement delta, and actual machine-check status."),
    ("IT-18", "generic transition → P3", "An arbitrary state transition does not establish two typed routes, noncommutation, or a holonomy residue.", "Declare the route pair/currentizer and exhibit a nonzero route-comparison residual."),
    ("IT-19", "generic path → P5 packaging", "Traversing a path does not define an idempotent packaging endomap or certify a fixed-point object.", "Declare the P5 packaging map and discharge its objecthood/fixed-point audit."),
    ("IT-20", "semantics → P1", "Interpretation or meaning does not itself supply the typed P1 source/primitive role.", "Name the carrier/source, type the role channel, and audit that it is not being inferred from semantic description alone."),
]


def write_invalid_transfers() -> list[dict[str, Any]]:
    rows = []
    for ident, collapse, failure, remedy in INVALID_TRANSFERS:
        rows.append({
            "invalid_transfer_id": ident,
            "forbidden_collapse": collapse,
            "why_invalid": failure,
            "required_bridge_or_certificate": remedy,
            "detector": f"Flag any prose or graph edge that asserts `{collapse}` without the named bridge/certificate.",
            "nearest_countermodel": nearest_countermodel(collapse),
            "status": "FORBIDDEN_WITHOUT_EXPLICIT_BRIDGE",
        })
    write_csv(BRIDGE_DIR / "invalid_transfers.csv", rows, list(rows[0]))
    md = ["# Invalid-transfer register", "", "These are recurrent SBT overreads. Each transition is forbidden unless the stated bridge or certificate is supplied.", "", "| ID | Forbidden collapse | Why it fails | Required repair |", "|---|---|---|---|"]
    for r in rows:
        md.append(f"| `{r['invalid_transfer_id']}` | {r['forbidden_collapse']} | {r['why_invalid']} | {r['required_bridge_or_certificate']} |")
    (BRIDGE_DIR / "INVALID_TRANSFER_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


NO_GO_DETAILS = {
    "NG_ARROW_DPI": {
        "carrier": "finite micro path law and its deterministic pointwise observation on a fixed horizon",
        "rules_out": "increasing forward/reverse path-space KL by an honest deterministic coarse-graining",
        "does_not_rule_out": "stochastic observation, fitted proxy macro models, changed dynamics, or genuine microscopic nonreversibility",
    },
    "NG_PROTOCOL_TRAP": {
        "carrier": "finite stationary reversible autonomous lifted Markov chain, including hidden protocol coordinates",
        "rules_out": "obtaining a positive micro or observed arrow solely from an autonomous reversible protocol loop",
        "does_not_rule_out": "external scheduling, nonstationarity, broken detailed balance, or genuinely driven lifted dynamics",
    },
    "NG_FORCE_FOREST": {
        "carrier": "finite undirected forest with an antisymmetric edge field on exact support",
        "rules_out": "a nontrivial cycle obstruction on forest support",
        "does_not_rule_out": "graphs with positive cycle rank or thresholded/regularized proxy supports",
    },
    "NG_FORCE_NULL": {
        "carrier": "finite graph carrying an exact antisymmetric edge form",
        "rules_out": "nonzero circulation on a closed walk for an exact form",
        "does_not_rule_out": "nonexact forms or altered approximate/thresholded support notions",
    },
    "NG_MACRO_CLOSURE_DEFICIT": {
        "carrier": "finite Markov chain, deterministic package, fixed lag, and KL-scored macro kernel family",
        "rules_out": "exact macro closure when same-package microstates have distinct packaged future laws",
        "does_not_rule_out": "changing the package, lag, dynamics, or using a fitted macro kernel as a diagnostic proxy",
    },
    "NG_OBJECT_CONTRACTIVE": {
        "carrier": "finite stochastic matrix in a strict Dobrushin-contractive regime",
        "rules_out": "widely separated epsilon-stable distributions and multiple exact stationary distributions",
        "does_not_rule_out": "noncontractive regimes or heuristic clustering not represented by stationary distributions",
    },
    "NG_LADDER_IDEM": {
        "carrier": "a fixed idempotent endomap on a fixed state/package space",
        "rules_out": "an infinite or multi-step strict ladder generated by iterating that same idempotent map",
        "does_not_rule_out": "operator change, package/interface growth, or non-idempotent updates",
    },
    "NG_LADDER_BOUNDED_INTERFACE": {
        "carrier": "a fixed deterministic finite-image interface and its definable Boolean predicates",
        "rules_out": "an infinite strict definability ladder inside that fixed finite interface",
        "does_not_rule_out": "growth of the lens, domain, package, or interface image",
    },
}


def write_no_go_scope_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ng in NG_ROWS:
        nid = ng["law_id"]
        claim = LAW_CLAIM[nid]
        detail = NO_GO_DETAILS[nid]
        rows.append({
            "no_go_id": nid,
            "name": ng["name"],
            "source_claim": claim["claim_id"],
            "source_location": claim["source_location"],
            "carrier": detail["carrier"],
            "hypotheses": hypothesis_texts(claim) or [compact(ng["statement_plain"], 1200)],
            "conclusion": compact(claim.get("conclusion") or ng["statement_plain"], 1800),
            "source_statement_tex": claim.get("source_wording_tex", ""),
            "expanded_statement_tex": claim.get("expanded_source_wording_tex", "") or claim.get("source_wording_tex", ""),
            "rules_out": detail["rules_out"],
            "does_not_rule_out": detail["does_not_rule_out"],
            "escape_route": ng["escape_route"],
            "formalization": transform_formalization(claim),
            "review_status": "STEP2_EXACT_SCOPE_AND_ESCAPE_RECORDED",
        })
    write_csv(BRIDGE_DIR / "no_go_scope_matrix.csv", rows, list(rows[0]))
    write_jsonl(BRIDGE_DIR / "no_go_scope_matrix.jsonl", rows)
    md = ["# No-go scope matrix", "", "Every negative result is carrier- and hypothesis-bounded. The escape route is part of the result's safe reuse contract. Formal posture records whether the supplied Lean spine contains an exact declaration, an abstract/core correspondence requiring an adapter, only a paper-disclosed asset, or no local match.", "", "| No-go | Exact carrier | Rules out | Does not rule out | Escape route | Formal posture |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| `{r['no_go_id']}` / `{r['source_claim']}` | {r['carrier']} | {r['rules_out']} | {r['does_not_rule_out']} | {r['escape_route']} | `{r['formalization']['source_match_status']}` |")
    (SYNTH_DIR / "NO_GO_SCOPE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


APPLICATION_SPECS = {
    "P018": ("formal problem carriers for the three Clay closure programs", "problem-specific theorem/proof interfaces", "translation schemas, residual trees, and claim-grade ledger", "conditional cross-domain transport and failure of untyped transfer", "translation theorem and bridge discipline", "A common grammar does not make the three target closures mutually evidentiary.", "conditional closure translation Clay problem"),
    "P019": ("finite SAT encodings and the saturated SAT layer", "saturation/quotient readouts and proof-complexity observables", "translation theorem, AOR instance, residual and no-go checks", "saturation versus actual complexity-class closure", "operational reachability of proof rules", "It does not establish P=NP or P≠NP without the declared bridge summit.", "saturated SAT closure reachability proof rules complexity"),
    "P024": ("spectral/trace carrier with involutive self-duality", "trace, zero-set, and confinement readouts", "translation theorem and AOR-instance audit", "conditional transfer from trace confinement to RH", "conditional theorem transport", "The structural membrane does not independently prove the analytic bridge hypotheses or RH.", "self-dual trace confinement translation Riemann hypothesis"),
    "P017": ("Navier–Stokes solution, energy, and regularity carriers", "PDE norms, continuation criteria, and membrane interfaces", "framework no-gos, residual tree, and conditional AOR bridge", "layer dissolution versus genuine PDE regularity", "membrane/closure dissolution", "It does not solve the Clay problem without the criterion-native bridge.", "Navier Stokes membrane regularity continuation closure"),
    "P035": ("dyadic shell/energy-flux carrier for a no-Zeno regularity program", "shell-localization and positive-work/capacity interfaces", "abstract no-Zeno theorem, legality checks, and finite tests", "localization legality versus a true PDE regularity bridge", "no-Zeno and legal localization", "The abstract/Lean no-Zeno result does not certify that Navier–Stokes supplies every legality hypothesis.", "no-Zeno dyadic shell localization legality capacity"),
    "P057": ("finite controlled systems, bits, gates, and Boolean readouts", "control and compositional gate interfaces", "operational diagnostics and packaging audit", "local Boolean control versus global lawful packaging", "local/global packaging and operational Booleanity", "A local gate representation does not by itself yield a global event package or universal computational claim.", "bits gates Boolean control global package"),
    "P020": ("Hilbert-cell and symmetry-protected-topological legality carrier", "channelized feasibility and persistence readouts", "legality, feasibility, and persistence certificates", "feasibility versus lawfully persistent SPT structure", "persistence under precise channel assumptions", "Feasibility alone does not establish persistence or a general physical realization.", "symmetry protected topological Hilbert cell legality persistence"),
    "P002": ("quantum operational carrier with measurement contexts and records", "contextual measurement/readout interfaces", "record-stability, contextuality, and operational closure audits", "contextual access and stable records versus hidden-value overread", "measurement context and operational closure", "Operational closure does not license an ontological hidden-variable claim or erase context dependence.", "quantum measurement contextuality record stability operational closure"),
    "P036": ("common-support neutrino mass model under alternative lenses", "lens-swap and staging interfaces", "support, readout, and stability comparisons", "lens-relative description versus support-stable content", "lens-swap stability", "The example is a domain model, not a general proof that arbitrary lens swaps preserve objecthood.", "neutrino mass lens swap common support stability"),
    "P001": ("cosmological expansion and inference carrier", "distance, clustering, and route-dependent readout interfaces", "route-mismatch and path-space arrow audits", "apparent acceleration from protocol/readout effects versus genuine drive", "arrow versus schedule/route mismatch", "The audit does not replace empirical cosmology or infer a physical drive from P3 holonomy.", "dark energy route mismatch acceleration arrow audit"),
    "P039": ("contingent-modulus dark-energy carrier described only in the supplied abstract", "missing in the supplied source package", "abstract-level assertions only", "potential dependence of apparent acceleration on modulus closure", "source completeness and contingent closure", "No theorem, proof, or detailed instantiation bridge is recoverable from the missing 18 included TeX files.", "contingent modulus dark energy closure"),
    "P047": ("stochastic substrate with coarse-grained geometric and thermodynamic observables", "Markov/coarse-graining lens", "closure, residual, and thermodynamic diagnostics", "emergent geometry/thermodynamics under a declared package", "stochastic emergence and diagnostic closure", "A successful finite stochastic construction does not establish a universal physical substrate theory.", "stochastic substrate geometry thermodynamics Markov coarse graining"),
    "P052": ("Markov geometry with macro kernels, prototypes, distances, and route data", "macro-state and transport/holonomy interfaces", "closure deficit, geometry, and route audit", "birth of macro geometry and holonomy without automatic arrow", "geometry formation and order-sensitive memory", "Nonzero geometric holonomy does not establish P6 directionality.", "Markov geometry macro kernel distance holonomy"),
    "P049": ("Standard Model, quantum-mechanical, and relativistic theory packages", "cross-theory completion, common-refinement, and demarcation interfaces", "translation and applicability audits", "genuine common refinement versus verbal unification", "true common refinement and strict join pressure", "The shared grammar does not by itself derive a unified physical theory or make applications independent evidence for SBT.", "Standard Model quantum general relativity common refinement unification"),
}


def write_application_pressure_tests(law_bridges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for b in law_bridges:
        by_target[b["target_paper"]].append(b)
    for pid in sorted(APP_PAPERS, key=lambda p: int(p[1:])):
        carrier, interface, audit, distinguishes, pressure, forbidden, query = APPLICATION_SPECS[pid]
        principal = top_claim_ids(query, [pid], {"theorem", "proposition", "lemma", "corollary", "schema", "result_summary", "paper_thesis"}, 10)
        boundaries = top_claim_ids(query + " limitation nonclaim scope", [pid], {"nonclaim", "scope_boundary", "open_problem"}, 8)
        bridges = by_target.get(pid, [])
        abstract_laws = sorted({b["source_law"] for b in bridges})
        if pid == "P039":
            classification = "BLOCKED_SOURCE"
            ruling = "ABSTRACT_ONLY; NO DETAILED INSTANTIATION CLAIMED"
        elif bridges:
            classes = sorted({b["classification"] for b in bridges})
            classification = ";".join(classes)
            ruling = "CONCRETE DOMAIN MAP RECORDED; EXACT LAW REUSE REMAINS HYPOTHESIS-BOUND"
        else:
            classification = "ANALOGY_ONLY_OR_LOCAL_DOMAIN_RESULT"
            ruling = "CONCRETE PRESSURE-TEST MAP RECORDED; NO NAMED PRIOR-LAW TRANSFER CLAIMED"
        rows.append({
            "paper_id": pid,
            "title": CATALOG[pid]["title"],
            "source_completeness": "BLOCKED_MISSING_INCLUDED_FILES" if pid == "P039" else "FULL_SUPPLIED_SOURCE_TREE",
            "concrete_carrier": carrier,
            "interface_or_lens": interface,
            "audit_or_certificate": audit,
            "abstract_laws_invoked": abstract_laws,
            "bridge_ids": [b["bridge_id"] for b in bridges],
            "bridge_classification": classification,
            "what_the_application_distinguishes_or_falsifies": distinguishes,
            "missing_vii_primitive_or_pressure": pressure,
            "forbidden_back_transfer": forbidden,
            "principal_claims": principal,
            "nonclaims_or_open_boundaries": boundaries,
            "pressure_test_ruling": ruling,
        })
    write_csv(SYNTH_DIR / "application_pressure_tests.csv", rows, list(rows[0]))
    write_jsonl(SYNTH_DIR / "application_pressure_tests.jsonl", rows)
    md = ["# Application pressure tests", "", "Applications are adversarial tests of bridge discipline, not extra votes for the abstract theory.", "", "| Paper | Carrier/interface | Bridge ruling | What it tests | Forbidden back-transfer |", "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| `{r['paper_id']}` | {r['concrete_carrier']}; {r['interface_or_lens']} | `{r['bridge_classification']}` | {r['what_the_application_distinguishes_or_falsifies']} | {r['forbidden_back_transfer']} |")
    (SYNTH_DIR / "APPLICATION_PRESSURE_TESTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows




def write_examples_carrier_registry(apps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build the Step-2 example/carrier registry.

    The corpus rarely uses a dedicated ``example`` theorem environment.  The
    registry therefore combines the fourteen concrete domain carriers used as
    pressure tests with source-named examples, toy models, benchmarks, and
    constructions.  Every row is anchored to a canonical claim ID.
    """
    rows: list[dict[str, Any]] = []
    for app in apps:
        source_claim = (app.get("principal_claims") or [f"{app['paper_id']}-C0001"])[0]
        claim = CLAIM_BY_ID[source_claim]
        rows.append({
            "record_id": f"CAR-APP-{app['paper_id']}",
            "record_kind": "APPLICATION_PRESSURE_CARRIER",
            "source_paper": app["paper_id"],
            "source_claim": source_claim,
            "source_location": claim["source_location"],
            "carrier_or_model": app["concrete_carrier"],
            "interface_or_lens": app["interface_or_lens"],
            "audit_or_evidence": app["audit_or_certificate"],
            "claim_grade": claim["claim_grade"],
            "formalization": transform_formalization(claim),
            "what_it_distinguishes": app["what_the_application_distinguishes_or_falsifies"],
            "nonclaim_or_boundary": app["forbidden_back_transfer"],
            "source_completeness": app["source_completeness"],
        })

    named_pat = re.compile(r"\b(example|toy model|benchmark|experiment|laboratory|finite model|worked model)\b", re.I)
    for claim in CLAIMS:
        title = claim.get("source_title_tex", "") or ""
        if claim.get("claim_type") != "construction" and not named_pat.search(title):
            continue
        rows.append({
            "record_id": f"CAR-SRC-{claim['claim_id']}",
            "record_kind": "SOURCE_NAMED_EXAMPLE_OR_MODEL",
            "source_paper": claim["source_paper"],
            "source_claim": claim["claim_id"],
            "source_location": claim["source_location"],
            "carrier_or_model": compact(claim.get("normalized_claim", ""), 1200),
            "interface_or_lens": infer_interface(claim.get("normalized_claim", "")),
            "audit_or_evidence": claim.get("proof_status", "SOURCE_RECORD"),
            "claim_grade": claim.get("claim_grade", ""),
            "formalization": transform_formalization(claim),
            "what_it_distinguishes": "Source-named finite/example/model surface retained as a reusable pressure-test carrier.",
            "nonclaim_or_boundary": "Example or model status does not license transfer beyond the exact source statement and its hypotheses.",
            "source_completeness": claim.get("source_completeness", ""),
        })

    rows.sort(key=lambda r: (r["source_paper"], r["record_kind"], r["source_claim"], r["record_id"]))
    write_csv(ROOT / "registry" / "examples_carriers.csv", rows, list(rows[0]))
    write_jsonl(ROOT / "registry" / "examples_carriers.jsonl", rows)
    md = [
        "# Example and carrier registry", "",
        "This registry combines concrete application pressure-test carriers with source-named examples, toy models, benchmarks, experiments, and constructions. Every row is anchored to a canonical claim; no example is promoted beyond its source grade.", "",
        "| Record | Paper / claim | Kind | Carrier or model | Boundary |", "|---|---|---|---|---|",
    ]
    for r in rows:
        md.append(f"| `{r['record_id']}` | `{r['source_paper']}` / `{r['source_claim']}` | `{r['record_kind']}` | {compact(r['carrier_or_model'], 280)} | {r['nonclaim_or_boundary']} |")
    (ROOT / "registry" / "EXAMPLES_CARRIERS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


TAXONOMY_TABLES: dict[str, list[dict[str, str]]] = {
    "access_state_matrix": [
        {"state": "EXPRESSIBLE", "definition": "A well-typed sentence, rule, or operation can be formed in the declared language.", "required_certificate": "grammar/signature witness", "nonimplication": "Does not imply that the referenced object or operation is present on the carrier.", "query": "expressible language grammar signature well typed"},
        {"state": "PRESENT", "definition": "The relevant carrier object, rule, record, or operation exists in the package.", "required_certificate": "source/provenance record", "nonimplication": "Does not imply exposure, executable access, or use.", "query": "present carrier source provenance record exists"},
        {"state": "EXPOSED", "definition": "A declared instrument can distinguish, display, or invoke the item through an interface.", "required_certificate": "visibility/exposure certificate", "nonimplication": "Exposure may be lossy and does not imply recoverability or admissible execution.", "query": "exposure visibility instrument interface readout"},
        {"state": "RECOVERABLE", "definition": "The item can be reconstructed to declared fidelity from exposed data.", "required_certificate": "decoder plus residual/fidelity bound", "nonimplication": "Recoverability does not imply permission, reachability, or occurrence.", "query": "recoverability decoder reconstruction residual fidelity"},
        {"state": "ADEQUATE", "definition": "The exposed/recovered representation meets the declared task or probe family.", "required_certificate": "adequacy audit and residual threshold", "nonimplication": "Adequacy is probe-relative and does not imply complete access.", "query": "adequacy residual blind spot task probe family"},
        {"state": "ADMISSIBLE", "definition": "The item passes current type, source, budget, and audit gates.", "required_certificate": "typed admission verdict", "nonimplication": "A sound/admissible rule can remain operationally unreachable.", "query": "admissible admission gate source budget audit"},
        {"state": "REACHABLE", "definition": "An executable finite path from an admitted current state reaches the item under declared resources.", "required_certificate": "path and guard-activity witness", "nonimplication": "Existence of a path does not witness actual firing.", "query": "reachable finite path executable guard operation"},
        {"state": "OCCURRENT", "definition": "A run/event record witnesses that the transition, contact, or join actually fired.", "required_certificate": "timestamped occurrence/event record", "nonimplication": "Occurrence alone does not establish novelty, closure, or directionality.", "query": "occurrence fired event run record timestamp"},
    ],
    "admission_kind_matrix": [
        {"kind": "RULE_TEXT", "definition": "A declarative admission rule exists.", "required_evidence": "syntax, type, and source", "nonclaim": "Not necessarily executable.", "query": "rule text declarative syntax source admission"},
        {"kind": "EXECUTABLE_OPERATION", "definition": "A carried operation is available to the runtime.", "required_evidence": "typed implementation and scope", "nonclaim": "May still be unreachable.", "query": "carried executable operation runtime reachability"},
        {"kind": "NATIVE_RECORD", "definition": "Evidence is produced by the target package's own declared source.", "required_evidence": "source/provenance audit", "nonclaim": "May still fail relevance, budget, or quality gates.", "query": "native record source provenance package evidence"},
        {"kind": "BRIDGED_RECORD", "definition": "Evidence comes from another package through an explicit translation.", "required_evidence": "bridge, fidelity, and loss audit", "nonclaim": "Must not be relabeled native.", "query": "bridged record translation fidelity source"},
        {"kind": "PROSPECTIVE_COMMITMENT", "definition": "A timestamped, preregistered, budgeted rule reserves later admission conditions.", "required_evidence": "order, price, immutable predicate", "nonclaim": "Post-hoc predicates do not qualify.", "query": "prospective commitment preregistered timestamp budget predicate"},
        {"kind": "EXTERNAL_PROVISION", "definition": "An allowed seed, tool, or record is supplied from outside.", "required_evidence": "subsidy/source label", "nonclaim": "Cannot be credited as endogenous.", "query": "external provision seed subsidy source endogenous"},
        {"kind": "ENDOGENOUS_GENERATION", "definition": "The package carries and executes its own admissible generator.", "required_evidence": "carried source, reachability, firing, budget", "nonclaim": "Theorist execution is not enough.", "query": "endogenous generation carried generator reachability firing"},
        {"kind": "RETRACTION_OR_ROLLBACK", "definition": "A previously admitted item is lawfully withdrawn or reverted.", "required_evidence": "typed retraction rule, dependency audit, and record preservation", "nonclaim": "Deletion is not automatically lawful rollback.", "query": "retraction rollback withdrawal forgetting record preservation"},
    ],
    "contact_join_status_matrix": [
        {"status": "NO_EVIDENCED_CONTACT", "definition": "No admissible contact witness has been supplied.", "required_certificate": "none", "nonimplication": "Not equivalent to certified non-interaction.", "query": "no contact witness absence evidence non interaction"},
        {"status": "POTENTIAL_CONTACT", "definition": "Interfaces are type-compatible in principle.", "required_certificate": "type compatibility", "nonimplication": "Compatibility is not evidence of access or execution.", "query": "compatible interface potential contact type"},
        {"status": "EVIDENCED_CONTACT", "definition": "A native or honestly bridged record crosses a declared contact surface.", "required_certificate": "source, bridge, and crossing record", "nonimplication": "Does not imply a joint object or joint novelty.", "query": "contact surface crossed record bridge interaction"},
        {"status": "PEER_TRANSPORT", "definition": "Certified content is transported through an explicit peer map.", "required_certificate": "transport map and fidelity audit", "nonimplication": "Does not imply formation of a joint theory.", "query": "peer transport map fidelity theory"},
        {"status": "COMMON_REFINEMENT", "definition": "A carrier/package projects lawfully to both parents.", "required_certificate": "two projection/descent certificates", "nonimplication": "May be a fork or product rather than a strict join.", "query": "common refinement projects both parents descent"},
        {"status": "COMPOSITE_PACKAGE", "definition": "Both parents are retained in one auditable package.", "required_certificate": "parent retention and provenance", "nonimplication": "Retention is not anti-product novelty.", "query": "composite package parent retention provenance"},
        {"status": "STRICT_JOIN", "definition": "A composite is formed and has an anti-product/nonfactorization witness relative to both parents and their mere product/refinement.", "required_certificate": "objecthood, retention, anti-product novelty, and occurrence; directionality separately", "nonimplication": "Does not by itself establish a P6 arrow.", "query": "strict join anti product nonfactorization parent retention"},
        {"status": "OBSTRUCTED_JOIN", "definition": "A typed obstruction blocks source, budget, compatibility, gluing, retention, or novelty.", "required_certificate": "gate-specific obstruction witness", "nonimplication": "A failed gate must not be relabeled generic non-interaction.", "query": "obstructed join gate compatibility gluing budget novelty"},
        {"status": "CERTIFIED_NON_INTERACTION", "definition": "A coverage- and power-qualified audit establishes irrelevance or impossibility within a declared family.", "required_certificate": "coverage, null, power, and scope record", "nonimplication": "Does not universalize beyond the covered family.", "query": "certified non interaction coverage power null family"},
    ],
    "enablement_attribution_matrix": [
        {"attribution": "THEORIST", "definition": "The analyst declares or executes the enabling operation.", "required_evidence": "external source and execution record", "nonclaim": "Not endogenous.", "query": "theorist executes external source operation"},
        {"attribution": "CARRIER", "definition": "Substrate dynamics supplies the enabling transition.", "required_evidence": "carrier-generated provenance", "nonclaim": "Carrier causation need not imply theory-level descent.", "query": "carrier generated dynamics provenance transition"},
        {"attribution": "OTHER_THEORY", "definition": "A peer package supplies a bridged operation or record.", "required_evidence": "peer bridge and source independence", "nonclaim": "Must retain peer provenance.", "query": "other theory peer bridge source independence"},
        {"attribution": "OBSERVER_INSTRUMENT", "definition": "An observer/instrument creates exposure or admissibility.", "required_evidence": "occupancy, cost, and no-smuggling audit", "nonclaim": "Observer resources are not free.", "query": "observer instrument exposure occupancy cost"},
        {"attribution": "ENVIRONMENT", "definition": "An environmental input triggers or maintains the condition.", "required_evidence": "subsidy and withdrawal behavior", "nonclaim": "Environmentally sustained is not closed-loop endogenous.", "query": "environment input subsidy trigger withdrawal"},
        {"attribution": "ENDOGENOUS_SYSTEM", "definition": "The system carries, reaches, executes, and audits the generator itself.", "required_evidence": "closed-loop E-style certificate", "nonclaim": "Theorist-triggered execution does not qualify.", "query": "endogenous system generator closed loop carried executes audit"},
        {"attribution": "MIXED", "definition": "Multiple sources are load-bearing.", "required_evidence": "contribution, occupancy, and cost decomposition", "nonclaim": "Mixed provenance must not be simplified to a single source.", "query": "mixed source contribution cost decomposition"},
    ],
    "order_holonomy_matrix": [
        {"status": "COMMUTING", "definition": "Declared routes agree on the audited target readout.", "required_certificate": "commuting-square witness", "nonimplication": "Agreement at one readout need not imply equality at a richer predictive quotient.", "query": "commuting routes readout square"},
        {"status": "ORDER_SENSITIVE", "definition": "Two admissible operation orders produce distinguishable outputs.", "required_certificate": "same-source controlled route comparison", "nonimplication": "Order sensitivity alone is not memory or directionality.", "query": "order sensitive operation routes distinguishable"},
        {"status": "HOLONOMY", "definition": "A closed protocol loop has nontrivial route residue relative to the declared quotient/readout.", "required_certificate": "loop and nonzero residue witness", "nonimplication": "Holonomy does not imply P6 arrow.", "query": "holonomy loop route residue quotient"},
        {"status": "MEMORY_REQUIRED", "definition": "Current quotient equality hides a route difference relevant to future probes.", "required_certificate": "predictive split pair and memory repair", "nonimplication": "Memory need not create a new object or sustained drive.", "query": "memory route residue predictive quotient split pair"},
        {"status": "CONFLUENT", "definition": "All admissible reduction/interaction orders join to an equivalent audited result.", "required_certificate": "diamond/confluence certificate", "nonimplication": "Confluence does not imply absence of transient route information.", "query": "confluence diamond orders join"},
        {"status": "NONCONFLUENT", "definition": "Admissible orders lead to inequivalent terminal or predictive statuses.", "required_certificate": "critical-pair counterexample", "nonimplication": "Nonconfluence is not automatically a temporal arrow.", "query": "nonconfluence critical pair terminal order"},
        {"status": "P6_DRIVE_OR_ARROW", "definition": "A separate drive/affinity or path-space asymmetry certificate establishes directionality.", "required_certificate": "P6/affinity/path-space audit", "nonimplication": "Cannot be inferred from P3 holonomy alone.", "query": "P6 drive affinity path space arrow directionality"},
    ],
    "currency_budget_matrix": [
        {"currency": "ACCESS_COST", "definition": "Resources consumed to expose or invoke an interface.", "required_accounting": "source, amount, scope, and payer", "failure_refund": "No access credit when exposure fails.", "query": "access cost resource interface payer"},
        {"currency": "BLIND_SPOT_RESIDUAL", "definition": "Task-relevant distinctions remaining inaccessible or inadequate.", "required_accounting": "probe family and residual measure", "failure_refund": "Residual remains on the ledger until repaired or scope is narrowed.", "query": "blind spot residual adequacy currency"},
        {"currency": "COMMITMENT_BUDGET", "definition": "Capacity reserved prospectively for later admission or testing.", "required_accounting": "timestamp, immutable predicate, and price", "failure_refund": "Post-hoc choice receives no prospective-credit refund.", "query": "commitment budget prospective timestamp price"},
        {"currency": "OBSERVER_OCCUPANCY", "definition": "Instrument/observer resources occupying a channel, state, or budget slot.", "required_accounting": "occupancy and opportunity cost", "failure_refund": "Unpriced observer work cannot be credited as free endogeny.", "query": "observer occupancy instrument resource cost"},
        {"currency": "PROVENANCE_DEBT", "definition": "Unresolved source or translation obligations attached to a record.", "required_accounting": "native/bridged source and fidelity record", "failure_refund": "Unresolved debt blocks native or exact-bridge credit.", "query": "provenance source debt bridge fidelity"},
        {"currency": "NOVELTY_BUDGET", "definition": "New distinctions actually earned relative to the current interface/package.", "required_accounting": "nonfactorization witness and comparison class", "failure_refund": "Relabeling or product composition earns no strict-novelty credit.", "query": "novelty budget nonfactorization comparison"},
        {"currency": "FAILURE_REFUND", "definition": "Explicit reversal of credit when a gate, detector, or bridge fails.", "required_accounting": "failed gate and withdrawn claim grade", "failure_refund": "Refund restores honest status but does not erase the failure record.", "query": "failure refund credit gate withdrawn claim"},
    ],
    "retention_absorption_matrix": [
        {"status": "PARENT_RETAINED", "definition": "Each parent remains recoverable with source identity inside the child/composite.", "required_certificate": "two recovery/projection maps and provenance", "nonimplication": "Retention alone does not give strict join novelty.", "query": "parent retained recoverable projection provenance child"},
        {"status": "PARTIAL_RETENTION", "definition": "Only declared parent readouts survive.", "required_certificate": "scope-limited recovery map and loss register", "nonimplication": "Must not be described as full parent preservation.", "query": "partial retention readout loss parent"},
        {"status": "ABSORPTION", "definition": "A parent loses independent recoverability or identity in the child.", "required_certificate": "explicit loss/quotient record", "nonimplication": "Absorption is not automatically failure if the claim permits it.", "query": "absorption parent lost recoverability identity"},
        {"status": "ERASURE", "definition": "A parent distinction or provenance record is silently or explicitly removed.", "required_certificate": "erasure event and authorization", "nonimplication": "Silent erasure invalidates retention claims.", "query": "erasure forgetting provenance parent distinction"},
        {"status": "RECOMBINATION", "definition": "Parent/branch content is reorganized under a richer comparison quotient.", "required_certificate": "branchwise and recombination comparison maps", "nonimplication": "Branchwise equality need not determine recombination equality.", "query": "recombination branch quotient comparison"},
    ],
}


def write_taxonomies() -> dict[str, int]:
    counts: dict[str, int] = {}
    for name, specs in TAXONOMY_TABLES.items():
        rows: list[dict[str, Any]] = []
        for spec in specs:
            query = spec.pop("query")
            support = top_claim_ids(query, None, None, 7)
            row = dict(spec)
            row["source_claims"] = support
            rows.append(row)
            spec["query"] = query
        write_csv(SYNTH_DIR / f"{name}.csv", rows, list(rows[0]))
        counts[name] = len(rows)
    md = ["# Interaction, access, enablement, and budget taxonomy", "", "The matrices keep status ladders typed and prevent familiar collapses. Source claim IDs are navigation pointers; the frozen TeX remains authoritative.", ""]
    for name, specs in TAXONOMY_TABLES.items():
        title = name.replace("_", " ").title()
        md += [f"## {title}", "", f"Machine-readable table: `{name}.csv` ({len(specs)} rows).", ""]
        for spec in specs:
            key = spec.get("state") or spec.get("kind") or spec.get("status") or spec.get("attribution") or spec.get("currency")
            md.append(f"- **{key}:** {spec['definition']} **Boundary:** {spec.get('nonimplication') or spec.get('nonclaim') or spec.get('failure_refund')}")
        md.append("")
    (SYNTH_DIR / "INTERACTION_ACCESS_TAXONOMY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return counts


def build_version_claim_delta() -> list[dict[str, Any]]:
    """Align P040/P058 claims conservatively without quadratic long-text diffing.

    Exact normalized matches are paired first. Remaining rows are matched only
    within a bounded relative-order window using token similarity. This is a
    navigation delta, never theorem-equivalence evidence.
    """
    a = BY_PAPER["P040"]
    b = BY_PAPER["P058"]
    unused = set(range(len(b)))
    exact_index: dict[tuple[str, str], list[int]] = defaultdict(list)
    for j, cb in enumerate(b):
        exact_index[(cb["claim_type"], cb.get("normalized_claim", ""))].append(j)
    rows: list[dict[str, Any]] = []
    for i, ca in enumerate(a):
        exact_candidates = [j for j in exact_index.get((ca["claim_type"], ca.get("normalized_claim", "")), []) if j in unused]
        best_j: int | None = exact_candidates[0] if exact_candidates else None
        best_score = 1.0 if best_j is not None else -1.0
        if best_j is None:
            expected = round(i * max(len(b) - 1, 0) / max(len(a) - 1, 1))
            candidates = [j for j in unused if abs(j - expected) <= 24]
            if not candidates:
                candidates = list(unused)
            qa = ca.get("normalized_claim", "")[:6000]
            for j in candidates:
                cb = b[j]
                score = lexical_similarity(qa, cb.get("normalized_claim", "")[:6000])
                if ca["claim_type"] == cb["claim_type"]:
                    score += 0.08
                else:
                    score -= 0.08
                score -= min(abs(j - expected), 100) * 0.001
                if score > best_score:
                    best_score, best_j = score, j
        if best_j is not None and best_score >= 0.42:
            cb = b[best_j]
            unused.remove(best_j)
            if ca.get("normalized_claim") == cb.get("normalized_claim"):
                status = "IDENTICAL_NORMALIZED_STATEMENT"
                shown_score = 1.0
            elif best_score >= 0.83:
                status = "NEAR_EQUIVALENT_WORDING_NOT_THEOREM_EQUIVALENCE"
                shown_score = min(best_score, 0.9999)
            elif best_score >= 0.62:
                status = "RELATED_CHANGED_WORDING_OR_SCOPE"
                shown_score = best_score
            else:
                status = "TENTATIVE_ALIGNMENT_REQUIRES_CLAIM_REVIEW"
                shown_score = best_score
            rows.append({
                "family_id": "VF-SAU-01", "p040_claim": ca["claim_id"], "p058_claim": cb["claim_id"],
                "p040_type": ca["claim_type"], "p058_type": cb["claim_type"], "similarity": round(max(0.0, shown_score), 4),
                "status": status, "p040_source": ca["source_location"], "p058_source": cb["source_location"],
                "semantic_ruling": "Navigation alignment only; no theorem equivalence or evidence independence is inferred.",
            })
        else:
            rows.append({
                "family_id": "VF-SAU-01", "p040_claim": ca["claim_id"], "p058_claim": "", "p040_type": ca["claim_type"], "p058_type": "",
                "similarity": round(max(best_score, 0.0), 4), "status": "P040_ONLY_AT_STEP2_ALIGNMENT_THRESHOLD",
                "p040_source": ca["source_location"], "p058_source": "", "semantic_ruling": "No aligned P058 claim was promoted at the conservative threshold.",
            })
    for j in sorted(unused):
        cb = b[j]
        rows.append({
            "family_id": "VF-SAU-01", "p040_claim": "", "p058_claim": cb["claim_id"], "p040_type": "", "p058_type": cb["claim_type"],
            "similarity": 0.0, "status": "P058_ONLY_AT_STEP2_ALIGNMENT_THRESHOLD", "p040_source": "", "p058_source": cb["source_location"],
            "semantic_ruling": "No aligned P040 claim was promoted at the conservative threshold.",
        })
    write_csv(BRIDGE_DIR / "VF-SAU-01_claim_delta.csv", rows, list(rows[0]))
    counts = Counter(r["status"] for r in rows)
    md = [
        "# P040/P058 claim-level version-family delta", "",
        "P040 and P058 remain one non-independent unresolved family. Claim alignment is a source-navigation aid, not theorem-equivalence evidence.", "",
        f"- P040 claims: {len(a)}; P058 claims: {len(b)}; aligned/delta rows: {len(rows)}.",
        f"- Status census: `{dict(counts)}`.", "",
        "The exact source-level line and section deltas from Step 1 remain controlling. No canonical member is selected in Step 2.",
    ]
    (BRIDGE_DIR / "VF-SAU-01_CLAIM_DELTA.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows

def build_wishlist_links(all_bridges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    atoms = read_csv(WISH_DIR / "atomic_requests.csv")
    group_rows = read_csv(WISH_DIR / "convergence_groups.csv")
    group_by_request = {r["request_id"]: r["convergence_group"] for r in group_rows}
    bridge_by_claim: dict[str, list[str]] = defaultdict(list)
    audited_laws_by_claim: dict[str, set[str]] = defaultdict(set)
    for b in all_bridges:
        if b["bridge_kind"] == "PRIOR_LAW_REUSE_CONTRACT":
            continue
        bridge_by_claim[b["source_claim"]].append(b["bridge_id"])
        bridge_by_claim[b["target_claim_or_context"]].append(b["bridge_id"])
        if b["bridge_kind"] == "NAMED_LAW_IMPORT":
            for cid in b.get("target_claims", []) or [b["target_claim_or_context"]]:
                audited_laws_by_claim[cid].add(b["source_law"])
                bridge_by_claim[cid].append(b["bridge_id"])
    rows: list[dict[str, Any]] = []
    for atom in atoms:
        rid = atom["request_id"]
        group = group_by_request.get(rid, "")
        query = " ".join([atom.get("atomic_request", ""), atom.get("required_artifact", ""), atom.get("cluster", ""), atom.get("acceptance_or_red_line", "")])
        candidates = [c for c in CLAIMS if group in (c.get("vii_links") or [])]
        if not candidates:
            candidates = CLAIMS
        support_pool = [c for c in candidates if c["claim_type"] not in {"nonclaim", "scope_boundary", "open_problem", "remark"}]
        boundary_pool = [c for c in candidates if c["claim_type"] in {"nonclaim", "scope_boundary"} or c.get("no_go_id")]
        open_pool = [c for c in candidates if c["claim_type"] == "open_problem"]
        support = [cid for _, cid in sorted(((claim_score(c, query), c["claim_id"]) for c in support_pool), reverse=True)[:10]]
        boundary = [cid for _, cid in sorted(((claim_score(c, query), c["claim_id"]) for c in boundary_pool), reverse=True)[:8]]
        opens = [cid for _, cid in sorted(((claim_score(c, query), c["claim_id"]) for c in open_pool), reverse=True)[:5]]
        laws: set[str] = set()
        for cid in support + boundary:
            c = CLAIM_BY_ID[cid]
            if c.get("law_id"): laws.add(c["law_id"])
            if c.get("no_go_id"): laws.add(c["no_go_id"])
            # Only source-audited named-law imports may enter the precision
            # wishlist linkage.  The claim-level imported_laws field remains a
            # recall aid and can contain local-label collisions.
            laws.update(audited_laws_by_claim.get(cid, set()))
        # Canonical registries use G1 for the law row; G1b is a component tag
        # internal to the paper statement and must not leak into cross-artifact
        # law identifiers.
        laws = {"G1" if law == "G1b" else law for law in laws}
        bridge_ids: list[str] = []
        for cid in support + boundary:
            bridge_ids.extend(bridge_by_claim.get(cid, []))
        bridge_ids = list(dict.fromkeys(bridge_ids))[:20]
        prior = atom.get("prior_coverage_status") or atom.get("step1_disposition", "")
        counter_req = (atom.get("countermodel_requirement", "") or "").upper()
        if "BLOCK" in prior.upper():
            status = "CONSTRAINED_BY_EXISTING_NO_GO_OR_SOURCE_BLOCK"
        elif counter_req == "YES" or "COUNTERMODEL" in prior.upper():
            status = "COUNTERMODEL_OBLIGATION_CONFIRMED"
        elif "EXIST" in prior.upper() and "PARTIAL" not in prior.upper():
            status = "CORPUS_RESULT_IDENTIFIED_VERIFY_EXACT_SCOPE"
        elif "PARTIAL" in prior.upper():
            status = "PARTIAL_PRECEDENT_IDENTIFIED"
        elif "UNCLEAR" in prior.upper():
            status = "UNRESOLVED_REQUIRES_LATER_SCOPE_DECISION"
        else:
            status = "RELATED_PRECEDENT_ONLY_NEW_VII_WORK_REMAINS"
        rows.append({
            **atom,
            "convergence_group": group,
            "step2_evidence_status": status,
            "supporting_claim_ids": support,
            "counterclaim_or_boundary_ids": boundary,
            "open_problem_ids": opens,
            "linked_law_or_no_go_ids": sorted(laws),
            "linked_bridge_ids": bridge_ids,
            "future_readiness_obligation": "A later phase must adjudicate inheritance versus new VII work; Step 2 supplies evidence and boundaries only.",
        })
    write_csv(WISH_DIR / "step2_evidence_links.csv", rows, list(rows[0]))
    write_jsonl(WISH_DIR / "step2_evidence_links.jsonl", rows)
    counts = Counter(r["step2_evidence_status"] for r in rows)
    md = ["# Wish-list evidence disposition after Step 2", "", "All 130 atomic requests are linked to supporting claims, boundary/counterclaims, open problems, laws/no-gos, and bridge records. These are evidence dispositions, not final Foundations VII adjudications.", "", f"Status census: `{dict(counts)}`.", "", "| Request | Group | Step-2 evidence status | Supporting claims | Boundaries |", "|---|---|---|---:|---:|"]
    for r in rows:
        md.append(f"| `{r['request_id']}` | `{r['convergence_group']}` | `{r['step2_evidence_status']}` | {len(r['supporting_claim_ids'])} | {len(r['counterclaim_or_boundary_ids'])} |")
    (WISH_DIR / "WISHLIST_DISPOSITION_STEP2.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows



def augment_dossiers(all_bridges: list[dict[str, Any]], wish_rows: list[dict[str, Any]], app_rows: list[dict[str, Any]]) -> None:
    """Append a deterministic bridge-completion supplement to every dossier."""
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for b in all_bridges:
        if b.get("target_paper") in BY_PAPER:
            by_target[b["target_paper"]].append(b)
        if b.get("source_paper") in BY_PAPER:
            by_source[b["source_paper"]].append(b)
    wish_by_paper: dict[str, set[str]] = defaultdict(set)
    for w in wish_rows:
        for cid in (w.get("supporting_claim_ids") or []) + (w.get("counterclaim_or_boundary_ids") or []) + (w.get("open_problem_ids") or []):
            c = CLAIM_BY_ID.get(cid)
            if c:
                wish_by_paper[c["source_paper"]].add(w["request_id"])
    app_by_pid = {r["paper_id"]: r for r in app_rows}
    start_marker = "<!-- STEP2_BRIDGE_SUPPLEMENT_START -->"
    end_marker = "<!-- STEP2_BRIDGE_SUPPLEMENT_END -->"
    for pid in sorted(BY_PAPER):
        path = ROOT / "notes" / "dossiers" / f"{pid}.md"
        text = path.read_text(encoding="utf-8")
        if start_marker in text and end_marker in text:
            text = text.split(start_marker, 1)[0].rstrip() + "\n"
        if pid == "P039":
            text = text.replace("`CLAIM_EXTRACTED_BLOCKED_FULL_TEXT`", "`BLOCKED_FULL_TEXT_WITH_ABSTRACT_BRIDGE_AUDIT`")
        else:
            text = text.replace("`CLAIM_EXTRACTED`", "`BRIDGED`", 1)
        outgoing = [b for b in by_target.get(pid, []) if b["bridge_kind"] != "PRIOR_LAW_REUSE_CONTRACT"]
        incoming = [b for b in by_source.get(pid, []) if b["bridge_kind"] != "PRIOR_LAW_REUSE_CONTRACT"]
        reuse = [b for b in by_source.get(pid, []) if b["bridge_kind"] == "PRIOR_LAW_REUSE_CONTRACT"]
        classes = Counter(b["classification"] for b in outgoing)
        unresolved = sum(1 for b in outgoing if b["classification"] in {"UNKNOWN_REQUIRES_PROOF", "ANALOGY_ONLY_OR_DOMAIN_MAP_REQUIRED", "PARTIAL_BRIDGE_REQUIRES_DOMAIN_MAP", "BLOCKED_SOURCE"})
        supplement = [
            start_marker,
            "",
            "## Step-2 bridge-completion supplement",
            "",
            f"- **Outbound/import invocation rows:** {len(outgoing)}; classification census: `{dict(classes)}`.",
            f"- **Inbound reuse rows from later papers:** {len(incoming)}.",
            f"- **Prior-law/no-go reuse contracts sourced here:** {len(reuse)}.",
            f"- **Wish-list atoms linked through this paper's claims/boundaries:** {len(wish_by_paper.get(pid, set()))}.",
            f"- **Undischarged/analogy/source-blocked invocation rows:** {unresolved}. These rows carry their exact obligations in `bridges/bridge_atlas.*`.",
            "- Citation remains navigation evidence; exact reuse requires statement-level type/hypothesis, nonclaim, trust-base, and machine-status checks.",
        ]
        if pid in app_by_pid:
            app = app_by_pid[pid]
            supplement += [
                f"- **Application pressure-test ruling:** `{app['pressure_test_ruling']}`.",
                f"- **Forbidden back-transfer:** {app['forbidden_back_transfer']}",
            ]
        if pid == "P039":
            supplement += [
                "- **Inherited blocker:** eighteen included TeX files and the bibliography are absent. The bridge audit therefore licenses no theorem-level transfer beyond the supplied abstract.",
            ]
        supplement += [
            "",
            "### Bridge files",
            "",
            "- `bridges/paper_invocation_bridges.*` — all in-corpus citation contexts.",
            "- `bridges/imported_law_bridges.*` — every source-audited named F/E/G import pair; local-label collisions are retained in `bridges/named_law_occurrence_audit.*`.",
            "- `bridges/law_reuse_contracts.*` — all F/E/G/no-go source contracts.",
            "- `wishlists/step2_evidence_links.*` — request-level support, counterclaims, and unresolved obligations.",
            "",
            end_marker,
        ]
        path.write_text(text.rstrip() + "\n\n" + "\n".join(supplement) + "\n", encoding="utf-8")
        json_path = ROOT / "notes" / "dossiers" / f"{pid}.json"
        dossier = json.loads(json_path.read_text(encoding="utf-8"))
        dossier["status"] = "BLOCKED_FULL_TEXT_WITH_ABSTRACT_BRIDGE_AUDIT" if pid == "P039" else "BRIDGED"
        dossier["bridge_completion"] = {
            "outbound_or_import_bridge_ids": [b["bridge_id"] for b in outgoing],
            "inbound_reuse_bridge_ids": [b["bridge_id"] for b in incoming],
            "source_reuse_contract_ids": [b["bridge_id"] for b in reuse],
            "classification_counts": dict(classes),
            "undischarged_or_blocked_count": unresolved,
            "wishlist_request_ids": sorted(wish_by_paper.get(pid, set())),
            "application_pressure_test": app_by_pid.get(pid),
        }
        json_path.write_text(json.dumps(dossier, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Promote dossier index statuses without altering extraction counts.
    index_path = ROOT / "corpus" / "step2_dossier_index.csv"
    index_rows = read_csv(index_path)
    for r in index_rows:
        r["status"] = "BLOCKED_FULL_TEXT_WITH_ABSTRACT_BRIDGE_AUDIT" if r["paper_id"] == "P039" else "BRIDGED"
    write_csv(index_path, index_rows, list(index_rows[0]))
    md = ["# Step-2 dossier index", "", "All supplied source has been processed in one canonical claim-ID space. P039 remains explicitly source-blocked.", "", "| Paper | Status | Claims | Formal | Definitions | Nonclaims/scope | Open |", "|---|---|---:|---:|---:|---:|---:|"]
    for r in index_rows:
        md.append(f"| [{r['paper_id']}](../{r['dossier']}) | `{r['status']}` | {r['claim_count']} | {r['formal_claim_count']} | {r['definition_count']} | {r['nonclaim_scope_count']} | {r['open_problem_count']} |")
    (ROOT / "reports" / "STEP2_DOSSIER_INDEX.md").write_text("\n".join(md) + "\n", encoding="utf-8")

def build_claim_graph(all_bridges: list[dict[str, Any]], wish_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    for c in CLAIMS:
        nodes.append({
            "node_id": c["claim_id"], "node_type": "CLAIM", "paper_id": c["source_paper"], "claim_type": c["claim_type"], "grade": c["claim_grade"], "label": compact(c.get("normalized_claim", ""), 260),
        })
    for law in LAW_ROWS + NG_ROWS:
        nodes.append({"node_id": f"LAW:{law['law_id']}", "node_type": "LAW_OR_NO_GO", "paper_id": law["source_paper"], "claim_type": "LAW", "grade": law.get("formal_status") or law.get("paper_grade") or "THEOREM", "label": law.get("name", law["law_id"])})
    for w in wish_rows:
        nodes.append({"node_id": f"WISH:{w['request_id']}", "node_type": "WISH_ATOM", "paper_id": "", "claim_type": "WISH", "grade": w["step2_evidence_status"], "label": compact(w["atomic_request"], 260)})
    edges: list[dict[str, Any]] = []
    eid = 0
    def add(source: str, target: str, etype: str, classification: str = "") -> None:
        nonlocal eid
        eid += 1
        edges.append({"edge_id": f"E{eid:06d}", "source": source, "target": target, "edge_type": etype, "classification": classification})
    for c in CLAIMS:
        for d in c.get("dependencies", []) or []:
            pid = d.get("paper_id", "") if isinstance(d, dict) else ""
            if pid in BY_PAPER:
                add(c["claim_id"], thesis_claim(pid)["claim_id"], "CITES_PAPER", "NAVIGATION_NOT_THEOREM_BRIDGE")
        if c.get("law_id"):
            source_law = "G1" if c["law_id"] == "G1b" else c["law_id"]
            add(c["claim_id"], f"LAW:{source_law}", "IS_SOURCE_STATEMENT_FOR", "SOURCE_REGISTRY_LINK")
        if c.get("no_go_id"):
            add(c["claim_id"], f"LAW:{c['no_go_id']}", "IS_SOURCE_STATEMENT_FOR", "SOURCE_REGISTRY_LINK")
        for nc in c.get("nonclaims", []) or []:
            if nc in CLAIM_BY_ID:
                add(c["claim_id"], nc, "BOUNDED_BY_NONCLAIM", "SCOPE_BOUNDARY")
    for b in all_bridges:
        if b["target_claim_or_context"] in CLAIM_BY_ID:
            add(b["source_claim"], b["target_claim_or_context"], "BRIDGE", b["classification"])
    for w in wish_rows:
        wid = f"WISH:{w['request_id']}"
        for cid in w["supporting_claim_ids"]:
            add(cid, wid, "SUPPORTS_WISH", w["step2_evidence_status"])
        for cid in w["counterclaim_or_boundary_ids"]:
            add(cid, wid, "BOUNDS_WISH", "COUNTERCLAIM_OR_SCOPE")
    write_csv(SYNTH_DIR / "claim_graph_nodes.csv", nodes, list(nodes[0]))
    write_csv(SYNTH_DIR / "claim_graph_edges.csv", edges, list(edges[0]))
    graphml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="ntype" for="node" attr.name="node_type" attr.type="string"/>',
        '  <key id="etype" for="edge" attr.name="edge_type" attr.type="string"/>',
        '  <key id="class" for="edge" attr.name="classification" attr.type="string"/>',
        '  <graph id="Step2ClaimGraph" edgedefault="directed">',
    ]
    for n in nodes:
        graphml.append(f'    <node id="{html.escape(n["node_id"])}"><data key="label">{html.escape(n["label"])}</data><data key="ntype">{html.escape(n["node_type"])}</data></node>')
    for e in edges:
        graphml.append(f'    <edge id="{e["edge_id"]}" source="{html.escape(e["source"])}" target="{html.escape(e["target"])}"><data key="etype">{html.escape(e["edge_type"])}</data><data key="class">{html.escape(e["classification"])}</data></edge>')
    graphml += ["  </graph>", "</graphml>"]
    (SYNTH_DIR / "claim_dependency_graph.graphml").write_text("\n".join(graphml) + "\n", encoding="utf-8")
    return nodes, edges


def write_conflict_register() -> list[dict[str, Any]]:
    rows = [
        {"conflict_id": "CF-01", "topic": "P040/P058 version family", "papers": ["P040", "P058"], "status": "NON_INDEPENDENT_UNRESOLVED_VERSION_FAMILY", "source_grounding": ["bridges/VF-SAU-01_claim_delta.csv", "corpus/version_family_line_delta.csv"], "safe_ruling": "Count as one evidence family; do not select a canonical member or infer theorem equivalence at Step 2."},
        {"conflict_id": "CF-02", "topic": "P039 incomplete source", "papers": ["P039"], "status": "BLOCKED_MISSING_18_INCLUDES_AND_BIBLIOGRAPHY", "source_grounding": ["notes/dossiers/P039.md", "corpus/source_exceptions.csv"], "safe_ruling": "Use supplied abstract only; do not reconstruct theorem text, proofs, nonclaims, or bridges."},
        {"conflict_id": "CF-03", "topic": "Foundations IV paper law surface versus local Lean availability", "papers": ["P028"], "status": "52_PAPER_ROWS_14_LOCAL_MODULES", "source_grounding": ["formalization/integration/f_law_formalization_disclosure.csv"], "safe_ruling": "Paper theorem grade and local module availability remain distinct."},
        {"conflict_id": "CF-04", "topic": "Lean source presence versus local kernel replay", "papers": ["P026", "P027", "P028", "P029", "P030", "P031"], "status": "STATIC_IMPORT_GRAPH_ONLY_LOCAL_LEAN_4_28_UNAVAILABLE", "source_grounding": ["formalization/integration/cumulative_formalization_summary.json"], "safe_ruling": "Do not claim a fresh local Lean kernel build."},
        {"conflict_id": "CF-05", "topic": "Application claims and general SBT", "papers": sorted(APP_PAPERS), "status": "DOMAIN_BOUND_BRIDGES_OR_ANALOGY_ONLY", "source_grounding": ["synthesis/step2/application_pressure_tests.csv"], "safe_ruling": "No application-specific conclusion transfers back to the abstract theory without an explicit typed bridge."},
        {"conflict_id": "CF-06", "topic": "Objecthood, novelty, and directionality", "papers": ["P031", "P027", "P026", "P028", "P029"], "status": "LOGICALLY_DISTINCT_CERTIFICATES", "source_grounding": ["synthesis/SBT_STEP1_SYNTHESIS.md", "bridges/INVALID_TRANSFER_REPORT.md"], "safe_ruling": "Never infer one certificate from another."},
    ]
    write_csv(BRIDGE_DIR / "unresolved_conflicts.csv", rows, list(rows[0]))
    write_jsonl(BRIDGE_DIR / "unresolved_conflicts.jsonl", rows)
    return rows


def update_coverage() -> None:
    rows = read_csv(ROOT / "corpus" / "coverage.csv")
    for r in rows:
        pid = r["paper_id"]
        if pid == "P039":
            r["state"] = "BLOCKED"
            r["deep_note"] = "notes/dossiers/P039.md"
            r["last_transition"] = TODAY
            r["transition_note"] = "Step 2 completed for supplied abstract; full claim/proof/nonclaim read blocked by 18 missing TeX includes and bibliography"
        else:
            r["state"] = "BRIDGED"
            r["deep_note"] = f"notes/dossiers/{pid}.md"
            r["last_transition"] = TODAY
            r["transition_note"] = "Step 2 canonical claim extraction, formalization matching, invocation audit, and bridge classification complete"
    write_csv(ROOT / "corpus" / "coverage.csv", rows, list(rows[0]))


def write_bridge_overview(all_bridges: list[dict[str, Any]], invalid: list[dict[str, Any]], no_gos: list[dict[str, Any]], apps: list[dict[str, Any]], version_rows: list[dict[str, Any]], tax_counts: dict[str, int]) -> None:
    kinds = Counter(b["bridge_kind"] for b in all_bridges)
    classes = Counter(b["classification"] for b in all_bridges)
    md = [
        "# Step-2 bridge atlas",
        "",
        f"- Canonical claim IDs: **{len(CLAIMS)}** across **{len(BY_PAPER)}** papers.",
        f"- Bridge rows: **{len(all_bridges)}**; kinds: `{dict(kinds)}`.",
        f"- Classification census: `{dict(classes)}`.",
        f"- Invalid-transfer rules: **{len(invalid)}**.",
        f"- No-go scope rows: **{len(no_gos)}**.",
        f"- Application pressure tests: **{len(apps)}**.",
        f"- P040/P058 claim-delta rows: **{len(version_rows)}**.",
        f"- Taxonomy rows: `{tax_counts}`.",
        "",
        "## Reuse rule",
        "",
        "A citation is navigation evidence. A named law identifier is still not a proof. Exact reuse requires the source claim, all hypotheses, a typed carrier/interface map, statement-fidelity audit, nonclaims, trust-base accounting, and the recorded machine-check status.",
        "",
        "## Source exception",
        "",
        "P039 is represented by its supplied abstract and remains `BLOCKED_MISSING_INCLUDED_FILES`; no missing theorem or bridge text has been reconstructed.",
    ]
    (BRIDGE_DIR / "BRIDGE_ATLAS.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    # Remove obsolete competing-ID products if present.
    for p in [ROOT / "registry" / "step2", ROOT / "generated" / "step2", ROOT / "notes" / "claim_dossiers"]:
        if p.exists():
            import shutil
            shutil.rmtree(p)
    for p in [
        ROOT / "generated" / "step2_claim_corpus_summary.json",
        ROOT / "corpus" / "step2_paper_census.csv",
        ROOT / "corpus" / "step2_paper_census.json",
        ROOT / "corpus" / "step2_paper_summary.csv",
        ROOT / "bridges" / "citation_context_bridges.csv",
        ROOT / "bridges" / "NO_GO_SCOPE_MATRIX.md",
    ]:
        if p.exists():
            p.unlink()

    citation = build_citation_bridges()
    named_occurrences = scan_named_law_occurrences()
    imported = build_imported_law_bridges(named_occurrences)
    reuse = build_law_reuse_contracts()
    all_bridges = citation + imported + reuse
    write_jsonl(BRIDGE_DIR / "bridge_atlas.jsonl", all_bridges)
    write_csv(BRIDGE_DIR / "bridge_atlas.csv", all_bridges, list(all_bridges[0]))
    write_jsonl(BRIDGE_DIR / "paper_invocation_bridges.jsonl", citation)
    write_csv(BRIDGE_DIR / "paper_invocation_bridges.csv", citation, list(citation[0]))
    write_jsonl(BRIDGE_DIR / "imported_law_bridges.jsonl", imported)
    write_csv(BRIDGE_DIR / "imported_law_bridges.csv", imported, list(imported[0]))
    write_jsonl(BRIDGE_DIR / "law_reuse_contracts.jsonl", reuse)
    write_csv(BRIDGE_DIR / "law_reuse_contracts.csv", reuse, list(reuse[0]))

    invalid = write_invalid_transfers()
    no_gos = write_no_go_scope_matrix()
    apps = write_application_pressure_tests(imported)
    example_carriers = write_examples_carrier_registry(apps)
    tax_counts = write_taxonomies()
    version_rows = build_version_claim_delta()
    wish = build_wishlist_links(all_bridges)
    augment_dossiers(all_bridges, wish, apps)
    nodes, edges = build_claim_graph(all_bridges, wish)
    conflicts = write_conflict_register()
    update_coverage()
    write_bridge_overview(all_bridges, invalid, no_gos, apps, version_rows, tax_counts)

    summary = {
        "canonical_claims": len(CLAIMS),
        "papers": len(BY_PAPER),
        "citation_bridge_rows": len(citation),
        "named_law_candidate_occurrences": len(named_occurrences),
        "named_law_accepted_occurrences": sum(1 for r in named_occurrences if r["decision"].startswith("ACCEPTED")),
        "named_law_import_rows": len(imported),
        "prior_law_reuse_contracts": len(reuse),
        "total_bridge_rows": len(all_bridges),
        "bridge_kinds": dict(Counter(b["bridge_kind"] for b in all_bridges)),
        "bridge_classifications": dict(Counter(b["classification"] for b in all_bridges)),
        "no_go_scope_rows": len(no_gos),
        "invalid_transfer_rows": len(invalid),
        "application_rows": len(apps),
        "example_carrier_rows": len(example_carriers),
        "wishlist_atoms": len(wish),
        "version_delta_rows": len(version_rows),
        "taxonomy_rows": tax_counts,
        "graph_nodes": len(nodes),
        "graph_edges": len(edges),
        "conflict_rows": len(conflicts),
        "source_blockers": ["P039"],
        "step3_started": False,
    }
    (GENERATED / "step2_bridge_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
