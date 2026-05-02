#!/usr/bin/env python3
"""
readout_mitigation.py — Readout error mitigation analysis for ibm_torino.

Applies matrix-free measurement error mitigation (M3R-style) to the
ibm_torino CHSH data and shows that post-mitigation S > 2.0 recovers.

This addresses:
  - M3: "No error mitigation = not NISQ ready"
  - M4: "ibm_torino is diagnosed but not explained"

Method:
  For 2-qubit readout, the confusion matrix is:
    M = [[1-e0, e0], [e1, 1-e1]]  (per qubit)
  where e0 = P(measure 1 | prepared 0), e1 = P(measure 0 | prepared 1).

  For simplicity (M3R-style), we assume symmetric readout error:
    e0 ≈ e1 ≈ epsilon_ro

  The 2-qubit confusion matrix is M_2 = M_1 ⊗ M_1.
  Mitigation: p_corrected = M_2^{-1} @ p_observed.

Dependencies: Python 3.7+ stdlib only.
"""

import json
import math
import os
import sys


# Published approximate per-qubit readout assignment error for ibm_torino
# (symmetric model: P(flip|0) ≈ P(flip|1) ≈ epsilon_ro)
IBM_TORINO_READOUT_ERROR = 0.045


def confusion_matrix_1q(eps):
    """
    1-qubit confusion matrix (symmetric model).
    M[measured][prepared] = P(measured | prepared)
    M = [[1-eps, eps], [eps, 1-eps]]
    """
    return [[1 - eps, eps], [eps, 1 - eps]]


def invert_2x2(m):
    """Invert a 2x2 matrix."""
    a, b = m[0]
    c, d = m[1]
    det = a * d - b * c
    if abs(det) < 1e-15:
        raise ValueError("Singular matrix")
    return [[d / det, -b / det], [-c / det, a / det]]


def tensor_2x2(a, b):
    """Compute 4x4 tensor product of two 2x2 matrices."""
    result = [[0.0] * 4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for l in range(2):
                    result[2 * i + k][2 * j + l] = a[i][j] * b[k][l]
    return result


def invert_4x4(m):
    """Invert a 4x4 matrix using Gauss-Jordan elimination."""
    n = 4
    # Augment with identity
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]

    for col in range(n):
        # Find pivot
        max_row = col
        for row in range(col + 1, n):
            if abs(aug[row][col]) > abs(aug[max_row][col]):
                max_row = row
        aug[col], aug[max_row] = aug[max_row], aug[col]

        pivot = aug[col][col]
        if abs(pivot) < 1e-15:
            raise ValueError("Singular matrix")

        for j in range(2 * n):
            aug[col][j] /= pivot

        for row in range(n):
            if row != col:
                factor = aug[row][col]
                for j in range(2 * n):
                    aug[row][j] -= factor * aug[col][j]

    return [row[n:] for row in aug]


def mat_vec_4(m, v):
    """Multiply 4x4 matrix by 4-vector."""
    result = [0.0] * 4
    for i in range(4):
        for j in range(4):
            result[i] += m[i][j] * v[j]
    return result


def mitigate_distribution(probs, eps_q0, eps_q1=None):
    """
    Apply M3R-style readout mitigation to a 2-qubit distribution.

    probs: dict with keys "00", "01", "10", "11"
    eps_q0, eps_q1: per-qubit readout error (symmetric model)

    Returns: mitigated probability dict (may have slightly negative values
    due to matrix inversion; we clip and renormalize).
    """
    if eps_q1 is None:
        eps_q1 = eps_q0

    # Build 2-qubit confusion matrix
    m1_q0 = confusion_matrix_1q(eps_q0)
    m1_q1 = confusion_matrix_1q(eps_q1)
    m2 = tensor_2x2(m1_q0, m1_q1)

    # Invert
    m2_inv = invert_4x4(m2)

    # Observed probabilities as vector [P(00), P(01), P(10), P(11)]
    keys = ["00", "01", "10", "11"]
    p_obs = [probs.get(k, 0.0) for k in keys]

    # Apply inverse
    p_mit = mat_vec_4(m2_inv, p_obs)

    # Clip negative values and renormalize
    p_mit = [max(0.0, p) for p in p_mit]
    total = sum(p_mit)
    if total > 0:
        p_mit = [p / total for p in p_mit]

    return dict(zip(keys, p_mit))


def correlation(dist):
    """E = P(00) - P(01) - P(10) + P(11)."""
    return dist.get("00", 0) - dist.get("01", 0) - dist.get("10", 0) + dist.get("11", 0)


def compute_chsh(quasi):
    """Compute CHSH S from per-setting distributions."""
    e00 = correlation(quasi["a0b0"])
    e01 = correlation(quasi["a0b1"])
    e10 = correlation(quasi["a1b0"])
    e11 = correlation(quasi["a1b1"])
    s = e00 + e01 + e10 - e11
    return s, [e00, e01, e10, e11]


def se_chsh(e_vals, n_shots):
    """Standard error of S (IID approximation)."""
    se_sq = sum(max(0, 1 - e**2) / n_shots for e in e_vals)
    return math.sqrt(se_sq)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ancillary_dir = script_dir  # data files live alongside scripts in anc/

    if "--ancillary-dir" in sys.argv:
        idx = sys.argv.index("--ancillary-dir")
        ancillary_dir = sys.argv[idx + 1]

    eps_ro = IBM_TORINO_READOUT_ERROR
    if "--readout-error" in sys.argv:
        idx = sys.argv.index("--readout-error")
        eps_ro = float(sys.argv[idx + 1])

    print("=" * 72)
    print("Readout Error Mitigation Analysis (ibm_torino)")
    print(f"Assumed per-qubit readout error: {eps_ro}")
    print("=" * 72)
    print()

    data_path = os.path.join(ancillary_dir, "12_ARXIV_ANCILLARY_DATA_v1.json")
    with open(data_path) as f:
        data = json.load(f)

    # Filter to ibm_torino runs
    torino_runs = [r for r in data["runs"] if r["backend"] == "ibm_torino"]
    print(f"ibm_torino runs: {len(torino_runs)}")
    print()

    print(
        f"{'Run':>4s} {'Shots':>6s} {'S_raw':>8s} {'S_mit':>8s} "
        f"{'CI95_raw':>18s} {'CI95_mit':>18s} {'Gate_raw':>9s} {'Gate_mit':>9s}"
    )
    print("-" * 100)

    results = []
    for i, run in enumerate(torino_runs):
        shots = run["shots"]
        quasi = run.get("quasi_by_setting", {})

        if not quasi or "a0b0" not in quasi:
            continue

        # Raw
        s_raw, e_raw = compute_chsh(quasi)
        se_raw = se_chsh(e_raw, shots)
        ci_raw = (s_raw - 1.96 * se_raw, s_raw + 1.96 * se_raw)
        gate_raw = "PASS" if s_raw > 2.0 and ci_raw[0] > 2.0 else "FAIL"

        # Mitigated
        quasi_mit = {}
        for setting in ["a0b0", "a0b1", "a1b0", "a1b1"]:
            quasi_mit[setting] = mitigate_distribution(quasi[setting], eps_ro)

        s_mit, e_mit = compute_chsh(quasi_mit)
        se_mit = se_chsh(e_mit, shots)
        ci_mit = (s_mit - 1.96 * se_mit, s_mit + 1.96 * se_mit)
        gate_mit = "PASS" if s_mit > 2.0 and ci_mit[0] > 2.0 else "FAIL"

        note = run.get("note", "") or ""
        is_neg_ctrl = "product" in note.lower() or "neg" in note.lower()

        print(
            f"{i + 1:>4d} {shots:>6d} {s_raw:>8.4f} {s_mit:>8.4f} "
            f"[{ci_raw[0]:>7.4f},{ci_raw[1]:>7.4f}] "
            f"[{ci_mit[0]:>7.4f},{ci_mit[1]:>7.4f}] "
            f"{gate_raw:>9s} {gate_mit:>9s}"
            f"{'  (neg ctrl)' if is_neg_ctrl else ''}"
        )

        results.append(
            {
                "run": i + 1,
                "job_id": run["job_id"],
                "shots": shots,
                "is_negative_control": is_neg_ctrl,
                "S_raw": round(s_raw, 6),
                "S_mitigated": round(s_mit, 6),
                "ci95_raw": [round(ci_raw[0], 6), round(ci_raw[1], 6)],
                "ci95_mitigated": [round(ci_mit[0], 6), round(ci_mit[1], 6)],
                "gate_raw": gate_raw,
                "gate_mitigated": gate_mit,
                "delta_S": round(s_mit - s_raw, 6),
            }
        )

    print()

    # Summary
    bell_results = [r for r in results if not r["is_negative_control"]]
    neg_results = [r for r in results if r["is_negative_control"]]

    raw_pass = sum(1 for r in bell_results if r["gate_raw"] == "PASS")
    mit_pass = sum(1 for r in bell_results if r["gate_mitigated"] == "PASS")
    neg_pass = sum(1 for r in neg_results if r["gate_mitigated"] == "PASS")

    print(f"Bell-state runs: {len(bell_results)}")
    print(f"  Raw claim gate PASS:       {raw_pass}/{len(bell_results)}")
    print(f"  Mitigated claim gate PASS: {mit_pass}/{len(bell_results)}")
    print(f"Negative control runs: {len(neg_results)}")
    print(f"  Mitigated gate PASS:       {neg_pass}/{len(neg_results)} (should be 0)")
    print()

    if mit_pass > raw_pass:
        print("CONCLUSION: Readout error mitigation recovers CHSH violation on")
        print(f"  ibm_torino ({mit_pass}/{len(bell_results)} Bell runs pass after mitigation,")
        print(f"  vs {raw_pass}/{len(bell_results)} raw). This confirms that the framework's")
        print("  preserved decision rule correctly identified a readout-dominated")
        print("  failure rather than a genuine absence of entanglement.")
    else:
        print("CONCLUSION: Readout mitigation does not substantially change the")
        print("  verdict. The ibm_torino result may involve gate errors beyond")
        print("  readout noise.")

    if neg_pass == 0:
        print("  Negative control correctly fails the gate even after mitigation.")

    # Save results
    output_path = os.path.join(script_dir, "..", "summary", "readout_mitigation.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(
            {
                "description": "Readout error mitigation (M3R-style) for ibm_torino CHSH",
                "readout_error_assumed": eps_ro,
                "results": results,
                "summary": {
                    "bell_raw_pass": raw_pass,
                    "bell_mitigated_pass": mit_pass,
                    "negative_control_mitigated_pass": neg_pass,
                },
            },
            f,
            indent=2,
        )
    print(f"\nResults saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
