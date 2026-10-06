# ADR-0012 — Formalization reuse must preserve paper, statement, local-asset, trust, and machine-status boundaries

**Status:** accepted  
**Date:** 2026-07-26

## Context

The imported Foundations V and VI repositories provide a rich prior Lean spine, but several distinct facts can otherwise be conflated:

- a paper reports a mechanization;
- a corresponding source file is present locally;
- a local declaration is plausibly related;
- hypotheses and conclusion match exactly;
- the declaration elaborates under the pinned toolchain;
- finite tests or labs have been replayed locally.

The supplied Foundations IV paper reports 52 formal rows while only 14 dedicated local modules are in the imported scaffold. Paper-reported declarations must therefore not be stored as if they were locally matched declarations.

## Decision

1. Claim and bridge schemas separate `paper_reported_declarations` from locally imported modules/declarations.
2. Formalization status uses conservative categories: exact imported law assignment, abstract-core match, prior-core correspondence requiring audit, plausible lexical match requiring review, paper-disclosed asset not imported, and no match.
3. Exact hypothesis and conclusion match are nullable and are never inferred from name similarity.
4. Trust base, statement delta, elaboration status, source files, and lab/test evidence are separate fields.
5. Foundations IV rows absent from the supplied local scaffold remain `PAPER_DISCLOSED_ASSET_NOT_IMPORTED`, even when the paper names a declaration.
6. The inherited 123-module / 2,587-declaration / 793-theorem spine is not modified in Step 2.
7. Lean 4.28.0 unavailability is recorded as an environment limitation; no fresh local kernel replay is claimed.

## Consequences

- Paper mathematical grade is preserved without overstating local mechanization.
- Prior declarations can be reused later through explicit adapters.
- One inherited axiom and five opaque declarations remain visible.
- Step 2 introduces no Foundations VII declaration.
