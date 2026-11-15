"""
Unit tests for benchmarking/performance_analyzer.py.
Verifies graph generator, naive brute force MST, and PerformanceAnalyzer.
"""

import os
from benchmarking.performance_analyzer import (
    PerformanceAnalyzer,
    generate_random_farm_network,
    naive_brute_force_mst
)
from algorithms.prim import prim_mst
from algorithms.kruskal import kruskal_mst


def test_generate_random_farm_network():
    """Validates that generated random farm networks are connected and have expected counts."""
    g = generate_random_farm_network(num_vertices=20, edge_multiplier=2.5, seed=42)
    assert g.num_vertices == 20
    assert g.num_edges >= 19
    assert "Reservoir" in g.nodes


def test_naive_brute_force_mst_correctness():
    """Validates that naive brute force MST achieves identical cost to Prim and Kruskal."""
    g = generate_random_farm_network(num_vertices=15, edge_multiplier=2.0, seed=123)

    prim_res = prim_mst(g)
    kruskal_res = kruskal_mst(g)
    mst_edges, brute_cost, elapsed_ms, timed_out = naive_brute_force_mst(g)

    assert not timed_out
    assert len(mst_edges) == g.num_vertices - 1
    assert abs(brute_cost - prim_res.total_cost) < 1e-3
    assert abs(brute_cost - kruskal_res.total_cost) < 1e-3


def test_performance_analyzer_execution(tmp_path):
    """Verifies that PerformanceAnalyzer runs successfully on small vertex subset."""
    analyzer = PerformanceAnalyzer(vertex_counts=[10, 20], num_trials=2)
    data = analyzer.run_benchmarks()

    assert len(data["v_sizes"]) == 2
    assert all(data["cost_equivalence"])

    plot_path = str(tmp_path / "test_performance.png")
    fig = analyzer.generate_performance_chart(save_path=plot_path)
    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 1000
