"""
Graph Representation Module for Farm Irrigation Network.

This module provides data structures to model the topological layout of an
agricultural irrigation network. Nodes represent physical assets (Reservoir,
Pumping Stations, Crop Fields, Greenhouses), while edges represent prospective
or existing pipeline trenches with associated civil engineering costs, lengths,
and hydraulic friction/pressure loss parameters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import networkx as nx  # type: ignore


@dataclass(order=True)
class Edge:
    """
    Represents a bidirectional pipeline segment connecting two farm nodes.

    Attributes:
        u (str): Source node identifier.
        v (str): Destination node identifier.
        weight (float): Pipe laying / trench excavation cost (used for MST optimization).
        length (float): Physical distance in meters between nodes.
        pressure_loss (float): Hydraulic head / pressure drop in bar (used for Dijkstra route optimization).
        diameter_mm (int): Pipe diameter in millimeters.
    """
    weight: float
    u: str = field(compare=False)
    v: str = field(compare=False)
    length: float = field(default=0.0, compare=False)
    pressure_loss: float = field(default=0.0, compare=False)
    diameter_mm: int = field(default=100, compare=False)

    def to_tuple(self) -> Tuple[str, str, float]:
        """Returns standard (u, v, weight) representation."""
        return self.u, self.v, self.weight


class Graph:
    """
    Undirected Weighted Graph representing the Farm Irrigation Network.

    Implemented using an Adjacency List for space efficiency:
        Space Complexity: O(|V| + |E|)

    Supports node metadata (geographic coordinates, elevation, node role)
    and bidirectional edge insertion.
    """

    def __init__(self):
        # Adjacency list: node -> List of (neighbor, weight, edge_obj)
        self.adj: Dict[str, List[Tuple[str, float, Edge]]] = {}
        # Node attributes: node -> Dict of properties (coords, type, demand)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # Unique list of edges
        self.edges: List[Edge] = []

    def add_node(
        self,
        node_id: str,
        node_type: str = "field",
        coordinates: Tuple[float, float] = (0.0, 0.0),
        demand_liters_per_hr: float = 1000.0,
        crop_type: Optional[str] = None
    ) -> None:
        """
        Adds a vertex representing a farm asset.

        Args:
            node_id: Unique identifier (e.g., 'Reservoir', 'Field_Wheat').
            node_type: Asset type ('reservoir', 'pump_station', 'crop_field', 'greenhouse').
            coordinates: (x, y) relative Cartesian layout coordinates for visualization.
            demand_liters_per_hr: Water requirement in L/hr.
            crop_type: Agricultural classification.
        """
        if node_id not in self.adj:
            self.adj[node_id] = []
        self.nodes[node_id] = {
            "type": node_type,
            "coordinates": coordinates,
            "demand": demand_liters_per_hr,
            "crop": crop_type or ("Source" if node_type == "reservoir" else "Mixed")
        }

    def add_edge(
        self,
        u: str,
        v: str,
        weight: float,
        length: Optional[float] = None,
        pressure_loss: Optional[float] = None,
        diameter_mm: int = 100
    ) -> None:
        """
        Adds an undirected pipeline edge between node u and node v.

        Args:
            u: First node identifier.
            v: Second node identifier.
            weight: Cost of laying the pipe (currency / cost units).
            length: Physical pipe length in meters (defaults to weight * 10).
            pressure_loss: Pressure loss in bar (defaults to weight * 0.15 if not provided).
            diameter_mm: Pipe internal diameter in mm.
        """
        # Ensure endpoints exist
        if u not in self.adj:
            self.add_node(u)
        if v not in self.adj:
            self.add_node(v)

        len_val = length if length is not None else float(weight * 10.0)
        # Darcy-Weisbach head loss proxy: proportional to length / resistance
        loss_val = pressure_loss if pressure_loss is not None else round(weight * 0.12 + 0.1, 2)

        edge = Edge(
            u=u,
            v=v,
            weight=float(weight),
            length=len_val,
            pressure_loss=loss_val,
            diameter_mm=diameter_mm
        )
        self.edges.append(edge)
        self.adj[u].append((v, float(weight), edge))
        self.adj[v].append((u, float(weight), edge))

    @property
    def num_vertices(self) -> int:
        """Returns |V|, number of vertices."""
        return len(self.nodes)

    @property
    def num_edges(self) -> int:
        """Returns |E|, number of undirected edges."""
        return len(self.edges)

    def get_neighbors(self, u: str) -> List[Tuple[str, float, Edge]]:
        """Returns adjacent vertices for node u as (neighbor, weight, edge_obj)."""
        return self.adj.get(u, [])

    def get_all_edges(self) -> List[Edge]:
        """Returns all registered unique edges."""
        return self.edges

    def to_networkx(self) -> nx.Graph:
        """
        Converts internal adjacency model to a NetworkX Graph for rendering and validation.
        """
        g = nx.Graph()
        for node_id, attrs in self.nodes.items():
            g.add_node(
                node_id,
                pos=attrs["coordinates"],
                type=attrs["type"],
                crop=attrs["crop"],
                demand=attrs["demand"]
            )
        for edge in self.edges:
            g.add_edge(
                edge.u,
                edge.v,
                weight=edge.weight,
                length=edge.length,
                pressure_loss=edge.pressure_loss,
                diameter_mm=edge.diameter_mm
            )
        return g

    @classmethod
    def create_sample_farm_network(cls) -> "Graph":
        """
        Factory method to generate a realistic Smart Farm Irrigation Network.

        Topology Layout:
        - 1 Central Reservoir (Node R: Main gravity storage)
        - 2 Primary Booster Pumping Hubs (P1: North Pump, P2: South Pump)
        - 7 Crop Zones:
            - W1: Wheat Field (North-West)
            - C1: Corn Field (North)
            - P_Z: Paddy Rice Field (High demand, North-East)
            - O1: Citrus Orchard (Central-East)
            - V1: Vineyard (Drip, South-East)
            - G1: Automated Greenhouse (South)
            - S1: Sugarcane Field (South-West)
        
        Total: 10 Vertices, 15 Prospective Pipeline Trenches.
        """
        g = cls()

        # Nodes with coordinates (x, y) on a 100x100 grid
        g.add_node("Reservoir", "reservoir", coordinates=(50, 85), demand_liters_per_hr=0.0, crop_type="Water Source")
        g.add_node("Pump_North", "pump_station", coordinates=(35, 65), demand_liters_per_hr=200.0, crop_type="Booster Pump")
        g.add_node("Pump_South", "pump_station", coordinates=(65, 60), demand_liters_per_hr=200.0, crop_type="Booster Pump")
        g.add_node("Wheat_NW", "crop_field", coordinates=(15, 75), demand_liters_per_hr=2500.0, crop_type="Wheat")
        g.add_node("Corn_N", "crop_field", coordinates=(40, 40), demand_liters_per_hr=3200.0, crop_type="Corn")
        g.add_node("Paddy_NE", "crop_field", coordinates=(85, 75), demand_liters_per_hr=6000.0, crop_type="Paddy Rice")
        g.add_node("Orchard_E", "crop_field", coordinates=(85, 40), demand_liters_per_hr=1800.0, crop_type="Citrus Orchard")
        g.add_node("Vineyard_SE", "crop_field", coordinates=(75, 15), demand_liters_per_hr=1200.0, crop_type="Vineyard")
        g.add_node("Greenhouse_S", "greenhouse", coordinates=(50, 15), demand_liters_per_hr=1500.0, crop_type="Exotic Vegetables")
        g.add_node("Sugarcane_SW", "crop_field", coordinates=(20, 20), demand_liters_per_hr=4500.0, crop_type="Sugarcane")

        # Candidate pipeline trenches: (u, v, cost_in_k$, length_m, pressure_loss_bar)
        trench_candidates = [
            # Main arteries from Reservoir
            ("Reservoir", "Pump_North", 12.0, 150.0, 0.45),
            ("Reservoir", "Pump_South", 14.0, 175.0, 0.52),
            ("Reservoir", "Paddy_NE", 28.0, 320.0, 1.25),

            # North sector distribution
            ("Pump_North", "Wheat_NW", 15.0, 180.0, 0.60),
            ("Pump_North", "Corn_N", 11.0, 130.0, 0.38),
            ("Wheat_NW", "Sugarcane_SW", 25.0, 300.0, 1.10),
            ("Corn_N", "Sugarcane_SW", 18.0, 210.0, 0.72),

            # Central inter-pump cross-tie (provides hydraulic redundancy)
            ("Pump_North", "Pump_South", 20.0, 240.0, 0.85),

            # South and East sector distribution
            ("Pump_South", "Paddy_NE", 16.0, 190.0, 0.65),
            ("Pump_South", "Orchard_E", 13.0, 160.0, 0.50),
            ("Pump_South", "Greenhouse_S", 17.0, 200.0, 0.70),
            ("Orchard_E", "Vineyard_SE", 10.0, 120.0, 0.35),
            ("Vineyard_SE", "Greenhouse_S", 12.0, 140.0, 0.42),
            ("Greenhouse_S", "Sugarcane_SW", 19.0, 220.0, 0.78),
            ("Corn_N", "Greenhouse_S", 22.0, 260.0, 0.95),
        ]

        for u, v, cost, length, p_loss in trench_candidates:
            g.add_edge(u, v, weight=cost, length=length, pressure_loss=p_loss)

        return g
