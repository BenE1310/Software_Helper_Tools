import json
import os
import subprocess
import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox

import pythoncom
import wmi


def check_communication(ip):
    """Attempts to ping the given IP and returns True if successful, False otherwise."""
    try:
        result = subprocess.run(["ping", "-n", "1", ip], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print(f"SUCCESS: Communication with {ip} is OK.")
            return True
        else:
            print(f"ERROR: No communication with {ip}. Ping output:\n{result.stdout}")
            return False
    except Exception as e:
        print(f"EXCEPTION: Failed to check communication with {ip}. Error: {e}")
        return False


def check_services(ip, services):
    """Check if services are running on a remote machine using WMI."""
    try:
        pythoncom.CoInitialize()
        print(f"[DEBUG] Connecting to {ip} for service status check...")
        conn = wmi.WMI(ip)
        service_status = {}
        for service_name in services:
            print(f"[DEBUG] Checking service: {service_name} on {ip}...")
            service = conn.Win32_Service(Name=service_name)
            if service:
                actual_state = service[0].State
                print(f"[DEBUG] {service_name} is {actual_state}")
                service_status[service_name] = actual_state == "Running"
            else:
                print(f"[ERROR] Service {service_name} not found on {ip}")
                service_status[service_name] = False
        return service_status
    except Exception as e:
        print(f"[EXCEPTION] Error checking services on {ip}: {e}")
        return {service: False for service in services}
    finally:
        pythoncom.CoUninitialize()

def check_service_user(ip, service, expected_user):
    """Check which user a service is running under and compare it with the expected user."""
    try:
        pythoncom.CoInitialize()
        conn = wmi.WMI(ip)
        service_obj = conn.Win32_Service(Name=service)
        if service_obj:
            actual_user = service_obj[0].StartName
            if actual_user != expected_user:
                print(f"[ERROR] Service {service} is running under {actual_user}, expected {expected_user}.")
                return False
            return True
        else:
            print(f"[ERROR] Service {service} not found on {ip}")
            return False
    except Exception as e:
        print(f"[EXCEPTION] Error checking service user for {service} on {ip}: {e}")
        return False
    finally:
        pythoncom.CoUninitialize()



def check_service_recovery(ip, service, expected_recovery):
    """Check the recovery settings for a Windows service and compare it with expected recovery type."""
    try:
        pythoncom.CoInitialize()
        command = ["sc"]
        if ip != "127.0.0.1":
            command.append(f"\\{ip}")
        command.extend(["qfailure", service])

        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout.lower()

        restart_count = output.count("restart -- delay")
        valid_recovery = (expected_recovery == "Restart" and restart_count == 3) or \
                          (expected_recovery == "RunProgram" and "run program" in output) or \
                          (expected_recovery == "None" and "none" in output)

        if not valid_recovery:
            print(f"[ERROR] Recovery settings for {service} are not as expected ({expected_recovery}).")
        return valid_recovery
    except Exception as e:
        print(f"[EXCEPTION] Error checking recovery settings for {service} on {ip}: {e}")
        return False
    finally:
        pythoncom.CoUninitialize()



def refresh_all_hosts(hosts, labels, progress_bar):
    """Performs refresh check on all hosts and their services."""
    if not hosts:
        messagebox.showwarning("No Hosts", "No hosts to refresh.")
        return

    progress_bar["value"] = 0
    step = 100 / len(hosts)

    for host, info in hosts.items():
        ip = info["ip"]
        if not check_communication(ip):
            labels[host].config(fg="black", text=f"{host} (No Communication)")
        else:
            services_status = check_services(ip, info["services"])
            for service, status in services_status.items():
                if not status:
                    labels[host].config(fg="red", text=f"{host} (Service Down)")
                    break
            else:
                # Check user and recovery type for each service
                for service_info in info["services"]:
                    service_name = service_info["name"]
                    expected_user = service_info["user"]
                    expected_recovery = service_info["recovery"]

                    if not check_service_user(ip, service_name, expected_user):
                        labels[host].config(fg="yellow", text=f"{host} (Invalid User for {service_name})")
                        break
                    if not check_service_recovery(ip, service_name, expected_recovery):
                        labels[host].config(fg="yellow", text=f"{host} (Invalid Recovery for {service_name})")
                        break
                else:
                    labels[host].config(fg="green", text=f"{host} (Service OK)")
        progress_bar["value"] += step
    progress_bar["value"] = 100




def perform_tests(hosts, labels, progress_bar):
    total_tests = len(hosts)
    if total_tests == 0:
        return

    progress_bar["value"] = 0
    step = 100 / total_tests

    for index, (host, info) in enumerate(hosts.items()):
        ip = info["ip"]
        if not check_communication(ip):
            labels[host].config(fg="black", text=f"{host} (No Communication)")
        else:
            services_status = check_services(ip, info["services"])
            for service, status in services_status.items():
                if not status:
                    labels[host].config(fg="red", text=f"{host} (Service Down)")
                    break
            else:
                # Check user and recovery type for each service
                for service_info in info["services"]:
                    service_name = service_info["name"]
                    expected_user = service_info["user"]
                    expected_recovery = service_info["recovery"]

                    if not check_service_user(ip, service_name, expected_user):
                        labels[host].config(fg="yellow", text=f"{host} (Invalid User for {service_name})")
                        break
                    if not check_service_recovery(ip, service_name, expected_recovery):
                        labels[host].config(fg="yellow", text=f"{host} (Invalid Recovery for {service_name})")
                        break
                else:
                    labels[host].config(fg="green", text=f"{host} (Service OK)")
        progress_bar["value"] += step
    progress_bar["value"] = 100

def add_log_to_result_bar(log_text, result_text_widget):
    """Update the result bar with logs."""
    result_text_widget.insert(tk.END, log_text + '\n')
    result_text_widget.yview(tk.END)  # Auto-scroll to the bottom




def start_services(selected_hosts, hosts, labels):
    """Simulates starting services and updates UI."""
    for host in selected_hosts:
        for service in hosts[host]["services"]:
            print(f"Starting {service} on {host}")
            # Simulate the service being started
            labels[host].config(fg="green", text=f"{host} (Service Running)")
    messagebox.showinfo("Start", f"Started services on: {', '.join(selected_hosts)}")

def stop_services(selected_hosts, hosts, labels):
    """Simulates stopping services and updates UI."""
    for host in selected_hosts:
        for service in hosts[host]["services"]:
            print(f"Stopping {service} on {host}")
            # Simulate the service being stopped
            labels[host].config(fg="red", text=f"{host} (Service Stopped)")
    messagebox.showinfo("Stop", f"Stopped services on: {', '.join(selected_hosts)}")

def open_utilities_window():
    utilities_window = tk.Toplevel()
    utilities_window.title("Utilities")
    utilities_window.geometry("1000x800")  # Larger window size
    utilities_window.resizable(True, True)
    utilities_window.configure(bg="#2E2E2E")  # Background color for a modern look

    default_hosts = {
        "Ben": {
            "ip": "127.0.0.1",
            "services": [
                {"name": "Spooler", "user": "LocalSystem", "recovery": "Restart"}
            ]
        },
        "Server2": {
            "ip": "192.168.1.20",
            "services": [
                {"name": "ServiceC", "user": "Administrator", "recovery": "RunProgram"}
            ]
        },
        "DB-Server": {
            "ip": "192.168.1.30",
            "services": [
                {"name": "DatabaseService1", "user": "DBAdmin", "recovery": "None"},
                {"name": "DatabaseService2", "user": "DBAdmin", "recovery": "Restart"}
            ]
        }
    }

    # Placeholder function for your threading tasks
    def perform_tests(hosts, labels, progress_bar):
        pass

    services_file = "services.json"
    if os.path.exists(services_file):
        with open(services_file, 'r') as file:
            hosts = json.load(file)
    else:
        hosts = default_hosts
        messagebox.showinfo("Info", "Using default host list as services.json was not found.")

    selections = {host: tk.BooleanVar() for host in hosts}
    labels = {}

    # Header label
    tk.Label(utilities_window, text="Utilities Management", font=("Arial", 24, "bold"), bg="#2E2E2E", fg="white").place(x=380, y=20)

    # Progress Bar
    progress_bar = ttk.Progressbar(utilities_window, orient="horizontal", mode="determinate", length=400)
    progress_bar.place(x=300, y=70)

    # Direct Host Checkboxes (No Scroll Frame)
    y_position = 150  # Starting position for checkboxes
    for host, info in hosts.items():
        row_frame = tk.Frame(utilities_window, bg="#2E2E2E")
        row_frame.place(x=50, y=y_position, width=900, height=40)
        tk.Checkbutton(row_frame, variable=selections[host], bg="#2E2E2E", fg="white", selectcolor="#2E2E2E").pack(side="left", padx=5)
        labels[host] = tk.Label(row_frame, text=host, font=("Arial", 16), bg="#2E2E2E", fg="white")
        labels[host].pack(side="left")
        y_position += 50  # Increment y position for the next checkbox

    threading.Thread(target=perform_tests, args=(hosts, labels, progress_bar)).start()

    # Result Text Widget
    result_text_widget = tk.Text(utilities_window, width=80, height=10, wrap=tk.WORD, bg="#333333", fg="white", bd=2, font=("Arial", 12))
    result_text_widget.place(x=50, y=y_position + 20)

    # Button Frame for right-alignment
    button_frame = tk.Frame(utilities_window, bg="#2E2E2E")
    button_frame.place(x=700, y=150, width=250, height=500)  # Adjusted height to fit all buttons

    button_style = {"font": ("Arial", 16), "bg": "#4B7BE8", "fg": "white", "bd": 2, "relief": "solid", "width": 15}

    # Buttons with proper placement, all aligned to the right
    button_y_position = 0  # Starting y position for the first button

    tk.Button(button_frame, text="Set All", command=lambda: [var.set(True) for var in selections.values()],
              bg="green", **button_style).place(x=0, y=button_y_position)
    button_y_position += 60  # Increment y position for the next button

    tk.Button(button_frame, text="Clear All", command=lambda: [var.set(False) for var in selections.values()],
              bg="red", **button_style).place(x=0, y=button_y_position)
    button_y_position += 60  # Increment y position for the next button

    tk.Button(button_frame, text="Restart Watchdog", command=lambda: print("Restarting Watchdog..."),
              **button_style).place(x=0, y=button_y_position)
    button_y_position += 60  # Increment y position for the next button

    tk.Button(button_frame, text="Shutdown Servers", command=lambda: print("Shutting down Servers..."),
              **button_style).place(x=0, y=button_y_position)
    button_y_position += 60  # Increment y position for the next button

    tk.Button(button_frame, text="Refresh", command=lambda: threading.Thread(target=refresh_all_hosts, args=(hosts, labels, progress_bar)).start(),
              **button_style).place(x=0, y=button_y_position)

    utilities_window.mainloop()

# Calling the function to open the window
open_utilities_window()
