"""
graph_data.py
-------------
Represents the weighted graph structure for the Drone Delivery Route Optimization system.
Includes default network configurations, node management, edge operations, and
conversion helpers for NetworkX visualization.
"""

from collections import defaultdict
import networkx as nx

class DeliveryGraph:
    """
    Weighted Undirected Graph representation using an adjacency list.
    Suitable for Dijkstra's Shortest Path Algorithm and NetworkX conversion.
    """
    def __init__(self):
        self.adj = defaultdict(dict)
        self.node_positions = {}
        self.load_default_graph()

    def load_default_graph(self):
        """Loads the default drone delivery network with realistic 2D layout coordinates."""
        self.adj.clear()
        
        # Default Edges and Weights (in kilometers)
        default_edges = [
            ("Warehouse", "Customer A", 5.0),
            ("Warehouse", "Customer B", 8.0),
            ("Customer A", "Customer B", 3.0),
            ("Customer A", "Customer C", 6.0),
            ("Customer B", "Customer C", 4.0),
            ("Customer C", "Customer D", 5.0),
            ("Customer D", "Customer E", 3.0),
            ("Customer C", "Customer F", 7.0),
            ("Customer B", "Charging Station", 4.0),
            ("Charging Station", "Customer E", 6.0),
            ("Customer E", "Customer F", 4.0)
        ]

        for u, v, w in default_edges:
            self.add_edge(u, v, w)

        # Default 2D layout positions for clean Matplotlib visualization
        self.node_positions = {
            "Warehouse": (0.0, 2.0),
            "Customer A": (2.0, 3.5),
            "Customer B": (2.5, 0.5),
            "Charging Station": (4.5, -0.5),
            "Customer C": (5.0, 3.0),
            "Customer D": (7.5, 3.5),
            "Customer E": (7.0, 0.5),
            "Customer F": (9.0, 2.0)
        }

    def add_node(self, node_name, pos=None):
        """Adds a new node to the graph if it doesn't already exist."""
        node_name = node_name.strip()
        if not node_name:
            return False, "Node name cannot be empty."
        if node_name not in self.adj:
            self.adj[node_name] = {}
            if pos:
                self.node_positions[node_name] = pos
            else:
                # Assign default position if none provided
                self.node_positions[node_name] = (len(self.adj) * 1.2, 1.0)
            return True, f"Node '{node_name}' added successfully."
        return False, f"Node '{node_name}' already exists."

    def remove_node(self, node_name):
        """Removes a node and all connecting edges from the graph."""
        if node_name in self.adj:
            # Remove node from neighbor lists
            for neighbor in list(self.adj[node_name].keys()):
                del self.adj[neighbor][node_name]
            del self.adj[node_name]
            if node_name in self.node_positions:
                del self.node_positions[node_name]
            return True, f"Node '{node_name}' removed."
        return False, f"Node '{node_name}' not found."

    def add_edge(self, u, v, weight):
        """Adds or updates a weighted undirected edge between u and v."""
        u, v = u.strip(), v.strip()
        if not u or not v:
            return False, "Source and destination nodes must be specified."
        if u == v:
            return False, "Self-loops are not allowed."
        if weight <= 0:
            return False, "Edge weight (distance) must be positive."

        # Ensure both nodes exist in the adjacency dictionary
        if u not in self.adj:
            self.add_node(u)
        if v not in self.adj:
            self.add_node(v)

        self.adj[u][v] = float(weight)
        self.adj[v][u] = float(weight)
        return True, f"Edge ({u} <-> {v}, {weight} km) updated."

    def remove_edge(self, u, v):
        """Removes an edge between u and v."""
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
            del self.adj[v][u]
            return True, f"Edge ({u} <-> {v}) removed."
        return False, f"Edge between '{u}' and '{v}' does not exist."

    def get_nodes(self):
        """Returns a sorted list of all node names in the graph."""
        return sorted(list(self.adj.keys()))

    def get_edges(self):
        """Returns a list of unique tuples (u, v, weight) representing all edges."""
        edges = []
        seen = set()
        for u in self.adj:
            for v, w in self.adj[u].items():
                edge_key = tuple(sorted([u, v]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append((u, v, w))
        return edges

    def get_neighbors(self, node):
        """Returns a dictionary of {neighbor: weight} for a given node."""
        return self.adj.get(node, {})

    def to_networkx(self):
        """Converts internal graph to a NetworkX Graph instance for visualization."""
        G = nx.Graph()
        for u in self.adj:
            G.add_node(u)
            for v, w in self.adj[u].items():
                if u < v:  # Add undirected edge once
                    G.add_edge(u, v, weight=w)
        return G
