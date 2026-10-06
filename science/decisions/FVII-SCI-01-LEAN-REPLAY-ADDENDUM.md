# FVII-SCI-01 Lean replay execution addendum

**Date:** 2026-07-26
**Status:** accepted execution constraint

The controlling phase plan originally required a local Lean 4.28.0 build as a hard exit gate. During execution, the owner explicitly authorized the least-resistance path: a different Lean version may be selected if useful, and lack of a locally installable Lean toolchain is not a blocker provided the repository retains exact external compilation directions and does not claim a kernel build that did not occur.

This addendum changes only the execution gate. It does not lower the source discipline: VII-owned Lean contains no `sorry`, `admit`, new `axiom`, `opaque`, or `unsafe` declaration; imported Foundations V/VI source remains immutable; theorem-grade status remains pending until external kernel replay succeeds.
