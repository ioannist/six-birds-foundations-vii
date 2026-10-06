#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest=list(csv.DictReader((ROOT/'corpus'/'paper_manifest.csv').open(newline='',encoding='utf-8')))
coverage=list(csv.DictReader((ROOT/'corpus'/'coverage.csv').open(newline='',encoding='utf-8')))
atoms=list(csv.DictReader((ROOT/'wishlists'/'atomic_requests.csv').open(newline='',encoding='utf-8')))
convergence=list(csv.DictReader((ROOT/'wishlists'/'convergence_groups.csv').open(newline='',encoding='utf-8')))
metrics={
  'delivery':'foundations-vii-read-01-canonical-map.zip',
  'git_tag':'read-step-01',
  'paper_roots':len(manifest),
  'source_files_frozen':sum(1 for p in (ROOT/'source').rglob('*') if p.is_file()),
  'paper_dependency_file_references':sum(int(r['source_files']) for r in manifest),
  'paper_source_bytes':sum(int(r['source_bytes']) for r in manifest),
  'recovered_plain_words':sum(int(r['plain_word_count']) for r in manifest),
  'coverage_states':dict(Counter(r['state'] for r in coverage)),
  'clusters':dict(Counter(r['cluster'] for r in manifest)),
  'survey_cards':sum(1 for _ in (ROOT/'notes'/'survey').glob('P*.md')),
  'deep_notes':sum(1 for _ in (ROOT/'notes'/'deep').glob('P*.md')),
  'primitive_roles':sum(1 for _ in csv.DictReader((ROOT/'registry'/'primitive_roles.csv').open(newline='',encoding='utf-8'))),
  'F_laws':sum(1 for _ in csv.DictReader((ROOT/'registry'/'F_laws.csv').open(newline='',encoding='utf-8'))),
  'E_laws':sum(1 for _ in csv.DictReader((ROOT/'registry'/'E_laws.csv').open(newline='',encoding='utf-8'))),
  'G_laws':sum(1 for _ in csv.DictReader((ROOT/'registry'/'G_laws.csv').open(newline='',encoding='utf-8'))),
  'no_go_theorems':sum(1 for _ in csv.DictReader((ROOT/'registry'/'no_go_theorems.csv').open(newline='',encoding='utf-8'))),
  'glossary_terms':sum(1 for _ in csv.DictReader((ROOT/'synthesis'/'canonical_glossary.csv').open(newline='',encoding='utf-8'))),
  'wishlist_atoms':len(atoms),
  'wishlist_source_counts':dict(Counter(r['source_code'] for r in atoms)),
  'wishlist_convergence_groups':len({r['convergence_group'] for r in convergence}),
  'version_families':1,
  'source_exceptions':2,
  'full_text_blocks':['P039'],
}
(ROOT/'generated'/'step1_metrics.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2,sort_keys=True))
