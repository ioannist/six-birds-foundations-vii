# ADR-0007 — Import the Foundations VI scaffold as an immutable prior-proof base

**Status:** accepted
**Date:** 2026-07-26

## Context

The Step-1 corpus map treated the papers as source text. Before claim-level Step 2, the user supplied `six-birds-collatz_v19.zip`, which contains the mechanized Foundations VI project and vendored formal assets from earlier Foundations papers. Later Foundations VII claims are expected to depend on these prior definitions and proofs. Reconstructing them from prose would risk type drift, theorem weakening, duplicated trust assumptions, and loss of the existing law-to-lab-to-proof traceability.

## Decision

1. Record the supplied archive's digest and upstream commit under `formalization/_provenance/`; retain the original archive locally rather than distributing it publicly.
2. Extract a curated, byte-exact 282-file baseline to `formalization/foundations_vi_scaffold/`.
3. Import together the Lean tree, theorem ledger, law-design and landing protocol, formalization gates/examples/manifests, labs and results, paper source, CI recipe, and dependency audit. These assets form one evidence chain and must not be separated.
4. Treat the imported subtree as immutable. Foundations VII work must extend it from `formalization/lean/`, not edit it in place.
5. Keep operational prompts, review-request history, freeform idea files, and packaging scripts outside the active scaffold and public release. The archive digest and per-file import manifest preserve the public provenance boundary without making those materials project dependencies.
6. Record import-scope gaps explicitly. In particular, this archive has no dedicated Foundations V E-series Lean library; no absence claim is made beyond this supplied snapshot.

## Consequences

The repository is now self-contained for the prior formal scaffold and the external Collatz zip can be set aside. Every future VII theorem can cite an exact prior module/declaration or declare a new obligation. Upstream byte identity remains mechanically verifiable. The active VII Lake project can evolve without compromising the provenance of prior proofs.
