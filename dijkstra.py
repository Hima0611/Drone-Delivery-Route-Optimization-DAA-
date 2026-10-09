"""
dijkstra.py
-----------
Manual implementation of Dijkstra's Shortest Path Algorithm using a Binary Heap (heapq).
Provides step-by-step trace analysis for educational demonstration in DAA mini-projects,
as well as alternative route computation for comparison.
"""

import heapq

def dijkstra_shortest_path(delivery_graph, source, destination):
    """
    Computes the single-source shortest path using manual Dijkstra's algorithm.

    Parameters:
        delivery_graph (DeliveryGraph): Graph instance containing nodes & adjacency list.
        source (str): Source node name.
        destination (str): Target/destination node name.

    Returns:
        dict with keys:
            'path': list of nodes in shortest path from source to destination.
            'distance': float total path distance (inf if no path exists).
            'distances': dict of shortest distances from source to all nodes.
            'predecessors': dict mapping each node to its predecessor.
            'steps': list of dicts recording step-by-step algorithm trace.
    """
    nodes = delivery_graph.get_nodes()

    # Handle edge cases
    if source not in nodes or destination not in nodes:
        return {
            'path': [],
            'distance': float('inf'),
            'distances': {},
            'predecessors': {},
            'steps': []
        }

    # Step 1: Initialize distances to infinity and predecessor map to None
    distances = {node: float('inf') for node in nodes}
    predecessors = {node: None for node in nodes}
    visited = set()

    # Distance to source node is 0
    distances[source] = 0.0

    # Priority Queue (Min-Heap): Stores tuples of (current_distance, node_name)
    priority_queue = [(0.0, source)]

    # Step trace for algorithm visualization table
    steps = []
    step_counter = 1

    while priority_queue:
        # Step 2: Pop node with smallest tentative distance
        current_dist, current_node = heapq.heappop(priority_queue)

        # Skip duplicate entries in priority queue if already visited
        if current_node in visited:
            continue

        visited.add(current_node)

        # Stop early if destination is popped (greedy property guarantee)
        if current_node == destination:
            # Record final reach step
            steps.append({
                'step': step_counter,
                'current_node': current_node,
                'neighbor': '-',
                'edge_weight': '-',
                'old_dist': f"{current_dist:.1f}",
                'new_dist': f"{current_dist:.1f}",
                'action': f"Reached Target '{destination}'",
                'pq_state': str([n for d, n in priority_queue])
            })
            break

        # Step 3: Evaluate neighbors (Edge Relaxation Step)
        neighbors = delivery_graph.get_neighbors(current_node)
        for neighbor, weight in neighbors.items():
            if neighbor in visited:
                continue

            tentative_dist = current_dist + weight
            old_dist = distances[neighbor]

            # Step 4: Relaxation condition: d[u] + w(u, v) < d[v]
            if tentative_dist < old_dist:
                distances[neighbor] = tentative_dist
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (tentative_dist, neighbor))
                
                action = f"Updated dist of '{neighbor}' ({old_dist if old_dist != float('inf') else '∞'} -> {tentative_dist:.1f})"
                
                steps.append({
                    'step': step_counter,
                    'current_node': current_node,
                    'neighbor': neighbor,
                    'edge_weight': weight,
                    'old_dist': '∞' if old_dist == float('inf') else f"{old_dist:.1f}",
                    'new_dist': f"{tentative_dist:.1f}",
                    'action': action,
                    'pq_state': str([f"{n}:{d:.1f}" for d, n in sorted(priority_queue)])
                })
                step_counter += 1
            else:
                action = f"Skipped '{neighbor}' (tentative {tentative_dist:.1f} >= current {old_dist:.1f})"
                steps.append({
                    'step': step_counter,
                    'current_node': current_node,
                    'neighbor': neighbor,
                    'edge_weight': weight,
                    'old_dist': f"{old_dist:.1f}",
                    'new_dist': f"{old_dist:.1f}",
                    'action': action,
                    'pq_state': str([f"{n}:{d:.1f}" for d, n in sorted(priority_queue)])
                })
                step_counter += 1

    # Step 5: Reconstruct shortest path from destination back to source
    path = []
    curr = destination
    if distances[destination] != float('inf'):
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()

    return {
        'path': path,
        'distance': distances[destination],
        'distances': distances,
        'predecessors': predecessors,
        'steps': steps
    }


def find_alternative_paths(delivery_graph, source, destination, max_paths=3):
    """
    Finds alternative simple paths between source and destination
    to demonstrate why Dijkstra's chosen path is optimal compared to alternatives.

    Returns:
        List of dicts: [{'path': [...], 'distance': float}, ...] sorted by distance.
    """
    nodes = delivery_graph.get_nodes()
    if source not in nodes or destination not in nodes:
        return []

    all_paths = []

    def dfs(curr, visited, path, dist):
        if len(all_paths) >= 20:  # limit search depth for efficiency
            return
        if curr == destination:
            all_paths.append({'path': list(path), 'distance': dist})
            return

        for neighbor, weight in delivery_graph.get_neighbors(curr).items():
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, visited, path, dist + weight)
                path.pop()
                visited.remove(neighbor)

    visited_set = {source}
    dfs(source, visited_set, [source], 0.0)

    # Sort paths by distance
    all_paths.sort(key=lambda x: x['distance'])

    # Deduplicate and return top max_paths
    unique_paths = []
    seen_path_tuples = set()
    for p in all_paths:
        tup = tuple(p['path'])
        if tup not in seen_path_tuples:
            seen_path_tuples.add(tup)
            unique_paths.append(p)
            if len(unique_paths) >= max_paths:
                break

    return unique_paths
