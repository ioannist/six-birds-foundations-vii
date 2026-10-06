# FVII-SCI-01 finite reference world

The reference world has independent Python and Lean source implementations. Only the Python implementation was executable locally. Canonical JSON under the closed `FVII-SCI-01.3` schema freezes the input family before later scientific phases.

- Scenarios: 24/24 pass
- Countermodels: 27/27 pass
- Scenario result SHA-256: `2352bfd24dd32a433b4091af7fd53fb6b4f027410e7e519f993f35480550fad3`
- Countermodel result SHA-256: `14fad5e3e51b429f1afaa3810682b95aa5334db4ab2ec6b3bf3373f15553ccd6`
- Python regression/protocol tests: 25/25 pass
- Structural sections per scenario: all fifteen VII-owned object families plus append-only audit
- Closed-root, closed-section, closed-flag, and closed-nested-record mutation tests: pass
- Lean finite replay boundary: semantic flag/status/assertion projection, not full structural JSON parsing
- Deterministic canonical JSON and Lean-fixture regeneration: pass
- Lean runtime differential: pending external replay

Evidence grade: finite reference assay over exactly 24 frozen scenarios and 27 frozen countermodels. It has no force outside that declared family without a separate theorem.
