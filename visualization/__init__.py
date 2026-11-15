"""
Visualization Package for Farm Irrigation Network Optimization.

Provides:
- FarmGraphVisualizer (Presentation-grade visualizer class)
- plot_farm_topography (2D Topography with distance/diameter weights)
- highlight_mst_pipeline (Bright MST overlay over network mesh)
- simulate_dijkstra_path (Water flow path simulation)
- plot_presentation_dashboard (3-in-1 executive viva layout)
- plot_farm_topology, plot_mst, plot_shortest_path, plot_dashboard (Legacy/Direct helpers)
"""

from visualization.graph_visualizer import (
    FarmGraphVisualizer,
    THEME,
    NODE_CONFIG,
    plot_farm_topography,
    highlight_mst_pipeline,
    simulate_dijkstra_path,
    plot_presentation_dashboard
)
from visualization.network_visualizer import (
    plot_farm_topology,
    plot_mst,
    plot_shortest_path,
    plot_dashboard
)

__all__ = [
    "FarmGraphVisualizer",
    "THEME",
    "NODE_CONFIG",
    "plot_farm_topography",
    "highlight_mst_pipeline",
    "simulate_dijkstra_path",
    "plot_presentation_dashboard",
    "plot_farm_topology",
    "plot_mst",
    "plot_shortest_path",
    "plot_dashboard",
]
