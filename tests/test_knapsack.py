"""Comprehensive pytest suite for Knapsack Inventory Optimization."""

from __future__ import annotations

import pytest

from src.data_loader import load_inventory_csv, save_inventory_csv
from src.knapsack_solver import fractional_knapsack, zero_one_knapsack_dp
from src.models import Product


def test_empty_inventory_and_zero_capacity() -> None:
    p = [Product("P1", "Box", 10, 50.0)]
    assert fractional_knapsack([], 50).total_profit == 0.0
    assert zero_one_knapsack_dp([], 50).total_profit == 0.0
    assert fractional_knapsack(p, 0).total_profit == 0.0
    assert zero_one_knapsack_dp(p, 0).total_profit == 0.0


def test_classic_textbook_example() -> None:
    """Classic DAA test: W=50, items (10,60), (20,100), (30,120).
    Fractional optimal = 240.0; 0/1 DP optimal = 220.0.
    """
    items = [
        Product("P1", "Item A", 10, 60.0),
        Product("P2", "Item B", 20, 100.0),
        Product("P3", "Item C", 30, 120.0),
    ]
    g_res = fractional_knapsack(items, 50)
    dp_res = zero_one_knapsack_dp(items, 50)

    assert g_res.total_profit == pytest.approx(240.0)
    assert g_res.total_weight_used == pytest.approx(50.0)
    assert dp_res.total_profit == pytest.approx(220.0)
    assert dp_res.total_weight_used == pytest.approx(50.0)
    assert {s.product.product_id for s in dp_res.selected_items} == {"P2", "P3"}


def test_fractional_always_upper_bounds_zero_one() -> None:
    items = [
        Product("P1", "A", 6, 30.0),
        Product("P2", "B", 3, 14.0),
        Product("P3", "C", 4, 16.0),
        Product("P4", "D", 2, 9.0),
    ]
    for cap in [0, 5, 10, 15, 20]:
        g_res = fractional_knapsack(items, cap)
        dp_res = zero_one_knapsack_dp(items, cap)
        assert g_res.total_profit >= dp_res.total_profit
        assert g_res.total_weight_used <= cap + 1e-6
        assert dp_res.total_weight_used <= cap


def test_csv_roundtrip(tmp_path) -> None:
    items = [Product("P001", "Laptop", 5, 500.0, "Electronics")]
    csv_file = tmp_path / "inv.csv"
    save_inventory_csv(items, str(csv_file))
    loaded = load_inventory_csv(str(csv_file))
    assert loaded == items


def test_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        Product("P1", "Bad", 0, 10.0)
    with pytest.raises(ValueError):
        Product("P1", "Bad", 5, -1.0)
    with pytest.raises(ValueError):
        fractional_knapsack([], -5)
    with pytest.raises(ValueError):
        zero_one_knapsack_dp([], -5)
