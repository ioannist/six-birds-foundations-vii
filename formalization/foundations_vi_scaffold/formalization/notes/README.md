# Foundations VI Formalization Notes

This directory will hold per-law notes once actual G-law mechanization begins.

`notes/examples/G<N>.md` is the six-part deep-dive for a law, split out from the compressed `THEOREMS.md` catalog entry when Lean work starts. It records the exact Lean statement target, local examples, imported theorem dependencies, and any prose-to-Lean fidelity issues discovered during mechanization.

`notes/gates/G<N>.md` is the promotion-gate-panel plus null-battery record for the same law. It is built only when the vendored Foundations III promotion machinery is actually invoked for that law, and it records which gates apply, which are not required, and which nonclaims/nulls were checked.

No per-law example or gate notes are created during scaffold setup. They are created by the mechanization packet for the specific law being landed.
