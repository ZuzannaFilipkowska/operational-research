import tkinter as tk
from tkinter import filedialog, messagebox
from amplpy import AMPL


def run_basic_model():
    try:
        ampl = AMPL()

        ampl.read("basic_model.mod")

        data_path = data_file_var.get()
        if not data_path:
            messagebox.showerror("Error", "Wybierz plik z danymi.")
            return

        ampl.read_data(data_path)

        ampl.setOption("solver", "gurobi")

        ampl.solve()

        obj_value = ampl.get_objective('TotalProfit').value()  
        results_text.delete(1.0, tk.END)  
        results_text.insert(tk.END, f"Basic Model Objective Value: {obj_value}\n")

        var = ampl.get_variable('x') 
        for index, value in var.get_values().to_dict().items():
            results_text.insert(tk.END, f"Variable {index}: {value}\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running the Basic Model:\n{str(e)}")


def run_detailed_model():
    try:
        ampl = AMPL()

        ampl.read("detailed_model.mod")

        data_path = data_file_var.get()
        if not data_path:
            messagebox.showerror("Error", "Wybierz plik z danymi.")
            return

        ampl.read_data(data_path)

        ampl.setOption("solver", "gurobi")

        ampl.solve()

        obj_value = ampl.get_objective('ObjectiveFunction').value() 
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, f"Detailed Model Objective Value: {obj_value}\n")

        var = ampl.get_variable('x')  
        for index, value in var.get_values().to_dict().items():
            results_text.insert(tk.END, f"Variable {index}: {value}\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running the Detailed Model:\n{str(e)}")


def select_data_file():
    file_path = filedialog.askopenfilename(filetypes=[("AMPL Data Files", "*.dat")])
    data_file_var.set(file_path)


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
results_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# Start the Tkinter event loop
root.mainloop()
