# ADR-0011 — Source-audited bridges rather than citation or lexical transfer

**Status:** accepted  
**Date:** 2026-07-26

## Context

A citation, shared term, or token such as `F1`, `E2`, or `G3` does not establish theorem inheritance. Across the corpus, the same token can name a local figure, experiment, table cell, workflow freeze, future-work item, or a genuine prior-law invocation.

Foundations VII preparation therefore needs a bridge atlas that is precise enough to prevent silent transfers of carriers, hypotheses, proof grade, nonclaims, and directionality.

## Decision

1. Every one of the 240 Step-1 in-corpus paper-invocation edges receives a bridge row.
2. Every candidate F/E/G token occurrence is source-audited. Accepted occurrences and rejected local-label collisions are both retained.
3. The 217 accepted occurrences are covered exactly once by 45 grouped paper/law bridges.
4. Every 52 F, 16 E, 13 G, and eight no-go row receives a future-reuse contract.
5. Bridge rows name source and target claims/contexts, objects/interfaces, inherited/added/lost hypotheses, source of truth, audit path, licensed conclusion, nonclaims, nearest countermodel, formalization posture, and classification.
6. The recall-oriented claim field `imported_laws` is not a precision-controlling transfer set.
7. The graph excludes unaudited lexical law edges and retains only source-statement, citation-navigation, typed bridge, scope, and wishlist-evidence edges.

## Consequences

- Local labels cannot masquerade as Foundations-law imports.
- Forty-one recall-only lexical law-tag edges are absent from the final graph; audited bridge edges remain.
- Large `UNKNOWN`, `PARTIAL`, and `ANALOGY` populations remain visible as later proof obligations.
- Citation identity never licenses exact theorem transfer.
