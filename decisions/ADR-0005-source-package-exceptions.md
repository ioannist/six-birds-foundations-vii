# ADR-0005 — Incomplete source packages and converter failures

**Status:** accepted for Step 1.

A failed converter does not reduce a complete TeX source to an unread paper, and an incomplete source package must not be made to look complete by inference. P020 is read from its full frozen TeX with a conservative plain-text fallback. P039 is represented only at the depth supported by its root stub: abstract, declarations, and include map. The missing 18 included files and bibliography are an explicit `BLOCKED_FULL_TEXT` condition for Step 2. No web copy, OCR reconstruction, or guessed section content may be substituted without a separate provenance decision.
