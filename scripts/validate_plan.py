#!/usr/bin/env python3
from pathlib import Path
import csv, sys
root=Path(__file__).resolve().parents[1]
errors=[]
with (root/'config/paper_catalog.csv').open(encoding='utf-8',newline='') as f:
    rows=list(csv.DictReader(f))
ids=[r['paper_id'] for r in rows]
if len(rows)!=58: errors.append(f'Expected 58 papers; found {len(rows)}')
if len(set(ids))!=58: errors.append('Paper IDs are not unique')
expected={f'P{i:03d}' for i in range(1,59)}
if set(ids)!=expected: errors.append(f'ID mismatch: missing={sorted(expected-set(ids))}, extra={sorted(set(ids)-expected)}')
orders=[int(r['reading_order']) for r in rows]
if sorted(orders)!=list(range(1,59)): errors.append('Reading order is not a permutation of 1..58')
for r in rows:
    for key in ['title','source_path','cluster','step_1_pass','step_2_pass','step_3_pass','foundations_vii_hooks']:
        if not r[key].strip(): errors.append(f"{r['paper_id']} has blank {key}")
with (root/'config/wishlist_catalog.csv').open(encoding='utf-8',newline='') as f:
    wishes=list(csv.DictReader(f))
if len(wishes)!=4: errors.append(f'Expected 4 wishlists; found {len(wishes)}')
with (root/'config/mandatory_coverage.csv').open(encoding='utf-8',newline='') as f:
    cov={r['coverage_class']:int(r['expected_count']) for r in csv.DictReader(f)}
expected_counts={'papers':58,'wishlists':4,'primitive_roles':6,'F_series_laws':52,'E_series_laws':16,'G_series_laws':13,'existing_no_go_theorems':8}
if cov!=expected_counts: errors.append(f'Mandatory coverage mismatch: {cov}')
print(f'papers={len(rows)} unique_ids={len(set(ids))} wishlists={len(wishes)}')
print('clusters:')
for c in sorted(set(r['cluster'] for r in rows)):
    print(f"  {c}: {sum(r['cluster']==c for r in rows)}")
if errors:
    print('VALIDATION: FAIL')
    for e in errors: print(' -',e)
    sys.exit(1)
print('VALIDATION: PASS')
