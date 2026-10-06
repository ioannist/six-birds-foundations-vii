# No-go theorem / prior-scaffold correspondence

The no-go paper does not supply a dedicated Lean library for all eight fronts. This table records only conservative correspondences to reusable earlier scaffold declarations. `MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION` and `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` are not claims that the complete no-go theorem has already been mechanized.

| No-go | Source claim | Correspondence | Prior declarations | Exact match? |
|---|---|---|---|---|
| `NG_ARROW_DPI` | `P032-C0005` | `NO_MATCH` | none | hyp=None, concl=None |
| `NG_FORCE_FOREST` | `P032-C0009` | `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` | `SixBirdsIII.forest_no_drive` | hyp=False, concl=False |
| `NG_FORCE_NULL` | `P032-C0011` | `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` | `SixBirdsIII.exact_form_null_drive` | hyp=False, concl=False |
| `NG_LADDER_BOUNDED_INTERFACE` | `P032-C0019` | `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` | `SixBirdsIII.fixed_interface_definability_bound` | hyp=False, concl=False |
| `NG_LADDER_IDEM` | `P032-C0017` | `MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION` | `SixBirdsIII.idempotent_saturation` | hyp=False, concl=False |
| `NG_MACRO_CLOSURE_DEFICIT` | `P032-C0013` | `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` | `SixBirdsIII.finite_markov_closure_deficit` | hyp=False, concl=False |
| `NG_OBJECT_CONTRACTIVE` | `P032-C0015` | `PAPER_DISCLOSED_ASSET_NOT_IMPORTED` | none | hyp=False, concl=False |
| `NG_PROTOCOL_TRAP` | `P032-C0007` | `NO_MATCH` | none | hyp=None, concl=None |
