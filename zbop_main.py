import tkinter as tk
from tkinter import filedialog, messagebox
from amplpy import AMPL, add_to_path


# Function to solve the basic model
def run_basic_model():
    try:
        # Initialize AMPL
        ampl = AMPL()

        # Load the basic model from the file bundled with the source code
        ampl.read("basic_model.mod")

        # Check if the user provided a data file
        data_path = data_file_var.get()
        if not data_path:
            messagebox.showerror("Error", "Please select a data file for the Basic Model.")
            return

        # Load the data file
        ampl.read_data(data_path)

        ampl.setOption("solver", "gurobi")
        # Solve the model
        ampl.solve()

        # Get the results (update objective name and variable names as per your model)
        obj_value = ampl.get_objective('TotalProfit').value()  # Change 'obj' to your AMPL objective name
        results_text.delete(1.0, tk.END)  # Clear the Results box
        results_text.insert(tk.END, f"Basic Model Objective Value: {obj_value}\n")

        # Example: Retrieve variable results (replace 'x' with your decision variable name)
        var = ampl.get_variable('x')  # Replace 'x' with variable name in your model
        for index, value in var.get_values().to_dict().items():
            results_text.insert(tk.END, f"Variable {index}: {value}\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running the Basic Model:\n{str(e)}")


# Function to solve the detailed model
def run_detailed_model():
    try:
        # Initialize AMPL
        ampl = AMPL()

        # Load the detailed model from the file bundled with the source code
        ampl.read("detailed_model.mod")

        # Check if the user provided a data file
        data_path = data_file_var.get()
        if not data_path:
            messagebox.showerror("Error", "Please select a data file for the Detailed Model.")
            return

        # Load the data file
        ampl.read_data(data_path)

        ampl.setOption("solver", "gurobi")

        # Solve the model
        ampl.solve()

        # Get the results
        obj_value = ampl.get_objective('ObjectiveFunction').value()  #  AMPL objective name
        results_text.delete(1.0, tk.END)  # Clear the Results box
        results_text.insert(tk.END, f"Detailed Model Objective Value: {obj_value}\n")

        # Example: Retrieve variable results
        var = ampl.get_variable('x')  
        for index, value in var.get_values().to_dict().items():
            results_text.insert(tk.END, f"Variable {index}: {value}\n")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running the Detailed Model:\n{str(e)}")


# Function to select a data file
def select_data_file():
    file_path = filedialog.askopenfilename(filetypes=[("AMPL Data Files", "*.dat")])
    data_file_var.set(file_path)


# Create the GUI window
root = tk.Tk()
root.title("AMPL Model Runner")

# Input data file selection
tk.Label(root, text="Select Data File (.dat):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
data_file_var = tk.StringVar()
tk.Entry(root, textvariable=data_file_var, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse...", command=select_data_file).grid(row=0, column=2, padx=10, pady=5)

# Buttons to run the models
tk.Button(root, text="Run Basic Model", command=run_basic_model, width=15).grid(row=1, column=0, padx=10, pady=10)
tk.Button(root, text="Run Detailed Model", command=run_detailed_model, width=15).grid(row=1, column=1, padx=10, pady=10)

# Results display
tk.Label(root, text="Results:").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
results_text = tk.Text(root, width=80, height=20)
results_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# Start the Tkinter event loop
root.mainloop()
