"""Core Knapsack Optimization Algorithms:
1. Greedy Approach: Fractional Knapsack — O(N log N) time, O(N) space.
2. Dynamic Programming Approach: 0/1 Knapsack — O(N * W) time, O(N * W) space
   (with exact item reconstruction via backtracking).
"""

from __future__ import annotations

import time
from typing import List

from .models import KnapsackResult, Product, SelectedItem


def fractional_knapsack(products: List[Product], capacity: int) -> KnapsackResult:
    """Solve the Fractional Knapsack problem using the Greedy paradigm.

    Sorts products in descending order of profit-to-weight ratio and packs
    each product completely if it fits, or takes the maximum possible fraction
    of the next highest-ratio product to fill remaining capacity.

    Time Complexity: O(N log N) due to sorting N products.
    Space Complexity: O(N) for sorted product list and output selection.
    """
    if capacity < 0:
        raise ValueError(f"Warehouse capacity must be >= 0, got {capacity}.")

    start = time.perf_counter()

    if capacity == 0 or not products:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return KnapsackResult(
            algorithm="Greedy (Fractional Knapsack)",
            capacity=capacity,
            total_profit=0.0,
            total_weight_used=0.0,
            selected_items=[],
            execution_time_ms=round(elapsed_ms, 4),
        )

    # Sort by profit/weight ratio descending; tie-break by higher profit, then ID
    sorted_products = sorted(
        products,
        key=lambda p: (-p.profit_to_weight_ratio, -p.profit, p.product_id),
    )

    remaining = float(capacity)
    total_profit = 0.0
    total_weight = 0.0
    selected: List[SelectedItem] = []

    for product in sorted_products:
        if remaining <= 0:
            break
        if product.weight <= remaining:
            selected.append(SelectedItem(product=product, fraction=1.0))
            total_profit += product.profit
            total_weight += product.weight
            remaining -= product.weight
        else:
            fraction = remaining / product.weight
            selected.append(SelectedItem(product=product, fraction=round(fraction, 6)))
            total_profit += product.profit * fraction
            total_weight += remaining
            remaining = 0.0
            break

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return KnapsackResult(
        algorithm="Greedy (Fractional Knapsack)",
        capacity=capacity,
        total_profit=round(total_profit, 2),
        total_weight_used=round(total_weight, 2),
        selected_items=selected,
        execution_time_ms=round(elapsed_ms, 4),
    )


def zero_one_knapsack_dp(products: List[Product], capacity: int) -> KnapsackResult:
    """Solve the 0/1 Knapsack problem using Bottom-Up Dynamic Programming.

    Each product is either taken completely (1) or excluded (0). Uses a 2D
    DP table dp[i][w] storing maximum profit using the first i products within
    capacity w, followed by O(N) backtracking to recover the exact selected items.

    Time Complexity: O(N * W), where N = number of products, W = capacity.
    Space Complexity: O(N * W) for the DP table.
    """
    if capacity < 0:
        raise ValueError(f"Warehouse capacity must be >= 0, got {capacity}.")

    start = time.perf_counter()
    n = len(products)

    if capacity == 0 or n == 0:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return KnapsackResult(
            algorithm="Dynamic Programming (0/1 Knapsack)",
            capacity=capacity,
            total_profit=0.0,
            total_weight_used=0.0,
            selected_items=[],
            execution_time_ms=round(elapsed_ms, 4),
        )

    # dp[i][w] = max profit considering first i items with capacity w
    dp: List[List[float]] = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        prod = products[i - 1]
        wt = prod.weight
        val = prod.profit
        prev_row = dp[i - 1]
        curr_row = dp[i]

        for w in range(capacity + 1):
            if wt <= w:
                take = val + prev_row[w - wt]
                skip = prev_row[w]
                curr_row[w] = take if take > skip else skip
            else:
                curr_row[w] = prev_row[w]

    # Backtrack to find exact selected items
    selected: List[SelectedItem] = []
    w = capacity
    total_weight = 0.0

    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            prod = products[i - 1]
            selected.append(SelectedItem(product=prod, fraction=1.0))
            w -= prod.weight
            total_weight += prod.weight

    selected.reverse()
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return KnapsackResult(
        algorithm="Dynamic Programming (0/1 Knapsack)",
        capacity=capacity,
        total_profit=round(dp[n][capacity], 2),
        total_weight_used=round(total_weight, 2),
        selected_items=selected,
        execution_time_ms=round(elapsed_ms, 4),
    )
