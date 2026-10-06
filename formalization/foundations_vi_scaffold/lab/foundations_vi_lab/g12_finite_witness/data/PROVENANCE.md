# Data provenance — Heule 826-vertex unit-distance graph

`heule_826.vtx` and `heule_826.edge` were fetched verbatim by the manager on 2026-07-07 from Marijn
Heule's personal page:

- `https://www.cs.utexas.edu/~marijn/CNP/826.vtx` (826 vertex coordinates, Mathematica/Wolfram-syntax
  algebraic expressions using `Sqrt[n]`, some with non-integer radicands e.g. `Sqrt[11/3]`)
- `https://www.cs.utexas.edu/~marijn/CNP/826.edge` (DIMACS-edge-format graph: header `p edge 826 4273`,
  then `e i j` lines, 1-indexed)

This is the "G3" intermediate graph from the Polymath16 project's search for small 5-chromatic
unit-distance graphs in the plane (Hadwiger-Nelson problem), predating the eventual smallest known
record — Parts's 509-vertex graph (arXiv:2010.12665). A dedicated literature-verification research pass
confirmed:

- The current smallest known published 5-chromatic unit-distance graph is 509 vertices / 2442 edges
  (Jaan Parts, arXiv:2010.12665, also *Geombinatorics* 29/4 (2020), 137-166), corroborated independently
  by the Hadwiger-Nelson-problem Wikipedia article citing Mixon's 2021 Polymath16 wrap-up. Raw
  coordinate/edge data for this specific 509-vertex record was not found publicly archived (checked
  arXiv ancillary files for arXiv:2010.12665: 404; checked the Polymath16 wiki's linked Dropbox folder).
- **Correction (2026-07-07, external review caught this):** an earlier version of this note claimed no
  raw coordinate data exists for the 553-vertex or 529-vertex Heule graphs either. That claim was wrong —
  it missed Heule's own `github.com/marijnheule/CNP-SAT` repository (distinct from his personal
  `cs.utexas.edu/~marijn/CNP/` page, which is what the original research pass checked), which publicly
  hosts matched `.vtx`/`.edge` coordinate-and-edge data for `510`, `517`, `529`, `553`, `610`, `633`,
  `803`, `826`, and `874` vertices, plus **public DRAT proof certificates** (`proof/*-4-sbp.drat`) for the
  `517`, `529`, `553`, `610`, `633`, and `803` 4-coloring UNSAT instances — independently confirmed by the
  manager by querying the GitHub API directly. `826` (used by this lab) does **not** have a DRAT
  certificate in that repository; nor does `510` or `874`. The 509-vertex Parts record itself still has no
  known public raw-data bundle.
- This 826-vertex graph was chosen over the 1585-vertex de Grey original for computational tractability
  (SAT-solving a real geometric 4-coloring instance scales steeply with size; see
  `lab/results/G12-L1/verdict.md` for the actual feasibility probing and timing). In hindsight, given the
  above correction, a smaller graph with an existing public DRAT certificate (e.g. `517` or `529`) would
  have let this lab additionally proof-check the UNSAT result rather than merely solver-verify it; this
  lab does not attempt that upgrade and the choice of `826` remains a valid calibration exhibit regardless.
- This specific lab's non-4-colorability determination (for the `826`-vertex instance, which has no public
  DRAT certificate) is a solver-verified result (SAT solver returns UNSAT), not a separately proof-checked
  one — disclosed honestly in the verdict. This is a fact about the `826` instance specifically, not a
  claim that no such certificate exists anywhere in this literature stream (corrected above).

Citation for the construction lineage: de Grey, "The Chromatic Number of the Plane Is at least 5,"
*Geombinatorics* 28, 5-18, 2018, arXiv:1804.02385; Heule, "Computing Small Unit-Distance Graphs with
Chromatic Number 5," arXiv:1805.12181; Polymath16 project wiki and collaborative search materials;
Parts, arXiv:2010.12665.
