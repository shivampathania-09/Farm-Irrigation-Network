"""
Unit & Integration Test Suite for Farm Irrigation Network Algorithms.
Validates Prim's, Kruskal's, and Dijkstra's correctness against DAA invariants.
"""
try:
    import pytest
except ImportError:
    import contextlib

    class _PytestFallback:
        @staticmethod
        @contextlib.contextmanager
        def raises(expected_exception):
            try:
                yield
            except expected_exception:
                pass
            else:
                raise AssertionError(f"Expected exception {expected_exception} was not raised.")

    pytest = _PytestFallback()
from algorithms.graph import Graph, Edge
from algorithms.prim import prim_mst
from algorithms.kruskal import kruskal_mst, DisjointSetUnion
from algorithms.dijkstra import dijkstra_shortest_path


def test_dsu_operations():
    """Validates Disjoint Set Union (Make-Set, Find with Path Compression, Union by Rank)."""
    vertices = ["A", "B", "C", "D", "E"]
    dsu = DisjointSetUnion(vertices)

    assert dsu.num_components == 5
    assert dsu.find("A") == "A"

    # Union A and B
    assert dsu.union("A", "B") is True
    assert dsu.find("A") == dsu.find("B")
    assert dsu.num_components == 4

    # Redundant union should return False (cycle)
    assert dsu.union("A", "B") is False
    assert dsu.num_components == 4

    # Union C and D, then merge (A, B) with (C, D)
    assert dsu.union("C", "D") is True
    assert dsu.union("B", "D") is True
    assert dsu.find("A") == dsu.find("C")
    assert dsu.num_components == 2


def test_mst_equivalence_sample_farm():
    """Validates that Prim's and Kruskal's produce identical total cost on sample farm."""
    graph = Graph.create_sample_farm_network()

    prim_res = prim_mst(graph, start_node="Reservoir")
    kruskal_res = kruskal_mst(graph)

    # 1. Total cost must be identical
    assert abs(prim_res.total_cost - kruskal_res.total_cost) < 1e-4

    # 2. Spanning Tree Property: exactly |V| - 1 edges
    assert len(prim_res.mst_edges) == graph.num_vertices - 1
    assert len(kruskal_res.mst_edges) == graph.num_vertices - 1

    # 3. Known CapEx cost for sample farm network is $121.00k
    assert prim_res.total_cost == 121.0
    assert kruskal_res.total_cost == 121.0


def test_dijkstra_shortest_path():
    """Validates Dijkstra SSSP distances and path reconstruction."""
    graph = Graph.create_sample_farm_network()
    dijkstra_res = dijkstra_shortest_path(graph, source="Reservoir", weight_attribute="pressure_loss")

    # Source distance is 0
    assert dijkstra_res.distances["Reservoir"] == 0.0

    # Every connected node has non-infinite distance
    for node, dist in dijkstra_res.distances.items():
        assert dist < float("inf")
        path = dijkstra_res.get_path(node)
        assert len(path) >= 1
        assert path[0] == "Reservoir"
        assert path[-1] == node

    # Check path to Sugarcane_SW
    path_sugar = dijkstra_res.get_path("Sugarcane_SW")
    assert path_sugar == ["Reservoir", "Pump_North", "Corn_N", "Sugarcane_SW"]
    assert dijkstra_res.distances["Sugarcane_SW"] == 1.55


def test_empty_and_single_node_graphs():
    """Validates edge cases for zero and single node graphs."""
    empty_graph = Graph()
    with pytest.raises(ValueError):
        prim_mst(empty_graph)
    with pytest.raises(ValueError):
        kruskal_mst(empty_graph)

    single_node_graph = Graph()
    single_node_graph.add_node("Reservoir")
    prim_res = prim_mst(single_node_graph)
    kruskal_res = kruskal_mst(single_node_graph)

    assert prim_res.total_cost == 0.0
    assert len(prim_res.mst_edges) == 0
    assert kruskal_res.total_cost == 0.0
    assert len(kruskal_res.mst_edges) == 0
