"""
Prim's Algorithm for Minimum Spanning Tree (MST) Optimization.

DAA Classification:
    - Paradigm: Greedy Approach.
    - Theoretical Foundation: Cut Property of Spanning Trees.
    - Application in Irrigation: Minimizes total capital expenditure (CapEx) for
      trench excavation and pipe laying across all agricultural zones.

Complexity Analysis:
    - Time Complexity:
        * Best Case:    O(E log V)
        * Average Case: O(E log V)
        * Worst Case:   O(E log V) [Binary Min-Heap with Adjacency List]
        * Theoretical:  O(E + V log V) [with Fibonacci Heap]
    - Space Complexity:
        * Auxiliary Space: O(V + E) for the Priority Queue and Visited Hash Set.
"""

import heapq
from typing import Dict, List, Set, Tuple, Optional, Any
from algorithms.graph import Graph, Edge


class PrimMSTResult:
    """
    Encapsulates results and diagnostic telemetry for Prim's MST execution.
    """
    def __init__(
        self,
        mst_edges: List[Tuple[str, str, float]],
        total_cost: float,
        step_log: List[Dict[str, Any]],
        start_node: str,
        num_vertices_visited: int
    ):
        self.mst_edges = mst_edges
        self.total_cost = total_cost
        self.step_log = step_log
        self.start_node = start_node
        self.num_vertices_visited = num_vertices_visited

    def summary(self) -> str:
        """Generates a structured text summary for viva/terminal display."""
        lines = [
            "=" * 60,
            "PRIM'S ALGORITHM - MINIMUM SPANNING TREE (MST) REPORT",
            "=" * 60,
            f"Root / Starting Vertex : {self.start_node}",
            f"Total MST Edges Chosen : {len(self.mst_edges)}",
            f"Total Pipe Laying Cost : ${self.total_cost:,.2f}k",
            f"Vertices Connected     : {self.num_vertices_visited}",
            "-" * 60,
            f"{'Step':<6}{'Edge (u <-> v)':<30}{'Cost ($k)':<12}{'Cum. Cost ($k)':<14}",
            "-" * 60
        ]
        cum_cost = 0.0
        for i, (u, v, cost) in enumerate(self.mst_edges, 1):
            cum_cost += cost
            lines.append(f"{i:<6}{f'{u} <-> {v}':<30}{cost:<12.2f}{cum_cost:<14.2f}")
        lines.append("=" * 60)
        return "\n".join(lines)


def prim_mst(graph: Graph, start_node: Optional[str] = None) -> PrimMSTResult:
    """
    Executes Prim's Algorithm to find the Minimum Spanning Tree using a Min-Heap.

    Algorithmic Mechanics:
        1. Initialize an empty MST tree set T and a visited set S = {start_node}.
        2. Push all edges incident to start_node into a binary min-heap keyed by cost.
        3. While heap is non-empty and |S| < |V|:
           a. Extract edge (u, v) with lowest weight.
           b. If target vertex v is already in S, discard (avoids cycle formation).
           c. Otherwise, add v to S, add edge (u, v) to T, accumulate cost.
           d. Push all incident edges from v to unvisited neighbors into min-heap.
        4. If |S| < |V|, graph is disconnected; returns spanning forest for component.

    Parameters:
        graph: Graph instance representing the irrigation network.
        start_node: Optional starting root node. Defaults to 'Reservoir' or first node.

    Returns:
        PrimMSTResult containing selected edges, total cost, and execution history.

    Raises:
        ValueError: If graph has no vertices.
    """
    if graph.num_vertices == 0:
        raise ValueError("Cannot compute MST on an empty graph.")

    # Select default root: prefer Reservoir if present, else first node
    if start_node is None or start_node not in graph.nodes:
        start_node = "Reservoir" if "Reservoir" in graph.nodes else next(iter(graph.nodes.keys()))

    visited: Set[str] = set()
    mst_edges: List[Tuple[str, str, float]] = []
    step_log: List[Dict[str, Any]] = []
    total_cost: float = 0.0

    # Min-Heap stores tuples: (weight, u, v, edge_obj)
    min_heap: List[Tuple[float, str, str, Edge]] = []

    # Step 1: Mark root as visited and add outgoing edges to heap
    visited.add(start_node)
    for neighbor, weight, edge_obj in graph.get_neighbors(start_node):
        heapq.heappush(min_heap, (weight, start_node, neighbor, edge_obj))

    step_log.append({
        "step": 0,
        "action": "INIT",
        "node": start_node,
        "cut_size": len(visited),
        "comment": f"Initialized spanning tree rooted at '{start_node}'."
    })

    # Step 2: Greedily expand cut by selecting minimum crossing edge
    step_counter = 1
    while min_heap and len(visited) < graph.num_vertices:
        weight, u, v, edge_obj = heapq.heappop(min_heap)

        # Cycle prevention check (both endpoints already in current MST cut)
        if v in visited:
            continue

        # Valid cut-crossing edge: expand tree S <- S U {v}
        visited.add(v)
        mst_edges.append((u, v, weight))
        total_cost += weight

        step_log.append({
            "step": step_counter,
            "action": "ADD_EDGE",
            "edge": (u, v),
            "cost": weight,
            "new_node": v,
            "cum_cost": round(total_cost, 2),
            "comment": f"Greedily connected '{v}' via edge ({u}, {v}) with cost {weight}k."
        })
        step_counter += 1

        # Push newly accessible incident edges from v
        for neighbor, next_weight, next_edge_obj in graph.get_neighbors(v):
            if neighbor not in visited:
                heapq.heappush(min_heap, (next_weight, v, neighbor, next_edge_obj))

    return PrimMSTResult(
        mst_edges=mst_edges,
        total_cost=round(total_cost, 2),
        step_log=step_log,
        start_node=start_node,
        num_vertices_visited=len(visited)
    )
