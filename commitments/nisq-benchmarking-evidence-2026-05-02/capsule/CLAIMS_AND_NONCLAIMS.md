# Claims and Non-Claims

## Primary Claim

This capsule demonstrates a reviewer-auditable evidence contract for NISQ benchmarking: a reviewer can inspect the declared logical workload identities, provider job-id provenance, an author-preserved evaluation plan, negative controls, public summary artifacts, and replay scripts from the shipped bundle.

## Promoted Empirical Claims

- The public six-backend corpus contains 168 S1 offline distributions across 28 workload kinds.
- The declared v1.1 S1 manifest remains 156 submitted runs across 26 workload kinds.
- The S2 confirmatory stage contains 40 runs across 10 workload kinds on 2 backends.
- The regenerated cross-backend analysis reports mean Spearman rho 0.8409.
- Deterministic permutation sensitivity retains 14 of 15 significant backend pairs after Bonferroni correction.
- All 15 pairwise backend correlations are significant after Bonferroni correction under the analytic Spearman t-approximation.
- The weakest retained backend pair is `ibm_boston vs ibm_torino`, rho 0.537, analytic p_Bonferroni 0.04782, permutation p_Bonferroni 0.06074696.
- Product-state negative controls correctly fail the CHSH claim gate.

## Methodological Claims

- Workload identity is content-addressed through OpenQASM source bytes and SHA256 digests.
- Execution identity is recorded through provider `job_id` values.
- Decision gates and non-claims are preserved in the public author-maintained evaluation-plan surface.
- Core verification scripts replay with the Python standard library.
- A bundled AWS Braket confirmation set, backed by machine-readable provider facts, shows that the same logical workloads, provider job IDs, and raw-artifact capture pattern operate on a second real-hardware provider surface outside IBM.

## Non-Claims

- This is not a quantum-advantage claim.
- This is not a fault-tolerance claim.
- This is not a loophole-free Bell-test claim.
- This is not a provider-signed attestation claim.
- This is not an independently preregistered study claim.
- Later IBM/AWS execution timestamps do not convert the author-declared plan into independent preregistration.
- This is not a post-transpilation identity claim; OpenQASM SHA256 hashes bind logical workload bytes only.
- This is not a multi-vendor universality claim.
- The bundled AWS Braket confirmation set is not part of the IBM cross-backend correlation statistics.
- The AWS Braket confirmation set does not prove hardware-independent workload difficulty across vendor families.
- Azure simulator submissions are excluded from the real-hardware claim.
- This does not show that all NISQ hardware is production-ready for useful advantage workloads.
- This does not claim that backend correlations exclude all architecture-homogeneity explanations.
- This does not claim that the weakest backend pair remains significant under every sensitivity test.

## Reviewer-Safe Summary

The defensible contribution is a reproducible evidence contract for NISQ benchmarking, demonstrated statistically on real IBM quantum hardware and accompanied by a bundled second-provider real-hardware confirmation set on AWS Braket. The result should be evaluated as a provenance-focused evidence contract, an IBM empirical case study, and a narrow two-provider-surface hardware-portability demonstration for the evidence contract, not as a broad claim that NISQ devices have reached quantum advantage, that the study is independently preregistered, or that workload rankings have already generalized across vendor families.
