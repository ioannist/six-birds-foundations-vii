# ADR-0004 — P040/P058 version-family handling

**Status:** unresolved canonical choice; controlled handling accepted.

P040 and P058 have normalized five-word-shingle Jaccard similarity 0.687845 and share the SAU theorem stack, examples, and architecture. Their filenames and internal titles are crossed, and the texts contain substantive editorial and theorem-presentation deltas. Neither is silently discarded. They are represented as one version family with two stable IDs and hashes; downstream synthesis cites the shared result family only when both support it and records variant-specific wording separately.
