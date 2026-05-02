#!/usr/bin/env python3
"""
validate_ancillaries.py — Validate arXiv ancillary JSON structure.

Checks that ancillary manifests and data files have the required fields
and structural invariants for publication.

Dependencies: Python 3.7+ standard library only.

Usage:
    python validate_ancillaries.py [--ancillary-dir PATH]

Exit codes:
    0 = all validations passed
    1 = validation errors found
    2 = usage error
"""

import json
import os
import sys


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def validate_v1_manifest(data, filename):
    """Validate 09_ARXIV_ANCILLARY_MANIFEST_v1.json structure."""
    errors = []

    # Top-level required fields
    for field in ["kind", "date_utc", "workloads", "chsh_evidence"]:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    if data.get("kind") != "arxiv_ancillary_manifest_v1":
        errors.append(f"Unexpected kind: {data.get('kind')} (expected arxiv_ancillary_manifest_v1)")

    # Workloads
    workloads = data.get("workloads", [])
    if not isinstance(workloads, list) or len(workloads) == 0:
        errors.append("workloads must be a non-empty list")
    for i, w in enumerate(workloads):
        for field in ["id", "sha256", "format"]:
            if field not in w:
                errors.append(f"workloads[{i}] missing field: {field}")
        if "sha256" in w and len(w["sha256"]) != 64:
            errors.append(f"workloads[{i}].sha256 is not 64 hex chars: {w['sha256'][:20]}...")

    # CHSH evidence
    chsh = data.get("chsh_evidence", {})
    if "claim_gate" not in chsh:
        errors.append("chsh_evidence missing claim_gate")
    if "runs" not in chsh:
        errors.append("chsh_evidence missing runs")
    else:
        runs = chsh["runs"]
        if not isinstance(runs, list) or len(runs) == 0:
            errors.append("chsh_evidence.runs must be a non-empty list")
        for i, r in enumerate(runs):
            for field in ["backend", "job_id", "shots", "S", "ci95", "entangled_ci95"]:
                if field not in r:
                    errors.append(f"chsh_evidence.runs[{i}] missing field: {field}")
            if "ci95" in r:
                if not isinstance(r["ci95"], list) or len(r["ci95"]) != 2:
                    errors.append(f"chsh_evidence.runs[{i}].ci95 must be [low, high]")
            if "S" in r and "ci95" in r and isinstance(r["ci95"], list) and len(r["ci95"]) == 2:
                if not (r["ci95"][0] <= r["S"] <= r["ci95"][1]):
                    errors.append(
                        f"chsh_evidence.runs[{i}]: S={r['S']} not within ci95={r['ci95']}"
                    )

    return errors


def validate_v1_data(data, filename):
    """Validate 12_ARXIV_ANCILLARY_DATA_v1.json structure."""
    errors = []

    for field in ["kind", "date_utc", "runs"]:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    if data.get("kind") != "arxiv_ancillary_data_v1":
        errors.append(f"Unexpected kind: {data.get('kind')} (expected arxiv_ancillary_data_v1)")

    runs = data.get("runs", [])
    if not isinstance(runs, list) or len(runs) == 0:
        errors.append("runs must be a non-empty list")

    required_settings = {"a0b0", "a0b1", "a1b0", "a1b1"}
    required_bitstrings = {"00", "01", "10", "11"}

    for i, r in enumerate(runs):
        for field in ["job_id", "shots", "quasi_by_setting"]:
            if field not in r:
                errors.append(f"runs[{i}] missing field: {field}")

        quasi = r.get("quasi_by_setting", {})
        if set(quasi.keys()) != required_settings:
            errors.append(
                f"runs[{i}].quasi_by_setting has keys {set(quasi.keys())}, "
                f"expected {required_settings}"
            )

        for setting, dist in quasi.items():
            if set(dist.keys()) != required_bitstrings:
                errors.append(
                    f"runs[{i}].quasi_by_setting.{setting} has keys "
                    f"{set(dist.keys())}, expected {required_bitstrings}"
                )
            # Check normalization (should sum to ~1.0)
            total = sum(dist.values())
            if abs(total - 1.0) > 0.01:
                errors.append(
                    f"runs[{i}].quasi_by_setting.{setting} sums to {total:.4f} (expected ~1.0)"
                )

    return errors


def validate_v11_manifest(data, filename):
    """Validate v1.1 manifest JSON structure."""
    errors = []

    for field in ["kind", "runs"]:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    runs = data.get("runs", [])
    if not isinstance(runs, list) or len(runs) == 0:
        errors.append("runs must be a non-empty list")

    for i, r in enumerate(runs):
        for field in ["backend", "job_id", "shots", "circuit_kind", "workload_sha256", "status"]:
            if field not in r:
                errors.append(f"runs[{i}] missing field: {field}")
        if "workload_sha256" in r and len(r["workload_sha256"]) != 64:
            errors.append(f"runs[{i}].workload_sha256 is not 64 hex chars")
        if r.get("status") != "DONE":
            errors.append(f"runs[{i}] status={r.get('status')} (expected DONE)")
        if r.get("binding_verified") is not True:
            errors.append(f"runs[{i}] binding_verified={r.get('binding_verified')} (expected true)")

    return errors


def validate_v11_data(data, filename):
    """Validate v1.1 data JSON structure."""
    errors = []

    if "runs" not in data:
        errors.append("Missing top-level field: runs")
        return errors

    runs = data.get("runs", [])
    if not isinstance(runs, list):
        errors.append("runs must be a list")
        return errors

    for i, r in enumerate(runs):
        for field in ["job_id", "shots"]:
            if field not in r:
                errors.append(f"runs[{i}] missing field: {field}")
        if "prob_by_bitstring" not in r and "quasi_by_setting" not in r:
            errors.append(f"runs[{i}] missing both prob_by_bitstring and quasi_by_setting")

    return errors


# File -> validator mapping
VALIDATORS = {
    "09_ARXIV_ANCILLARY_MANIFEST_v1.json": validate_v1_manifest,
    "12_ARXIV_ANCILLARY_DATA_v1.json": validate_v1_data,
    "16_ARXIV_ANCILLARY_MANIFEST_v1_1.json": validate_v11_manifest,
    "17_ARXIV_ANCILLARY_DATA_v1_1.json": validate_v11_data,
    "20_ARXIV_ANCILLARY_MANIFEST_v1_1_S2.json": validate_v11_manifest,
    "21_ARXIV_ANCILLARY_DATA_v1_1_S2.json": validate_v11_data,
}


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_ancillary_dir = script_dir

    ancillary_dir = default_ancillary_dir
    if "--ancillary-dir" in sys.argv:
        idx = sys.argv.index("--ancillary-dir")
        if idx + 1 < len(sys.argv):
            ancillary_dir = sys.argv[idx + 1]

    print("=" * 60)
    print("arXiv Ancillary Schema Validator")
    print("=" * 60)
    print()
    print(f"Scanning: {ancillary_dir}")
    print()

    total_errors = 0
    files_validated = 0

    for filename, validator in VALIDATORS.items():
        filepath = os.path.join(ancillary_dir, filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename} (not found)")
            continue

        files_validated += 1
        print(f"  [VALIDATE] {filename}...")

        try:
            data = load_json(filepath)
        except json.JSONDecodeError as e:
            print(f"             -> FAIL: Invalid JSON: {e}")
            total_errors += 1
            continue

        errors = validator(data, filename)
        if errors:
            print(f"             -> FAIL: {len(errors)} error(s)")
            for err in errors:
                print(f"                {err}")
            total_errors += len(errors)
        else:
            print(f"             -> PASS")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"Files validated: {files_validated}")
    print(f"Total errors:    {total_errors}")

    if total_errors == 0:
        print()
        print("RESULT: All ancillary files pass schema validation.")
        return 0
    else:
        print()
        print(f"RESULT: {total_errors} error(s) found. Fix before publishing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
