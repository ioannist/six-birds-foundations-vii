#!/usr/bin/env python3
"""Build the complete Step-2 source-grounded claim corpus and paper dossiers."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from step2_common import (
    ROOT, METADATA, claim_grade_for, classify_prose_paragraph, collect_simple_macros,
    ensure_dirs, extract_environments, find_expanded_path, format_location, json_load,
    expand_simple_macros, lexical_similarity, normalize_tokens, paragraph_spans, read_csv, source_line_map,
    split_hypotheses_conclusion, tex_to_plain, write_csv, write_jsonl,
)

CLAIMS_DIR = ROOT / "claims"
BY_PAPER = CLAIMS_DIR / "by_paper"
DOSSIERS = ROOT / "notes" / "dossiers"
REGISTRY = ROOT / "registry"
GENERATED = ROOT / "generated"

CATALOG = read_csv(ROOT / "config" / "paper_catalog.csv")
CAT_BY_ID = {r["paper_id"]: r for r in CATALOG}
DEPS = json_load(ROOT / "corpus" / "dependency_trees.json")
DISCLOSURES = {r["paper_id"]: r for r in read_csv(ROOT / "corpus" / "survey_artifact_formalization.csv")}
CITATION_EDGES = read_csv(ROOT / "corpus" / "paper_dependency_edges.csv")

F_ROWS = {r["law_id"]: r for r in read_csv(ROOT / "registry" / "F_laws.csv")}
E_ROWS = {r["law_id"]: r for r in read_csv(ROOT / "registry" / "E_laws.csv")}
G_ROWS = {r["law_id"]: r for r in read_csv(ROOT / "registry" / "G_laws.csv")}
NG_ROWS = {r["law_id"]: r for r in read_csv(ROOT / "registry" / "no_go_theorems.csv")}
F_DISC = {r["law_id"]: r for r in read_csv(ROOT / "formalization" / "integration" / "f_law_formalization_disclosure.csv")}
E_DISC = {r["law_id"]: r for r in read_csv(ROOT / "formalization" / "integration" / "e_law_formalization_disclosure.csv")}
G_DISC = {r["law_id"]: r for r in read_csv(ROOT / "formalization" / "integration" / "g_law_formalization_disclosure.csv")}
E_TRACE = {r["law_id"]: r for r in read_csv(ROOT / "formalization" / "integration" / "foundations_v_e_law_traceability.csv")}
G_TRACE = {r["law_id"]: r for r in read_csv(ROOT / "formalization" / "integration" / "g_law_traceability.csv")}
LEAN_DECLS = read_csv(ROOT / "formalization" / "integration" / "cumulative_lean_declarations.csv")
LEAN_THEOREMS = [r for r in LEAN_DECLS if r["kind"] == "theorem"]
TRUST_BASE = [r["fully_qualified_name"] for r in LEAN_DECLS if r["kind"] in {"axiom", "opaque"}]

# Candidate local module families.  Matching is a navigation aid unless a law
# disclosure row explicitly establishes statement fidelity.
MODULE_PREFIXES = {
    "P031": ("ClosureLadder", "SixBirdsMetaMath.FoundationsICompat"),
    "P027": ("SixBirds.", "SixBirds"),
    "P026": ("SixBirdsIII",),
    "P028": ("SixBirdsMetaMath.FoundationsIV",),
    "P030": ("SixBirdsFoundationsV",),
    "P029": ("SixBirdsFoundationsVI",),
    "P012": ("HolonomyMemory",),
    "P004": ("Xi.", "SixBirdsMetaMath.Xi", "Main.CriticalPair", "SixBirdsMetaMath.Main.CriticalPair"),
    "P034": ("ClosureLadder",),
    "P040": ("ClosureLadder", "Xi.", "Main.", "SixBirdsMetaMath.Main"),
    "P058": ("ClosureLadder", "Xi.", "Main.", "SixBirdsMetaMath.Main"),
}

# Convergence groups are linked by paper-level relevance.  Step 2 uses these
# as a recall net; the wish-list builder later ranks exact claims inside them.
GROUP_PAPER_MAP = {
    "CG01": ["P011", "P004", "P009", "P028", "P030", "P032", "P034"],
    "CG02": ["P027", "P026", "P008", "P003", "P030", "P045"],
    "CG03": ["P031", "P032", "P034", "P011", "P004", "P028"],
    "CG04": ["P030", "P029", "P054", "P051", "P042"],
    "CG05": ["P011", "P028", "P026", "P049", "P023"],
    "CG06": ["P026", "P016", "P022", "P021", "P008", "P003"],
    "CG07": ["P015", "P016", "P022", "P028", "P032", "P048"],
    "CG08": ["P016", "P022", "P021", "P014", "P003", "P037", "P028"],
    "CG09": ["P026", "P044", "P030", "P049", "P013"],
    "CG10": ["P004", "P054", "P030", "P029", "P042"],
    "CG11": ["P016", "P012", "P048", "P025", "P049", "P028"],
    "CG12": ["P012", "P033", "P048", "P025", "P029", "P051"],
    "CG13": ["P016", "P022", "P028", "P037", "P049"],
    "CG14": ["P030", "P005", "P055", "P013", "P045", "P043"],
    "CG15": ["P045", "P038", "P030", "P043", "P050"],
    "CG16": ["P005", "P055", "P044", "P013", "P030", "P056"],
    "CG17": ["P007", "P008", "P003", "P037", "P028", "P040", "P058"],
    "CG18": ["P012", "P033", "P048", "P025", "P051", "P029"],
    "CG19": ["P004", "P054", "P030", "P042", "P029"],
    "CG20": ["P026", "P030", "P055", "P044", "P013"],
    "CG21": ["P031", "P027", "P026", "P028", "P030", "P029"],
    "CG22": ["P032", "P015", "P023", "P034", "P025"],
    "CG23": ["P026", "P028", "P030", "P029", "P050"],
    "CG24": ["P004", "P009", "P011", "P054", "P042"],
    "CG25": ["P006", "P040", "P058", "P041", "P046", "P056"],
    "CG26": ["P005", "P055", "P044", "P013", "P056"],
    "CG27": ["P001", "P002", "P017", "P018", "P019", "P020", "P024", "P035", "P036", "P039", "P047", "P049", "P052", "P057"],
    "CG28": ["P026", "P028", "P030", "P029", "P032"],
    "CG29": ["P040", "P058", "P006", "P023", "P034"],
    "CG30": ["P031", "P027", "P026", "P028", "P030", "P029", "P032"],
}
PAPER_GROUPS: dict[str, list[str]] = defaultdict(list)
for group, pids in GROUP_PAPER_MAP.items():
    for pid in pids:
        PAPER_GROUPS[pid].append(group)


def cite_dependencies(text: str, pid: str) -> list[dict[str, Any]]:
    by_key: dict[str, str] = {}
    for edge in CITATION_EDGES:
        if edge["source_paper_id"] != pid:
            continue
        for k in edge["citation_keys"].split(";"):
            if k.strip():
                by_key[k.strip()] = edge["target_paper_id"]
    found: list[dict[str, Any]] = []
    for m in re.finditer(r"\\cite\w*\*?(?:\[[^\]]*\])?\{([^{}]+)\}", text):
        for key in m.group(1).split(","):
            k = key.strip()
            if not k:
                continue
            found.append({"citation_key": k, "paper_id": by_key.get(k, "OUT_OF_CORPUS_OR_UNRESOLVED")})
    # stable unique
    seen = set()
    out = []
    for x in found:
        sig = (x["citation_key"], x["paper_id"])
        if sig not in seen:
            seen.add(sig); out.append(x)
    return out


def imported_laws(text: str, own_paper: str) -> list[str]:
    ids = set(re.findall(r"\b(?:F(?:[1-9]|[1-4][0-9]|5[0-2])(?:[ab])?|E(?:[1-9]|1[0-6])|G(?:[1-9]|1[0-3])(?:b)?)\b", text))
    # Normalize G1b as G1 for source-law lookup but retain component tag.
    out = []
    for law in sorted(ids, key=lambda x: (x[0], int(re.search(r"\d+", x).group()), x)):
        if (own_paper == "P028" and law.startswith("F")) or (own_paper == "P030" and law.startswith("E")) or (own_paper == "P029" and law.startswith("G")):
            continue
        out.append(law)
    return out


def typed_objects(statement: str) -> list[dict[str, str]]:
    objs: list[dict[str, str]] = []
    # Plain-language declarations.
    for m in re.finditer(r"\b(?:Let|Fix|Given|For)\s+([^.;]{1,140}?)\s+be\s+(?:an?|the)\s+([^.;]{1,140})", statement, flags=re.I):
        objs.append({"symbol_or_phrase": m.group(1).strip(), "declared_type_or_role": m.group(2).strip()})
    # Map/interface signatures.
    for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]*)\s*:\s*([^,.;]{1,80}?)(?:→|->|to)\s*([^,.;]{1,80})", statement):
        objs.append({"symbol_or_phrase": m.group(1), "declared_type_or_role": f"map/interface {m.group(2).strip()} → {m.group(3).strip()}"})
    # Deduplicate and bound; full source wording remains authoritative.
    seen = set(); out = []
    for obj in objs:
        sig = (obj["symbol_or_phrase"], obj["declared_type_or_role"])
        if sig not in seen:
            seen.add(sig); out.append(obj)
    return out[:24]


def law_id_from_claim(pid: str, title: str, body: str, labels: list[str]) -> str | None:
    joined = " ".join(labels + [title, body[:500]])
    series = {"P028": "F", "P030": "E", "P029": "G"}.get(pid)
    if not series:
        return None
    # labels such as thm:F13a or theorem:E1
    m = re.search(r"(?:^|[:_-])(" + series + r"\d+(?:[ab])?)\b", joined, flags=re.I)
    if m:
        return m.group(1).upper().replace("A", "a").replace("B", "b")
    m = re.search(r"\b(" + series + r"\d+(?:[ab])?)\b", joined)
    if m:
        return m.group(1)
    return None


def formalization_for_law(law_id: str) -> dict[str, Any]:
    base_id = "G1" if law_id == "G1b" else law_id
    if base_id.startswith("F"):
        d = F_DISC.get(base_id)
        if not d:
            return no_match_formalization("No F-law disclosure row exists for this source row.")
        # The disclosure table distinguishes the 14 modules actually supplied
        # in the imported Foundations-IV scaffold from the 38 modules reported
        # by the paper but absent from the supplied archive.  Keep those two
        # evidence grades separate: a paper-reported declaration is useful
        # provenance, but it is not a locally imported declaration.
        present = d.get("local_import_status") == "IMPORTED_SUBSET_MODULE"
        local_decls = [x.strip() for x in d.get("local_key_declarations", "").split(";") if x.strip()]
        paper_reported_decls = [d["paper_lean_declaration"]] if d.get("paper_lean_declaration") else []
        trust = TRUST_BASE if base_id == "F13a" else []
        return {
            "status": "MATCHED_IMPORTED_LAW_DECLARATION" if present else "PAPER_DISCLOSED_ASSET_NOT_IMPORTED",
            "modules": [d["local_lean_module"]] if present and d.get("local_lean_module") else [],
            "declarations": local_decls if present else [],
            "paper_reported_declarations": paper_reported_decls,
            "source_files": [],
            "exact_hypothesis_match": True if present and d.get("paper_semantic_alignment") == "faithful" else None,
            "exact_conclusion_match": True if present and d.get("paper_semantic_alignment") == "faithful" else None,
            "statement_delta": [d.get("caveat", "")] if d.get("caveat") else [],
            "trust_base": trust,
            "elaboration_status": d.get("local_kernel_build", "NOT_RUN"),
            "lab_or_test_evidence": [],
            "caveats": [
                "Paper grade and source statement remain controlling; module presence is not a fresh kernel replay."
                if present else
                "The paper reports a Lean declaration, but no corresponding source module is present in the supplied scaffold; no local formal match is claimed."
            ],
        }
    if base_id.startswith("E"):
        d, t = E_DISC.get(base_id), E_TRACE.get(base_id)
        if not d:
            return no_match_formalization("No E-law disclosure row exists for this source row.")
        decls = [x.strip() for x in d.get("paper_principal_declarations", "").split(";") if x.strip()]
        evidence = []
        modules = []
        files = []
        if t:
            modules = [t["lean_module"]] if t.get("lean_module") else []
            files = [t["lean_file"]] if t.get("lean_file") else []
            for k in ("gate_note", "example_note", "sweep_predictions", "sweep_results", "pytest_file", "standalone_sweep"):
                if t.get(k): evidence.extend([x for x in t[k].split(";") if x])
        return {
            "status": "MATCHED_IMPORTED_LAW_DECLARATION",
            "modules": modules,
            "declarations": decls,
            "source_files": files,
            "exact_hypothesis_match": None,
            "exact_conclusion_match": None,
            "statement_delta": [d.get("caveat", ""), d.get("paper_certified_or_open_boundary", "")],
            "trust_base": ["No authored Foundations V axiom/opaque declaration; transitive imported trust is governed by the cumulative scaffold ledger."],
            "elaboration_status": d.get("local_kernel_build", "NOT_RUN"),
            "lab_or_test_evidence": evidence,
            "caveats": ["Conditional host-supplied certificates and the paper's theorem/schema grade must travel with reuse."],
        }
    if base_id.startswith("G"):
        d, t = G_DISC.get(base_id), G_TRACE.get(base_id)
        if not d:
            return no_match_formalization("No G-law disclosure row exists for this source row.")
        modules = [d["local_lean_module"]] if d.get("local_lean_module") else []
        files = [d["local_lean_file"]] if d.get("local_lean_file") else []
        decls = [r["fully_qualified_name"] for r in LEAN_THEOREMS if r["module"] in modules]
        evidence = []
        for k in ("gate_note", "example_note", "lab_packages", "test_files", "recorded_results"):
            if d.get(k): evidence.extend([x for x in d[k].split(";") if x])
        return {
            "status": "MATCHED_IMPORTED_LAW_DECLARATION",
            "modules": modules,
            "declarations": decls,
            "source_files": files,
            "exact_hypothesis_match": None,
            "exact_conclusion_match": None,
            "statement_delta": [d.get("caveat", ""), f"Paper grade: {d.get('paper_grade','')}"],
            "trust_base": ["No G-law axiom/opaque declaration identified; transitive imported trust is governed by the scaffold ledger."],
            "elaboration_status": d.get("local_kernel_build", "NOT_RUN"),
            "lab_or_test_evidence": evidence,
            "caveats": ["Tests and finite labs do not discharge the general law hypotheses."],
        }
    return no_match_formalization("Unrecognized law series.")


def no_match_formalization(reason: str, disclosure: str = "") -> dict[str, Any]:
    return {
        "status": "NO_MATCH",
        "modules": [], "declarations": [], "source_files": [],
        "exact_hypothesis_match": None, "exact_conclusion_match": None,
        "statement_delta": [reason], "trust_base": [],
        "elaboration_status": "NOT_APPLICABLE_OR_NOT_RUN",
        "lab_or_test_evidence": [],
        "caveats": ([disclosure] if disclosure else []),
    }


NO_GO_PRIOR_SCAFFOLD = {
    "NG_ARROW_DPI": {
        "status": "NO_MATCH",
        "modules": [],
        "declarations": [],
        "source_files": [],
        "statement_delta": [
            "No imported declaration was identified for the no-go paper's deterministic data-processing inequality for arrow audits."
        ],
        "caveats": ["The no-go source theorem remains authoritative; absence of a local correspondence is not evidence of falsehood."],
    },
    "NG_PROTOCOL_TRAP": {
        "status": "NO_MATCH",
        "modules": [],
        "declarations": [],
        "source_files": [],
        "statement_delta": [
            "No imported declaration was identified for the protocol/schedule trap theorem."
        ],
        "caveats": ["Finite examples and audit tests do not replace the source theorem's exact hypotheses."],
    },
    "NG_FORCE_FOREST": {
        "status": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "modules": ["SixBirdsIII.GraphCohomology"],
        "declarations": ["SixBirdsIII.forest_no_drive"],
        "source_files": ["formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/GraphCohomology.lean"],
        "statement_delta": [
            "The imported theorem proves the abstract forest/no-cycle drive core. It is not certified identical to the no-go paper's potential-representation statement on its declared force carrier."
        ],
        "caveats": ["Treat this as a reusable core lemma only after an explicit carrier and sign-convention adapter."],
    },
    "NG_FORCE_NULL": {
        "status": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "modules": ["SixBirdsIII.GraphCohomology"],
        "declarations": ["SixBirdsIII.exact_form_null_drive"],
        "source_files": ["formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/GraphCohomology.lean"],
        "statement_delta": [
            "The imported theorem proves null drive for an exact graph 1-form. Exact equality with the no-go paper's force-normalization statement still requires a typed adapter."
        ],
        "caveats": ["Do not infer the full no-go theorem from the declaration name alone."],
    },
    "NG_MACRO_CLOSURE_DEFICIT": {
        "status": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "modules": ["SixBirdsIII.FiniteProbability"],
        "declarations": ["SixBirdsIII.finite_markov_closure_deficit"],
        "source_files": ["formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/FiniteProbability.lean"],
        "statement_delta": [
            "The imported theorem provides the abstract finite closure-deficit/minimization core. The no-go paper's full Markov/KL construction and admissible macroscopic class are not certified identical."
        ],
        "caveats": ["Reuse requires an explicit identification of probability objects, conditional-information convention, and minimization domain."],
    },
    "NG_OBJECT_CONTRACTIVE": {
        "status": "PAPER_DISCLOSED_ASSET_NOT_IMPORTED",
        "modules": [],
        "declarations": [],
        "source_files": [],
        "statement_delta": [
            "The source paper discloses a narrower contraction/uniqueness supplement, but no dedicated local declaration for the complete no-go theorem is present in the imported scaffold."
        ],
        "caveats": ["Contraction uniqueness is not by itself the complete object-formation no-go statement."],
    },
    "NG_LADDER_IDEM": {
        "status": "MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION",
        "modules": ["SixBirdsIII.Completion"],
        "declarations": ["SixBirdsIII.idempotent_saturation"],
        "source_files": ["formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/Completion.lean"],
        "statement_delta": [
            "The imported theorem gives the pointwise idempotent-saturation core. The no-go paper's exact ladder vocabulary and scope remain source-controlled."
        ],
        "caveats": ["This correspondence does not mechanize the entire no-go chapter or its escape-route analysis."],
    },
    "NG_LADDER_BOUNDED_INTERFACE": {
        "status": "PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT",
        "modules": ["SixBirdsIII.Definability"],
        "declarations": ["SixBirdsIII.fixed_interface_definability_bound"],
        "source_files": ["formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/Definability.lean"],
        "statement_delta": [
            "The imported theorem gives a fixed-interface definability bound. It does not, without further finite-cardinality and iteration lemmas, establish the no-go paper's full bounded-interface ladder theorem."
        ],
        "caveats": ["An adapter must expose the exact interface family, cardinality bound, and strict-chain notion."],
    },
}


def formalization_for_nogo(no_go_id: str) -> dict[str, Any]:
    row = NO_GO_PRIOR_SCAFFOLD.get(no_go_id)
    if not row:
        return no_match_formalization(f"No correspondence row exists for {no_go_id}.")
    return {
        "status": row["status"],
        "modules": list(row.get("modules", [])),
        "declarations": list(row.get("declarations", [])),
        "source_files": list(row.get("source_files", [])),
        "exact_hypothesis_match": False if row["status"] != "NO_MATCH" else None,
        "exact_conclusion_match": False if row["status"] != "NO_MATCH" else None,
        "statement_delta": list(row.get("statement_delta", [])),
        "trust_base": [],
        "elaboration_status": "STATIC_INDEX_AND_IMPORT_RESOLUTION_ONLY; LOCAL_LEAN_KERNEL_NOT_RUN" if row.get("modules") else "NOT_APPLICABLE_OR_NOT_RUN",
        "lab_or_test_evidence": [],
        "caveats": list(row.get("caveats", [])),
    }


def plausible_formalization(pid: str, title: str, statement: str, claim_type: str) -> dict[str, Any]:
    prefixes = MODULE_PREFIXES.get(pid, ())
    disclosure = DISCLOSURES.get(pid, {}).get("formalization_status", "")
    if not prefixes:
        status = "PAPER_DISCLOSED_ASSET_NOT_IMPORTED" if disclosure and "NO_DEDICATED" not in disclosure else "NO_MATCH"
        f = no_match_formalization("No imported module family was assigned to this paper at Step-2 intake.", disclosure)
        f["status"] = status
        return f
    candidates = [r for r in LEAN_DECLS if any(r["module"] == p.rstrip(".") or r["module"].startswith(p) for p in prefixes)]
    query = f"{title} {statement[:700]}"
    scored = []
    for r in candidates:
        name = r["fully_qualified_name"].replace("_", " ").replace(".", " ")
        score = lexical_similarity(query, name)
        if score >= 0.42:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1]["fully_qualified_name"]))
    if not scored:
        return no_match_formalization("Imported module family exists, but no plausible declaration-name match passed the conservative threshold.", disclosure)
    top = scored[:3]
    modules = sorted({r["module"] for _, r in top})
    decls = [r["fully_qualified_name"] for _, r in top]
    files = sorted({r["file"] for _, r in top})
    return {
        "status": "PLAUSIBLE_IMPORTED_MATCH_REQUIRES_STATEMENT_REVIEW",
        "modules": modules,
        "declarations": decls,
        "source_files": files,
        "exact_hypothesis_match": None,
        "exact_conclusion_match": None,
        "statement_delta": [
            "Lexical/declaration-name alignment only; exact parameters, hypotheses, and conclusions were not certified equivalent.",
            "Candidate scores: " + "; ".join(f"{r['fully_qualified_name']}={s:.3f}" for s, r in top),
        ],
        "trust_base": TRUST_BASE if any("HiddennessNormalForm" in r["module"] for _, r in top) else [],
        "elaboration_status": "STATIC_INDEX_AND_IMPORT_RESOLUTION_ONLY; LOCAL_LEAN_KERNEL_NOT_RUN",
        "lab_or_test_evidence": [],
        "caveats": [disclosure] if disclosure else [],
    }


def make_claim_base(pid: str, cat: dict[str, str], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_paper": pid,
        "source_title": cat["title"],
        "reading_order": int(cat["reading_order"]),
        "cluster": cat["cluster"],
        "source_root": f"source/{meta['source_path']}",
        "source_root_sha256": meta["root_sha256"],
        "source_tree_sha256": meta["tree_sha256"],
        "source_completeness": "BLOCKED_MISSING_INCLUDED_FILES" if pid == "P039" else "AVAILABLE_SUPPLIED_SOURCE_TREE",
        "vii_links": PAPER_GROUPS.get(pid, []),
    }


def named_section_surfaces(raw: str, macros: dict[str, str]) -> list[dict[str, Any]]:
    """Extract explicitly named definition/schema/result/boundary sections.

    Many applied papers state their theorem schemas as titled subsections rather
    than theorem environments.  This pass records those named surfaces without
    pretending that every ordinary section is itself a theorem.
    """
    pat = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\s*\{")
    heads = []
    for m in pat.finditer(raw):
        # Balanced titles are shallow in the supplied corpus; use common helper behavior indirectly.
        depth = 0; i = raw.find("{", m.start()); j = i; buf=[]
        while j < len(raw):
            ch=raw[j]; esc=j>0 and raw[j-1]=="\\"
            if ch=="{" and not esc:
                depth += 1
                if depth>1: buf.append(ch)
            elif ch=="}" and not esc:
                depth -= 1
                if depth==0: break
                buf.append(ch)
            else: buf.append(ch)
            j += 1
        if depth != 0: continue
        tail = raw[j+1:j+240]
        lm = re.search(r"\\label\{([^{}]+)\}", tail)
        heads.append({"kind":m.group(1), "start":m.start(), "body_start":j+1, "title_tex":"".join(buf), "label":lm.group(1) if lm else ""})
    out=[]
    for idx,h in enumerate(heads):
        end=heads[idx+1]["start"] if idx+1<len(heads) else len(raw)
        body=raw[h["body_start"]:end]
        # Remove leading label and retain only the first two substantive paragraphs.
        body=re.sub(r"^\s*\\label\{[^{}]+\}\s*", "", body)
        paras=[x.strip() for x in re.split(r"\n\s*\n+", body) if x.strip()]
        body_tex="\n\n".join(paras[:2])
        title=tex_to_plain(h["title_tex"], macros)
        plain=tex_to_plain(body_tex, macros)
        # Heading/label semantics control the classification.  Body keywords are
        # used only when the opening sentence explicitly announces a schema or
        # result.  This avoids turning ordinary sections that merely discuss
        # ``closure``, ``status``, or ``construction`` into theorem records.
        head_marker=(title+" "+h["label"]).lower()
        lead=plain[:500].lower().strip()
        ctype=None; grade=None
        schema_head = bool(re.search(r"\bschema\b", head_marker))
        schema_lead = bool(re.match(r"^(?:the )?(?:first|second|third|fourth|fifth|sixth|seventh|next|following) schema\b", lead))
        explicit_result_head = bool(re.search(
            r"\b(?:theorem|lemma|proposition|corollary|principal result|main result|headline result|"
            r"result(?:s)?|verdict|decision logic|gate|criterion|certificate|prediction|finding|"
            r"no[- ]?go|obstruction theorem|classification theorem|equivalence theorem|comparison theorem|"
            r"normal form|acceptance theorem|admissibility theorem|exactification theorem|realization theorem|"
            r"main claim|principal claim|final claim)\b", head_marker))
        explicit_result_lead = bool(re.match(
            r"^(?:we (?:prove|show|establish|derive|construct|certify)|this (?:theorem|proposition|lemma|result)|"
            r"the (?:main|principal|central|headline|first|second|third|fourth|fifth|sixth|seventh) "
            r"(?:result|theorem|claim|schema)\b)", lead))
        if schema_head or schema_lead:
            ctype,grade="schema","SCHEMA"
        elif re.search(r"\bdefinitions?\b", title.lower()):
            ctype,grade="prose_definition","PROSE_DEFINITION_SECTION"
        elif re.search(r"\b(?:nonclaims?|claim boundary|limitations?|scope boundary|bounded scope|negative scope)\b", head_marker):
            ctype,grade="scope_boundary","SCOPE_OR_LIMITATION_RECORD"
        elif re.search(r"\b(?:open problems?|open questions?|future work|outlook|deferred obligations?)\b", head_marker):
            ctype,grade="open_problem","OPEN_PROBLEM_OR_DEFERRED_WORK"
        elif explicit_result_head or explicit_result_lead:
            ctype,grade="result_summary","NAMED_RESULT_OR_GATE_SURFACE"
        if ctype and len(plain.split())>=8:
            out.append({**h,"end":end,"body_tex":body_tex,"title_plain":title,"plain":plain,"claim_type":ctype,"claim_grade":grade})
    return out


PROSE_FOCUS_PATTERNS = {
    "open_problem": re.compile(r"\b(?:open problem|open question|future work|remains open|left for future|we defer|is deferred|outlook)\b", re.I),
    "nonclaim": re.compile(
        r"\b(?:non[- ]?claim|we do not claim|does not claim|do not assert|does not assert|"
        r"does not prove|not claimed here|not proven here|not proved here|"
        r"(?:is|are|was|were)\s+not\s+(?:claimed|proven|proved|established|derived|refuted)(?:\s+here)?|"
        r"outside (?:the )?scope)\b",
        re.I,
    ),
    "scope_boundary": re.compile(
        r"\b(?:limitation|scope boundary|bounded result|within the declared scope|"
        r"only under the declared|conditional on|restricted to|limited to|we restrict|we limit)\b",
        re.I,
    ),
}

# Abstracts are unusually dense and frequently mention nonclaim *registers*
# or *checks* without themselves stating a nonclaim.  Use a stricter detector
# for abstract components so navigation records capture actual boundaries,
# not merely vocabulary about boundary-management machinery.
ABSTRACT_BOUNDARY_PATTERNS = {
    "nonclaim": re.compile(
        r"\b(?:"
        r"(?:we|this paper|the paper|the account|foundations?\s+[ivx]+)\s+"
        r"(?:do(?:es)?\s+not|doesn't)\s+(?:claim|assert|derive|prove|establish)|"
        r"(?:we|this paper|the paper)\s+make(?:s)?\s+no\s+[^.!?;]{0,220}?\bclaims?\b|"
        r"(?:we|this paper|the paper)\s+claim(?:s)?\s+no\s+|"
        r"claim(?:s)?\s+none|"
        r"not\s+(?:re-?)?(?:proven|proved|established|derived|refuted)(?:\s+here)?|"
        r"(?:is|are|was|were)\s+not\s+(?:claimed|proven|proved|established|derived|refuted)(?:\s+here)?|"
        r"(?:do|does)\s+not\s+(?:claim|assert|derive|prove|establish)|"
        r"not\s+(?:an?\s+)?[^.!?;]{0,180}?\b(?:claim|theorem|proof)\b|"
        r"no\s+[^.!?;]{0,180}?\bclaim(?:s)?\b"
        r")",
        re.I,
    ),
    "scope_boundary": re.compile(
        r"\b(?:"
        r"scope\s+(?:is|are)\s+(?:deliberately|intentionally|explicitly)?\s*(?:limited|narrow|bounded)|"
        r"claims?\s+(?:is|are)\s+(?:deliberately\s+)?(?:scoped|limited|narrow|narrower)|"
        r"within\s+(?:the\s+)?(?:declared\s+|covered\s+|stated\s+|present\s+)?scope|"
        r"outside\s+(?:the\s+)?(?:declared\s+|covered\s+|stated\s+|present\s+)?scope|"
        r"out\s+of\s+scope|restricted\s+to|limited\s+to|"
        r"two\s+scope\s+disclosures\s+apply|"
        r"used\s+only\s+[^.!?;]{0,180}?not\s+as\s+proof\s+support"
        r")",
        re.I,
    ),
    "open_problem": re.compile(
        r"\b(?:remains?\s+open|future\s+work|left\s+for\s+future|we\s+defer|is\s+deferred)\b",
        re.I,
    ),
}


def focus_prose_surface(plain: str, kind: str, pattern: re.Pattern[str] | None = None) -> str:
    """Return the exact claim-bearing sentences while retaining full TeX separately.

    Paragraphs in the corpus often combine a theorem summary, a citation note,
    and a final nonclaim/open sentence.  Recording the whole paragraph as the
    nonclaim would misstate its semantic center.  The full paragraph remains in
    ``source_wording_tex`` and ``source_wording_digest``; this function narrows
    only the normalized navigation statement.
    """
    text = re.sub(r"\s+", " ", plain).strip()
    if pattern is not None or kind in PROSE_FOCUS_PATTERNS:
        pat = pattern or PROSE_FOCUS_PATTERNS[kind]
        sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\[])|\s*;\s*", text) if x.strip()]
        hits = [x for x in sentences if pat.search(x)]
        if hits:
            return " ".join(hits[:12])
    if kind == "result_summary":
        sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\[])", text) if x.strip()]
        return " ".join(sentences[:6]) if sentences else text
    return text


def extract_abstract_surface(raw: str, macros: dict[str, str], metadata_abstract: str) -> dict[str, Any] | None:
    """Return one source-located abstract surface for either common TeX form.

    Most papers use an ``abstract`` environment, but at least one supplied
    source uses ``\\section*{Abstract}``.  Step 2 needs one composite thesis for
    every paper and must not silently lose abstract-only nonclaims, limitations,
    or open obligations.  The returned container range is also used to prevent
    the paragraph lane from double-counting abstract prose.
    """
    env = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, flags=re.S | re.I)
    if env:
        body_start, body_end = env.start(1), env.end(1)
        container_start, container_end = env.start(), env.end()
    else:
        heading = re.search(
            r"\\section\*?\s*\{\s*Abstract\s*\}(?:\s*\\label\{[^{}]+\})?",
            raw,
            flags=re.I,
        )
        if not heading:
            # Metadata-only fallback is retained for malformed or generated
            # source packages.  It remains source-marked as a one-line surface.
            plain = metadata_abstract.strip()
            if not plain:
                return None
            return {
                "container_start": 0,
                "container_end": 0,
                "body_start": 0,
                "body_end": 0,
                "abstract_tex": plain,
                "abstract_plain": plain,
                "source_mode": "METADATA_ONLY_FALLBACK",
            }
        next_section = re.search(r"\\section\*?\s*\{", raw[heading.end():], flags=re.I)
        container_start = heading.start()
        container_end = heading.end() + next_section.start() if next_section else len(raw)
        body_start, body_end = heading.end(), container_end

        # Do not absorb a trailing keyword line into the mathematical abstract.
        body_chunk = raw[body_start:body_end]
        keyword = re.search(
            r"(?:\\noindent\s*)?\\(?:textbf|textsc|emph)\s*\{\s*keywords?\s*:?\s*\}",
            body_chunk,
            flags=re.I,
        )
        if keyword:
            body_end = body_start + keyword.start()

    abstract_tex = raw[body_start:body_end].strip()
    abstract_plain = metadata_abstract.strip() or tex_to_plain(abstract_tex, macros).strip()
    if not abstract_plain:
        return None
    return {
        "container_start": container_start,
        "container_end": container_end,
        "body_start": body_start,
        "body_end": body_end,
        "abstract_tex": abstract_tex,
        "abstract_plain": abstract_plain,
        "source_mode": "TEX_SOURCE",
    }


def build_paper_claims(cat: dict[str, str]) -> list[dict[str, Any]]:
    pid = cat["paper_id"]
    meta = json_load(METADATA / f"{pid}.json")
    expanded_path = find_expanded_path(meta)
    raw = expanded_path.read_text(encoding="utf-8", errors="replace")
    macros = collect_simple_macros(raw)
    doc_start = raw.find(r"\begin{document}")
    if doc_start < 0: doc_start = 0
    abstract_surface = extract_abstract_surface(raw, macros, meta.get("abstract", ""))
    abs_start = abstract_surface["container_start"] if abstract_surface else -1
    abs_end = abstract_surface["container_end"] if abstract_surface else -1
    bib_start_candidates = [x for x in (raw.find(r"\bibliography", doc_start), raw.find(r"\begin{thebibliography}", doc_start)) if x >= 0]
    body_end = min(bib_start_candidates) if bib_start_candidates else len(raw)
    dep = DEPS[pid]
    line_map = source_line_map(raw, dep["root"], dep["files"])
    envs = extract_environments(raw, dep["root"], dep["files"])
    claims: list[dict[str, Any]] = []
    base = make_claim_base(pid, cat, meta)

    # Composite abstract thesis.  It is a navigation claim, not a replacement
    # for component theorem records.  Preserve the exact supplied TeX body as
    # well as the plain metadata view so even this composite lane is auditable.
    if abstract_surface:
        abstract = abstract_surface["abstract_plain"]
        abstract_tex = abstract_surface["abstract_tex"]
        exp_start = raw.count("\n", 0, abstract_surface["body_start"]) + 1
        exp_end = raw.count("\n", 0, abstract_surface["body_end"]) + 1
        idx0 = min(max(exp_start - 1, 0), len(line_map)-1) if line_map else 0
        idx1 = min(max(exp_end - 1, 0), len(line_map)-1) if line_map else 0
        sp, sl = line_map[idx0] if line_map else (dep["root"], exp_start)
        ep, el = line_map[idx1] if line_map else (sp, sl + max(0, exp_end-exp_start))
        if ep != sp:
            el = sl + max(0, exp_end-exp_start)
        claim = dict(base)
        claim.update({
            "source_location": format_location(sp, sl, el, expanded_path.name, exp_start, exp_end),
            "source_path": sp, "source_start_line": sl, "source_end_line": el,
            "expanded_path": f"derived/expanded/{expanded_path.name}",
            "expanded_start_line": exp_start, "expanded_end_line": exp_end,
            "source_labels": [], "source_wording_tex": abstract_tex,
            "expanded_source_wording_tex": expand_simple_macros(abstract_tex, macros),
            "source_wording_digest": abstract,
            "normalized_claim": abstract,
            "claim_type": "paper_thesis", "claim_grade": "PAPER_STATED_COMPOSITE_RESULT",
            "typed_objects": typed_objects(abstract), "hypotheses": [{"text": "Composite abstract; component claim records govern exact hypotheses.", "extraction": "COMPONENT_CLAIMS_CONTROL"}],
            "conclusion": abstract, "conclusion_extraction": "ABSTRACT_COMPOSITE",
            "proof_status": "MIXED_SEE_COMPONENT_CLAIMS",
            "dependencies": [], "imported_laws": imported_laws(abstract, pid),
            "bridge_requirements": ["Do not reuse the abstract as an exact theorem statement; cite component records."],
            "escape_routes": [], "nonclaims": [], "nearest_countermodel": None,
            "review_status": "SOURCE_EXTRACTED_COMPOSITE",
        })
        claim["formalization"] = plausible_formalization(pid, cat["title"], abstract, "paper_thesis")
        claims.append(claim)

        # Abstract-only boundaries are first-class records, not hidden inside
        # the composite thesis.  This matters for papers whose strongest scope
        # qualification or open obligation appears nowhere else in the source.
        abstract_grade = {
            "open_problem": "OPEN_PROBLEM_OR_DEFERRED_WORK",
            "nonclaim": "EXPLICIT_NONCLAIM",
            "scope_boundary": "SCOPE_OR_LIMITATION_RECORD",
        }
        for kind in ("nonclaim", "scope_boundary", "open_problem"):
            abstract_pattern = ABSTRACT_BOUNDARY_PATTERNS[kind]
            if not abstract_pattern.search(abstract):
                continue
            focused = focus_prose_surface(abstract, kind, abstract_pattern)
            hyps, conclusion, cstatus = split_hypotheses_conclusion(focused, kind)
            component = dict(base)
            component.update({
                "source_location": format_location(sp, sl, el, expanded_path.name, exp_start, exp_end),
                "source_path": sp, "source_start_line": sl, "source_end_line": el,
                "expanded_path": f"derived/expanded/{expanded_path.name}",
                "expanded_start_line": exp_start, "expanded_end_line": exp_end,
                "source_labels": [], "source_title_tex": "Abstract",
                "source_wording_tex": abstract_tex,
                "expanded_source_wording_tex": expand_simple_macros(abstract_tex, macros),
                "source_wording_digest": abstract,
                "normalized_claim": focused,
                "claim_type": kind, "claim_grade": abstract_grade[kind],
                "typed_objects": typed_objects(focused), "hypotheses": hyps,
                "conclusion": conclusion, "conclusion_extraction": cstatus,
                "proof_status": "ABSTRACT_STATUS_BOUNDARY",
                "dependencies": cite_dependencies(abstract_tex, pid),
                "imported_laws": imported_laws(abstract + " " + abstract_tex, pid),
                "bridge_requirements": [
                    "Abstract component; exact body records control any stronger reuse when available."
                ],
                "escape_routes": [], "nonclaims": [], "nearest_countermodel": None,
                "review_status": "SOURCE_EXTRACTED_EXPLICIT_PROSE_SURFACE",
            })
            component["formalization"] = plausible_formalization(pid, "Abstract", focused, kind)
            claims.append(component)

    # Formal environments.
    occupied: list[tuple[int, int]] = []
    for env in envs:
        occupied.append((env.start_offset, env.end_offset))
        title_plain = tex_to_plain(env.title_tex, macros)
        body_plain = tex_to_plain(env.body_tex, macros)
        if not body_plain:
            body_plain = "[TeX-only statement; consult source_wording_tex.]"
        ctype, grade = claim_grade_for(env.env, title_plain, body_plain)
        hyps, conclusion, cstatus = split_hypotheses_conclusion(body_plain, env.env)
        law_id = law_id_from_claim(pid, title_plain, body_plain, env.labels)
        claim = dict(base)
        claim.update({
            "source_location": format_location(env.source_path, env.source_start_line, env.source_end_line, expanded_path.name, env.expanded_start_line, env.expanded_end_line),
            "source_path": env.source_path,
            "source_start_line": env.source_start_line,
            "source_end_line": env.source_end_line,
            "expanded_path": f"derived/expanded/{expanded_path.name}",
            "expanded_start_line": env.expanded_start_line,
            "expanded_end_line": env.expanded_end_line,
            "source_labels": env.labels,
            "source_title_tex": env.title_tex,
            "source_wording_tex": env.body_tex,
            "expanded_source_wording_tex": expand_simple_macros(env.body_tex, macros),
            "source_wording_digest": body_plain,
            "normalized_claim": (f"{title_plain}: {body_plain}" if title_plain else body_plain),
            "claim_type": ctype,
            "claim_grade": grade,
            "typed_objects": typed_objects(body_plain),
            "hypotheses": hyps,
            "conclusion": conclusion,
            "conclusion_extraction": cstatus,
            "proof_status": ("PROOF_PRESENT_IN_SOURCE" if env.proof_present and env.env in {"theorem","lemma","proposition","corollary","Theorem","Lemma","theorem*"}
                             else "STATEMENT_PRESENT_NO_SEPARATE_PROOF_DETECTED" if env.env in {"theorem","lemma","proposition","corollary","Theorem","Lemma","theorem*"}
                             else "NOT_APPLICABLE_DEFINITION" if env.env in {"definition","Definition","construction","convention"}
                             else "SOURCE_ARGUMENT_OR_STATUS_LANE"),
            "dependencies": cite_dependencies(env.body_tex, pid),
            "imported_laws": imported_laws(body_plain + " " + env.body_tex, pid),
            "bridge_requirements": [],
            "escape_routes": [],
            "nonclaims": [],
            "nearest_countermodel": None,
            "law_id": law_id,
            "review_status": "SOURCE_EXTRACTED_FORMAL_SURFACE",
        })
        claim["formalization"] = formalization_for_law(law_id) if law_id else plausible_formalization(pid, title_plain, body_plain, ctype)
        claims.append(claim)

    # Named section surfaces used as theorem/schema/gate lanes in papers that do
    # not use formal theorem environments.
    existing_sigs = {re.sub(r"\W+", " ", c["source_wording_digest"].lower()).strip() for c in claims}
    for sec in named_section_surfaces(raw, macros):
        if sec["start"] < doc_start or sec["start"] >= body_end:
            continue
        sig = re.sub(r"\W+", " ", sec["plain"].lower()).strip()
        if not sig or sig in existing_sigs:
            continue
        existing_sigs.add(sig)
        exp_line = raw.count("\n", 0, sec["start"]) + 1
        end_line = raw.count("\n", 0, sec["end"]) + 1
        idx = min(max(exp_line-1,0),len(line_map)-1) if line_map else 0
        idx2 = min(max(end_line-1,0),len(line_map)-1) if line_map else idx
        sp,sl=line_map[idx] if line_map else (dep["root"],exp_line)
        sp2,sl2=line_map[idx2] if line_map else (sp,sl+end_line-exp_line)
        if sp2!=sp: sl2=sl+end_line-exp_line
        hyps, conclusion, cstatus = split_hypotheses_conclusion(sec["plain"], sec["claim_type"])
        claim=dict(base)
        claim.update({
            "source_location": format_location(sp,sl,sl2,expanded_path.name,exp_line,end_line),
            "source_path":sp,"source_start_line":sl,"source_end_line":sl2,
            "expanded_path":f"derived/expanded/{expanded_path.name}","expanded_start_line":exp_line,"expanded_end_line":end_line,
            "source_labels":[sec["label"]] if sec["label"] else [],"source_title_tex":sec["title_tex"],"source_wording_tex":sec["body_tex"],
            "expanded_source_wording_tex":expand_simple_macros(sec["body_tex"], macros),
            "source_wording_digest":sec["plain"],"normalized_claim":f"{sec['title_plain']}: {sec['plain']}",
            "claim_type":sec["claim_type"],"claim_grade":sec["claim_grade"],"typed_objects":typed_objects(sec["plain"]),
            "hypotheses":hyps,"conclusion":conclusion,"conclusion_extraction":cstatus,"proof_status":"NAMED_SOURCE_SECTION_ARGUMENT",
            "dependencies":cite_dependencies(sec["body_tex"],pid),"imported_laws":imported_laws(sec["plain"]+" "+sec["body_tex"],pid),
            "bridge_requirements":[],"escape_routes":[],"nonclaims":[],"nearest_countermodel":None,
            "review_status":"SOURCE_EXTRACTED_NAMED_SECTION_SURFACE",
        })
        claim["formalization"]=plausible_formalization(pid,sec["title_plain"],sec["plain"],sec["claim_type"])
        claims.append(claim)

    # Explicit prose definitions, result summaries, nonclaims, scope limits and
    # open problems outside formal environments.
    seen_plain = {re.sub(r"\W+", " ", c["source_wording_digest"].lower()).strip() for c in claims}
    for start, end, exp_line, para_tex in paragraph_spans(raw):
        if start < doc_start or start >= body_end:
            continue
        if abs_start >= 0 and abs_start <= start < abs_end:
            continue
        if any(a <= start < b for a, b in occupied):
            continue
        plain = tex_to_plain(para_tex, macros)
        kind = classify_prose_paragraph(plain)
        if not kind or len(plain) > 5000:
            continue
        sig = re.sub(r"\W+", " ", plain.lower()).strip()
        if not sig or sig in seen_plain:
            continue
        # Ignore bibliography and boilerplate.
        if re.search(r"\b(?:copyright|automorph inc|keywords|references)\b", plain, flags=re.I) and len(plain.split()) < 80:
            continue
        seen_plain.add(sig)
        idx = min(max(exp_line - 1, 0), len(line_map)-1) if line_map else 0
        sp, sl = line_map[idx] if line_map else (dep["root"], exp_line)
        end_line = exp_line + para_tex.count("\n")
        idx2 = min(max(end_line - 1, 0), len(line_map)-1) if line_map else idx
        sp2, sl2 = line_map[idx2] if line_map else (sp, sl + para_tex.count("\n"))
        if sp2 != sp: sl2 = sl + para_tex.count("\n")
        grade_map = {
            "open_problem": "OPEN_PROBLEM_OR_DEFERRED_WORK",
            "nonclaim": "EXPLICIT_NONCLAIM",
            "scope_boundary": "SCOPE_OR_LIMITATION_RECORD",
            "prose_definition": "PROSE_DEFINITION",
            "result_summary": "PAPER_STATED_RESULT_SUMMARY",
        }
        focused = focus_prose_surface(plain, kind)
        hyps, conclusion, cstatus = split_hypotheses_conclusion(focused, kind)
        claim = dict(base)
        claim.update({
            "source_location": format_location(sp, sl, sl2, expanded_path.name, exp_line, end_line),
            "source_path": sp, "source_start_line": sl, "source_end_line": sl2,
            "expanded_path": f"derived/expanded/{expanded_path.name}",
            "expanded_start_line": exp_line, "expanded_end_line": end_line,
            "source_labels": [], "source_title_tex": "", "source_wording_tex": para_tex,
            "expanded_source_wording_tex": expand_simple_macros(para_tex, macros),
            "source_wording_digest": plain, "normalized_claim": focused,
            "claim_type": kind, "claim_grade": grade_map[kind],
            "typed_objects": typed_objects(focused), "hypotheses": hyps,
            "conclusion": conclusion, "conclusion_extraction": cstatus,
            "proof_status": "PROSE_STATUS_OR_ARGUMENT_RECORD",
            "dependencies": cite_dependencies(para_tex, pid),
            "imported_laws": imported_laws(plain + " " + para_tex, pid),
            "bridge_requirements": [], "escape_routes": [], "nonclaims": [],
            "nearest_countermodel": None,
            "review_status": "SOURCE_EXTRACTED_EXPLICIT_PROSE_SURFACE",
        })
        claim["formalization"] = plausible_formalization(pid, "", focused, kind)
        claims.append(claim)

    # Stable source order: abstract first, then expanded location.
    claims.sort(key=lambda c: (0 if c["claim_type"] == "paper_thesis" else 1, c["expanded_start_line"], c["claim_type"], c["normalized_claim"][:80]))
    for i, claim in enumerate(claims, 1):
        claim["claim_id"] = f"{pid}-C{i:04d}"
    return claims


def augment_law_and_nogo_records(all_claims: list[dict[str, Any]]) -> None:
    """Guarantee every F/E/G/no-go registry row resolves to a claim ID."""
    by_pid = defaultdict(list)
    for c in all_claims:
        by_pid[c["source_paper"]].append(c)
    for series, pid, rows in (("F", "P028", F_ROWS), ("E", "P030", E_ROWS), ("G", "P029", G_ROWS)):
        for law_id, row in rows.items():
            matches = [c for c in by_pid[pid] if c.get("law_id") == law_id]
            if not matches:
                # source-line nearest formal claim
                line = int(row.get("source_line", "0") or 0)
                candidates = [c for c in by_pid[pid] if c["claim_type"] in {"theorem","lemma","proposition","corollary","schema"}]
                if candidates:
                    nearest = min(candidates, key=lambda c: abs(int(c["source_start_line"]) - line))
                    if abs(int(nearest["source_start_line"]) - line) <= 12:
                        nearest["law_id"] = law_id
                        nearest["formalization"] = formalization_for_law(law_id)
                        matches = [nearest]
            if matches:
                for c in matches:
                    c.setdefault("registry_links", []).append(f"registry/{series}_laws.csv:{law_id}")
    # No-go source rows.
    for ng_id, row in NG_ROWS.items():
        pid = row["source_paper"]
        line = int(row.get("source_line", "0") or 0)
        candidates = [c for c in by_pid[pid] if c["claim_type"] in {"theorem","lemma","proposition","corollary","result_summary"}]
        if candidates:
            nearest = min(candidates, key=lambda c: abs(int(c["source_start_line"]) - line))
            if abs(int(nearest["source_start_line"]) - line) <= 20:
                nearest["no_go_id"] = ng_id
                nearest["escape_routes"] = [row.get("escape_route", "")]
                nearest["nearest_countermodel"] = None
                nearest["formalization"] = formalization_for_nogo(ng_id)
                nearest.setdefault("registry_links", []).append(f"registry/no_go_theorems.csv:{ng_id}")


def attach_paper_nonclaims(all_claims: list[dict[str, Any]]) -> None:
    by_pid = defaultdict(list)
    for c in all_claims:
        by_pid[c["source_paper"]].append(c)
    for pid, claims in by_pid.items():
        nc = [c["claim_id"] for c in claims if c["claim_type"] in {"nonclaim", "scope_boundary"}]
        for c in claims:
            if c["claim_type"] not in {"nonclaim", "scope_boundary", "open_problem"}:
                c["nonclaims"] = nc[:40]


def assign_vii_links(all_claims: list[dict[str, Any]]) -> None:
    group_rows = read_csv(ROOT / "wishlists" / "convergence_groups.csv")
    group_text = defaultdict(str)
    for r in group_rows:
        group_text[r["convergence_group"]] += " " + r["group_title"] + " " + r["group_scope"] + " " + r["atomic_request"]
    for c in all_claims:
        candidates = PAPER_GROUPS.get(c["source_paper"], [])
        scored = []
        text = c["normalized_claim"][:2500]
        for g in candidates:
            s = lexical_similarity(text, group_text[g])
            scored.append((s, g))
        scored.sort(reverse=True)
        # Always retain paper-level recall groups; rank the top exact hooks.
        c["vii_links"] = [g for s, g in scored if s >= 0.10][:8] or candidates[:5]
        c["vii_link_scores"] = {g: round(s, 4) for s, g in scored[:8]}


def write_claim_products(all_claims: list[dict[str, Any]]) -> None:
    ensure_dirs(CLAIMS_DIR, BY_PAPER, DOSSIERS, REGISTRY, GENERATED)
    by_pid = defaultdict(list)
    for c in all_claims:
        by_pid[c["source_paper"]].append(c)
    # IDs may have changed after augmentation only in fields, not sequence.
    write_jsonl(REGISTRY / "claims.jsonl", all_claims)
    csv_fields = [
        "claim_id", "source_paper", "source_title", "claim_type", "claim_grade", "law_id", "no_go_id",
        "source_location", "source_labels", "source_wording_tex", "expanded_source_wording_tex", "normalized_claim", "hypotheses", "conclusion", "proof_status",
        "dependencies", "imported_laws", "formalization", "escape_routes", "nonclaims", "vii_links", "review_status",
    ]
    write_csv(REGISTRY / "claims.csv", all_claims, csv_fields)

    for pid in sorted(by_pid):
        write_jsonl(BY_PAPER / f"{pid}.jsonl", by_pid[pid])

    # Derived registries, keeping full claim IDs and source locations.
    defs = [c for c in all_claims if c["claim_type"] in {"definition","prose_definition","construction","convention"}]
    nonclaims = [c for c in all_claims if c["claim_type"] in {"nonclaim","scope_boundary"}]
    opens = [c for c in all_claims if c["claim_type"] == "open_problem"]
    examples = [c for c in all_claims if c["claim_type"] == "example"]
    theorem_claims = [c for c in all_claims if c["claim_type"] in {"theorem","theorem*","lemma","proposition","corollary","schema","conjecture","postulate","assumption","principle","result_summary"}]
    for name, rows in (("definitions", defs), ("theorem_claims", theorem_claims), ("nonclaims_withdrawals", nonclaims), ("open_problems", opens), ("examples_carriers", examples)):
        write_jsonl(REGISTRY / f"{name}.jsonl", rows)
        write_csv(REGISTRY / f"{name}.csv", rows, ["claim_id","source_paper","claim_type","claim_grade","source_location","normalized_claim","proof_status","formalization","vii_links"])

    # Formalization and provenance registries.
    form_rows = []
    prov_rows = []
    for c in all_claims:
        f = c["formalization"]
        form_rows.append({
            "claim_id": c["claim_id"], "source_paper": c["source_paper"], "claim_type": c["claim_type"],
            "formalization_status": f.get("status"), "modules": f.get("modules", []), "declarations": f.get("declarations", []),
            "exact_hypothesis_match": f.get("exact_hypothesis_match"), "exact_conclusion_match": f.get("exact_conclusion_match"),
            "statement_delta": f.get("statement_delta", []), "trust_base": f.get("trust_base", []),
            "elaboration_status": f.get("elaboration_status"), "lab_or_test_evidence": f.get("lab_or_test_evidence", []),
        })
        prov_rows.append({
            "claim_id": c["claim_id"], "source_paper": c["source_paper"], "source_path": c["source_path"],
            "source_start_line": c["source_start_line"], "source_end_line": c["source_end_line"],
            "source_root_sha256": c["source_root_sha256"], "source_tree_sha256": c["source_tree_sha256"],
            "source_completeness": c["source_completeness"], "expanded_path": c["expanded_path"],
            "expanded_start_line": c["expanded_start_line"], "expanded_end_line": c["expanded_end_line"],
        })
    write_csv(REGISTRY / "proof_artifact_lean_coverage.csv", form_rows, list(form_rows[0]))
    write_jsonl(REGISTRY / "proof_artifact_lean_coverage.jsonl", form_rows)
    write_csv(REGISTRY / "source_truth_provenance.csv", prov_rows, list(prov_rows[0]))

    write_dossiers(by_pid)



def write_no_go_prior_scaffold_correspondence(all_claims: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for claim in all_claims:
        nid = claim.get("no_go_id")
        if not nid:
            continue
        f = claim.get("formalization", {})
        rows.append({
            "no_go_id": nid,
            "source_claim": claim["claim_id"],
            "source_location": claim["source_location"],
            "correspondence_status": f.get("status", "NO_MATCH"),
            "prior_modules": f.get("modules", []),
            "prior_declarations": f.get("declarations", []),
            "source_files": f.get("source_files", []),
            "exact_hypothesis_match": f.get("exact_hypothesis_match"),
            "exact_conclusion_match": f.get("exact_conclusion_match"),
            "statement_delta": f.get("statement_delta", []),
            "machine_check_status": f.get("elaboration_status", ""),
            "caveats": f.get("caveats", []),
        })
    rows.sort(key=lambda r: r["no_go_id"])
    out = ROOT / "formalization" / "integration" / "no_go_prior_scaffold_correspondence.csv"
    write_csv(out, rows, list(rows[0]))
    write_jsonl(out.with_suffix(".jsonl"), rows)
    md = [
        "# No-go theorem / prior-scaffold correspondence", "",
        "The no-go paper does not supply a dedicated Lean library for all eight fronts. This table records only conservative correspondences to reusable earlier scaffold declarations. `MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION` and `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` are not claims that the complete no-go theorem has already been mechanized.", "",
        "| No-go | Source claim | Correspondence | Prior declarations | Exact match? |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        decls = ", ".join(f"`{x}`" for x in r["prior_declarations"]) or "none"
        exact = f"hyp={r['exact_hypothesis_match']}, concl={r['exact_conclusion_match']}"
        md.append(f"| `{r['no_go_id']}` | `{r['source_claim']}` | `{r['correspondence_status']}` | {decls} | {exact} |")
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")

def write_dossiers(by_pid: dict[str, list[dict[str, Any]]]) -> None:
    index_rows = []
    for cat in sorted(CATALOG, key=lambda r: int(r["reading_order"])):
        pid = cat["paper_id"]
        claims = by_pid[pid]
        counts = Counter(c["claim_type"] for c in claims)
        grades = Counter(c["claim_grade"] for c in claims)
        formal = Counter(c["formalization"]["status"] for c in claims)
        dependencies = sorted({d["paper_id"] for c in claims for d in c.get("dependencies", []) if d["paper_id"].startswith("P")})
        imported = sorted({x for c in claims for x in c.get("imported_laws", [])})
        nonclaims = [c for c in claims if c["claim_type"] in {"nonclaim","scope_boundary"}]
        opens = [c for c in claims if c["claim_type"] == "open_problem"]
        formal_claims = [c for c in claims if c["claim_type"] in {"theorem","theorem*","lemma","proposition","corollary","schema","conjecture","postulate","assumption","principle"}]
        definitions = [c for c in claims if c["claim_type"] in {"definition","prose_definition","construction","convention"}]
        text = [f"# {pid} — {cat['title']}", "", "## Dossier status", ""]
        if pid == "P039":
            text += [
                "- **Status:** `CLAIM_EXTRACTED_BLOCKED_FULL_TEXT`.",
                "- The supplied root contains the abstract and include commands, but 18 included TeX files and the bibliography are absent. The dossier records every supplied statement and does not reconstruct missing theorem text from the abstract.",
            ]
        else:
            text += ["- **Status:** `CLAIM_EXTRACTED`."]
        text += [
            f"- **Source root:** `{claims[0]['source_root']}`.",
            f"- **Source tree SHA-256:** `{claims[0]['source_tree_sha256']}`.",
            f"- **Cluster:** `{cat['cluster']}`; reading order {cat['reading_order']}.",
            f"- **Claim records:** {len(claims)}; formal theorem/schema surfaces: {len(formal_claims)}; definitions/constructions: {len(definitions)}; explicit nonclaim/scope records: {len(nonclaims)}; open/deferred records: {len(opens)}.",
            "- TeX source wording and exact locations are retained in `claims/by_paper/" + pid + ".jsonl`; the prose below is a navigation view.",
            "", "## Paper thesis", "",
            claims[0]["normalized_claim"] if claims else "No supplied thesis text.",
            "", "## Definitions and typed objects", "",
        ]
        for c in definitions[:30]:
            text.append(f"- **{c['claim_id']}** — {c['normalized_claim'][:700]}  ")
            text.append(f"  Source: `{c['source_location']}`.")
        if len(definitions) > 30:
            text.append(f"- {len(definitions)-30} additional definition records are in the machine registry.")
        text += ["", "## Principal theorem, schema, and negative-result surfaces", ""]
        ranked = sorted(formal_claims, key=lambda c: (0 if c.get("law_id") or c.get("no_go_id") else 1, c["expanded_start_line"]))
        for c in ranked[:45]:
            tag = f" [{c.get('law_id') or c.get('no_go_id')}]" if c.get("law_id") or c.get("no_go_id") else ""
            text.append(f"- **{c['claim_id']}**{tag} `{c['claim_grade']}` — {c['normalized_claim'][:900]}  ")
            text.append(f"  Source: `{c['source_location']}`; proof: `{c['proof_status']}`; formalization: `{c['formalization']['status']}`.")
        if len(ranked) > 45:
            text.append(f"- {len(ranked)-45} additional formal surfaces are retained in the per-paper JSONL.")
        text += ["", "## Nonclaims, limitations, and escape boundaries", ""]
        for c in nonclaims[:30]:
            text.append(f"- **{c['claim_id']}** — {c['normalized_claim'][:900]}  ")
            text.append(f"  Source: `{c['source_location']}`.")
        if not nonclaims:
            text.append("- No explicit nonclaim paragraph was isolated beyond the abstract/source surfaces; absence is not permission to strengthen the paper.")
        if len(nonclaims) > 30:
            text.append(f"- {len(nonclaims)-30} additional records are in `registry/nonclaims_withdrawals.*`.")
        text += ["", "## Open problems and deferred work", ""]
        for c in opens[:25]:
            text.append(f"- **{c['claim_id']}** — {c['normalized_claim'][:900]}  ")
            text.append(f"  Source: `{c['source_location']}`.")
        if not opens:
            text.append("- No explicit open-problem paragraph was mechanically isolated; consult the full claim file and conclusion sections before inferring closure.")
        text += [
            "", "## Dependencies, imported laws, and bridge obligations", "",
            "- **Resolved in-corpus paper dependencies:** " + (", ".join(dependencies) if dependencies else "none resolved at claim text level") + ".",
            "- **Lexical prior-law identifier candidates:** " + (", ".join(imported) if imported else "none detected outside the paper's own law series") + ". These are recall candidates only; `bridges/named_law_occurrence_audit.*` controls accepted imports.",
            "- Citation is not a bridge. Each paper-level invocation is adjudicated in `bridges/paper_invocation_bridges.*`; named law reuse is in `bridges/imported_law_bridges.*`.",
            "", "## Formalization and artifact posture", "",
            "- Claim-level formalization statuses: " + "; ".join(f"`{k}`={v}" for k,v in formal.most_common()) + ".",
            f"- Paper-side disclosure: `{DISCLOSURES.get(pid,{}).get('formalization_status','UNKNOWN')}`.",
            "- Exact law matches use the F/E/G disclosure and traceability ledgers. Other matches are explicitly lexical candidates or `NO_MATCH`; no local Lean kernel replay is claimed.",
            "", "## Foundations VII relevance", "",
            f"- Catalog hook: {cat['foundations_vii_hooks']}.",
            "- Candidate convergence groups: " + (", ".join(PAPER_GROUPS.get(pid, [])) if PAPER_GROUPS.get(pid) else "none assigned") + ".",
            "- This dossier supplies inherited definitions, proof grades, counterclaims, and bridge obligations only. It does not create a Foundations VII theorem.",
            "", "## Claim-type census", "",
            "| Claim type | Count |", "|---|---:|",
        ]
        for k,v in sorted(counts.items()): text.append(f"| `{k}` | {v} |")
        text += [
            "", "## Complete source-located claim index", "",
            "This index represents every canonical claim record for the paper. Full TeX wording, structured hypotheses, conclusion, proof status, dependencies, formalization metadata, nonclaims, and bridge requirements remain in the adjacent per-paper JSONL.",
            "", "| Claim | Type / grade | Source | Navigation text |", "|---|---|---|---|",
        ]
        for c in claims:
            nav = re.sub(r"\s+", " ", c["normalized_claim"]).strip().replace("|", "\\|")
            if len(nav) > 280:
                nav = nav[:279].rstrip() + "…"
            source = c["source_location"].replace("|", "\\|")
            text.append(f"| `{c['claim_id']}` | `{c['claim_type']}` / `{c['claim_grade']}` | `{source}` | {nav} |")
        path = DOSSIERS / f"{pid}.md"
        path.write_text("\n".join(text) + "\n", encoding="utf-8")
        dossier_json = {
            "paper_id": pid,
            "title": cat["title"],
            "status": "CLAIM_EXTRACTED_BLOCKED_FULL_TEXT" if pid == "P039" else "CLAIM_EXTRACTED",
            "source_root": claims[0]["source_root"],
            "source_root_sha256": claims[0]["source_root_sha256"],
            "source_tree_sha256": claims[0]["source_tree_sha256"],
            "source_completeness": claims[0]["source_completeness"],
            "cluster": cat["cluster"],
            "reading_order": int(cat["reading_order"]),
            "claim_count": len(claims),
            "claim_type_counts": dict(counts),
            "claim_grade_counts": dict(grades),
            "formalization_status_counts": dict(formal),
            "claim_ids": [c["claim_id"] for c in claims],
            "formal_claim_ids": [c["claim_id"] for c in formal_claims],
            "definition_claim_ids": [c["claim_id"] for c in definitions],
            "nonclaim_scope_ids": [c["claim_id"] for c in nonclaims],
            "open_problem_ids": [c["claim_id"] for c in opens],
            "source_law_ids": sorted({c.get("law_id") for c in claims if c.get("law_id")}),
            "source_no_go_ids": sorted({c.get("no_go_id") for c in claims if c.get("no_go_id")}),
            "resolved_dependency_papers": dependencies,
            "lexical_prior_law_candidates": imported,
            "foundations_vii_groups": PAPER_GROUPS.get(pid, []),
            "foundations_vii_hook": cat["foundations_vii_hooks"],
            "canonical_claim_file": f"claims/by_paper/{pid}.jsonl",
            "markdown_dossier": f"notes/dossiers/{pid}.md",
            "bridge_completion": {},
        }
        (DOSSIERS / f"{pid}.json").write_text(json.dumps(dossier_json, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        index_rows.append({
            "paper_id": pid, "title": cat["title"], "status": "CLAIM_EXTRACTED_BLOCKED_FULL_TEXT" if pid=="P039" else "CLAIM_EXTRACTED",
            "claim_count": len(claims), "formal_claim_count": len(formal_claims), "definition_count": len(definitions),
            "nonclaim_scope_count": len(nonclaims), "open_problem_count": len(opens),
            "dossier": f"notes/dossiers/{pid}.md", "claim_file": f"claims/by_paper/{pid}.jsonl",
        })
    write_csv(ROOT / "corpus" / "step2_dossier_index.csv", index_rows, list(index_rows[0]))
    md = ["# Step-2 dossier index", "", "| Paper | Status | Claims | Formal | Definitions | Nonclaims/scope | Open |", "|---|---|---:|---:|---:|---:|---:|"]
    for r in index_rows:
        md.append(f"| [{r['paper_id']}](../{r['dossier']}) | `{r['status']}` | {r['claim_count']} | {r['formal_claim_count']} | {r['definition_count']} | {r['nonclaim_scope_count']} | {r['open_problem_count']} |")
    (ROOT / "reports" / "STEP2_DOSSIER_INDEX.md").write_text("\n".join(md)+"\n", encoding="utf-8")


def main() -> None:
    ensure_dirs(CLAIMS_DIR, BY_PAPER, DOSSIERS, REGISTRY, GENERATED)
    all_claims: list[dict[str, Any]] = []
    for cat in sorted(CATALOG, key=lambda r: int(r["reading_order"])):
        all_claims.extend(build_paper_claims(cat))
    augment_law_and_nogo_records(all_claims)
    # Reassign IDs per paper after all deterministic additions/augmentations.
    by_pid = defaultdict(list)
    for c in all_claims: by_pid[c["source_paper"]].append(c)
    for pid, claims in by_pid.items():
        claims.sort(key=lambda c: (0 if c["claim_type"]=="paper_thesis" else 1, c["expanded_start_line"], c["claim_type"], c["normalized_claim"][:80]))
        for i,c in enumerate(claims,1): c["claim_id"] = f"{pid}-C{i:04d}"
    attach_paper_nonclaims(all_claims)
    assign_vii_links(all_claims)
    write_claim_products(all_claims)
    write_no_go_prior_scaffold_correspondence(all_claims)
    summary = {
        "papers": len(by_pid),
        "claims": len(all_claims),
        "claim_types": Counter(c["claim_type"] for c in all_claims),
        "claim_grades": Counter(c["claim_grade"] for c in all_claims),
        "formalization_statuses": Counter(c["formalization"]["status"] for c in all_claims),
        "law_claims": Counter((c.get("law_id") or "")[0:1] for c in all_claims if c.get("law_id")),
        "no_go_claims": sum(1 for c in all_claims if c.get("no_go_id")),
        "blocked_papers": [pid for pid, claims in by_pid.items() if claims and claims[0]["source_completeness"].startswith("BLOCKED")],
    }
    # Counter is JSON serializable only after dict conversion.
    for k in ("claim_types","claim_grades","formalization_statuses","law_claims"):
        summary[k] = dict(summary[k])
    (GENERATED / "step2_claim_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
