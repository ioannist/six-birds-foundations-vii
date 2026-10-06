# Repository contents

## Paper

- `paper/main.tex` — canonical LaTeX entry point.
- `paper/sections/` and `paper/appendices/` — modular manuscript source.
- `paper/references.bib` — active bibliography containing 41 cited works.
- `paper/tables/` — generated tables used by the manuscript.
- `paper/submission/artifacts/` — canonical release PDF.
- `paper/submission/zenodo-*.json` and `zenodo-description.html` — Zenodo record metadata
  (DOI 10.5281/zenodo.22254857).

## Final formal-science release

- `FVII_SCIENCE_FINAL_REPORT.md` and `FVII_SCI_05_REPORT.md` — controlling release reports.
- `formalization/lean/FoundationsVII.lean` — public Lean root.
- `formalization/lean/FoundationsVII/Release/Terminal.lean` — executable terminal registries.
- `formalization/lean/FoundationsVII/Trust/PrintAxiomsFinal.lean` — public theorem axiom-replay
  surface.
- `formalization/foundations_vii_lab/phase5/` — final bounded laboratory and certificates.
- `science/registry/final_*` — canonical object, theorem, no-go, corollary, decision, dependency,
  trust, candidate, target, and finite-assay registries.
- `science/traceability/final_*` — statement hashes, declaration edges, imports, trust, and bounded
  witness records.
- `reports/FVII_SCI_05_*` — final acceptance, evidence, trust, and closure reports.

## Cumulative foundations and provenance

- `corpus/`, `notes/`, `synthesis/`, and `registry/` — reading inventory and canonical corpus map.
- `claims/` and `bridges/` — claim atlas and bridge records.
- `readiness/` — terminal candidate dossiers, scope rulings, countermodels, and formalization map.
- `formalization/foundations_v_scaffold/` and `formalization/foundations_vi_scaffold/` — curated
  inherited formal trees.
- `formalization/_provenance/` — import manifests, hashes, selection policies, and upstream commit
  identities. Original ZIPs are local-only.

## Reproducibility

- `scripts/rebuild_fvii_sci05.sh` — deterministic source/Python release rebuild.
- `scripts/run_fvii_sci05_external_lean.sh` — full Lean kernel, axiom, and five-phase differential
  replay.
- `scripts/build_delivery_manifest.py` and `scripts/verify_delivery_manifest.py` — delivery ledger
  generation and verification.
- `generated/file_manifest.csv` and `SHA256SUMS` — complete tracked release ledger.
- `.github/workflows/formalization-baseline.yml` — CI for deterministic regeneration, Lean replay,
  and the imported Foundations VI laboratory.

Earlier `FVII_SCI_01` through `FVII_SCI_04` reports and corresponding phase directories are retained
as cumulative evidence. The SCI-05 records are the current release authority.
