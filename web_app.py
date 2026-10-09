"""
web_app.py
----------
Flask Web Backend for the Drone Delivery Route Optimizer DAA Mini-Project.
Exposes RESTful JSON APIs for graph management, manual Dijkstra path calculation,
battery feasibility modeling, step trace logs, and performance benchmarks.
Serves the HTML5 + CSS3 + JS frontend interface.
"""

from flask import Flask, render_template, jsonify, request
from graph_data import DeliveryGraph
from dijkstra import dijkstra_shortest_path, find_alternative_paths
from performance import run_performance_benchmark

app = Flask(__name__)

# Global DeliveryGraph Instance
delivery_graph = DeliveryGraph()

@app.route("/")
def index():
    """Renders the main web application frontend dashboard."""
    return render_template("index.html")

@app.route("/api/graph", methods=["GET"])
def get_graph():
    """Returns current graph nodes, weighted edges, and 2D visual layout positions."""
    nodes = delivery_graph.get_nodes()
    edges = [
        {"from": u, "to": v, "weight": w, "label": f"{w:.1f} km"}
        for u, v, w in delivery_graph.get_edges()
    ]
    positions = delivery_graph.node_positions
    return jsonify({
        "nodes": nodes,
        "edges": edges,
        "positions": positions
    })

@app.route("/api/optimize", methods=["POST"])
def optimize_route():
    """Calculates manual Dijkstra shortest path, battery metrics, alternative routes, and step trace."""
    data = request.json or {}
    source = data.get("source", "").strip()
    destination = data.get("destination", "").strip()
    
    try:
        battery_capacity = float(data.get("battery_capacity", 100.0))
        burn_rate = float(data.get("burn_rate", 5.0))
        speed = float(data.get("speed", 30.0))
        
        if battery_capacity <= 0 or burn_rate <= 0 or speed <= 0:
            return jsonify({"error": "Battery capacity, burn rate, and speed must be positive numbers."}), 400
    except ValueError:
        return jsonify({"error": "Invalid numerical parameters."}), 400

    if not source or not destination:
        return jsonify({"error": "Source and destination nodes must be specified."}), 400

    # Run Dijkstra
    res = dijkstra_shortest_path(delivery_graph, source, destination)
    path = res["path"]
    distance = res["distance"]

    if not path or distance == float("inf"):
        return jsonify({
            "feasible": False,
            "error_msg": "No path exists between selected locations.",
            "path": [],
            "distance": float("inf"),
            "steps": res.get("steps", [])
        })

    flight_time_mins = (distance / speed) * 60.0
    battery_required = distance * burn_rate
    remaining_battery = battery_capacity - battery_required
    is_feasible = (battery_capacity >= battery_required)

    alternatives = find_alternative_paths(delivery_graph, source, destination, max_paths=3)
    formatted_alternatives = []
    for alt in alternatives:
        alt_dist = alt["distance"]
        alt_bat = alt_dist * burn_rate
        formatted_alternatives.append({
            "path": alt["path"],
            "distance": alt_dist,
            "battery_required": alt_bat,
            "feasible": (battery_capacity >= alt_bat)
        })

    return jsonify({
        "feasible": is_feasible,
        "path": path,
        "distance": round(distance, 2),
        "flight_time_mins": round(flight_time_mins, 1),
        "battery_capacity": round(battery_capacity, 1),
        "battery_required": round(battery_required, 1),
        "remaining_battery": round(remaining_battery, 1),
        "burn_rate": burn_rate,
        "speed": speed,
        "alternatives": formatted_alternatives,
        "steps": res.get("steps", [])
    })

@app.route("/api/node", methods=["POST"])
def add_node():
    """Adds a new node to the graph network."""
    data = request.json or {}
    name = data.get("name", "").strip()
    success, msg = delivery_graph.add_node(name)
    if success:
        return jsonify({"message": msg, "nodes": delivery_graph.get_nodes()})
    return jsonify({"error": msg}), 400

@app.route("/api/node", methods=["DELETE"])
def remove_node():
    """Removes a node from the graph network."""
    data = request.json or {}
    name = data.get("name", "").strip()
    success, msg = delivery_graph.remove_node(name)
    if success:
        return jsonify({"message": msg, "nodes": delivery_graph.get_nodes()})
    return jsonify({"error": msg}), 400

@app.route("/api/edge", methods=["POST"])
def add_edge():
    """Adds or updates a weighted edge."""
    data = request.json or {}
    u = data.get("u", "").strip()
    v = data.get("v", "").strip()
    try:
        w = float(data.get("weight", 0))
    except ValueError:
        return jsonify({"error": "Edge weight must be a valid number."}), 400

    success, msg = delivery_graph.add_edge(u, v, w)
    if success:
        return jsonify({"message": msg, "edges": delivery_graph.get_edges()})
    return jsonify({"error": msg}), 400

@app.route("/api/edge", methods=["DELETE"])
def remove_edge():
    """Removes an edge between two nodes."""
    data = request.json or {}
    u = data.get("u", "").strip()
    v = data.get("v", "").strip()
    success, msg = delivery_graph.remove_edge(u, v)
    if success:
        return jsonify({"message": msg, "edges": delivery_graph.get_edges()})
    return jsonify({"error": msg}), 400

@app.route("/api/reset", methods=["POST"])
def reset_graph():
    """Resets graph network to default setup."""
    delivery_graph.load_default_graph()
    return jsonify({"message": "Graph restored to default state.", "nodes": delivery_graph.get_nodes()})

@app.route("/api/benchmark", methods=["GET"])
def get_benchmark():
    """Runs empirical performance benchmark and returns timing data."""
    results = run_performance_benchmark(node_sizes=[10, 25, 50, 100, 200], iterations=5)
    return jsonify({"results": results})

if __name__ == "__main__":
    print("Starting Drone Delivery Route Optimizer Web Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
