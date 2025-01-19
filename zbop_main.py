import tkinter as tk
from tkinter import filedialog, messagebox
from amplpy import AMPL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import ttk


def run_basic_model():
    try:
        ampl = AMPL()

        ampl.read("basic_model.mod")

        data_path = data_file_var.get()
        if not data_path:
            messagebox.showerror("Błąd", "Wybierz plik z danymi.")
            return

        ampl.read_data(data_path)
        ampl.setOption("solver", "gurobi")

        ampl.solve()

        for widget in right_frame.winfo_children():
          widget.destroy()

        results_text.delete(1.0, tk.END)

        results_text.insert(tk.END, "===== Wyniki: =====\n\n")

        results_text.insert(tk.END, "Wybrane Projekty:\n")
        var_x = ampl.get_variable('x')
        selected_projects = [
            index for index, value in var_x.get_values().to_dict().items() if value > 0.5
        ]
        profit_values = []
        cost_values = []
        
        for project in selected_projects:
            results_text.insert(tk.END, f" - Projekt: {project}\n")
            profit_values.append(ampl.get_parameter('S')[project])

            cost = 0
            var_y = ampl.get_variable('y')
            var_y_dict = var_y.get_values().to_dict()
            for (i, p, j), value in var_y_dict.items():
                if j == project and value > 0.5:
                    cost += ampl.get_parameter('K_i')[i]
            cost_values.append(cost)

        employee_assignment_data = gather_employee_project_assignments(ampl, selected_projects)

        if not selected_projects:
            results_text.insert(tk.END, "  Nie wybrano żadnych projektów.\n")

        results_text.insert(tk.END, "\n")

        results_text.insert(tk.END, "Przypisanie Pracowników:\n")
        var_y = ampl.get_variable('y')
        assignments = [
            (i, p, j) for (i, p, j), value in var_y.get_values().to_dict().items() if value > 0.5
        ]
        for i, p, j in assignments:
            results_text.insert(tk.END, f" - Pracownik: {i} przypisany do Stanowiska: {p} w Projekcie: {j}\n")

        if not assignments:
            results_text.insert(tk.END, "  Nie przypisano żadnych pracowników do projektów.\n")

        results_text.insert(tk.END, "\nPodsumowanie:\n")
        results_text.insert(
            tk.END,
            "Na podstawie wyników modelu, wybrano projekty i przypisania pracowników, które zostały wyświetlone powyżej.\n"
        )

        total_profit = ampl.get_objective('TotalProfit').value()
        total_cost = 0

        var_y_dict = var_y.get_values().to_dict()
        for (i, p, j), value in var_y_dict.items():
            if value > 0.5:
                cost = ampl.get_parameter('K_i')[i]
                total_cost += cost

        display_stacked_project_profit_chart(selected_projects, profit_values, cost_values)
        display_employee_project_graph(employee_assignment_data)

        results_text.insert(tk.END, f"Całkowity zysk: {total_profit}")
        results_text.insert(tk.END, f"Całkowity koszt: {total_cost}")

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas uruchamiania Modelu Podstawowego:\n{str(e)}")

def compute_resource_stats(D, resource_usage, Cmax):
    resource_stats = []

    # Przechodzimy przez zasoby
    for r in D.keys():
        usage_values = [resource_usage[(r, t)] for t in range(1, int(Cmax) + 1)]  # Użycie zasobów w każdym czasie
        total_usage = sum(usage_values)  # Całkowite wykorzystanie
        max_usage = max(usage_values)   # Maksymalne wykorzystanie
        avg_usage = total_usage / len(usage_values)  # Średnie wykorzystanie

        # Dodajemy statystyki dla zasobu
        resource_stats.append((r, avg_usage, max_usage))

    return resource_stats

def display_stacked_project_profit_chart(selected_projects, profit_values, cost_values):
    """Display a stacked bar chart for Project Selection vs Profit (with Cost)."""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Create stacked bars: first plot the cost and then add the profit on top
    ax.bar(selected_projects, profit_values, color='#4C9F70', label='Przychód')
    ax.bar(selected_projects, cost_values, bottom=profit_values, color='#E45756', label='Koszt')

    ax.set_xlabel('Projekt')
    ax.set_ylabel('Wartość')
    ax.set_title('Przychód i koszt wybranych projektów')
    
    ax.legend()

    # Adding value labels on top of the profit part
    for i, (cost, profit) in enumerate(zip(cost_values, profit_values)):
        ax.text(i, cost + profit + 0.05, f'{cost:.2f}', ha='center', va='bottom', fontsize=12)
        ax.text(i, profit - 0.05, f'{profit:.2f}', ha='center', va='top', fontsize=12)

    # Embed the chart in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=3, column=0, padx=10, pady=10)
    canvas.draw()
    
def gather_employee_project_assignments(ampl, selected_projects):
    """Gather employee-to-project assignment data."""
    var_y = ampl.get_variable('y')
    employee_project_data = []

    # Loop over all assignments and collect the employee-project connections
    for (i, p, j), value in var_y.get_values().to_dict().items():
        if value > 0.5:  # If the employee is assigned to the project
            if j in selected_projects:  # Only count if project is selected
                employee_project_data.append((f"{i}", f"Projekt {j}"))

    return employee_project_data

def display_employee_project_graph(employee_project_data):
    """Display an employee-to-project assignment graph."""
    G = nx.Graph()

    G.add_edges_from(employee_project_data)

    fig, ax = plt.subplots(figsize=(10, 8))

    pos = nx.spring_layout(G, seed=42)

    node_colors = []
    for node in G.nodes:
        if node.startswith("Projekt"):
            node_colors.append("lightgreen")
        else:
            node_colors.append("lightblue")

    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold", edge_color="gray")

    ax.set_title("Przypisanie pracowników do projektów")

    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=5, column=0, padx=10, pady=10)
    canvas.draw()

def run_detailed_model():
    try:
        ampl = AMPL()

        ampl.read("detailed_model.mod")

        data_path = data_file_var.get()
        if not data_path:
            messagebox.showerror("Błąd", "Wybierz plik z danymi.")
            return

        ampl.read_data(data_path)

        ampl.setOption("solver", "gurobi")

        ampl.solve()

        results_text.delete(1.0, tk.END)

        for widget in right_frame.winfo_children():
          widget.destroy()

        # Define the highlighting style for "Wolny"
        results_text.tag_configure("highlight_free", foreground="green", font=("TkDefaultFont", 10, "bold"))

        results_text.insert(tk.END, "===== Wyniki: Model Szczegółowy =====\n\n")

        # Fetch the value of Cmax (objective function)
        Cmax = ampl.get_objective('ObjectiveFunction').value()
        results_text.insert(tk.END, f"Czas trwania projektu: {Cmax}\n\n")

        # Get x{I, T} - Task schedule
        results_text.insert(tk.END, f"Harmonogram zadań:\n")
        var_x = ampl.get_variable('x')
        tasks_schedule = [
            (i, t) for (i, t), value in var_x.get_values().to_dict().items() if value > 0.5 and t <= Cmax
        ]

        print(tasks_schedule)
        for i, t in tasks_schedule:
            results_text.insert(tk.END, f" - Zadanie: {i} jest aktywne w czasie: {t}\n")

        if not tasks_schedule:
            results_text.insert(tk.END, "  Żadne zadanie nie jest aktywne.\n")

        results_text.insert(tk.END, "\n")

        # Display resource usage and availability until Cmax
        results_text.insert(tk.END, "Dostępność zasobów w czasie (do czasu Cmax):\n")
        D = ampl.get_parameter('D').get_values().to_dict()  # Dostępne zasoby
        requirement = ampl.get_parameter('d').get_values().to_dict()  # Wymagania zadań dla zasobów

        resource_usage = {}  # Klucz: (zasób R, czas T), wartość: suma przypisania
        free_resources = {}  # Klucz: (zasób R, czas T), wartość: ilość zasobu wolna

        for r in D.keys():
            for t in range(1, int(Cmax) + 1):  # Iteracja po czasie do Cmax
                # Oblicz przypisanie zasobu r w czasie t
                usage = sum(
                    requirement[i, r]  # Wymaganie zasobu r dla zadania i
                    for (i, t_prime), value in var_x.get_values().to_dict().items()
                    if t_prime == t and value > 0.5 and (i, r) in requirement
                )
                resource_usage[(r, t)] = usage
                free_resources[(r, t)] = D[r] - usage

        # Display and highlight free resources
        for t in range(1, int(Cmax)):  # Ogranicz do czasu <= Cmax
            results_text.insert(tk.END, f"Czas {t}:\n")
            for r in D.keys():
                results_text.insert(tk.END, f" - Zasób: {r}, Przypisano: {resource_usage[(r, t)]}, ")

                # Highlight "Wolny" resources
                results_text.insert(tk.END, f"Wolny: {free_resources[(r, t)]}\n", "highlight_free" if free_resources[(r, t)] > 0 else None)

        results_text.insert(tk.END, "\nPodsumowanie:\n")
        results_text.insert(
            tk.END,
            f"Projekt zakończył się w czasie = {Cmax}.\n"
        )
        results_text.insert(tk.END, "Harmonogram zadań i dostępność zasobów wyświetlone powyżej.\n")

        create_gantt_in_tkinter(tasks_schedule,right_frame)
        
        display_statistics(compute_resource_stats(D, resource_usage, Cmax), right_frame)


    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas uruchamiania Modelu Szczegółowego:\n{str(e)}")

def select_data_file():
    file_path = filedialog.askopenfilename(filetypes=[("AMPL Data Files", "*.dat")])
    data_file_var.set(file_path)

def create_gantt_in_tkinter(task_schedule, canvas_frame):
    # Clear existing widgets in the canvas_frame
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    # Create Gantt chart
    fig, ax = plt.subplots(figsize=(8, 4))

    # Plotting tasks on the chart
    tasks_dict = {}

    for task, start_time in task_schedule:
        if task not in tasks_dict:
            tasks_dict[task] = []
        tasks_dict[task].append(start_time)

    # Draw bars for each task
    for task, times in tasks_dict.items():
        for start_time in times:
            ax.barh(f"Zadanie {task}", width=1, left=start_time, color='#4C9F70')

    ax.set_xlabel("Czas")
    ax.set_ylabel("Zadania")
    ax.set_title("Wykres Gantta")

    # Embed the plot in the Tkinter window canvas_frame
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas.draw()


def display_statistics(data, results_frame):
    """Function to display statistics in the form of a table and a stacked bar chart."""

    # Create a frame for statistics
    stats_frame = tk.Frame(results_frame)
    stats_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)  # Use pack here

    # Create a treeview for displaying statistics
    tree = ttk.Treeview(stats_frame, columns=("Zasób", "Średnie wykorzystanie", "Maksymalne wykorzystanie"), show="headings")
    tree.heading("Zasób", text="Zasób")
    tree.heading("Średnie wykorzystanie", text="Średnie wykorzystanie")
    tree.heading("Maksymalne wykorzystanie", text="Maksymalne wykorzystanie")

    # Insert data into the treeview
    for resource, avg, max_val in data:
        tree.insert("", "end", values=(resource, avg, max_val))

    tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # Pack the treeview to expand in frame

    # Create a stacked bar chart based on the data
    resources = [entry[0] for entry in data]
    avg_usage = [entry[1] for entry in data]
    max_usage = [entry[2] for entry in data]

    fig, ax = plt.subplots(figsize=(8, 5))

    # Plotting stacked bars
    ax.bar(resources, avg_usage, label="Średnie wykorzystanie", color='#4C9F70')
    ax.bar(resources, [max_val - avg for max_val, avg in zip(max_usage, avg_usage)],
           bottom=avg_usage, label="Maksymalne wykorzystanie", color='#E45756')

    ax.set_xlabel('Zasoby')
    ax.set_ylabel('Wykorzystanie')
    ax.set_title('Wykorzystanie zasobów (Wykres skumulowany)')
    ax.legend()

    # Embed the plot in the statistics frame
    canvas = FigureCanvasTkAgg(fig, master=stats_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  # Use pack to position the canvas
    canvas.draw()

# Main application setup
root = tk.Tk()
root.title("AMPL Model Runner")

# Frame for file selection
file_frame = tk.Frame(root)
file_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
tk.Label(file_frame, text="Wybierz plik z danymi (.dat):").pack(side=tk.LEFT)
data_file_var = tk.StringVar()
tk.Entry(file_frame, textvariable=data_file_var, width=50).pack(side=tk.LEFT)
tk.Button(file_frame, text="Wybierz...", command=select_data_file).pack(side=tk.LEFT)

# Frame for model running buttons
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
tk.Button(button_frame, text="Wybierz projekty", command=run_basic_model).pack(side=tk.LEFT)
tk.Button(button_frame, text="Zaplanuj projekt", command=run_detailed_model).pack(side=tk.LEFT)

# Results display frame
two_col_grid_frame = tk.Frame(root)
two_col_grid_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

# Configure the grid_frame to fill available space
root.grid_rowconfigure(2, weight=1)  # Allow the row to expand
root.grid_columnconfigure(0, weight=1)  # Allow the column to expand
root.grid_columnconfigure(1, weight=1)

canvas = tk.Canvas(two_col_grid_frame)
scrollbar = tk.Scrollbar(two_col_grid_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")

# Configure canvas
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas
scrollable_frame = tk.Frame(canvas)

# Add the scrollable frame to the canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

# Function to resize the canvas when the scrollable frame is resized
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", on_frame_configure)

# Left: Results Text Area
results_frame = tk.Frame(scrollable_frame)
results_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

tk.Label(results_frame, text="Wyniki:").pack(anchor="nw")
results_text = tk.Text(results_frame, width=40, height=20)
results_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(scrollable_frame)
right_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

# Final window adjustments
two_col_grid_frame.grid_rowconfigure(0, weight=1)
two_col_grid_frame.grid_columnconfigure(0, weight=1)
two_col_grid_frame.grid_columnconfigure(1, weight=3)

root.mainloop()