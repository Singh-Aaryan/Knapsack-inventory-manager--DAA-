"""Interactive Streamlit Web Dashboard for Intelligent Inventory Management (Knapsack)."""

from __future__ import annotations

import csv
import io
import os
import streamlit as st

from src.analyzer import run_benchmarks
from src.data_loader import load_inventory_csv
from src.knapsack_solver import fractional_knapsack, zero_one_knapsack_dp
from src.models import Product

st.set_page_config(
    page_title="Knapsack Inventory Optimizer — DAA Capstone",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 Intelligent Inventory Management Using Knapsack Optimization")
st.caption("Design and Analysis of Algorithms (DAA) Capstone Project — Greedy (Fractional) vs. Dynamic Programming (0/1)")

tab_optimizer, tab_benchmarks = st.tabs(
    ["📦 Inventory Optimizer (Greedy vs. DP)", "📊 DAA Benchmarks & Complexity Charts"]
)

with tab_optimizer:
    st.subheader("Select or Upload Warehouse Inventory")

    col_src, col_cap = st.columns([2, 1])
    with col_src:
        source_mode = st.radio(
            "Dataset Source",
            ["Use Sample Warehouse Dataset", "Upload Custom CSV"],
            horizontal=True,
        )

    products: list[Product] = []
    default_cap = 50

    if source_mode == "Use Sample Warehouse Dataset":
        sample_files = sorted(
            f for f in os.listdir("sample_files") if f.endswith(".csv")
        ) if os.path.isdir("sample_files") else []
        if sample_files:
            chosen = st.selectbox("Choose sample CSV:", sample_files)
            products = load_inventory_csv(os.path.join("sample_files", chosen))
            total_w = sum(p.weight for p in products)
            default_cap = max(10, int(total_w * 0.45))
    else:
        uploaded = st.file_uploader("Upload CSV (columns: product_id, name, weight, profit, category)", type=["csv"])
        if uploaded is not None:
            text_stream = io.StringIO(uploaded.read().decode("utf-8"))
            reader = csv.DictReader(text_stream)
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
            total_w = sum(p.weight for p in products)
            default_cap = max(10, int(total_w * 0.45))

    with col_cap:
        capacity = st.number_input("Warehouse Storage Capacity (W)", min_value=0, value=default_cap, step=10)

    if products:
        greedy_res = fractional_knapsack(products, int(capacity))
        dp_res = zero_one_knapsack_dp(products, int(capacity))

        st.markdown("### Side-by-Side Comparison")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Greedy (Fractional) Profit", f"${greedy_res.total_profit:,.2f}")
        m2.metric("DP (0/1) Profit", f"${dp_res.total_profit:,.2f}")
        m3.metric("Greedy Time", f"{greedy_res.execution_time_ms:.3f} ms")
        m4.metric("DP Time", f"{dp_res.execution_time_ms:.3f} ms")

        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown(f"#### ⚡ Greedy (Fractional) — {greedy_res.capacity_utilization_pct}% Capacity Used")
            st.dataframe(
                [
                    {
                        "ID": s.product.product_id,
                        "Product": s.product.name,
                        "Fraction": f"{s.fraction * 100:.1f}%",
                        "Weight Used": s.effective_weight,
                        "Profit": s.effective_profit,
                    }
                    for s in greedy_res.selected_items
                ],
                use_container_width=True,
                height=320,
            )

        with right_col:
            st.markdown(f"#### 🧠 DP (0/1 Knapsack) — {dp_res.capacity_utilization_pct}% Capacity Used")
            st.dataframe(
                [
                    {
                        "ID": s.product.product_id,
                        "Product": s.product.name,
                        "Fraction": "100.0%",
                        "Weight Used": s.effective_weight,
                        "Profit": s.effective_profit,
                    }
                    for s in dp_res.selected_items
                ],
                use_container_width=True,
                height=320,
            )

with tab_benchmarks:
    st.subheader("Empirical Performance & Complexity Analysis")
    if st.button("🔄 Re-run Full Benchmark Suite"):
        with st.spinner("Running benchmarks across warehouse datasets..."):
            run_benchmarks()
        st.success("Benchmarks updated!")

    csv_path = os.path.join("results", "benchmark_results.csv")
    if os.path.isfile(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        st.dataframe(rows, use_container_width=True)

    c_left, c_right = st.columns(2)
    p_img = os.path.join("results", "profit_comparison.png")
    t_img = os.path.join("results", "time_complexity.png")
    if os.path.isfile(p_img):
        c_left.image(p_img, caption="Greedy vs. DP Total Profit Comparison", use_container_width=True)
    if os.path.isfile(t_img):
        c_right.image(t_img, caption="Empirical Time Complexity: O(N log N) vs. O(N × W)", use_container_width=True)
