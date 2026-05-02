# Public Summary

## An Evidence-First Reproducibility Capsule for NISQ Benchmarking

This release presents a reproducible evidence capsule for NISQ benchmarking on real IBM quantum hardware. The central contribution is not a quantum-advantage claim. It is a way to make a NISQ experiment auditable: what workload ran, where it ran, how it was scored, what the preserved plan says, and what claims are not allowed.

The capsule binds logical OpenQASM workload files to SHA256 content hashes, records provider `job_id` provenance, preserves an author-maintained evaluation plan and non-claims, includes negative controls, and ships replay scripts that recompute the main public results from the ancillary data.

A bundled companion note records completed AWS Braket IQM Garnet hardware confirmations for four published workloads at 256 and 4096 shots, and a bundled machine-readable provider-facts JSON records provider-side timestamps and hash fields for all 8 AWS confirmation tasks. That supports a narrow two-provider-surface real-hardware claim for the evidence contract; it is not used to update the IBM cross-backend statistics and does not make this a matched multi-vendor statistical study. Azure simulator submissions are excluded from the real-hardware claim.

Frozen public archive DOI: `10.5281/zenodo.19954164`.

## Headline Result

Within the IBM-only six-backend corpus, the public packet contains 168 S1 offline distributions across 28 workload kinds, plus 40 S2 confirmatory runs. The regenerated cross-backend analysis reports mean Spearman rho 0.8409 across the 28-workload public corpus. A deterministic permutation sensitivity check keeps 14 of 15 backend-pair correlations significant after Bonferroni correction and flags the weakest pair, IBM Boston vs IBM Torino, as borderline: rho 0.537, analytic p_Bonferroni 0.04782, permutation p_Bonferroni 0.06074696. Under the analytic Spearman t-approximation, all 15 backend-pair correlations are significant after Bonferroni correction.

## Why It Matters

Quantum benchmarking often reports outcomes without enough public evidence binding for an outside reader to verify the chain from workload to execution to metric to claim. This capsule demonstrates a stricter posture: every major claim is paired with public data, replay commands, hashes, decision gates, and explicit non-claims.

## What This Does Not Claim

This release does not claim quantum advantage, fault tolerance, loophole-free Bell testing, provider-signed attestation, independent preregistration, post-transpilation circuit identity, or multi-vendor universality. It demonstrates a reproducible evidence standard for NISQ experiments, applies the statistical part of that standard to an IBM Quantum hardware corpus, and bundles a second-provider real-hardware confirmation surface on AWS Braket.

## Fast Review Path

Start with:

- `CLAIMS_AND_NONCLAIMS.md`
- `REPRODUCE.md`
- `anc/README.md`
- `summary/cross_backend_analysis.json`
- `nisq_readiness.pdf`

The core replay path uses only Python standard-library scripts from `anc/`.
