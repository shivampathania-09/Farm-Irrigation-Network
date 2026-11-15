# Farm Irrigation Network Optimization
### Design and Analysis of Algorithms (DAA) — Capstone Lab Project
**Academic Level:** MCA / B.Tech Computer Science & Engineering  
**Curriculum Mapping:** **DAA Unit-2: Greedy Method & Graph Optimization Algorithms**

---

## 🌾 1. Project Overview & Real-World Context

In precision agriculture and smart farm engineering, water distribution networks represent a critical capital and operational investment. Designing an automated irrigation network presents two competing, multi-objective optimization challenges:

```
                                    +------------------------------+
                                    | Water Reservoir (Head Source)|
                                    +------------------------------+
                                             /             \
                                            /               \
                       +-----------------------+     +-----------------------+
                       | Booster Pump North P1 |     | Booster Pump South P2 |
                       +-----------------------+     +-----------------------+
                                   |                             |
                       +-----------------------+     +-----------------------+
                       | Open Crop Fields      |     | High-Tech Greenhouse  |
                       | (Wheat, Corn, Paddy)  |     | (Drip Manifold System)|
                       +-----------------------+     +-----------------------+
```

### The Engineering & Algorithmic Duality:
1. **Capital Expenditure (CapEx) Optimization (Minimum Spanning Tree):**
   * *Problem:* Laying underground pipeline trenches requires significant excavation costs ($\$/\text{meter}$), raw PVC/HDPE piping, and valve manifolds.
   * *Algorithmic Formulation:* Connect all agricultural zones using the absolute minimum total trench installation cost without introducing redundant cycles.
   * *DAA Solution:* **Prim's Algorithm** (Min-Heap) and **Kruskal's Algorithm** (Disjoint Set Union with Path Compression & Union by Rank).

2. **Operational Hydraulic Optimization (Single-Source Shortest Path):**
   * *Problem:* While an MST minimizes pipe-laying CapEx, water transit routes through an MST can be meandering and indirect. As water traverses long pipes, Darcy-Weisbach pipe friction induces cumulative pressure drops ($\Delta P$ in $\text{bar}$). Micro-drip emitters and spray nozzles require a guaranteed terminal pressure ($\ge 2.5\text{ bar}$) to function.
   * *Algorithmic Formulation:* Determine the path of minimum cumulative friction head loss from the primary Water Reservoir to every individual crop field.
   * *DAA Solution:* **Dijkstra's Algorithm** (Min-Heap based SSSP).

---

## 📚 2. Mapping to DAA Syllabus (Unit-2)

This project directly maps to **Unit-2 of the Design and Analysis of Algorithms (DAA)** curriculum for MCA and B.Tech CSE:

| Syllabus Topic | Academic Concept | Concrete Project Implementation | Source Code Link |
| :--- | :--- | :--- | :--- |
| **Greedy Strategy Foundations** | Greedy Choice Property & Optimal Substructure | Locally optimal choices of minimum-weight edges lead to global optimum without backtracking. | [`algorithms/`](file:///c:/Users/navee/Desktop/MCA_AI&ML-1_Sem/Design_and_Analysis_of_Algorithms/Farm%20Irrigation%20Network/algorithms) |
| **Minimum Spanning Trees (MST)** | Cut Property of Spanning Trees | **Prim's Algorithm:** Min-heap priority queue growing a tree from the Reservoir cut into unvisited field nodes. | [prim.py](file:///c:/Users/navee/Desktop/MCA_AI&ML-1_Sem/Design_and_Analysis_of_Algorithms/Farm%20Irrigation%20Network/algorithms/prim.py) |
| **Disjoint Set Union (DSU)** | Path Compression & Union by Rank | **Kruskal's Algorithm:** Forest synthesis with edge sorting and cycle prevention via Inverse Ackermann $\mathcal{O}(\alpha(V))$ amortized operations. | [kruskal.py](file:///c:/Users/navee/Desktop/MCA_AI&ML-1_Sem/Design_and_Analysis_of_Algorithms/Farm%20Irrigation%20Network/algorithms/kruskal.py) |
| **Single-Source Shortest Paths** | Triangle Inequality & Edge Relaxation | **Dijkstra's Algorithm:** Binary min-heap calculating minimal cumulative pressure loss ($\Delta P$) from reservoir head. | [dijkstra.py](file:///c:/Users/navee/Desktop/MCA_AI&ML-1_Sem/Design_and_Analysis_of_Algorithms/Farm%20Irrigation%20Network/algorithms/dijkstra.py) |
| **Empirical Asymptotic Analysis** | Growth of Functions ($\mathcal{O}$, $\Omega$, $\Theta$) | Empirical scaling tests across $V \in [10, 1000]$, verifying constant ratio $c = T(n) / (E \log_2 V)$. | [performance_analyzer.py](file:///c:/Users/navee/Desktop/MCA_AI&ML-1_Sem/Design_and_Analysis_of_Algorithms/Farm%20Irrigation%20Network/benchmarking/performance_analyzer.py) |

---

## ⚡ 3. Theoretical vs. Empirical Complexity Table

### Theoretical Bounds (Adjacency List Representation):

$$\text{Let } |V| = \text{number of agricultural nodes, } |E| = \text{number of pipeline trench corridors}$$

| Algorithm | DAA Paradigm | Core Data Structure | Time Complexity (Best) | Time Complexity (Average/Worst) | Auxiliary Space Complexity | Practical Irrigation Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Prim's Algorithm** | Greedy (Vertex Growth) | Binary Min-Heap (`heapq`) | $\mathcal{O}(E \log V)$ | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V + E)$ | Minimizes total trench excavation CapEx |
| **Kruskal's Algorithm** | Greedy (Edge Forest) | Disjoint Set Union (DSU) | $\mathcal{O}(E \log V)$ | $\mathcal{O}(E \log E) = \mathcal{O}(E \log V)$ | $\mathcal{O}(V + E)$ | MST verification; optimal on sparse topologies |
| **Dijkstra's Algorithm** | Greedy (Edge Relaxation)| Binary Min-Heap (`heapq`) | $\mathcal{O}(E \log V)$ | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V)$ | Minimizes cumulative pipe friction head loss |
| **Brute Force Baseline** | Exhaustive (DFS Cycle Check)| Adjacency List + DFS Stack | $\mathcal{O}(E \log E)$ | $\mathcal{O}(E \cdot V)$ | $\mathcal{O}(V + E)$ | Naive baseline showing why DSU is essential |

### Empirical Benchmarking Measurements (Python 3.14 Environment):

```
================================================================================================
          EMPIRICAL ASYMPTOTIC RUNTIME & THEORETICAL COMPLEXITY SUMMARY
================================================================================================
|V|   |E|   |V+E|   E*log2(V)   Prim(ms)   Kruskal(ms)  Brute(ms)     c(Prim)    c(Kruskal) Cost  
------------------------------------------------------------------------------------------------
10    22    32      73          0.141      0.164        0.089         1.9312     2.2386     PASS  
50    110   160     621         0.656      1.023        1.070         1.0573     1.6472     PASS  
100   220   320     1462        1.443      1.499        4.803         0.9875     1.0254     PASS  
500   1100  1600    9862        7.403      9.765        185.980       0.7506     0.9901     PASS  
1000  2200  3200    21925       14.725     17.783       TIMEOUT       0.6716     0.8111     PASS  
================================================================================================
```

> **Viva Insight:** Notice that the normalized ratio $c = \frac{T_{\text{measured}}}{E \log_2 V}$ converges to a stable horizontal band ($0.67 \times 10^{-3}$ to $1.05 \times 10^{-3}$), empirically proving that both Prim and Kruskal scale in strict accordance with $\mathcal{O}(E \log V)$, whereas Brute Force degrades quadratically ($\mathcal{O}(E \cdot V)$), suffering a 25x slowdown at $V=500$ and timing out at $V=1000$.

---

## 📂 4. Project Directory Structure

```
Farm Irrigation Network/
│
├── algorithms/                    # Core DAA Algorithmic Implementations
│   ├── __init__.py                # Package exports
│   ├── graph.py                   # Adjacency List Graph & Edge data structures (Dual-weight model)
│   ├── prim.py                    # Prim's Algorithm (Min-Heap / heapq) -> O(E log V)
│   ├── kruskal.py                 # Kruskal's Algorithm (DSU with Path Compression & Rank) -> O(E log V)
│   └── dijkstra.py                # Dijkstra's Algorithm (Min-Heap) -> O(E log V)
│
├── visualization/                 # Matplotlib & NetworkX Rendering Suite
│   ├── __init__.py
│   ├── graph_visualizer.py        # Presentation Layer: Topography, MST Highlight, Flow Simulation
│   └── network_visualizer.py      # Core plotting utilities & legacy dashboard
│
├── benchmarking/                  # Empirical Asymptotic Complexity Evaluation
│   ├── __init__.py
│   ├── performance_analyzer.py    # Core DAA Benchmarks: Prim vs Kruskal vs Brute Force (V=10 to 1000)
│   └── benchmark.py               # Sparse vs Dense scaling benchmarks
│
├── tests/                         # Automated Unit & Property-Based Tests
│   ├── __init__.py
│   ├── test_algorithms.py         # Pytest verification of MST and SSSP invariants
│   ├── test_visualizer.py         # Pytest validation of visual figure generation
│   └── test_performance_analyzer.py # Pytest validation of benchmarking harness
│
├── main.py                        # Central demonstration & interactive CLI harness
├── requirements.txt               # Dependencies: networkx, matplotlib, numpy
├── DAA_VIVA_DEFENSE_GUIDE.md      # Professor's viva voce preparation and theoretical proofs
└── README.md                      # Comprehensive project documentation
```

---

## 🚀 5. Installation & Run Instructions

### Step 1: Install Dependencies
Open your terminal in the project directory and install the required scientific libraries:
```bash
pip install -r requirements.txt
```
*(Dependencies: `networkx>=3.0`, `matplotlib>=3.7.0`, `numpy>=1.24.0`)*

---

### Step 2: Launch the Interactive CLI Menu
Run the central entry point:
```bash
python main.py
```
*(On Windows systems, you can also use `py main.py`)*

You will be greeted with the interactive DAA terminal menu:
```text
==========================================================================
                        MAIN MENU - DAA CLI
==========================================================================
  [1] Run Default Farm Irrigation Network Simulation (MST & Dijkstra)
  [2] Custom Farm Configuration (Input custom fields & pipe distances)
  [3] Run DAA Algorithm Benchmark Analysis (Generate performance plots)
  [4] Exit
==========================================================================
Enter choice [1-4]: 
```

---

### Step 3: Menu Option Walkthrough

#### Option 1: Run Default Farm Irrigation Network Simulation
* Solves the realistic 10-node farm topology (Main Reservoir, Booster Pumps Alpha/Beta, Wheat, Corn, Paddy Rice, Sugarcane, Orchard, Vineyard, Greenhouse).
* Executes Prim's Algorithm (Optimal CapEx: **$121.00k**).
* Executes Kruskal's Algorithm (Validates identical **$121.00k** cost across 9 edges).
* Solves Dijkstra's Algorithm (Identifies minimum head loss corridor: $\text{Reservoir} \to \text{Pump\_North} \to \text{Corn\_N} \to \text{Sugarcane\_SW}$ with $1.55\text{ bar}$ loss, yielding $2.95\text{ bar}$ nozzle delivery pressure).
* Generates all presentation figures:
  * `farm_topography.png`
  * `mst_highlight.png`
  * `dijkstra_simulation.png`
  * `farm_irrigation_master_presentation.png`

#### Option 2: Custom Farm Configuration Builder
* Interactively configure your own farm fields:
  * Specify custom field count (e.g., $3$ to $10$).
  * Define custom field names and crop types.
  * Enter custom pipe distances (in meters) and trench costs ($\$k$).
* Automatically runs Prim's, Kruskal's, and Dijkstra's algorithms on your custom layout.
* Generates custom visual plots: `custom_farm_topography.png`, `custom_mst_highlight.png`, `custom_dijkstra_flow.png`, and `custom_farm_dashboard.png`.

#### Option 3: Run DAA Algorithm Benchmark Analysis
* Executes the automated empirical performance suite across $V \in [10, 50, 100, 500, 1000]$.
* Renders [performance_plot.png](performance_plot.png) showing Graph Size ($|V| + |E|$) on the X-axis vs Execution Time (ms) on the Y-axis.
* Displays the empirical summary table verifying $\mathcal{O}(E \log V)$ convergence.

---

### Step 3b: Launch the Interactive Web Dashboard (Streamlit)
To launch the interactive browser dashboard with visual topologies, real-time sliders, and live benchmark simulations:
```bash
streamlit run app.py
```
* **Dashboard Features:**
  * **Sidebar:** Choose between Default 10-node farm, 5-node compact farm, or 25-node estate. Adjust Reservoir static head (bar) and pipe friction factor in real time.
  * **Tab 1 (Topology & MST):** Interactive view of farm topography, Prim's vs Kruskal's MST, and edge selection step traces.
  * **Tab 2 (Hydraulic Dijkstra Routing):** Live water flow corridor simulation with nozzle pressure adequacy banners.
  * **Tab 3 (Live Benchmarks):** One-click execution of $|V| \in [10, 1000]$ empirical scaling with live charts and summary table.
  * **Tab 4 (Viva Voce Reference):** Asymptotic complexities, invariant proofs, and professor Q&A cheat sheet.

---

### Step 4: Non-Interactive / Batch Execution Flags
For scripted grading or automated test execution:
```bash
# Run Option 1 directly (Default simulation)
python main.py --sim

# Run Option 2 directly (Custom configuration)
python main.py --custom

# Run Option 3 directly (Benchmarks & performance plots)
python main.py --benchmark
```

---

### Step 5: Run Automated Unit Tests
Verify all algorithmic invariants and visual rendering functions:
```bash
py -m pytest
```
* **8 passed in ~13 seconds** across all test suites in `tests/`.

---

## 🖼️ 6. Generated Visualization Gallery

| Artifact | Visual Role & Content |
| :--- | :--- |
| **`farm_topography.png`** | 2D Cartesian farm site plan with distinct node icons (Reservoir square, Pump pentagon, Crop circle, Greenhouse diamond) with labeled distances ($m$), pipe diameters ($\varnothing\text{ mm}$), and costs ($\$k$). |
| **`mst_highlight.png`** | Highlights optimal pipe laying trench layout in vivid emerald green (`#059669`) with an underlay glow over the inactive gray dashed network mesh. |
| **`dijkstra_simulation.png`** | Displays directional water flow corridor (`-|>` arrows) from source Reservoir to destination with pressure loss ($\Delta P$) and nozzle delivery pressure check. |
| **`performance_plot.png`** | Dual-panel empirical benchmark chart: Graph Size ($|V| + |E|$) vs Runtime (ms), and asymptotic constant factor convergence ($c = T / [E \log_2 V]$). |
| **`farm_irrigation_master_presentation.png`** | Executive 3-in-1 wide-format presentation dashboard combining Topography, MST, and Dijkstra routing for project presentations and viva defense. |

---

## 🎓 7. Academic Viva Voce Defense

For mathematical proofs (Cut Property, Cycle Property, Inverse Ackermann function $\alpha(V)$ derivation) and the Top 5 Professor Viva Voce questions with model answers, refer to [DAA_VIVA_DEFENSE_GUIDE.md](DAA_VIVA_DEFENSE_GUIDE.md).
