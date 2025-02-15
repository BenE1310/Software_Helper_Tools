import os
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.ttk import Label
import subprocess


def open_services_windows():
    # List of server names with associated IPs and services
    servers_info = [
        {"name": "BMC Main", "ip": "12.9.19.1", "service": "spooler"},
        {"name": "BMC Backup", "ip": "12.9.19.2", "service": "spooler"},
        {"name": "ICS Main", "ip": "12.9.19.3", "service": "spooler"},
        {"name": "ICS Backup", "ip": "12.9.19.4", "service": "spooler"},
        {"name": "DB Main", "ip": "12.9.19.5", "service": "mssqlserver"},
        {"name": "DB Backup", "ip": "12.9.19.5", "service": "mssqlserver"},
        {"name": "Client1", "ip": "192.168.3.154", "service": "spooler"},
        {"name": "Client2", "ip": "12.9.19.8", "service": "client_service"},
        {"name": "Client3", "ip": "12.9.19.9", "service": "client_service"},
        {"name": "Client4", "ip": "12.9.19.10", "service": "client_service"},
        {"name": "Client5", "ip": "12.9.19.11", "service": "client_service"}
    ]

    def update_server_status_async():
        # Run the update_server_status function in a separate thread
        thread = threading.Thread(target=update_server_status, daemon=True)
        thread.start()

    def replace_ip_number(new_number):
        for server in servers_info:
            server['ip'] = server['ip'].replace('12.9.', f'12.9.{new_number}')

    def ping_server(ip):
        # Determine the ping command based on the operating system
        if platform.system().lower() == "windows":
            command = f"ping -n 2 -w 500 {ip} > NUL"  # Windows: -n for number of echo requests, -w for timeout in milliseconds
        response = os.system(command)
        return response == 0  # Returns True if ping is successful (exit code 0), False otherwise

    # Function to check if a specific service is running on a server
    def is_service_running(ip, service_name):
        try:
            command = f"sc \\\\{ip} query {service_name}"
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "RUNNING" in result.stdout.decode()
        except subprocess.CalledProcessError as e:
            print(f"Failed to query {service_name} on {ip}: {e.stderr.decode()}")
            return False

    # Function to update server status colors based on ping and service status
    def update_server_status():
        # Show a message box to inform the user about the process
        messagebox.showinfo(
            "Pay attention",
            "The app is checking the status of the servers and clients. It will take a few moments, please wait."
        )

        # Reset the progress bar
        progress["value"] = 0
        progress["maximum"] = len(servers)  # Set the maximum value to the number of servers

        # Iterate through the servers and check their status
        for i, server in enumerate(servers):
            server_info = next((s for s in servers_info if s["name"] == server["name"]), None)
            if server_info:
                ip = server_info["ip"]
                service_name = server_info["service"]

                # Check if the server is reachable
                reachable = ping_server(ip)

                if reachable:
                    # Check if the service is running
                    service_running = is_service_running(ip, service_name)
                    if service_running:
                        server["label"].config(fg="green")  # Server reachable and service running
                    else:
                        server["label"].config(fg="red")  # Server reachable but service not running
                else:
                    server["label"].config(fg="black")  # Server not reachable

            # Update the progress bar
            progress["value"] = i + 1
            root.update_idletasks()  # Update the GUI to reflect progress

        # Notify the user when the update is complete
        messagebox.showinfo("Status Update Complete", "The status check is complete.")

    # Function to start marked servers
    def start_servers():
        for server in servers:
            if server["checker"].var.get():
                server_info = next((s for s in servers_info if s["name"] == server["name"]), None)
                if server_info:
                    ip = server_info["ip"]
                    service_name = server_info["service"]
                    success = start_service(ip, service_name)
                    if success:
                        server["label"].config(fg="green")

    # Function to stop marked servers
    def stop_servers():
        for server in servers:
            if server["checker"].var.get():
                server_info = next((s for s in servers_info if s["name"] == server["name"]), None)
                if server_info:
                    ip = server_info["ip"]
                    service_name = server_info["service"]
                    success = stop_service(ip, service_name)
                    if success:
                        server["label"].config(fg="red")

    # Function to start a specific service on a server
    def start_service(ip, service_name):
        try:
            command = f"sc \\\\{ip} start {service_name}"
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Started {service_name} on {ip}: {result.stdout.decode()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to start {service_name} on {ip}: {e.stderr.decode()}")
            return False

    # Function to stop a specific service on a server
    def stop_service(ip, service_name):
        try:
            command = f"sc \\\\{ip} stop {service_name}"
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Stopped {service_name} on {ip}: {result.stdout.decode()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop {service_name} on {ip}: {e.stderr.decode()}")
            return False

    # Function to check all servers
    def check_all():
        for server in servers:
            server["checker"].var.set(True)  # Set checkbox to checked

    # Function to uncheck all servers
    def uncheck_all():
        for server in servers:
            server["checker"].var.set(False)  # Set checkbox to unchecked

    # Initialize the main Tkinter window
    root = tk.Tk()
    root.title("Server Control Panel")
    root.geometry("550x550")
    root.configure(bg="gray")

    # Configure button style
    style = ttk.Style()
    style.configure('TButton', font=('calibri', 14, 'bold'))

    # List to hold server information (name, label, and checkbox)
    servers = []

    # Create server rows
    for i, server_info in enumerate(servers_info):
        label = tk.Label(root, text=server_info["name"], font=('calibri', 12, 'bold'), bg="gray", fg="white")
        label.place(x=50, y=60 + i * 40)

        var = tk.BooleanVar()
        checker = tk.Checkbutton(root, variable=var, bg="gray")
        checker.place(x=200, y=60 + i * 40)

        servers.append({"name": server_info["name"], "label": label, "checker": checker})
        servers[-1]["checker"].var = var

    user_input = simpledialog.askstring("Input", "Enter the battery number:")
    if user_input is not None and user_input.isdigit():
        replace_ip_number(user_input)
    else:
        print("Invalid input. Please enter a valid number.")

    title_label = tk.Label(root, text="Services Control - Battery " + user_input, font=('calibri', 18, 'bold'),
                           bg="gray",
                           fg="white")
    title_label.place(x=140, y=10)

    start_button = ttk.Button(root, text="Start", command=start_servers)
    start_button.place(x=400, y=60)

    stop_button = ttk.Button(root, text="Stop", command=stop_servers)
    stop_button.place(x=400, y=110)

    # Check All and Uncheck All buttons
    check_all_button = ttk.Button(root, text="Mark All", command=check_all)
    check_all_button.place(x=400, y=210)

    uncheck_all_button = ttk.Button(root, text="Unmark All", command=uncheck_all)
    uncheck_all_button.place(x=400, y=260)

    refresh_buttom = ttk.Button(root, text="Refresh", command=update_server_status_async)
    refresh_buttom.place(x=400, y=160)

    exit_button = ttk.Button(root, text="Exit", command=root.quit)
    exit_button.place(x=400, y=500)

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.place(x=50, y=500)  # Place it near the bottom of the window
    # Initial server status check on startup

    update_server_status()
    root.mainloop()


if __name__ == "__main__":
    open_services_windows()
