"""DAA Benchmarking & Performance Analysis Module for Knapsack Optimization.

Compares Greedy (Fractional Knapsack) vs. Dynamic Programming (0/1 Knapsack)
across multiple warehouse dataset sizes on:
- Total Profit & Profit Gap (%)
- Capacity Utilization (%)
- Execution Time (ms)
- Peak Memory Usage (KB via tracemalloc)
Exports benchmark_results.csv and renders Matplotlib comparison charts.
"""

from __future__ import annotations

import csv
import os
import tracemalloc
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .data_loader import generate_sample_datasets, load_inventory_csv
from .knapsack_solver import fractional_knapsack, zero_one_knapsack_dp


def run_benchmarks(
    sample_dir: str = "sample_files",
    results_dir: str = "results",
) -> List[Dict[str, object]]:
    """Run full benchmark suite comparing Fractional vs. 0/1 Knapsack."""
    os.makedirs(results_dir, exist_ok=True)
    datasets = generate_sample_datasets(sample_dir)

    records: List[Dict[str, object]] = []

    for csv_path, capacity in datasets:
        dataset_name = os.path.basename(csv_path)
        products = load_inventory_csv(csv_path)

        # Benchmark Greedy Fractional Knapsack
        tracemalloc.start()
        greedy_res = fractional_knapsack(products, capacity)
        _, greedy_peak_b = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Benchmark DP 0/1 Knapsack
        tracemalloc.start()
        dp_res = zero_one_knapsack_dp(products, capacity)
        _, dp_peak_b = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Fundamental invariant: Fractional Knapsack profit >= 0/1 Knapsack profit
        if greedy_res.total_profit + 1e-6 < dp_res.total_profit:
            raise AssertionError(
                f"Invariant violated on {dataset_name}: "
                f"Fractional ({greedy_res.total_profit}) < DP ({dp_res.total_profit})"
            )

        profit_diff = round(greedy_res.total_profit - dp_res.total_profit, 2)
        records.append(
            {
                "Dataset": dataset_name,
                "Items (N)": len(products),
                "Capacity (W)": capacity,
                "Greedy Profit": greedy_res.total_profit,
                "DP 0/1 Profit": dp_res.total_profit,
                "Profit Gap": profit_diff,
                "Greedy Time (ms)": greedy_res.execution_time_ms,
                "DP Time (ms)": dp_res.execution_time_ms,
                "Greedy Mem (KB)": round(greedy_peak_b / 1024.0, 2),
                "DP Mem (KB)": round(dp_peak_b / 1024.0, 2),
                "DP Utilization (%)": dp_res.capacity_utilization_pct,
            }
        )

    csv_path = os.path.join(results_dir, "benchmark_results.csv")
    fieldnames = list(records[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    _plot_profit_comparison(records, os.path.join(results_dir, "profit_comparison.png"))
    _plot_time_comparison(records, os.path.join(results_dir, "time_complexity.png"))
    return records


def _plot_profit_comparison(records: List[Dict[str, object]], output_path: str) -> None:
    """Bar chart comparing Greedy (Fractional) vs. DP (0/1) Total Profit."""
    labels = [f"N={r['Items (N)']}\n(W={r['Capacity (W)']})" for r in records]
    greedy_p = [float(r["Greedy Profit"]) for r in records]
    dp_p = [float(r["DP 0/1 Profit"]) for r in records]

    x = list(range(len(labels)))
    width = 0.36

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
    ax.bar([i - width / 2 for i in x], greedy_p, width, label="Greedy (Fractional Knapsack)", color="#3b82f6")
    ax.bar([i + width / 2 for i in x], dp_p, width, label="DP (0/1 Knapsack)", color="#10b981")

    ax.set_ylabel("Total Profit ($)", fontsize=11, fontweight="bold")
    ax.set_title("Profit Comparison: Greedy (Fractional) vs. Dynamic Programming (0/1 Knapsack)", fontsize=12.5, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)


def _plot_time_comparison(records: List[Dict[str, object]], output_path: str) -> None:
    """Line chart comparing execution time scaling: O(N log N) vs. O(N * W)."""
    items = [int(r["Items (N)"]) for r in records]
    greedy_ms = [float(r["Greedy Time (ms)"]) for r in records]
    dp_ms = [float(r["DP Time (ms)"]) for r in records]

    fig, ax = plt.subplots(figsize=(9.5, 5), dpi=150)
    ax.plot(items, greedy_ms, marker="o", linewidth=2.2, label="Greedy Fractional — O(N log N)", color="#2563eb")
    ax.plot(items, dp_ms, marker="s", linewidth=2.2, label="DP 0/1 Knapsack — O(N * W)", color="#ef4444")

    ax.set_xlabel("Number of Warehouse Products (N)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Execution Time (ms)", fontsize=11, fontweight="bold")
    ax.set_title("Empirical Time Complexity: Greedy O(N log N) vs. DP O(N × W)", fontsize=12.5, fontweight="bold", pad=12)
    ax.grid(True, linestyle="--", alpha=0.45)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)


if __name__ == "__main__":
    res = run_benchmarks()
    print(f"Benchmarked {len(res)} warehouse datasets. Results saved in results/.")
