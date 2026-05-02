# Scope Reconciliation

This file records the count reconciliation for the public evidence capsule. It is intentionally separate from the historical plan JSON so the original declaration surface remains unchanged.

## Count Surfaces

| Surface | Runs | Workload kinds | Backends | Role |
| --- | ---: | ---: | ---: | --- |
| Declared v1.1 S1 target in `anc/PREREGISTRATION_PUBLIC.json` | 180 | 30 | 6 | Planning target recorded in the author-declared plan surface. |
| Submitted v1.1 S1 manifest in `anc/16_ARXIV_ANCILLARY_MANIFEST_v1_1.json` | 156 | 26 | 6 | Bound submitted-run manifest used for submission integrity. |
| Completed v1.1 S1 offline distributions in `anc/17_ARXIV_ANCILLARY_DATA_v1_1.json` | 168 | 28 | 6 | Complete public six-backend corpus used for cross-backend analysis. |
| Confirmatory v1.1 S2 stage in `anc/20_ARXIV_ANCILLARY_MANIFEST_v1_1_S2.json` and `anc/21_ARXIV_ANCILLARY_DATA_v1_1_S2.json` | 40 | 10 | 2 | Higher-shot confirmation subset. |

## Rationale

The declared target remains a historical planning artifact and is not rewritten. The manuscript makes result claims against completed public evidence surfaces, not against the original target count.

The 26-workload submitted S1 manifest contains the mirror, GHZ-7, Grover, QFT, and fixed-seed random-circuit families. The completed S1 offline distribution file adds the two historically declared application-relevant variational workloads, `v11_vqe_h2` and `v11_qaoa_maxcut4`, yielding 28 complete six-backend workload kinds and 168 distributions.

The remaining declared target gap is reported as unexecuted planning scope, not as a failed or hidden result. No headline claim depends on the unexecuted target slots, and the cross-backend analysis uses only workload kinds with complete six-backend public distributions.

## Reviewer Rule

When citing counts, use the surface-specific numbers above. Do not collapse them into a single run count, and do not describe the 168-distribution public corpus as if it were identical to the 156-run submitted manifest.
