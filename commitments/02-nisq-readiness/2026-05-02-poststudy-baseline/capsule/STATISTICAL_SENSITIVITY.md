# Statistical Sensitivity Notes

This file records reviewer-facing sensitivity checks for the headline cross-backend correlation result.

## Spearman Correlations

The manuscript reports pairwise Spearman rank correlations across 28 complete six-backend workload kinds. Ranks use average-rank tie handling. The release should lead with deterministic permutation sensitivity, while retaining the analytic Spearman t-approximation as a secondary check.

Under the analytic test, all 15 of 15 backend pairs are significant after Bonferroni correction. The weakest pair is `ibm_boston vs ibm_torino`, with rho `0.537`, raw p-value `0.003188`, and Bonferroni p-value `0.04782`.

## Deterministic Permutation Sensitivity

The release script `anc/cross_backend_analysis.py` also runs a deterministic Monte Carlo permutation sensitivity check:

- permutations per backend pair: `20000`
- seed base: `424242`
- test: two-sided permutation test on average ranks
- smoothing: add-one finite Monte Carlo smoothing

This stricter sensitivity check reports 14 of 15 backend pairs as Bonferroni-significant. The weakest pair, `ibm_boston vs ibm_torino`, is borderline under permutation sensitivity with permutation Bonferroni p-value `0.06074696`.

## Interpretation Rule

The capsule should therefore state the result as follows: deterministic permutation sensitivity gives 14/15 significant backend pairs after Bonferroni correction and flags the weakest Boston-Torino pair as borderline; the analytic Spearman test gives 15/15 significant backend pairs. Do not describe the weakest pair as robust under every sensitivity test.

## Additional Hardening Results

The current release now includes the main family/workload sensitivity checks that a referee would expect around the headline IBM-only rank-preservation result.

### Leave-One-Family-Out

- mean off-diagonal `rho_bar` stays in `[0.7722, 0.8918]`
- lowest mean occurs when dropping the `rand` family: `rho_bar = 0.7722`
- highest mean occurs when dropping the `mirror` family: `rho_bar = 0.8918`
- no single family removal collapses the sign or the basic high-correlation pattern

### Leave-One-Workload-Out

- maximum absolute change in `rho_bar` is `0.0210`
- dropping `v11_grover2` raises `rho_bar` to `0.8619`
- dropping `v11_qaoa_maxcut4` lowers `rho_bar` to `0.8225`
- these are leverage effects, not qualitative reversals

### Family-Clustered Bootstrap

- bootstrap design: resample the 7 workload families with replacement
- replicates: `5000`
- observed mean `rho_bar`: `0.8409`
- 95% cluster-bootstrap CI for mean `rho_bar`: `[0.4415, 0.9575]`
- weakest observed pair `ibm_boston vs ibm_torino`: observed `rho = 0.5374`, cluster-bootstrap CI `[0.1372, 0.9785]`

This interval is intentionally wide because the family count is small and the `rand` family contributes most workload kinds. It is therefore best interpreted as a conservative family-level uncertainty bound, not as evidence against the high central estimate.

### Residualized Rank Correlation

- residualization target: within-backend average ranks of the primary workload metrics
- covariates removed: `num_qubits`, QASM-derived logical depth (excluding measurement), and family dummies
- mean residualized backend correlation: `0.9209`
- residualized pairwise range: `[0.8527, 0.9684]`

### Current Scope Judgment

These added checks materially strengthen the IBM-only empirical regularity claim. They do not convert the result into a proof of hardware-independent workload ordering, and they do not remove the need for a real multi-vendor corpus before making broader universality claims.
