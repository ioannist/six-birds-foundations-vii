# Survey artifact/formalization disclosure audit

## Result

All **58** paper cards now contain a dedicated, source-located disclosure section. This is a Step-1 paper-side audit, not a declaration-level equivalence or local build claim.

- Formalization-status distribution: `CONDITIONAL_LEAN_SCHEMAS_EMPIRICAL_PREMISES_EXTERNAL`=1, `CORPUS_EVIDENCE_DISCUSSION_ONLY_NO_OWN_FORMALIZATION_APPENDIX`=1, `FINITE_RECOMPUTATION_EXPLICITLY_NOT_PROOF_ASSISTANT`=1, `FORMAL_OR_PROOF_ASSISTANT_COMPONENT_DISCLOSED`=47, `IN_HOUSE_LEAN_LADDER_PLUS_CONDITIONAL_EXTERNAL_CONTRACT`=1, `NO_DEDICATED_FORMAL_COMPONENT_LOCATED_AT_SURVEY_DEPTH`=4, `NO_DEDICATED_PROOF_ASSISTANT_COMPONENT_LOCATED`=2, `SOURCE_PACKAGE_BLOCKED`=1.
- Artifact-status distribution: `AUDITED_MACHINE_READABLE_ARTIFACT_PIPELINE`=1, `CODE_CONFIGURATIONS_AND_PROCESSED_RUN_ARTIFACTS_DISCLOSED`=1, `COMPUTATIONAL_AUDIT_OR_SUPPORT_ARTIFACTS_DISCLOSED`=36, `EXACT_FINITE_COMPUTATION_AND_VALIDATOR_EVIDENCE`=1, `NO_DEDICATED_ARTIFACT_COMPONENT_LOCATED_AT_SURVEY_DEPTH`=15, `NO_DEDICATED_PAPER_SPECIFIC_ARTIFACT_APPENDIX_LOCATED`=1, `SOURCE_PACKAGE_BLOCKED`=1, `SUPPORTING_COMPUTATIONAL_AND_AUDIT_EVIDENCE_ONLY`=1, `SUPPORTING_EMPIRICAL_PERIMETER_DOES_NOT_CARRY_PROOF`=1.
- Papers without a dedicated disclosure heading: P056, P039. Their card findings state the exact limitation.

## Anti-overread controls

- P003: conditional Lean schemas do not derive empirical artifact premises.
- P013: exact finite recomputation is explicitly not proof-assistant verification.
- P034: the in-house Lean ladder is separated from the conditional arithmetic contract and empirical perimeter.
- P038: support diagnostics do not enlarge the theorem package.
- P056: a philosophy synthesis inherits evidence grades from cited papers; it does not create a new formal artifact.
- P039: the full disclosure remains unauditable because the supplied source package is incomplete.

## Step-2 boundary

The audit records disclosure surfaces and high-risk status boundaries only. Exact theorem/declaration mappings, hypotheses, trust dependencies, imported-versus-owned status, execution results, and bridge judgments remain Step-2 records.
