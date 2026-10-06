#!/usr/bin/env python3
"""Create a deterministic cumulative repository ZIP, including Git history.

Usage:
    python scripts/package_deterministic_zip.py OUTPUT.zip [ARCHIVE_ROOT_NAME]

The output must be outside the repository.  File order, timestamps, Unix modes,
and compression settings are fixed so identical repository bytes produce an
identical ZIP.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = (2026, 7, 26, 0, 0, 0)
EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".ipynb_checkpoints",
    ".venv",
    ".lake",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.is_file() and path.suffix in EXCLUDED_SUFFIXES:
        return False
    if path.name in {"index.lock", "packed-refs.lock"} and ".git" in rel.parts:
        return False
    # Directory entries are intentional.  Git repositories with packed refs may
    # have required empty directories such as `.git/refs`; omitting them makes
    # an otherwise complete extracted repository fail Git discovery.
    return path.is_file() or path.is_symlink() or path.is_dir()


def zip_info(arcname: str, mode: int) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (mode & 0xFFFF) << 16
    return info


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    output = Path(sys.argv[1]).resolve()
    if ROOT == output or ROOT in output.parents:
        raise SystemExit("output ZIP must be outside the repository")
    prefix = sys.argv[2] if len(sys.argv) == 3 else ROOT.name
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()

    paths = sorted((p for p in ROOT.rglob("*") if included(p)), key=lambda p: p.relative_to(ROOT).as_posix())

    # The Git index contains path-local stat-cache data and is refreshed by
    # ordinary read-only commands such as ``git status`` after extraction.
    # Package a canonical index rebuilt from HEAD so identical commits and
    # worktree bytes produce identical archives across different paths.
    normalized_index: bytes | None = None
    with tempfile.TemporaryDirectory(prefix="six-birds-git-index-") as td:
        git_index = Path(td) / "index"
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(git_index)
        result = subprocess.run(
            ["git", "read-tree", "HEAD"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(f"failed to build canonical Git index: {result.stderr.strip()}")
        normalized_index = git_index.read_bytes()

        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as zf:
            for path in paths:
                rel = path.relative_to(ROOT).as_posix()
                arcname = f"{prefix}/{rel}"
                if path.is_symlink():
                    mode = stat.S_IFLNK | 0o777
                    data = os.readlink(path).encode("utf-8")
                elif path.is_dir():
                    st_mode = path.stat().st_mode
                    mode = stat.S_IFDIR | (st_mode & 0o777)
                    data = b""
                    arcname += "/"
                else:
                    st_mode = path.stat().st_mode
                    mode = stat.S_IFREG | (st_mode & 0o777)
                    data = normalized_index if rel == ".git/index" else path.read_bytes()
                zf.writestr(zip_info(arcname, mode), data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    tmp.replace(output)
    print(f"archive={output}")
    print(f"files={len(paths)}")
    print(f"bytes={output.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
