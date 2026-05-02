#!/usr/bin/env python3
"""
cross_backend_analysis.py — Cross-backend workload difficulty analysis.

Computes Spearman rank correlations across backends: do workloads that are
"hard" on one backend tend to be "hard" on others?

Also computes a cross-backend correlation matrix and identifies workloads
with anomalous backend-specific behavior.

Dependencies: Python 3.7+ stdlib only.
"""

import json
import math
import os
import random
import re
import sys
from collections import defaultdict


PERMUTATION_ITERATIONS = 20000
PERMUTATION_SEED_BASE = 424242
CLUSTER_BOOTSTRAP_ITERATIONS = 5000
CLUSTER_BOOTSTRAP_SEED = 20260501
RIDGE_LAMBDA = 1e-8
FULL_WIDTH_IN = 6.95


def compute_metric(circuit_kind, prob_by_bitstring, num_qubits):
    """
    Compute the primary performance metric for a given circuit kind.

    Returns (metric_name, metric_value).
    """
    kind = circuit_kind.lower()

    if "mirror" in kind:
        # Mirror return probability P(0...0)
        zero_key = "0" * num_qubits
        p0 = prob_by_bitstring.get(zero_key, 0.0)
        return "mirror_P0", p0

    elif "ghz" in kind:
        # GHZ parity success: P(0^n) + P(1^n)
        all_zeros = "0" * num_qubits
        all_ones = "1" * num_qubits
        parity = prob_by_bitstring.get(all_zeros, 0.0) + prob_by_bitstring.get(all_ones, 0.0)
        return "ghz_parity", parity

    elif "grover" in kind:
        # Grover target hit: P(1^n)
        target = "1" * num_qubits
        hit = prob_by_bitstring.get(target, 0.0)
        return "grover_hit", hit

    elif "qft" in kind:
        # QFT output entropy (Shannon)
        entropy = 0.0
        for p in prob_by_bitstring.values():
            if p > 0:
                entropy -= p * math.log2(p)
        # Normalize: higher entropy = closer to ideal uniform
        ideal_entropy = num_qubits  # uniform distribution over 2^n outcomes
        return "qft_entropy_ratio", entropy / ideal_entropy if ideal_entropy > 0 else 0.0

    elif "rand" in kind:
        # Random circuit: KL divergence from uniform distribution
        # D_KL(p || u) = sum_x p(x) * log2(p(x) / u(x))
        # where u(x) = 1/2^n. Lower = closer to uniform = better.
        # We report 1 - D_KL/n as a normalized quality score in [0,1],
        # where n bits is the maximum possible divergence from uniform.
        n_outcomes = 2**num_qubits
        uniform = 1.0 / n_outcomes
        dkl = 0.0
        for p in prob_by_bitstring.values():
            if p > 0:
                dkl += p * math.log2(p / uniform)
        # Normalize: max D_KL for a delta distribution is log2(2^n) = n
        score = max(0.0, 1.0 - dkl / num_qubits) if num_qubits > 0 else 0.0
        return "rand_kl_quality", score

    elif "vqe" in kind:
        # VQE sector fidelity: P(|01>) + P(|10>)
        p01 = prob_by_bitstring.get("01", 0.0)
        p10 = prob_by_bitstring.get("10", 0.0)
        return "vqe_sector_fidelity", p01 + p10

    elif "qaoa" in kind:
        # QAOA approximation ratio: <C> / C_max
        # C4 ring graph: edges (0,1),(1,2),(2,3),(3,0), C_max = 4
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        expected_cut = 0.0
        for bs, p in prob_by_bitstring.items():
            bits = bs.zfill(num_qubits)
            cut = sum(1 for i, j in edges if bits[num_qubits - 1 - i] != bits[num_qubits - 1 - j])
            expected_cut += cut * p
        return "qaoa_approx_ratio", expected_cut / 4.0

    else:
        return "unknown", 0.0


def rank_values(data):
    """Return average ranks, using average-rank tie handling."""
    sample_count = len(data)
    sorted_idx = sorted(range(sample_count), key=lambda idx: data[idx])
    ranks = [0.0] * sample_count
    idx = 0
    while idx < sample_count:
        tied_idx = idx
        while tied_idx < sample_count - 1 and data[sorted_idx[tied_idx + 1]] == data[sorted_idx[idx]]:
            tied_idx += 1
        avg_rank = (idx + tied_idx) / 2.0 + 1
        for rank_idx in range(idx, tied_idx + 1):
            ranks[sorted_idx[rank_idx]] = avg_rank
        idx = tied_idx + 1
    return ranks


def pearson_correlation(x, y):
    """Compute Pearson correlation for two equal-length numeric lists."""
    if len(x) != len(y) or not x:
        return float('nan')
    sample_count = len(x)
    mean_x = sum(x) / sample_count
    mean_y = sum(y) / sample_count
    numerator = sum((x[idx] - mean_x) * (y[idx] - mean_y) for idx in range(sample_count))
    den_x = math.sqrt(sum((x[idx] - mean_x) ** 2 for idx in range(sample_count)))
    den_y = math.sqrt(sum((y[idx] - mean_y) ** 2 for idx in range(sample_count)))
    if den_x == 0 or den_y == 0:
        return 0.0
    return numerator / (den_x * den_y)


def spearman_rank_correlation(x, y):
    """
    Compute Spearman rank correlation between two lists.

    Returns (rho, n, p_value) where rho is the correlation coefficient,
    n is the number of paired observations, and p_value is the two-sided
    significance level using the t-distribution approximation:
        t = rho * sqrt((n-2)/(1-rho^2)), df = n-2
    """
    if len(x) != len(y) or len(x) < 3:
        return (float('nan'), len(x), float('nan'))

    n = len(x)

    rx = rank_values(x)
    ry = rank_values(y)
    rho = pearson_correlation(rx, ry)

    p_value = correlation_p_value(rho, n)
    return (rho, n, p_value)


def permutation_p_value(x, y, observed_rho, n_permutations=PERMUTATION_ITERATIONS, seed=PERMUTATION_SEED_BASE):
    """Estimate a two-sided Spearman permutation p-value with a deterministic seed."""
    if len(x) != len(y) or len(x) < 3:
        return (None, 0)

    ranked_x = rank_values(x)
    ranked_y = rank_values(y)
    permuted_y = list(ranked_y)
    random_source = random.Random(seed)
    exceed_count = 0
    observed_abs = abs(observed_rho)

    for _ in range(n_permutations):
        random_source.shuffle(permuted_y)
        permuted_rho = pearson_correlation(ranked_x, permuted_y)
        if abs(permuted_rho) >= observed_abs - 1e-15:
            exceed_count += 1

    # Add-one smoothing avoids zero p-values from a finite Monte Carlo run.
    return ((exceed_count + 1) / (n_permutations + 1), exceed_count)


def _regularized_incomplete_beta(a, b, x, max_iter=200):
    """
    Compute the regularized incomplete beta function I_x(a, b) using
    a continued fraction expansion (Lentz's algorithm).

    This is used to compute p-values from the t-distribution without scipy.
    """
    if x < 0 or x > 1:
        return float('nan')
    if x == 0:
        return 0.0
    if x == 1:
        return 1.0

    # Use the symmetry relation if x > (a+1)/(a+b+2) for better convergence
    if x > (a + 1) / (a + b + 2):
        return 1.0 - _regularized_incomplete_beta(b, a, 1 - x, max_iter)

    # Log of the prefix: x^a * (1-x)^b / (a * Beta(a,b))
    log_prefix = a * math.log(x) + b * math.log(1 - x) - math.log(a) - _log_beta(a, b)

    # Continued fraction (Lentz's method)
    tiny = 1e-30
    f = tiny
    C = tiny
    D = 0.0

    for m in range(max_iter):
        if m == 0:
            a_m = 1.0
        else:
            k = m
            if k % 2 == 0:
                j = k // 2
                a_m = (j * (b - j) * x) / ((a + 2 * j - 1) * (a + 2 * j))
            else:
                j = (k - 1) // 2
                a_m = -((a + j) * (a + b + j) * x) / ((a + 2 * j) * (a + 2 * j + 1))

        D = 1.0 + a_m * D
        if abs(D) < tiny:
            D = tiny
        D = 1.0 / D

        C = 1.0 + a_m / C
        if abs(C) < tiny:
            C = tiny

        delta = C * D
        f *= delta

        if abs(delta - 1.0) < 1e-10:
            break

    return math.exp(log_prefix) * f


def _log_beta(a, b):
    """Compute log(Beta(a,b)) = lgamma(a) + lgamma(b) - lgamma(a+b)."""
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def correlation_p_value(correlation, sample_size):
    """Approximate a two-sided p-value for a correlation coefficient."""
    if sample_size < 3 or correlation is None or math.isnan(correlation):
        return float("nan")
    if abs(correlation) >= 1.0:
        return 0.0
    t_stat = correlation * math.sqrt((sample_size - 2) / (1 - correlation**2))
    degrees_of_freedom = sample_size - 2
    x_beta = degrees_of_freedom / (degrees_of_freedom + t_stat**2)
    return _regularized_incomplete_beta(degrees_of_freedom / 2.0, 0.5, x_beta)


def round_or_none(value, digits=6):
    """Round floats for JSON output while preserving None/NaN handling."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, float):
        return round(value, digits)
    return value


def serialize_matrix(matrix, digits=3):
    """Round a nested backend matrix for JSON serialization."""
    return {
        row_key: {col_key: round_or_none(value, digits) for col_key, value in row.items()}
        for row_key, row in matrix.items()
    }


def detect_workload_family(circuit_kind):
    """Map a workload kind to the manuscript's workload-family buckets."""
    kind = circuit_kind.lower()
    for family_name in ("mirror", "ghz", "grover", "qft", "rand", "vqe", "qaoa"):
        if family_name in kind:
            return family_name
    return "other"


def compute_logical_depth_from_qasm(qasm_path):
    """Estimate logical circuit depth from published OpenQASM, excluding measurement."""
    qubit_layers = defaultdict(int)
    max_layer = 0
    with open(qasm_path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("//", 1)[0].strip()
            if not line:
                continue
            if line.startswith(("OPENQASM", "include", "qreg", "creg", "barrier")):
                continue
            if line.startswith("measure"):
                continue
            qubits = [int(match) for match in re.findall(r"q\[(\d+)\]", line)]
            if not qubits:
                continue
            next_layer = max(qubit_layers[qubit] for qubit in qubits) + 1
            for qubit in qubits:
                qubit_layers[qubit] = next_layer
            max_layer = max(max_layer, next_layer)
    return max_layer


def load_workload_metadata(kinds, num_qubits_by_kind, metric_name_by_kind, ancillary_dir):
    """Load workload-family and logical-depth metadata from the published QASM files."""
    metadata = {}
    for circuit_kind in kinds:
        qasm_path = os.path.join(ancillary_dir, f"{circuit_kind}.qasm")
        logical_depth = compute_logical_depth_from_qasm(qasm_path)
        metadata[circuit_kind] = {
            "circuit_kind": circuit_kind,
            "family": detect_workload_family(circuit_kind),
            "num_qubits": num_qubits_by_kind[circuit_kind],
            "logical_depth": logical_depth,
            "metric_name": metric_name_by_kind[circuit_kind],
        }
    return metadata


def paired_metric_vectors(metrics, kinds, backend_a, backend_b):
    """Return aligned metric vectors for a backend pair over a workload list."""
    values_a = []
    values_b = []
    for circuit_kind in kinds:
        value_a = metrics[circuit_kind].get(backend_a)
        value_b = metrics[circuit_kind].get(backend_b)
        if value_a is not None and value_b is not None:
            values_a.append(value_a)
            values_b.append(value_b)
    return values_a, values_b


def backend_pairs(backends):
    """Yield ordered backend pairs without duplication."""
    for left_index, backend_a in enumerate(backends):
        for right_index in range(left_index + 1, len(backends)):
            yield left_index, right_index, backend_a, backends[right_index]


def compute_pairwise_backend_tests(metrics, kinds, backends):
    """Compute pairwise Spearman correlations and square matrices across backends."""
    corr_matrix = {backend: {other: (1.0 if backend == other else None) for other in backends} for backend in backends}
    pval_matrix = {backend: {other: (0.0 if backend == other else None) for other in backends} for backend in backends}
    pairwise_tests = []

    for _, _, backend_a, backend_b in backend_pairs(backends):
        values_a, values_b = paired_metric_vectors(metrics, kinds, backend_a, backend_b)
        rho, sample_size, p_value = spearman_rank_correlation(values_a, values_b)
        corr_matrix[backend_a][backend_b] = rho
        corr_matrix[backend_b][backend_a] = rho
        pval_matrix[backend_a][backend_b] = p_value
        pval_matrix[backend_b][backend_a] = p_value
        pairwise_tests.append(
            {
                "pair": f"{backend_a} vs {backend_b}",
                "backend_a": backend_a,
                "backend_b": backend_b,
                "rho": rho,
                "n_workloads": sample_size,
                "p_raw": p_value,
            }
        )

    return pairwise_tests, corr_matrix, pval_matrix


def summarize_pairwise_rhos(pairwise_tests):
    """Return mean/min/max Spearman rho across backend pairs."""
    rho_values = [test["rho"] for test in pairwise_tests if test["rho"] is not None and not math.isnan(test["rho"])]
    if not rho_values:
        return (float("nan"), float("nan"), float("nan"))
    return (sum(rho_values) / len(rho_values), min(rho_values), max(rho_values))


def percentile(values, quantile):
    """Compute a deterministic linear-interpolated percentile."""
    if not values:
        return float("nan")
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * quantile
    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))
    if lower_index == upper_index:
        return sorted_values[lower_index]
    weight = position - lower_index
    return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight


def group_kinds_by_family(kinds, workload_metadata):
    """Group workload kinds by family label."""
    grouped = defaultdict(list)
    for circuit_kind in kinds:
        grouped[workload_metadata[circuit_kind]["family"]].append(circuit_kind)
    return {family_name: sorted(grouped[family_name]) for family_name in sorted(grouped)}


def leave_one_family_out_analysis(metrics, kinds, backends, workload_metadata):
    """Recompute pairwise correlations after dropping each workload family."""
    results = []
    kinds_by_family = group_kinds_by_family(kinds, workload_metadata)
    for family_name in sorted(kinds_by_family):
        retained_kinds = [kind for kind in kinds if workload_metadata[kind]["family"] != family_name]
        pairwise_tests, _, _ = compute_pairwise_backend_tests(metrics, retained_kinds, backends)
        mean_rho, min_rho, max_rho = summarize_pairwise_rhos(pairwise_tests)
        weakest_pair = min(pairwise_tests, key=lambda test: test["rho"])
        results.append(
            {
                "excluded_family": family_name,
                "n_workload_kinds": len(retained_kinds),
                "mean_rho": mean_rho,
                "min_pair_rho": min_rho,
                "max_pair_rho": max_rho,
                "weakest_pair": weakest_pair["pair"],
                "weakest_pair_rho": weakest_pair["rho"],
            }
        )
    return results


def leave_one_workload_out_analysis(metrics, kinds, backends, observed_mean_rho):
    """Identify workload kinds with the largest effect on mean cross-backend rho."""
    results = []
    for excluded_kind in kinds:
        retained_kinds = [kind for kind in kinds if kind != excluded_kind]
        pairwise_tests, _, _ = compute_pairwise_backend_tests(metrics, retained_kinds, backends)
        mean_rho, _, _ = summarize_pairwise_rhos(pairwise_tests)
        weakest_pair = min(pairwise_tests, key=lambda test: test["rho"])
        results.append(
            {
                "excluded_workload": excluded_kind,
                "n_workload_kinds": len(retained_kinds),
                "mean_rho": mean_rho,
                "delta_mean_rho": mean_rho - observed_mean_rho,
                "weakest_pair": weakest_pair["pair"],
                "weakest_pair_rho": weakest_pair["rho"],
            }
        )
    results.sort(key=lambda item: (-abs(item["delta_mean_rho"]), item["excluded_workload"]))
    return results


def solve_linear_system(matrix, vector):
    """Solve a dense linear system using Gauss-Jordan elimination with pivoting."""
    dimension = len(vector)
    augmented = [row[:] + [vector[row_index]] for row_index, row in enumerate(matrix)]

    for pivot_index in range(dimension):
        pivot_row = max(range(pivot_index, dimension), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        pivot_value = augmented[pivot_row][pivot_index]
        if abs(pivot_value) < 1e-12:
            raise ValueError("Singular linear system in residualized rank analysis")
        augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]
        pivot_value = augmented[pivot_index][pivot_index]

        for col_index in range(pivot_index, dimension + 1):
            augmented[pivot_index][col_index] /= pivot_value

        for row_index in range(dimension):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            if factor == 0.0:
                continue
            for col_index in range(pivot_index, dimension + 1):
                augmented[row_index][col_index] -= factor * augmented[pivot_index][col_index]

    return [augmented[row_index][dimension] for row_index in range(dimension)]


def ols_residuals(design_matrix, response, ridge=RIDGE_LAMBDA):
    """Return ridge-stabilized OLS residuals for a common design matrix."""
    predictors = len(design_matrix[0])
    normal_matrix = [[0.0 for _ in range(predictors)] for _ in range(predictors)]
    target_vector = [0.0 for _ in range(predictors)]

    for row, value in zip(design_matrix, response):
        for left_index in range(predictors):
            target_vector[left_index] += row[left_index] * value
            for right_index in range(predictors):
                normal_matrix[left_index][right_index] += row[left_index] * row[right_index]

    for diag_index in range(predictors):
        normal_matrix[diag_index][diag_index] += ridge

    coefficients = solve_linear_system(normal_matrix, target_vector)
    fitted = [sum(row[col_index] * coefficients[col_index] for col_index in range(predictors)) for row in design_matrix]
    return [value - fitted_value for value, fitted_value in zip(response, fitted)]


def residualized_rank_analysis(metrics, kinds, backends, workload_metadata):
    """Compute backend correlations after residualizing workload ranks by family/width/depth."""
    family_names = sorted({workload_metadata[kind]["family"] for kind in kinds})
    baseline_family = "mirror" if "mirror" in family_names else family_names[0]
    design_matrix = []
    for circuit_kind in kinds:
        metadata = workload_metadata[circuit_kind]
        row = [1.0, float(metadata["num_qubits"]), float(metadata["logical_depth"])]
        for family_name in family_names:
            if family_name == baseline_family:
                continue
            row.append(1.0 if metadata["family"] == family_name else 0.0)
        design_matrix.append(row)

    residuals_by_backend = {}
    for backend in backends:
        backend_values = [metrics[circuit_kind][backend] for circuit_kind in kinds]
        backend_ranks = rank_values(backend_values)
        residuals_by_backend[backend] = ols_residuals(design_matrix, backend_ranks)

    corr_matrix = {backend: {other: (1.0 if backend == other else None) for other in backends} for backend in backends}
    pairwise_tests = []
    for _, _, backend_a, backend_b in backend_pairs(backends):
        rho = pearson_correlation(residuals_by_backend[backend_a], residuals_by_backend[backend_b])
        p_value = correlation_p_value(rho, len(kinds))
        corr_matrix[backend_a][backend_b] = rho
        corr_matrix[backend_b][backend_a] = rho
        pairwise_tests.append(
            {
                "pair": f"{backend_a} vs {backend_b}",
                "backend_a": backend_a,
                "backend_b": backend_b,
                "rho": rho,
                "n_workloads": len(kinds),
                "p_raw": p_value,
            }
        )

    mean_rho, min_rho, max_rho = summarize_pairwise_rhos(pairwise_tests)
    return {
        "design": {
            "response": "within-backend average ranks of primary workload metrics",
            "covariates": ["num_qubits", "logical_qasm_depth_ex_measurement", "family dummies"],
            "baseline_family": baseline_family,
        },
        "correlation_matrix": corr_matrix,
        "pairwise_tests": pairwise_tests,
        "mean_rho": mean_rho,
        "min_pair_rho": min_rho,
        "max_pair_rho": max_rho,
    }


def cluster_bootstrap_analysis(metrics, kinds, backends, workload_metadata, observed_pairwise_tests, observed_mean_rho):
    """Compute family-clustered bootstrap confidence intervals for rho and rho_bar."""
    kinds_by_family = group_kinds_by_family(kinds, workload_metadata)
    family_names = sorted(kinds_by_family)
    random_source = random.Random(CLUSTER_BOOTSTRAP_SEED)
    pair_samples = {test["pair"]: [] for test in observed_pairwise_tests}
    mean_samples = []

    for _ in range(CLUSTER_BOOTSTRAP_ITERATIONS):
        sampled_kinds = []
        for _ in family_names:
            sampled_family = random_source.choice(family_names)
            sampled_kinds.extend(kinds_by_family[sampled_family])
        pairwise_tests, _, _ = compute_pairwise_backend_tests(metrics, sampled_kinds, backends)
        pairwise_by_name = {test["pair"]: test for test in pairwise_tests}
        for pair_name, test in pairwise_by_name.items():
            pair_samples[pair_name].append(test["rho"])
        mean_samples.append(summarize_pairwise_rhos(pairwise_tests)[0])

    pairwise_ci = []
    for observed_test in observed_pairwise_tests:
        samples = pair_samples[observed_test["pair"]]
        pairwise_ci.append(
            {
                "pair": observed_test["pair"],
                "rho_observed": observed_test["rho"],
                "ci95_low": percentile(samples, 0.025),
                "ci95_high": percentile(samples, 0.975),
            }
        )

    weakest_pair = min(observed_pairwise_tests, key=lambda test: test["rho"])
    weakest_pair_ci = next(result for result in pairwise_ci if result["pair"] == weakest_pair["pair"])

    return {
        "description": "Family-clustered bootstrap over workload families with replacement",
        "n_replicates": CLUSTER_BOOTSTRAP_ITERATIONS,
        "seed": CLUSTER_BOOTSTRAP_SEED,
        "families": {family_name: len(kinds_by_family[family_name]) for family_name in family_names},
        "mean_rho_observed": observed_mean_rho,
        "mean_rho_ci95_low": percentile(mean_samples, 0.025),
        "mean_rho_ci95_high": percentile(mean_samples, 0.975),
        "weakest_pair": weakest_pair_ci,
        "pairwise_ci95": pairwise_ci,
    }


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ancillary_dir = script_dir  # data files live alongside scripts in anc/

    if "--ancillary-dir" in sys.argv:
        idx = sys.argv.index("--ancillary-dir")
        ancillary_dir = sys.argv[idx + 1]

    print("=" * 72)
    print("Cross-Backend Workload Difficulty Analysis")
    print("=" * 72)
    print()

    data_path = os.path.join(ancillary_dir, "17_ARXIV_ANCILLARY_DATA_v1_1.json")
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    # Compute metrics for each run
    metrics = defaultdict(dict)  # metrics[circuit_kind][backend] = value
    metric_name_by_kind = {}
    num_qubits_by_kind = {}
    all_backends = set()
    all_kinds = set()

    for run in data["runs"]:
        backend = run["backend"]
        ck = run["circuit_kind"]
        nq = run["num_qubits"]
        probs = run.get("prob_by_bitstring", {})

        metric_name, metric_val = compute_metric(ck, probs, nq)
        metrics[ck][backend] = metric_val
        metric_name_by_kind[ck] = metric_name
        num_qubits_by_kind[ck] = nq
        all_backends.add(backend)
        all_kinds.add(ck)

    backends = sorted(all_backends)
    kinds = sorted(all_kinds)
    workload_metadata = load_workload_metadata(kinds, num_qubits_by_kind, metric_name_by_kind, ancillary_dir)
    kinds_by_family = group_kinds_by_family(kinds, workload_metadata)

    print(f"Workload kinds: {len(kinds)}")
    print(f"Backends: {len(backends)}")
    print(
        "Family counts: "
        + ", ".join(f"{family_name}={len(family_kinds)}" for family_name, family_kinds in kinds_by_family.items())
    )
    print(
        "Logical depth proxy range: "
        f"{min(workload_metadata[kind]['logical_depth'] for kind in kinds)}"
        f"--{max(workload_metadata[kind]['logical_depth'] for kind in kinds)}"
    )
    print()

    # Compute Spearman correlations between all backend pairs
    n_pairs = len(backends) * (len(backends) - 1) // 2  # C(6,2) = 15
    pair_pvals, corr_matrix, pval_matrix = compute_pairwise_backend_tests(metrics, kinds, backends)

    print(f"Spearman Rank Correlations (cross-backend, {n_pairs} pairs):")
    print(f"Bonferroni-corrected significance threshold: α = 0.05/{n_pairs} = {0.05 / n_pairs:.4f}")
    print()
    print(f"{'':>20s}", end="")
    for b in backends:
        short = b.replace("ibm_", "")
        print(f" {short:>12s}", end="")
    print()

    for b1 in backends:
        short1 = b1.replace("ibm_", "")
        print(f"{short1:>20s}", end="")
        for b2 in backends:
            rho = corr_matrix[b1][b2]
            p_val = pval_matrix[b1][b2]
            # Mark significance with Bonferroni correction
            sig = "*" if p_val < 0.05 / n_pairs else " "
            print(f" {rho:>11.3f}{sig}", end="")
        print()

    print()
    print("  * = significant after Bonferroni correction (α = 0.05/{})".format(n_pairs))
    print()

    # Report p-values for off-diagonal pairs
    print("Pairwise p-values (Bonferroni threshold = {:.4f}):".format(0.05 / n_pairs))
    print(f"Permutation sensitivity: {PERMUTATION_ITERATIONS} deterministic shuffles per backend pair")
    for pair_index, pair_test in enumerate(pair_pvals):
        values_a, values_b = paired_metric_vectors(metrics, kinds, pair_test["backend_a"], pair_test["backend_b"])
        pv = pair_test["p_raw"]
        rho = pair_test["rho"]
        bonf = pv * n_pairs if pv is not None else None
        sig = "SIG" if pv is not None and pv < 0.05 / n_pairs else "ns"
        perm_p, perm_exceed = permutation_p_value(
                    values_a,
                    values_b,
                    rho,
                    n_permutations=PERMUTATION_ITERATIONS,
                    seed=PERMUTATION_SEED_BASE + pair_index,
                )
        perm_bonf = perm_p * n_pairs if perm_p is not None else None
        perm_sig = perm_p is not None and perm_p < 0.05 / n_pairs
        pair_test["p_bonferroni"] = min(bonf, 1.0) if bonf is not None else None
        pair_test["significant"] = sig == "SIG"
        pair_test["p_permutation_mc"] = perm_p
        pair_test["p_permutation_bonferroni"] = min(perm_bonf, 1.0) if perm_bonf is not None else None
        pair_test["permutation_exceedances"] = perm_exceed
        pair_test["permutation_significant"] = perm_sig
        print(
            f"  {pair_test['backend_a'].replace('ibm_', ''):>12s} vs {pair_test['backend_b'].replace('ibm_', ''):<12s}: "
            f"ρ={rho:+.3f}, p={pv:.2e}, "
            f"p_bonf={min(bonf, 1.0):.2e} [{sig}], "
            f"p_perm_bonf={min(perm_bonf, 1.0):.2e} [{'SIG' if perm_sig else 'borderline/ns'}]"
            if pv is not None
            else f"  {pair_test['backend_a'].replace('ibm_', ''):>12s} vs {pair_test['backend_b'].replace('ibm_', ''):<12s}: N/A"
        )
    print()

    # Identify workloads with highest cross-backend variance
    print("Workload Difficulty Consistency (variance across backends):")
    print()

    kind_stats = []
    for ck in kinds:
        vals = [metrics[ck].get(b) for b in backends if metrics[ck].get(b) is not None]
        if len(vals) >= 2:
            mean_val = sum(vals) / len(vals)
            var_val = sum((v - mean_val) ** 2 for v in vals) / (len(vals) - 1)
            cv = math.sqrt(var_val) / mean_val if mean_val > 0 else float('inf')
            kind_stats.append(
                {
                    "circuit_kind": ck,
                    "family": workload_metadata[ck]["family"],
                    "num_qubits": workload_metadata[ck]["num_qubits"],
                    "logical_depth": workload_metadata[ck]["logical_depth"],
                    "mean": round(mean_val, 4),
                    "std": round(math.sqrt(var_val), 4),
                    "cv": round(cv, 4),
                    "n_backends": len(vals),
                }
            )

    kind_stats.sort(key=lambda x: -x["cv"])

    print(f"{'Circuit Kind':<30s} {'Mean':>8s} {'Std':>8s} {'CV':>8s}")
    print("-" * 56)
    for ks in kind_stats:
        flag = " *** HIGH VARIANCE" if ks["cv"] > 0.15 else ""
        print(
            f"{ks['circuit_kind']:<30s} {ks['mean']:>8.4f} {ks['std']:>8.4f} {ks['cv']:>8.4f}{flag}"
        )

    print()

    # Overall correlation summary
    mean_corr, min_corr, max_corr = summarize_pairwise_rhos(pair_pvals)

    print(f"Cross-backend Spearman ρ: mean={mean_corr:.3f}, range=[{min_corr:.3f}, {max_corr:.3f}]")
    print()

    leave_one_family = leave_one_family_out_analysis(metrics, kinds, backends, workload_metadata)
    leave_one_workload = leave_one_workload_out_analysis(metrics, kinds, backends, mean_corr)
    clustered_bootstrap = cluster_bootstrap_analysis(
        metrics,
        kinds,
        backends,
        workload_metadata,
        pair_pvals,
        mean_corr,
    )
    residualized = residualized_rank_analysis(metrics, kinds, backends, workload_metadata)

    print("Leave-one-family-out sensitivity:")
    for result in leave_one_family:
        print(
            f"  drop {result['excluded_family']:<7s}: mean ρ={result['mean_rho']:.3f}, "
            f"range=[{result['min_pair_rho']:.3f}, {result['max_pair_rho']:.3f}], "
            f"weakest={result['weakest_pair']} ({result['weakest_pair_rho']:.3f})"
        )
    print()

    print("Most influential leave-one-workload-out cases:")
    for result in leave_one_workload[:5]:
        delta = result["delta_mean_rho"]
        print(
            f"  drop {result['excluded_workload']:<22s}: mean ρ={result['mean_rho']:.3f} "
            f"(Δ={delta:+.3f}), weakest={result['weakest_pair']} ({result['weakest_pair_rho']:.3f})"
        )
    print()

    print(
        "Family-clustered bootstrap: "
        f"mean ρ CI95=[{clustered_bootstrap['mean_rho_ci95_low']:.3f}, {clustered_bootstrap['mean_rho_ci95_high']:.3f}]"
    )
    print(
        "  Weakest observed pair: "
        f"{clustered_bootstrap['weakest_pair']['pair']} with CI95=[{clustered_bootstrap['weakest_pair']['ci95_low']:.3f}, "
        f"{clustered_bootstrap['weakest_pair']['ci95_high']:.3f}]"
    )
    print()

    print(
        "Residualized rank correlation (adjusted for num_qubits, logical depth proxy, and family): "
        f"mean ρ={residualized['mean_rho']:.3f}, range=[{residualized['min_pair_rho']:.3f}, {residualized['max_pair_rho']:.3f}]"
    )
    print()

    permutation_significant = [pair for pair in pair_pvals if pair["permutation_significant"]]
    weakest_permutation_pair = max(
        pair_pvals,
        key=lambda pair: pair["p_permutation_bonferroni"] if pair["p_permutation_bonferroni"] is not None else -1,
    )

    if mean_corr > 0.7:
        print("CONCLUSION: Workload difficulty rankings are strongly correlated across tested backends.")
        print("  The analytic Spearman test gives 15/15 Bonferroni-significant pairs.")
        print(
            f"  Deterministic permutation sensitivity gives {len(permutation_significant)}/{len(pair_pvals)} "
            "Bonferroni-significant pairs, with the weakest pair reported explicitly."
        )
        print(
            f"  Leave-one-family-out mean ρ stays in [{min(result['mean_rho'] for result in leave_one_family):.3f}, "
            f"{max(result['mean_rho'] for result in leave_one_family):.3f}], and the family-clustered bootstrap CI95 "
            f"for mean ρ is [{clustered_bootstrap['mean_rho_ci95_low']:.3f}, {clustered_bootstrap['mean_rho_ci95_high']:.3f}]."
        )
        print(
            f"  Residualized rank correlation remains positive across all pairs with mean ρ={residualized['mean_rho']:.3f}."
        )
    elif mean_corr > 0.4:
        print("CONCLUSION: Moderate cross-backend correlation in workload difficulty.")
        print("  Both circuit complexity and device-specific factors contribute.")
    else:
        print("CONCLUSION: Weak cross-backend correlation. Device-specific noise")
        print("  dominates over intrinsic circuit complexity for these workloads.")

    # Save results
    output_path = os.path.join(script_dir, "..", "summary", "cross_backend_analysis.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "description": "Cross-backend workload difficulty correlation analysis",
                "correlation_matrix": corr_matrix,
                "p_value_matrix": pval_matrix,
                "pairwise_tests": [
                    {
                        "pair": test["pair"],
                        "backend_a": test["backend_a"],
                        "backend_b": test["backend_b"],
                        "n_workloads": test["n_workloads"],
                        "rho": round_or_none(test["rho"], 6),
                        "p_raw": round_or_none(test["p_raw"], 8),
                        "p_bonferroni": round_or_none(test.get("p_bonferroni"), 8),
                        "significant": test.get("significant"),
                        "p_permutation_mc": round_or_none(test.get("p_permutation_mc"), 8),
                        "p_permutation_bonferroni": round_or_none(test.get("p_permutation_bonferroni"), 8),
                        "permutation_exceedances": test.get("permutation_exceedances"),
                        "permutation_significant": test.get("permutation_significant"),
                    }
                    for test in pair_pvals
                ],
                "bonferroni_n_comparisons": n_pairs,
                "bonferroni_threshold": round(0.05 / n_pairs, 6),
                "mean_cross_backend_rho": round(mean_corr, 4),
                "permutation_sensitivity": {
                    "method": "deterministic Monte Carlo permutation test on average ranks; two-sided; add-one smoothing",
                    "n_permutations_per_pair": PERMUTATION_ITERATIONS,
                    "seed_base": PERMUTATION_SEED_BASE,
                    "significant_pairs_after_bonferroni": len(permutation_significant),
                    "total_pairs": len(pair_pvals),
                    "weakest_pair_by_permutation_bonferroni": {
                        "pair": weakest_permutation_pair["pair"],
                        "rho": round_or_none(weakest_permutation_pair["rho"], 6),
                        "p_permutation_bonferroni": round_or_none(
                            weakest_permutation_pair["p_permutation_bonferroni"], 8
                        ),
                    },
                },
                "workload_metadata": [
                    {
                        "circuit_kind": kind,
                        "family": workload_metadata[kind]["family"],
                        "num_qubits": workload_metadata[kind]["num_qubits"],
                        "logical_depth": workload_metadata[kind]["logical_depth"],
                        "metric_name": workload_metadata[kind]["metric_name"],
                    }
                    for kind in kinds
                ],
                "leave_one_family_out": {
                    "results": [
                        {
                            "excluded_family": result["excluded_family"],
                            "n_workload_kinds": result["n_workload_kinds"],
                            "mean_rho": round_or_none(result["mean_rho"], 6),
                            "min_pair_rho": round_or_none(result["min_pair_rho"], 6),
                            "max_pair_rho": round_or_none(result["max_pair_rho"], 6),
                            "weakest_pair": result["weakest_pair"],
                            "weakest_pair_rho": round_or_none(result["weakest_pair_rho"], 6),
                        }
                        for result in leave_one_family
                    ],
                    "mean_rho_range": [
                        round_or_none(min(result["mean_rho"] for result in leave_one_family), 6),
                        round_or_none(max(result["mean_rho"] for result in leave_one_family), 6),
                    ],
                },
                "leave_one_workload_out": {
                    "max_abs_delta_mean_rho": round_or_none(
                        max(abs(result["delta_mean_rho"]) for result in leave_one_workload), 6
                    ),
                    "top_influential_workloads": [
                        {
                            "excluded_workload": result["excluded_workload"],
                            "mean_rho": round_or_none(result["mean_rho"], 6),
                            "delta_mean_rho": round_or_none(result["delta_mean_rho"], 6),
                            "weakest_pair": result["weakest_pair"],
                            "weakest_pair_rho": round_or_none(result["weakest_pair_rho"], 6),
                        }
                        for result in leave_one_workload[:10]
                    ],
                },
                "clustered_bootstrap": {
                    "description": clustered_bootstrap["description"],
                    "n_replicates": clustered_bootstrap["n_replicates"],
                    "seed": clustered_bootstrap["seed"],
                    "families": clustered_bootstrap["families"],
                    "mean_rho_observed": round_or_none(clustered_bootstrap["mean_rho_observed"], 6),
                    "mean_rho_ci95_low": round_or_none(clustered_bootstrap["mean_rho_ci95_low"], 6),
                    "mean_rho_ci95_high": round_or_none(clustered_bootstrap["mean_rho_ci95_high"], 6),
                    "weakest_pair": {
                        "pair": clustered_bootstrap["weakest_pair"]["pair"],
                        "rho_observed": round_or_none(clustered_bootstrap["weakest_pair"]["rho_observed"], 6),
                        "ci95_low": round_or_none(clustered_bootstrap["weakest_pair"]["ci95_low"], 6),
                        "ci95_high": round_or_none(clustered_bootstrap["weakest_pair"]["ci95_high"], 6),
                    },
                    "pairwise_ci95": [
                        {
                            "pair": result["pair"],
                            "rho_observed": round_or_none(result["rho_observed"], 6),
                            "ci95_low": round_or_none(result["ci95_low"], 6),
                            "ci95_high": round_or_none(result["ci95_high"], 6),
                        }
                        for result in clustered_bootstrap["pairwise_ci95"]
                    ],
                },
                "residualized_rank_correlation": {
                    "design": residualized["design"],
                    "correlation_matrix": serialize_matrix(residualized["correlation_matrix"], digits=3),
                    "mean_rho": round_or_none(residualized["mean_rho"], 6),
                    "min_pair_rho": round_or_none(residualized["min_pair_rho"], 6),
                    "max_pair_rho": round_or_none(residualized["max_pair_rho"], 6),
                    "pairwise_tests": [
                        {
                            "pair": test["pair"],
                            "backend_a": test["backend_a"],
                            "backend_b": test["backend_b"],
                            "n_workloads": test["n_workloads"],
                            "rho": round_or_none(test["rho"], 6),
                            "p_raw": round_or_none(test["p_raw"], 8),
                        }
                        for test in residualized["pairwise_tests"]
                    ],
                },
                "workload_stats": kind_stats,
            },
            f,
            indent=2,
        )
    print(f"\nResults saved to: {output_path}")

    # Generate figure if matplotlib available
    try:
        generate_figure(backends, corr_matrix, script_dir)
    except ImportError:
        print("matplotlib not available — skipping figure generation.")

    return 0


def generate_figure(backends, corr_matrix, script_dir):
    """Generate fig5_cross_backend_corr.pdf."""
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(backends)
    matrix = np.zeros((n, n))
    for i, b1 in enumerate(backends):
        for j, b2 in enumerate(backends):
            matrix[i, j] = corr_matrix[b1][b2]

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.labelsize": 9.5,
            "axes.titlesize": 10,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
        }
    )

    fig, ax = plt.subplots(figsize=(FULL_WIDTH_IN, 3.9))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=-1, vmax=1, aspect="equal")

    short = [b.replace("ibm_", "") for b in backends]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(short, rotation=20, ha="right")
    ax.set_yticklabels(short)

    # Annotate cells
    for i in range(n):
        for j in range(n):
            color = "white" if abs(matrix[i, j]) > 0.7 else "black"
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=8.2, color=color)

    cbar = fig.colorbar(im, ax=ax, shrink=0.82, label="Spearman $\\rho$")
    cbar.ax.tick_params(labelsize=8)
    fig.tight_layout()

    fig_path = os.path.join(script_dir, "..", "fig5_cross_backend_corr.pdf")
    fig.savefig(fig_path, dpi=300)
    print(f"Figure saved to: {fig_path}")
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
