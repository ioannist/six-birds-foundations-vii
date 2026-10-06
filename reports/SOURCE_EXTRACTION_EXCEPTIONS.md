# Source extraction and package exceptions

Step 1 treats frozen TeX as authoritative and records any limitation that changes the evidentiary depth of a paper. No OCR, web replacement, or silently substituted edition was used.

## P020 — converter failure, recovered

The supplied paper source is present, but malformed verbatim markup breaks the standard conversion path. A conservative repository TeX stripper recovered **11,741 words**, **83 section headings**, and **24 standard theorem/definition environments**. Its survey card therefore uses the full supplied TeX tree plus the recovered plain text. This is not a Step-1 coverage blocker.

## P039 — incomplete supplied source package

The supplied root contains its title, abstract, preamble, and document assembly map, but all **18** declared `\input`/`\include` files are absent. `references.bib` is also absent. Consequently the P039 card is limited to the root abstract, declarations, and the names/order of the missing sections and appendices. It is **not** represented as a full-paper read.

Missing declared files:

- `papers/includes/paper_macros.tex`
- `papers/sections/sec_01_introduction.tex`
- `papers/sections/sec_02_the_calculus.tex`
- `papers/sections/sec_03_method.tex`
- `papers/sections/sec_04_form.tex`
- `papers/sections/sec_05_window.tex`
- `papers/sections/sec_06_value.tex`
- `papers/sections/sec_07_measure.tex`
- `papers/sections/sec_08_audits.tex`
- `papers/sections/sec_09_mysteries.tex`
- `papers/sections/sec_10_one_grammar.tex`
- `papers/sections/sec_11_scope.tex`
- `papers/sections/sec_12_discussion.tex`
- `papers/sections/sec_13_conclusion.tex`
- `papers/appendices/app_a_carriers.tex`
- `papers/appendices/app_b_audits.tex`
- `papers/appendices/app_c_reproducibility.tex`
- `papers/appendices/app_d_external_review.tex`

**Status:** `BLOCKED_FULL_TEXT`. Step 2 may not create a claim/proof/nonclaim dossier for P039 until a complete, authoritatively matched source package or PDF is supplied. P039 remains useful only as a clearly scoped domain-pressure-test stub.

## Consequence for Step-1 completion

The exception does not invalidate the canonical SBT spine, law registries, wish-list synthesis, or the other 57 paper cards. It does qualify the statement ‘all papers’: Step 1 has complete source-located coverage for 57 papers and root-stub-level coverage for P039, with the deficit mechanically exposed here and in its survey card.
