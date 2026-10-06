# G9-L1 Verdict - Rule 184 Defect Evacuation

## Hypothesis
Rule 184 on an exact finite ring evacuates blocked-car `11` defects below density `1/2`, evacuates dual blocked-hole `00` defects above density `1/2`, and reaches the alternating critical regime at density `1/2`. Each evacuated tail should admit an exact recurrence-with-displacement certificate.

## Outcome
PASS. Exact Rule 184 was run on a ring of length `2000` for `5` exact density settings with max step budget `8000` and total wall time `3.007608` seconds.
All tested regimes reached the predicted evacuated defect census and all recurrence certificates were checked over `128` consecutive tail times.

| density | cars/ring | regime | evacuated measure | evac step | tau | d | windows | final 11 | final 00 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `3/10` | `600/2000` | subcritical | `adjacent_11_blocked_cars` | 11 | 1 | 1 | 128 | 0 | 800 |
| `2/5` | `800/2000` | subcritical | `adjacent_11_blocked_cars` | 26 | 1 | 1 | 128 | 0 | 400 |
| `1/2` | `1000/2000` | critical | `adjacent_11_plus_adjacent_00_alternation_defects` | 999 | 1 | 1 | 128 | 0 | 0 |
| `3/5` | `1200/2000` | supercritical | `adjacent_00_blocked_holes` | 62 | 1 | -1 | 128 | 400 | 0 |
| `7/10` | `1400/2000` | supercritical | `adjacent_00_blocked_holes` | 14 | 1 | -1 | 128 | 800 | 0 |

## Defect-Census Finding
For `rho < 1/2`, adjacent `11` blocked-car pairs evacuate to zero. For `rho > 1/2`, the measure that evacuates to zero is the dual adjacent `00` blocked-hole count; adjacent `11` pairs remain in the high-density jammed background and are not the evacuated supercritical defect measure. At `rho = 1/2`, both adjacent `11` and adjacent `00` counts reach zero, giving the alternating critical pattern.

## Scope Note
This is a deterministic finite-ring calibration for Rule 184 only. It does not construct Langton's ant or any other G9 instance, and it does not prove the abstract G9 schemas in Python; the lab supplies a concrete exact census and transporter-record exhibit.

## Surprise
None.

## Implication
The run supplies concrete transporter records: subcritical particles move with displacement `+1`, supercritical holes move with displacement `-1`, and the critical alternating pattern has an exact nonzero shift recurrence. These are positive-schema calibration instances, not negative unbounded-creation witnesses.

This result exercises `SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.TransportData`, `SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.CertifiedTransportRegime`, and `SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.certified_transport_regime_of_assigned_nonzero` for the concrete Rule 184 ring instance. The evacuated census is consistent with `SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport.census_excludes_unbounded_creation`, but this lab instantiates the positive transport-certification schema rather than the negative unbounded-creation exclusion theorem.
