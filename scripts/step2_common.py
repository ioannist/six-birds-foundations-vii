#!/usr/bin/env python3
"""Shared utilities for the Step-2 claim and bridge corpus.

The helpers are deliberately conservative.  TeX source remains authoritative;
plain-text fields are navigation views and every generated record retains an
exact source location plus the original TeX statement when available.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
EXPANDED = ROOT / "derived" / "expanded"
METADATA = ROOT / "derived" / "metadata"

FORMAL_ENVS = (
    "definition", "theorem", "theorem*", "lemma", "proposition", "corollary",
    "schema", "conjecture", "assumption", "postulate", "construction",
    "convention", "nonclaim", "example", "remark", "principle",
    # A few source files use capitalized variants.
    "Definition", "Theorem", "Lemma",
)

THEOREM_LIKE = {
    "theorem", "theorem*", "lemma", "proposition", "corollary", "Theorem", "Lemma"
}
DEFINITION_LIKE = {"definition", "Definition", "construction", "convention"}

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "if", "in", "into", "is", "it", "its", "law", "lemma", "of", "on",
    "or", "paper", "proposition", "schema", "that", "the", "their", "then", "theorem",
    "this", "to", "under", "we", "with", "without",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: scalarize(row.get(k, "")) for k in fieldnames})


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def scalarize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def strip_comments_preserve_lines(text: str) -> str:
    """Remove unescaped TeX comments while preserving line count."""
    out: list[str] = []
    for line in text.splitlines():
        cut: int | None = None
        for i, ch in enumerate(line):
            if ch != "%":
                continue
            n = 0
            j = i - 1
            while j >= 0 and line[j] == "\\":
                n += 1
                j -= 1
            if n % 2 == 0:
                cut = i
                break
        out.append(line if cut is None else line[:cut])
    # Retain trailing line behavior sufficiently for line-number calculation.
    return "\n".join(out)


def balanced_group(text: str, brace_pos: int) -> tuple[str | None, int | None]:
    if not (0 <= brace_pos < len(text)) or text[brace_pos] != "{":
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


def collect_simple_macros(text: str) -> dict[str, str]:
    """Collect no-argument macro bodies used to make statements readable.

    Parameterized macros are intentionally ignored.  This is a display aid,
    not a TeX evaluator.
    """
    macros: dict[str, str] = {}
    clean = strip_comments_preserve_lines(text)
    # \newcommand{\Foo}{body}, \renewcommand{\Foo}{body}, optional [0]
    pat = re.compile(r"\\(?:re)?newcommand\s*\{\\([A-Za-z@]+)\}\s*(?:\[0\])?\s*\{")
    for m in pat.finditer(clean):
        brace = clean.find("{", m.end() - 1)
        body, _ = balanced_group(clean, brace)
        # Statement macros in the supplied corpus can be several thousand
        # characters long (notably the no-go theorem statements).  They are
        # still no-argument macros and are safe to expand as a navigation aid.
        # Keep a generous finite bound to avoid treating whole chapters as
        # lexical substitutions.
        if body is not None and re.search(r"(?<!\\)#", body) is None and len(body) <= 12000:
            macros[m.group(1)] = body
    # \def\Foo{body}
    pat2 = re.compile(r"\\def\s*\\([A-Za-z@]+)\s*\{")
    for m in pat2.finditer(clean):
        brace = clean.find("{", m.end() - 1)
        body, _ = balanced_group(clean, brace)
        if body is not None and re.search(r"(?<!\\)#", body) is None and len(body) <= 12000:
            macros.setdefault(m.group(1), body)
    return macros


def expand_simple_macros(text: str, macros: dict[str, str], rounds: int = 4) -> str:
    if not macros:
        return text
    names = sorted(macros, key=len, reverse=True)
    out = text
    for _ in range(rounds):
        before = out
        for name in names:
            out = re.sub(r"\\" + re.escape(name) + r"\b(?:\{\})?", lambda _m, v=macros[name]: v, out)
        if out == before:
            break
    return out


def tex_to_plain(text: str, macros: dict[str, str] | None = None) -> str:
    if macros:
        text = expand_simple_macros(text, macros)
    text = strip_comments_preserve_lines(text)
    replacements = {
        r"\&": "&", r"\%": "%", r"\_": "_", r"\#": "#", r"~": " ",
        "---": "—", "--": "–", r"\,": " ", r"\;": " ", r"\!": "",
        r"\quad": " ", r"\qquad": " ", r"\colon": ":", r"\to": "→",
        r"\mapsto": "↦", r"\iff": " iff ", r"\Rightarrow": " implies ",
        r"\Longrightarrow": " implies ", r"\neq": "≠", r"\leq": "≤", r"\geq": "≥",
        r"\subseteq": "⊆", r"\in": "∈", r"\emptyset": "∅", r"\times": "×",
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    # Drop labels before generic command handling.
    text = re.sub(r"\\label\s*\{[^{}]*\}", " ", text)
    # Keep visible contents of common one-argument commands.
    visible = (
        "textbf", "textit", "emph", "mathrm", "mathbf", "mathsf", "mathtt",
        "operatorname", "textrm", "texttt", "text", "underline", "mbox",
        "ensuremath", "mathcal", "mathbb", "mathfrak", "overline", "widehat",
    )
    for _ in range(8):
        old = text
        text = re.sub(r"\\(?:" + "|".join(visible) + r")\s*\{([^{}]*)\}", r"\1", text)
        text = re.sub(r"\\texorpdfstring\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"\1", text)
        text = re.sub(r"\\href\s*\{[^{}]*\}\s*\{([^{}]*)\}", r"\1", text)
        if text == old:
            break
    # References are useful only as source links; do not contaminate statement text.
    text = re.sub(r"\\(?:cite\w*|ref|cref|Cref|eqref|autoref|pageref)\*?(?:\[[^\]]*\])?\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\(?:url|doi)\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\begin\{[^{}]+\}|\\end\{[^{}]+\}", " ", text)
    # Preserve command names that appear to be semantic constants if not expanded.
    def command_repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name in {"item", "noindent", "smallskip", "medskip", "bigskip", "hfill", "centering"}:
            return " "
        if name in {"alpha", "beta", "gamma", "delta", "epsilon", "lambda", "mu", "nu", "pi", "rho", "sigma", "tau", "phi", "psi", "omega", "Lambda", "Sigma", "Phi", "Psi", "Omega"}:
            return name
        # A paper-specific semantic macro is more informative by name than by deletion.
        if name and name[0].isupper():
            return name
        return " "
    text = re.sub(r"\\([A-Za-z@]+)\*?(?:\[[^\]]*\])?", command_repl, text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\$+|\\\(|\\\)|\\\[|\\\]", " ", text)
    text = re.sub(r"&", " ", text)
    text = re.sub(r"\\\\", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def source_line_map(expanded_text: str, root_rel: str, dep_files: list[str]) -> list[tuple[str, int]]:
    """Map each expanded line to an original dependency file and line.

    Expansion markers are generated by Step 1 as `% BEGIN INCLUDED <basename>`.
    If a basename is ambiguous, the root-relative path plus an ambiguity marker
    is retained; the expanded line remains available in every record.
    """
    by_name: dict[str, list[str]] = defaultdict(list)
    for f in dep_files:
        by_name[Path(f).name].append(f)
    stack: list[tuple[str, int]] = [(root_rel, 0)]
    out: list[tuple[str, int]] = []
    begin_re = re.compile(r"^% BEGIN INCLUDED (.+)$")
    end_re = re.compile(r"^% END INCLUDED (.+)$")
    for line in expanded_text.splitlines():
        mb = begin_re.match(line.strip())
        if mb:
            name = mb.group(1).strip()
            choices = by_name.get(name, [])
            if len(choices) == 1:
                path = choices[0]
            elif choices:
                path = choices[0] + " [basename ambiguous]"
            else:
                path = str(Path(root_rel).parent / name) + " [unresolved marker]"
            stack.append((path, 0))
            out.append((stack[-2][0], stack[-2][1]))
            continue
        me = end_re.match(line.strip())
        if me and len(stack) > 1:
            out.append((stack[-1][0], stack[-1][1]))
            stack.pop()
            continue
        path, n = stack[-1]
        n += 1
        stack[-1] = (path, n)
        out.append((path, n))
    return out


@dataclass
class EnvRecord:
    env: str
    title_tex: str
    body_tex: str
    labels: list[str]
    expanded_start_line: int
    expanded_end_line: int
    source_path: str
    source_start_line: int
    source_end_line: int
    proof_present: bool
    start_offset: int
    end_offset: int


def extract_environments(expanded_text: str, root_rel: str, dep_files: list[str]) -> list[EnvRecord]:
    clean = strip_comments_preserve_lines(expanded_text)
    line_map = source_line_map(expanded_text, root_rel, dep_files)
    env_re = "|".join(re.escape(e) for e in sorted(FORMAL_ENVS, key=len, reverse=True))
    pat = re.compile(r"\\begin\{(" + env_re + r")\}(?:\[([^\]]*)\])?")
    out: list[EnvRecord] = []
    occupied_until = -1
    for m in pat.finditer(clean):
        if m.start() < occupied_until:
            continue
        env = m.group(1)
        end_token = r"\end{" + env + "}"
        end = clean.find(end_token, m.end())
        if end < 0:
            continue
        body = clean[m.end():end]
        end2 = end + len(end_token)
        labels = re.findall(r"\\label\{([^{}]+)\}", body[:1200])
        start_line = clean.count("\n", 0, m.start()) + 1
        end_line = clean.count("\n", 0, end2) + 1
        idx0 = max(0, min(start_line - 1, len(line_map) - 1)) if line_map else 0
        idx1 = max(0, min(end_line - 1, len(line_map) - 1)) if line_map else 0
        sp0, sl0 = line_map[idx0] if line_map else (root_rel, start_line)
        sp1, sl1 = line_map[idx1] if line_map else (sp0, sl0 + max(0, end_line-start_line))
        if sp1 != sp0:
            # An environment should not cross include boundaries; preserve expanded range if it does.
            sl1 = sl0 + max(0, end_line - start_line)
        tail = clean[end2:end2 + 1600]
        proof_present = bool(re.search(r"^\s*\\begin\{proof\}", tail))
        out.append(EnvRecord(
            env=env,
            title_tex=(m.group(2) or "").strip(),
            body_tex=body.strip(),
            labels=labels,
            expanded_start_line=start_line,
            expanded_end_line=end_line,
            source_path=sp0,
            source_start_line=sl0,
            source_end_line=sl1,
            proof_present=proof_present,
            start_offset=m.start(),
            end_offset=end2,
        ))
        occupied_until = end2
    return out


def paragraph_spans(expanded_text: str) -> Iterator[tuple[int, int, int, str]]:
    """Yield (start_offset, end_offset, start_line, paragraph_tex)."""
    clean = strip_comments_preserve_lines(expanded_text)
    for m in re.finditer(r"(?:\A|\n\s*\n)(.*?)(?=\n\s*\n|\Z)", clean, flags=re.S):
        body = m.group(1).strip()
        if not body:
            continue
        start = m.start(1) + (len(m.group(1)) - len(m.group(1).lstrip()))
        yield start, m.end(1), clean.count("\n", 0, start) + 1, body


def normalize_tokens(text: str) -> set[str]:
    toks = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text.lower())
    return {t for t in toks if t not in STOPWORDS and not t.isdigit()}


def lexical_similarity(a: str, b: str) -> float:
    ta, tb = normalize_tokens(a), normalize_tokens(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    j = inter / union
    contain = inter / min(len(ta), len(tb))
    return 0.55 * j + 0.45 * contain


def split_hypotheses_conclusion(statement: str, claim_type: str) -> tuple[list[dict[str, str]], str, str]:
    """Conservatively split a plain statement while retaining full-source control."""
    s = re.sub(r"\s+", " ", statement).strip()
    if claim_type in DEFINITION_LIKE or claim_type.lower() in {"definition", "construction", "convention"}:
        return [], s, "NOT_APPLICABLE_DEFINITION"
    # Prefer explicit then/therefore boundaries.
    matches = list(re.finditer(r"\b(?:then|therefore|hence|it follows that|we have that|one has)\b[:,]?", s, flags=re.I))
    if matches:
        cut = matches[-1]
        left = s[:cut.start()].strip(" ;,.")
        right = s[cut.end():].strip(" ;,.")
        if len(right) >= 10:
            hyp = [{"text": left, "extraction": "EXPLICIT_CONCLUSION_BOUNDARY"}] if left else []
            return hyp, right, "EXPLICIT_BOUNDARY"
    # Collect leading setup sentences.
    parts = re.split(r"(?<=[.;])\s+", s)
    hyps: list[dict[str, str]] = []
    rest: list[str] = []
    leading = True
    for part in parts:
        p = part.strip()
        if not p:
            continue
        if leading and re.match(r"^(Let|Fix|Suppose|Assume|Given|For|Under|Whenever|If|On)\b", p, flags=re.I):
            hyps.append({"text": p, "extraction": "LEADING_SETUP_CLAUSE"})
        else:
            leading = False
            rest.append(p)
    if hyps and rest:
        return hyps, " ".join(rest), "LEADING_SETUP_SPLIT"
    # No lossy guess: the full statement governs.
    return ([{
        "text": "No independent hypothesis block was mechanically separable; all quantifiers and conditions in source_wording_tex govern.",
        "extraction": "SOURCE_STATEMENT_CONTROLS",
    }] if claim_type in THEOREM_LIKE or claim_type.lower() in {"schema", "conjecture", "postulate", "assumption"} else []), s, "FULL_STATEMENT_CONTROLS"


def find_expanded_path(metadata: dict[str, Any]) -> Path:
    plain = Path(metadata["plain_text_path"])
    candidate = EXPANDED / (plain.stem + ".tex")
    if candidate.exists():
        return candidate
    source_name = Path(metadata["source_path"]).name
    candidate = EXPANDED / source_name
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"No expanded source for {metadata['paper_id']}")


def line_context(text: str, line: int, radius: int = 2, macros: dict[str, str] | None = None) -> str:
    lines = text.splitlines()
    lo = max(0, line - 1 - radius)
    hi = min(len(lines), line + radius)
    return tex_to_plain(" ".join(lines[lo:hi]), macros)


def claim_grade_for(env: str, title: str, body: str) -> tuple[str, str]:
    lower = f"{title} {body}".lower()
    e = env.lower().rstrip("*")
    if e == "definition":
        return "definition", "DEFINITION"
    if e in {"construction", "convention"}:
        return e, "DEFINITIONAL_CONSTRUCTION"
    if e in {"theorem", "lemma", "proposition", "corollary"}:
        if any(x in lower for x in ("no-go", "impossib", "cannot ", "no free", "obstruction")):
            return e, "NEGATIVE_RESULT_THEOREM"
        if "conditional" in lower:
            return e, "CONDITIONAL_THEOREM"
        return e, "THEOREM_GRADE"
    if e == "principle":
        return "principle", "DECLARED_METHOD_PRINCIPLE"
    if e == "schema":
        if "calibrat" in lower:
            return "schema", "CALIBRATION_ANCHORED_SCHEMA"
        return "schema", "SCHEMA"
    if e == "conjecture":
        return "conjecture", "CONJECTURAL_INSTANCE"
    if e in {"assumption", "postulate"}:
        return e, "DECLARED_ASSUMPTION"
    if e == "nonclaim":
        return "nonclaim", "EXPLICIT_NONCLAIM"
    if e == "example":
        return "example", "WORKED_EXAMPLE_OR_MODEL"
    if e == "remark":
        return "remark", "INTERPRETIVE_REMARK"
    return e, e.upper()


def classify_prose_paragraph(plain: str) -> str | None:
    p = plain.strip()
    if len(p.split()) < 10:
        return None
    if re.search(r"\b(?:open problem|open question|future work|remains open|left for future|we defer|is deferred|outlook)\b", p, flags=re.I):
        return "open_problem"
    if re.search(r"\b(?:non[- ]?claim|we do not claim|does not claim|do not assert|does not assert|does not prove|not claimed here|outside (?:the )?scope)\b", p, flags=re.I):
        return "nonclaim"
    if re.search(r"\b(?:limitation|scope boundary|bounded result|within the declared scope|only under the declared|conditional on)\b", p, flags=re.I):
        return "scope_boundary"
    if re.match(r"^(?:Definition|We define|Define|Call |By .{0,60} we mean)\b", p, flags=re.I):
        return "prose_definition"
    if re.match(r"^(?:Main result|The principal result|Theorem|Proposition|Claim|Result|Finding|Final verdict|Verdict)\b", p, flags=re.I):
        return "result_summary"
    return None


def format_location(source_path: str, start: int, end: int, expanded_path: str, expanded_start: int, expanded_end: int) -> str:
    primary = f"source/{source_path}:L{start}" if start == end else f"source/{source_path}:L{start}-L{end}"
    exp = f"derived/expanded/{expanded_path}:L{expanded_start}" if expanded_start == expanded_end else f"derived/expanded/{expanded_path}:L{expanded_start}-L{expanded_end}"
    return primary + "; " + exp


def json_load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
