# ADR-0006 — Repository-local path in the source-archive checksum record

**Status:** accepted  
**Date:** 2026-07-26

## Context

The generated provenance file `source/_provenance/archive.sha256` initially retained the staging-workspace path `source_snapshot/_provenance/...`. The digest was correct, but that path does not exist in the delivered repository and therefore prevented direct `sha256sum -c` verification from the repository root.

## Decision

Change only the recorded path token to the repository-local path:

`source/_provenance/six-birds-foundations-vii_v0.zip`

The archive digest remains `ae9e1cefecf56a921157e31a1a5ab43a7dac8653069eb21ec8e7ba39ef61047b`. No supplied paper or wish-list byte is changed. Regenerate the frozen-source hash ledger and delivery checksum manifest after this metadata correction.

## Consequence

The original source archive can be verified directly from the delivered repository, and the correction remains visible as a separate Git commit rather than rewriting the source-import history.
