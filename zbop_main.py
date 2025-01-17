import tkinter as tk
from tkinter import filedialog, messagebox
from amplpy import AMPL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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

        results_text.delete(1.0, tk.END)

        results_text.insert(tk.END, "===== Wyniki: =====\n\n")

        results_text.insert(tk.END, "Wybrane Projekty:\n")
        var_x = ampl.get_variable('x')
        selected_projects = [
            index for index, value in var_x.get_values().to_dict().items() if value > 0.5
        ]
        for project in selected_projects:
            results_text.insert(tk.END, f" - Projekt: {project}\n")

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

        # Define the highlighting style for "Wolny"
        results_text.tag_configure("highlight_free", foreground="green", font=("TkDefaultFont", 10, "bold"))

        results_text.insert(tk.END, "===== Wyniki: Model Szczegółowy =====\n\n")

        # Fetch the value of Cmax (objective function)
        Cmax = ampl.get_objective('ObjectiveFunction').value()
        results_text.insert(tk.END, f"Czas trwania projektu: {Cmax - 1}\n\n")

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
            f"Projekt zakończył się w czasie = {Cmax - 1}.\n"
        )
        results_text.insert(tk.END, "Harmonogram zadań i dostępność zasobów wyświetlone powyżej.\n")

        create_gantt_in_tkinter(tasks_schedule)
        
        display_statistics(root, compute_resource_stats(D, resource_usage, Cmax))


    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd podczas uruchamiania Modelu Szczegółowego:\n{str(e)}")




def select_data_file():
    file_path = filedialog.askopenfilename(filetypes=[("AMPL Data Files", "*.dat")])
    data_file_var.set(file_path)


def create_gantt_in_tkinter(task_schedule):
    # Tworzenie wykresu Gantta
    fig, ax = plt.subplots(figsize=(8, 4))

    # Rysowanie zadań na wykresie
    tasks_dict = {}

    for task, start_time in task_schedule:
        if task not in tasks_dict:
            tasks_dict[task] = []
        tasks_dict[task].append(start_time)

    # Rysowanie pasków dla każdego zadania
    for task, times in tasks_dict.items():
        for start_time in times:
            ax.barh(f"Zadanie {task}", width=1, left=start_time, color="blue")

    ax.set_xlabel("Czas")
    ax.set_ylabel("Zadania")
    ax.set_title("Wykres Gantta")

    # Osadzenie wykresu w oknie Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=3, column=0, padx=10, pady=10)
    canvas.draw()



def display_statistics(root, data):
    """Funkcja do wyświetlania statystyk w postaci tabeli"""
    tree = ttk.Treeview(root, columns=("Zasób", "Średnie wykorzystanie", "Maksymalne wykorzystanie"), show="headings")
    tree.heading("Zasób", text="Zasób")
    tree.heading("Średnie wykorzystanie", text="Średnie wykorzystanie")
    tree.heading("Maksymalne wykorzystanie", text="Maksymalne wykorzystanie")

    for resource, avg, max_val in data:
        tree.insert("", "end", values=(resource, avg, max_val))

    tree.grid(row=4, column=2, padx=10, pady=10)


root = tk.Tk()
root.title("AMPL Model Runner")

tk.Label(root, text="Wybierz plik z danymi (.dat):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
data_file_var = tk.StringVar()
tk.Entry(root, textvariable=data_file_var, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Wybierz...", command=select_data_file).grid(row=0, column=2, padx=10, pady=5)

# Buttons to run the models
tk.Button(root, text="Wybierz projekty", command=run_basic_model, width=15).grid(row=1, column=0, padx=10, pady=10)
tk.Button(root, text="Zaplanuj projekt", command=run_detailed_model, width=15).grid(row=1, column=1, padx=10, pady=10)

# Results display
tk.Label(root, text="Wyniki:").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
results_text = tk.Text(root, width=80, height=20)
results_text.grid(row=3, column=2, columnspan=4, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
