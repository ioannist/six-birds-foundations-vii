# G13-L1 Verdict - Apollonian Curvature Census

## Hypothesis
The baseline packing `(-1,2,2,3)` should match the stated mod-24 admissible classes without any claimed reciprocity obstruction. The packing `(-6,11,14,15)` should have the same admissible residue type while avoiding every curvature in the published reciprocity-obstructed families `2n^2`, `3n^2`, and `6n^2` within the computational bound.

## Outcome
PASS. Exact Descartes-reflection BFS was run for both root quadruples to curvature bound `300000`.
Every generated quadruple was checked against Descartes' identity during generation. Both generated positive-curvature sets stayed inside the expected admissible classes `[2, 3, 6, 11, 14, 15, 18, 23] mod 24`.
For `(-6,11,14,15)`, the reciprocity-family check found `0` hits among all generated curvatures in `2n^2`, `3n^2`, and `6n^2` up to the bound.

## Scope Note
This is a finite exact-integer orbit census. It does not reprove Bourgain-Kontorovich density-one saturation, and it does not reprove, extend, or contradict Haag-Kertzer-Rickards-Stange. It checks that the generated finite orbits are consistent with the cited reciprocity obstruction for the corrected packing.
`(-1,2,2,3)` is treated only as the clean baseline from `THEOREMS.md`: its residual missing set is case (iv) uncertain within this bounded census, not a reciprocity obstruction. `(-6,11,14,15)` supplies the concrete case (iii) reciprocity-obstructed exhibit through the three checked quadratic families.
The design-spec target bound was `10^6`; this checked-in canonical run deliberately uses `300000` instead because feasibility probing showed steep cost scaling, so the larger bound was not forced in this landing pass.

## Baseline Packing

### `baseline (-1,2,2,3)`

Root quadruple: `(-1, 2, 2, 3)`.
Curvature bound: `300000`.
States explored: `2851863`.
Positive curvatures hit: `99939`.
Residues hit mod 24: `(2, 3, 6, 11, 14, 15, 18, 23)`.
Residue violations: `0`.
Admissible curvatures up to bound: `100000`.
Missing admissible curvatures: `61`.
First missing admissible values: `[78, 159, 207, 243, 246, 342, 435, 603, 711, 834, 1422, 1923, 2010, 2022, 2175, 2319, 2454, 2718, 2766, 3150, 3402, 3510, 3711, 3774, 4167]`.
Last missing admissible values: `[10638, 10923, 11295, 12063, 12534, 13154, 13206, 13806, 16311, 16515, 18051, 19815, 20406, 21135, 23175, 24270, 28323, 32670, 41655, 42186, 45258, 48075, 55878, 68055, 97287]`.
Elapsed seconds: `35.108017`.

Coverage checkpoints:

| bound | admissible | hit | missing | coverage |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 34 | 33 | 1 | 33/34 (0.970588) |
| 1000 | 334 | 324 | 10 | 324/334 (0.970060) |
| 10000 | 3334 | 3299 | 35 | 3299/3334 (0.989502) |
| 100000 | 33334 | 33273 | 61 | 33273/33334 (0.998170) |
| 300000 | 100000 | 99939 | 61 | 99939/100000 (0.999390) |

Reciprocity-family checks:

No reciprocity-family check was assigned to this baseline packing.

## Reciprocity-Obstructed Packing

### `reciprocity (-6,11,14,15)`

Root quadruple: `(-6, 11, 14, 15)`.
Curvature bound: `300000`.
States explored: `548885`.
Positive curvatures hit: `96839`.
Residues hit mod 24: `(2, 3, 6, 11, 14, 15, 18, 23)`.
Residue violations: `0`.
Admissible curvatures up to bound: `100000`.
Missing admissible curvatures: `3161`.
First missing admissible values: `[2, 3, 6, 18, 27, 30, 38, 39, 50, 54, 62, 63, 66, 75, 83, 87, 90, 98, 99, 111, 114, 126, 135, 138, 146]`.
Last missing admissible values: `[288675, 288774, 289278, 290163, 290286, 290307, 290322, 291702, 291782, 291843, 291942, 292143, 292535, 293046, 293378, 293478, 293907, 294234, 295218, 296439, 296450, 296502, 297675, 298374, 299538]`.
Elapsed seconds: `6.599874`.

Coverage checkpoints:

| bound | admissible | hit | missing | coverage |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 34 | 15 | 19 | 15/34 (0.441176) |
| 1000 | 334 | 211 | 123 | 211/334 (0.631737) |
| 10000 | 3334 | 2649 | 685 | 2649/3334 (0.794541) |
| 100000 | 33334 | 31084 | 2250 | 31084/33334 (0.932501) |
| 300000 | 100000 | 96839 | 3161 | 96839/100000 (0.968390) |

Reciprocity-family checks:

| family | values checked | hits found | first checked values |
| --- | ---: | ---: | --- |
| `2n^2` | 387 | 0 | `[2, 8, 18, 32, 50, 72, 98, 128, 162, 200, 242, 288]` |
| `3n^2` | 316 | 0 | `[3, 12, 27, 48, 75, 108, 147, 192, 243, 300, 363, 432]` |
| `6n^2` | 223 | 0 | `[6, 24, 54, 96, 150, 216, 294, 384, 486, 600, 726, 864]` |

## Surprise
None.

Traceability: this finite census is a case-enumeration exhibit for G13. It does not discharge `SixBirdsFoundationsVI.Laws.G13ThinOrbitSaturation.relative_density_theorem`, because the imported sublinear exceptional bound and positive-density target theorem are not proved here. The `(-6,11,14,15)` obstruction check is a concrete finite consistency check for `SixBirdsFoundationsVI.Laws.G13ThinOrbitSaturation.reciprocity_compatibility_observation`: an infinite reciprocity record can coexist with density-one saturation when its count is negligible, but negligibility itself remains imported instance content.
