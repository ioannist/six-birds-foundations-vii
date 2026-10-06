# Foundations V and VI import provenance

The public repository retains curated, byte-verified extracts of the supplied Foundations V and VI
archives. The original ZIPs are deliberately not distributed because they also contain operational
review material that is not part of the scientific release. Their digest records and upstream commit
identities remain public so a maintainer with a local copy can verify it.

The Foundations VI archive `six-birds-collatz_v19.zip` has SHA-256:

`a595687d1ebccac4407aa5131f6ee03df349131c0cace236f1ae91f6d6a86ad4`

Its zip comment records upstream commit:

`220b45879d8e63f1a75573145e0be6bb3f52567c`

The Foundations V archive `six-birds-cognition_v45_2.zip` has SHA-256:

`7d88998a856a6cb5019ee01d39925ec9b42deb1cf3ab74862067627d27de3a4a`

Its recorded upstream commit is `d548b834481ffe9160194907df61e6e247defc8e`.

The two selection records state the curated extraction policies. The import manifests and
`*_imported_files.sha256` files bind every distributed scaffold file to its original archive bytes.

The curated active scaffold imports 282 files: the theorem ledger, all design documents, the formalization inventory/manifests/notes, the complete Lean tree, the complete lab tree and recorded results, paper source and bibliography, the upstream CI workflow, `.gitignore`, and the dependency-audit script.

Operational prompts, review-request history, freeform idea notes, and upstream packaging scripts are
not copied into the active scaffolds and are not dependencies of the Foundations VII workflow.
