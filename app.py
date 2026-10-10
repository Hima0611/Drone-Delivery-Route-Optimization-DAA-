"""
app.py
------
Main Application GUI for the Drone Delivery Route Optimizer DAA Mini-Project.
Built with Python Tkinter, NetworkX, and Matplotlib.
Integrates manual Dijkstra shortest path execution, battery feasibility model,
step-by-step algorithm trace, dynamic graph editing, complexity analysis, and performance benchmarking.
"""

import sys

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    HAS_TK = True
except (ImportError, ModuleNotFoundError):
    HAS_TK = False

import matplotlib.pyplot as plt

from graph_data import DeliveryGraph
from dijkstra import dijkstra_shortest_path, find_alternative_paths
from visualization import draw_graph
from performance import run_performance_benchmark
from web_app import app  # Fallback export so 'gunicorn app:app' works seamlessly on Render


class DroneDeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Delivery Route Optimizer")
        self.root.geometry("1280x820")
        self.root.minsize(1024, 720)

        # Initialize Graph Data
        self.graph = DeliveryGraph()
        self.last_shortest_path = []
        self.last_dijkstra_result = None

        # Apply Modern Styling
        self.setup_styles()

        # Build UI Components
        self.build_header()
        self.build_tabs()

        # Initial Render
        self.on_find_route()

    def setup_styles(self):
        """Configures clean ttk styles and custom color palette."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color Palette
        self.PRIMARY = "#1E293B"      # Dark Slate
        self.ACCENT = "#2563EB"       # Royal Blue
        self.BG_LIGHT = "#F8FAFC"     # Very Light Gray
        self.CARD_BG = "#FFFFFF"      # White Card
        self.SUCCESS_GREEN = "#16A34A"
        self.DANGER_RED = "#DC2626"

        self.root.configure(bg=self.BG_LIGHT)

        # Configure TTK Styles
        self.style.configure(".", background=self.BG_LIGHT, font=("Segoe UI", 10))
        self.style.configure("TNotebook", background=self.BG_LIGHT, borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#E2E8F0", foreground="#334155", padding=[14, 8], font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", self.PRIMARY)], foreground=[("selected", "#FFFFFF")])

        self.style.configure("Card.TFrame", background=self.CARD_BG, relief="flat", borderwidth=1)
        self.style.configure("Header.TFrame", background=self.PRIMARY)
        
        self.style.configure("Primary.TButton", background=self.ACCENT, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=[12, 6])
        self.style.map("Primary.TButton", background=[("active", "#1D4ED8")])

        self.style.configure("Secondary.TButton", background="#64748B", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), padding=[10, 6])
        self.style.map("Secondary.TButton", background=[("active", "#475569")])

        self.style.configure("Header.TLabel", background=self.PRIMARY, foreground="#FFFFFF", font=("Segoe UI", 18, "bold"))
        self.style.configure("SubHeader.TLabel", background=self.PRIMARY, foreground="#94A3B8", font=("Segoe UI", 11))

        self.style.configure("CardTitle.TLabel", background=self.CARD_BG, foreground="#0F172A", font=("Segoe UI", 13, "bold"))
        self.style.configure("FieldLabel.TLabel", background=self.CARD_BG, foreground="#475569", font=("Segoe UI", 10, "bold"))

    def build_header(self):
        """Builds the main top header banner."""
        header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=[20, 14])
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_lbl = ttk.Label(header_frame, text="DRONE DELIVERY ROUTE OPTIMIZER", style="Header.TLabel")
        title_lbl.pack(anchor=tk.W)

        subtitle_lbl = ttk.Label(
            header_frame,
            text="Autonomous Flight Path & Energy Optimization • Dijkstra's Shortest Path",
            style="SubHeader.TLabel"
        )
        subtitle_lbl.pack(anchor=tk.W, pady=(2, 0))

    def build_tabs(self):
        """Builds the tabbed interface notebook."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Tab 1: Route Optimizer & Graph Visualization
        self.tab_optimizer = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_optimizer, text=" 🚁 Route Optimizer & Graph ")

        # Tab 2: Algorithm Visualization (Step Trace)
        self.tab_steps = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_steps, text=" 📊 Dijkstra Steps Trace ")

        # Tab 3: Graph Editor & Management
        self.tab_editor = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_editor, text=" 🛠 Manage Graph & Distances ")

        # Tab 4: DAA Complexity & Theory
        self.tab_theory = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_theory, text=" 📚 Complexity & DAA Theory ")

        # Tab 5: Performance Benchmark
        self.tab_performance = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_performance, text=" ⏱ Performance Analysis ")

        # Populate individual tab contents
        self.setup_tab_optimizer()
        self.setup_tab_steps()
        self.setup_tab_editor()
        self.setup_tab_theory()
        self.setup_tab_performance()

    # ==========================================
    # TAB 1: ROUTE OPTIMIZER & GRAPH VISUALIZATION
    # ==========================================
    def setup_tab_optimizer(self):
        """Sets up the main dashboard with controls, result cards, and matplotlib canvas."""
        main_container = ttk.Frame(self.tab_optimizer)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left Column: Inputs & Results
        left_col = ttk.Frame(main_container, width=420)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right Column: Matplotlib Graph Canvas
        right_col = ttk.Frame(main_container)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Card 1: Flight Controls ---
        ctrl_card = ttk.Frame(left_col, style="Card.TFrame", padding=15)
        ctrl_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ctrl_card, text="Route & Drone Parameters", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))

        # Source Dropdown
        ttk.Label(ctrl_card, text="Source Location:", style="FieldLabel.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.combo_source = ttk.Combobox(ctrl_card, state="readonly", font=("Segoe UI", 10))
        self.combo_source.pack(fill=tk.X, pady=(0, 8))

        # Destination Dropdown
        ttk.Label(ctrl_card, text="Destination Location:", style="FieldLabel.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.combo_dest = ttk.Combobox(ctrl_card, state="readonly", font=("Segoe UI", 10))
        self.combo_dest.pack(fill=tk.X, pady=(0, 8))

        # Battery & Speed Parameters in sub-grid
        param_grid = ttk.Frame(ctrl_card, style="Card.TFrame")
        param_grid.pack(fill=tk.X, pady=5)

        ttk.Label(param_grid, text="Battery Cap (%):", style="FieldLabel.TLabel").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.entry_battery = ttk.Entry(param_grid, width=8, font=("Segoe UI", 10))
        self.entry_battery.insert(0, "100")
        self.entry_battery.grid(row=0, column=1, padx=(5, 15), pady=4)

        ttk.Label(param_grid, text="Burn Rate (%/km):", style="FieldLabel.TLabel").grid(row=0, column=2, sticky=tk.W, pady=4)
        self.entry_burn = ttk.Entry(param_grid, width=8, font=("Segoe UI", 10))
        self.entry_burn.insert(0, "5.0")
        self.entry_burn.grid(row=0, column=3, pady=4)

        ttk.Label(param_grid, text="Speed (km/h):", style="FieldLabel.TLabel").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.entry_speed = ttk.Entry(param_grid, width=8, font=("Segoe UI", 10))
        self.entry_speed.insert(0, "30")
        self.entry_speed.grid(row=1, column=1, padx=(5, 15), pady=4)

        # Action Buttons
        btn_box = ttk.Frame(ctrl_card, style="Card.TFrame")
        btn_box.pack(fill=tk.X, pady=(12, 0))

        btn_find = ttk.Button(btn_box, text="⚡ Find Optimal Route", style="Primary.TButton", command=self.on_find_route)
        btn_find.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_reset = ttk.Button(btn_box, text="🔄 Reset", style="Secondary.TButton", command=self.on_reset_defaults)
        btn_reset.pack(side=tk.RIGHT, padx=(5, 0))

        # --- Card 2: Route Result Display ---
        res_card = ttk.Frame(left_col, style="Card.TFrame", padding=15)
        res_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(res_card, text="Optimal Route Results", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 10))

        # Status Badge Frame
        self.status_badge = tk.Label(
            res_card, text="Status: Ready", bg="#E2E8F0", fg="#334155",
            font=("Segoe UI", 11, "bold"), padding=8, anchor="center"
        )
        self.status_badge.pack(fill=tk.X, pady=(0, 10))

        # Results Text Output
        self.lbl_path = ttk.Label(res_card, text="Path: -", font=("Segoe UI", 11, "bold"), foreground=self.ACCENT, wraplength=380)
        self.lbl_path.pack(anchor=tk.W, pady=3)

        self.lbl_dist = ttk.Label(res_card, text="Total Distance: -", font=("Segoe UI", 10))
        self.lbl_dist.pack(anchor=tk.W, pady=2)

        self.lbl_time = ttk.Label(res_card, text="Estimated Flight Time: -", font=("Segoe UI", 10))
        self.lbl_time.pack(anchor=tk.W, pady=2)

        self.lbl_battery_used = ttk.Label(res_card, text="Battery Required: -", font=("Segoe UI", 10))
        self.lbl_battery_used.pack(anchor=tk.W, pady=2)

        self.lbl_battery_rem = ttk.Label(res_card, text="Remaining Battery: -", font=("Segoe UI", 10))
        self.lbl_battery_rem.pack(anchor=tk.W, pady=2)

        # Disclaimer
        disclaimer = ttk.Label(
            res_card,
            text="* Note: Educational simulation model (linear energy consumption).",
            font=("Segoe UI", 8, "italic"), foreground="#64748B"
        )
        disclaimer.pack(anchor=tk.W, pady=(8, 10))

        # Route Comparison / Alternatives Section
        ttk.Label(res_card, text="Route Alternatives Comparison", font=("Segoe UI", 10, "bold"), foreground="#1E293B").pack(anchor=tk.W, pady=(6, 4))
        
        self.alt_routes_text = tk.Text(res_card, height=4, font=("Consolas", 9), bg="#F1F5F9", relief="flat", wrap="none")
        self.alt_routes_text.pack(fill=tk.BOTH, expand=True)

        # --- Right Panel: Matplotlib Graph Canvas ---
        canvas_card = ttk.Frame(right_col, style="Card.TFrame", padding=10)
        canvas_card.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, canvas_card)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.refresh_comboboxes()

    def refresh_comboboxes(self):
        """Refreshes dropdown lists when graph nodes change."""
        nodes = self.graph.get_nodes()
        self.combo_source['values'] = nodes
        self.combo_dest['values'] = nodes

        if nodes:
            if "Warehouse" in nodes:
                self.combo_source.set("Warehouse")
            else:
                self.combo_source.set(nodes[0])

            if "Customer D" in nodes:
                self.combo_dest.set("Customer D")
            elif len(nodes) > 1:
                self.combo_dest.set(nodes[-1])
            else:
                self.combo_dest.set(nodes[0])

    def on_find_route(self):
        """Executes manual Dijkstra's algorithm and updates the UI results."""
        src = self.combo_source.get()
        dst = self.combo_dest.get()

        if not src or not dst:
            messagebox.showwarning("Input Error", "Please select valid Source and Destination locations.")
            return

        # Validate inputs
        try:
            battery_cap = float(self.entry_battery.get().strip())
            burn_rate = float(self.entry_burn.get().strip())
            speed = float(self.entry_speed.get().strip())

            if battery_cap <= 0 or burn_rate <= 0 or speed <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Battery capacity, burn rate, and speed must be positive numbers.")
            return

        # Execute Manual Dijkstra
        res = dijkstra_shortest_path(self.graph, src, dst)
        self.last_dijkstra_result = res
        path = res['path']
        dist = res['distance']

        self.last_shortest_path = path

        if not path or dist == float('inf'):
            self.status_badge.config(text="⚠ No Path Found", bg="#EF4444", fg="#FFFFFF")
            self.lbl_path.config(text="Path: Unreachable")
            self.lbl_dist.config(text="Total Distance: Infinite")
            self.lbl_time.config(text="Estimated Flight Time: -")
            self.lbl_battery_used.config(text="Battery Required: -")
            self.lbl_battery_rem.config(text="Remaining Battery: -")
            self.alt_routes_text.delete("1.0", tk.END)
            self.alt_routes_text.insert(tk.END, "No valid flight route exists between these locations.")
        else:
            # Battery & Flight Time Calculations
            flight_time_mins = (dist / speed) * 60.0
            battery_required = dist * burn_rate
            remaining_battery = battery_cap - battery_required
            is_feasible = (battery_cap >= battery_required)

            path_str = " → ".join(path)
            self.lbl_path.config(text=f"Path: {path_str}")
            self.lbl_dist.config(text=f"Total Distance: {dist:.1f} km")
            self.lbl_time.config(text=f"Estimated Flight Time: {flight_time_mins:.1f} minutes")
            self.lbl_battery_used.config(text=f"Battery Required: {battery_required:.1f}% ({dist:.1f} km × {burn_rate:.1f}%/km)")
            self.lbl_battery_rem.config(text=f"Remaining Battery: {remaining_battery:.1f}%")

            if is_feasible:
                self.status_badge.config(
                    text="✓ Route Feasible (Sufficient Battery)",
                    bg=self.SUCCESS_GREEN, fg="#FFFFFF"
                )
            else:
                self.status_badge.config(
                    text=f"⚠ Route Not Feasible! Required: {battery_required:.1f}%, Available: {battery_cap:.1f}%",
                    bg=self.DANGER_RED, fg="#FFFFFF"
                )

            # Populate Alternative Routes
            alternatives = find_alternative_paths(self.graph, src, dst, max_paths=3)
            self.alt_routes_text.delete("1.0", tk.END)
            for idx, alt in enumerate(alternatives, start=1):
                alt_dist = alt['distance']
                alt_path_str = " → ".join(alt['path'])
                alt_bat = alt_dist * burn_rate
                tag = " (Dijkstra Optimal)" if idx == 1 else ""
                self.alt_routes_text.insert(
                    tk.END,
                    f"Route {idx}{tag}:\n  {alt_path_str}\n  Distance: {alt_dist:.1f} km | Battery: {alt_bat:.1f}%\n\n"
                )

        # Update Graph Canvas
        draw_graph(self.graph, shortest_path=path, source=src, destination=dst, figure=self.fig, ax=self.ax)
        self.canvas.draw()

        # Update Step Trace Table in Tab 2
        self.update_step_trace_table()

    def on_reset_defaults(self):
        """Resets graph to default network setup and clears selections."""
        self.graph.load_default_graph()
        self.refresh_comboboxes()
        self.entry_battery.delete(0, tk.END)
        self.entry_battery.insert(0, "100")
        self.entry_burn.delete(0, tk.END)
        self.entry_burn.insert(0, "5.0")
        self.entry_speed.delete(0, tk.END)
        self.entry_speed.insert(0, "30")
        self.on_find_route()
        self.refresh_editor_tables()
        messagebox.showinfo("Reset Complete", "Default graph network and parameters restored.")

    # ==========================================
    # TAB 2: DIJKSTRA STEP-BY-STEP TRACE
    # ==========================================
    def setup_tab_steps(self):
        """Sets up the algorithm step trace visualizer table."""
        container = ttk.Frame(self.tab_steps, style="Card.TFrame", padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Dijkstra Algorithm Execution Steps (Step-by-Step Trace)", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        info_lbl = ttk.Label(
            container,
            text="This table demonstrates the step-by-step internal execution of manual Dijkstra's algorithm using a Priority Queue (Min-Heap).",
            font=("Segoe UI", 9), foreground="#475569"
        )
        info_lbl.pack(anchor=tk.W, pady=(0, 10))

        # Scrollable Treeview Table
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("step", "curr_node", "neighbor", "weight", "old_dist", "new_dist", "action")
        self.tree_steps = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        self.tree_steps.heading("step", text="Step #")
        self.tree_steps.heading("curr_node", text="Current Node (u)")
        self.tree_steps.heading("neighbor", text="Neighbor Node (v)")
        self.tree_steps.heading("weight", text="Edge Weight (w)")
        self.tree_steps.heading("old_dist", text="Prev Dist d[v]")
        self.tree_steps.heading("new_dist", text="New Dist d[v]")
        self.tree_steps.heading("action", text="Algorithm Action / Decision")

        self.tree_steps.column("step", width=60, anchor="center")
        self.tree_steps.column("curr_node", width=120, anchor="center")
        self.tree_steps.column("neighbor", width=120, anchor="center")
        self.tree_steps.column("weight", width=100, anchor="center")
        self.tree_steps.column("old_dist", width=100, anchor="center")
        self.tree_steps.column("new_dist", width=100, anchor="center")
        self.tree_steps.column("action", width=380, anchor="w")

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_steps.yview)
        self.tree_steps.configure(yscroll=scroll_y.set)

        self.tree_steps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def update_step_trace_table(self):
        """Populates the step trace table with the last Dijkstra execution logs."""
        for item in self.tree_steps.get_children():
            self.tree_steps.delete(item)

        if not self.last_dijkstra_result or 'steps' not in self.last_dijkstra_result:
            return

        steps = self.last_dijkstra_result['steps']
        for s in steps:
            self.tree_steps.insert("", tk.END, values=(
                s['step'],
                s['current_node'],
                s['neighbor'],
                f"{s['edge_weight']} km" if isinstance(s['edge_weight'], (int, float)) else s['edge_weight'],
                s['old_dist'],
                s['new_dist'],
                s['action']
            ))

    # ==========================================
    # TAB 3: GRAPH EDITOR & MANAGEMENT
    # ==========================================
    def setup_tab_editor(self):
        """Sets up controls for adding/removing nodes and edges interactively."""
        main_frame = ttk.Frame(self.tab_editor)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main_frame, width=380)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_panel = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Node Management Card ---
        node_card = ttk.Frame(left_panel, style="Card.TFrame", padding=15)
        node_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(node_card, text="Manage Nodes", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(node_card, text="Node Name:", style="FieldLabel.TLabel").pack(anchor=tk.W)
        self.entry_node_name = ttk.Entry(node_card, font=("Segoe UI", 10))
        self.entry_node_name.pack(fill=tk.X, pady=(2, 6))

        btn_node_box = ttk.Frame(node_card, style="Card.TFrame")
        btn_node_box.pack(fill=tk.X)

        ttk.Button(btn_node_box, text="➕ Add Node", style="Primary.TButton", command=self.on_add_node).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(btn_node_box, text="❌ Remove Node", style="Secondary.TButton", command=self.on_remove_node).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))

        # --- Edge Management Card ---
        edge_card = ttk.Frame(left_panel, style="Card.TFrame", padding=15)
        edge_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(edge_card, text="Manage Edges & Distances", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(edge_card, text="Node 1:", style="FieldLabel.TLabel").pack(anchor=tk.W)
        self.combo_edge_u = ttk.Combobox(edge_card, state="readonly", font=("Segoe UI", 10))
        self.combo_edge_u.pack(fill=tk.X, pady=(2, 6))

        ttk.Label(edge_card, text="Node 2:", style="FieldLabel.TLabel").pack(anchor=tk.W)
        self.combo_edge_v = ttk.Combobox(edge_card, state="readonly", font=("Segoe UI", 10))
        self.combo_edge_v.pack(fill=tk.X, pady=(2, 6))

        ttk.Label(edge_card, text="Distance (km):", style="FieldLabel.TLabel").pack(anchor=tk.W)
        self.entry_edge_w = ttk.Entry(edge_card, font=("Segoe UI", 10))
        self.entry_edge_w.insert(0, "5.0")
        self.entry_edge_w.pack(fill=tk.X, pady=(2, 10))

        btn_edge_box = ttk.Frame(edge_card, style="Card.TFrame")
        btn_edge_box.pack(fill=tk.X)

        ttk.Button(btn_edge_box, text="🔗 Add / Update Edge", style="Primary.TButton", command=self.on_add_edge).pack(fill=tk.X, pady=(0, 4))
        ttk.Button(btn_edge_box, text="✂ Remove Edge", style="Secondary.TButton", command=self.on_remove_edge).pack(fill=tk.X)

        # --- Right Panel: Current Edges Table ---
        ttk.Label(right_panel, text="Current Flight Connections (Edges)", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        columns = ("u", "v", "weight")
        self.tree_edges = ttk.Treeview(right_panel, columns=columns, show="headings", height=15)
        self.tree_edges.heading("u", text="Location 1")
        self.tree_edges.heading("v", text="Location 2")
        self.tree_edges.heading("weight", text="Distance (km)")

        self.tree_edges.column("u", width=150, anchor="center")
        self.tree_edges.column("v", width=150, anchor="center")
        self.tree_edges.column("weight", width=120, anchor="center")

        scroll_y = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.tree_edges.yview)
        self.tree_edges.configure(yscroll=scroll_y.set)

        self.tree_edges.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_editor_tables()

    def refresh_editor_tables(self):
        """Refreshes the edge list table and editor dropdowns."""
        nodes = self.graph.get_nodes()
        self.combo_edge_u['values'] = nodes
        self.combo_edge_v['values'] = nodes
        if nodes:
            self.combo_edge_u.set(nodes[0])
            self.combo_edge_v.set(nodes[1] if len(nodes) > 1 else nodes[0])

        for item in self.tree_edges.get_children():
            self.tree_edges.delete(item)

        for u, v, w in self.graph.get_edges():
            self.tree_edges.insert("", tk.END, values=(u, v, f"{w:.1f} km"))

    def on_add_node(self):
        """Adds a new node to the graph."""
        name = self.entry_node_name.get().strip()
        success, msg = self.graph.add_node(name)
        if success:
            messagebox.showinfo("Success", msg)
            self.entry_node_name.delete(0, tk.END)
            self.refresh_comboboxes()
            self.refresh_editor_tables()
            self.on_find_route()
        else:
            messagebox.showerror("Error", msg)

    def on_remove_node(self):
        """Removes a node from the graph."""
        name = self.entry_node_name.get().strip()
        success, msg = self.graph.remove_node(name)
        if success:
            messagebox.showinfo("Success", msg)
            self.entry_node_name.delete(0, tk.END)
            self.refresh_comboboxes()
            self.refresh_editor_tables()
            self.on_find_route()
        else:
            messagebox.showerror("Error", msg)

    def on_add_edge(self):
        """Adds or updates an edge between two nodes."""
        u = self.combo_edge_u.get()
        v = self.combo_edge_v.get()
        try:
            w = float(self.entry_edge_w.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric edge weight.")
            return

        success, msg = self.graph.add_edge(u, v, w)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_editor_tables()
            self.on_find_route()
        else:
            messagebox.showerror("Error", msg)

    def on_remove_edge(self):
        """Removes an edge between two nodes."""
        u = self.combo_edge_u.get()
        v = self.combo_edge_v.get()
        success, msg = self.graph.remove_edge(u, v)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_editor_tables()
            self.on_find_route()
        else:
            messagebox.showerror("Error", msg)

    # ==========================================
    # TAB 4: COMPLEXITY & DAA THEORY
    # ==========================================
    def setup_tab_theory(self):
        """Populates educational DAA theoretical analysis and complexity breakdowns."""
        container = ttk.Frame(self.tab_theory, style="Card.TFrame", padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(container, font=("Segoe UI", 10), wrap="word", bg="#FFFFFF", relief="flat")
        scroll_y = ttk.Scrollbar(container, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscroll=scroll_y.set)

        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        theory_content = """
========================================================================================
            DESIGN AND ANALYSIS OF ALGORITHMS (DAA) MINI-PROJECT ANALYSIS
========================================================================================

PROJECT TITLE:
   "Design and Analysis of an Optimized Drone Delivery Route Using Graph Algorithms"

1. PROBLEM FORMULATION & GRAPH MODELING
----------------------------------------------------------------------------------------
   • Vertices (V): Represent physical physical locations in the drone delivery network.
       - Warehouse: Dispatch hub where drone flight originates.
       - Customer Locations (A, B, C, D, E, F): Drop-off delivery targets.
       - Charging Station: Intermediate recharge waypoint for long flights.
   
   • Edges (E): Represent navigable flight corridors between two locations.
   
   • Edge Weights w(u, v): Non-negative scalar representing the Euclidean flight distance 
     in kilometers (km) between location u and location v.

2. DIJKSTRA'S SHORTEST PATH ALGORITHM (GREEDY PARADIGM)
----------------------------------------------------------------------------------------
   Dijkstra's algorithm computes single-source shortest paths on non-negatively weighted graphs.
   It employs a Greedy Choice Strategy: at each iteration, it selects the unvisited node 
   with the smallest tentative distance from the source.

   Edge Relaxation Condition:
       For any edge (u, v) with weight w(u, v):
       if d[u] + w(u, v) < d[v]:
           d[v] = d[u] + w(u, v]
           pi[v] = u

3. ALGORITHM TIME & SPACE COMPLEXITY ANALYSIS
----------------------------------------------------------------------------------------
   • TIME COMPLEXITY:  O((V + E) log V)
       - Min-Heap / Priority Queue Operations:
           * Extract-Min is called V times -> O(V log V)
           * Decrease-Key / Push is called E times -> O(E log V)
       - Total Time Complexity = O((V + E) log V).
       - For connected sparse graphs where E >= V, this simplifies to O(E log V).

   • SPACE COMPLEXITY:  O(V + E)
       - Adjacency List representation: O(V + E) storage.
       - Min-Heap Priority Queue: Stores at most O(V) elements.
       - Distance Array & Predecessor Map: O(V) memory space.

4. BATTERY FEASIBILITY & PHYSICAL DRONE CONSTRAINTS
----------------------------------------------------------------------------------------
   • Battery Consumption Model: Linear energy discharge rate (B_rate in %/km).
   • Required Battery B_req = Distance × B_rate
   • Feasibility Criterion: B_available >= B_req
   * Note: This mini-project uses a simplified energy model suitable for academic demonstration.
========================================================================================
"""
        txt.insert(tk.END, theory_content)
        txt.config(state="disabled")

    # ==========================================
    # TAB 5: EMPIRICAL PERFORMANCE BENCHMARK
    # ==========================================
    def setup_tab_performance(self):
        """Sets up the empirical benchmark tab with execution timing tables and benchmark plot."""
        main_container = ttk.Frame(self.tab_performance)
        main_container.pack(fill=tk.BOTH, expand=True)

        left_col = ttk.Frame(main_container, width=420)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right_col = ttk.Frame(main_container, style="Card.TFrame", padding=10)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Control Card
        ctrl_card = ttk.Frame(left_col, style="Card.TFrame", padding=15)
        ctrl_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(ctrl_card, text="Performance Testing", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(
            ctrl_card,
            text="Tests empirical execution times across graphs of 10, 25, 50, 100, and 200 nodes.",
            font=("Segoe UI", 9), foreground="#475569", wraplength=380
        ).pack(anchor=tk.W, pady=(0, 10))

        btn_run_bench = ttk.Button(ctrl_card, text="⚡ Run Performance Benchmark", style="Primary.TButton", command=self.on_run_benchmark)
        btn_run_bench.pack(fill=tk.X)

        # Benchmark Table Card
        tbl_card = ttk.Frame(left_col, style="Card.TFrame", padding=15)
        tbl_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(tbl_card, text="Measured Execution Times", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        columns = ("nodes", "edges", "time", "dist")
        self.tree_bench = ttk.Treeview(tbl_card, columns=columns, show="headings", height=10)
        self.tree_bench.heading("nodes", text="Nodes (V)")
        self.tree_bench.heading("edges", text="Edges (E)")
        self.tree_bench.heading("time", text="Time (ms)")
        self.tree_bench.heading("dist", text="Distance (km)")

        self.tree_bench.column("nodes", width=80, anchor="center")
        self.tree_bench.column("edges", width=80, anchor="center")
        self.tree_bench.column("time", width=100, anchor="center")
        self.tree_bench.column("dist", width=100, anchor="center")

        self.tree_bench.pack(fill=tk.BOTH, expand=True)

        # Right Canvas: Benchmark Plot
        ttk.Label(right_col, text="Execution Time Scaling O((V+E) log V)", style="CardTitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        self.fig_bench, self.ax_bench = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas_bench = FigureCanvasTkAgg(self.fig_bench, master=right_col)
        self.canvas_bench.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial message on plot
        self.ax_bench.text(0.5, 0.5, "Click 'Run Performance Benchmark' to start empirical timing", horizontalalignment='center', verticalalignment='center')
        self.ax_bench.axis('off')

    def on_run_benchmark(self):
        """Runs performance benchmark and updates table & matplotlib plot."""
        for item in self.tree_bench.get_children():
            self.tree_bench.delete(item)

        results = run_performance_benchmark(node_sizes=[10, 25, 50, 100, 200], iterations=5)

        nodes_list = []
        times_list = []

        for r in results:
            self.tree_bench.insert("", tk.END, values=(r['nodes'], r['edges'], f"{r['exec_time_ms']:.3f}", f"{r['distance']:.1f}"))
            nodes_list.append(r['nodes'])
            times_list.append(r['exec_time_ms'])

        # Update Plot
        self.ax_bench.clear()
        self.ax_bench.plot(nodes_list, times_list, marker='o', color='#2563EB', linewidth=2.5, markersize=8, label='Measured Time (ms)')
        self.ax_bench.set_title("Dijkstra Execution Time vs. Node Count (V)", fontsize=11, fontweight='bold')
        self.ax_bench.set_xlabel("Number of Nodes (V)", fontsize=10)
        self.ax_bench.set_ylabel("Execution Time (ms)", fontsize=10)
        self.ax_bench.grid(True, linestyle='--', alpha=0.6)
        self.ax_bench.legend(loc='upper left')
        self.fig_bench.tight_layout()
        self.canvas_bench.draw()


def main():
    if HAS_TK:
        root = tk.Tk()
        app = DroneDeliveryApp(root)
        root.mainloop()
    else:
        print("Tkinter GUI is not available in headless environment. Use web_app.py for web deployment.")

if __name__ == "__main__":
    main()

