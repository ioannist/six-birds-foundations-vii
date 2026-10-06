#!/usr/bin/env python3
"""Rebuild the documented conservative plain-text fallback for sources that defeat Pandoc."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("step1_inventory", ROOT / "scripts" / "build_step1_inventory.py")
if spec is None or spec.loader is None:
    raise SystemExit("Could not load inventory helpers")
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)

rows = list(csv.DictReader((ROOT / "config" / "paper_catalog.csv").open(newline="", encoding="utf-8")))
row = next(r for r in rows if r["paper_id"] == "P020")
source = ROOT / "source" / row["source_path"]
plain_path = ROOT / "derived" / "plain" / f"{source.stem}.txt"
plain_path.parent.mkdir(parents=True, exist_ok=True)
plain = inv.tex_to_plain(inv.expand_dependencies(source))
plain_path.write_text(plain + "\n", encoding="utf-8")
print(f"P020 fallback={plain_path.relative_to(ROOT)} split_words={len(plain.split())}")
