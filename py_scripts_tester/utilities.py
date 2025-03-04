import os
import json
import platform
import re
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pythoncom


###############################################################################
#                               CHECK FUNCTIONS                               #
###############################################################################

def can_ping(ip_address):
    """
    Simple function to check host reachability via a single ping.
    Returns True if ping succeeds, False otherwise.
    """
    # Pick the right parameter for Windows ('-n') or Linux/macOS ('-c')
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    # Suppress the ping output by redirecting it
    result = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result == 0

def is_service_running(host_ip, service_name):
    """
    Check if a given Windows service is running on a remote machine.
    Distinguish between service not running, service access denied, and other errors.
    :param host_ip: IP or hostname of the remote Windows machine.
    :param service_name: Name of the Windows service to query.
    :return: Tuple (status, message)
             status: True if running, False if not running, None if error.
             message: None if running, error message if not running or error.
    """
    cmd = ['sc', f'\\\\{host_ip}', 'query', service_name]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        if 'RUNNING' in output:
            return True, None
        else:
            return False, f"Service '{service_name}' is down."
    except subprocess.CalledProcessError as e:
        if 'Access is denied' in e.output:
            return None, f"Access denied when checking service '{service_name}' on host {host_ip}."
        else:
            return None, f"Error checking service '{service_name}' on host {host_ip}: {str(e)}"

def get_service_running_user(host_ip, service_name):
    """
    Retrieves the 'Log On As' (running user) of a Windows service on a remote machine.
    Uses 'sc \\<host_ip> qc <service_name>' and parses the 'SERVICE_START_NAME:' line.

    Returns a string like 'LocalSystem', 'NT AUTHORITY\\NetworkService', 'DOMAIN\\user', etc.
    Returns None if the command fails or we can't parse the result.
    """
    # Example command: sc \\192.168.1.10 qc Spooler
    cmd = ['sc', f'\\\\{host_ip}', 'qc', service_name]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError:
        # If the command fails (e.g. service not found, permission denied, etc.), return None
        return None

    # The sc qc output typically contains a line like:
    #    SERVICE_START_NAME : LocalSystem
    #
    # Another example:
    #    SERVICE_START_NAME : NT AUTHORITY\NetworkService
    #
    # We'll search for a line that starts with "SERVICE_START_NAME" or a similar pattern,
    # then parse the user.

    match = re.search(r"SERVICE_START_NAME\s*:\s*(.+)", output)
    if match:
        return match.group(1).strip()
    else:
        return None

def get_service_recovery_type(host_ip, service_name, expected_recovery):
    """
    Retrieves and validates the recovery settings for a Windows service on a remote machine.
    Uses 'sc qfailure' and checks the recovery actions for the first three failures.

    :param host_ip: IP or hostname of the Windows machine.
    :param service_name: Name of the service to check.
    :param expected_recovery: The expected recovery setting ("Restart", "RunProgram", "None").
    :return: True if the recovery settings match the expectation, False otherwise.
    """
    try:
        # Initialize COM libraries (required if this runs in a threaded environment or needs COM)
        pythoncom.CoInitialize()

        # Build the command
        cmd = ["sc", f"\\\\{host_ip}", "qfailure", service_name]

        # Run the command and get output
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.lower()

        # Count occurrences of "restart -- delay" which indicates a restart action
        restart_count = output.count("restart -- delay")

        # Validate against expected recovery settings
        valid = (
            (expected_recovery == "Restart" and restart_count == 3) or
            (expected_recovery == "RunProgram" and "run program" in output) or
            (expected_recovery == "None" and "none" in output)
        )
        return valid

    except Exception as e:
        print(f"[EXCEPTION recovery] {e}")
        return False

    finally:
        # Uninitialize COM libraries
        pythoncom.CoUninitialize()

###############################################################################
#                           OPEN UTILITIES WINDOW                             #
###############################################################################

def open_utilities_window():
    utilities_window = tk.Toplevel()
    utilities_window.title("Utilities")
    utilities_window.geometry("1000x800")
    utilities_window.resizable(False, False)
    utilities_window.configure(bg="#2E2E2E")

    label_window = "Regional"

    # Sample fallback data
    default_hostnames_utilities = {
        "Ben": {
            "ip": "12.9.95.10",
            "services": [
                {"name": "Spooler", "user": "admin", "recovery": "Restart"}
            ]
        },
        "Host2": {
            "ip": "192.168.0.2",
            "services": [
                {"name": "Watchdog", "user": "user1", "recovery": "RunProgram"},
                {"name": "ServiceB", "user": "user1", "recovery": "RunProgram"}
            ]
        },
    }

    def load_json(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            root = tk.Tk()  # Ensure that there's a root window
            root.withdraw()  # Hide the root window
            messagebox.showerror("JSON Loading Error", f"Failed to load JSON file: {e}", parent=utilities_window)
            messagebox.showinfo("Loading hosts", "Loading default file.", parent=utilities_window)
            root.destroy()  # Destroy the root window after displaying the message
            return None  # Return None to indicate failure

    # Load from JSON or use default
    # Define the path to the JSON configuration file
    hostnames_file_path_utilities = ".\\Config\\utilitiesHostnames.json"

    # Check if the JSON file exists
    if os.path.exists(hostnames_file_path_utilities):
        # Load the JSON data using the load_json function
        hostnames = load_json(hostnames_file_path_utilities)

        # Check if there was an error loading the JSON (i.e., hostnames is None)
        if hostnames is None:
            # If there was an error, fall back to default settings
            hostnames = default_hostnames_utilities
    else:
        # If the file doesn't exist, use the default settings
        hostnames = default_hostnames_utilities

    # Title label
    tk.Label(
        utilities_window,
        text=f"Utilities - {label_window}",
        font=("Arial", 24, "bold"),
        bg="#2E2E2E",
        fg="white"
    ).place(x=500, y=30, anchor="center")

    # Scrollable frame for hosts
    scroll_frame = tk.Frame(utilities_window, bg="#2E2E2E")
    scroll_frame.place(x=10, y=100, width=275, height=620)

    canvas = tk.Canvas(scroll_frame, bg="#2E2E2E", highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    host_frame = tk.Frame(canvas, bg="#2E2E2E")

    host_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((10, 0), window=host_frame, anchor="nw")
    scrollbar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)

    # Track checkboxes and labels for each host
    selections = {}
    labels = {}

    for host in hostnames:
        selections[host] = tk.BooleanVar(value=True)
        item_frame = tk.Frame(host_frame, bg="#2E2E2E")
        item_frame.pack(anchor="w", pady=10)

        checkbutton = tk.Checkbutton(
            item_frame,
            variable=selections[host],
            bg="#2E2E2E",
            fg="white",
            selectcolor="#2E2E2E",
            anchor="w"
        )
        checkbutton.grid(row=0, column=0, padx=5)

        host_label = tk.Label(
            item_frame,
            text=host,
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#2E2E2E",
            anchor="w"
        )
        host_label.grid(row=0, column=1, padx=5)
        labels[host] = host_label

    # Text widget for showing results
    result_text_widget = tk.Text(
        utilities_window,
        width=48,
        height=34,
        wrap=tk.WORD,
        bg="#333333",
        fg="white",
        bd=2,
        font=("Arial", 12)
    )

    #################### Start Watchdog ####################

    def start_service(host_ip, service_name):
        """
        Attempts to start a specified service on a remote machine.
        Returns a tuple (success: bool, message: str).
        """
        cmd = ['sc', f'\\\\{host_ip}', 'start', service_name]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            return True, f"Service '{service_name}' started successfully on host {host_ip}."
        except subprocess.CalledProcessError as e:
            return False, f"Failed to start service '{service_name}' on host {host_ip}: {str(e)}"

    def start_watchdog_threaded():
        """Called by the button. Spawns a worker thread so the UI doesn't freeze."""
        t = threading.Thread(target=start_watchdog_process)
        t.start()

    def start_watchdog_process():
        """
        Runs in a background thread:
        1. Finds which hosts are selected,
        2. Starts all services for those hosts,
        3. Logs progress to the result bar and updates the progress bar.
        """
        # Clear the results bar
        result_text_widget.delete("1.0", tk.END)

        # Collect all services from marked hosts
        services_to_start = []
        for host_name, host_info in hostnames.items():
            if selections[host_name].get():  # Only if this host is marked
                ip_address = host_info["ip"]
                for svc in host_info["services"]:
                    services_to_start.append((host_name, ip_address, svc["name"]))

        # If there are no services to start, just return
        if not services_to_start:
            result_text_widget.insert(tk.END, "No hosts/services selected to start.\n")
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=utilities_window)
            return

        # Calculate how much to increment the progress bar per service
        step_value = 100 / len(services_to_start)
        progress_bar["value"] = 0

        # Start each service in turn
        for host_name, ip_address, service_name in services_to_start:
            # Log that we are starting this service
            insert_text_threadsafe(f"Starting service '{service_name}' on host {host_name}...\n")

            # Attempt to start
            success, message = start_service(ip_address, service_name)

            # Log the result
            insert_text_threadsafe(message + "\n")

            # Update the host label color
            if success:
                labels[host_name].config(fg="white")
            else:
                labels[host_name].config(fg="red")

            # Increment progress bar
            increment_progress_threadsafe(step_value)

        # Make sure the progress bar is at 100% if not already
        progress_bar["value"] = 100

    def insert_text_threadsafe(text):
        """
        Safely insert text into the result_text_widget from a background thread.
        """
        result_text_widget.after(0, lambda: result_text_widget.insert(tk.END, text))

    def increment_progress_threadsafe(value):
        """
        Safely increment the progress bar from a background thread.
        """

        def update_bar():
            progress_bar["value"] = min(progress_bar["value"] + value, 100)

        progress_bar.after(0, update_bar)

    #################### Stop Watchdog ####################

    def stop_service(host_ip, service_name):
        """
        Attempts to stop a specified service on a remote machine.
        Returns a tuple (success: bool, message: str).
        """
        cmd = ['sc', f'\\\\{host_ip}', 'stop', service_name]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            return True, f"Service '{service_name}' stopped successfully on host {host_ip}."
        except subprocess.CalledProcessError as e:
            return False, f"Failed to stop service '{service_name}' on host {host_ip}: {str(e)}"

    def stop_watchdog_threaded():
        """
        Spawns a worker thread to stop the services for all marked hosts.
        Keeps the UI responsive.
        """
        t = threading.Thread(target=stop_watchdog_process)
        t.start()

    def stop_watchdog_process():
        """
        1. Finds the marked hosts and collects their services.
        2. Stops each service, logging progress to the result bar.
        3. Updates the progress bar in a thread-safe manner.
        """
        # Clear the results bar
        result_text_widget.delete("1.0", tk.END)

        # Collect all services from marked hosts
        services_to_stop = []
        for host_name, host_info in hostnames.items():
            if selections[host_name].get():  # Only if this host is marked
                ip_address = host_info["ip"]
                for svc in host_info["services"]:
                    services_to_stop.append((host_name, ip_address, svc["name"]))

        # If there are no services to stop, just return
        if not services_to_stop:
            result_text_widget.insert(tk.END, "No hosts/services selected to stop.\n")
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=utilities_window)
            return

        # Calculate how much to increment the progress bar per service
        step_value = 100 / len(services_to_stop)
        progress_bar["value"] = 0

        # Stop each service in turn
        for host_name, ip_address, service_name in services_to_stop:
            # Log that we are stopping this service
            insert_text_threadsafe(f"Stopping service '{service_name}' on host {host_name}...\n")

            # Attempt to stop
            success, message = stop_service(ip_address, service_name)

            # Log the result
            insert_text_threadsafe(message + "\n")

            # Update the host label color
            if success:
                labels[host_name].config(fg="white")
            else:
                labels[host_name].config(fg="red")

            # Increment progress bar
            increment_progress_threadsafe(step_value)

        # Make sure the progress bar is at 100% if not already
        progress_bar["value"] = 100


    #################### Restart Watchdog ####################

    def restart_watchdog_threaded():
        """Spawn a worker thread to restart (stop+start) all services for marked hosts."""
        t = threading.Thread(target=restart_watchdog_process)
        t.start()

    def restart_watchdog_process():
        """
        Background thread:
          1) Collect all services from marked hosts.
          2) For each service: stop -> start.
          3) Log messages in the result widget, update the progress bar.
        """
        # Clear the results bar
        result_text_widget.delete("1.0", tk.END)

        # Gather all services for marked hosts
        services_to_restart = []
        for host_name, host_info in hostnames.items():
            if selections[host_name].get():  # Check if this host is marked
                ip_address = host_info["ip"]
                for svc in host_info["services"]:
                    services_to_restart.append((host_name, ip_address, svc["name"]))


        if not services_to_restart:
            insert_text_threadsafe("No hosts/services selected to restart.\n")
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=utilities_window)
            return

        # Each service requires 2 operations (stop, then start).
        step_value = 100 / (len(services_to_restart) * 2)
        progress_bar["value"] = 0

        for host_name, ip_address, service_name in services_to_restart:
            # 1) Stop the service
            insert_text_threadsafe(f"Stopping service '{service_name}' on host {host_name}...\n")
            success_stop, msg_stop = stop_service(ip_address, service_name)
            insert_text_threadsafe(msg_stop + "\n")

            increment_progress_threadsafe(step_value)

            # 2) Start the service (only attempt if stop succeeded, or you can attempt anyway)
            insert_text_threadsafe(f"Starting service '{service_name}' on host {host_name}...\n")
            success_start, msg_start = start_service(ip_address, service_name)
            insert_text_threadsafe(msg_start + "\n")

            increment_progress_threadsafe(step_value)

            # Update host label color:
            if success_stop and success_start:
                labels[host_name].config(fg="white")
            else:
                labels[host_name].config(fg="red")

        # Ensure progress bar is fully complete
        progress_bar["value"] = 100

    #################### Copy from result bar functions ####################

    def copy_selection_to_clipboard(event=None):
        try:
            # Get the current selection from the text widget
            selected_text = result_text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Clear the clipboard and append the selected text
            result_text_widget.clipboard_clear()
            result_text_widget.clipboard_append(selected_text)
        except tk.TclError:
            # If there's no text selected, pass without doing anything
            pass

    def create_context_menu(text_widget):
        # Create a menu widget
        context_menu = tk.Menu(text_widget, tearoff=0)
        context_menu.add_command(label="Copy", command=copy_selection_to_clipboard)

        def on_right_click(event):
            try:
                # Display the context menu
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Make sure the menu is torn down properly
                context_menu.grab_release()

        text_widget.bind("<Button-3>",
                         on_right_click)  # Bind right-click to the context menu (Button-3 is the right-click button)

    create_context_menu(result_text_widget)

    result_text_widget.place(x=278, y=106)
    result_text_widget.bind("<Control-c>", copy_selection_to_clipboard)
    result_text_widget.bind("<Control-C>", copy_selection_to_clipboard)  # Sometimes needed for different platforms

    # Progress bar
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TProgressbar", thickness=14)
    progress_bar = ttk.Progressbar(
        utilities_window,
        style="TProgressbar",
        length=440,
        mode="determinate"
    )  
    progress_bar.place(x=278, y=70)
    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    #################### Refresh Function ####################

    def refresh_services():
        global root
        result_text_widget.delete("1.0", tk.END)
        total_services = sum(
            len(host_info['services']) for host_name, host_info in hostnames.items() if selections[host_name].get())
        # Each host we check also does a single ping
        total_marked_hosts = sum(1 for host_name in hostnames if selections[host_name].get())

        # Prevent division by zero if nothing is selected
        if total_services + total_marked_hosts == 0:
            result_text_widget.insert(tk.END, "No marked hosts to refresh.\n")
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=utilities_window)
            progress_bar["value"] = 0
            return

        progress_step = 100 / (total_services + total_marked_hosts)
        current_progress = 0
        progress_bar["value"] = 0

        for host_name, host_info in hostnames.items():
            # If the user didn't mark this host, skip it
            if not selections[host_name].get():
                continue

            ip_address = host_info["ip"]
            services = host_info["services"]

            # 1) Ping check
            host_reachable = can_ping(ip_address)
            current_progress += progress_step
            progress_bar["value"] = current_progress

            if not host_reachable:
                result_text_widget.insert(tk.END, f"No communication with {host_name}\n")
                labels[host_name].config(fg="#90E0Ef")
                continue  # Skip further checks for this host

            # 2) If reachable, check services
            for svc in services:
                service_name = svc["name"]
                expected_user = svc["user"]
                expected_recovery = svc["recovery"]

                is_up, error_message = is_service_running(ip_address, service_name)
                actual_user = get_service_running_user(ip_address, service_name)
                recovery_valid = get_service_recovery_type(ip_address, service_name, expected_recovery)

                current_progress += progress_step
                progress_bar["value"] = current_progress

                if is_up is None:
                    # Permission / other critical error
                    result_text_widget.insert(tk.END, error_message + f" for host {host_name}\n")
                    labels[host_name].config(fg="red")
                elif not is_up:
                    # Service is down
                    result_text_widget.insert(tk.END, f"Service '{service_name}' is down for host {host_name}\n")
                    labels[host_name].config(fg="red")
                elif actual_user and actual_user.lower() != expected_user.lower():
                    result_text_widget.insert(tk.END,
                                              f"Invalid running user for service '{service_name}' on host {host_name}. "
                                              f"Expected '{expected_user}', got '{actual_user}'.\n")
                    labels[host_name].config(fg="yellow")
                elif not recovery_valid:
                    result_text_widget.insert(tk.END,
                                              f"Recovery settings incorrect for service '{service_name}' on host {host_name}. "
                                              f"Expected '{expected_recovery}'.\n")
                    labels[host_name].config(fg="yellow")
                else:
                    result_text_widget.insert(tk.END, f"Service '{service_name}' is up properly for host {host_name}\n")
                    labels[host_name].config(fg="green")

        # Ensure the progress bar completes if not already full
        progress_bar["value"] = 100

    def refresh_threaded():
        # Run all checks in a worker thread so the UI remains responsive
        t = threading.Thread(target=refresh_services)
        t.start()


    #################### Restart Hosts ####################

    def restart_machine(host_ip):
        """
        Attempts to force an immediate restart on a remote Windows machine.
        Returns (success: bool, message: str).
        """
        cmd = ['shutdown', '/r', '/m', f'\\\\{host_ip}', '/t', '0', '/f']
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            return True, f"Restart command sent to host {host_ip}."
        except subprocess.CalledProcessError as e:
            return False, f"Failed to restart host {host_ip}: {str(e)}"

    def restart_component_threaded():
        """
        Called by the 'Restart Component' button.
        - Asks for user confirmation.
        - If yes, spawns a background thread to perform the restarts.
        """
        confirmation = messagebox.askyesno("Restart Component", "Are you sure you want to restart the selected hosts?", parent=utilities_window)
        if not confirmation:
            return  # User chose No

        # If user clicked Yes, spawn a worker thread
        t = threading.Thread(target=restart_component_process)
        t.start()

    def restart_component_process():
        """
        Runs in a background thread:
        - Finds all marked hosts
        - Sends the restart command to each
        - Logs results to the text widget
        """
        # Clear result text
        result_text_widget.delete("1.0", tk.END)

        # Gather the marked hosts
        marked_hosts = [host_name for host_name in hostnames if selections[host_name].get()]
        if not marked_hosts:
            insert_text_threadsafe("No hosts selected for restart.\n")
            return

        # For each marked host, send the restart command
        for host_name in marked_hosts:
            host_ip = hostnames[host_name]["ip"]
            success, message = restart_machine(host_ip)
            insert_text_threadsafe(message + "\n")

            # Update label color to indicate success or failure
            if success:
                labels[host_name].config(fg="white")
            else:
                labels[host_name].config(fg="red")

    #################### Shutdown Hosts ####################

    def shutdown_machine(host_ip):
        """
        Attempts to force an immediate shutdown on a remote Windows machine.
        Returns (success: bool, message: str).
        """
        cmd = ['shutdown', '/s', '/m', f'\\\\{host_ip}', '/t', '0', '/f']
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            return True, f"Shutdown command sent to host {host_ip}."
        except subprocess.CalledProcessError as e:
            return False, f"Failed to shutdown host {host_ip}: {str(e)}"

    def shutdown_component_threaded():
        """
        Called by the 'Shutdown Component' button.
        - Asks for user confirmation.
        - If yes, spawns a background thread to perform the shutdowns.
        """
        confirmation = messagebox.askyesno("Shutdown Component",
                                           "Are you sure you want to shut down the selected hosts?", parent=utilities_window)
        if not confirmation:
            return  # User chose No

        # If user clicked Yes, spawn a worker thread
        t = threading.Thread(target=shutdown_component_process)
        t.start()

    def shutdown_component_process():
        """
        Background thread:
        - Finds all marked hosts
        - Sends the shutdown command to each
        - Logs results to the text widget
        """
        # Clear result text
        result_text_widget.delete("1.0", tk.END)

        # Gather the marked hosts
        marked_hosts = [host_name for host_name in hostnames if selections[host_name].get()]
        if not marked_hosts:
            insert_text_threadsafe("No hosts selected for shutdown.\n")
            return

        # For each marked host, send the shutdown command
        for host_name in marked_hosts:
            host_ip = hostnames[host_name]["ip"]
            success, message = shutdown_machine(host_ip)
            insert_text_threadsafe(message + "\n")

            # Update host label color
            if success:
                labels[host_name].config(fg="green")
            else:
                labels[host_name].config(fg="red")

    # Common button style
    button_style = {
        "font": ("Arial", 14),
        "fg": "white",
        "bd": 3,
        "relief": "solid",
        "width": 18,
        "height": 2
    }

    # Mark All
    tk.Button(
        utilities_window,
        text="Mark All",
        command=lambda: [v.set(True) for v in selections.values()],
        bg="green",
        **button_style
    ).place(x=750, y=100)

    # Unmark All
    tk.Button(
        utilities_window,
        text="Unmark All",
        command=lambda: [v.set(False) for v in selections.values()],
        bg="red",
        **button_style
    ).place(x=750, y=180)

    # "Refresh" uses the threaded function
    tk.Button(
        utilities_window,
        text="Refresh",
        command=refresh_threaded,
        bg="#000080",
        **button_style
    ).place(x=750, y=260)

    # The rest remain no-op
    tk.Button(
        utilities_window,
        text="Restart Watchdog",
        command=restart_watchdog_threaded,
        bg="#0099cc",
        **button_style
    ).place(x=750, y=340)

    tk.Button(
        utilities_window,
        text="Start Watchdog",
        command=start_watchdog_threaded,
        bg="#0099cc",
        **button_style
    ).place(x=750, y=420)

    tk.Button(
        utilities_window,
        text="Stop Watchdog",
        command=stop_watchdog_threaded,
        bg="#0099cc",
        **button_style
    ).place(x=750, y=500)

    tk.Button(
        utilities_window,
        text="Restart Component",
        command=restart_component_threaded,
        bg="#0099cc",
        **button_style
    ).place(x=750, y=580)

    tk.Button(
        utilities_window,
        text="Shutdown Component",
        command=shutdown_component_threaded,
        bg="#0099cc",
        **button_style
    ).place(x=750, y=660)

    # Close button
    close_button_style = {
        "font": ("Arial", 12),
        "fg": "white",
        "bd": 3,
        "relief": "solid",
        "width": 10,
        "height": 2
    }
    tk.Button(
        utilities_window,
        text="Close",
        command=utilities_window.destroy,
        bg="gray",
        **close_button_style
    ).place(x=500, y=764, anchor="center")


###############################################################################
#                          MAIN / DEMO APP LAUNCH                             #
###############################################################################

def main():
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("400x300")

    tk.Button(
        root, text="Open Utilities",
        command=open_utilities_window,
        font=("Arial", 16)
    ).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()


## (Get-Process -Name spoolsv).StartTime
