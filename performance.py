"""
performance.py
--------------
Empirical performance benchmarking module for Dijkstra's Shortest Path Algorithm.
Generates connected weighted graphs of varying node counts (10 to 200 nodes),
runs high-precision timing measurements, and returns formatted benchmark data.
"""

import time
import random
import networkx as nx
from graph_data import DeliveryGraph
from dijkstra import dijkstra_shortest_path

def generate_random_connected_graph(node_count, avg_degree=3):
    """
    Generates a connected random weighted DeliveryGraph for benchmark testing.

    Parameters:
        node_count (int): Total number of vertices (V).
        avg_degree (int): Target average degree of each node.

    Returns:
        DeliveryGraph instance containing V nodes and ~ (V * avg_degree / 2) edges.
    """
    g = DeliveryGraph()
    g.adj.clear()
    g.node_positions.clear()

    # Step 1: Create nodes
    nodes = [f"Node_{i+1}" for i in range(node_count)]
    for n in nodes:
        g.add_node(n)

    # Step 2: Ensure graph connectivity by creating a random spanning tree
    shuffled_nodes = list(nodes)
    random.shuffle(shuffled_nodes)
    for i in range(len(shuffled_nodes) - 1):
        u = shuffled_nodes[i]
        v = shuffled_nodes[i + 1]
        dist = round(random.uniform(2.0, 15.0), 1)
        g.add_edge(u, v, dist)

    # Step 3: Add additional random edges to match target edge density
    target_edges = max(node_count, (node_count * avg_degree) // 2)
    current_edges = len(g.get_edges())

    attempts = 0
    max_attempts = node_count * 10
    while current_edges < target_edges and attempts < max_attempts:
        attempts += 1
        u, v = random.sample(nodes, 2)
        if v not in g.get_neighbors(u):
            dist = round(random.uniform(2.0, 15.0), 1)
            g.add_edge(u, v, dist)
            current_edges += 1

    return g

def run_performance_benchmark(node_sizes=[10, 25, 50, 100, 200], iterations=5):
    """
    Runs empirical performance testing across various graph sizes.

    Parameters:
        node_sizes (list): List of node counts to test.
        iterations (int): Number of test runs per size to average execution timing.

    Returns:
        list of dicts containing node count, edge count, execution time (ms), and sample shortest distance.
    """
    results = []

    for n in node_sizes:
        total_time_ns = 0
        sample_dist = 0.0
        edge_count = 0

        for _ in range(iterations):
            graph = generate_random_connected_graph(n)
            nodes = graph.get_nodes()
            source = nodes[0]
            destination = nodes[-1]

            edge_count = len(graph.get_edges())

            # Measure precise execution time of manual Dijkstra algorithm
            start_time = time.perf_counter_ns()
            res = dijkstra_shortest_path(graph, source, destination)
            end_time = time.perf_counter_ns()

            total_time_ns += (end_time - start_time)
            if res['distance'] != float('inf'):
                sample_dist = res['distance']

        avg_time_ms = (total_time_ns / iterations) / 1e6

        results.append({
            'nodes': n,
            'edges': edge_count,
            'exec_time_ms': round(avg_time_ms, 3),
            'distance': round(sample_dist, 1)
        })

    return results

if __name__ == "__main__":
    print("Testing Performance Benchmark...")
    bench = run_performance_benchmark()
    print(f"{'Nodes':<8} | {'Edges':<8} | {'Exec Time (ms)':<15} | {'Distance (km)':<15}")
    print("-" * 55)
    for r in bench:
        print(f"{r['nodes']:<8} | {r['edges']:<8} | {r['exec_time_ms']:<15.3f} | {r['distance']:<15.1f}")
