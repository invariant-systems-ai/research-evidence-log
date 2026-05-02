# Execution Order And Timestamp Posture (2026-05-01)

This note tightens the timestamp posture for the NISQ-readiness capsule.

## Claim Boundary

- The public plan file `PREREGISTRATION_PUBLIC.json` is an author-declared plan surface with `date_declared: 2026-02-01`.
- Later IBM and AWS execution artifacts provide execution-order evidence that jobs were run after that declared date.
- These later timestamps do **not** convert the plan into an independently preregistered study, because the plan itself was not timestamped by an external registry before execution.

## Author-Declared Plan Date

- Source surface: `anc/PREREGISTRATION_PUBLIC.json`
- Declared date: `2026-02-01`
- Independent registry timestamp: not available (`OSF DOI: NOT_AVAILABLE`)

## IBM Execution-Order Evidence

Two timestamp surfaces are preserved for IBM runs in the broader execution evidence.

### IBM CHSH capture-time example

- Job ID: `d7pqo5m7g7gs73cfa980`
- Backend: `ibm_fez`
- Bound run capture UTC: `2026-04-30T19:23:03Z`
- Result capture UTC: `2026-04-30T19:34:22Z`
- Bound schedule hash: `sha256:ab557270afb211999d02439f4192b52d9981bbc4bfcc689501d4b2a93fa417dc`
- Bound Merkle root: `sha256:b5b8016077a869ec9bc0ce1fb33def5cb6e8ae1834249150bd128c932bacbb8f`

These capture times are later than the declared plan date and show that the preserved IBM execution evidence post-dates the author-declared plan surface.

### IBM provider-result execution-span example

- Job ID: `d5vsuo3uf71s73cj286g`
- Status: `DONE`
- Preserved result payload records IBM Runtime execution metadata with span:
  - start: `2026-02-01 22:10:43`
  - stop: `2026-02-01 22:10:46`
  - shots: `8192`

This provider-result metadata is preserved in the extracted IBM result surface and shows that IBM runtime execution-span timing is recoverable from the execution evidence, even when wrapper files use separate local capture timestamps.

## AWS Provider-Native Timestamp Evidence

The release bundle includes machine-readable AWS provider facts at `anc/23_AWS_BRAKET_PROVIDER_FACTS_20260501.json`.

That file records, for each of the eight bundled IQM Garnet confirmation tasks:

- local submission timestamp (`submitted_at`)
- provider-side `createdAt`
- provider-side `endedAt`
- HTTP `Date` headers from submission and result responses
- task ID / task ARN linkage
- logical workload hash fields (`schedule_hash`, `merkle_root`)

Example row:

- Logical workload: `v11_qft4`
- Shots: `256`
- Task ID: `19097b04-1a34-47f3-9f16-7deecb2be79a`
- Submitted at: `20260501T095441Z`
- Provider createdAt: `2026-05-01 09:54:40.951000+00:00`
- Provider endedAt: `2026-05-01 09:54:44.413000+00:00`

These are provider-native AWS timestamps, not merely local wrapper times.

## Interpretation

- Supported: the capsule preserves concrete execution-order evidence showing that the author-declared plan predates later IBM/AWS execution artifacts.
- Supported: the AWS second-provider confirmation is backed by machine-readable provider-native timing and hash facts, not only a prose note.
- Not supported: a claim that the plan was independently preregistered by a third party before execution.
- Not supported: a claim that all IBM timing in the paper bundle is already packaged in the same provider-native form as the AWS Braket companion surface.
