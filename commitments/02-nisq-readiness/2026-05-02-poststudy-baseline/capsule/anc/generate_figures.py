#!/usr/bin/env python3
"""
generate_figures.py — Generate publication figures for the NISQ Readiness paper.

Produces 3 figures from the arXiv ancillary data:
  - fig1_chsh_backends.pdf/png: CHSH S values with CI95 error bars
  - fig2_mirror_depth_sweep.pdf/png: Mirror-1Q P(0) vs depth per backend
  - fig3_v11_heatmap.pdf/png: Cross-backend workload heatmap

Dependencies: matplotlib, numpy (standard scientific Python)

Usage:
    python generate_figures.py [--ancillary-dir PATH] [--output-dir PATH] [--format png|pdf]

If --ancillary-dir is not specified, looks for ../ancillaries/ relative to this script.
If --output-dir is not specified, outputs beside the manuscript.
"""

import json
import math
import os
import sys

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np

    HAS_MPL = True
except ImportError:
    HAS_MPL = False


COLUMN_WIDTH_IN = 3.35
FULL_WIDTH_IN = 6.95


def apply_pub_style():
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.labelsize": 9.5,
            "axes.titlesize": 10,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 7.8,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.minor.width": 0.6,
            "ytick.minor.width": 0.6,
        }
    )


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fig1_chsh_backends(manifest, output_dir, fmt="pdf"):
    """
    Figure 1: CHSH S values grouped by backend with CI95 error bars.
    Horizontal line at S=2.0 (classical bound).
    """
    runs = manifest["chsh_evidence"]["runs"]

    # Separate entangled runs from negative controls
    entangled_runs = [r for r in runs if r.get("entangled_ci95", False)]
    control_runs = [r for r in runs if not r.get("entangled_ci95", False)]

    backends = sorted({r["backend"] for r in runs})
    x_base = {backend: idx for idx, backend in enumerate(backends)}

    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN, 3.15))

    def plot_runs(group, marker, color, label):
        by_backend = {backend: [] for backend in backends}
        for run in group:
            by_backend[run["backend"]].append(run)

        first = True
        for backend in backends:
            backend_runs = sorted(by_backend[backend], key=lambda run: run["S"], reverse=True)
            count = len(backend_runs)
            if count == 0:
                continue
            offsets = np.linspace(-0.22, 0.22, count) if count > 1 else [0.0]
            for offset, run in zip(offsets, backend_runs):
                x = x_base[backend] + offset
                y = run["S"]
                yerr = [[y - run["ci95"][0]], [run["ci95"][1] - y]]
                ax.errorbar(
                    x,
                    y,
                    yerr=yerr,
                    fmt=marker,
                    color=color,
                    ecolor="black",
                    elinewidth=0.8,
                    capsize=2.5,
                    markersize=4.5,
                    alpha=0.9,
                    label=label if first else None,
                )
                first = False

    plot_runs(entangled_runs, "o", "#1976D2", "Bell state")
    plot_runs(control_runs, "s", "#F57C00", "Negative control")

    # Classical bound
    ax.axhline(y=2.0, color="#E53935", linestyle="--", linewidth=2, label="$S=2$")

    # Quantum bound (reference)
    ax.axhline(
        y=2 * math.sqrt(2),
        color="#9E9E9E",
        linestyle=":",
        linewidth=1,
        label="$2\\sqrt{2}$",
    )

    ax.set_xticks(np.arange(len(backends)))
    ax.set_xticklabels([b.replace("ibm_", "") for b in backends], rotation=20, ha="right")
    ax.set_ylabel("CHSH $S$")
    ax.set_ylim(0, 3.2)
    ax.set_xlim(-0.6, len(backends) - 0.4)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.grid(axis="y", alpha=0.3)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=2,
        frameon=False,
        columnspacing=0.9,
        handletextpad=0.4,
        borderaxespad=0.0,
    )

    plt.tight_layout(rect=(0, 0, 1, 0.84))
    outpath = os.path.join(output_dir, f"fig1_chsh_backends.{fmt}")
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def fig2_mirror_depth_sweep(summary, output_dir, fmt="pdf"):
    """
    Figure 2: Mirror-1Q P(0) vs depth per backend.
    """
    mirror_data = summary["metrics"]["mirror"]
    backends = sorted(mirror_data.keys())
    depths = [1, 2, 4, 8, 16]

    # Color palette
    palette = ["#1976D2", "#388E3C", "#F57C00", "#7B1FA2", "#D32F2F", "#00796B"]

    fig, ax = plt.subplots(figsize=(COLUMN_WIDTH_IN, 2.82))

    for i, backend in enumerate(backends):
        y_vals = [mirror_data[backend][str(d)] for d in depths]
        color = palette[i % len(palette)]
        ax.plot(
            depths,
            y_vals,
            "o-",
            label=backend.replace("ibm_", ""),
            color=color,
            linewidth=2,
            markersize=6,
        )

    ax.set_xlabel("Circuit depth ($d$)")
    ax.set_ylabel("Return probability $P(0)$")
    ax.set_xscale("log", base=2)
    ax.set_xticks(depths)
    ax.set_xticklabels([str(d) for d in depths])
    ax.set_ylim(0.88, 1.005)
    ax.legend(
        fontsize=7.0,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.29),
        frameon=False,
        ncol=3,
        columnspacing=0.9,
        handlelength=1.6,
        handletextpad=0.4,
        borderaxespad=0.0,
    )
    ax.grid(alpha=0.3)

    plt.tight_layout(rect=(0, 0, 1, 0.84))
    outpath = os.path.join(output_dir, f"fig2_mirror_depth_sweep.{fmt}")
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def fig3_v11_heatmap(summary, output_dir, fmt="pdf", v11_data=None):
    """
    Figure 3: Cross-backend workload heatmap.
    Rows = workload families/kinds, Cols = backends.
    Values = primary success metric (normalized to [0,1]).
    """
    backends = sorted(summary["backends"])
    metrics = summary["metrics"]

    # Build rows: workload kind -> per-backend value
    rows = []
    row_labels = []

    # Mirror depths
    for d in [1, 2, 4, 8, 16]:
        row = []
        for b in backends:
            row.append(metrics["mirror"][b][str(d)])
        rows.append(row)
        row_labels.append(f"Mirror d={d}")

    # GHZ-7
    row = [metrics["ghz7"][b] for b in backends]
    rows.append(row)
    row_labels.append("GHZ-7")

    # Grover-2
    row = [metrics["grover"][b]["v11_grover2"] for b in backends]
    rows.append(row)
    row_labels.append("Grover-2")

    # Grover-3
    row = [metrics["grover"][b]["v11_grover3"] for b in backends]
    rows.append(row)
    row_labels.append("Grover-3")

    # QFT-4 and QFT-5 (entropy normalized to ideal)
    if "qft" in metrics:
        for qn, ideal_h in [(4, 4.0), (5, 5.0)]:
            row = []
            for b in backends:
                h = metrics["qft"][b].get(f"v11_qft{qn}", {}).get("entropy_bits", 0)
                # Normalize entropy to [0,1] as fraction of ideal
                row.append(h / ideal_h if ideal_h > 0 else 0)
            rows.append(row)
            row_labels.append(f"QFT-{qn}")

    # VQE-H2 and QAOA-MaxCut4 from v1.1 ancillary data
    if v11_data:
        vqe_by_backend = {}
        qaoa_by_backend = {}
        for r in v11_data.get("runs", []):
            ck = r.get("circuit_kind", "")
            b = r.get("backend", "")
            probs = r.get("prob_by_bitstring", {})
            if ck == "v11_vqe_h2":
                vqe_by_backend[b] = probs.get("01", 0) + probs.get("10", 0)
            elif ck == "v11_qaoa_maxcut4":
                total_c = 0
                for bs, p in probs.items():
                    bits = [int(x) for x in bs]
                    cut = sum(1 for i in range(4) if bits[i] != bits[(i + 1) % 4])
                    total_c += cut * p
                qaoa_by_backend[b] = total_c / 4.0
        if vqe_by_backend:
            row = [vqe_by_backend.get(b, float('nan')) for b in backends]
            rows.append(row)
            row_labels.append("VQE-H$_2$")
        if qaoa_by_backend:
            row = [qaoa_by_backend.get(b, float('nan')) for b in backends]
            rows.append(row)
            row_labels.append("QAOA-MaxCut")

    data = np.array(rows)

    fig, ax = plt.subplots(figsize=(FULL_WIDTH_IN, 4.6))

    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", vmin=0.3, vmax=1.0)

    # Labels
    ax.set_xticks(np.arange(len(backends)))
    ax.set_xticklabels(
        [b.replace("ibm_", "") for b in backends], rotation=20, ha="right"
    )
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)

    # Annotate cells
    for i in range(len(row_labels)):
        for j in range(len(backends)):
            val = data[i, j]
            if np.isnan(val):
                ax.text(j, i, "---", ha="center", va="center", fontsize=7.2, color="gray")
            else:
                color = "white" if val < 0.55 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7.2, color=color)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Success metric")
    cbar.ax.tick_params(labelsize=8)

    plt.tight_layout()
    outpath = os.path.join(output_dir, f"fig3_v11_heatmap.{fmt}")
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def main():
    if not HAS_MPL:
        print("Error: matplotlib and numpy are required to generate figures.", file=sys.stderr)
        print("Install with: pip install matplotlib numpy", file=sys.stderr)
        sys.exit(1)

    # Parse arguments
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ancillary_dir = script_dir
    summary_dir = os.path.join(script_dir, "..", "summary")
    output_dir = os.path.join(script_dir, "..")
    fmt = "pdf"

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--ancillary-dir" and i + 1 < len(args):
            ancillary_dir = args[i + 1]
            summary_dir = os.path.join(os.path.dirname(ancillary_dir), "summary")
            i += 2
        elif args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == "--format" and i + 1 < len(args):
            fmt = args[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {args[i]}", file=sys.stderr)
            sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Load data
    manifest_path = os.path.join(ancillary_dir, "09_ARXIV_ANCILLARY_MANIFEST_v1.json")
    summary_path = os.path.join(summary_dir, "18_ADDON_V1_1_RESULTS_SUMMARY.json")
    if not os.path.exists(summary_path):
        summary_path = os.path.join(ancillary_dir, "18_ADDON_V1_1_RESULTS_SUMMARY.json")

    print("=" * 60)
    print("NISQ Readiness Paper — Figure Generation")
    print("=" * 60)
    print()

    if not os.path.exists(manifest_path):
        print(f"Error: manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(summary_path):
        print(f"Error: summary not found at {summary_path}", file=sys.stderr)
        sys.exit(1)

    manifest = load_json(manifest_path)
    summary = load_json(summary_path)

    # Load v1.1 ancillary data for VQE/QAOA metrics in heatmap
    v11_data_path = os.path.join(ancillary_dir, "17_ARXIV_ANCILLARY_DATA_v1_1.json")
    v11_data = None
    if os.path.exists(v11_data_path):
        v11_data = load_json(v11_data_path)

    print(f"Output format: {fmt}")
    print(f"Output dir:    {output_dir}")
    print()

    apply_pub_style()

    print("Generating Figure 1: CHSH S values across backends...")
    fig1_chsh_backends(manifest, output_dir, fmt)

    print("Generating Figure 2: Mirror-1Q depth sweep...")
    fig2_mirror_depth_sweep(summary, output_dir, fmt)

    print("Generating Figure 3: Cross-backend workload heatmap...")
    fig3_v11_heatmap(summary, output_dir, fmt, v11_data=v11_data)

    print()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
