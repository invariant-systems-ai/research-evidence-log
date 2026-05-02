# Add-on (v1.1) Results Summary — Stage S1 (2048 shots)

**Purpose:** Provide a reviewer-friendly, evidence-backed summary of the v1.1 workload expansion campaign.

**Accompanying ancillary files:**
- Workload definitions (OpenQASM + SHA256): `15_ADDON_V1_1_WORKLOAD_CORPUS_APPENDIX.md`
- Run table (job_id keyed): `16_ARXIV_ANCILLARY_MANIFEST_v1_1.json`
- Offline distributions: `17_ARXIV_ANCILLARY_DATA_v1_1.json`
- Machine summary: `18_ADDON_V1_1_RESULTS_SUMMARY.json`

---

## 1) Coverage and integrity

- **Total runs submitted**: 156 (26 workloads × 6 backends)
- **Binding verified (remote tags / receipt check)**: 156 / 156
- **Runs with fetched results + offline distributions available**: 156 / 156

Note: this summary covers the declared 26-workload S1 manifest. The current public offline distribution file also includes the later six-backend VQE-H2 and QAOA-MaxCut4 additions, bringing `17_ARXIV_ANCILLARY_DATA_v1_1.json` to 168 records and 28 workload kinds for the cross-backend analysis script.

### Per-backend status

| Backend | Runs | Binding verified | Results fetched | Offline distributions | Status snapshot |
|---|---:|---:|---:|---:|---|
| `ibm_boston` | 26 | 26 | 26 | 26 | DONE (26) |
| `ibm_fez` | 26 | 26 | 26 | 26 | DONE (26) |
| `ibm_kingston` | 26 | 26 | 26 | 26 | DONE (26) |
| `ibm_marrakesh` | 26 | 26 | 26 | 26 | DONE (26) |
| `ibm_pittsburgh` | 26 | 26 | 26 | 26 | DONE (26) |
| `ibm_torino` | 26 | 26 | 26 | 26 | DONE (26) |

---

## 2) Key metrics (simple, prereg-safe proxies)

These are **measurement summaries**, not universal claims.

### 2.1 Mirror-1Q depth sweep: return probability \(P(0)\)

`P(0)` from `prob_by_bitstring` for the Mirror circuits (`v11_mirror1q_d{d}`).

| Backend | d=1 | d=2 | d=4 | d=8 | d=16 |
|---|---:|---:|---:|---:|---:|
| `ibm_boston` | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `ibm_fez` | 0.9990 | 0.9995 | 0.9976 | 0.9985 | 0.9971 |
| `ibm_kingston` | 0.9980 | 0.9932 | 0.9985 | 0.9956 | 0.9966 |
| `ibm_marrakesh` | 0.9912 | 0.9907 | 0.9907 | 0.9927 | 0.9897 |
| `ibm_pittsburgh` | 0.9966 | 0.9976 | 0.9990 | 0.9961 | 0.9966 |
| `ibm_torino` | 0.9092 | 0.9092 | 0.9067 | 0.9141 | 0.9199 |

### 2.2 GHZ-7: parity success proxy \(P(0^n)+P(1^n)\)

| Backend | GHZ7 parity success |
|---|---:|
| `ibm_boston` | 0.8931 |
| `ibm_fez` | 0.5044 |
| `ibm_kingston` | 0.8965 |
| `ibm_marrakesh` | 0.9121 |
| `ibm_pittsburgh` | 0.8774 |
| `ibm_torino` | 0.7075 |

### 2.3 Grover: target-hit proxy \(P(1^n)\)

| Backend | Grover2 \(P(11)\) | Grover3 \(P(111)\) |
|---|---:|---:|
| `ibm_boston` | 0.9844 | 0.6621 |
| `ibm_fez` | 0.7954 | 0.6616 |
| `ibm_kingston` | 0.9692 | 0.6841 |
| `ibm_marrakesh` | 0.9604 | 0.6914 |
| `ibm_pittsburgh` | 0.9160 | 0.7285 |
| `ibm_torino` | 0.7944 | 0.6431 |

### 2.4 Random circuits: distribution shape proxies (mean over 4 seeds per bucket)

Reported per (width, depth) bucket:
- **entropy_bits_mean**: Shannon entropy of the output distribution
- **collision_mean**: \((\sum p(x)^2)\) (smaller ≈ “flatter” distribution)

See `18_ADDON_V1_1_RESULTS_SUMMARY.json` for the full per-backend bucket table.

---

## 3) Notes for reviewers

- The v1.1 campaign is designed to address “toy workload” / “handcrafted circuit” critiques while preserving the evidence-first posture.
- These results should be cited via `job_id` + workload SHA256 IDs.

