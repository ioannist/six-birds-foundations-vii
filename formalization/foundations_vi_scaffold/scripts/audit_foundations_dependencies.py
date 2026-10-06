#!/usr/bin/env python3
"""Validate Foundations VI imported-foundations citations.

Each imported-foundations row points at one vendored Lean source file and names
the Lean declarations that support the audit summary. This script checks that
those paths exist, statuses use the known vocabulary, and every declared
identifier literally appears in its source file.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "formalization" / "inventory" / "imported_foundations.yml"
VALID_STATUSES = {"verified_correct", "discrepancy_found"}


def _strip(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return [_strip(value)] if value else []
    try:
        parsed = ast.literal_eval(value)
    except Exception:
        inner = value[1:-1].strip()
        return [_strip(item) for item in inner.split(",") if item.strip()]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return []


def _load_with_yaml(path: Path) -> list[dict[str, Any]] | None:
    try:
        import yaml  # type: ignore[import-not-found]
    except Exception:
        return None

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return data["entries"]
    raise ValueError("inventory must be a YAML list or a mapping with an 'entries' list")


def _load_minimal_yaml(path: Path) -> list[dict[str, Any]]:
    """Parse the YAML subset used by formalization/inventory/imported_foundations.yml."""

    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    active_list_key: str | None = None
    active_block_key: str | None = None
    active_block_indent = 0
    active_block_lines: list[str] = []

    def flush_block() -> None:
        nonlocal active_block_key, active_block_indent, active_block_lines
        if current is not None and active_block_key is not None:
            current[active_block_key] = "\n".join(active_block_lines).strip()
        active_block_key = None
        active_block_indent = 0
        active_block_lines = []

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if active_block_key is not None:
            if indent > active_block_indent:
                active_block_lines.append(raw[active_block_indent + 2 :])
                continue
            flush_block()

        if stripped == "entries:":
            continue

        if indent == 0 and raw.startswith("- "):
            flush_block()
            if current is not None:
                rows.append(current)
            current = {}
            active_list_key = None
            item = stripped[2:].strip()
            if item:
                if ":" not in item:
                    raise ValueError(f"{path}:{lineno}: expected key/value after list marker")
                key, value = item.split(":", 1)
                current[key.strip()] = _strip(value)
            continue

        if current is None:
            raise ValueError(f"{path}:{lineno}: key outside entry")

        if indent > 0 and stripped.startswith("- "):
            if active_list_key is None:
                raise ValueError(f"{path}:{lineno}: nested list without active key")
            current.setdefault(active_list_key, []).append(_strip(stripped[2:]))
            continue

        if indent != 2 or ":" not in stripped:
            raise ValueError(f"{path}:{lineno}: expected entry field")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", ">-", ">+", "|", "|-", "|+"}:
            active_block_key = key
            active_block_indent = indent
            active_block_lines = []
            active_list_key = None
        elif not value:
            current[key] = []
            active_list_key = key
        elif value.startswith("["):
            current[key] = _parse_inline_list(value)
            active_list_key = None
        else:
            current[key] = _strip(value)
            active_list_key = None

    flush_block()
    if current is not None:
        rows.append(current)
    return rows


def load_inventory(path: Path) -> list[dict[str, Any]]:
    rows = _load_with_yaml(path)
    if rows is not None:
        return rows
    return _load_minimal_yaml(path)


def _source_path(value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def _identifiers(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def validate_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    name = str(row.get("object", "<unnamed>"))

    source = _source_path(row.get("lean_source"))
    if source is None:
        errors.append(f"{name}: missing lean_source")
    elif not source.exists():
        errors.append(f"{name}: lean_source does not exist: {source}")

    status = row.get("status")
    if status not in VALID_STATUSES:
        errors.append(f"{name}: invalid status {status!r}")

    identifiers = _identifiers(row.get("identifiers"))
    if not identifiers:
        errors.append(f"{name}: missing identifiers")

    if source is None or not source.exists() or not identifiers:
        return errors

    text = source.read_text(encoding="utf-8", errors="replace")
    for identifier in identifiers:
        pattern = rf"^\s*(theorem|lemma|def|axiom|opaque|structure|inductive)\s+{re.escape(identifier)}\b"
        if re.search(pattern, text, re.MULTILINE) is None:
            errors.append(f"{name}: top-level declaration not found in {source}: {identifier!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    args = parser.parse_args()

    if not args.inventory.exists():
        print(f"missing inventory: {args.inventory}", file=sys.stderr)
        return 2

    try:
        rows = load_inventory(args.inventory)
    except Exception as exc:
        print(f"failed to parse {args.inventory}: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for row in rows:
        errors.extend(validate_row(row))

    if errors:
        print("Foundations dependency audit failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Foundations dependency audit passed: {len(rows)} entries checked, 0 violations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
