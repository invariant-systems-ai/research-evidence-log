# Reproducing the Evidence-First Reproducibility Capsule for NISQ Benchmarking

This guide is written for a reviewer starting from the Zenodo capsule archive or a checked-out copy of this capsule directory.

## Requirements

- Python 3.10 or newer.
- No external Python packages are needed for the core replay path.
- `pdflatex` is optional and only needed to rebuild the manuscript PDF.
- `numpy` and `matplotlib` are optional and only needed for figure rendering paths.

No AIIR installation is required for reviewer replay. AIIR was used to assemble the public capsule and companion receipt surfaces, but the verification path in this guide starts from the exported files shipped in this directory.

## 10-Minute Replay

From the capsule root:

```bash
cd anc
python validate_ancillaries.py
python verify_chsh.py
python cross_backend_analysis.py
python readout_mitigation.py
python noise_model_comparison.py
python scaling_analysis.py
python bootstrap_ci.py --n-bootstrap 200
```

Expected outcome:

- `validate_ancillaries.py` validates 6 JSON ancillary files.
- `verify_chsh.py` reports that recomputed CHSH values match the manifest.
- `cross_backend_analysis.py` reports 28 workload kinds.
- `cross_backend_analysis.py` writes analytic p-values and deterministic permutation sensitivity results.
- `readout_mitigation.py` keeps the product-state negative control below the claim gate.
- `noise_model_comparison.py` writes `summary/noise_model_comparison.json`.
- `scaling_analysis.py` writes `summary/scaling_analysis.json`.
- The bootstrap smoke run reports a Bootstrap/IID width ratio near 0.977 for 200 replicates.

The 200-replicate bootstrap command is a smoke test. It is not the basis for the manuscript-level bootstrap claim.

## Full Bootstrap Replay

For the slower bootstrap validation used by the manuscript-level claim boundary:

```bash
cd anc
python bootstrap_ci.py --n-bootstrap 10000
```

This writes `summary/bootstrap_ci.json` in the local working copy and is the replay path for the manuscript statement that uses `B = 10000` bootstrap replicates. The release capsule includes the retained 10000-replicate artifact at `summary/bootstrap_ci.json`.

## Manuscript Rebuild

From the capsule root:

```bash
pdflatex -interaction=nonstopmode -halt-on-error nisq_readiness.tex
```

The migrated capsule rebuilt with exit code 0 on 2026-05-01. The remaining warnings were REVTeX, underfull-box, and float-placement warnings, not compile failures.

## Headline Values To Check

`summary/cross_backend_analysis.json` should contain:

- `workload_metadata`: 28 entries.
- Sensitivity surfaces: `leave_one_family_out`, `leave_one_workload_out`, `clustered_bootstrap`, and `residualized_rank_correlation`.
- `mean_cross_backend_rho`: 0.8409.
- `pairwise_tests`: 15 entries.
- `significant=true`: 15 of 15 entries.
- `permutation_sensitivity.significant_pairs_after_bonferroni`: 14 of 15 entries.
- Weakest pair: `ibm_boston vs ibm_torino`, rho 0.537, analytic p_Bonferroni 0.04782, permutation p_Bonferroni 0.06074696.

## Checksum Verification

After unpacking the Zenodo archive, run:

```bash
sha256sum -c checksums.sha256
```

This checks all capsule files listed in the checksum manifest. The manifest intentionally omits its own digest so the verification command succeeds directly.

## Companion Provider Evidence

The core replay path above verifies the IBM statistical corpus. The release capsule also bundles `anc/22_AWS_BRAKET_REAL_HARDWARE_CONFIRMATION_20260501.md`, which records a second real-hardware provider-surface confirmation on AWS Braket IQM Garnet for `v11_qft4`, `v11_vqe_h2`, `v11_qaoa_maxcut4`, and `v11_grover3` at 256 and 4096 shots.

The bundled provider-facts surface `anc/23_AWS_BRAKET_PROVIDER_FACTS_20260501.json` records provider-side `createdAt` / `endedAt` timestamps, HTTP `Date` headers, and logical hash fields for all 8 AWS confirmation tasks. The companion note `anc/24_EXECUTION_ORDER_AND_TIMESTAMP_POSTURE_20260501.md` distinguishes those later execution timestamps from independent preregistration of the plan.

These bundled companion surfaces support a narrow two-provider-surface hardware portability claim for the evidence contract. They are not part of the manuscript's IBM cross-backend correlation statistics and are not required for the standard-library replay above.

Azure Quantum submissions from the same campaign were simulator-only under the attached workspace SKU and are excluded from the real-hardware claim.
