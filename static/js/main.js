/* ==========================================================================
   DRONE DELIVERY ROUTE OPTIMIZER - INTERACTIVE FRONTEND JS
   DAA Mini-Project Web Interface Logic & Vis.js Graph Rendering
   ========================================================================== */

let networkInstance = null;
let currentGraphData = { nodes: [], edges: [], positions: {} };
let benchmarkChart = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    fetchGraph();
});

// --- Tab Switcher ---
function switchTab(tabId) {
    document.querySelectorAll(".nav-tab").forEach(tab => tab.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));

    const targetTabBtn = Array.from(document.querySelectorAll(".nav-tab")).find(b => b.getAttribute("onclick").includes(tabId));
    if (targetTabBtn) targetTabBtn.classList.add("active");

    const targetContent = document.getElementById(`tab-${tabId}`);
    if (targetContent) targetContent.classList.add("active");

    if (tabId === 'optimizer' && networkInstance) {
        setTimeout(() => networkInstance.fit(), 100);
    }
}

// --- Fetch Graph from Server ---
async function fetchGraph() {
    try {
        const response = await fetch("/api/graph");
        const data = await response.json();
        currentGraphData = data;

        populateDropdowns(data.nodes);
        renderVisNetwork(data, []);
        renderEdgesTable(data.edges);
    } catch (err) {
        console.error("Error fetching graph data:", err);
    }
}

// --- Populate Dropdown Controls ---
function populateDropdowns(nodes) {
    const srcSelect = document.getElementById("select-source");
    const dstSelect = document.getElementById("select-dest");
    const uSelect = document.getElementById("edit-edge-u");
    const vSelect = document.getElementById("edit-edge-v");

    srcSelect.innerHTML = "";
    dstSelect.innerHTML = "";
    uSelect.innerHTML = "";
    vSelect.innerHTML = "";

    nodes.forEach(n => {
        srcSelect.add(new Option(n, n));
        dstSelect.add(new Option(n, n));
        uSelect.add(new Option(n, n));
        vSelect.add(new Option(n, n));
    });

    if (nodes.includes("Warehouse")) srcSelect.value = "Warehouse";
    if (nodes.includes("Customer D")) dstSelect.value = "Customer D";
    else if (nodes.length > 1) dstSelect.value = nodes[nodes.length - 1];
}

// --- Render Vis.js Interactive Network Graph ---
function renderVisNetwork(graphData, pathNodes = []) {
    const container = document.getElementById("canvas-graph");
    if (!container) return;

    const sourceNode = document.getElementById("select-source")?.value;
    const destNode = document.getElementById("select-dest")?.value;

    const pathSet = new Set(pathNodes);
    const pathEdges = new Set();
    if (pathNodes.length > 1) {
        for (let i = 0; i < pathNodes.length - 1; i++) {
            const pair = [pathNodes[i], pathNodes[i + 1]].sort().join("---");
            pathEdges.add(pair);
        }
    }

    const nodesArray = graphData.nodes.map(n => {
        let color = "#90CAF9"; // Default Customer Blue
        let shape = "dot";
        let size = 25;

        if (n === sourceNode) {
            color = "#4CAF50"; // Green
            size = 32;
        } else if (n === destNode) {
            color = "#E53935"; // Red
            size = 32;
        } else if (pathSet.has(n)) {
            color = "#FF9800"; // Orange Path Node
            size = 28;
        } else if (n.toLowerCase().includes("warehouse")) {
            color = "#7E57C2"; // Purple
            shape = "square";
            size = 30;
        } else if (n.toLowerCase().includes("charging")) {
            color = "#FBC02D"; // Gold
            shape = "diamond";
            size = 28;
        }

        const pos = graphData.positions[n];
        return {
            id: n,
            label: n,
            color: { background: color, border: "#333333" },
            shape: shape,
            size: size,
            x: pos ? pos[0] * 100 : undefined,
            y: pos ? -pos[1] * 100 : undefined,
            font: { size: 14, face: "Segoe UI", bold: true }
        };
    });

    const edgesArray = graphData.edges.map(e => {
        const pair = [e.from, e.to].sort().join("---");
        const isPathEdge = pathEdges.has(pair);

        return {
            from: e.from,
            to: e.to,
            label: e.label,
            color: isPathEdge ? { color: "#D32F2F", highlight: "#D32F2F" } : { color: "#B0BEC5" },
            width: isPathEdge ? 4.5 : 2.0,
            dashes: !isPathEdge,
            font: { size: 12, background: "#ffffff" }
        };
    });

    const data = {
        nodes: new vis.DataSet(nodesArray),
        edges: new vis.DataSet(edgesArray)
    };

    const options = {
        physics: { enabled: false },
        interaction: { hover: true, dragNodes: true, zoomView: true }
    };

    networkInstance = new vis.Network(container, data, options);
}

// --- Execute Route Optimization ---
async function optimizeRoute() {
    const source = document.getElementById("select-source").value;
    const destination = document.getElementById("select-dest").value;
    const batteryCapacity = parseFloat(document.getElementById("input-battery").value);
    const burnRate = parseFloat(document.getElementById("input-burn").value);
    const speed = parseFloat(document.getElementById("input-speed").value);

    if (!source || !destination) {
        alert("Please select valid Source and Destination locations.");
        return;
    }

    try {
        const response = await fetch("/api/optimize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source,
                destination,
                battery_capacity: batteryCapacity,
                burn_rate: burnRate,
                speed
            })
        });

        const res = await response.json();

        if (res.error) {
            alert(res.error);
            return;
        }

        const badge = document.getElementById("status-badge");
        if (res.feasible) {
            badge.className = "status-badge status-feasible";
            badge.innerText = "✓ Route Feasible (Sufficient Battery)";
        } else {
            badge.className = "status-badge status-infeasible";
            badge.innerText = res.path.length === 0 ? "⚠ No Path Found" : `⚠ Route Not Feasible! Required: ${res.battery_required}%, Available: ${res.battery_capacity}%`;
        }

        document.getElementById("res-path").innerText = res.path.length ? `Path: ${res.path.join(" → ")}` : "Path: Unreachable";
        document.getElementById("res-dist").innerText = res.distance !== null && res.distance !== undefined && res.distance !== Infinity ? `${res.distance} km` : "-";
        document.getElementById("res-time").innerText = res.flight_time_mins ? `${res.flight_time_mins} minutes` : "-";
        document.getElementById("res-battery-req").innerText = res.battery_required ? `${res.battery_required}%` : "-";
        document.getElementById("res-battery-rem").innerText = res.remaining_battery !== undefined ? `${res.remaining_battery}%` : "-";

        // Render Alternatives
        const altContainer = document.getElementById("alt-routes-container");
        altContainer.innerHTML = "";
        if (res.alternatives && res.alternatives.length > 0) {
            res.alternatives.forEach((alt, i) => {
                const card = document.createElement("div");
                card.className = `alt-route-card ${i === 0 ? 'optimal selected' : ''}`;
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                        <strong>Route ${i + 1}${i === 0 ? ' (Dijkstra Optimal)' : ''}:</strong>
                        <span class="alt-click-badge">Click to view ➔</span>
                    </div>
                    <div>${alt.path.join(" → ")}</div>
                    <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 2px;">Distance: ${alt.distance} km | Battery: ${alt.battery_required}%</div>
                `;

                card.addEventListener("click", () => {
                    selectAlternativeRoute(alt, i, speed, batteryCapacity, card);
                });

                altContainer.appendChild(card);
            });
        }

        // Highlight Graph & Update Steps Table
        renderVisNetwork(currentGraphData, res.path);
        renderStepsTable(res.steps || []);

    } catch (err) {
        console.error("Optimization error:", err);
    }
}

// --- Select and Display an Alternative Route ---
function selectAlternativeRoute(alt, index, speed, batteryCapacity, cardElement) {
    document.querySelectorAll(".alt-route-card").forEach(c => c.classList.remove("selected"));
    if (cardElement) {
        cardElement.classList.add("selected");
    }

    const dist = typeof alt.distance === "number" ? Math.round(alt.distance * 100) / 100 : alt.distance;
    const burnRate = parseFloat(document.getElementById("input-burn").value) || 5.0;
    const batteryReq = Math.round(dist * burnRate * 10) / 10;
    const flightTime = Math.round((dist / speed) * 60.0 * 10) / 10;
    const batteryRem = Math.round((batteryCapacity - batteryReq) * 10) / 10;
    const isFeasible = batteryCapacity >= batteryReq;

    const badge = document.getElementById("status-badge");
    if (isFeasible) {
        badge.className = "status-badge status-feasible";
        badge.innerText = `✓ Route ${index + 1} Feasible (Sufficient Battery)`;
    } else {
        badge.className = "status-badge status-infeasible";
        badge.innerText = `⚠ Route ${index + 1} Not Feasible! Required: ${batteryReq}%, Available: ${batteryCapacity}%`;
    }

    document.getElementById("res-path").innerText = alt.path && alt.path.length ? `Path: ${alt.path.join(" → ")}` : "Path: Unreachable";
    document.getElementById("res-dist").innerText = dist !== null && dist !== undefined && dist !== Infinity ? `${dist} km` : "-";
    document.getElementById("res-time").innerText = flightTime ? `${flightTime} minutes` : "-";
    document.getElementById("res-battery-req").innerText = batteryReq !== undefined ? `${batteryReq}%` : "-";
    document.getElementById("res-battery-rem").innerText = batteryRem !== undefined ? `${batteryRem}%` : "-";

    renderVisNetwork(currentGraphData, alt.path);
}

// --- Render Steps Table ---
function renderStepsTable(steps) {
    const tbody = document.getElementById("tbody-steps");
    tbody.innerHTML = "";

    if (!steps || steps.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No trace logs recorded.</td></tr>`;
        return;
    }

    steps.forEach(s => {
        const row = document.createElement("tr");
        const isUpdate = s.action.includes("Updated");
        const badgeClass = isUpdate ? "badge-update" : "badge-skip";

        row.innerHTML = `
            <td>${s.step}</td>
            <td><strong>${s.current_node}</strong></td>
            <td>${s.neighbor}</td>
            <td>${s.edge_weight !== '-' ? s.edge_weight + ' km' : '-'}</td>
            <td>${s.old_dist}</td>
            <td><strong>${s.new_dist}</strong></td>
            <td><span class="${badgeClass}">${s.action}</span></td>
        `;
        tbody.appendChild(row);
    });
}

// --- Render Edges Table ---
function renderEdgesTable(edges) {
    const tbody = document.getElementById("tbody-edges");
    tbody.innerHTML = "";

    edges.forEach(e => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${e.from}</td>
            <td>${e.to}</td>
            <td>${e.weight.toFixed(1)} km</td>
        `;
        tbody.appendChild(row);
    });
}

// --- Reset Defaults ---
async function resetDefaults() {
    try {
        await fetch("/api/reset", { method: "POST" });
        await fetchGraph();
        optimizeRoute();
    } catch (err) {
        console.error("Reset error:", err);
    }
}

// --- Graph Editor Handlers ---
async function handleAddNode() {
    const name = document.getElementById("edit-node-name").value.trim();
    if (!name) return alert("Please enter a node name.");

    const res = await fetch("/api/node", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });
    const data = await res.json();
    if (data.error) alert(data.error);
    else {
        document.getElementById("edit-node-name").value = "";
        await fetchGraph();
        optimizeRoute();
    }
}

async function handleRemoveNode() {
    const name = document.getElementById("edit-node-name").value.trim();
    if (!name) return alert("Please enter a node name to remove.");

    const res = await fetch("/api/node", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });
    const data = await res.json();
    if (data.error) alert(data.error);
    else {
        document.getElementById("edit-node-name").value = "";
        await fetchGraph();
        optimizeRoute();
    }
}

async function handleAddEdge() {
    const u = document.getElementById("edit-edge-u").value;
    const v = document.getElementById("edit-edge-v").value;
    const weight = parseFloat(document.getElementById("edit-edge-w").value);

    const res = await fetch("/api/edge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ u, v, weight })
    });
    const data = await res.json();
    if (data.error) alert(data.error);
    else {
        await fetchGraph();
        optimizeRoute();
    }
}

async function handleRemoveEdge() {
    const u = document.getElementById("edit-edge-u").value;
    const v = document.getElementById("edit-edge-v").value;

    const res = await fetch("/api/edge", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ u, v })
    });
    const data = await res.json();
    if (data.error) alert(data.error);
    else {
        await fetchGraph();
        optimizeRoute();
    }
}

// --- Benchmark Runner ---
async function runBenchmark() {
    const tbody = document.getElementById("tbody-bench");
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--accent);">Running empirical tests... Please wait.</td></tr>`;

    try {
        const response = await fetch("/api/benchmark");
        const data = await response.json();
        const results = data.results;

        tbody.innerHTML = "";
        const nodesList = [];
        const timesList = [];

        results.forEach(r => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>${r.nodes}</strong></td>
                <td>${r.edges}</td>
                <td><strong style="color: var(--accent);">${r.exec_time_ms.toFixed(3)} ms</strong></td>
                <td>${r.distance} km</td>
            `;
            tbody.appendChild(row);
            nodesList.push(r.nodes);
            timesList.push(r.exec_time_ms);
        });

        renderBenchmarkChart(nodesList, timesList);
    } catch (err) {
        console.error("Benchmark error:", err);
    }
}

// --- Render Chart.js Performance Benchmark Curve ---
function renderBenchmarkChart(labels, dataPoints) {
    const ctx = document.getElementById("chart-benchmark")?.getContext("2d");
    if (!ctx) return;

    if (benchmarkChart) benchmarkChart.destroy();

    benchmarkChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels.map(n => `${n} Nodes`),
            datasets: [{
                label: "Measured Execution Time (ms)",
                data: dataPoints,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.1)",
                fill: true,
                tension: 0.3,
                pointRadius: 6,
                pointBackgroundColor: "#2563eb"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: "Execution Scaling O((V+E) log V)", font: { size: 14, weight: "bold" } }
            },
            scales: {
                x: { title: { display: true, text: "Graph Size (Number of Vertices V)" } },
                y: { title: { display: true, text: "Execution Time (ms)" }, beginAtZero: true }
            }
        }
    });
}
