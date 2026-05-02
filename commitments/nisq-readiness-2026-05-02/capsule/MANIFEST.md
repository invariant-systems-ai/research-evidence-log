# arXiv Upload Manifest — An Evidence-First Reproducibility Capsule for NISQ Benchmarking

Updated: 2026-05-01 (v8 — wrapper alignment + public boundary confirmation)

This manifest records the arXiv-facing manuscript, summary, and ancillary contents of the public capsule. The authoritative file-level submission boundary is `PUBLIC_ARCHIVE_FILESET.txt`; files not listed there are not part of the submission packet.

## Root files

- nisq_readiness.tex
- nisq_readiness.bbl
- references.bib
- fig1_chsh_backends.pdf
- fig2_mirror_depth_sweep.pdf
- fig3_v11_heatmap.pdf
- fig4_noise_model.pdf
- fig5_cross_backend_corr.pdf
- fig6_ghz_scaling.pdf

## Summary files (summary/)

- bootstrap_ci.json
- cross_backend_analysis.json
- noise_model_comparison.json
- readout_mitigation.json
- scaling_analysis.json

## Ancillary files (anc/)

- README.md
- 08_WORKLOAD_CORPUS_APPENDIX.md
- 09_ARXIV_ANCILLARY_MANIFEST_v1.json
- 12_ARXIV_ANCILLARY_DATA_v1.json
- 15_ADDON_V1_1_WORKLOAD_CORPUS_APPENDIX.md
- 16_ARXIV_ANCILLARY_MANIFEST_v1_1.json
- 17_ARXIV_ANCILLARY_DATA_v1_1.json
- 18_ADDON_V1_1_RESULTS_SUMMARY.json
- 18_ADDON_V1_1_RESULTS_SUMMARY.md
- 20_ARXIV_ANCILLARY_MANIFEST_v1_1_S2.json
- 21_ARXIV_ANCILLARY_DATA_v1_1_S2.json
- 22_AWS_BRAKET_REAL_HARDWARE_CONFIRMATION_20260501.md
- 23_AWS_BRAKET_PROVIDER_FACTS_20260501.json
- 24_EXECUTION_ORDER_AND_TIMESTAMP_POSTURE_20260501.md
- PREREGISTRATION_PUBLIC.json

### Scripts — Verification (stdlib only)

- verify_chsh.py
- validate_ancillaries.py
- bootstrap_ci.py
- readout_mitigation.py
- cross_backend_analysis.py

### Scripts — Figures (require numpy + matplotlib)

- generate_figures.py
- noise_model_comparison.py
- scaling_analysis.py

### Quantum workloads (OpenQASM 2.0)

- v1_bell_2q.qasm
- v1_ghz_3q.qasm
- v1_ghz_5q.qasm
- v1_mirror_1q.qasm
- v11_ghz7.qasm
- v11_grover2.qasm
- v11_grover3.qasm
- v11_mirror1q_d1.qasm
- v11_mirror1q_d2.qasm
- v11_mirror1q_d4.qasm
- v11_mirror1q_d8.qasm
- v11_mirror1q_d16.qasm
- v11_qaoa_maxcut4.qasm
- v11_qft4.qasm
- v11_qft5.qasm
- v11_rand_w4_d8_s7.qasm
- v11_rand_w4_d8_s42.qasm
- v11_rand_w4_d8_s1337.qasm
- v11_rand_w4_d8_s314159.qasm
- v11_rand_w4_d16_s7.qasm
- v11_rand_w4_d16_s42.qasm
- v11_rand_w4_d16_s1337.qasm
- v11_rand_w4_d16_s314159.qasm
- v11_rand_w6_d8_s7.qasm
- v11_rand_w6_d8_s42.qasm
- v11_rand_w6_d8_s1337.qasm
- v11_rand_w6_d8_s314159.qasm
- v11_rand_w6_d16_s7.qasm
- v11_rand_w6_d16_s42.qasm
- v11_rand_w6_d16_s1337.qasm
- v11_rand_w6_d16_s314159.qasm
- v11_vqe_h2.qasm

## Release wrapper files

- LICENSE_RELEASE.md
- SCOPE_RECONCILIATION.md
- STATISTICAL_SENSITIVITY.md
