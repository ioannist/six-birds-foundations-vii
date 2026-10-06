#!/usr/bin/env python3
"""Verify SHA256SUMS for all non-Git repository files."""
from __future__ import annotations
import hashlib, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SUMS=ROOT/'SHA256SUMS'
SKIP_DIRS={'.git','__pycache__','.pytest_cache','.ipynb_checkpoints','.venv','.lake'}
SKIP_SUFFIXES={'.pyc','.pyo','.olean','.ilean'}

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()
errors=[]; count=0
for line in SUMS.read_text(encoding='utf-8').splitlines():
 if not line: continue
 m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line)
 if not m:
  errors.append(f'malformed: {line}'); continue
 expected,rel=m.groups(); path=ROOT/rel; count+=1
 if not path.exists(): errors.append(f'missing: {rel}')
 elif sha256(path)!=expected: errors.append(f'mismatch: {rel}')
candidates=[
 p for p in ROOT.rglob('*')
 if p.is_file()
 and not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)
 and p.suffix not in SKIP_SUFFIXES
 and p!=SUMS
]
# Git-ignored files (e.g. .codex/logs, .codex/threads) are machine-local and are
# absent from a clean checkout, so the ledger must not record them. Mirrors
# build_delivery_manifest.py.
_ignored=set()
if candidates:
 _r=subprocess.run(['git','check-ignore','--stdin'],cwd=ROOT,text=True,capture_output=True,check=False,
                   input='\n'.join(p.relative_to(ROOT).as_posix() for p in candidates))
 if _r.returncode in (0,1):
  _ignored={ln for ln in _r.stdout.splitlines() if ln}
actual={str(p.relative_to(ROOT)) for p in candidates if p.relative_to(ROOT).as_posix() not in _ignored}
listed={line.split('  ',1)[1] for line in SUMS.read_text(encoding='utf-8').splitlines() if '  ' in line}
if actual!=listed: errors.append(f'ledger set mismatch: missing={sorted(actual-listed)[:10]} extra={sorted(listed-actual)[:10]}')
if errors:
 print('DELIVERY HASH VALIDATION: FAIL')
 for e in errors: print(' -',e)
 sys.exit(1)
print(f'DELIVERY HASH VALIDATION: PASS ({count} files)')
