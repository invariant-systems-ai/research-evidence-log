# AIIR Receipt Bundles

This directory houses AIIR-native commitment receipts and Sigstore bundle sidecars for the public NISQ post-study baseline packet and the full paper-facing capsule mirror.

Current bundle set:

- `receipts/receipt_nisq-public-evidence-cap_a25683519087f75a.json` binds `capsule/`, the full 82-file public evidence capsule mirror copied from the published allowlist. This is the primary paper-referenceable receipt in the sidecar repo.
- `receipts/receipt_nisq-poststudy-baseline-_a256aed808e54ca3.json` binds the public packet files `README.md`, `COMMITMENT.json`, `SHA256SUMS`, and the copied `source/` directory after the top-level manifest was normalized to point at `BUNDLESET.json` for exact receipt coordinates and the final README lint cleanup was folded back into the packet boundary.
- `receipts/receipt_nisq-zenodo-release-pack_a256d471841487c1.json` binds the exact published Zenodo tarball digest `sha256:e5511fbf5cafbe9fce809f9b9820d27027852430e4e8f1feee6bfaad2b219d67`.
- Each receipt has a deterministic CBOR sidecar in the same `receipts/` directory.
- Each receipt now also has a Sigstore bundle sidecar in the same `receipts/` directory.
- `SHA256SUMS` records plain file hashes for the emitted JSON, CBOR, and `.sigstore` receipt artifacts.
- `capsule/checksums.sha256` validates the copied 82-file public mirror exactly against the published release checksums.

Generator provenance:

- AIIR repository: <https://github.com/invariant-systems-ai/aiir>
- AIIR ref used for emission: `feat/commitment-receipts`
- AIIR commit used for emission: `2d20f37a259d515cf4877a0abf998753ce3c0621`
- AIIR receipt schema: `aiir/commitment_receipt.v1`
- AIIR version reported in the receipts: `1.5.1`

Signing status:

- All three receipts have Sigstore bundle sidecars and passed identity-pinned verification for signer `noah@invariantsystems.io` with issuer `https://accounts.google.com`.
- `receipts/receipt_nisq-public-evidence-cap_a25683519087f75a.json.sigstore` records Rekor log index `1429021050` with integrated time `2026-05-02T12:00:17Z`.
- `receipts/receipt_nisq-poststudy-baseline-_a256aed808e54ca3.json.sigstore` records Rekor log index `1429082977` with integrated time `2026-05-02T12:55:48Z`.
- `receipts/receipt_nisq-zenodo-release-pack_a256d471841487c1.json.sigstore` records Rekor log index `1429022622` with integrated time `2026-05-02T12:03:18Z`.
- The current signed state is recorded in `BUNDLESET.json`; after the top-level packet files were normalized to point at `BUNDLESET.json` for exact receipt coordinates, the packet receipt was re-issued and re-signed so the smaller packet boundary stayed self-consistent.

Verification:

```bash
cd commitments/02-nisq-readiness/2026-05-02-poststudy-baseline
sha256sum -c aiir/SHA256SUMS

PYTHONPATH=/path/to/aiir /usr/bin/env python3 -m aiir.cli \
  --verify aiir/receipts/receipt_nisq-public-evidence-cap_a25683519087f75a.json \
  --verify-signature \
  --signer-identity noah@invariantsystems.io \
  --signer-issuer https://accounts.google.com

PYTHONPATH=/path/to/aiir /usr/bin/env python3 -m aiir.cli \
  --verify aiir/receipts/receipt_nisq-poststudy-baseline-_a256aed808e54ca3.json \
  --verify-signature \
  --signer-identity noah@invariantsystems.io \
  --signer-issuer https://accounts.google.com

PYTHONPATH=/path/to/aiir /usr/bin/env python3 -m aiir.cli \
  --verify aiir/receipts/receipt_nisq-zenodo-release-pack_a256d471841487c1.json \
  --verify-signature \
  --signer-identity noah@invariantsystems.io \
  --signer-issuer https://accounts.google.com

cd capsule
sha256sum -c checksums.sha256
```

Signature verification requires an environment with AIIR's signing extras or equivalent `sigstore` dependencies installed.

Until commitment receipts land on AIIR main, verification needs an AIIR checkout that includes commit `2d20f37a259d515cf4877a0abf998753ce3c0621` or a descendant that still carries `aiir/commitment_receipt.v1`.

Claim boundary:

- supports tamper-evident integrity for the full copied paper-facing public capsule mirror in `capsule/`
- supports tamper-evident integrity for the copied sidecar packet files in this repository
- supports tamper-evident direct digest binding for the published Zenodo tarball hash
- supports identity-pinned Sigstore signing for the three receipt sidecars under `noah@invariantsystems.io` via `https://accounts.google.com`
- supports Rekor-backed public transparency-log timestamps for the three receipt sidecars

- does not support independent preregistration of the current NISQ study
- does not support a witness-quorum or multi-log transparency proof beyond the included Sigstore bundle and Rekor entry material
