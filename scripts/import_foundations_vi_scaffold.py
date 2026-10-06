#!/usr/bin/env python3
"""Import the reusable Foundations VI scaffold from the supplied Collatz archive.

The imported tree is a byte-for-byte, curated subset of the upstream archive.
It is deliberately kept separate from Foundations-VII-authored work so later
changes cannot silently rewrite the prior proof base.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = ROOT / "formalization" / "_provenance" / "six-birds-collatz_v19.zip"
TARGET = ROOT / "formalization" / "foundations_vi_scaffold"
PROVENANCE = ROOT / "formalization" / "_provenance"

EXACT_FILES = {
    ".gitignore",
    ".github/workflows/ci.yml",
    "THEOREMS.md",
    "scripts/audit_foundations_dependencies.py",
}
PREFIXES = (
    "design/",
    "formalization/",
    "lab/",
    "lean/",
    "paper/",
)

INTENDED_USE = {
    ".gitignore": "upstream build-artifact hygiene",
    ".github": "baseline Lean/lab/audit CI recipe",
    "THEOREMS.md": "authoritative Foundations VI theorem and schema ledger",
    "design": "law design, landing methodology, terminology, and traceability protocol",
    "formalization": "law manifests, imported-foundation audit, proof gates, and examples",
    "lean": "active mechanized theorem scaffold for Foundations I/II/III/IV/VI",
    "lab": "finite-model probes, fixtures, regression tests, and recorded results",
    "paper": "Foundations VI source text and bibliography for statement alignment",
    "scripts": "imported-foundation dependency audit",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def selected(name: str) -> bool:
    return name in EXACT_FILES or any(name.startswith(prefix) for prefix in PREFIXES)


def safe_member(name: str) -> PurePosixPath:
    rel = PurePosixPath(name)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe archive member: {name!r}")
    return rel


def category(name: str) -> str:
    first = PurePosixPath(name).parts[0]
    return first


def intended_use(name: str) -> str:
    first = category(name)
    return INTENDED_USE.get(name, INTENDED_USE.get(first, "curated upstream support asset"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--target", type=Path, default=TARGET)
    args = parser.parse_args()

    archive = args.archive.resolve()
    target = args.target.resolve()
    if not archive.is_file():
        raise SystemExit(f"missing archive: {archive}")

    PROVENANCE.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    rows: list[dict[str, object]] = []
    archive_comment = ""
    with zipfile.ZipFile(archive) as zf:
        archive_comment = zf.comment.decode("utf-8", errors="replace").strip()
        infos = sorted(zf.infolist(), key=lambda item: item.filename)
        for info in infos:
            name = info.filename.rstrip("/") if info.is_dir() else info.filename
            if not name or info.is_dir() or not selected(name):
                continue
            rel = safe_member(name)
            data = zf.read(info)
            out = target.joinpath(*rel.parts)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            mode = (info.external_attr >> 16) & 0o777
            if mode:
                out.chmod(mode)
            rows.append(
                {
                    "source_archive_path": name,
                    "imported_path": str(out.relative_to(ROOT)),
                    "category": category(name),
                    "bytes": len(data),
                    "sha256": sha256_bytes(data),
                    "intended_reuse": intended_use(name),
                }
            )

    if not rows:
        raise SystemExit("selection produced no files")

    manifest = PROVENANCE / "foundations_vi_import_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    sums = PROVENANCE / "foundations_vi_imported_files.sha256"
    sums.write_text(
        "".join(f"{row['sha256']}  {row['imported_path']}\n" for row in rows),
        encoding="utf-8",
    )

    archive_hash = sha256_file(archive)
    (PROVENANCE / "six-birds-collatz_v19.zip.sha256").write_text(
        f"{archive_hash}  {archive.relative_to(ROOT)}\n", encoding="utf-8"
    )
    if not re.fullmatch(r"[0-9a-f]{40}", archive_comment):
        raise SystemExit(f"archive comment is not an upstream commit id: {archive_comment!r}")
    (PROVENANCE / "upstream_commit.txt").write_text(archive_comment + "\n", encoding="utf-8")

    selection_record = {
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": archive_hash,
        "upstream_commit_from_zip_comment": archive_comment,
        "target": str(target.relative_to(ROOT)),
        "selected_exact_files": sorted(EXACT_FILES),
        "selected_prefixes": list(PREFIXES),
        "selected_file_count": len(rows),
        "selected_bytes": sum(int(row["bytes"]) for row in rows),
        "excluded_top_level": [
            ".codex/",
            "collatz_idea.md",
            "ideas.md",
            "review_requests/",
            "scripts/make_review_zip.sh",
            "scripts/package_repo_snapshot.sh",
        ],
        "policy": "Imported files are immutable upstream baseline assets; VII-authored extensions live outside this subtree.",
    }
    (PROVENANCE / "import_selection.json").write_text(
        json.dumps(selection_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"Imported Foundations VI scaffold: {len(rows)} files, "
        f"{selection_record['selected_bytes']} bytes, upstream {archive_comment}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
