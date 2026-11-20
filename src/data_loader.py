"""CSV inventory loader, saver, and synthetic warehouse dataset generator."""

from __future__ import annotations

import csv
import os
import random
from typing import Dict, List, Tuple

from .models import Product

CATEGORIES = ["Electronics", "Appliances", "Furniture", "Apparel", "Groceries", "Hardware"]


def load_inventory_csv(csv_path: str) -> List[Product]:
    """Load warehouse products from a CSV file.

    Expected columns: product_id, name, weight, profit, category (optional).
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Inventory CSV not found: {csv_path}")

    products: List[Product] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            products.append(
                Product(
                    product_id=(row.get("product_id") or f"P{idx:03d}").strip(),
                    name=(row.get("name") or f"Item {idx}").strip(),
                    weight=int(row["weight"]),
                    profit=float(row["profit"]),
                    category=(row.get("category") or "General").strip(),
                )
            )
    return products


def save_inventory_csv(products: List[Product], csv_path: str) -> None:
    """Save a list of Product objects to a CSV file."""
    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["product_id", "name", "weight", "profit", "category"],
        )
        writer.writeheader()
        for p in products:
            writer.writerow(
                {
                    "product_id": p.product_id,
                    "name": p.name,
                    "weight": p.weight,
                    "profit": p.profit,
                    "category": p.category,
                }
            )


def generate_synthetic_products(count: int, seed: int = 42, max_weight: int = 40) -> List[Product]:
    """Generate deterministic synthetic warehouse inventory items."""
    rng = random.Random(seed)
    products: List[Product] = []
    for i in range(1, count + 1):
        cat = rng.choice(CATEGORIES)
        weight = rng.randint(2, max_weight)
        profit = round(weight * rng.uniform(5.0, 25.0) + rng.uniform(10.0, 80.0), 2)
        products.append(
            Product(
                product_id=f"P{i:03d}",
                name=f"{cat} Unit #{i}",
                weight=weight,
                profit=profit,
                category=cat,
            )
        )
    return products


def generate_sample_datasets(sample_dir: str = "sample_files") -> List[Tuple[str, int]]:
    """Generate standard warehouse CSV datasets with recommended capacities.

    Returns:
        List of (csv_path, recommended_capacity) tuples.
    """
    os.makedirs(sample_dir, exist_ok=True)

    # Classic textbook/viva example where Greedy (0/1) fails vs DP, and Fractional > 0/1
    classic_products = [
        Product("P001", "Smart LED TV", 10, 60.0, "Electronics"),
        Product("P002", "Gaming Laptop", 20, 100.0, "Electronics"),
        Product("P003", "Home Refrigerator", 30, 120.0, "Appliances"),
        Product("P004", "Wireless Earbuds", 5, 45.0, "Electronics"),
        Product("P005", "Ergonomic Chair", 15, 75.0, "Furniture"),
        Product("P006", "Microwave Oven", 12, 66.0, "Appliances"),
        Product("P007", "Mechanical Keyboard", 4, 38.0, "Electronics"),
        Product("P008", "Air Purifier", 18, 92.0, "Appliances"),
    ]

    configs: Dict[str, Tuple[List[Product], int]] = {
        "01_small_warehouse_8items.csv": (classic_products, 50),
        "02_medium_warehouse_25items.csv": (generate_synthetic_products(25, seed=101), 150),
        "03_standard_warehouse_50items.csv": (generate_synthetic_products(50, seed=202), 300),
        "04_large_warehouse_100items.csv": (generate_synthetic_products(100, seed=303), 600),
        "05_enterprise_warehouse_200items.csv": (generate_synthetic_products(200, seed=404), 1200),
    }

    created: List[Tuple[str, int]] = []
    for filename, (items, cap) in configs.items():
        path = os.path.join(sample_dir, filename)
        save_inventory_csv(items, path)
        created.append((path, cap))
    return created
