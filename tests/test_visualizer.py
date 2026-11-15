"""
Unit tests for visualization/graph_visualizer.py.
Validates generation of Topography, MST Highlight, Dijkstra Simulation, and Dashboard plots.
"""

import os
import matplotlib
matplotlib.use("Agg")
try:
    import pytest
except ImportError:
    class _PytestFallback:
        @staticmethod
        def fixture(func):
            return func
    pytest = _PytestFallback()
from algorithms.graph import Graph
from algorithms.prim import prim_mst
from algorithms.dijkstra import dijkstra_shortest_path
from visualization.graph_visualizer import (
    FarmGraphVisualizer,
    plot_farm_topography,
    highlight_mst_pipeline,
    simulate_dijkstra_path,
    plot_presentation_dashboard
)


@pytest.fixture
def sample_graph():
    return Graph.create_sample_farm_network()


def test_visualizer_pipeline(sample_graph, tmp_path):
    """Verifies that all visualizer methods produce valid image files."""
    prim_res = prim_mst(sample_graph)
    dijkstra_res = dijkstra_shortest_path(sample_graph, source="Reservoir")

    topo_path = str(tmp_path / "test_topo.png")
    mst_path = str(tmp_path / "test_mst.png")
    dijkstra_path = str(tmp_path / "test_dijkstra.png")
    dash_path = str(tmp_path / "test_dash.png")

    visualizer = FarmGraphVisualizer(sample_graph)

    # 1. Topography
    fig1 = visualizer.plot_farm_topography(save_path=topo_path)
    assert os.path.exists(topo_path)
    assert os.path.getsize(topo_path) > 1000

    # 2. MST Highlight
    fig2 = visualizer.highlight_mst_pipeline(mst_result=prim_res, save_path=mst_path)
    assert os.path.exists(mst_path)
    assert os.path.getsize(mst_path) > 1000

    # 3. Dijkstra Simulation
    fig3 = visualizer.simulate_dijkstra_path(
        dijkstra_result=dijkstra_res,
        source_node="Reservoir",
        target_node="Sugarcane_SW",
        save_path=dijkstra_path
    )
    assert os.path.exists(dijkstra_path)
    assert os.path.getsize(dijkstra_path) > 1000

    # 4. Presentation Dashboard
    fig4 = visualizer.plot_presentation_dashboard(
        mst_result=prim_res,
        dijkstra_result=dijkstra_res,
        target_node="Sugarcane_SW",
        save_path=dash_path
    )
    assert os.path.exists(dash_path)
    assert os.path.getsize(dash_path) > 1000
