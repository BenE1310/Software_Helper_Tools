import tkinter as tk
from tkinter import messagebox

def set_server(choice):
    """Stores the server choice and opens the second window"""
    global server_choice
    server_choice = choice
    selection_window.destroy()  # Close first window
    open_parameter_window()  # Open second window

def open_parameter_window():
    """Opens the second popup with parameters based on the selected server"""
    parameter_window = tk.Toplevel()
    parameter_window.title(f"Settings for Server {server_choice}")
    parameter_window.geometry("400x200")
    parameter_window.configure(bg="#f0f0f0")

    # Define parameters based on the server choice
    if server_choice == 1:
        param_text = "🔹 Server1\nIP: 192.168.1.100\nPort: 3306"
        color = "#4CAF50"  # Green
    else:
        param_text = "🔹 Server2\nIP: 192.168.2.200\nPort: 5432"
        color = "#2196F3"  # Blue

    tk.Label(parameter_window, text=param_text, font=("Arial", 14, "bold"), fg=color, bg="#f0f0f0").pack(pady=20)
    tk.Button(parameter_window, text="OK", font=("Arial", 12, "bold"), padx=15, pady=5, command=parameter_window.destroy).pack(pady=10)

# Hide the main window initially
root = tk.Tk()
root.withdraw()

# Create the first popup for server selection
selection_window = tk.Toplevel()
selection_window.title("Select Server")
selection_window.geometry("400x250")
selection_window.configure(bg="#2C3E50")
selection_window.resizable(False, False)
selection_window.protocol("WM_DELETE_WINDOW", lambda: messagebox.showerror("Error", "You must select a server!"))

# Header label
tk.Label(selection_window, text="Choose DB Server", font=("Arial", 16, "bold"), fg="white", bg="#2C3E50").pack(pady=15)

# Buttons
btn1 = tk.Button(selection_window, text="DB01", font=("Arial", 14, "bold"), fg="white", bg="#2196F3",
                 padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0, command=lambda: set_server(1))
btn1.pack(pady=10)

btn2 = tk.Button(selection_window, text="DB02", font=("Arial", 14, "bold"), fg="white", bg="#2196F3",
                 padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0, command=lambda: set_server(2))
btn2.pack(pady=10)

root.mainloop()  # Start Tkinter event loop
