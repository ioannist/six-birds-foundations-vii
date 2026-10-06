#!/usr/bin/env python3
"""Lint draft prose against the PP-06 claim ledger.

Written during the prep phase so the writing phase inherits an enforcer rather than
a convention. Catches the three failure modes PP-01..PP-06 exist to prevent:

  1. grade inflation   -- verification vocabulary applied to a non-theorem grade
  2. grade-verb misuse -- a verb forbidden for a claim's disposition, near that claim
  3. unqualified finite claims -- "exhaustive"/"complete"/"for all" without a carrier

Usage:
    python3 scripts/lint_paper_prose.py <file> [<file> ...]

Exit status is the number of findings, so it can gate a build.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "paper_prep" / "PP-06_claim_ledger.json"

# PP-04 §4: a finite claim must carry its carrier cardinality.
UNQUALIFIED_FINITE = re.compile(
    r"\b(exhaustive|complete|for all|in general|universal|always)\b", re.I)
CARDINALITY_NEARBY = re.compile(r"\b(N\s*=|carrier|cardinality|declared|bounded|\d{2,})", re.I)
# A DENIAL of universality is the opposite of an overclaim.  "The taxonomy is not
# universal", "no finite null universalises", "never exhaustive" must not be flagged:
# firing on them trains a drafter to ignore the tool, which is worse than the noise.
NEGATED_SCOPE = re.compile(
    r"\b(not|no|never|nor|cannot|need not|does not|is not|are not|without|"
    r"neither|non-universal|unrestricted)\b", re.I)


def sentences(text: str) -> list[tuple[int, str]]:
    """Sentences with the line they start on, joined across line breaks.

    LaTeX sources wrap mid-sentence, so a line-bounded splitter chops most
    sentences in half.  That silently defeats both the negation test and the
    carrier test, because the qualifying clause usually sits on the other line --
    it made the linter fire on "... are *not* asserted to / be jointly exhaustive."
    Paragraphs are therefore unwrapped before splitting.
    """
    out: list[tuple[int, str]] = []
    # (line_no, text) per paragraph, blank-line separated
    para_lines: list[tuple[int, str]] = []
    lines = text.splitlines()

    def flush(chunk: list[tuple[int, str]]) -> None:
        if not chunk:
            return
        joined = " ".join(ln for _, ln in chunk)
        start = chunk[0][0]
        # map each sentence back to the line it begins on
        consumed = 0
        for m in re.finditer(r"[^.!?]*[.!?]|[^.!?]+$", joined):
            s = m.group(0).strip()
            if not s:
                continue
            # advance the line pointer by however much text precedes this sentence
            before = joined[:m.start()]
            line_off = 0
            acc = 0
            for i, (_, ln) in enumerate(chunk):
                if acc + len(ln) + 1 > len(before):
                    line_off = i
                    break
                acc += len(ln) + 1
            out.append((chunk[line_off][0], s))
            consumed = m.end()
        _ = (start, consumed)

    for i, ln in enumerate(lines):
        if ln.strip():
            para_lines.append((i + 1, ln.strip()))
        else:
            flush(para_lines)
            para_lines = []
    flush(para_lines)
    return out


# Grade verbs must match their inflections: a rule on "proved" has to catch
# "proves"/"proving"/"prove", which is the commonest way grade inflation arrives.
_STEM = {
    "proved": r"prov(?:ed|es|ing|e)",
    "establishes": r"establish(?:es|ed|ing)?",
    "demonstrates": r"demonstrat(?:es|ed|ing|e)",
    "delivered": r"deliver(?:ed|s|ing)?",
    "refuted": r"refut(?:ed|es|ing|e)",
    "open": r"open",
    "unproven": r"unproven",
}


def verb_pattern(verb: str) -> str:
    return _STEM.get(verb, re.escape(verb))



def check_environments(path: Path, text: str, claims: dict) -> list[str]:
    """A claim rendered in an environment its disposition forbids.

    PP-02 §2 / PP-04 §3 bind environment to disposition. Prose-level verb rules
    cannot see this: a schema stated inside \\begin{theorem} is a structural
    overclaim even if every word is careful.
    """
    ALLOWED = {
        "CONDITIONAL_THEOREM": {"theorem"},
        "FORMAL_SCHEMA": {"definition", "remark"},
        "REFUTED_CANDIDATE": {"remark", "theorem"},
        "CLOSED_DEFERRAL": {"remark"},
        "CONSTRUCTIVE_COUNTERMODEL": {"theorem"},
        "LEAN_DECIDABLE_FINITE": {"theorem"},
    }
    out = []
    for m in re.finditer(r"\\begin\{(theorem|definition|remark|lemma|proposition|corollary)\}(.*?)\\end\{\1\}",
                         text, re.S):
        env, body = m.group(1), m.group(2)
        line = text.count("\n", 0, m.start()) + 1
        low = body.lower()
        for cid, c in claims.items():
            nm = (c.get("name") or "").strip()
            hit = cid in body or (len(nm) >= 12 and nm.lower() in low)
            if not hit:
                continue
            ok = ALLOWED.get(c["disposition"], set())
            if env not in ok:
                out.append(f"{path}:{line}: BAD-ENVIRONMENT {cid} is {c['disposition']}; "
                           f"rendered in \\begin{{{env}}}, allowed: {sorted(ok) or 'none'}")
    return out


def main(argv: list[str]) -> int:
    if not LEDGER.is_file():
        print(f"missing {LEDGER}; run scripts/build_paper_claim_ledger.py first", file=sys.stderr)
        return 2
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    forbidden = [p.lower() for p in led["forbidden_phrases"]]
    claims = {c["candidate_id"]: c for c in led["claims"]}

    findings: list[str] = []
    for path in (Path(p) for p in argv):
        local: list[str] = []
        text = path.read_text(encoding="utf-8", errors="replace")
        # Grade-verb rules are proximity rules: a forbidden verb NEAR a named claim.
        # Inside a tabular the cells are independent, so a disposition column
        # containing "Conditional Theorem" sits next to every schema's id and fires
        # spuriously. Blank the table bodies for the prose passes; the environment
        # check below still sees the real document.
        prose = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}",
                       lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
        # Auditable suppression. A line carrying `% lint-allow: <reason>` is exempt.
        # Sections that discuss the vocabulary (e.g. stating which phrases are
        # forbidden) legitimately mention what they must not use. Suppression must
        # carry a reason, so every exemption is visible in the source and reviewable
        # -- which is the difference between a usable linter and one a drafter turns
        # off wholesale.
        _lines = text.splitlines()
        allowed_lines: set[int] = set()
        for i, ln in enumerate(_lines):
            if not re.search(r"%\s*lint-allow:\s*\S", ln):
                continue
            # exempt the marker line and the following sentence (up to a blank line),
            # so the marker can sit on its own line rather than mid-prose
            allowed_lines.add(i + 1)
            j = i + 1
            while j < len(_lines) and _lines[j].strip():
                allowed_lines.add(j + 1)
                if _lines[j].rstrip().endswith((".", "!", "?")):
                    break
                j += 1
        local.extend(check_environments(path, text, claims))
        for lineno, sent in sentences(prose):
            low = sent.lower()

            for phrase in forbidden:
                if phrase in low:
                    local.append(f"{path}:{lineno}: GRADE-INFLATION forbidden phrase {phrase!r}")

            # A claim binds its verb rules when the sentence names it by ID *or by
            # name*. Review gate 2 found the bypass: "Accessible-domain state normal
            # form establishes ..." named no ID, so no rule fired.
            named = set(re.findall(r"VII-C\d{3}", sent))
            for cid, c in claims.items():
                nm = (c.get("name") or "").strip()
                if len(nm) >= 12 and nm.lower() in low:
                    named.add(cid)
            for cid in sorted(named):
                c = claims.get(cid)
                if not c:
                    local.append(f"{path}:{lineno}: UNKNOWN claim id {cid}")
                    continue
                for verb in filter(None, c["must_not_use"].split(";")):
                    if verb == "*":
                        local.append(f"{path}:{lineno}: {cid} carries a forbidden disposition")
                    elif re.search(rf"\b{verb_pattern(verb)}\b", low):
                        local.append(
                            f"{path}:{lineno}: GRADE-VERB {cid} is {c['disposition']}; "
                            f"{verb!r} is forbidden for that grade")

            if (UNQUALIFIED_FINITE.search(sent)
                    and not CARDINALITY_NEARBY.search(sent)
                    and not NEGATED_SCOPE.search(sent)):
                m = UNQUALIFIED_FINITE.search(sent)
                local.append(
                    f"{path}:{lineno}: UNQUALIFIED-SCOPE {m.group(1)!r} without a declared carrier")

        # Drop suppressed lines, then merge. Per-file, so one file's exemptions
        # cannot silence another's.
        findings.extend(f for f in local
                        if int(re.search(r":(\d+):", f).group(1)) not in allowed_lines)

    for f in findings:
        print(f)
    print(f"\n{len(findings)} finding(s) across {len(argv)} file(s)")
    return len(findings)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
