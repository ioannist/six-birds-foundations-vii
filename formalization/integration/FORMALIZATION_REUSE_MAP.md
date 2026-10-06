# Foundations VII formalization reuse map

## 1. Controlling posture

The imported scaffold is not merely a library of convenient lemmas. It is a typed proof architecture with linked theorem prose, mechanized declarations, finite models, gate notes, and trust records. Foundations VII should reuse that architecture in four ways:

1. import exact prior definitions rather than restating them;
2. prove adapters when VII objects are not definitionally identical to prior objects;
3. retain theorem/schema/calibration grades and trust assumptions;
4. use prior countermodels and labs when testing proposed VII statements.

The active import surface is `formalization/lean/FoundationsVII/PriorScaffold.lean`. It introduces no VII definitions and imports the full prior base selected below. `FoundationsVII.PriorFoundationsVComplete` is the narrower complete Foundations V entry point; it explicitly adds the landed E16 module omitted by the immutable upstream root.

## 2. Direct reuse surfaces

### A. Formation, closure, and packaging

**Modules**

- `ClosureLadder.Basic`
- `ClosureLadder.IdempotentEndo`
- `ClosureLadder.Packaging`
- `ClosureLadder.MetaPackaging`
- `SixBirdsMetaMath.FoundationsICompat`
- `SixBirdsMetaMath.Main.LegalQuotient`
- `SixBirdsMetaMath.Main.LayerDissolving`
- `SixBirdsMetaMath.Main.XiInterface`

**VII use**

These are the first candidates for formalizing theory packages, package closure, strict extension, legal quotients, contact-produced objects, and any distinction between closure of a carrier and closure of a package containing records/audits.

**Boundary**

Do not equate idempotent closure, package survival, strictness, endogenous execution, or realization. The Step-1 three-certificate separation remains controlling.

### B. Typed primitive roles and admissibility

**Modules**

- `SixBirds.Roles`
- `SixBirds.FATCD`
- `SixBirds.Admissibility`
- `SixBirds.Decomposition`
- `SixBirds.ScopedExactSix`
- `SixBirds.SemanticTests`
- `SixBirds.IntegratedStress`
- `SixBirds.LowerBounds`
- `SixBirds.UpperBound`

**VII use**

Use these modules to keep contact, join, admission, reachability, audit, and directionality channels typed. They supply the established P1–P6 discipline, exact-six scoping, non-collapse checks, and admissibility/decomposition surfaces.

**Boundary**

Exact-six is scoped, existential, and non-unique. It does not imply that every VII construction activates six roles or that a candidate join is lawful merely because six labels can be assigned.

### C. BirdInt and finite audited interaction calculus

**Modules of highest likely leverage**

- `SixBirdsIII.Domain`
- `SixBirdsIII.Records`
- `SixBirdsIII.CoreInteraction`
- `SixBirdsIII.Definability`
- `SixBirdsIII.Completion`
- `SixBirdsIII.CompletionExamples`
- `SixBirdsIII.Strictness`
- `SixBirdsIII.Defects`
- `SixBirdsIII.Promotion`
- `SixBirdsIII.InstrumentClaims`
- `SixBirdsIII.RotatingAudit`
- `SixBirdsIII.TopDownChannel`
- `SixBirdsIII.GraphCohomology`
- `SixBirdsIII.HighStructure`
- `SixBirdsIII.AbstractInterpretation`
- `SixBirdsIII.ModelRealizations`
- `SixBirdsIII.FiniteMaps`
- `SixBirdsIII.FiniteProbability`

**VII use**

This is the main inherited substrate for typed theory domains, directed cells, pair observables, promotion and claim records, defects, completion order, strictness, top-down channels, route/cohomological obstructions, and finite realization. Candidate contact and join certificates should preferentially be expressed as extensions or adapters over these records rather than as unrelated structures.

**Boundary**

BirdInt is not already a theory-join algebra. A valid VII join will need new definitions and proofs showing how two partially accessible theory domains inhabit or extend the existing typed state. Completion noncommutativity and graph holonomy can support order-obstruction statements, but they do not by themselves establish contact, novelty, or directionality.

### D. Access, quotient, transport, and repair laws

The imported Foundations IV surface contains 14 mechanized F-law modules:

- F2 `DescentRepair`
- F3 `HolonomyMemoryRepair`
- F4 `LocalGlobalObstruction`
- F6 `NoNeedles`
- F7 `SufficiencyClosure`
- F10 `Quotientality`
- F11 `Adequacy`
- F12 `NoFreeDistinction`
- F13a `HiddennessNormalForm`
- F19 `ObjectPersistence`
- F27 `ConservationAsOrbitDescent`
- F34 `InformationLoss`
- F40 `Anomaly`
- F49 `CommonSourceNonlocal`

**VII use**

- **Access and shared visibility:** F10, F11, F13a.
- **Strict distinction and pricing:** F12 and F6.
- **Contact transport and repair:** F2 and F4.
- **Route/order residues:** F3 and F40.
- **Retention and loss across a join:** F19 and F34.
- **Common origin versus actual interaction:** F49.
- **Closure/sufficiency checks:** F7.
- **Conserved quantities along contact routes:** F27.

`prior_law_formalization_coverage.csv` records exact files and declarations. Ten of these modules are also covered by the supplied Foundations VI dependency audit; four are present but were not dependencies of VI and therefore require a fresh paper/Lean comparison before being used as exact bridges.

**Boundary**

The F4 mechanization abstracts local families without the finiteness language used in some prose. F13a contains the only inherited project-specific trust-base axiom and five opaque Paper-7 substrate constants. Those limitations must travel with any VII theorem that imports them.

### E. Endogenous closure, cognition, and institution laws

The supplied Foundations V archive contains the complete authored D/E theorem base:

- six definitional modules covering D1--D6;
- fifteen law modules covering E1--E16, with E6 and E9 sharing `E6E9PricedAccess`;
- 1,261 authored declarations, including 187 theorems;
- gate, example, prediction, result, test, and finite-sweep artifacts for every E law.

**Highest-leverage modules for VII**

- `SixBirdsFoundationsV.Definitional.RepairJoin` — candidate repair/join packaging and evidence linkage.
- `SixBirdsFoundationsV.Definitional.PredictiveSurplus` — predictive distinctions beyond current access.
- `SixBirdsFoundationsV.Definitional.CarriedRecord` — provenance-bearing records across closure.
- `SixBirdsFoundationsV.Definitional.ESystem` and `ClosedLoopScope` — endogenous-system and scope discipline.
- `SixBirdsFoundationsV.Definitional.ProbeEconomy` — priced observation and audit resources.
- E1--E5 — internalization, bounded reflexivity, self-maintaining reclosure, repair compilation, and reclosure collapse.
- E6/E9 — priced access and shared probe-economy constraints.
- E7--E8 — alarms, controls, and their resource cost.
- E10--E14 — cognitive demarcation, institutional rewrite, individuation, repair transport, and reconsolidation.
- E15--E16 — offline reclosure, route-sensitive repair capacity, and adaptability classification.

**VII use**

These modules are likely to supply exact types and conditional theorems for admission, carried evidence, endogenous versus theorist-triggered extension, enablement, priced observer access, repair transport, institution-level rewrite, and route-sensitive adaptation. `foundations_v_e_law_traceability.csv` links every E law to its exact module, declaration census, theorem ledger, gate, example, predictions, results, and executable evidence.

**Import repair**

The immutable upstream root imports 20 of 21 authored submodules and omits the already-landed `E16Adaptability`; the upstream 1,141-row manifest likewise omits E16's 120 declarations. Foundations VII must import `FoundationsVII.PriorFoundationsVComplete` (or E16 explicitly), and should use the 1,261-row `foundations_v_completed_manifest.toml` for declaration lookup. These are discoverability repairs, not new theorems.

**Boundary**

Many E theorems are conditional classifications over complete, linked, host-supplied evidence. They do not construct honest biological, cognitive, social, or institutional certificates. E7.1, E12.1, and named cross-law bridges remain interpretive or open as recorded in the paper. Module presence, finite sweeps, and type correctness must not upgrade those claims.

### F. Dynamic and history-sensitive laws

All thirteen G-law files are present and marked `landed_step8` in the supplied manifest. Their paper grades remain heterogeneous:

- theorem or theorem component: G1(a), G2, G3, G8, G10, G11, G12;
- schema or schema component: G1(b), G4, G6, G13;
- calibration-anchored schema: G5, G7, G9.

**Likely VII reuse**

- G1–G3: currencies, accumulated resources, escrow, and solvency for contact/admission processes.
- G4–G7: moving covers, horizon limits, endogenous needles, adversarial reachability, and liveness/obstruction distinctions.
- G8–G10: order independence, transport, persistence, and loss across evolving interfaces.
- G11–G13: global anti-symmetry, finite witness radiation, and saturation/density effects.

Every row in `g_law_traceability.csv` links the law to its theorem ledger, Lean module, gate note, example note, lab package, tests, recorded results, and paper source.

**Boundary**

A landed Lean schema is not an unconditional theorem about every VII model. The precise hypotheses in the G module and the theorem/schema grade in `THEOREMS.md` must be inherited together.

### G. Finite-model and regression scaffold

The imported `lab/` tree supplies:

- reusable package and test layout;
- exact finite models and fixtures;
- SAT/CNF encodings and data assets;
- recorded run JSON and verdict files;
- 15 regression-test files;
- a law-by-law pattern for detector, positive case, null, countermodel, and gate recording.

Foundations VII should reuse this structure for the Two-Theory World, bootstrap obstruction, pseudo-join controls, obstructed joins, construction-order experiments, and certified non-interaction. New VII labs should live outside the immutable subtree but mirror its evidence-chain conventions.

## 3. Coverage by prior Foundations layer

| Layer | Imported mechanized surface | Reuse posture |
|---|---|---|
| Foundations I | closure ladder, packaging, compatibility and shared meta-math interfaces | direct import, with adapters for VII package types |
| Foundations II | P1–P6 role system, FATCD, admissibility, exact-six and stress tests | direct import; preserve scoped typing and non-collapse rules |
| Foundations III | full 24-module BirdInt/interaction tree | principal host for VII typed state and records |
| Foundations IV | 14 F-law normal-form modules | direct or bridged reuse after statement/hypothesis comparison |
| Foundations V | complete D1–D6 / E1–E16 authored theorem base; 22 authored modules, 1,261 declarations, gates/sweeps/labs | direct or bridged reuse through the complete V wrapper; preserve conditional evidence assumptions and open bridges |
| Foundations VI | all 13 G-law modules, theorem ledger, gates, labs and results | direct reuse with original grade/hypotheses retained |

## 4. What must remain new in Foundations VII

The imported base does not yet define:

- a general partial theory domain with separate expressible/present/reachable/occurrent levels;
- evidenced contact between two theory packages;
- a strict join certificate separating common refinement from genuine interaction;
- bootstrap/admission/reachability certificates;
- enablement versus descent as separately typed relations;
- a general join-obstruction or no-free-join theorem;
- observer occupancy/pricing for contact;
- a multi-domain interaction holonomy object whose relation to directionality is formally controlled.

Those are genuine VII obligations. The prior scaffold constrains and supports them; it does not discharge them by name similarity.

## 5. Step-2 bridge protocol

Before a Step-2 claim is marked mechanized or reusable:

1. locate the source paper statement;
2. locate candidate rows in `cumulative_lean_theorems.csv` for theorem-first search, then `cumulative_lean_declarations.csv` and the archive-specific indexes when definitions or provenance matter;
3. compare exact Lean parameters, hypotheses, conclusion, and namespace;
4. inspect `prior_law_formalization_coverage.csv` plus the F/E/G disclosure matrices for audit status and caveats;
5. for Foundations V, check `foundations_v_completed_manifest.toml`, the E-law traceability row, and whether the import requires the E16-complete wrapper;
6. record inherited axioms/opaque constants and host-supplied certificates from the transitive dependency path;
7. classify the bridge as exact, narrowed, strengthened, conditional, analogy-only, or blocked;
8. cite the appropriate gate/example/lab artifacts for E and G laws;
9. retain explicit nonclaims and nearest countermodels.

Module presence alone is never sufficient evidence of an exact theorem bridge.

## 6. Active build surface

The future extension project is:

```text
formalization/lean/
├── lakefile.toml
├── lean-toolchain
├── FoundationsVII.lean
└── FoundationsVII/
    ├── PriorScaffold.lean
    └── PriorFoundationsVComplete.lean
```

The expected command is `cd formalization/lean && lake build`. At this pre-Step-2 stage the project contains no VII declarations. Local compilation could not be rerun because this environment has no Lean/Lake executable; static module resolution is complete and records zero unresolved imports.
