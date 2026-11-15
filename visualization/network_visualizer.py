"""
Visualization Module for Farm Irrigation Network Optimization.

Provides publication-grade visualizations using NetworkX and Matplotlib:
    1. Raw Farm Topology with Asset Classes (Reservoir, Booster Pumps, Fields).
    2. Prim's MST Pipe Trench Network (CapEx Minimization).
    3. Kruskal's MST Pipe Trench Network (Comparison & Disjoint Set Verification).
    4. Dijkstra's Hydraulic Flow Corridor & Pressure Gradient.
    5. Comprehensive 4-Panel Executive Dashboard.
"""

from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx  # type: ignore
from algorithms.graph import Graph
from algorithms.prim import PrimMSTResult
from algorithms.kruskal import KruskalMSTResult
from algorithms.dijkstra import DijkstraResult


# Curated Theme & Visual Palettes
NODE_COLORS = {
    "reservoir": "#1E88E5",      # Deep Ocean Blue
    "pump_station": "#FB8C00",   # High-Visibility Amber
    "crop_field": "#43A047",     # Lush Foliage Green
    "greenhouse": "#8E24AA",     # Royal Purple
    "field": "#7CB342"           # Grass Green
}

NODE_SHAPES = {
    "reservoir": "s",      # Square
    "pump_station": "p",   # Pentagon
    "crop_field": "o",     # Circle
    "greenhouse": "D",     # Diamond
    "field": "o"
}


def _get_node_positions(graph: Graph) -> Dict[str, Tuple[float, float]]:
    """Extracts predefined Cartesian (x, y) coordinates or computes spring layout."""
    pos: Dict[str, Tuple[float, float]] = {}
    missing = False
    for node_id, attrs in graph.nodes.items():
        coords = attrs.get("coordinates")
        if coords and coords != (0.0, 0.0):
            pos[node_id] = (float(coords[0]), float(coords[1]))
        else:
            missing = True

    if missing or len(pos) < graph.num_vertices:
        nx_g = graph.to_networkx()
        spring = nx.spring_layout(nx_g, seed=42)
        pos = {str(k): (float(v[0]), float(v[1])) for k, v in spring.items()}
    return pos


def _draw_nodes_by_type(ax: plt.Axes, graph: Graph, pos: Dict[str, Tuple[float, float]]):
    """Renders customized node symbols based on agricultural asset classification."""
    by_type: Dict[str, List[str]] = {}
    for node, attrs in graph.nodes.items():
        t = attrs.get("type", "crop_field")
        by_type.setdefault(t, []).append(node)

    nx_g = graph.to_networkx()
    for node_type, nodes in by_type.items():
        color = NODE_COLORS.get(node_type, "#757575")
        shape = NODE_SHAPES.get(node_type, "o")
        nx.draw_networkx_nodes(
            nx_g,
            pos,
            nodelist=nodes,
            ax=ax,
            node_color=color,
            node_shape=shape,
            node_size=650,
            edgecolors="#212121",
            linewidths=1.8,
            label=node_type.replace("_", " ").title()
        )

    # Node text labels
    nx.draw_networkx_labels(
        graph.to_networkx(),
        pos,
        ax=ax,
        font_size=8,
        font_weight="bold",
        font_color="#1A202C",
        verticalalignment="bottom"
    )


def plot_farm_topology(graph: Graph, title: str = "Farm Irrigation Network - Prospective Layout", save_path: Optional[str] = None):
    """
    Renders all prospective pipeline corridors, elevation coordinates, and asset nodes.
    """
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    pos = _get_node_positions(graph)
    nx_g = graph.to_networkx()

    # Draw all prospective pipeline edges
    nx.draw_networkx_edges(
        nx_g,
        pos,
        ax=ax,
        edge_color="#B0BEC5",
        width=1.8,
        style="solid",
        alpha=0.85
    )

    # Edge cost labels
    edge_labels = {
        (u, v): f"${d['weight']}k\n({d['pressure_loss']}b)"
        for u, v, d in nx_g.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        nx_g,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=6.5,
        font_color="#455A64"
    )

    _draw_nodes_by_type(ax, graph, pos)

    ax.set_title(f"{title}\n|V|={graph.num_vertices} Nodes, |E|={graph.num_edges} Candidate Trenches", fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=8)
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"[Visualizer] Saved topology plot to: {save_path}")
    plt.close(fig)


def plot_mst(
    graph: Graph,
    mst_result: PrimMSTResult,
    algorithm_name: str = "Prim's Algorithm (Min-Heap)",
    save_path: Optional[str] = None
):
    """
    Renders the Minimum Spanning Tree pipe-laying solution.
    Inactive candidate edges are grayed out dashed, while active MST pipes are solid bold.
    """
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    pos = _get_node_positions(graph)
    nx_g = graph.to_networkx()

    # Create canonical set of MST edges
    mst_set = set()
    for u, v, _ in mst_result.mst_edges:
        mst_set.add((min(u, v), max(u, v)))

    # Identify non-MST candidate edges
    candidate_edges = [
        (u, v) for u, v in nx_g.edges()
        if (min(u, v), max(u, v)) not in mst_set
    ]
    active_mst_edges = [
        (u, v) for u, v in nx_g.edges()
        if (min(u, v), max(u, v)) in mst_set
    ]

    # Draw inactive candidate trenches
    nx.draw_networkx_edges(
        nx_g,
        pos,
        edgelist=candidate_edges,
        ax=ax,
        edge_color="#CFD8DC",
        style="dashed",
        width=1.2,
        alpha=0.6,
        label="Discarded Candidate (Costly/Cyclic)"
    )

    # Draw chosen MST pipeline trenches
    nx.draw_networkx_edges(
        nx_g,
        pos,
        edgelist=active_mst_edges,
        ax=ax,
        edge_color="#00897B",
        width=3.2,
        alpha=0.95,
        label=f"Optimized MST Pipe Segment ({len(active_mst_edges)} total)"
    )

    # Edge cost labels on MST
    edge_labels = {
        (u, v): f"${d['weight']}k"
        for u, v, d in nx_g.edges(data=True)
        if (min(u, v), max(u, v)) in mst_set
    }
    nx.draw_networkx_edge_labels(
        nx_g,
        pos,
        edge_labels=edge_labels,
        ax=ax,
        font_size=7,
        font_weight="bold",
        font_color="#004D40"
    )

    _draw_nodes_by_type(ax, graph, pos)

    subtitle = f"Total Pipe Installation CapEx: ${mst_result.total_cost:,.2f}k | Spans all {graph.num_vertices} Vertices"
    ax.set_title(f"{algorithm_name} - Minimum Spanning Tree\n{subtitle}", fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=8)
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"[Visualizer] Saved MST plot to: {save_path}")
    plt.close(fig)


def plot_shortest_path(
    graph: Graph,
    dijkstra_result: DijkstraResult,
    target_node: str,
    save_path: Optional[str] = None
):
    """
    Visualizes the optimal hydraulic corridor from source reservoir to a target node,
    highlighting the path in crimson with flow direction arrows and pressure drop annotations.
    """
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    pos = _get_node_positions(graph)
    nx_g = graph.to_networkx()

    path = dijkstra_result.get_path(target_node)
    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if len(path) > 1 else []
    path_set = { (min(u, v), max(u, v)) for u, v in path_edges }

    other_edges = [
        (u, v) for u, v in nx_g.edges()
        if (min(u, v), max(u, v)) not in path_set
    ]

    # Background edges
    nx.draw_networkx_edges(
        nx_g,
        pos,
        edgelist=other_edges,
        ax=ax,
        edge_color="#ECEFF1",
        width=1.2,
        alpha=0.7
    )

    # Highlighted shortest path edges
    nx.draw_networkx_edges(
        nx_g,
        pos,
        edgelist=path_edges,
        ax=ax,
        edge_color="#E53935",
        width=3.6,
        alpha=0.95,
        label=f"Shortest Water Flow Route -> {target_node}"
    )

    # Labels along the path showing pressure drop
    path_edge_labels = {}
    for u, v in path_edges:
        for nbr, wt, edge_obj in graph.get_neighbors(u):
            if nbr == v:
                path_edge_labels[(u, v)] = f"-{edge_obj.pressure_loss:.2f} bar"
                break

    nx.draw_networkx_edge_labels(
        nx_g,
        pos,
        edge_labels=path_edge_labels,
        ax=ax,
        font_size=7.5,
        font_weight="bold",
        font_color="#B71C1C"
    )

    _draw_nodes_by_type(ax, graph, pos)

    loss = dijkstra_result.distances.get(target_node, 0.0)
    route_str = " -> ".join(path)
    title_str = (
        f"Dijkstra's Water Delivery Route to {target_node}\n"
        f"Path: {route_str} | Cumulative Friction Head Loss: {loss:.2f} bar"
    )
    ax.set_title(title_str, fontsize=11, fontweight="bold", pad=12)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=8)
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"[Visualizer] Saved Shortest Path plot to: {save_path}")
    plt.close(fig)


def plot_dashboard(
    graph: Graph,
    prim_res: PrimMSTResult,
    kruskal_res: KruskalMSTResult,
    dijkstra_res: DijkstraResult,
    target_node: str = "Sugarcane_SW",
    save_path: Optional[str] = "farm_irrigation_dashboard.png"
):
    """
    Generates a unified 4-panel executive and educational dashboard:
        - Panel (1,1): Full Farm Topological Layout & Edge Weights
        - Panel (1,2): Prim's Algorithm MST (Min-Heap, O(E log V))
        - Panel (2,1): Kruskal's Algorithm MST (DSU Union-Find, O(E log V))
        - Panel (2,2): Dijkstra's Shortest Hydraulic Route & Pressure Loss
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 14), dpi=150)
    pos = _get_node_positions(graph)
    nx_g = graph.to_networkx()

    # ---------------- PANEL 1: Network Topology ----------------
    ax1 = axes[0, 0]
    nx.draw_networkx_edges(nx_g, pos, ax=ax1, edge_color="#90A4AE", width=1.5, alpha=0.8)
    edge_labels = {(u, v): f"${d['weight']}k" for u, v, d in nx_g.edges(data=True)}
    nx.draw_networkx_edge_labels(nx_g, pos, edge_labels=edge_labels, ax=ax1, font_size=6, font_color="#37474F")
    _draw_nodes_by_type(ax1, graph, pos)
    ax1.set_title(f"A. Farm Pipeline Layout (|V|={graph.num_vertices}, |E|={graph.num_edges})", fontsize=11, fontweight="bold")
    ax1.axis("off")

    # ---------------- PANEL 2: Prim's MST ----------------
    ax2 = axes[0, 1]
    prim_set = { (min(u, v), max(u, v)) for u, v, _ in prim_res.mst_edges }
    nx.draw_networkx_edges(
        nx_g, pos,
        edgelist=[(u, v) for u, v in nx_g.edges() if (min(u, v), max(u, v)) not in prim_set],
        ax=ax2, edge_color="#ECEFF1", style="dashed", width=1.0
    )
    nx.draw_networkx_edges(
        nx_g, pos,
        edgelist=[(u, v) for u, v in nx_g.edges() if (min(u, v), max(u, v)) in prim_set],
        ax=ax2, edge_color="#00897B", width=2.8
    )
    _draw_nodes_by_type(ax2, graph, pos)
    ax2.set_title(f"B. Prim's MST (Min-Heap) | Cost: ${prim_res.total_cost:.2f}k | O(E log V)", fontsize=11, fontweight="bold")
    ax2.axis("off")

    # ---------------- PANEL 3: Kruskal's MST ----------------
    ax3 = axes[1, 0]
    kruskal_set = { (min(u, v), max(u, v)) for u, v, _ in kruskal_res.mst_edges }
    nx.draw_networkx_edges(
        nx_g, pos,
        edgelist=[(u, v) for u, v in nx_g.edges() if (min(u, v), max(u, v)) not in kruskal_set],
        ax=ax3, edge_color="#ECEFF1", style="dashed", width=1.0
    )
    nx.draw_networkx_edges(
        nx_g, pos,
        edgelist=[(u, v) for u, v in nx_g.edges() if (min(u, v), max(u, v)) in kruskal_set],
        ax=ax3, edge_color="#3949AB", width=2.8
    )
    _draw_nodes_by_type(ax3, graph, pos)
    ax3.set_title(f"C. Kruskal's MST (DSU Union-Find) | Cost: ${kruskal_res.total_cost:.2f}k | O(E log V)", fontsize=11, fontweight="bold")
    ax3.axis("off")

    # ---------------- PANEL 4: Dijkstra Route ----------------
    ax4 = axes[1, 1]
    path = dijkstra_res.get_path(target_node)
    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if len(path) > 1 else []
    path_set = { (min(u, v), max(u, v)) for u, v in path_edges }
    nx.draw_networkx_edges(
        nx_g, pos,
        edgelist=[(u, v) for u, v in nx_g.edges() if (min(u, v), max(u, v)) not in path_set],
        ax=ax4, edge_color="#ECEFF1", width=1.0
    )
    nx.draw_networkx_edges(
        nx_g, pos,
        edgelist=path_edges,
        ax=ax4, edge_color="#E53935", width=3.2
    )
    _draw_nodes_by_type(ax4, graph, pos)
    loss = dijkstra_res.distances.get(target_node, 0.0)
    ax4.set_title(f"D. Dijkstra Route -> {target_node} | Head Loss: {loss:.2f} bar | O(E log V)", fontsize=11, fontweight="bold")
    ax4.axis("off")

    fig.suptitle("FARM IRRIGATION NETWORK - ALGORITHMIC OPTIMIZATION DASHBOARD", fontsize=15, fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))

    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
        print(f"[Visualizer] Master dashboard successfully saved to: {save_path}")
    plt.close(fig)
