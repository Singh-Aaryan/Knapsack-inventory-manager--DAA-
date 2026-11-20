"""Command-Line Interface for Intelligent Inventory Management (Knapsack DAA Capstone)."""

from __future__ import annotations

import argparse
import sys

from src.analyzer import run_benchmarks
from src.data_loader import load_inventory_csv
from src.knapsack_solver import fractional_knapsack, zero_one_knapsack_dp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knapsack-cli",
        description="Intelligent Warehouse Inventory Management using Greedy & DP Knapsack.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # solve
    p_solve = subparsers.add_parser("solve", help="Solve inventory selection for a CSV file")
    p_solve.add_argument("csv_file", help="Path to warehouse inventory CSV file")
    p_solve.add_argument("-c", "--capacity", type=int, required=True, help="Warehouse weight capacity")

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run full DAA benchmark suite & generate charts")
    p_bench.add_argument("--sample-dir", default="sample_files", help="Directory for sample CSVs")
    p_bench.add_argument("--results-dir", default="results", help="Directory for CSV & chart outputs")

    return parser


def _print_result(res) -> None:
    print(f"\n=== {res.algorithm} ===")
    print(f"  Capacity          : {res.capacity}")
    print(f"  Weight Used       : {res.total_weight_used} ({res.capacity_utilization_pct}%)")
    print(f"  Total Profit      : {res.total_profit:,.2f}")
    print(f"  Execution Time    : {res.execution_time_ms:.4f} ms")
    print(f"  Selected Products : {len(res.selected_items)}")
    for item in res.selected_items:
        pct = f"{item.fraction * 100:.1f}%"
        print(
            f"    - {item.product.product_id} | {item.product.name:<22} | "
            f"Take: {pct:>6} | Wt: {item.effective_weight:>6.2f} | Profit: {item.effective_profit:>8.2f}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "solve":
        products = load_inventory_csv(args.csv_file)
        greedy_res = fractional_knapsack(products, args.capacity)
        dp_res = zero_one_knapsack_dp(products, args.capacity)
        _print_result(greedy_res)
        _print_result(dp_res)
        return 0

    if args.command == "benchmark":
        records = run_benchmarks(sample_dir=args.sample_dir, results_dir=args.results_dir)
        header = (
            f"{'Dataset':<36} {'N':>4} {'W':>5} {'Greedy($)':>11} {'DP($)':>11} "
            f"{'G(ms)':>8} {'DP(ms)':>9} {'DP Mem(KB)':>11}"
        )
        print(header)
        print("-" * len(header))
        for r in records:
            print(
                f"{str(r['Dataset']):<36} {int(r['Items (N)']):>4} {int(r['Capacity (W)']):>5} "
                f"{float(r['Greedy Profit']):>11,.2f} {float(r['DP 0/1 Profit']):>11,.2f} "
                f"{float(r['Greedy Time (ms)']):>8.3f} {float(r['DP Time (ms)']):>9.3f} "
                f"{float(r['DP Mem (KB)']):>11.2f}"
            )
        print(f"\nCSV and Matplotlib charts saved in: {args.results_dir}/")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
