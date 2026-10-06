#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/derived/plain"
expanded="$root/derived/expanded"
logs="$root/derived/logs"
mkdir -p "$out" "$expanded" "$logs"
python "$root/scripts/build_step1_inventory.py" >/dev/null 2>&1 || true
python - "$root" <<'PY'
import csv, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]); source=root/'source'; out=root/'derived/plain'; expanded=root/'derived/expanded'; logs=root/'derived/logs'
rows=list(csv.DictReader((root/'config/paper_catalog.csv').open()))
for r in rows:
    src=source/r['source_path']
    stem=src.parent.name if src.name=='main.tex' else src.stem
    exp=expanded/(stem+'.tex'); txt=out/(stem+'.txt')
    with (logs/(stem+'.latexpand.err')).open('w') as err, exp.open('w') as f:
        subprocess.run(['latexpand', src.name], cwd=src.parent, stdout=f, stderr=err, check=False)
    with (logs/(stem+'.pandoc.err')).open('w') as err, txt.open('w') as f:
        subprocess.run(['pandoc','-f','latex','-t','plain',str(exp)], stdout=f, stderr=err, check=False)
PY
