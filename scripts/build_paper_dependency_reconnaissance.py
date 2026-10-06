#!/usr/bin/env python3
"""Build a Step-1, citation-level dependency reconnaissance for the 58-paper corpus.

This is deliberately weaker than the claim/bridge dependency graph planned for Step 2.
It records only which supplied corpus papers are visibly cited by which source roots,
using an explicit auditable alias table.  It never infers theorem inheritance, statement
identity, bridge validity, or evidentiary independence from a citation alone.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "paper_catalog.csv"
SOURCE_ROOT = ROOT / "source"
CORPUS = ROOT / "corpus"
REPORTS = ROOT / "reports"
GENERATED = ROOT / "generated"

# Citation commands used by the supplied roots.  Optional prenote/postnote brackets are
# accepted; citation lists may span lines.
CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|citeyearpar|autocite|"
    r"parencite|textcite|footcite|nocite)\*?(?:\[[^\]]*\]){0,2}\{([^{}]+)\}",
    re.MULTILINE,
)


def aliases(*keys: str) -> set[str]:
    return {key.casefold() for key in keys}


# Exact citation-key aliases observed in the frozen source.  Descriptive aliases are
# preferable to fuzzy title matching because most external .bib files were not supplied.
# A key may map to more than one paper only where the source itself cites a series/family.
PID_ALIASES: dict[str, set[str]] = {
    "P001": aliases("sixbirds_darkenergy", "de"),
    "P002": aliases("Tsiokos2026Quantum", "tsiokos2026quantum", "quantum"),
    "P003": aliases("Tsiokos2026AcceptedNewLayer", "Tsiokos2026StrictTests"),
    "P004": aliases("Tsiokos2026Adequacy", "Tsiokos2026XiCompanion"),
    "P006": aliases("Tsiokos2026AOR", "TsiokosAOR2026"),
    "P007": aliases("Tsiokos2026CarrierExactification"),
    "P008": aliases("Tsiokos2026CarrierToEvent"),
    "P009": aliases("Tsiokos2026NeedleKiller"),
    "P011": aliases("Tsiokos2026Hiddenness", "TsiokosHiddenness2026", "hiddenness"),
    "P012": aliases(
        "Tsiokos2026HolonomyMemory",
        "Tsiokos2026Holonomy",
        "Tsiokos2026PredictiveQuotients",
        "Tsiokos2026RouteTransport",
    ),
    "P013": aliases("Tsiokos2026Institutions", "Tsiokos2026InstitutionsStrictExtensions", "institutions"),
    "P014": aliases("Tsiokos2026InternalStructure"),
    "P015": aliases("Tsiokos2026EventPackages", "Tsiokos2026LocallyBoolean"),
    "P016": aliases("Tsiokos2026MarkingErasureRecombination", "Tsiokos2026MarkingErasure"),
    "P017": aliases("Tsiokos2026NavierStokes"),
    "P018": aliases("Tsiokos2026OneMetaTheory", "clay"),
    "P019": aliases("Tsiokos2026PvNP", "Tsiokos2026CSL"),
    "P021": aliases("Tsiokos2026PromotionCriteria"),
    "P022": aliases("Tsiokos2026RecombinationWitnesses"),
    "P023": aliases("Tsiokos2026Reflexive"),
    "P024": aliases("Tsiokos2026RH"),
    "P025": aliases("Tsiokos2026SDTC", "TsiokosSDTC2026"),
    "P026": aliases(
        "Tsiokos2026FoundationsIII",
        "Tsiokos2026FoundIII",
        "TsiokosFoundationsIII2026",
        "TsiokosFoundationsIII",
        "Tsiokos_FoundationsIII",
    ),
    "P027": aliases(
        "Tsiokos2026FoundationsII",
        "Tsiokos2026FoundII",
        "TsiokosFoundationsII2026",
        "TsiokosFoundationsII",
        "Tsiokos_FoundationsII",
        "foundations2",
    ),
    "P028": aliases(
        "Tsiokos2026FoundationsIV",
        "Tsiokos2026FoundIV",
        "Tsiokos_FoundationsIV",
        "foundations4",
    ),
    "P029": aliases("Tsiokos2026FoundationsVIDynamicalLaws", "Tsiokos2026FoundVI"),
    "P030": aliases("Tsiokos2026FoundationsVEndogenousClosure", "FoundationsVCognition", "cognition"),
    "P031": aliases(
        "Tsiokos2026SixBirds",
        "Tsiokos2026Foundations",
        "Tsiokos2026EmergenceCalculus",
        "Tsiokos2026FoundationsI",
        "Tsiokos2026FoundI",
        "TsiokosFoundationsI2026",
        "TsiokosFoundations",
        "Tsiokos2026SixBirdsFoundations",
        "sixbirds_foundations",
        "tsiokos2026sixbirds",
        "tsiokos2026_foundations",
        "sixbirds2026",
        "SixBirdsFramework",
        "SixBirdsTheory",
        "SB_FOUNDATIONS",
        "SBTFoundationsI",
        "Tsiokos_FoEC",
        "foundations1",
        "tsiokos_2026_18365949",
    ),
    "P032": aliases("Tsiokos2026NoGo", "Tsiokos2026SixBirdsNoGo"),
    "P033": aliases("Tsiokos2026ProtocolTrap", "Tsiokos2026SixBirdsProtocolTrap", "sixbirds_protocol_trap"),
    "P034": aliases("SBTIncompleteness", "Tsiokos2026PackageChange"),
    "P035": aliases("ns"),
    "P036": aliases("neutrino"),
    "P038": aliases("Tsiokos2026CantorShell", "Tsiokos2026Cantor", "SBTCantorShell", "cantor"),
    "P039": aliases("cc"),
    "P042": aliases("Tsiokos2026CastStone", "TsiokosCastStone"),
    "P043": aliases("Tsiokos2026ToChart"),
    "P044": aliases("ltm"),
    "P045": aliases("Tsiokos2026ToClassify"),
    "P046": aliases(
        "Tsiokos2026CountStone",
        "Tsiokos2026ToCount",
        "tsiokos2026countstone",
        "TsiokosMathTheory",
        "ToCountAStone",
        "tocount",
    ),
    "P047": aliases(
        "Tsiokos2026ToCreate",
        "TsiokosCreateStone",
        "Tsiokos2026MinSubstrate",
        "tsiokos2026minsubstrate",
        "tsiokos2026create",
        "tsiokos2026_create",
        "tsiokos2026pica",
        "sixbirds_create_stone",
        "create",
    ),
    "P048": aliases("Tsiokos2026FlattenStone", "Tsiokos2026Rewriting"),
    "P049": aliases("threestones"),
    "P050": aliases("Tsiokos2026LayStone", "tsiokos2026_lay", "sixbirds_lay_stone"),
    "P051": aliases("Tsiokos2026NotchAStone", "tsiokos2026notch", "notch"),
    "P052": aliases("tsiokos2026_plot", "plot"),
    "P053": aliases("zfc"),
    "P054": aliases("Tsiokos2026Currency", "Tsiokos2026SpendStone", "tsiokos2026_spend"),
    "P055": aliases("Tsiokos2026Agents", "Tsiokos2026ThrowStone", "agents"),
    "P057": aliases("xor"),
    "P058": aliases("Tsiokos2026WhyMath", "Tsiokos_WhyMath"),
}

# Family/series keys intentionally map to every paper named by the source entry.
MULTI_TARGET_ALIASES: dict[str, tuple[str, ...]] = {
    "fixedsupport": ("P003", "P007", "P008", "P014", "P021", "P037"),
    "sau": ("P040", "P058"),
    "zfc": ("P053", "P034"),
}

# Corpus-like references named in the source but absent from the 58-paper catalog.
# These remain visible rather than being guessed onto a nearby supplied paper.
OUT_OF_CORPUS: dict[str, str] = {
    "tsiokos2026wakestone": "To Wake a Stone / A Life Is a Theory; not in the 58-paper catalog",
    "tsiokos2026life": "Life-theory paper; not in the 58-paper catalog",
    "six_birds_life": "Life-theory paper/repository; not in the 58-paper catalog",
    "life": "A Life Is a Theory; not in the 58-paper catalog",
    "tte": "Tests to Events / Born-route repository; not in the 58-paper catalog",
    "tobe": "What It Is Like to Be a Layer proposal; not in the 58-paper catalog",
}

# Internal-looking keys whose supplied roots do not identify a unique catalog member.
UNRESOLVED_INTERNAL: dict[str, str] = {
    "tsiokos2026stone": "ambiguous cross-domain Six Birds paper key; external bibliography absent",
    "sbtrecognition": "recognition-source key; no unique 58-paper target recoverable from supplied roots",
}

# Internal artifacts/repositories, not paper dependencies.
NON_PAPER_INTERNAL: dict[str, str] = {
    "sixbirds_de_repo": "dark-energy code repository citation",
}


def load_catalog() -> list[dict[str, str]]:
    with CATALOG.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def invert_aliases() -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = defaultdict(list)
    for pid, keys in PID_ALIASES.items():
        for key in keys:
            out[key].append(pid)
    for key, pids in MULTI_TARGET_ALIASES.items():
        for pid in pids:
            if pid not in out[key.casefold()]:
                out[key.casefold()].append(pid)
    return {key: tuple(sorted(pids)) for key, pids in out.items()}


def citation_occurrences(raw: str) -> list[tuple[str, int]]:
    found: list[tuple[str, int]] = []
    for match in CITE_RE.finditer(raw):
        line = raw.count("\n", 0, match.start()) + 1
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                found.append((key, line))
    return found


def looks_internal(key: str) -> bool:
    folded = key.casefold()
    return (
        "tsiokos" in folded
        or "sixbird" in folded
        or folded.startswith("sbt")
        or folded == "sb_foundations"
        or folded in {
            "foundations1", "foundations2", "foundations4", "foundationsvcognition",
            "fixedsupport", "cognition", "agents", "institutions", "threestones",
            "quantum", "de", "cc", "neutrino", "ns", "plot", "xor", "notch",
            "create", "cantor", "zfc", "tocount", "clay", "sau", "life",
            "tte", "tobe", "hiddenness", "ltm",
        }
    )


def join_lines(values: Iterable[int]) -> str:
    vals = sorted(set(values))
    return ";".join(str(v) for v in vals)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    catalog = load_catalog()
    by_pid = {row["paper_id"]: row for row in catalog}
    expected = set(by_pid)
    alias_to_pids = invert_aliases()
    unknown_targets = {pid for pids in alias_to_pids.values() for pid in pids} - expected
    if unknown_targets:
        raise SystemExit(f"Alias table contains unknown targets: {sorted(unknown_targets)}")

    edge_acc: dict[tuple[str, str], dict[str, object]] = {}
    summary_rows: list[dict[str, str]] = []
    per_paper_json: dict[str, object] = {}
    all_citation_rows: list[dict[str, str]] = []

    for row in sorted(catalog, key=lambda r: int(r["reading_order"])):
        source_pid = row["paper_id"]
        path = SOURCE_ROOT / row["source_path"]
        raw = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        occurrences = citation_occurrences(raw)
        by_key_lines: dict[str, set[int]] = defaultdict(set)
        key_original: dict[str, set[str]] = defaultdict(set)
        for key, line in occurrences:
            folded = key.casefold()
            by_key_lines[folded].add(line)
            key_original[folded].add(key)

        out_keys: dict[str, str] = {}
        unresolved_keys: dict[str, str] = {}
        nonpaper_keys: dict[str, str] = {}
        self_keys: set[str] = set()
        resolved_targets: set[str] = set()
        mapped_keys: set[str] = set()

        for folded, lines in sorted(by_key_lines.items()):
            originals = sorted(key_original[folded])
            display_key = "/".join(originals)
            targets = alias_to_pids.get(folded, ())
            if targets:
                mapped_keys.add(folded)
                for target_pid in targets:
                    if target_pid == source_pid:
                        self_keys.add(display_key)
                        continue
                    resolved_targets.add(target_pid)
                    acc = edge_acc.setdefault(
                        (source_pid, target_pid),
                        {"keys": set(), "lines": set(), "basis": set()},
                    )
                    acc["keys"].update(originals)  # type: ignore[index,union-attr]
                    acc["lines"].update(lines)  # type: ignore[index,union-attr]
                    acc["basis"].add(
                        "explicit series/family bibliography key"
                        if folded in MULTI_TARGET_ALIASES
                        else "exact curated citation-key alias"
                    )  # type: ignore[index,union-attr]
                continue
            if folded in OUT_OF_CORPUS:
                out_keys[display_key] = OUT_OF_CORPUS[folded]
            elif folded in NON_PAPER_INTERNAL:
                nonpaper_keys[display_key] = NON_PAPER_INTERNAL[folded]
            elif folded in UNRESOLVED_INTERNAL:
                unresolved_keys[display_key] = UNRESOLVED_INTERNAL[folded]
            elif looks_internal(display_key):
                unresolved_keys[display_key] = "internal-looking citation key not resolved by the supplied bibliography surface"

        for folded, lines in sorted(by_key_lines.items()):
            originals = sorted(key_original[folded])
            all_citation_rows.append(
                {
                    "source_paper_id": source_pid,
                    "citation_key": "/".join(originals),
                    "source_lines": join_lines(lines),
                    "classification": (
                        "RESOLVED_CORPUS"
                        if folded in mapped_keys
                        else "OUT_OF_CORPUS"
                        if folded in OUT_OF_CORPUS
                        else "NON_PAPER_INTERNAL"
                        if folded in NON_PAPER_INTERNAL
                        else "UNRESOLVED_INTERNAL"
                        if folded in unresolved_keys or looks_internal("/".join(originals))
                        else "EXTERNAL_OR_GENERAL"
                    ),
                    "targets": ";".join(alias_to_pids.get(folded, ())),
                }
            )

        summary = {
            "source_paper_id": source_pid,
            "source_title": row["title"],
            "source_path": row["source_path"],
            "citation_occurrence_count": str(len(occurrences)),
            "distinct_citation_key_count": str(len(by_key_lines)),
            "resolved_target_count": str(len(resolved_targets)),
            "resolved_target_ids": ";".join(sorted(resolved_targets)),
            "out_of_corpus_key_count": str(len(out_keys)),
            "out_of_corpus_keys": "; ".join(f"{key} [{reason}]" for key, reason in sorted(out_keys.items())),
            "unresolved_internal_key_count": str(len(unresolved_keys)),
            "unresolved_internal_keys": "; ".join(f"{key} [{reason}]" for key, reason in sorted(unresolved_keys.items())),
            "non_paper_internal_key_count": str(len(nonpaper_keys)),
            "non_paper_internal_keys": "; ".join(f"{key} [{reason}]" for key, reason in sorted(nonpaper_keys.items())),
            "self_reference_keys": ";".join(sorted(self_keys)),
            "status": (
                "SOURCE_PACKAGE_BLOCKED"
                if source_pid == "P039"
                else "RESOLVED_IN_CORPUS_REFERENCES"
                if resolved_targets
                else "NO_IN_CORPUS_REFERENCE_RESOLVED_AT_SURVEY_DEPTH"
            ),
            "inference_boundary": "CITATION_NAVIGATION_ONLY_NOT_THEOREM_DEPENDENCY_OR_BRIDGE_ADJUDICATION",
        }
        summary_rows.append(summary)
        per_paper_json[source_pid] = {
            **summary,
            "resolved_targets": sorted(resolved_targets),
            "out_of_corpus": out_keys,
            "unresolved_internal": unresolved_keys,
            "non_paper_internal": nonpaper_keys,
        }

    edge_rows: list[dict[str, str]] = []
    for (source_pid, target_pid), acc in sorted(edge_acc.items()):
        edge_rows.append(
            {
                "source_paper_id": source_pid,
                "source_title": by_pid[source_pid]["title"],
                "target_paper_id": target_pid,
                "target_title": by_pid[target_pid]["title"],
                "citation_keys": ";".join(sorted(acc["keys"])),  # type: ignore[index]
                "source_lines": join_lines(acc["lines"]),  # type: ignore[arg-type,index]
                "mapping_basis": ";".join(sorted(acc["basis"])),  # type: ignore[index]
                "status": "SURVEY_DEPTH_CITATION_EDGE",
                "inference_boundary": "NO_THEOREM_INHERITANCE_STATEMENT_IDENTITY_OR_EVIDENCE_INDEPENDENCE_INFERRED",
            }
        )

    write_csv(
        CORPUS / "paper_dependency_edges.csv",
        edge_rows,
        [
            "source_paper_id", "source_title", "target_paper_id", "target_title",
            "citation_keys", "source_lines", "mapping_basis", "status", "inference_boundary",
        ],
    )
    write_csv(
        CORPUS / "paper_dependency_summary.csv",
        summary_rows,
        [
            "source_paper_id", "source_title", "source_path", "citation_occurrence_count",
            "distinct_citation_key_count", "resolved_target_count", "resolved_target_ids",
            "out_of_corpus_key_count", "out_of_corpus_keys", "unresolved_internal_key_count",
            "unresolved_internal_keys", "non_paper_internal_key_count", "non_paper_internal_keys",
            "self_reference_keys", "status", "inference_boundary",
        ],
    )
    write_csv(
        CORPUS / "paper_citation_key_audit.csv",
        all_citation_rows,
        ["source_paper_id", "citation_key", "source_lines", "classification", "targets"],
    )

    indegree = Counter(row["target_paper_id"] for row in edge_rows)
    outdegree = Counter(row["source_paper_id"] for row in edge_rows)
    status_counts = Counter(row["status"] for row in summary_rows)
    unresolved_papers = [row for row in summary_rows if int(row["unresolved_internal_key_count"]) > 0]
    out_papers = [row for row in summary_rows if int(row["out_of_corpus_key_count"]) > 0]

    report = [
        "# Step-1 corpus-paper dependency reconnaissance",
        "",
        "## Scope and authority",
        "",
        "This report closes the original Step-1 requirement that every survey card name its dependency papers. It parses citation commands in the frozen supplied TeX roots and resolves only an explicit, reviewable table of in-corpus citation-key aliases. It is a **navigation graph**, not a theorem dependency graph.",
        "",
        "A citation edge does **not** establish that a result is imported, that hypotheses match, that a bridge is valid, that two papers are independent evidence, or that a cited paper is the unique source of a construction. Those judgments remain Step-2 claim/bridge work.",
        "",
        "## Census",
        "",
        f"- Papers covered: **{len(summary_rows)}**.",
        f"- Resolved directed in-corpus citation edges: **{len(edge_rows)}**.",
        f"- Papers with at least one resolved in-corpus citation: **{sum(bool(outdegree[pid]) for pid in by_pid)}**.",
        f"- Papers with an unresolved internal-looking key: **{len(unresolved_papers)}**.",
        f"- Papers naming a corpus-like work outside the 58-paper catalog: **{len(out_papers)}**.",
        "- P039 remains source-package blocked; absence of resolved citations there is not evidence of independence.",
        "",
        "## Most-cited supplied corpus papers at survey depth",
        "",
        "| Paper | Incoming source-paper count |",
        "|---|---:|",
    ]
    for pid, count in sorted(indegree.items(), key=lambda item: (-item[1], item[0]))[:20]:
        report.append(f"| {pid} — {by_pid[pid]['title']} | {count} |")

    report += [
        "",
        "## Papers with unresolved or out-of-corpus internal references",
        "",
        "| Source | Unresolved internal keys | Out-of-corpus keys |",
        "|---|---|---|",
    ]
    special = [
        row for row in summary_rows
        if int(row["unresolved_internal_key_count"]) or int(row["out_of_corpus_key_count"])
    ]
    if special:
        for row in special:
            report.append(
                f"| {row['source_paper_id']} | {row['unresolved_internal_keys'] or '—'} | "
                f"{row['out_of_corpus_keys'] or '—'} |"
            )
    else:
        report.append("| — | — | — |")

    report += [
        "",
        "## Machine-readable products",
        "",
        "- `corpus/paper_dependency_edges.csv` — resolved source-to-target citation edges with keys and source lines.",
        "- `corpus/paper_dependency_summary.csv` — exactly one status row per paper.",
        "- `corpus/paper_citation_key_audit.csv` — classification of every distinct citation key used by every root.",
        "- `generated/paper_dependency_reconnaissance.json` — complete per-paper reconstruction data and census.",
        "",
        "## Step-2 boundary",
        "",
        "Step 2 must replace citation-level navigation with claim-level records: exact source statement, hypotheses, object typing, proof/evidence grade, local Lean declaration where any, target use, and an explicit bridge verdict. This Step-1 graph is useful for reading order and omission detection only.",
    ]
    (REPORTS / "PAPER_DEPENDENCY_RECONNAISSANCE.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    payload = {
        "paper_count": len(summary_rows),
        "edge_count": len(edge_rows),
        "papers_with_resolved_targets": sum(bool(outdegree[pid]) for pid in by_pid),
        "papers_with_unresolved_internal_keys": len(unresolved_papers),
        "papers_with_out_of_corpus_keys": len(out_papers),
        "status_counts": dict(sorted(status_counts.items())),
        "alias_count": len(alias_to_pids),
        "inference_boundary": "citation navigation only; Step 2 not started",
        "papers": per_paper_json,
    }
    (GENERATED / "paper_dependency_reconnaissance.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({k: payload[k] for k in payload if k != "papers"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
