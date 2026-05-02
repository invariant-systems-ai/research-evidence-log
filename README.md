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
- `commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/` records a post-study public commitment for the NISQ-readiness evaluation-plan surface and the released Zenodo evidence package
- `commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/capsule/` mirrors the exact 82-file published public capsule allowlist and validates it against the shipped `checksums.sha256`
- `commitments/02-nisq-readiness/2026-05-02-poststudy-baseline/aiir/` adds AIIR-native commitment receipts and CBOR sidecars for the full capsule mirror, the minimal chronology packet, and the published Zenodo tarball digest

Planned steady-state workflow for new campaigns:
1. commit the declared evaluation-plan file or its exact hash here on day zero
2. mirror the exact public release allowlist when the campaign has a paper-facing capsule
3. emit an AIIR commitment receipt over the full public capsule mirror, copied public packet, and/or the exact released digest
4. verify the AIIR receipt locally and, when available, attach a Sigstore bundle
5. mirror the same hash to an external transparency log such as Rekor or OpenTimestamps
6. record the transparency-log entry in the campaign directory
7. never rewrite history for prior commitments

Canonical URL:
- https://github.com/invariant-systems-ai/evidence-commitments