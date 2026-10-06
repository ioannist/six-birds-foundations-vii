#!/usr/bin/env python3
"""Build the Step-1 immutable corpus inventory and source-located digests.

The script deliberately extracts structure, not semantic verdicts. Human survey cards and
canonical syntheses live elsewhere and cite these machine-generated locations.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
CATALOG = ROOT / "config" / "paper_catalog.csv"
DEEP_IDS = {
    "P031", "P027", "P026", "P028", "P030", "P029", "P032",
    "P006", "P023", "P034", "P053", "P046", "P041", "P040", "P058", "P056",
    # Expanded beyond the minimum plan because the user explicitly named cognition.
    "P005", "P055", "P044", "P013",
}

ENVIRONMENTS = (
    "definition", "theorem", "lemma", "proposition", "corollary", "remark",
    "conjecture", "assumption", "example",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def strip_comments(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        # A percent escaped by an odd number of backslashes is literal.
        cut = None
        for idx, ch in enumerate(line):
            if ch != "%":
                continue
            backslashes = 0
            j = idx - 1
            while j >= 0 and line[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                cut = idx
                break
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def balanced_group(text: str, brace_pos: int) -> tuple[str | None, int | None]:
    if brace_pos < 0 or brace_pos >= len(text) or text[brace_pos] != "{":
        return None, None
    depth = 0
    buf: list[str] = []
    i = brace_pos
    while i < len(text):
        ch = text[i]
        escaped = i > 0 and text[i - 1] == "\\"
        if ch == "{" and not escaped:
            depth += 1
            if depth > 1:
                buf.append(ch)
        elif ch == "}" and not escaped:
            depth -= 1
            if depth == 0:
                return "".join(buf), i + 1
            buf.append(ch)
        else:
            buf.append(ch)
        i += 1
    return None, None


def command_arguments(text: str, command: str) -> list[tuple[str, int]]:
    pat = re.compile(r"\\" + re.escape(command) + r"\*?(?:\s*\[[^\]]*\])?\s*\{")
    out: list[tuple[str, int]] = []
    for m in pat.finditer(text):
        brace = text.find("{", m.start())
        arg, _ = balanced_group(text, brace)
        if arg is not None:
            out.append((arg, text.count("\n", 0, m.start()) + 1))
    return out


def resolve_include(base: Path, raw: str) -> Path | None:
    cleaned = raw.strip().replace("\\jobname", "")
    if not cleaned or any(tok in cleaned for tok in ("#", "\\", "{")):
        return None
    candidate = (base / cleaned).resolve()
    if candidate.suffix == "":
        candidate = candidate.with_suffix(".tex")
    try:
        candidate.relative_to(SOURCE.resolve())
    except ValueError:
        return None
    return candidate if candidate.exists() else None


def dependency_closure(root_file: Path) -> tuple[list[Path], list[dict[str, str]]]:
    seen: set[Path] = set()
    edges: list[dict[str, str]] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        for cmd in ("input", "include"):
            for raw, _line in command_arguments(text, cmd):
                child = resolve_include(path.parent, raw)
                if child is None:
                    continue
                edges.append({
                    "from": str(path.relative_to(SOURCE.resolve())),
                    "to": str(child.relative_to(SOURCE.resolve())),
                    "kind": cmd,
                })
                visit(child)

    visit(root_file)
    return sorted(seen), edges


def expand_dependencies(root_file: Path) -> str:
    """Simple recursive expansion used only for metadata extraction."""
    stack: set[Path] = set()

    def expand(path: Path) -> str:
        path = path.resolve()
        if path in stack:
            return f"\n% CYCLIC INCLUDE SUPPRESSED: {path.name}\n"
        stack.add(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        pattern = re.compile(r"\\(input|include)\s*\{([^{}]+)\}")

        def repl(m: re.Match[str]) -> str:
            child = resolve_include(path.parent, m.group(2))
            if child is None:
                return m.group(0)
            return f"\n% BEGIN INCLUDED {child.name}\n{expand(child)}\n% END INCLUDED {child.name}\n"

        result = pattern.sub(repl, text)
        stack.remove(path)
        return result

    return expand(root_file)


def tex_to_plain(text: str) -> str:
    replacements = {
        r"\&": "&", r"\%": "%", r"\_": "_", r"~": " ",
        r"---": "—", r"--": "–", r"\,": " ", r"\;": " ", r"\!": "",
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    # Retain contents of common formatting commands, repeatedly for shallow nesting.
    for _ in range(5):
        text = re.sub(
            r"\\(?:textbf|textit|emph|mathrm|mathbf|mathsf|mathtt|operatorname|textrm|texttt|text|underline)\s*\{([^{}]*)\}",
            r"\1", text,
        )
        text = re.sub(r"\\texorpdfstring\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:cite\w*|ref|cref|Cref|eqref|autoref|label|footnote|url|href)\*?(?:\[[^\]]*\])?\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\begin\{[^{}]+\}|\\end\{[^{}]+\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\$+|\\\(|\\\)|\\\[|\\\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_abstract(expanded: str) -> str:
    cleaned = strip_comments(expanded)
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", cleaned, flags=re.S)
    if m:
        return tex_to_plain(m.group(1))
    m = re.search(r"\\abstract\s*\{", cleaned)
    if m:
        brace = cleaned.find("{", m.start())
        arg, _ = balanced_group(cleaned, brace)
        return tex_to_plain(arg or "")
    return ""


def extract_date(expanded: str) -> str:
    args = command_arguments(strip_comments(expanded), "date")
    return tex_to_plain(args[0][0]) if args else ""


def extract_sections(expanded: str) -> list[dict[str, object]]:
    text = strip_comments(expanded)
    pat = re.compile(r"\\(part|chapter|section|subsection|subsubsection)\*?(?:\s*\[[^\]]*\])?\s*\{")
    out: list[dict[str, object]] = []
    for m in pat.finditer(text):
        brace = text.find("{", m.start())
        arg, _ = balanced_group(text, brace)
        if arg is None:
            continue
        out.append({
            "level": m.group(1),
            "title_tex": arg.strip(),
            "title_plain": tex_to_plain(arg),
            "line": text.count("\n", 0, m.start()) + 1,
        })
    return out


def extract_env_headers(expanded: str) -> list[dict[str, object]]:
    text = strip_comments(expanded)
    env_re = "|".join(map(re.escape, ENVIRONMENTS))
    pat = re.compile(r"\\begin\{(" + env_re + r")\}(?:\[([^\]]*)\])?")
    out: list[dict[str, object]] = []
    for m in pat.finditer(text):
        nearby = text[m.end():m.end()+300]
        label_match = re.search(r"\\label\{([^{}]+)\}", nearby)
        out.append({
            "kind": m.group(1),
            "name_tex": (m.group(2) or "").strip(),
            "name_plain": tex_to_plain(m.group(2) or ""),
            "label": label_match.group(1) if label_match else "",
            "line": text.count("\n", 0, m.start()) + 1,
        })
    return out


def extract_keyword_paragraphs(expanded: str) -> dict[str, list[dict[str, object]]]:
    text = strip_comments(expanded)
    paragraphs = re.split(r"\n\s*\n+", text)
    keys = {
        "contribution": re.compile(r"contribution|what (?:this|the) paper prove|main result", re.I),
        "nonclaim": re.compile(r"non[- ]?claim|does not (?:prove|claim|establish)|not a claim", re.I),
        "limitation": re.compile(r"limitation|scope boundary|outside (?:the|this) scope", re.I),
        "future": re.compile(r"future work|open problem|outlook|deferred", re.I),
    }
    result: dict[str, list[dict[str, object]]] = {k: [] for k in keys}
    cursor = 0
    for para in paragraphs:
        pos = text.find(para, cursor)
        cursor = max(cursor, pos + len(para))
        plain = tex_to_plain(para)
        if len(plain) < 35:
            continue
        for key, rx in keys.items():
            if rx.search(plain) and len(result[key]) < 12:
                result[key].append({
                    "line": text.count("\n", 0, max(0, pos)) + 1,
                    "text": plain[:1800],
                })
    return result


def plain_path_for(source_path: str) -> Path | None:
    p = Path(source_path)
    if p.name == "main.tex":
        name = p.parent.name + ".txt"
    else:
        name = p.stem + ".txt"
    candidate = ROOT / "derived" / "plain" / name
    return candidate if candidate.exists() else None


def word_count(path: Path | None) -> int:
    if path is None:
        return 0
    return len(re.findall(r"\b[\w’'-]+\b", path.read_text(encoding="utf-8", errors="replace")))


def main() -> None:
    (ROOT / "corpus").mkdir(exist_ok=True)
    (ROOT / "derived" / "metadata").mkdir(parents=True, exist_ok=True)
    (ROOT / "derived" / "digests").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)

    with CATALOG.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    manifest: list[dict[str, object]] = []
    dependency_index: dict[str, object] = {}
    coverage: list[dict[str, str]] = []

    for row in sorted(rows, key=lambda r: int(r["reading_order"])):
        root_file = SOURCE / row["source_path"]
        if not root_file.exists():
            raise FileNotFoundError(f"Missing catalog root: {root_file}")
        deps, edges = dependency_closure(root_file)
        expanded = expand_dependencies(root_file)
        root_hash = sha256_file(root_file)
        tree_material = "".join(
            f"{p.relative_to(SOURCE)}\0{sha256_file(p)}\n" for p in deps
        ).encode("utf-8")
        tree_hash = sha256_bytes(tree_material)
        plain_path = plain_path_for(row["source_path"])
        metadata = {
            "paper_id": row["paper_id"],
            "reading_order": int(row["reading_order"]),
            "catalog_title": row["title"],
            "source_path": row["source_path"],
            "root_sha256": root_hash,
            "tree_sha256": tree_hash,
            "dependencies": [str(p.relative_to(SOURCE)) for p in deps],
            "dependency_edges": edges,
            "date": extract_date(expanded),
            "abstract": extract_abstract(expanded),
            "sections": extract_sections(expanded),
            "environment_headers": extract_env_headers(expanded),
            "keyword_paragraphs": extract_keyword_paragraphs(expanded),
            "plain_text_path": str(plain_path.relative_to(ROOT)) if plain_path else "",
            "plain_word_count": word_count(plain_path),
            "cluster": row["cluster"],
            "step_1_depth": "DEEP_READ" if row["paper_id"] in DEEP_IDS else "SURVEYED",
            "foundations_vii_hooks": row["foundations_vii_hooks"],
        }
        (ROOT / "derived" / "metadata" / f"{row['paper_id']}.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        dependency_index[row["paper_id"]] = {
            "root": row["source_path"],
            "files": metadata["dependencies"],
            "edges": edges,
            "tree_sha256": tree_hash,
        }
        manifest.append({
            "paper_id": row["paper_id"],
            "reading_order": row["reading_order"],
            "title": row["title"],
            "source_path": row["source_path"],
            "root_sha256": root_hash,
            "tree_sha256": tree_hash,
            "source_files": len(deps),
            "source_bytes": sum(p.stat().st_size for p in deps),
            "plain_word_count": metadata["plain_word_count"],
            "cluster": row["cluster"],
            "step_1_depth": metadata["step_1_depth"],
        })
        coverage.append({
            "paper_id": row["paper_id"],
            "title": row["title"],
            "state": metadata["step_1_depth"],
            "survey_card": f"notes/survey/{row['paper_id']}.md",
            "deep_note": f"notes/deep/{row['paper_id']}.md" if row["paper_id"] in DEEP_IDS else "",
            "source_hash": root_hash,
            "last_transition": "2026-07-26",
            "transition_note": "Step 1 source-located read",
        })

        digest_lines = [
            f"# Machine digest — {row['paper_id']} — {row['title']}", "",
            f"- Source: `{row['source_path']}`", f"- Root SHA-256: `{root_hash}`",
            f"- Dependency-tree SHA-256: `{tree_hash}`",
            f"- Step-1 depth: **{metadata['step_1_depth']}**", "",
            "## Abstract", "", metadata["abstract"] or "_No abstract was mechanically recovered._", "",
            "## Outline", "",
        ]
        for sec in metadata["sections"]:
            indent = {"part": 0, "chapter": 0, "section": 0, "subsection": 2, "subsubsection": 4}.get(sec["level"], 0)
            digest_lines.append(" " * indent + f"- L{sec['line']}: {sec['title_plain'] or sec['title_tex']}")
        digest_lines.extend(["", "## Named formal surfaces", ""])
        for env in metadata["environment_headers"][:250]:
            title = env["name_plain"] or "(unnamed)"
            label = f"; `{env['label']}`" if env["label"] else ""
            digest_lines.append(f"- L{env['line']}: {env['kind']} — {title}{label}")
        for key, heading in (("contribution", "Contribution/result passages"), ("nonclaim", "Nonclaim passages"), ("limitation", "Scope/limitation passages"), ("future", "Future/open passages")):
            digest_lines.extend(["", f"## {heading}", ""])
            if not metadata["keyword_paragraphs"][key]:
                digest_lines.append("_None mechanically isolated; consult the source and survey card._")
            for item in metadata["keyword_paragraphs"][key]:
                digest_lines.append(f"- L{item['line']}: {item['text']}")
        (ROOT / "derived" / "digests" / f"{row['paper_id']}.md").write_text(
            "\n".join(digest_lines).rstrip() + "\n", encoding="utf-8"
        )

    with (ROOT / "corpus" / "paper_manifest.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest[0].keys()), lineterminator="\n")
        writer.writeheader(); writer.writerows(manifest)
    with (ROOT / "corpus" / "coverage.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(coverage[0].keys()), lineterminator="\n")
        writer.writeheader(); writer.writerows(coverage)
    (ROOT / "corpus" / "dependency_trees.json").write_text(
        json.dumps(dependency_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    dep_md = ["# TeX dependency trees", ""]
    for row in sorted(rows, key=lambda r: int(r["reading_order"])):
        data = dependency_index[row["paper_id"]]
        dep_md.extend([f"## {row['paper_id']} — {row['title']}", "", f"Root: `{data['root']}`", f"Tree SHA-256: `{data['tree_sha256']}`", "", "Files:"])
        dep_md.extend(f"- `{p}`" for p in data["files"])
        dep_md.append("")
    (ROOT / "corpus" / "dependency_trees.md").write_text("\n".join(dep_md), encoding="utf-8")

    source_candidates = sorted(p for p in SOURCE.rglob("*") if p.is_file())
    ignored: set[str] = set()
    if source_candidates:
        result = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            cwd=ROOT,
            input="\n".join(str(p.relative_to(ROOT)) for p in source_candidates),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode in (0, 1):
            ignored = set(result.stdout.splitlines())
    source_files = sorted(p for p in source_candidates if str(p.relative_to(ROOT)) not in ignored)
    with (ROOT / "corpus" / "source_hashes.sha256").open("w", encoding="utf-8") as f:
        for p in source_files:
            f.write(f"{sha256_file(p)}  {p.relative_to(ROOT)}\n")

    report = [
        "# Step 1 source inventory report", "",
        f"- Cataloged paper roots: **{len(manifest)}**",
        f"- Deep-read roots: **{sum(m['step_1_depth']=='DEEP_READ' for m in manifest)}**",
        f"- Survey-read roots: **{sum(m['step_1_depth']=='SURVEYED' for m in manifest)}**",
        f"- Wish lists: **4**",
        f"- Frozen source files (including provenance archive): **{len(source_files)}**",
        f"- Total recovered plain-text words: **{sum(int(m['plain_word_count']) for m in manifest):,}**",
        "",
        "All root and dependency-tree hashes are recorded in `corpus/paper_manifest.csv`; all frozen-file hashes are in `corpus/source_hashes.sha256`.",
    ]
    (ROOT / "reports" / "SOURCE_INVENTORY.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Built inventory for", len(manifest), "paper roots")


if __name__ == "__main__":
    main()
