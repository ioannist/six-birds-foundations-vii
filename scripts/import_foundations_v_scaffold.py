#!/usr/bin/env python3
"""Import the reusable Foundations V scaffold from the supplied cognition archive.

The imported tree is a byte-for-byte curated subset of the upstream archive.
All Lean sources are retained, including vendored dependencies. Review-request
correspondence and packaging scripts are excluded from the active subtree and
the public repository. Maintainers may retain the original archive locally.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = ROOT / "formalization" / "_provenance" / "six-birds-cognition_v45_2.zip"
TARGET = ROOT / "formalization" / "foundations_v_scaffold"
PROVENANCE = ROOT / "formalization" / "_provenance"

EXACT_FILES = {
    ".gitignore",
    "LANDING_PLAN.md",
    "THEOREMS.md",
    "scripts/audit_foundations_dependencies.py",
}
PREFIXES = (
    ".github/",
    "formalization/",
    "kb/",
    "lab/",
    "lean/",
)

INTENDED_USE = {
    ".gitignore": "upstream build-artifact hygiene",
    ".github": "baseline Lean/lab/apparatus CI recipe",
    "LANDING_PLAN.md": "historical proof-landing order, gates, and dependencies",
    "THEOREMS.md": "authoritative Foundations V theorem and law-design ledger",
    "formalization": "declaration manifest, imported-foundations inventory, proof gates, examples, sweeps, and traceability",
    "kb": "SBT grammar, structural-law, instantiation, and cross-disciplinary knowledge base",
    "lean": "complete Foundations V Lean sources and all vendored Lean dependencies",
    "lab": "finite-model substrates, sweeps, fixtures, and regression tests",
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
    return PurePosixPath(name).parts[0]


def intended_use(name: str) -> str:
    first = category(name)
    return INTENDED_USE.get(name, INTENDED_USE.get(first, "curated upstream support asset"))


def is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0o170000
    return mode == 0o120000


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
        for info in sorted(zf.infolist(), key=lambda item: item.filename):
            name = info.filename.rstrip("/") if info.is_dir() else info.filename
            if not name or info.is_dir() or is_symlink(info) or not selected(name):
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

    manifest = PROVENANCE / "foundations_v_import_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    sums = PROVENANCE / "foundations_v_imported_files.sha256"
    sums.write_text(
        "".join(f"{row['sha256']}  {row['imported_path']}\n" for row in rows),
        encoding="utf-8",
    )

    archive_hash = sha256_file(archive)
    (PROVENANCE / "six-birds-cognition_v45_2.zip.sha256").write_text(
        f"{archive_hash}  {archive.relative_to(ROOT)}\n", encoding="utf-8"
    )
    if not re.fullmatch(r"[0-9a-f]{40}", archive_comment):
        raise SystemExit(f"archive comment is not an upstream commit id: {archive_comment!r}")
    (PROVENANCE / "foundations_v_upstream_commit.txt").write_text(
        archive_comment + "\n", encoding="utf-8"
    )

    selection_record = {
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": archive_hash,
        "upstream_commit_from_zip_comment": archive_comment,
        "target": str(target.relative_to(ROOT)),
        "selected_exact_files": sorted(EXACT_FILES),
        "selected_prefixes": list(PREFIXES),
        "selected_file_count": len(rows),
        "selected_bytes": sum(int(row["bytes"]) for row in rows),
        "all_lean_sources_included": True,
        "excluded_top_level": [
            "review_requests/",
            "scripts/make_review_zip.sh",
            "six-birds-papers (external symlink)",
        ],
        "policy": "Imported files are immutable upstream baseline assets; VII-authored adapters and extensions live outside this subtree.",
    }
    (PROVENANCE / "foundations_v_import_selection.json").write_text(
        json.dumps(selection_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"Imported Foundations V scaffold: {len(rows)} files, "
        f"{selection_record['selected_bytes']} bytes, upstream {archive_comment}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
