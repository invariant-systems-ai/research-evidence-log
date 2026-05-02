# Evidence Commitments

This repository is the public commitment surface for evaluation plans, evidence-package hashes, and later transparency-log references for Invariant Systems research campaigns.

Purpose:

- provide a public, append-only Git history for declared-plan surfaces and related evidence hashes
- separate public commitment mechanics from private working repositories
- give future campaigns a day-zero public repository target before execution begins

Claim boundary:

- a public Git commit timestamp is a public chronology surface
- it is not, by itself, a registry-backed preregistration or a substitute for an external transparency log
- post-study commits do not retroactively convert earlier work into preregistration

Current contents:

- [commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/README.md) records a post-study public commitment for the NISQ-readiness evaluation-plan surface and the released Zenodo evidence package
- [commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/README.md) mirrors the exact 82-file published public capsule allowlist and validates it against the shipped `checksums.sha256`
- [commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/aiir/](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/aiir/BUNDLESET.json) adds AIIR-native commitment receipts and CBOR sidecars for the full capsule mirror, the minimal chronology packet, and the published Zenodo tarball digest

Featured campaign:

The current public release is the NISQ-readiness paper bundle, *An Evidence-First
Reproducibility Capsule for NISQ Benchmarking*. The campaign entry combines four
review surfaces in one place: the paper-facing 82-file capsule mirror, the copied
public plan and checksum sidecars, AIIR-native receipt bundles with Sigstore and
Rekor transparency material, and direct links to the current Zenodo release. Read
it as the public release note for the paper rather than only as a chronology log:
start with the [campaign README](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/README.md),
then open the [paper capsule](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/README.md)
or the [manuscript PDF](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/nisq_readiness.pdf).

Paper linkage for the current NISQ campaign:

- paper title: `An Evidence-First Reproducibility Capsule for NISQ Benchmarking`
- manuscript PDF: [commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/nisq_readiness.pdf](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/nisq_readiness.pdf)
- manuscript source: [commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/nisq_readiness.tex](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/nisq_readiness.tex)
- paper-facing capsule README: [commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/README.md](commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/README.md)
- current public Zenodo record: [https://zenodo.org/records/19960217](https://zenodo.org/records/19960217)
- current public Zenodo version DOI: [10.5281/zenodo.19960217](https://doi.org/10.5281/zenodo.19960217)

Planned steady-state workflow for new campaigns:

1. commit the declared evaluation-plan file or its exact hash here on day zero
2. mirror the exact public release allowlist when the campaign has a paper-facing capsule
3. emit an AIIR commitment receipt over the full public capsule mirror, copied public packet, and/or the exact released digest
4. verify the AIIR receipt locally and, when available, attach a Sigstore bundle
5. mirror the same hash to an external transparency log such as Rekor or OpenTimestamps
6. record the transparency-log entry in the campaign directory
7. never rewrite history for prior commitments

Canonical URL:

- [https://github.com/invariant-systems-ai/evidence-commitments](https://github.com/invariant-systems-ai/evidence-commitments)
