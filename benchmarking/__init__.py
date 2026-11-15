"""
Benchmarking Package for Farm Irrigation Network Optimization.

Provides:
- PerformanceAnalyzer (Comprehensive benchmark harness)
- generate_random_farm_network (Scalable farm graph generator)
- naive_brute_force_mst (O(E * V) baseline)
- generate_random_connected_farm
- benchmark_algorithms
- plot_benchmark_results
- print_professor_analysis_table
"""

from benchmarking.performance_analyzer import (
    PerformanceAnalyzer,
    generate_random_farm_network,
    naive_brute_force_mst
)
from benchmarking.benchmark import (
    generate_random_connected_farm,
    benchmark_algorithms,
    plot_benchmark_results,
    print_professor_analysis_table
)

__all__ = [
    "PerformanceAnalyzer",
    "generate_random_farm_network",
    "naive_brute_force_mst",
    "generate_random_connected_farm",
    "benchmark_algorithms",
    "plot_benchmark_results",
    "print_professor_analysis_table",
]
