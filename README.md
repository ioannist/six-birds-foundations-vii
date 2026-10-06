# Six Birds Foundations VII: Lawful Theory Interaction

This repository contains the manuscript and reproducibility package for:

> **Six Birds Foundations VII: Lawful Theory Interaction**
>
> Ioannis Tsiokos
>
> Preprint v2.0, 6 October 2026. DOI (v2.0): [10.5281/zenodo.23187549](https://doi.org/10.5281/zenodo.23187549)
>
> DOI (all versions): [10.5281/zenodo.22254856](https://doi.org/10.5281/zenodo.22254856);
> v1.0 (2 September 2026): [10.5281/zenodo.22254857](https://doi.org/10.5281/zenodo.22254857)

The paper gives a typed certificate language for when two theories interact lawfully and what a
joint theory must show to count as more than its parts. It proves that an observable of a join is
strict exactly when it has a split pair against each parent and their pairing, and that admission
orders are confluent, by Newman's lemma, when admission only enables. Its claims are
deliberately scoped: finite enumerations establish results only on their declared carriers, and formal verification establishes
the stated Lean declarations rather than the adequacy of a scientific interpretation.

**Keywords:** emergence calculus; lawful theory interaction; join of theories; strict join;
factorization; split pair; confluence; Newman's lemma; certificate language; enablement;
access coordinates; Lean 4; Six Birds Theory.

## What this repository provides

- The modular LaTeX manuscript and its supplement under `paper/`, with the release PDFs at
  `paper/submission/artifacts/Tsiokos_2026_Six_Birds_Foundations_VII_Lawful_Theory_Interaction.pdf`
  (24 pages) and
  `paper/submission/artifacts/Tsiokos_2026_Supplement_to_Six_Birds_Foundations_VII_Lawful_Theory_Interaction.pdf`
  (28 pages).
- A Lean 4 formalization under `formalization/lean/`, pinned to
  `leanprover/lean4:v4.28.0`.
- Independent Python finite-model laboratories under
  `formalization/foundations_vii_lab/`, covering all five formal-science phases.
- Machine-readable theorem, candidate, no-go, corollary, dependency, trust, and finite-evidence
  registries under `science/`.
- Human-readable validation and audit reports under `reports/` and `docs/`.
- Curated Foundations V/VI formal scaffolds used to establish provenance and inherited theorem
  boundaries.

## Main results and evidence boundary

The final science surface contains 36 terminal candidate dispositions, 20 formalization targets,
11 no-go fronts, 21 cross-family corollaries, 24 frozen scenarios, and 27 named countermodels. The
Phase-5 finite laboratory enumerates 86,912 raw cases, of which 84,864 are canonical under the
declared symmetry quotient.

The public Lean library contains 111 modules, 1,477 public declarations, and 732 theorem, lemma, or
corollary declarations. The recorded local replay on Lean 4.28.0 passes the cumulative kernel build,
all five Lean/Python differentials, and the final `#print axioms` capture with no `sorry` dependency.
The authoritative status files are:

- `formalization/lean/BUILD_STATUS_FINAL.json`
- `formalization/foundations_vii_lab/phase5/results/cross_implementation_status.json`
- `reports/FVII_SCI_05_VALIDATION.json`

These checks do not convert schemas into theorems, enlarge finite-carrier results, or validate an
application outside its stated bridge conditions.

## Reproduce the release

The deterministic source/Python rebuild requires Python 3.11 or later:

```bash
bash scripts/rebuild_fvii_sci05.sh
```

For the complete Lean kernel build, axiom replay, and all five Lean/Python comparisons, install the
pinned Lean toolchain and run:

```bash
bash scripts/run_fvii_sci05_external_lean.sh
```

Detailed Lean instructions are in `formalization/lean/EXTERNAL_COMPILE_FINAL.md`.

## Build the paper

A TeX installation with `latexmk`, `pdflatex`, and BibTeX is required:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

Each document is built again so that its references into the other resolve.

Build outputs are written under `paper/build/` and are intentionally ignored. The release PDFs are
tracked separately under `paper/submission/artifacts/`.

## Repository layout

- `paper/` — manuscript source, bibliography, generated tables, submission metadata, and release PDFs.
- `formalization/lean/` — Foundations VII Lean source and trust receipts.
- `formalization/foundations_vii_lab/` — Python reference implementation and finite evidence.
- `formalization/foundations_v_scaffold/` and `formalization/foundations_vi_scaffold/` — curated
  inherited formal assets.
- `science/` — final machine-readable scientific registries and traceability records.
- `readiness/`, `claims/`, `bridges/`, and `registry/` — cumulative source-to-result evidence and
  adjudication records.
- `reports/` and `docs/` — validation, scope, provenance, and citation audits.
- `scripts/` — deterministic builders, validators, and replay entry points.
- `CONTENTS.md` — a more detailed guide to the release surface.

## Provenance and local-only material

Original supplied ZIP archives are not distributed because they also contain operational review
material unrelated to the scientific release. Their curated extracts, file-level import manifests,
archive digests, and upstream commit identities remain tracked under `formalization/_provenance/`
and `source/_provenance/`. A maintainer with the original local archives can still verify them
against the published digest records.

The project used AI-assisted implementation and review. Operational prompts, session logs, raw
research-discovery packages, planning records, the source-paper corpus snapshot, and superseded
drafting templates are intentionally excluded from the public repository; the file ledgers
(`SHA256SUMS`, `generated/file_manifest.csv`) and some records still name these local-only files. The manuscript, formal source, finite evidence, validation code, and scientific
audit trail remain available for direct inspection.

## Scope and limitations

- The calculus is not presented as a universal algebra of arbitrary theories.
- Finite assays are exhaustive only over their explicitly declared carriers.
- Citation does not license theorem transport; inherited results require explicit bridge records.
- Kernel checking establishes derivability from the recorded Lean environment, not specification
  adequacy or empirical validity.
