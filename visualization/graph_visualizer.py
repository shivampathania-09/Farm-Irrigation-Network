"""
Graph Visualizer Module for Farm Irrigation Network Optimization.

Provides presentation-grade visual analytics using Matplotlib and NetworkX:
    1. Farm Topography View: Physical 2D coordinate layout with pipe distance & diameter.
    2. MST Pipeline Highlight: Bright visual overlay of optimal Prim/Kruskal spanning tree.
    3. Dijkstra Path Simulation: Directed water flow corridor with pressure gradients & delivery metrics.
    4. Multi-Panel Presentation Dashboard: 3-in-1 executive viva demonstration layout.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import networkx as nx  # type: ignore

from algorithms.graph import Graph, Edge
from algorithms.prim import PrimMSTResult
from algorithms.kruskal import KruskalMSTResult
from algorithms.dijkstra import DijkstraResult


# ==============================================================================
# VISUAL THEME & PALETTE SPECIFICATION
# ==============================================================================
THEME = {
    "bg_color": "#F8FAFC",            # Clean slate-50 background
    "grid_color": "#E2E8F0",          # Subtle grid lines
    "text_primary": "#0F172A",        # Slate-900 high contrast
    "text_secondary": "#475569",      # Slate-600
    "mesh_edge": "#CBD5E1",           # Inactive mesh pipelines
    "mst_edge": "#059669",            # Vivid Emerald Green (Active MST)
    "mst_glow": "#A7F3D0",            # Glow underlay for MST
    "dijkstra_edge": "#2563EB",       # Royal Blue (Primary water flow)
    "dijkstra_arrow": "#1D4ED8",      # Flow direction marker
    "dijkstra_halo": "#BFDBFE",       # Halo around active water corridor
}

NODE_CONFIG = {
    "reservoir": {
        "color": "#0284C7",           # Sky-600
        "marker": "s",                # Square
        "size": 850,
        "label": "Water Reservoir (Source)",
        "edge_color": "#0369A1"
    },
    "pump_station": {
        "color": "#F59E0B",           # Amber-500
        "marker": "p",                # Pentagon
        "size": 750,
        "label": "Booster Pump Station",
        "edge_color": "#D97706"
    },
    "crop_field": {
        "color": "#10B981",           # Emerald-500
        "marker": "o",                # Circle
        "size": 650,
        "label": "Open Field Crop",
        "edge_color": "#047857"
    },
    "greenhouse": {
        "color": "#8B5CF6",           # Violet-500
        "marker": "D",                # Diamond
        "size": 700,
        "label": "Automated Greenhouse",
        "edge_color": "#6D28D9"
    },
    "field": {
        "color": "#10B981",
        "marker": "o",
        "size": 650,
        "label": "Crop Field Zone",
        "edge_color": "#047857"
    }
}


class FarmGraphVisualizer:
    """
    Presentation and rendering engine for Farm Irrigation Network topology,
    spanning tree layouts, and hydraulic shortest routes.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.nx_graph = graph.to_networkx()
        self.pos = self._resolve_positions()

    def _resolve_positions(self) -> Dict[str, Tuple[float, float]]:
        """Extracts fixed 2D Cartesian layout coordinates or calculates spring layout."""
        pos: Dict[str, Tuple[float, float]] = {}
        for node_id, attrs in self.graph.nodes.items():
            coords = attrs.get("coordinates")
            if coords and coords != (0.0, 0.0):
                pos[node_id] = (float(coords[0]), float(coords[1]))
        if len(pos) < self.graph.num_vertices:
            spring = nx.spring_layout(self.nx_graph, seed=42)
            pos = {str(k): (float(v[0]), float(v[1])) for k, v in spring.items()}
        return pos

    def _render_nodes(self, ax: plt.Axes, highlight_nodes: Optional[Set[str]] = None):
        """Draws categorized agricultural nodes with custom shapes, outlines, and badges."""
        grouped: Dict[str, List[str]] = {}
        for node, attrs in self.graph.nodes.items():
            ntype = attrs.get("type", "crop_field")
            grouped.setdefault(ntype, []).append(node)

        # Draw nodes by category
        for ntype, nodes in grouped.items():
            cfg = NODE_CONFIG.get(ntype, NODE_CONFIG["crop_field"])
            nx.draw_networkx_nodes(
                self.nx_graph,
                self.pos,
                nodelist=nodes,
                ax=ax,
                node_color=cfg["color"],
                node_shape=cfg["marker"],
                node_size=cfg["size"],
                edgecolors=cfg["edge_color"],
                linewidths=2.0
            )

        # Highlight ring for specified subset
        if highlight_nodes:
            coll = nx.draw_networkx_nodes(
                self.nx_graph,
                self.pos,
                nodelist=list(highlight_nodes),
                ax=ax,
                node_color="none",
                node_shape="o",
                node_size=1200,
                edgecolors="#DC2626",
                linewidths=2.5
            )
            if coll is not None:
                coll.set_linestyle("dashed")

        # Node labels with background bounding box for crisp legibility
        for node, (x, y) in self.pos.items():
            attrs = self.graph.nodes.get(node, {})
            crop = attrs.get("crop", "")
            label_text = f"{node}\n({crop})" if crop and crop != node else node
            ax.text(
                x,
                y - 4.2,
                label_text,
                fontsize=8,
                fontweight="bold",
                color=THEME["text_primary"],
                ha="center",
                va="top",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="#E2E8F0", alpha=0.9, lw=0.8)
            )

    def _setup_canvas(self, title: str, subtitle: str) -> Tuple[plt.Figure, plt.Axes]:
        """Initializes a styled engineering grid canvas."""
        fig, ax = plt.subplots(figsize=(12, 8.5), dpi=150)
        fig.patch.set_facecolor(THEME["bg_color"])
        ax.set_facecolor(THEME["bg_color"])

        # Display realistic 2D farm coordinate grid (100m x 100m scale)
        ax.grid(True, linestyle="--", linewidth=0.8, color=THEME["grid_color"], alpha=0.9, zorder=0)
        ax.set_axisbelow(True)
        ax.set_xlabel("Farm Layout X-Coordinate (Meters / Grid Units)", fontsize=9.5, fontweight="semibold", color=THEME["text_secondary"])
        ax.set_ylabel("Farm Layout Y-Coordinate (Meters / Grid Units)", fontsize=9.5, fontweight="semibold", color=THEME["text_secondary"])

        # Dynamic axis limits with margin padding
        xs = [coord[0] for coord in self.pos.values()]
        ys = [coord[1] for coord in self.pos.values()]
        x_pad = (max(xs) - min(xs)) * 0.15
        y_pad = (max(ys) - min(ys)) * 0.20
        ax.set_xlim(min(xs) - x_pad, max(xs) + x_pad)
        ax.set_ylim(min(ys) - y_pad, max(ys) + y_pad)

        ax.set_title(title, fontsize=14, fontweight="bold", color=THEME["text_primary"], pad=18)
        fig.text(0.5, 0.935, subtitle, ha="center", fontsize=9.5, color=THEME["text_secondary"])
        return fig, ax

    def _add_legend(self, ax: plt.Axes, extra_handles: Optional[List[Any]] = None):
        """Constructs an engineering legend explaining node types and edge lines."""
        handles = []
        for ntype, cfg in NODE_CONFIG.items():
            if ntype in ["field"]:
                continue
            handles.append(
                Line2D(
                    [0], [0],
                    marker=cfg["marker"],
                    color="w",
                    markerfacecolor=cfg["color"],
                    markeredgecolor=cfg["edge_color"],
                    markersize=9,
                    label=cfg["label"]
                )
            )
        if extra_handles:
            handles.extend(extra_handles)

        ax.legend(
            handles=handles,
            loc="upper left",
            frameon=True,
            facecolor="white",
            edgecolor="#E2E8F0",
            framealpha=0.95,
            fontsize=8.5,
            title="Farm Infrastructure Legend",
            title_fontsize=9.5
        )

    # ==========================================================================
    # 1. FARM TOPOGRAPHY VIEW
    # ==========================================================================
    def plot_farm_topography(self, save_path: Optional[str] = "farm_topography.png") -> plt.Figure:
        """
        Plots farm assets on a 2D coordinate grid with labeled pipeline weights:
        - Physical trench distance (meters)
        - Pipe internal diameter (mm)
        - Excavation & installation cost ($k)
        """
        fig, ax = self._setup_canvas(
            title="FARM TOPOGRAPHY & PROSPECTIVE PIPELINE NETWORK",
            subtitle=f"Physical Layout | |V| = {self.graph.num_vertices} Agricultural Nodes | |E| = {self.graph.num_edges} Candidate Trenches"
        )

        # Draw candidate pipeline mesh
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            ax=ax,
            edge_color="#94A3B8",
            width=2.0,
            alpha=0.85
        )

        # Labeled pipeline weights: distance, diameter, cost
        edge_labels = {}
        for edge in self.graph.get_all_edges():
            edge_labels[(edge.u, edge.v)] = (
                f"{edge.length:.0f}m | ∅{edge.diameter_mm}mm\n${edge.weight:.1f}k"
            )

        nx.draw_networkx_edge_labels(
            self.nx_graph,
            self.pos,
            edge_labels=edge_labels,
            ax=ax,
            font_size=7,
            font_color="#334155",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#F1F5F9", edgecolor="#CBD5E1", alpha=0.95)
        )

        self._render_nodes(ax)

        extra_handles = [
            Line2D([0], [0], color="#94A3B8", lw=2, label="Candidate Trench Corridor (Length / Diam / Cost)")
        ]
        self._add_legend(ax, extra_handles)

        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
        if save_path:
            fig.savefig(save_path, bbox_inches="tight")
            print(f"[GraphVisualizer] Saved Farm Topography plot -> {save_path}")
        return fig

    # ==========================================================================
    # 2. MST PIPELINE HIGHLIGHT
    # ==========================================================================
    def highlight_mst_pipeline(
        self,
        mst_result: Any,
        algorithm_name: str = "Prim's Algorithm (Min-Heap)",
        save_path: Optional[str] = "mst_highlight.png"
    ) -> plt.Figure:
        """
        Visually highlights the optimal pipeline layout generated by Prim's/Kruskal's
        algorithm in a vivid emerald green over the full candidate network mesh.
        """
        total_cost = getattr(mst_result, "total_cost", 0.0)
        mst_edges = getattr(mst_result, "mst_edges", mst_result)

        fig, ax = self._setup_canvas(
            title=f"MINIMUM SPANNING TREE (MST) PIPELINE OPTIMIZATION",
            subtitle=f"Synthesized via {algorithm_name} | Total CapEx: ${total_cost:,.2f}k | Exactly {len(mst_edges)} Segments"
        )

        # Canonical lookup of MST edges
        mst_set = { (min(u, v), max(u, v)) for u, v, _ in mst_edges }

        # Inactive candidate edges (gray dashed lines)
        inactive_edges = [
            (u, v) for u, v in self.nx_graph.edges()
            if (min(u, v), max(u, v)) not in mst_set
        ]
        # Active MST edges
        active_edges = [
            (u, v) for u, v in self.nx_graph.edges()
            if (min(u, v), max(u, v)) in mst_set
        ]

        # 1. Background Inactive Mesh
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            edgelist=inactive_edges,
            ax=ax,
            edge_color=THEME["mesh_edge"],
            style="dashed",
            width=1.4,
            alpha=0.65
        )

        # 2. Glow Underlay for MST edges
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            edgelist=active_edges,
            ax=ax,
            edge_color=THEME["mst_glow"],
            width=8.0,
            alpha=0.6
        )

        # 3. Vivid Primary MST Pipes
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            edgelist=active_edges,
            ax=ax,
            edge_color=THEME["mst_edge"],
            width=3.6,
            alpha=0.95
        )

        # Labels on active MST edges showing selected cost
        mst_labels = {}
        for u, v, cost in mst_edges:
            mst_labels[(u, v)] = f"${cost:.1f}k"

        nx.draw_networkx_edge_labels(
            self.nx_graph,
            self.pos,
            edge_labels=mst_labels,
            ax=ax,
            font_size=7.5,
            font_weight="bold",
            font_color="#065F46",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#ECFDF5", edgecolor="#10B981", alpha=0.95)
        )

        self._render_nodes(ax)

        # Information Callout Card
        info_box = (
            f"MST Pipe CapEx: ${total_cost:,.2f}k\n"
            f"Spanning Edges: {len(mst_edges)} of {self.graph.num_edges}\n"
            f"Network Status: 100% Connected\n"
            f"Cycles: 0 (Acyclic Tree)"
        )
        ax.text(
            0.98, 0.04,
            info_box,
            transform=ax.transAxes,
            fontsize=8.5,
            fontweight="bold",
            color="#065F46",
            ha="right",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ECFDF5", edgecolor="#059669", alpha=0.95, lw=1.2)
        )

        extra_handles = [
            Line2D([0], [0], color=THEME["mst_edge"], lw=3.5, label="Active MST Pipeline Segment"),
            Line2D([0], [0], color=THEME["mesh_edge"], lw=1.5, linestyle="--", label="Discarded Redundant Trench")
        ]
        self._add_legend(ax, extra_handles)

        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
        if save_path:
            fig.savefig(save_path, bbox_inches="tight")
            print(f"[GraphVisualizer] Saved MST Highlight plot -> {save_path}")
        return fig

    # ==========================================================================
    # 3. DIJKSTRA PATH SIMULATION
    # ==========================================================================
    def simulate_dijkstra_path(
        self,
        dijkstra_result: DijkstraResult,
        source_node: str = "Reservoir",
        target_node: str = "Sugarcane_SW",
        reservoir_head_bar: float = 4.5,
        save_path: Optional[str] = "dijkstra_simulation.png"
    ) -> plt.Figure:
        """
        Simulates and highlights the specific water flow corridor from source to
        destination, complete with directional markers, pressure drop, and terminal head.
        """
        path = dijkstra_result.get_path(target_node)
        loss = dijkstra_result.distances.get(target_node, 0.0)
        delivery_pressure = max(0.0, reservoir_head_bar - loss)
        path_str = " -> ".join(path)

        fig, ax = self._setup_canvas(
            title=f"DIJKSTRA WATER DISTRIBUTION SIMULATION (Source -> Destination)",
            subtitle=f"Flow Path: {path_str} | Head Loss: {loss:.2f} bar | Nozzle Delivery: {delivery_pressure:.2f} bar"
        )

        # Build path edge pairs
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if len(path) > 1 else []
        path_set = { (min(u, v), max(u, v)) for u, v in path_edges }

        # Non-path background pipelines
        inactive_edges = [
            (u, v) for u, v in self.nx_graph.edges()
            if (min(u, v), max(u, v)) not in path_set
        ]

        # 1. Background Mesh
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            edgelist=inactive_edges,
            ax=ax,
            edge_color="#E2E8F0",
            width=1.4,
            alpha=0.7
        )

        # 2. Glowing Halo along active water conduit
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            edgelist=path_edges,
            ax=ax,
            edge_color=THEME["dijkstra_halo"],
            width=9.0,
            alpha=0.7
        )

        # 3. Directed Water Distribution Conduit with Flow Direction
        nx.draw_networkx_edges(
            self.nx_graph,
            self.pos,
            edgelist=path_edges,
            ax=ax,
            edge_color=THEME["dijkstra_edge"],
            width=4.0,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=22,
            node_size=800
        )

        # Flow labels along the path: head loss per pipe segment
        path_labels = {}
        for u, v in path_edges:
            for nbr, wt, edge_obj in self.graph.get_neighbors(u):
                if nbr == v:
                    path_labels[(u, v)] = f"ΔP: -{edge_obj.pressure_loss:.2f}b\n({edge_obj.length:.0f}m)"
                    break

        nx.draw_networkx_edge_labels(
            self.nx_graph,
            self.pos,
            edge_labels=path_labels,
            ax=ax,
            font_size=7.5,
            font_weight="bold",
            font_color="#1E40AF",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#EFF6FF", edgecolor="#3B82F6", alpha=0.95)
        )

        # Render Nodes with highlight ring around source and destination
        self._render_nodes(ax, highlight_nodes={source_node, target_node})

        # Hydraulic Status Card
        pressure_status = "ADEQUATE (Drip Valid)" if delivery_pressure >= 2.5 else "LOW (Booster Required)"
        status_color = "#047857" if delivery_pressure >= 2.5 else "#B91C1C"
        hydraulics_card = (
            f"Source Head: {reservoir_head_bar:.2f} bar\n"
            f"Cumulative Loss: {loss:.2f} bar\n"
            f"Delivery Pressure: {delivery_pressure:.2f} bar\n"
            f"Operational Status: {pressure_status}"
        )
        ax.text(
            0.98, 0.04,
            hydraulics_card,
            transform=ax.transAxes,
            fontsize=8.5,
            fontweight="bold",
            color=status_color,
            ha="right",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8FAFC", edgecolor=status_color, alpha=0.95, lw=1.2)
        )

        extra_handles = [
            Line2D([0], [0], color=THEME["dijkstra_edge"], lw=4, label=f"Optimal Hydraulic Route -> {target_node}"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="none", markeredgecolor="#DC2626", markersize=9, label="Source / Target Terminals")
        ]
        self._add_legend(ax, extra_handles)

        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))
        if save_path:
            fig.savefig(save_path, bbox_inches="tight")
            print(f"[GraphVisualizer] Saved Dijkstra Path Simulation plot -> {save_path}")
        return fig

    # ==========================================================================
    # 4. MASTER 3-IN-1 PRESENTATION DASHBOARD
    # ==========================================================================
    def plot_presentation_dashboard(
        self,
        mst_result: Any,
        dijkstra_result: DijkstraResult,
        target_node: str = "Sugarcane_SW",
        save_path: Optional[str] = "farm_irrigation_master_presentation.png"
    ) -> plt.Figure:
        """
        Creates a side-by-side 3-panel presentation dashboard ideal for slides,
        capstone reviews, and viva voce demonstrations.
        """
        fig, axes = plt.subplots(1, 3, figsize=(24, 7.5), dpi=150)
        fig.patch.set_facecolor(THEME["bg_color"])

        # Panel 1: Topography
        ax1 = axes[0]
        ax1.set_facecolor(THEME["bg_color"])
        ax1.grid(True, linestyle="--", color=THEME["grid_color"], alpha=0.8)
        nx.draw_networkx_edges(self.nx_graph, self.pos, ax=ax1, edge_color="#94A3B8", width=1.8, alpha=0.8)
        top_labels = {(edge.u, edge.v): f"${edge.weight:.0f}k" for edge in self.graph.get_all_edges()}
        nx.draw_networkx_edge_labels(self.nx_graph, self.pos, edge_labels=top_labels, ax=ax1, font_size=6)
        self._render_nodes(ax1)
        ax1.set_title("1. Farm 2D Topography & Pipelines", fontsize=11, fontweight="bold", color=THEME["text_primary"])
        ax1.axis("off")

        # Panel 2: MST Optimization
        ax2 = axes[1]
        ax2.set_facecolor(THEME["bg_color"])
        ax2.grid(True, linestyle="--", color=THEME["grid_color"], alpha=0.8)
        mst_edges = getattr(mst_result, "mst_edges", mst_result)
        total_cost = getattr(mst_result, "total_cost", 0.0)
        mst_set = { (min(u, v), max(u, v)) for u, v, _ in mst_edges }
        nx.draw_networkx_edges(
            self.nx_graph, self.pos,
            edgelist=[(u, v) for u, v in self.nx_graph.edges() if (min(u, v), max(u, v)) not in mst_set],
            ax=ax2, edge_color=THEME["mesh_edge"], style="dashed", width=1.2
        )
        nx.draw_networkx_edges(
            self.nx_graph, self.pos,
            edgelist=[(u, v) for u, v in self.nx_graph.edges() if (min(u, v), max(u, v)) in mst_set],
            ax=ax2, edge_color=THEME["mst_edge"], width=3.2
        )
        self._render_nodes(ax2)
        ax2.set_title(f"2. MST Pipe Laying (CapEx: ${total_cost:,.2f}k)", fontsize=11, fontweight="bold", color=THEME["text_primary"])
        ax2.axis("off")

        # Panel 3: Dijkstra Flow Corridor
        ax3 = axes[2]
        ax3.set_facecolor(THEME["bg_color"])
        ax3.grid(True, linestyle="--", color=THEME["grid_color"], alpha=0.8)
        path = dijkstra_result.get_path(target_node)
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if len(path) > 1 else []
        path_set = { (min(u, v), max(u, v)) for u, v in path_edges }
        nx.draw_networkx_edges(
            self.nx_graph, self.pos,
            edgelist=[(u, v) for u, v in self.nx_graph.edges() if (min(u, v), max(u, v)) not in path_set],
            ax=ax3, edge_color="#E2E8F0", width=1.2
        )
        nx.draw_networkx_edges(
            self.nx_graph, self.pos,
            edgelist=path_edges,
            ax=ax3, edge_color=THEME["dijkstra_edge"], width=3.5,
            arrows=True, arrowstyle="-|>", arrowsize=20
        )
        self._render_nodes(ax3, highlight_nodes={dijkstra_result.source, target_node})
        loss = dijkstra_result.distances.get(target_node, 0.0)
        ax3.set_title(f"3. Hydraulic Corridor -> {target_node} (ΔP: {loss:.2f}b)", fontsize=11, fontweight="bold", color=THEME["text_primary"])
        ax3.axis("off")

        fig.suptitle("FARM IRRIGATION NETWORK — ALGORITHMIC OPTIMIZATION SUITE", fontsize=15, fontweight="bold", y=0.98)
        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))

        if save_path:
            fig.savefig(save_path, bbox_inches="tight")
            print(f"[GraphVisualizer] Saved 3-Panel Presentation Dashboard -> {save_path}")
        return fig


# ==============================================================================
# CONVENIENCE MODULE FUNCTIONS
# ==============================================================================
def plot_farm_topography(graph: Graph, save_path: Optional[str] = "farm_topography.png") -> plt.Figure:
    """Convenience function to render Farm Topography with distance, diameter, and cost labels."""
    visualizer = FarmGraphVisualizer(graph)
    return visualizer.plot_farm_topography(save_path=save_path)


def highlight_mst_pipeline(
    graph: Graph,
    mst_result: Any,
    algorithm_name: str = "Prim's Algorithm (Min-Heap)",
    save_path: Optional[str] = "mst_highlight.png"
) -> plt.Figure:
    """Convenience function to render MST pipeline in emerald green over full network mesh."""
    visualizer = FarmGraphVisualizer(graph)
    return visualizer.highlight_mst_pipeline(mst_result=mst_result, algorithm_name=algorithm_name, save_path=save_path)


def simulate_dijkstra_path(
    graph: Graph,
    dijkstra_result: DijkstraResult,
    source_node: str = "Reservoir",
    target_node: str = "Sugarcane_SW",
    reservoir_head_bar: float = 4.5,
    save_path: Optional[str] = "dijkstra_simulation.png"
) -> plt.Figure:
    """Convenience function to simulate and render directed hydraulic flow from source to target."""
    visualizer = FarmGraphVisualizer(graph)
    return visualizer.simulate_dijkstra_path(
        dijkstra_result=dijkstra_result,
        source_node=source_node,
        target_node=target_node,
        reservoir_head_bar=reservoir_head_bar,
        save_path=save_path
    )


def plot_presentation_dashboard(
    graph: Graph,
    mst_result: Any,
    dijkstra_result: DijkstraResult,
    target_node: str = "Sugarcane_SW",
    save_path: Optional[str] = "farm_irrigation_master_presentation.png"
) -> plt.Figure:
    """Convenience function to render 3-panel executive presentation dashboard."""
    visualizer = FarmGraphVisualizer(graph)
    return visualizer.plot_presentation_dashboard(
        mst_result=mst_result,
        dijkstra_result=dijkstra_result,
        target_node=target_node,
        save_path=save_path
    )
