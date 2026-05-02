#!/usr/bin/env python3
"""
verify_chsh.py — Standalone CHSH recomputation from arXiv ancillary data.

This script reads the public ancillary files and independently recomputes
CHSH S values and CI95 intervals for every run, then compares against
the reported manifest values.

Dependencies: Python 3.7+ standard library only (json, math, os, sys).
No external packages required.

Usage:
    python verify_chsh.py [--ancillary-dir PATH]

If --ancillary-dir is not specified, the script looks for the ancillary
data files in the same directory as this script (arXiv anc/ layout).

Reference: Section 11 of the accompanying manuscript.
"""

import json
import math
import os
import sys


def load_json(path):
    """Load a JSON file and return its contents."""
    with open(path, "r") as f:
        return json.load(f)


def correlation_conv_a(dist):
    """
    Compute correlation E under Convention A (Alice = first bit, Bob = second bit).

    E = sum_{x,y} (-1)^{x XOR y} * P(xy)

    For bitstrings "00","01","10","11":
      z("00") = (-1)^0 = +1
      z("01") = (-1)^1 = -1
      z("10") = (-1)^1 = -1
      z("11") = (-1)^0 = +1
    """
    p00 = dist.get("00", 0.0)
    p01 = dist.get("01", 0.0)
    p10 = dist.get("10", 0.0)
    p11 = dist.get("11", 0.0)
    return p00 - p01 - p10 + p11


def correlation_conv_b(dist):
    """
    Compute correlation E under Convention B (Alice = second bit, Bob = first bit).

    Under this convention, bitstring "xy" is read as Bob=x, Alice=y, so:
      z("00") = (-1)^{0 XOR 0} = +1
      z("01") = (-1)^{1 XOR 0} = -1  (Alice=1, Bob=0)
      z("10") = (-1)^{0 XOR 1} = -1  (Alice=0, Bob=1)
      z("11") = (-1)^{1 XOR 1} = +1

    Same as Convention A for this symmetric case.
    But with swapped assignment:
      z("01") under B = (-1)^{0 XOR 1} = -1  [Alice=0 (second bit), Bob=1 (first bit)]
      z("10") under B = (-1)^{1 XOR 0} = -1  [Alice=1 (second bit), Bob=0 (first bit)]

    Actually for XOR parity, swapping Alice/Bob doesn't change the result.
    The difference matters for marginal diagnostics, not for E itself.
    """
    p00 = dist.get("00", 0.0)
    p01 = dist.get("01", 0.0)
    p10 = dist.get("10", 0.0)
    p11 = dist.get("11", 0.0)
    return p00 - p01 - p10 + p11


def compute_chsh(e00, e01, e10, e11):
    """Compute CHSH S = E(a0b0) + E(a0b1) + E(a1b0) - E(a1b1)."""
    return e00 + e01 + e10 - e11


def se_correlation(e, n):
    """
    Standard error of correlation E estimated from N shots.
    SE(E) = sqrt((1 - E^2) / N)
    """
    var = max(0.0, 1.0 - e * e)
    return math.sqrt(var / n)


def se_chsh(e00, e01, e10, e11, n):
    """
    Standard error of CHSH S (sum in quadrature of individual SE's).
    SE(S) = sqrt(SE(E00)^2 + SE(E01)^2 + SE(E10)^2 + SE(E11)^2)
    """
    se00 = se_correlation(e00, n)
    se01 = se_correlation(e01, n)
    se10 = se_correlation(e10, n)
    se11 = se_correlation(e11, n)
    return math.sqrt(se00**2 + se01**2 + se10**2 + se11**2)


def ci95(s, se):
    """Compute 95% confidence interval: S +/- 1.96 * SE."""
    margin = 1.96 * se
    return (s - margin, s + margin)


def marginal_delta(dist, party="alice"):
    """
    Compute marginal probability for one party.
    Convention A: Alice = first bit, Bob = second bit.
    Returns P(party=0).
    """
    p00 = dist.get("00", 0.0)
    p01 = dist.get("01", 0.0)
    p10 = dist.get("10", 0.0)
    p11 = dist.get("11", 0.0)
    if party == "alice":
        return p00 + p01  # Alice=0
    else:
        return p00 + p10  # Bob=0


def no_signaling_delta(quasi_by_setting, convention="A"):
    """
    Compute max absolute no-signaling marginal delta.
    For each party, the marginal should not depend on the other party's setting.
    """
    deltas = []

    if convention == "A":
        # Alice marginal: P(A=0|b0) vs P(A=0|b1)
        alice_given_b0_a0 = marginal_delta(quasi_by_setting["a0b0"], "alice")
        alice_given_b1_a0 = marginal_delta(quasi_by_setting["a0b1"], "alice")
        deltas.append(abs(alice_given_b0_a0 - alice_given_b1_a0))

        alice_given_b0_a1 = marginal_delta(quasi_by_setting["a1b0"], "alice")
        alice_given_b1_a1 = marginal_delta(quasi_by_setting["a1b1"], "alice")
        deltas.append(abs(alice_given_b0_a1 - alice_given_b1_a1))

        # Bob marginal: P(B=0|a0) vs P(B=0|a1)
        bob_given_a0_b0 = marginal_delta(quasi_by_setting["a0b0"], "bob")
        bob_given_a1_b0 = marginal_delta(quasi_by_setting["a1b0"], "bob")
        deltas.append(abs(bob_given_a0_b0 - bob_given_a1_b0))

        bob_given_a0_b1 = marginal_delta(quasi_by_setting["a0b1"], "bob")
        bob_given_a1_b1 = marginal_delta(quasi_by_setting["a1b1"], "bob")
        deltas.append(abs(bob_given_a0_b1 - bob_given_a1_b1))

    return max(deltas) if deltas else 0.0


def verify_run(run_data, manifest_run=None):
    """
    Verify a single CHSH run from ancillary data.

    Returns a dict with computed values.
    """
    job_id = run_data["job_id"]
    shots = run_data["shots"]
    quasi = run_data["quasi_by_setting"]

    # Compute correlations under Convention A
    e00_a = correlation_conv_a(quasi["a0b0"])
    e01_a = correlation_conv_a(quasi["a0b1"])
    e10_a = correlation_conv_a(quasi["a1b0"])
    e11_a = correlation_conv_a(quasi["a1b1"])

    s_a = compute_chsh(e00_a, e01_a, e10_a, e11_a)
    se_a = se_chsh(e00_a, e01_a, e10_a, e11_a, shots)
    ci_a = ci95(s_a, se_a)

    # Convention B (for this symmetric observable, same as A)
    e00_b = correlation_conv_b(quasi["a0b0"])
    e01_b = correlation_conv_b(quasi["a0b1"])
    e10_b = correlation_conv_b(quasi["a1b0"])
    e11_b = correlation_conv_b(quasi["a1b1"])

    s_b = compute_chsh(e00_b, e01_b, e10_b, e11_b)

    # No-signaling diagnostic
    ns_delta_a = no_signaling_delta(quasi, "A")

    # Claim gate
    entangled = s_a > 2.0 and ci_a[0] > 2.0

    result = {
        "job_id": job_id,
        "shots": shots,
        "S_conv_A": s_a,
        "S_conv_B": s_b,
        "SE_S": se_a,
        "CI95": ci_a,
        "entangled_ci95": entangled,
        "no_signaling_delta_A": ns_delta_a,
    }

    # Compare against manifest if available
    if manifest_run is not None:
        result["manifest_S"] = manifest_run.get("S")
        result["manifest_ci95"] = manifest_run.get("ci95")
        result["manifest_entangled"] = manifest_run.get("entangled_ci95")

        s_match = abs(s_a - manifest_run["S"]) < 1e-6
        ci_match = (
            abs(ci_a[0] - manifest_run["ci95"][0]) < 1e-4
            and abs(ci_a[1] - manifest_run["ci95"][1]) < 1e-4
        )
        entangled_match = entangled == manifest_run["entangled_ci95"]

        result["S_matches"] = s_match
        result["CI95_matches"] = ci_match
        result["entangled_matches"] = entangled_match
        result["all_match"] = s_match and ci_match and entangled_match

    return result


def main():
    # Determine ancillary directory (default: same dir as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_ancillary_dir = script_dir

    ancillary_dir = default_ancillary_dir
    if "--ancillary-dir" in sys.argv:
        idx = sys.argv.index("--ancillary-dir")
        if idx + 1 < len(sys.argv):
            ancillary_dir = sys.argv[idx + 1]
        else:
            print("Error: --ancillary-dir requires a path argument", file=sys.stderr)
            sys.exit(1)

    # Load files
    manifest_path = os.path.join(ancillary_dir, "09_ARXIV_ANCILLARY_MANIFEST_v1.json")
    data_path = os.path.join(ancillary_dir, "12_ARXIV_ANCILLARY_DATA_v1.json")

    print("=" * 72)
    print("CHSH Verification Script")
    print("=" * 72)
    print()

    if not os.path.exists(manifest_path):
        print(f"Error: manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(data_path):
        print(f"Error: data file not found at {data_path}", file=sys.stderr)
        sys.exit(1)

    manifest = load_json(manifest_path)
    data = load_json(data_path)

    print(f"Manifest: {os.path.basename(manifest_path)}")
    print(f"Data:     {os.path.basename(data_path)}")
    print(f"Manifest runs: {len(manifest['chsh_evidence']['runs'])}")
    print(f"Data runs:     {len(data['runs'])}")
    print()

    # Build manifest lookup by job_id
    manifest_by_job = {}
    for run in manifest["chsh_evidence"]["runs"]:
        manifest_by_job[run["job_id"]] = run

    # Verify each data run
    all_pass = True
    results = []

    for run_data in data["runs"]:
        job_id = run_data["job_id"]
        manifest_run = manifest_by_job.get(job_id)
        result = verify_run(run_data, manifest_run)
        results.append(result)

        # Print result
        status = ""
        if manifest_run is not None:
            if result["all_match"]:
                status = "PASS"
            else:
                status = "MISMATCH"
                all_pass = False
        else:
            status = "NO_MANIFEST"

        note = manifest_run.get("note", "") if manifest_run else ""
        note_str = f"  ({note})" if note else ""

        print(f"[{status:>11s}] job_id={job_id}")
        print(f"             backend={run_data.get('backend', '?'):20s}  shots={result['shots']}")
        print(
            f"             S={result['S_conv_A']:.10f}  "
            f"CI95=[{result['CI95'][0]:.6f}, {result['CI95'][1]:.6f}]  "
            f"entangled={result['entangled_ci95']}{note_str}"
        )

        if manifest_run is not None and not result["all_match"]:
            print(
                f"             EXPECTED S={result['manifest_S']}  "
                f"CI95={result['manifest_ci95']}  "
                f"entangled={result['manifest_entangled']}"
            )
            if not result["S_matches"]:
                diff = abs(result["S_conv_A"] - result["manifest_S"])
                print(f"             S diff: {diff:.12f}")

        print()

    # Summary
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print()

    n_total = len(results)
    n_with_manifest = sum(1 for r in results if "manifest_S" in r)
    n_pass = sum(1 for r in results if r.get("all_match", False))
    n_entangled = sum(1 for r in results if r["entangled_ci95"])
    n_not_entangled = n_total - n_entangled

    print(f"Total runs verified:    {n_total}")
    print(f"With manifest entry:    {n_with_manifest}")
    print(f"All values match:       {n_pass}/{n_with_manifest}")
    print(f"Entangled (CI95 gate):  {n_entangled}")
    print(f"Not entangled:          {n_not_entangled}")
    print()

    # Claim gate summary
    print("Claim gate (S > 2.0 AND CI95_low > 2.0):")
    for r in results:
        gate = "PASS" if r["entangled_ci95"] else "FAIL"
        note = ""
        if "manifest_S" in r:
            mr = manifest_by_job.get(r["job_id"], {})
            if mr.get("note"):
                note = f"  [{mr['note']}]"
        print(
            f"  {r['job_id']}  S={r['S_conv_A']:8.4f}  CI95_low={r['CI95'][0]:8.4f}  {gate}{note}"
        )

    print()

    if all_pass and n_with_manifest > 0:
        print("RESULT: All recomputed values match the manifest. Verification PASSED.")
        return 0
    elif n_with_manifest == 0:
        print(
            "RESULT: No manifest entries found for comparison. "
            "Recomputation complete but unverified against manifest."
        )
        return 1
    else:
        n_fail = n_with_manifest - n_pass
        print(f"RESULT: {n_fail} run(s) did not match the manifest. Verification FAILED.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
