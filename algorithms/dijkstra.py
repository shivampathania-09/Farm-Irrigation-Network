"""
Dijkstra's Algorithm for Water Distribution Route & Hydraulic Pressure Optimization.

DAA Classification:
    - Paradigm: Greedy Approach with Edge Relaxation.
    - Theoretical Foundation: Triangle Inequality and Optimal Substructure.
    - Invariant: Once a vertex u is extracted from the priority queue, dist[u]
      is optimal and will never be updated (guaranteed by non-negative edge weights).
    - Application in Irrigation:
        * Identifies the optimal hydraulic supply corridor from the central Reservoir
          to each agricultural zone.
        * Minimizes cumulative pressure loss (bar) due to pipe friction, ensuring
          sufficient operating pressure for micro-drip emitters and spray nozzles.

Complexity Analysis:
    - Time Complexity:
        * Best Case:    O(E log V)
        * Average Case: O(E log V)
        * Worst Case:   O(E log V) [Binary Min-Heap with Adjacency List]
        * Theoretical:  O(V log V + E) [with Fibonacci Heap]
    - Space Complexity:
        * Auxiliary Space: O(V) for distances, predecessors, and visited set.
"""

import heapq
from typing import Dict, List, Tuple, Optional, Any
from algorithms.graph import Graph, Edge


class DijkstraResult:
    """
    Encapsulates results, hydraulic metrics, and reconstructed paths from Dijkstra's SSSP.
    """
    def __init__(
        self,
        source: str,
        distances: Dict[str, float],
        predecessors: Dict[str, Optional[str]],
        metric_name: str,
        relaxation_log: List[Dict[str, Any]],
        path_details: Dict[str, Dict[str, Any]]
    ):
        self.source = source
        self.distances = distances
        self.predecessors = predecessors
        self.metric_name = metric_name
        self.relaxation_log = relaxation_log
        self.path_details = path_details

    def get_path(self, target: str) -> List[str]:
        """
        Reconstructs the shortest path sequence from source to target using predecessor backtracking.
        Time Complexity: O(V)
        """
        if target not in self.distances or self.distances[target] == float("inf"):
            return []

        path = []
        curr: Optional[str] = target
        while curr is not None:
            path.append(curr)
            curr = self.predecessors.get(curr)
        path.reverse()
        return path

    def summary(self, reservoir_head_bar: float = 4.5) -> str:
        """
        Generates a comprehensive hydraulic routing report.

        Args:
            reservoir_head_bar: Base water pressure at the reservoir head (bar).
        """
        lines = [
            "=" * 75,
            f"DIJKSTRA'S HYDRAULIC ROUTE & PRESSURE OPTIMIZATION (Source: {self.source})",
            "=" * 75,
            f"Base Reservoir Static Head: {reservoir_head_bar:.2f} bar",
            f"Optimization Objective    : Minimum Cumulative {self.metric_name}",
            "-" * 75,
            f"{'Target Node':<16}{'Route Path':<32}{'Loss (bar)':<12}{'Delivery (bar)':<15}",
            "-" * 75
        ]

        for node, loss in sorted(self.distances.items(), key=lambda x: x[1]):
            path = self.get_path(node)
            path_str = " -> ".join(path) if path else "Unreachable"
            if len(path_str) > 30:
                path_str = path_str[:27] + "..."
            delivery_pressure = max(0.0, reservoir_head_bar - loss)
            lines.append(f"{node:<16}{path_str:<32}{loss:<12.2f}{delivery_pressure:<15.2f}")

        lines.append("=" * 75)
        return "\n".join(lines)


def dijkstra_shortest_path(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
    weight_attribute: str = "pressure_loss"
) -> DijkstraResult:
    """
    Computes Single-Source Shortest Paths (SSSP) using Dijkstra's Algorithm with a Binary Min-Heap.

    Algorithmic Mechanics:
        1. Initialize dist[v] = infinity for all v in V, dist[source] = 0.
        2. Set predecessors[v] = None.
        3. Push (0, source) into min-heap.
        4. While heap is non-empty:
           a. Extract vertex u with minimal tentative distance dist[u].
           b. If u is visited/finalized, skip (lazy heap cleanup).
           c. If u == target, terminate early (target-directed mode).
           d. For each neighbor v with edge (u, v):
              Edge Relaxation:
              if dist[u] + weight(u, v) < dist[v]:
                  dist[v] = dist[u] + weight(u, v)
                  predecessors[v] = u
                  heapq.heappush(heap, (dist[v], v))
        5. Return distance table and reconstructed path details.

    Parameters:
        graph: Graph instance representing the irrigation network.
        source: Source node identifier (typically 'Reservoir').
        target: Optional destination node for early exit.
        weight_attribute: Metric to minimize: 'pressure_loss', 'length', or 'weight'.

    Returns:
        DijkstraResult containing optimal routes, hydraulic loss, and diagnostic log.

    Raises:
        ValueError: If source is not in the graph.
    """
    if source not in graph.nodes:
        raise ValueError(f"Source vertex '{source}' does not exist in graph.")

    # Distance map initialized to infinity: dist[v] = inf
    distances: Dict[str, float] = {node: float("inf") for node in graph.nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.nodes}
    visited: set = set()

    distances[source] = 0.0

    # Min-Heap stores (current_distance, node_id)
    pq: List[Tuple[float, str]] = [(0.0, source)]
    relaxation_log: List[Dict[str, Any]] = []

    step_counter = 1

    while pq:
        curr_dist, u = heapq.heappop(pq)

        # Lazy deletion: ignore if already finalized with smaller distance
        if u in visited:
            continue
        visited.add(u)

        # Target-directed early stopping optimization
        if target is not None and u == target:
            break

        # Edge relaxation step
        for neighbor, edge_weight, edge_obj in graph.get_neighbors(u):
            if neighbor in visited:
                continue

            # Select desired edge attribute: pressure loss, length, or cost
            if weight_attribute == "pressure_loss":
                w = edge_obj.pressure_loss
            elif weight_attribute == "length":
                w = edge_obj.length
            else:
                w = edge_weight

            new_dist = curr_dist + w

            # Greedy Relaxation Condition: Triangle inequality violation check
            if new_dist < distances[neighbor]:
                old_dist = distances[neighbor]
                distances[neighbor] = round(new_dist, 4)
                predecessors[neighbor] = u
                heapq.heappush(pq, (new_dist, neighbor))

                relaxation_log.append({
                    "step": step_counter,
                    "relaxed_edge": (u, neighbor),
                    "old_dist": old_dist,
                    "new_dist": round(new_dist, 4),
                    "comment": f"Relaxed ({u} -> {neighbor}): distance improved from {old_dist} to {new_dist:.2f}."
                })
                step_counter += 1

    # Precompute path details (physical length, total cost, and pressure drop)
    path_details: Dict[str, Dict[str, Any]] = {}
    for node in graph.nodes:
        if distances[node] != float("inf"):
            path_nodes = []
            curr: Optional[str] = node
            while curr is not None:
                path_nodes.append(curr)
                curr = predecessors.get(curr)
            path_nodes.reverse()

            # Calculate total length and total cost along shortest path
            tot_len = 0.0
            tot_cost = 0.0
            for i in range(len(path_nodes) - 1):
                u_node, v_node = path_nodes[i], path_nodes[i + 1]
                for nbr, wt, edge_obj in graph.get_neighbors(u_node):
                    if nbr == v_node:
                        tot_len += edge_obj.length
                        tot_cost += wt
                        break

            path_details[node] = {
                "path": path_nodes,
                "metric_value": distances[node],
                "total_pipe_length_m": round(tot_len, 2),
                "total_trench_cost_k": round(tot_cost, 2),
            }

    return DijkstraResult(
        source=source,
        distances=distances,
        predecessors=predecessors,
        metric_name=weight_attribute.replace("_", " ").title(),
        relaxation_log=relaxation_log,
        path_details=path_details
    )
