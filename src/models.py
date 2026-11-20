"""Data models for Warehouse Inventory Knapsack Optimization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Product:
    """Represents a single warehouse product.

    Attributes:
        product_id: Unique identifier (e.g., 'P001').
        name: Human-readable product name.
        weight: Storage weight/volume required (positive integer).
        profit: Profit value earned when stocked (non-negative float/int).
        category: Optional product category.
    """

    product_id: str
    name: str
    weight: int
    profit: float
    category: str = "General"

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError(f"Product '{self.product_id}' weight must be > 0, got {self.weight}.")
        if self.profit < 0:
            raise ValueError(f"Product '{self.product_id}' profit must be >= 0, got {self.profit}.")

    @property
    def profit_to_weight_ratio(self) -> float:
        """Return profit per unit weight (used by Greedy Fractional Knapsack)."""
        return self.profit / self.weight


@dataclass(frozen=True)
class SelectedItem:
    """Represents a product (full or fractional) chosen by a knapsack algorithm."""

    product: Product
    fraction: float  # 1.0 for 0/1 Knapsack; (0.0, 1.0] for Fractional Knapsack

    @property
    def effective_weight(self) -> float:
        return round(self.product.weight * self.fraction, 4)

    @property
    def effective_profit(self) -> float:
        return round(self.product.profit * self.fraction, 4)


@dataclass
class KnapsackResult:
    """Structured output returned by Fractional and 0/1 Knapsack solvers."""

    algorithm: str
    capacity: int
    total_profit: float
    total_weight_used: float
    selected_items: List[SelectedItem]
    execution_time_ms: float

    @property
    def capacity_utilization_pct(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return round((self.total_weight_used / self.capacity) * 100.0, 2)
