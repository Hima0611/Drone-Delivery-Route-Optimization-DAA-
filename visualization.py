"""
visualization.py
----------------
Handles graph layout and rendering using Matplotlib and NetworkX.
Displays node roles (Warehouse, Customer, Charging Station, Source, Target)
and highlights the shortest path computed by Dijkstra's algorithm.
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

# Custom Color Palette
COLOR_DEFAULT_NODE = "#90CAF9"     # Soft Blue for standard customer nodes
COLOR_SOURCE = "#4CAF50"           # Green for Source Node
COLOR_DESTINATION = "#E53935"      # Red for Destination Node
COLOR_PATH_NODE = "#FF9800"        # Orange for Intermediate Shortest Path Nodes
COLOR_WAREHOUSE = "#7E57C2"        # Purple for Warehouse Node
COLOR_CHARGING = "#FBC02D"         # Gold/Amber for Charging Station

COLOR_DEFAULT_EDGE = "#B0BEC5"     # Light Gray for unselected edges
COLOR_PATH_EDGE = "#D32F2F"        # Dark Red/Coral for Shortest Path Edges

def draw_graph(delivery_graph, shortest_path=None, source=None, destination=None, figure=None, ax=None):
    """
    Renders the graph onto a Matplotlib axes object with custom node styling and path highlighting.

    Parameters:
        delivery_graph (DeliveryGraph): Graph object containing nodes, edges, positions.
        shortest_path (list): List of node names in calculated shortest path.
        source (str): Currently selected source node.
        destination (str): Currently selected destination node.
        figure (matplotlib.figure.Figure): Target figure.
        ax (matplotlib.axes.Axes): Target axes object.
    """
    if figure is None or ax is None:
        figure, ax = plt.subplots(figsize=(7, 5), dpi=100)

    ax.clear()

    G = delivery_graph.to_networkx()
    nodes = list(G.nodes())

    if not nodes:
        ax.text(0.5, 0.5, "Graph is empty", horizontalalignment='center', verticalalignment='center', fontsize=14)
        ax.axis('off')
        return figure, ax

    # Determine position mapping
    pos = {}
    for node in nodes:
        if node in delivery_graph.node_positions:
            pos[node] = delivery_graph.node_positions[node]
    
    # Fallback to spring layout for missing node positions
    missing_nodes = [n for n in nodes if n not in pos]
    if missing_nodes:
        spring_pos = nx.spring_layout(G, seed=42)
        for n in missing_nodes:
            pos[n] = spring_pos[n]

    # Categorize node colors and sizes
    node_colors = []
    node_sizes = []
    
    path_set = set(shortest_path) if shortest_path else set()
    path_edges = set()
    if shortest_path and len(shortest_path) > 1:
        for i in range(len(shortest_path) - 1):
            u, v = shortest_path[i], shortest_path[i+1]
            path_edges.add(tuple(sorted([u, v])))

    for node in nodes:
        if node == source:
            node_colors.append(COLOR_SOURCE)
            node_sizes.append(1200)
        elif node == destination:
            node_colors.append(COLOR_DESTINATION)
            node_sizes.append(1200)
        elif node in path_set:
            node_colors.append(COLOR_PATH_NODE)
            node_sizes.append(1000)
        elif "warehouse" in node.lower():
            node_colors.append(COLOR_WAREHOUSE)
            node_sizes.append(1100)
        elif "charging" in node.lower():
            node_colors.append(COLOR_CHARGING)
            node_sizes.append(1000)
        else:
            node_colors.append(COLOR_DEFAULT_NODE)
            node_sizes.append(850)

    # Separate edges into path edges and regular edges
    regular_edges = []
    highlight_edges = []

    for u, v in G.edges():
        edge_key = tuple(sorted([u, v]))
        if edge_key in path_edges:
            highlight_edges.append((u, v))
        else:
            regular_edges.append((u, v))

    # Draw regular edges
    nx.draw_networkx_edges(
        G, pos, edgelist=regular_edges, ax=ax,
        edge_color=COLOR_DEFAULT_EDGE, width=2.0, style='dashed', alpha=0.8
    )

    # Draw shortest path edges (bold)
    if highlight_edges:
        nx.draw_networkx_edges(
            G, pos, edgelist=highlight_edges, ax=ax,
            edge_color=COLOR_PATH_EDGE, width=4.5, style='solid', alpha=0.95
        )

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors, node_size=node_sizes,
        edgecolors='#333333', linewidths=1.5
    )

    # Draw node labels
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=9, font_weight='bold', font_family='sans-serif',
        font_color='#111111'
    )

    # Edge weight labels
    edge_labels = {(u, v): f"{d['weight']:.1f} km" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, ax=ax,
        font_size=8, font_color='#2C3E50', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#B0BEC5', alpha=0.85)
    )

    # Add Legend
    legend_elements = [
        Patch(facecolor=COLOR_SOURCE, edgecolor='#333', label='Source Node'),
        Patch(facecolor=COLOR_DESTINATION, edgecolor='#333', label='Destination Node'),
        Patch(facecolor=COLOR_PATH_NODE, edgecolor='#333', label='Shortest Path Node'),
        Patch(facecolor=COLOR_WAREHOUSE, edgecolor='#333', label='Warehouse'),
        Patch(facecolor=COLOR_CHARGING, edgecolor='#333', label='Charging Station'),
        Patch(facecolor=COLOR_DEFAULT_NODE, edgecolor='#333', label='Customer Node'),
        plt.Line2D([0], [0], color=COLOR_PATH_EDGE, lw=3, label='Optimal Flight Path')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7.5, framealpha=0.9)

    ax.set_title("Drone Flight Network Graph", fontsize=12, fontweight='bold', pad=10)
    ax.axis('off')
    figure.tight_layout()

    return figure, ax
