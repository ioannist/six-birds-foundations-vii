# Formalization evidence ladder and fidelity axes

This file is the controlling Step-1 rule for the words **formalized**, **mechanized**, **verified**, and **available for reuse**. A paper-side status, a Lean declaration, a locally present file, a resolved import graph, a kernel build, and a finite laboratory run are different facts. None may be substituted for another.

## Axis A — mathematical claim grade

Preserve the paper's grade independently of the implementation: theorem, schema, calibration-anchored schema, conditional classification, mechanized finite result, interpretive corollary, proposal, nonclaim, or open problem. A Lean theorem declaration does not automatically promote a paper-side schema.

## Axis B — statement fidelity

| Fidelity | What it licenses | What it does not license |
|---|---|---|
| `DIRECT_DERIVATION` | The Lean theorem derives the paper statement at the declared scope. | Broader prose, empirical realization, or an unstated bridge. |
| `NARROWED_OR_PARAMETRIC` | A genuine proof of a narrower or parameterized statement. | The full paper statement without the narrowing disclosure. |
| `CONDITIONAL_CLASSIFICATION` | Consequences follow from complete, linked, host-supplied evidence. | Discovery or construction of those host certificates. |
| `PROJECTION_OR_WRAPPER` | A proof-carrying record is projected or a guarded implication is applied. | An independent derivation of the wrapped premise. |
| `TYPED_MIRROR` | Types, constructors, statuses, and malformed-case rejection are checked. | The mathematical theorem mirrored by the types. |
| `PAPER_PROOF_ONLY` | The result is proved in the paper but not in the supplied Lean surface. | A mechanization claim. |
| `INTERPRETIVE_ONLY` | The statement is interpretation or outlook. | Theorem-grade inheritance. |

## Axis C — locally available verification state

| Code | State | Exact meaning |
|---|---|---|
| `R0_PAPER_REPORTED` | Paper disclosure only | The source paper reports a formal artifact. The artifact need not be present here. |
| `R1_ASSET_PRESENT` | File available | The relevant source file is present in this repository and covered by provenance hashes. |
| `R2_STATIC_INDEXED` | Lexically indexed | Modules, declarations, imports, placeholder tokens, and trust declarations were statically indexed. This is not elaboration. |
| `R3_IMPORT_RESOLVED` | Local import graph resolved | Every local import edge in the supplied project resolves to a present module. This is not a kernel check. |
| `R4_KERNEL_COMPILED` | Locally rebuilt by Lean | The exact local project compiled under its pinned toolchain. This state is **not reached in the current environment** because Lean/Lake is unavailable. |
| `R5_RUNTIME_VALIDATED` | Tests/labs rerun locally | The named finite or computational checks were executed locally. This is evidence for those fixtures, not a theorem proof. |

These states are cumulative only within one exact artifact. A paper can be `R0` while a narrower imported subset is `R1–R3`. Runtime validation is orthogonal to theorem fidelity; a passing laboratory does not upgrade a schema into a theorem.

## Current repository-wide ruling

- Foundations I, II, III, fourteen Foundations IV rows, all sixteen Foundations V E laws, and all thirteen Foundations VI law modules are present and statically indexed through `R3`.
- The Foundations V archive supplies the complete D1--D6 / E1--E16 authored theorem base. The immutable upstream root and 1,141-row manifest omit the already-landed E16 module/declarations; VII-owned import and manifest adapters complete discoverability without editing upstream files.
- No imported Lean project reached `R4` in this environment. The repository must say **source/import graph checked**, not **compiled here**.
- Sixty-two locally available Foundations VI lab tests and 317 non-E15 Foundations V tests reached `R5`; the E16 standalone sweep also passed 69/69 comparisons. Three G11 tests require unavailable PySAT, while the 74-test E15 file exceeded the local 900-second replay limit. These runtime facts do not alter paper grades.

## Mandatory citation form for later work

A later claim that reuses prior Lean must state all four items:

1. paper-side claim grade;
2. exact Lean module/declaration and fidelity;
3. trust-base or host-supplied premises;
4. local verification state (`R0`–`R5`).

The phrase “already mechanized” is forbidden unless these four fields are available.
