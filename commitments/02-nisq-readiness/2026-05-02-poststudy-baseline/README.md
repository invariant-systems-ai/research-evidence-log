# NISQ Readiness Post-Study Baseline

This directory records a public post-study commitment for the NISQ-readiness campaign.

What this entry does:

- places the declared evaluation-plan surface in a public Git history
- binds the public Zenodo evidence package checksum alongside that plan surface
- establishes the repository surface that future campaigns will use on day zero
- mirrors the exact published 82-file public capsule allowlist that the paper can cite directly
- adds AIIR-native receipt bundles for the public packet and the direct Zenodo digest binding
- adds an AIIR-native receipt over the full mirrored capsule
- records Sigstore bundle sidecars and Rekor-backed timestamps for the AIIR receipt set

What this entry does not do:

- it does not create an independent pre-execution timestamp for the February 1, 2026 plan
- it does not retroactively convert the NISQ paper into a preregistered study

This entry now has three parallel surfaces:

- `source/` preserves the copied public plan, timestamp-boundary, and checksum files verbatim
- `capsule/` is a verbatim mirror of the published public release allowlist, validated locally with `sha256sum -c checksums.sha256`
- `aiir/` carries AIIR-native receipt bundles and Sigstore bundle sidecars over the capsule mirror, the minimal chronology packet, and the published Zenodo tarball digest

## Paper Linkage

This public commitment is explicitly tied to the paper bundle for:

- title: `An Evidence-First Reproducibility Capsule for NISQ Benchmarking`
- manuscript PDF: `capsule/nisq_readiness.pdf`
- manuscript source: `capsule/nisq_readiness.tex`
- paper-facing capsule README: `capsule/README.md`
- claim boundary: `capsule/CLAIMS_AND_NONCLAIMS.md`
- public summary: `capsule/PUBLIC_SUMMARY.md`
- current public Zenodo record: `https://zenodo.org/records/19960217`
- current public Zenodo version DOI: `10.5281/zenodo.19960217`

The `capsule/` directory is the primary paper-referenceable sidecar packet in
this repository. It is kept verbatim with respect to the published allowlist,
while this outer directory carries chronology notes, commitment metadata, and
AIIR receipt material.

The machine-readable manifests for this entry are `COMMITMENT.json` and `aiir/BUNDLESET.json`.
The primary paper-referenceable sidecar surface is `capsule/`, with its integrity bound by `aiir/receipts/receipt_nisq-public-evidence-cap_a25683519087f75a.json`.
Exact receipt filenames, per-artifact hashes, signer policy, and Rekor entry details are recorded in `aiir/BUNDLESET.json`.
