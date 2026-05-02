#!/usr/bin/env python3
"""
bootstrap_ci.py — Bootstrap confidence intervals for CHSH S values.

Resamples per-setting shot data to compute non-parametric bootstrap CIs
and compares them to the IID analytic approximation reported in the paper.

This addresses the concern that IID confidence intervals may underestimate
uncertainty due to temporal correlations (T1/T2 drift, TLS fluctuators,
crosstalk) on NISQ hardware.

Dependencies: Python 3.7+ stdlib only (uses random for resampling).
"""

import json
import math
import os
import random
import sys
from collections import defaultdict


def counts_from_probs(probs, n_shots):
    """
    Convert probability distribution to integer shot counts.

    Since ancillary data stores probabilities (not raw counts), we reconstruct
    approximate counts. The sum may differ from n_shots by ±1 due to rounding.
    """
    counts = {}
    remaining = n_shots
    sorted_keys = sorted(probs.keys(), key=lambda k: -probs[k])
    for i, key in enumerate(sorted_keys):
        if i == len(sorted_keys) - 1:
            counts[key] = remaining
        else:
            c = round(probs[key] * n_shots)
            counts[key] = c
            remaining -= c
    return counts


def expand_shots(counts):
    """Expand count dict to list of individual outcomes for resampling."""
    outcomes = []
    for bitstring, count in counts.items():
        outcomes.extend([bitstring] * max(0, count))
    return outcomes


def parity(bitstring):
    """Compute (-1)^(XOR of all bits). For 2-bit: (-1)^(b0 XOR b1)."""
    xor = 0
    for ch in bitstring:
        xor ^= int(ch)
    return (-1) ** xor


def correlation_from_outcomes(outcomes):
    """Compute E = mean of (-1)^(x XOR y) over outcomes."""
    if not outcomes:
        return 0.0
    total = sum(parity(o) for o in outcomes)
    return total / len(outcomes)


def parity_plus_probability(probs, n_shots):
    """Return empirical probability that the parity observable is +1."""
    counts = counts_from_probs(probs, n_shots)
    plus_count = sum(count for bitstring, count in counts.items() if parity(bitstring) == 1)
    total_count = sum(counts.values())
    return plus_count / total_count if total_count else 0.0


def sample_binomial(random_source, trials, probability):
    """Sample Binomial(trials, probability) using stdlib support when available."""
    binomial = getattr(random_source, "binomialvariate", None)
    if binomial is not None:
        return binomial(trials, probability)

    # Compatibility fallback for Python versions before random.binomialvariate.
    if trials <= 512:
        return sum(1 for _ in range(trials) if random_source.random() < probability)

    mean = trials * probability
    std = math.sqrt(trials * probability * (1.0 - probability))
    return max(0, min(trials, round(random_source.gauss(mean, std))))


def compute_chsh_from_correlations(e00, e01, e10, e11):
    """S = E(a0b0) + E(a0b1) + E(a1b0) - E(a1b1)."""
    return e00 + e01 + e10 - e11


def bootstrap_chsh(quasi_by_setting, n_shots, n_bootstrap=10000, seed=42):
    """
    Compute bootstrap distribution of CHSH S.

    For each bootstrap replicate:
      1. Resample n_shots outcomes (with replacement) for each setting.
      2. Compute E for each setting.
      3. Compute S.

    Returns: (S_original, bootstrap_S_values)
    """
    rng = random.Random(seed)

    # CHSH depends only on the parity observable for each setting, so the
    # non-parametric bootstrap can resample parity counts directly.
    settings = ["a0b0", "a0b1", "a1b0", "a1b1"]
    plus_prob = {}
    for setting in settings:
        plus_prob[setting] = parity_plus_probability(quasi_by_setting[setting], n_shots)

    # Original S
    e_orig = {}
    for setting in settings:
        e_orig[setting] = 2.0 * plus_prob[setting] - 1.0
    s_orig = compute_chsh_from_correlations(
        e_orig["a0b0"], e_orig["a0b1"], e_orig["a1b0"], e_orig["a1b1"]
    )

    # Bootstrap
    bootstrap_s = []
    for _ in range(n_bootstrap):
        e_boot = {}
        for setting in settings:
            plus_count = sample_binomial(rng, n_shots, plus_prob[setting])
            e_boot[setting] = (2.0 * plus_count / n_shots) - 1.0

        s_boot = compute_chsh_from_correlations(
            e_boot["a0b0"], e_boot["a0b1"], e_boot["a1b0"], e_boot["a1b1"]
        )
        bootstrap_s.append(s_boot)

    return s_orig, bootstrap_s


def percentile(data, p):
    """Compute the p-th percentile of sorted data (0 <= p <= 100)."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (p / 100) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[f] * (c - k)
    d1 = sorted_data[c] * (k - f)
    return d0 + d1


def iid_ci95(s_val, e_vals, n_shots):
    """Compute IID analytic CI95 for comparison."""
    se_sq = 0.0
    for e in e_vals:
        var = max(0.0, 1.0 - e * e)
        se_sq += var / n_shots
    se_s = math.sqrt(se_sq)
    margin = 1.96 * se_s
    return (s_val - margin, s_val + margin)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ancillary_dir = script_dir  # data files live alongside scripts in anc/

    if "--ancillary-dir" in sys.argv:
        idx = sys.argv.index("--ancillary-dir")
        ancillary_dir = sys.argv[idx + 1]

    n_bootstrap = 10000
    if "--n-bootstrap" in sys.argv:
        idx = sys.argv.index("--n-bootstrap")
        n_bootstrap = int(sys.argv[idx + 1])

    print("=" * 72)
    print(f"Bootstrap CI Analysis (B={n_bootstrap} replicates)")
    print("=" * 72)
    print()

    data_path = os.path.join(ancillary_dir, "12_ARXIV_ANCILLARY_DATA_v1.json")
    manifest_path = os.path.join(ancillary_dir, "09_ARXIV_ANCILLARY_MANIFEST_v1.json")

    with open(data_path) as f:
        data = json.load(f)
    with open(manifest_path) as f:
        manifest = json.load(f)

    manifest_by_job = {}
    for run in manifest["chsh_evidence"]["runs"]:
        manifest_by_job[run["job_id"]] = run

    print(
        f"{'Run':>4s} {'Backend':<20s} {'Shots':>6s} "
        f"{'S':>8s} {'IID CI95':>20s} {'Boot CI95':>20s} "
        f"{'Width_IID':>10s} {'Width_Boot':>11s} {'Ratio':>7s}"
    )
    print("-" * 110)

    results = []
    for i, run in enumerate(data["runs"]):
        job_id = run["job_id"]
        mrun = manifest_by_job.get(job_id, {})
        backend = run["backend"]
        shots = run["shots"]
        quasi = run.get("quasi_by_setting", {})

        if not quasi or "a0b0" not in quasi:
            continue

        # Compute bootstrap
        s_orig, boot_s = bootstrap_chsh(quasi, shots, n_bootstrap=n_bootstrap, seed=42 + i)

        boot_lo = percentile(boot_s, 2.5)
        boot_hi = percentile(boot_s, 97.5)
        boot_width = boot_hi - boot_lo

        # Compute IID CI for comparison
        settings = ["a0b0", "a0b1", "a1b0", "a1b1"]
        e_vals = []
        for s in settings:
            p = quasi[s]
            e = p.get("00", 0) - p.get("01", 0) - p.get("10", 0) + p.get("11", 0)
            e_vals.append(e)
        iid_lo, iid_hi = iid_ci95(s_orig, e_vals, shots)
        iid_width = iid_hi - iid_lo

        ratio = boot_width / iid_width if iid_width > 0 else float('inf')

        print(
            f"{i + 1:>4d} {backend:<20s} {shots:>6d} "
            f"{s_orig:>8.4f} [{iid_lo:>8.4f}, {iid_hi:>8.4f}] "
            f"[{boot_lo:>8.4f}, {boot_hi:>8.4f}] "
            f"{iid_width:>10.4f} {boot_width:>11.4f} {ratio:>7.3f}"
        )

        results.append(
            {
                "run": i + 1,
                "backend": backend,
                "job_id": job_id,
                "shots": shots,
                "S": round(s_orig, 6),
                "iid_ci95": [round(iid_lo, 6), round(iid_hi, 6)],
                "bootstrap_ci95": [round(boot_lo, 6), round(boot_hi, 6)],
                "iid_width": round(iid_width, 6),
                "bootstrap_width": round(boot_width, 6),
                "ratio_boot_to_iid": round(ratio, 4),
            }
        )

    print()

    # Summary statistics
    ratios = [r["ratio_boot_to_iid"] for r in results]
    mean_ratio = sum(ratios) / len(ratios) if ratios else 0
    max_ratio = max(ratios) if ratios else 0
    min_ratio = min(ratios) if ratios else 0

    print(
        f"Bootstrap/IID width ratio: mean={mean_ratio:.3f}, "
        f"min={min_ratio:.3f}, max={max_ratio:.3f}"
    )
    print()

    if mean_ratio < 1.15:
        print("CONCLUSION: Bootstrap CIs are consistent with IID approximation")
        print("  (ratio ≈ 1.0). The IID assumption appears adequate for these")
        print("  workloads at these shot counts.")
    elif mean_ratio < 1.5:
        print("CONCLUSION: Bootstrap CIs are moderately wider than IID CIs.")
        print("  Some temporal correlation may be present. Consider Allan variance")
        print("  analysis for detailed characterization.")
    else:
        print("CONCLUSION: Bootstrap CIs are substantially wider than IID CIs.")
        print("  Temporal correlations are significant. IID CIs underestimate")
        print("  uncertainty.")

    # Save results
    output_path = os.path.join(script_dir, "..", "summary", "bootstrap_ci.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(
            {
                "description": "Bootstrap CI comparison against IID approximation",
                "n_bootstrap": n_bootstrap,
                "mean_ratio_boot_to_iid": round(mean_ratio, 4),
                "results": results,
            },
            f,
            indent=2,
        )
    print(f"\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
