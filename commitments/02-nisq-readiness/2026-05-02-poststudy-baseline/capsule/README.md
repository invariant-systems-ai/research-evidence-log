# An Evidence-First Reproducibility Capsule for NISQ Benchmarking

Canonical capsule date: 2026-05-01

This directory is the publication-facing evidence capsule archived at Zenodo DOI `10.5281/zenodo.19954164` and prepared for external review and journal submission. It contains the public manuscript bundle, ancillary data, verifier scripts, workload definitions, figures, and release wrapper needed for an outside reviewer to inspect and replay the claim boundary.

The public capsule and companion receipt surfaces were assembled with AIIR, the open-source receipt and reproducibility tool used in the broader project to emit reviewer-facing evidence bundles. Reviewers do not need AIIR to verify this paper; the exported capsule is the canonical public audit object.

## One-Sentence Claim

We demonstrate an evidence-first reproducibility capsule for NISQ benchmarking and an IBM-only empirical case study executed within it: an author-preserved evaluation plan, content-addressed logical workload identity, provider job-id provenance, negative controls, replayable cross-backend analysis on real IBM quantum hardware, and a bundled second-provider real-hardware confirmation note on AWS Braket.

The AWS Braket confirmation documents a narrow two-provider-surface hardware portability claim for the evidence contract. It does not create a matched multi-vendor performance statistic, and Azure simulator submissions are excluded from the real-hardware claim.

## What Is Demonstrated

- Public six-backend corpus: 168 S1 offline distributions across 28 workload kinds.
- Declared v1.1 S1 manifest scope: 156 submitted runs across 26 workload kinds.
- Confirmatory S2 stage: 40 runs across 10 workload kinds on 2 backends.
- Cross-backend structure within the IBM-only corpus: mean Spearman rho 0.8409 across the 28-workload public corpus.
- Deterministic permutation sensitivity: 14/15 significant after Bonferroni correction; the weakest pair is `ibm_boston vs ibm_torino`, rho 0.537, analytic p_Bonferroni 0.04782, permutation p_Bonferroni 0.06074696.
- Pairwise backend tests: 15/15 significant after Bonferroni correction under the analytic Spearman t-approximation.
- Public replay: ancillary schema validation, CHSH recomputation, cross-backend analysis, readout mitigation, noise-model comparison, scaling analysis, and bootstrap smoke validation all replay from the shipped bundle.
- Companion second-provider real-hardware confirmation: AWS Braket IQM Garnet runs cover four published workloads at 256 and 4096 shots and are accompanied by a machine-readable provider-facts surface with provider-side timestamps and hash fields.
- Execution-order note: the bundle separates the author-declared plan date from later IBM/AWS execution evidence and states explicitly that this is not independent preregistration.

## What Is Not Claimed

- No claim of quantum advantage.
- No claim of fault tolerance.
- No claim of loophole-free Bell testing.
- No claim of provider-signed attestation.
- No claim of independent preregistration backed by a third-party timestamp.
- No claim of post-transpilation circuit identity; OpenQASM SHA256 hashes bind logical workload bytes only.
- No claim of multi-vendor universality.
- No claim that the AWS Braket confirmation set updates the IBM cross-backend statistics.
- No claim that Azure simulator submissions count as real-hardware evidence.
- No claim that all NISQ hardware is generally ready for production advantage workloads.

The contribution is a reviewer-auditable evidence contract and an IBM empirical case study, not a broad quantum-performance victory claim.

## Entry Points

- `nisq_readiness.tex` - manuscript source.
- `nisq_readiness.pdf` - locally rebuilt manuscript PDF.
- `MANIFEST.md` - public upload manifest.
- `PUBLIC_ARCHIVE_FILESET.txt` - authoritative allowlist for the published Zenodo archive.
- `REPRODUCE.md` - reproducibility instructions and expected checks.
- `CLAIMS_AND_NONCLAIMS.md` - reviewer-safe claim boundary.
- `LICENSE_RELEASE.md` - public release license map for manuscript, data, QASM, and scripts.
- `SCOPE_RECONCILIATION.md` - target/submitted/completed run-count reconciliation.
- `STATISTICAL_SENSITIVITY.md` - reviewer-facing correlation sensitivity note.
- `PUBLIC_SUMMARY.md` - concise non-hype summary for landing pages and external readers.
- `CITATION.cff` - citation metadata for the release.
- `checksums.sha256` - generated checksums for the published file set.
- `anc/README.md` - reviewer-facing ancillary guide and verifier commands.
- `anc/22_AWS_BRAKET_REAL_HARDWARE_CONFIRMATION_20260501.md` - bundled second-provider real-hardware confirmation note.
- `anc/23_AWS_BRAKET_PROVIDER_FACTS_20260501.json` - machine-readable AWS provider facts for the 8 bundled Garnet tasks.
- `anc/24_EXECUTION_ORDER_AND_TIMESTAMP_POSTURE_20260501.md` - execution-order and timestamp-boundary note.
- `summary/` - public summary JSON files regenerated from the shipped scripts.

## Published Archive Boundary

The published Zenodo archive is intentionally narrower than this working directory. It is built from `PUBLIC_ARCHIVE_FILESET.txt` and contains only the manuscript bundle, figures, public ancillary data, public summary JSON, reproducibility scripts, workload definitions, and reviewer-facing wrapper notes needed to read and replay the result.

Every file in the submission packet is enumerated in `PUBLIC_ARCHIVE_FILESET.txt`, recorded in `checksums.sha256`, and included in the tarball only through that allowlist. If a file is not named in `PUBLIC_ARCHIVE_FILESET.txt`, it is not part of the public submission packet.

## Implementation Note

AIIR canonical public surface: `https://github.com/invariant-systems-ai/aiir`

For this paper, AIIR is the public implementation layer used to package the capsule and receipt surfaces. The scientific claim remains the exported evidence bundle and its replayability, not any private substrate behind the broader project.

## Zenodo Status

This capsule is archived for public release at Zenodo DOI `10.5281/zenodo.19954164` using the release-local license map in `LICENSE_RELEASE.md`. The license map applies to this publication capsule and the files listed in the public archive allowlist.
