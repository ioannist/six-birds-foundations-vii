# FVII-SCI-05 theorem dependency and trust audit

- Public theorems: 732
- Static theorem-reference rows: 732
- Static theorem-reference edges: 943
- Static axiom-free-core candidates: 625
- Static inherited-trust-reachable theorems: 0
- Explicit inherited trust declarations: 6
- Adapter contracts: 30
- Kernel status: `PASS`

`science/traceability/final_theorem_dependency_graph.graphml` and `final_module_import_graph.graphml` provide machine-readable DAGs. `formalization/lean/FoundationsVII/Trust/PrintAxiomsFinal.lean` contains one `#print axioms` command for every public theorem.

The axiom-free-core classification is backed by executed `#print axioms` receipts.
