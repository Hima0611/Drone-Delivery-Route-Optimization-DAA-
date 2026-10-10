# Design and Analysis of an Optimized Drone Delivery Route Using Graph Algorithms

**Autonomous Drone Flight Path & Route Optimization System**  
🌐 **Live Working Web App**: [https://drone-delivery-route-optimization-daa.onrender.com](https://drone-delivery-route-optimization-daa.onrender.com)

---



## 1. Project Overview

The **Drone Delivery Route Optimizer** is a graph-based simulation tool designed to compute the shortest and most energy-efficient flight paths for autonomous drones. This application models geographic locations (warehouses, customer destinations, and charging waypoints) as a weighted graph.

The project provides **Dual Interface Modes**:
1. 💻 **Tkinter Desktop GUI** (`python app.py`)
2. 🌐 **Modern Web Frontend** (`python web_app.py`) built with **HTML5**, **CSS3**, **JavaScript**, **Vis.js**, **Chart.js**, and **Flask**.

Both interfaces feature a **manual implementation of Dijkstra’s Shortest Path Algorithm** using a priority queue (`heapq`), step-by-step trace analysis, battery feasibility calculations, route comparison, graph management, and empirical performance benchmarks.

---

## 2. Problem Statement

Autonomous drone delivery systems face operational constraints, primarily limited battery flight endurance and varying geographic distances between delivery hubs and customers. Finding the shortest flight distance minimizes total energy consumption, reduces flight risk, and ensures flight feasibility.

This project addresses the path optimization problem by modeling flight corridors as a weighted graph $G = (V, E)$ and applying Dijkstra's algorithm to determine optimal delivery routes.

---

## 3. Project Objectives

- Represent drone flight networks using a **Weighted Undirected Graph**.
- Implement **Dijkstra’s Algorithm manually** using a Min-Heap (`heapq`) without relying on pre-built shortest path library functions.
- Provide both a **Tkinter Desktop GUI** and a **Web Frontend (HTML5/CSS3/JS)** with interactive graph rendering.
- Visualize the graph dynamically with highlighted optimal flight paths.
- Incorporate a **Simplified Battery Feasibility Model** to check if a flight route is executable within drone battery capacity.
- Perform **Theoretical and Empirical Complexity Analysis** on graph sizes ranging from 10 to 200 nodes.

---

## 4. Key Features

- 🚁 **Manual Dijkstra Shortest Path Solver**: Finds the exact minimum-cost route between any selected source and destination.
- 🔋 **Battery & Flight Time Estimator**: Calculates required battery percentage and estimated flight duration (minutes) based on burn rate (%/km) and speed (km/h).
- 📊 **Step-by-Step Algorithm Visualization**: Displays an interactive table tracing node relaxations, priority queue states, and distance updates.
- 🎨 **Dynamic Interactive Graph Visualization**: Renders node roles (Warehouse, Customers, Charging Station) and highlights the optimal path in bold red.
- 🛠 **Interactive Graph Editor**: Allows users to dynamically add/remove nodes and add/remove weighted flight edges.
- 🔄 **Route Comparison**: Displays alternative routes (2nd and 3rd shortest simple paths) to demonstrate greedy optimization.
- ⏱ **Empirical Performance Benchmarking**: Measures and plots execution times for graphs of size $V = 10, 25, 50, 100, 200$.

---

## 5. Technology Stack

- **Backend / Core Engine**: Python 3.x, `heapq`, NetworkX
- **Desktop GUI**: Tkinter (`ttk` widgets), Matplotlib (`FigureCanvasTkAgg`)
- **Web Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Web Graph Visualizer**: Vis.js Network Library
- **Web Charting**: Chart.js
- **Web Server Framework**: Flask

---

## 6. Graph Representation

The network is modeled as a weighted undirected graph $G = (V, E, W)$:

- **Vertices ($V$)**:
  - `Warehouse` (Dispatch hub)
  - `Customer A` through `Customer F` (Delivery locations)
  - `Charging Station` (Recharge waypoint)
- **Edges ($E$)**: Feasible flight corridors connecting locations.
- **Weights ($W$)**: Non-negative flight distance in kilometers (km).

### Default Delivery Network Connections
```text
Warehouse <---> Customer A (5.0 km)
Warehouse <---> Customer B (8.0 km)
Customer A <---> Customer B (3.0 km)
Customer A <---> Customer C (6.0 km)
Customer B <---> Customer C (4.0 km)
Customer C <---> Customer D (5.0 km)
Customer D <---> Customer E (3.0 km)
Customer C <---> Customer F (7.0 km)
Customer B <---> Charging Station (4.0 km)
Charging Station <---> Customer E (6.0 km)
Customer E <---> Customer F (4.0 km)
```

---

## 7. Dijkstra’s Shortest Path Algorithm

### Algorithm Overview
Dijkstra's algorithm follows a **Greedy Strategy**:
1. Maintains a distance map $d[u]$ initialized to $\infty$ for all vertices except the source $s$, where $d[s] = 0$.
2. Uses a **Min-Heap Priority Queue** to greedily pop the unvisited node $u$ with the minimum tentative distance.
3. Performs **Edge Relaxation** for every neighbor $v$ of $u$:
   $$\text{if } d[u] + w(u, v) < d[v] \implies d[v] = d[u] + w(u, v)$$
4. Tracks predecessors in a map $\pi[v]$ to reconstruct the final shortest path.

### Pseudocode
```text
Algorithm Manual_Dijkstra(G, source, target):
    Input: Graph G = (V, E), Source vertex 'source', Target vertex 'target'
    Output: Shortest distance d[target] and path sequence

    Initialize dist[v] = INFINITY for all v in V
    Initialize prev[v] = NULL for all v in V
    Initialize visited = empty set
    dist[source] = 0

    Initialize MinHeap priority_queue
    Insert (0, source) into priority_queue

    while priority_queue is not empty:
        (current_dist, u) = Extract_Min(priority_queue)

        if u is in visited:
            continue
        Add u to visited

        if u == target:
            break

        for each neighbor v of u with weight w(u, v):
            if v is not in visited:
                if dist[u] + w(u, v) < dist[v]:
                    dist[v] = dist[u] + w(u, v)
                    prev[v] = u
                    Insert (dist[v], v) into priority_queue

    Reconstruct path from target to source using prev[]
    Return path, dist[target]
```

---

## 8. Complexity Analysis

### Time Complexity
- **Adjacency List + Binary Heap (heapq)**:
  - Extract-Min operation is executed at most $V$ times: $O(V \log V)$
  - Edge relaxation / Decrease-Key operation is executed at most $E$ times: $O(E \log V)$
  - Total Time Complexity: $$\mathcal{O}((V + E) \log V)$$
- For sparse connected graphs ($E \approx V$), this is commonly simplified to $\mathcal{O}(E \log V)$.

### Space Complexity
- Adjacency List graph representation: $\mathcal{O}(V + E)$
- Priority Queue storage: $\mathcal{O}(V)$
- Distance array and predecessor map: $\mathcal{O}(V)$
- Total Space Complexity: $$\mathcal{O}(V + E)$$

---

## 9. Project Structure

```text
drone_delivery_optimizer/
│
├── app.py              # Tkinter Desktop GUI Application
├── web_app.py          # Flask Web Backend Server
├── dijkstra.py         # Manual Dijkstra Algorithm & Step Trace
├── graph_data.py       # Graph Representation & Default Network Data
├── visualization.py    # Matplotlib + NetworkX Drawing Module
├── performance.py      # Empirical Performance Benchmarking Module
├── requirements.txt    # Required Python Libraries
├── README.md           # Documentation & Academic Report
│
├── static/
│   ├── css/
│   │   └── style.css   # Custom CSS Stylesheet & Glassmorphism Theme
│   └── js/
│       └── main.js     # Frontend JS & Vis.js Interactive Graph Engine
│
├── templates/
│   └── index.html      # HTML5 Web Interface Layout
│
└── screenshots/
    └── sample_graph.png # Pre-rendered Network Graph Visualization
```

---

## 10. Live Web App & Local Execution Guide

### 🌐 Live Deployment
The web application is deployed and hosted live at:  
👉 **[https://drone-delivery-route-optimization-daa.onrender.com](https://drone-delivery-route-optimization-daa.onrender.com)**

---

### Prerequisites (For Local Setup)

- Python 3.8+ installed on your system.

### Step 1: Navigate to Project Directory
```bash
cd drone_delivery_optimizer
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Desktop GUI (Option A)
```bash
python app.py
```

### Step 4: Run Web Application Frontend (Option B)
```bash
python web_app.py
```
Then open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 11. Sample Inputs & Outputs

### Sample Scenario 1: Standard Route Calculation
- **Source**: `Warehouse`
- **Destination**: `Customer D`
- **Battery Capacity**: `100 %`
- **Burn Rate**: `5.0 %/km`
- **Drone Speed**: `30 km/h`

#### Result Output
```text
Optimal Route: Warehouse → Customer A → Customer C → Customer D
Total Distance: 16.0 km
Estimated Flight Time: 32.0 minutes
Battery Required: 80.0% (16.0 km × 5.0%/km)
Remaining Battery: 20.0%
Route Status: ✓ Route Feasible (Sufficient Battery)
```

---

## 12. Empirical Performance Results

Execution times measured on synthetic connected graphs (average of 5 test runs):

| Nodes ($V$) | Edges ($E$) | Measured Exec Time (ms) | Sample Distance (km) |
|-------------|-------------|-------------------------|----------------------|
| 10          | 15          | 0.13 ms                 | 17.5 km              |
| 25          | 37          | 0.25 ms                 | 20.2 km              |
| 50          | 75          | 0.41 ms                 | 6.8 km               |
| 100         | 150         | 1.51 ms                 | 50.3 km              |
| 200         | 300         | 9.54 ms                 | 17.5 km              |
