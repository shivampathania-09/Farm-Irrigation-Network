"""
Main Demonstration & Interactive CLI Menu for Farm Irrigation Network Optimization.
MCA / B.Tech Computer Science — Design and Analysis of Algorithms (DAA) Capstone.

Mapped to DAA Curriculum (Unit-2):
    1. Prim's Algorithm (Min-Heap / heapq) -> Minimum Spanning Tree (MST) CapEx Minimization
    2. Kruskal's Algorithm (Disjoint Set Union / Union-Find) -> MST Benchmark & Cycle Prevention
    3. Dijkstra's Algorithm (Min-Heap / heapq) -> Single-Source Shortest Path (SSSP) & Pressure Loss
"""

import os
import sys
import subprocess

def _ensure_runtime_environment():
    r"""
    Self-healing environment dispatcher:
    If invoked via an unconfigured interpreter (e.g. C:/msys64/ucrt64/bin/python.exe),
    automatically dispatches to the active Python 3.14 installation containing
    all required scientific packages (networkx, matplotlib, numpy).
    """
    if os.environ.get("FARM_IRRIGATION_BOOTSTRAPPED") == "1":
        return

    try:
        import networkx
        import matplotlib
        import numpy
        return  # Interpreter has packages installed
    except ImportError:
        pass

    candidates = [
        r"C:\Users\navee\AppData\Local\Programs\Python\Python314\python.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python314\python.exe"),
        "py.exe",
        "py"
    ]
    for cand in candidates:
        try:
            res = subprocess.run([cand, "-c", "import networkx, matplotlib, numpy"], capture_output=True)
            if res.returncode == 0:
                env = dict(os.environ)
                env["FARM_IRRIGATION_BOOTSTRAPPED"] = "1"
                proc = subprocess.run([cand, *sys.argv], env=env)
                sys.exit(proc.returncode)
        except Exception:
            continue

_ensure_runtime_environment()

import argparse
from typing import Optional, List, Tuple

from algorithms.graph import Graph, Edge
from algorithms.prim import prim_mst, PrimMSTResult
from algorithms.kruskal import kruskal_mst, KruskalMSTResult
from algorithms.dijkstra import dijkstra_shortest_path, DijkstraResult
from visualization.graph_visualizer import (
    FarmGraphVisualizer,
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
from benchmarking.performance_analyzer import PerformanceAnalyzer
from benchmarking.benchmark import (
    benchmark_algorithms,
    plot_benchmark_results,
    print_professor_analysis_table
)


def print_banner():
    """Prints academic project banner."""
    print("\n" + "=" * 80)
    print(" " * 18 + "SMART FARM IRRIGATION NETWORK OPTIMIZER")
    print(" " * 14 + "Design and Analysis of Algorithms (DAA) Lab Project")
    print("=" * 80)
    print("Specialization Focus (DAA Unit-2):")
    print("  * Prim's Algorithm (Min-Heap)          : O(E log V) CapEx Trench Cost Minimization")
    print("  * Kruskal's Algorithm (Union-Find/DSU) : O(E log V) MST Verification & Comparison")
    print("  * Dijkstra's Algorithm (Min-Heap)      : O(E log V) Hydraulic Head Loss Optimization")
    print("=" * 80)


# ==============================================================================
# OPTION 1: DEFAULT FARM SIMULATION
# ==============================================================================
def run_default_simulation(target_crop: str = "Sugarcane_SW"):
    """
    Executes the standard end-to-end algorithmic analysis pipeline on the
    default 10-node realistic farm irrigation network.
    """
    print("\n" + "#" * 80)
    print("OPTION 1: RUN DEFAULT FARM IRRIGATION NETWORK SIMULATION")
    print("#" * 80)

    # Phase 1: Initialize Topology
    print("\n[Phase 1/5] Loading 10-Node Farm Network Topology...")
    farm_graph = Graph.create_sample_farm_network()
    print(f" -> Topology loaded: |V| = {farm_graph.num_vertices} nodes, |E| = {farm_graph.num_edges} pipeline corridors.")
    for node, attrs in farm_graph.nodes.items():
        print(f"    - {node:<16} | Type: {attrs['type']:<14} | Crop: {attrs['crop']:<18} | Demand: {attrs['demand']:>5.0f} L/hr")

    # Phase 2: Prim's Algorithm
    print("\n[Phase 2/5] Executing Prim's Algorithm (Min-Heap) for Pipe-Laying CapEx Optimization...")
    prim_res = prim_mst(farm_graph, start_node="Reservoir")
    print(prim_res.summary())

    # Phase 3: Kruskal's Algorithm
    print("\n[Phase 3/5] Executing Kruskal's Algorithm (Union-Find with Path Compression & Rank)...")
    kruskal_res = kruskal_mst(farm_graph)
    print(kruskal_res.summary())

    # Theoretical Verification
    print("-" * 80)
    print("DAA MST THEORETICAL VERIFICATION CHECK:")
    print(f" -> Prim's Total MST Cost   : ${prim_res.total_cost:,.2f}k")
    print(f" -> Kruskal's Total MST Cost: ${kruskal_res.total_cost:,.2f}k")
    cost_diff = abs(prim_res.total_cost - kruskal_res.total_cost)
    if cost_diff < 1e-4:
        print(" [PASS] MST Cost Equivalence Confirmed! Both greedy strategies arrived at the globally optimal tree.")
    else:
        print(f" [FAIL] Discrepancy detected: {cost_diff}")
    print("-" * 80)

    # Phase 4: Dijkstra's Algorithm
    print("\n[Phase 4/5] Executing Dijkstra's Algorithm for Hydraulic Water Distribution...")
    dijkstra_res = dijkstra_shortest_path(farm_graph, source="Reservoir", weight_attribute="pressure_loss")
    print(dijkstra_res.summary(reservoir_head_bar=4.5))

    # Spotlight target node
    if target_crop not in farm_graph.nodes:
        target_crop = "Sugarcane_SW"
    path = dijkstra_res.get_path(target_crop)
    loss = dijkstra_res.distances[target_crop]
    rem_pressure = max(0.0, 4.5 - loss)

    print(f"\nTarget Crop Zone Spotlight: [{target_crop}]")
    print(f" -> Optimal Hydraulic Corridor: {' -> '.join(path)}")
    print(f" -> Cumulative Head Loss      : {loss:.2f} bar")
    print(f" -> Remaining Nozzle Pressure : {rem_pressure:.2f} bar (Status: {'ADEQUATE (>= 2.50 bar)' if rem_pressure >= 2.5 else 'LOW PRESSURE BOOST REQUIRED'})")

    # Phase 5: Visualizations
    print("\n[Phase 5/5] Generating Presentation-Grade Visualizations (FarmGraphVisualizer)...")
    visualizer = FarmGraphVisualizer(farm_graph)
    visualizer.plot_farm_topography(save_path="farm_topography.png")
    visualizer.highlight_mst_pipeline(mst_result=prim_res, algorithm_name="Prim's Algorithm (Min-Heap)", save_path="mst_highlight.png")
    visualizer.simulate_dijkstra_path(dijkstra_result=dijkstra_res, source_node="Reservoir", target_node=target_crop, save_path="dijkstra_simulation.png")
    visualizer.plot_presentation_dashboard(mst_result=prim_res, dijkstra_result=dijkstra_res, target_node=target_crop, save_path="farm_irrigation_master_presentation.png")

    print("\n" + "=" * 80)
    print(" SIMULATION COMPLETE! Visual assets generated in workspace:")
    print("  * farm_topography.png                 (2D Coordinates with length/diameter)")
    print("  * mst_highlight.png                   (Vivid Emerald MST over network mesh)")
    print("  * dijkstra_simulation.png             (Water flow path with nozzle pressure)")
    print("  * farm_irrigation_master_presentation.png (3-in-1 Executive Presentation Layout)")
    print("=" * 80)


# ==============================================================================
# OPTION 2: CUSTOM FARM CONFIGURATION
# ==============================================================================
def run_custom_farm_configuration():
    """
    Allows the user/examiner to input a custom farm network topology with:
    - Custom field node count
    - Custom field names / crops
    - Custom pipe trench distances, installation costs, and pressure loss
    Solves Prim's MST, Kruskal's MST, and Dijkstra's shortest water route.
    """
    print("\n" + "#" * 80)
    print("OPTION 2: CUSTOM FARM CONFIGURATION BUILDER")
    print("#" * 80)

    # 1. Number of fields
    while True:
        try:
            val = input("\nEnter number of farm fields to irrigate (e.g. 3 to 10) [Default: 4]: ").strip()
            if not val:
                num_fields = 4
                break
            num_fields = int(val)
            if 2 <= num_fields <= 20:
                break
            print("Please enter a reasonable field count between 2 and 20.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    custom_graph = Graph()
    # Add Central Water Reservoir
    custom_graph.add_node("Reservoir", node_type="reservoir", coordinates=(50.0, 90.0), demand_liters_per_hr=0.0, crop_type="Water Source")

    # 2. Field Names & Details
    field_nodes = []
    print(f"\nConfiguring {num_fields} Crop Fields:")
    default_crops = ["Wheat", "Corn", "Paddy", "Cotton", "Orchard", "Vegetables", "Sugarcane", "Barley"]

    use_preset = input("Use automatic field naming and coordinates? (Y/n) [Default: Y]: ").strip().lower() != "n"

    for i in range(1, num_fields + 1):
        if use_preset:
            fname = f"Field_{i}"
            crop = default_crops[(i - 1) % len(default_crops)]
            # Spread coordinates across 100x100 grid
            angle = (i / num_fields) * 3.14159
            x = round(50.0 + 35.0 * (i - (num_fields / 2.0)) / (num_fields / 2.0), 1)
            y = round(20.0 + (i % 2) * 35.0, 1)
        else:
            fname = input(f" Enter identifier for Field #{i} [Default: Field_{i}]: ").strip() or f"Field_{i}"
            crop = input(f" Enter crop type for {fname} [Default: Crop_{i}]: ").strip() or f"Crop_{i}"
            x = round(10.0 + (i * 80.0 / num_fields), 1)
            y = round(20.0 + (i % 2) * 40.0, 1)

        custom_graph.add_node(fname, node_type="crop_field", coordinates=(x, y), demand_liters_per_hr=1500.0, crop_type=crop)
        field_nodes.append(fname)

    # 3. Pipe Connections & Distances
    print("\n" + "-" * 70)
    print("CONFIGURING PIPELINE CORRIDORS:")
    print("Options:")
    print(" [1] Auto-generate realistic pipe connections (Recommended for quick testing)")
    print(" [2] Interactively enter custom pipe distances & installation costs")
    print("-" * 70)
    conn_choice = input("Select connection mode [1/2, Default: 1]: ").strip()

    if conn_choice == "2":
        # Interactive pipe entry
        print("\nEntering pipeline trenches. Every node must be reachable from Reservoir.")
        print("Format: u, v, distance_meters, cost_in_thousands")
        print("Example: Reservoir, Field_1, 150, 12.5")

        # Guarantee at least spanning tree backbone
        for i, field in enumerate(field_nodes, 1):
            parent = "Reservoir" if i == 1 else field_nodes[i - 2]
            dist_str = input(f"Pipe from [{parent}] to [{field}] - Distance in meters [Default: {i*50+60}]: ").strip()
            dist = float(dist_str) if dist_str else float(i * 50 + 60)
            cost = round(dist * 0.08 + 2.0, 2)
            loss = round(dist * 0.003 + 0.15, 2)
            custom_graph.add_edge(parent, field, weight=cost, length=dist, pressure_loss=loss)

        # Allow extra redundant edges
        print("\nAdd extra candidate cross-tie trenches (type 'done' when finished):")
        while True:
            extra = input("Extra trench (NodeA, NodeB, Distance_m) or 'done': ").strip()
            if extra.lower() in ["done", "", "exit"]:
                break
            try:
                parts = [p.strip() for p in extra.split(",")]
                if len(parts) >= 3:
                    u, v, d_val = parts[0], parts[1], float(parts[2])
                    if u in custom_graph.nodes and v in custom_graph.nodes:
                        c_val = round(d_val * 0.08 + 2.0, 2)
                        l_val = round(d_val * 0.003 + 0.15, 2)
                        custom_graph.add_edge(u, v, weight=c_val, length=d_val, pressure_loss=l_val)
                        print(f"  Added trench ({u} <-> {v}): Distance={d_val}m, Cost=${c_val}k")
                    else:
                        print(f"  Error: Node '{u}' or '{v}' not recognized.")
            except Exception as e:
                print(f"  Invalid format: {e}")
    else:
        # Auto-connect realistic candidate mesh
        import random
        rng = random.Random(77)
        # 1. Connect reservoir to first 2 fields
        custom_graph.add_edge("Reservoir", field_nodes[0], weight=12.0, length=140.0, pressure_loss=0.42)
        if len(field_nodes) > 1:
            custom_graph.add_edge("Reservoir", field_nodes[1], weight=15.0, length=175.0, pressure_loss=0.51)

        # 2. Sequential backbone
        for i in range(len(field_nodes) - 1):
            u, v = field_nodes[i], field_nodes[i + 1]
            dist = round(rng.uniform(80.0, 220.0), 1)
            cost = round(dist * 0.08 + rng.uniform(1.0, 3.0), 2)
            loss = round(dist * 0.003 + rng.uniform(0.1, 0.25), 2)
            custom_graph.add_edge(u, v, weight=cost, length=dist, pressure_loss=loss)

        # 3. Add 2 cross-ties for redundancy
        if len(field_nodes) >= 3:
            u, v = field_nodes[0], field_nodes[-1]
            custom_graph.add_edge(u, v, weight=28.0, length=320.0, pressure_loss=1.10)

    print(f"\n[Custom Network Configured] |V| = {custom_graph.num_vertices} nodes, |E| = {custom_graph.num_edges} trenches.")

    # Solve Prim's MST
    print("\n" + "=" * 60)
    print("1. SOLVING PRIM'S ALGORITHM (MIN-HEAP MST) ON CUSTOM FARM")
    print("=" * 60)
    prim_res = prim_mst(custom_graph, start_node="Reservoir")
    print(prim_res.summary())

    # Solve Kruskal's MST
    print("\n" + "=" * 60)
    print("2. SOLVING KRUSKAL'S ALGORITHM (UNION-FIND MST) ON CUSTOM FARM")
    print("=" * 60)
    kruskal_res = kruskal_mst(custom_graph)
    print(kruskal_res.summary())

    # Solve Dijkstra's Shortest Path
    print("\n" + "=" * 60)
    print("3. SOLVING DIJKSTRA'S HYDRAULIC PRESSURE SSSP")
    print("=" * 60)
    dijkstra_res = dijkstra_shortest_path(custom_graph, source="Reservoir", weight_attribute="pressure_loss")
    print(dijkstra_res.summary(reservoir_head_bar=4.5))

    # Generate custom plots
    print("\n[Visualizer] Generating Custom Plots...")
    vis = FarmGraphVisualizer(custom_graph)
    target_field = field_nodes[-1]
    vis.plot_farm_topography(save_path="custom_farm_topography.png")
    vis.highlight_mst_pipeline(mst_result=prim_res, algorithm_name="Prim's MST", save_path="custom_mst_highlight.png")
    vis.simulate_dijkstra_path(dijkstra_result=dijkstra_res, source_node="Reservoir", target_node=target_field, save_path="custom_dijkstra_flow.png")
    vis.plot_presentation_dashboard(mst_result=prim_res, dijkstra_result=dijkstra_res, target_node=target_field, save_path="custom_farm_dashboard.png")

    print("\n" + "=" * 80)
    print(" CUSTOM FARM ANALYSIS COMPLETE! Figures generated:")
    print("  * custom_farm_topography.png")
    print("  * custom_mst_highlight.png")
    print("  * custom_dijkstra_flow.png")
    print("  * custom_farm_dashboard.png")
    print("=" * 80)


# ==============================================================================
# OPTION 3: DAA ALGORITHM BENCHMARK ANALYSIS
# ==============================================================================
def run_benchmark_analysis():
    """
    Executes the comprehensive DAA empirical performance analysis across
    V = [10, 50, 100, 500, 1000] and generates performance_plot.png.
    """
    print("\n" + "#" * 80)
    print("OPTION 3: DAA ALGORITHM BENCHMARK & ASYMPTOTIC RUNTIME ANALYSIS")
    print("#" * 80)
    print("Comparing:")
    print("  1. Prim's Algorithm (Min-Heap / heapq):           O(E log V)")
    print("  2. Kruskal's Algorithm (Union-Find with Rank):    O(E log V)")
    print("  3. Brute Force Baseline (DFS Cycle Detection):   O(E * V)")
    print("  4. Graph scaling evaluations: V in [10, 50, 100, 500, 1000]")

    analyzer = PerformanceAnalyzer(vertex_counts=[10, 50, 100, 500, 1000], num_trials=3)
    analyzer.run_benchmarks()
    analyzer.generate_performance_chart(save_path="performance_plot.png")
    analyzer.output_empirical_summary_table()

    # Also run sparse vs dense topology scaling
    print("\nExecuting Graph Density Scaling Suite (Sparse vs Dense Regimes)...")
    sparse_dense = benchmark_algorithms(vertex_sizes=[10, 25, 50, 100, 150], num_trials=3)
    plot_benchmark_results(sparse_dense, save_path="benchmark_results.png")
    print_professor_analysis_table(sparse_dense)

    print("\n" + "=" * 80)
    print(" BENCHMARKING COMPLETE! Plots saved to workspace:")
    print("  * performance_plot.png (Graph Size V+E on X-axis vs Time in ms on Y-axis)")
    print("  * benchmark_results.png (Sparse vs Dense network scaling)")
    print("=" * 80)


# ==============================================================================
# INTERACTIVE CLI DISPATCHER
# ==============================================================================
def main_menu():
    """Renders the top-level interactive Command Line Interface."""
    print_banner()

    while True:
        print("\n" + "=" * 74)
        print("                        MAIN MENU - DAA CLI")
        print("=" * 74)
        print("  [1] Run Default Farm Irrigation Network Simulation (MST & Dijkstra)")
        print("  [2] Custom Farm Configuration (Input custom fields & pipe distances)")
        print("  [3] Run DAA Algorithm Benchmark Analysis (Generate performance plots)")
        print("  [4] Exit")
        print("=" * 74)

        try:
            choice = input("\nEnter choice [1-4]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Thank you!")
            break

        if choice == "1":
            run_default_simulation()
        elif choice == "2":
            run_custom_farm_configuration()
        elif choice == "3":
            run_benchmark_analysis()
        elif choice == "4":
            print("\nExiting Farm Irrigation Optimizer. Best wishes on your viva defense!\n")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")


def main():
    parser = argparse.ArgumentParser(description="Farm Irrigation Network DAA Optimization Pipeline")
    parser.add_argument("--sim", action="store_true", help="Run Default Farm Simulation (Option 1)")
    parser.add_argument("--custom", action="store_true", help="Run Custom Farm Configuration (Option 2)")
    parser.add_argument("--benchmark", action="store_true", help="Run DAA Benchmarks (Option 3)")
    args = parser.parse_args()

    # If flags were passed, execute non-interactively
    if args.sim:
        print_banner()
        run_default_simulation()
    elif args.custom:
        print_banner()
        run_custom_farm_configuration()
    elif args.benchmark:
        print_banner()
        run_benchmark_analysis()
    else:
        # Default behavior: Launch Interactive CLI Menu
        main_menu()


if __name__ == "__main__":
    main()
