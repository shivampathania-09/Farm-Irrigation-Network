"""
Kruskal's Algorithm for Minimum Spanning Tree (MST) Optimization.

DAA Classification:
    - Paradigm: Greedy Approach.
    - Core Data Structure: Disjoint Set Union (DSU) / Union-Find.
    - Optimizations: Path Compression + Union by Rank.
    - Application in Irrigation: Alternative decentralized network synthesis;
      validates Prim's CapEx solution and compares performance on sparse topologies.

Complexity Analysis:
    - Time Complexity:
        * Edge Sorting:      O(E log E) = O(E log V) [Since E <= V^2, log E <= 2 log V]
        * DSU Operations:     O(E * alpha(V)) where alpha is the Inverse Ackermann function
        * Total Time:        O(E log E) or O(E log V)
    - Space Complexity:
        * Disjoint Sets:     O(V) for parent and rank arrays/maps
        * Edge List Storage: O(E)
        * Total Space:       O(V + E)
"""

from typing import Dict, List, Tuple, Any
from algorithms.graph import Graph, Edge


class DisjointSetUnion:
    """
    Disjoint Set Union (DSU) / Union-Find with Path Compression and Union by Rank.

    Theoretical Operations:
        - Make-Set(x): Initializes parent pointer to self and rank to 0. Time: O(1)
        - Find(x):     Finds root representative with Two-Pass Path Compression.
                       Amortized Time: O(alpha(V))
        - Union(x, y): Merges smaller tree under larger tree based on rank.
                       Amortized Time: O(alpha(V))
    """

    def __init__(self, vertices: List[str]):
        # parent[x] points to x's parent in the disjoint forest
        self.parent: Dict[str, str] = {v: v for v in vertices}
        # rank[x] represents upper bound on height of tree rooted at x
        self.rank: Dict[str, int] = {v: 0 for v in vertices}
        self.num_components: int = len(vertices)

    def find(self, item: str) -> str:
        """
        Finds the representative root of the set containing 'item'.
        Implements Path Compression: points visited nodes directly to the root.
        """
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])  # Path compression
        return self.parent[item]

    def union(self, u: str, v: str) -> bool:
        """
        Unites the sets containing u and v using Union by Rank.

        Returns:
            True if u and v were in different sets and merged successfully.
            False if u and v were already in the same set (cycle detected).
        """
        root_u = self.find(u)
        root_v = self.find(v)

        # Cycle condition: both elements already share the same canonical representative
        if root_u == root_v:
            return False

        # Union by Rank: attach smaller rank tree under root of higher rank tree
        if self.rank[root_u] < self.rank[root_v]:
            self.parent[root_u] = root_v
        elif self.rank[root_u] > self.rank[root_v]:
            self.parent[root_v] = root_u
        else:
            # Ranks equal: attach arbitrarily and increment rank of the new root
            self.parent[root_v] = root_u
            self.rank[root_u] += 1

        self.num_components -= 1
        return True


class KruskalMSTResult:
    """
    Encapsulates results and diagnostic telemetry for Kruskal's MST execution.
    """
    def __init__(
        self,
        mst_edges: List[Tuple[str, str, float]],
        total_cost: float,
        step_log: List[Dict[str, Any]],
        num_components: int
    ):
        self.mst_edges = mst_edges
        self.total_cost = total_cost
        self.step_log = step_log
        self.num_components = num_components

    def summary(self) -> str:
        """Generates a structured text summary for viva/terminal display."""
        lines = [
            "=" * 60,
            "KRUSKAL'S ALGORITHM - MINIMUM SPANNING TREE (MST) REPORT",
            "=" * 60,
            f"Total MST Edges Selected : {len(self.mst_edges)}",
            f"Total Pipe Laying Cost   : ${self.total_cost:,.2f}k",
            f"Remaining Components     : {self.num_components} (1 = Fully Connected)",
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


def kruskal_mst(graph: Graph) -> KruskalMSTResult:
    """
    Executes Kruskal's Algorithm to find the Minimum Spanning Tree.

    Algorithmic Mechanics:
        1. Extract all |E| unique edges and sort them in non-decreasing order of cost:
           O(E log E) sorting step.
        2. Initialize Disjoint Set Union (DSU) where each vertex v in V is its own set.
        3. Iterate through sorted edges (u, v):
           a. Use DSU.find(u) and DSU.find(v) to test for cycles.
           b. If u and v belong to different components:
              - Accept edge into MST.
              - Merge sets using DSU.union(u, v).
              - Accumulate edge weight.
           c. If u and v share the same root, discard (avoids cycle formation).
        4. Terminate when |V| - 1 edges have been collected or all edges inspected.

    Parameters:
        graph: Graph instance representing the irrigation network.

    Returns:
        KruskalMSTResult containing selected edges, total cost, and execution history.

    Raises:
        ValueError: If graph has no vertices.
    """
    if graph.num_vertices == 0:
        raise ValueError("Cannot compute MST on an empty graph.")

    vertices = list(graph.nodes.keys())
    dsu = DisjointSetUnion(vertices)

    # Step 1: Collect unique edges and sort by weight (ascending)
    # Edge objects implement __lt__ by weight
    all_edges: List[Edge] = list(graph.get_all_edges())
    all_edges.sort(key=lambda edge: edge.weight)

    mst_edges: List[Tuple[str, str, float]] = []
    step_log: List[Dict[str, Any]] = []
    total_cost: float = 0.0
    target_edges_count = graph.num_vertices - 1

    step_counter = 1
    for edge in all_edges:
        u, v, weight = edge.u, edge.v, edge.weight

        # Step 2: Cycle check via DSU
        if dsu.find(u) != dsu.find(v):
            # No cycle: union the components
            dsu.union(u, v)
            mst_edges.append((u, v, weight))
            total_cost += weight

            step_log.append({
                "step": step_counter,
                "action": "ACCEPT",
                "edge": (u, v),
                "cost": weight,
                "cum_cost": round(total_cost, 2),
                "comment": f"Accepted edge ({u}, {v}) [Cost: {weight}k]. Merged components."
            })
            step_counter += 1

            # Early stopping optimization once MST has |V| - 1 edges
            if len(mst_edges) == target_edges_count:
                break
        else:
            step_log.append({
                "step": step_counter,
                "action": "REJECT_CYCLE",
                "edge": (u, v),
                "cost": weight,
                "comment": f"Rejected edge ({u}, {v}) [Cost: {weight}k] - creates cycle."
            })
            step_counter += 1

    return KruskalMSTResult(
        mst_edges=mst_edges,
        total_cost=round(total_cost, 2),
        step_log=step_log,
        num_components=dsu.num_components
    )
