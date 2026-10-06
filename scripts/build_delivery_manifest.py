#!/usr/bin/env python3
"""Build a deterministic non-Git delivery manifest and SHA256SUMS ledger.

The implementation walks the tree once, excludes transient/Git directories at
traversal time, and hashes each deliverable payload once.  This keeps the final
cumulative release rebuild practical while preserving the historical manifest
format.
"""
from __future__ import annotations

import csv
import hashlib
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "generated" / "file_manifest.csv"
SUMS = ROOT / "SHA256SUMS"
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".venv", ".lake"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".olean", ".ilean"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def category(rel: Path) -> str:
    return rel.parts[0] if len(rel.parts) > 1 else "root"


def git_ignored(paths: list[Path]) -> set[Path]:
    """Paths git ignores, so the ledger never records machine-local state.

    A clean checkout does not contain ignored files (e.g. `.codex/logs`,
    `.codex/threads`), so hashing them would make the release ledger
    unreproducible on any other machine.
    """
    if not paths:
        return set()
    rels = "\n".join(p.relative_to(ROOT).as_posix() for p in paths)
    result = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=ROOT, input=rels, text=True, capture_output=True, check=False,
    )
    if result.returncode not in (0, 1):       # 1 == nothing ignored
        return set()
    return {ROOT / line for line in result.stdout.splitlines() if line}


def discover_payload_files() -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT, topdown=True, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        base = Path(dirpath)
        for filename in sorted(filenames):
            path = base / filename
            if path in {MANIFEST, SUMS} or path.suffix in SKIP_SUFFIXES:
                continue
            if path.is_file():
                files.append(path)
    ignored = git_ignored(files)
    files = [path for path in files if path not in ignored]
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> int:
    files = discover_payload_files()
    workers = min(8, max(1, os.cpu_count() or 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        digests = dict(zip(files, pool.map(sha256, files)))

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "bytes", "sha256", "category"],
            lineterminator="\n",
        )
        writer.writeheader()
        for path in files:
            rel = path.relative_to(ROOT)
            writer.writerow(
                {
                    "path": rel.as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": digests[path],
                    "category": category(rel),
                }
            )

    sum_rows = [(path.relative_to(ROOT).as_posix(), digest) for path, digest in digests.items()]
    sum_rows.append((MANIFEST.relative_to(ROOT).as_posix(), sha256(MANIFEST)))
    sum_rows.sort()
    with SUMS.open("w", encoding="utf-8") as handle:
        for rel, digest in sum_rows:
            handle.write(f"{digest}  {rel}\n")

    print(f"manifest_entries={len(files)} sha256_entries={len(sum_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
