# Ancillary Files — An Evidence-First Reproducibility Capsule for NISQ Benchmarking

These files provide the complete data, workload definitions, and verification
scripts supporting the public evidence capsule (v1.0 and v1.1).

## Files

### Author-Declared Evaluation & Design

- **PREREGISTRATION_PUBLIC.json** — Historical author-declared evaluation plan (v1.0 + v1.1) with decision rules and metrics.

Scope reconciliation: `PREREGISTRATION_PUBLIC.json` intentionally preserves the historical v1.1 S1 target of 30 workload kinds / 180 expected runs. The completed public bundle reports the reconciled execution scope below: 156 declared S1 manifest runs / 26 workload kinds, 168 S1 offline distributions / 28 workload kinds, and 40 S2 confirmatory runs. See `../SCOPE_RECONCILIATION.md` for the release-level rationale.

Timestamp reconciliation: `PREREGISTRATION_PUBLIC.json` is retained as a historical author-declared evaluation surface. It was not independently timestamped through OSF before execution. Zenodo concept DOI `10.5281/zenodo.19954163` identifies the public release series, and the current version DOI `10.5281/zenodo.19985231` should be treated as a public release timestamp rather than an independent pre-execution registry timestamp.

- **24_EXECUTION_ORDER_AND_TIMESTAMP_POSTURE_20260501.md** — timestamp-boundary note distinguishing author-declared plan dating from later IBM/AWS execution evidence.

### v1.0 Evidence (CHSH)

- **08_WORKLOAD_CORPUS_APPENDIX.md** — v1.0 workload corpus descriptions.
- **09_ARXIV_ANCILLARY_MANIFEST_v1.json** — CHSH evidence manifest (33 runs).
- **12_ARXIV_ANCILLARY_DATA_v1.json** — CHSH offline distributions.

### v1.1 Evidence (S1 + S2)

- **15_ADDON_V1_1_WORKLOAD_CORPUS_APPENDIX.md** — v1.1 workload expansion corpus.
- **16_ARXIV_ANCILLARY_MANIFEST_v1_1.json** — v1.1 S1 manifest (156 declared runs, 26 workload kinds).
- **17_ARXIV_ANCILLARY_DATA_v1_1.json** — v1.1 S1 offline distributions (168 completed runs, 28 workload kinds, including VQE-H2 and QAOA-MaxCut4).
- **18_ADDON_V1_1_RESULTS_SUMMARY.md** — v1.1 results summary.
- **18_ADDON_V1_1_RESULTS_SUMMARY.json** — v1.1 results summary (machine-readable).
- **20_ARXIV_ANCILLARY_MANIFEST_v1_1_S2.json** — v1.1 S2 confirmatory manifest (40 runs).
- **21_ARXIV_ANCILLARY_DATA_v1_1_S2.json** — v1.1 S2 offline distributions.

### Companion Second-Provider Hardware Confirmation

- **22_AWS_BRAKET_REAL_HARDWARE_CONFIRMATION_20260501.md** — bundled AWS Braket IQM Garnet confirmation note for four published workloads at 256 and 4096 shots. This note supports a narrow two-provider-surface hardware claim for the evidence contract; it is not part of the IBM statistical corpus.
- **23_AWS_BRAKET_PROVIDER_FACTS_20260501.json** — machine-readable provider facts extracted from the bundled AWS Braket submission/result artifacts, including provider-side timestamps and hash fields for all 8 confirmation tasks.

### Quantum Workloads

- **v1_*.qasm, v11_*.qasm** — 32 OpenQASM files defining the public v1.0 and v1.1 workload corpus (4 v1.0 definitions + 28 v1.1 definitions).

### Scripts — Verification

- **validate_ancillaries.py** — Schema validation for all JSON ancillary files.
- **verify_chsh.py** — Standalone CHSH inequality verification (stdlib only).
- **generate_figures.py** — Regenerates paper figures from bundled data.

### Scripts — Analysis (reproduce all paper results)

- **noise_model_comparison.py** — Depolarizing noise-model comparison: predicts CHSH S from published gate/readout error rates, writes a JSON summary, and generates Fig. 4 when matplotlib is available.
- **bootstrap_ci.py** — Non-parametric bootstrap resampling (B=10,000) validation of IID confidence intervals for all 33 CHSH runs. Stdlib only.
- **cross_backend_analysis.py** — Pairwise Spearman rank correlations across all 6 backends for the 28 public-bundle v1.1 workload kinds, writes analytic p-values and deterministic permutation sensitivity results, and generates Fig. 5 when matplotlib is available. Stdlib only.
- **readout_mitigation.py** — M3-style readout error mitigation for ibm_torino CHSH runs (diagnostic, not claim-gate). Stdlib only.
- **scaling_analysis.py** — GHZ parity exponential-decay diagnostic using the bundled Mirror-1Q and GHZ-7 distributions, writes a JSON summary, and generates Fig. 6 when matplotlib is available.

## Verification

```bash
# Core verification (no external dependencies)
python verify_chsh.py            # Verify CHSH results from published distributions
python validate_ancillaries.py   # Validate JSON schemas
python bootstrap_ci.py           # Validate IID CI assumption via bootstrap
python readout_mitigation.py     # Reproduce ibm_torino mitigation analysis
python cross_backend_analysis.py # Reproduce cross-backend correlation matrix

# Summary and figure generation (figure rendering requires numpy + matplotlib)
python generate_figures.py       # Regenerate paper figures
python noise_model_comparison.py # Regenerate noise model figure (Fig. 4)
python scaling_analysis.py       # Regenerate GHZ scaling figure (Fig. 6)
```

## Dependencies

Python 3.10+. Core verification scripts (`verify_chsh.py`, `bootstrap_ci.py`, `readout_mitigation.py`, `cross_backend_analysis.py`) use only the standard library.
`noise_model_comparison.py` and `scaling_analysis.py` can write JSON summaries with the standard library; their figure-rendering paths, and `generate_figures.py`, require numpy and matplotlib.

## License

See `../LICENSE_RELEASE.md` for the release-local license map. In summary: manuscript and prose are `CC-BY-4.0`, ancillary JSON/QASM data are `CC0-1.0`, and verifier/analysis scripts are `MIT`.
