# AWS Braket Real-Hardware Confirmation (2026-05-01)

This note records the non-IBM real-hardware confirmation set bundled with the NISQ-readiness release. It is not part of the six-backend IBM statistical corpus used for the rank-correlation claims in the manuscript. Its role is narrower: to show that the same evidence contract, logical workload identities, provider job-ID capture, and raw-result export pattern also survive on a second real-hardware provider surface.

## Scope

- Provider surface: AWS Braket
- Hardware target: IQM Garnet (`arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet`)
- Logical workloads: `v11_qft4`, `v11_vqe_h2`, `v11_qaoa_maxcut4`, `v11_grover3`
- Shot lanes: 256 and 4096
- Status: all 8 tasks completed

## Completed Tasks

| logical_id | shots | task_id | status |
| --- | ---: | --- | --- |
| `v11_qft4` | 256 | `19097b04-1a34-47f3-9f16-7deecb2be79a` | `COMPLETED` |
| `v11_vqe_h2` | 256 | `2accd8ae-969e-48cb-9647-0129a96eee5e` | `COMPLETED` |
| `v11_qaoa_maxcut4` | 256 | `ae23910b-0c2d-4924-9d44-fe1633bd2bfc` | `COMPLETED` |
| `v11_grover3` | 256 | `e5d56d9a-5008-48e7-bf6b-298318534fd7` | `COMPLETED` |
| `v11_qft4` | 4096 | `8c292d4d-715c-4579-9fcf-fe3eddb6a3d3` | `COMPLETED` |
| `v11_vqe_h2` | 4096 | `00bd2a3e-2a36-4ba0-a7b8-a865b7eb47f3` | `COMPLETED` |
| `v11_qaoa_maxcut4` | 4096 | `8d3d7b4e-fb83-41d8-b0eb-9eea688bdbc6` | `COMPLETED` |
| `v11_grover3` | 4096 | `fa366c0e-b8dd-4263-ad1d-df26558fa680` | `COMPLETED` |

## Shot-Volume Stability Summary

The 256-shot lane was followed by a 4096-shot lane on the same device and logical workloads. The resulting total-variation distances (TVDs) and largest single-bin movements were:

| logical_id | shots_256 | shots_4096 | TVD | max_abs_delta | max_abs_delta_state |
| --- | ---: | ---: | ---: | ---: | --- |
| `v11_grover3` | 256 | 4096 | 0.0522 | 0.0259 | `001` |
| `v11_qaoa_maxcut4` | 256 | 4096 | 0.0859 | 0.0310 | `1001` |
| `v11_qft4` | 256 | 4096 | 0.0876 | 0.0310 | `1001` |
| `v11_vqe_h2` | 256 | 4096 | 0.0601 | 0.0581 | `10` |

These values should be read as a stability check for the companion provider surface, not as a replacement for the IBM corpus or as a matched vendor-normalized benchmark.

## Claim Boundary

- Supports: a narrow two-provider-surface real-hardware claim for the evidence contract (`IBM Quantum` + `AWS Braket`).
- Does not support: cross-vendor workload-ordering universality, hardware-vendor agnosticism, or a three-backend market-wide claim.
- Does not update: the IBM-only cross-backend correlation statistics in the manuscript.

## Excluded Surfaces

Azure Quantum submissions from the same campaign are excluded from the real-hardware claim because the attached workspace exposed simulator-only targets at submission time (`quantinuum.sim.h2-1e`). They remain useful as provider-surface submission artifacts, but not as evidence for a second non-IBM real-hardware execution surface.
