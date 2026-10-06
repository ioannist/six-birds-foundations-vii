# ADR-0010 — One canonical Step-2 claim-ID space

**Status:** accepted  
**Date:** 2026-07-26

## Context

Step 2 requires all 58 paper roots to be read at claim/proof/nonclaim depth and reused by registries, bridges, wish-list links, application maps, formalization mappings, dossiers, and the dependency graph. Independent extraction pipelines would create competing IDs, duplicate records, and reference drift.

The corpus also contains heterogeneous statement surfaces: ordinary theorem environments, custom principles and schemas, named gate/verdict/result sections, explicit prose definitions, scope statements, nonclaims, and open/deferred items.

## Decision

1. `scripts/build_step2_claims.py` is the sole producer of canonical IDs of the form `Pxxx-Cnnnn`.
2. IDs are sequential and stable within each paper under the frozen source snapshot.
3. Four extraction lanes are retained separately: composite abstract, explicit formal environment, named result/gate surface, and explicit prose definition/result/scope/nonclaim/open surface. Abstract-only nonclaims, scope boundaries, and open obligations enter the explicit-prose lane as typed components.
4. Exact TeX, original and expanded line ranges, root/tree hashes, and source-completeness state are stored with every record.
5. Every paper receives exactly one source-located composite abstract thesis, including section-form abstracts. Composite abstracts are navigation claims and cannot replace component theorem records.
6. Downstream builders consume `registry/claims.jsonl`; they may not independently extract or renumber claims.
7. P039 receives two abstract-level records—the composite thesis and its explicit nonclaim—because its eighteen included TeX files and bibliography are absent. Missing content is not reconstructed.

## Consequences

- All Step-2 artifacts resolve to one 2,821-record claim body.
- Per-paper JSONL files are exact partitions, not alternate corpora.
- Dossiers can be rebuilt deterministically from canonical IDs.
- Claim normalization aids navigation but does not supersede frozen TeX.
- A source change would require an explicit new corpus version and ID-impact audit.
