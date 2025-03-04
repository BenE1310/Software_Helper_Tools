import json
import platform
import shutil
import subprocess
import tkinter as tk
import time
from tkinter import PhotoImage, ttk, messagebox
import pythoncom
import wmi
from functions import check_communication, check_permissions, get_drive_space, get_remote_file_version, \
    change_bat_pos_function, cleanup_temp_files, prepare_installation_battery, prepare_installation_regional, \
    prepare_installation_simulator, write_bat_file_db_phase, handle_tables_battery, handle_adding_launchers_battery, \
    generate_sql_script_training_launchers, run_npcap_install, run_install_wireshark, run_open_wireshark
import tkinter.ttk as ttk
import threading
import pythoncom  # Import pythoncom for WMI operations
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring
import os
import sys
import tkinter as tk
import re


# Get the base directory (whether running from source or PyInstaller EXE)
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS  # PyInstaller EXE mode
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Normal script mode

# Locate all needed files and folders
icon_path = os.path.join(base_dir, "icon.ico")
logo_path = os.path.join(base_dir, "background.png")
version_file = os.path.join(base_dir, "version.txt")
functions_path = os.path.join(base_dir, "functions.py")
tools_path = os.path.join(base_dir, "tools")  # Folder
scripts_path = os.path.join(base_dir, "Scripts")  # Folder

# Read version info
VERSION = "Unknown"
if os.path.exists(version_file):
    with open(version_file, "r") as f:
        VERSION = f.read().strip()

# Get base directory (whether running as a script or inside an EXE)
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS  # PyInstaller temp directory
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Normal execution

# Locate icon inside the PyInstaller bundle
icon_source = os.path.join(base_dir, "icon.ico")
logo_source = os.path.join(base_dir, "background.png")


# Copy the icon to a writable temp directory if running as EXE
temp_icon_path = os.path.join(os.path.expanduser("~"), "icon_temp.ico")
temp_logo_path = os.path.join(os.path.expanduser("~"), "logo_temp.png")


if os.path.exists(icon_source):
    shutil.copy(icon_source, temp_icon_path)  # Copy icon to a valid location

if os.path.exists(logo_source):
    shutil.copy(logo_source, temp_logo_path)

# Button hover effect
def on_enter(button):
    button.config(bg='#666666')  # Lighter gray when hovered


def on_leave(button):
    button.config(bg='#444444')  # Default background color


# Button click effect
def on_click(button):
    button.config(bg='#555555')  # Dark gray when clicked
    button.after(200, lambda: button.config(bg='#444444'))  # Reset after 200ms


def on_button_click():
    clear_all_buttons()


def clear_all_buttons():
    for button in buttons:
        button.destroy()

def coming_soon():
    messagebox.showinfo("Coming Soon", "Coming soon!")


# Main Application
root = tk.Tk()
root.title("Software Helper Tools")
root.geometry("600x750")
root.resizable(False, False)
# root.eval('tk::PlaceWindow . center')
root.iconbitmap(temp_icon_path)

# Protect application
# try:
#     key = askstring('Lock', "Enter Master Key", show='*')
#     while key != "1234":
#         showinfo('Error', 'You type error master key!')
#         key = askstring('Enter Master Key', "The master key is invalid Please try again:", show='*')
# except:
#     pass
# else:
#     showinfo("Master key successful", "Welcome to \"FBE Software Helper Tool\"")

# Set Background Image


bg_image = PhotoImage(file=temp_logo_path)  # Ensure this image is in your directory
canvas = tk.Canvas(root, width=600, height=750, highlightthickness=0, borderwidth=0)
canvas.place(x=0, y=0)
canvas.create_image(0, 0, anchor='nw', image=bg_image)

# Button Styles
button_style = {
    'width': 24,
    'height': 2,
    'bg': '#444444',
    'fg': 'white',
    'font': ('Arial', 12, 'bold'),
    'activebackground': '#555555',
    'borderwidth': 0,
    'relief': 'flat'
}

button_style_small = {
    'width': 10,
    'height': 2,
    'bg': '#444444',
    'fg': 'white',
    'font': ('Arial', 12, 'bold'),
    'activebackground': '#555555',
    'borderwidth': 0,
    'relief': 'flat'
}

button_style_medium = {
    'width': 12,
    'height': 2,
    'bg': '#444444',
    'fg': 'white',
    'font': ('Arial', 12, 'bold'),
    'activebackground': '#555555',
    'borderwidth': 0,
    'relief': 'flat'
}

BN = 0
VSIL_BN = 0

buttons = []
installation_app_remote_message = []
progress_bar_ping = None
progress_bar_permissions = None
progress_bar_disk = None
progress_bar_version = None
selection_window_DB = None
server_choice = None



def open_ping_monitor():
    """
    Open a Toplevel window that displays a scrollable list of hostnames,
    pings them continuously in a background thread, highlights the current host,
    shows user alerts if the file is missing or invalid, and falls back to defaults
    if necessary.
    """

    # 1) Create the Toplevel first, so message dialogs can use it as a parent
    ping_window = tk.Toplevel()
    ping_window.title("Ping Monitor")
    ping_window.resizable(False, False)  # Disallow resizing
    # ping_window.iconbitmap(temp_icon_path)  # Optional: set window icon
    ping_window.geometry("300x900")

    # 2) Define default data
    default_hosts = [
        {
            "hostname": "Default Host",
            "ip": "192.168.0.1"
        }
    ]

    # 3) Attempt to load JSON
    def load_json(filename, parent_window):
        """
        Check if file exists; if not, show an error & info message, return None.
        If file exists but has invalid JSON, also show an error & info, return None.
        Otherwise return the parsed JSON.
        """
        if not os.path.exists(filename):
            messagebox.showerror(
                "File Not Found",
                f"The file '{filename}' doesn't exist.",
                parent=parent_window
            )
            messagebox.showinfo(
                "Loading Hosts",
                "Loading default file instead.",
                parent=parent_window
            )
            return None

        # Now try to parse it
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror(
                "JSON Loading Error",
                f"Failed to load JSON from '{filename}':\n\n{e}",
                parent=parent_window
            )
            messagebox.showinfo(
                "Loading Hosts",
                "Loading default file instead.",
                parent=parent_window
            )
            return None

    # 4) Load or fallback
    filename = 'Config\\pingBat.json'
    hosts_data = load_json(filename, ping_window)
    if hosts_data is None:
        hosts = default_hosts
    else:
        hosts = hosts_data

    # 5) Event used to stop the ping cycle thread
    stop_event = threading.Event()

    # 6) Ping logic
    def ping_host(ip):
        current_os = platform.system().lower()
        if 'windows' in current_os:
            cmd = f'ping -n 1 {ip} > NUL 2>&1'
        else:
            cmd = f'ping -c 1 {ip} > /dev/null 2>&1'
        response = os.system(cmd)
        return (response == 0)

    labels = []
    default_bg = []

    # Safe UI update functions (avoid TclError if window closes mid-update)
    def highlight_label(index):
        try:
            labels[index].config(bg='yellow')
        except tk.TclError:
            pass

    def unhighlight_label(index):
        try:
            labels[index].config(bg=default_bg[index])
        except tk.TclError:
            pass

    def update_label_color(index, reachable):
        try:
            if reachable:
                labels[index].config(fg='green')
            else:
                labels[index].config(fg='red')
        except tk.TclError:
            pass

    def ping_cycle():
        while not stop_event.is_set():
            for i, host in enumerate(hosts):
                if stop_event.is_set():
                    break

                # Highlight
                ping_window.after(0, highlight_label, i)

                # Ping
                reachable = ping_host(host["ip"])

                # Update color
                ping_window.after(0, update_label_color, i, reachable)

                # Unhighlight
                ping_window.after(0, unhighlight_label, i)

                time.sleep(1)

    def close_ping_window():
        stop_event.set()
        ping_window.destroy()

    ping_window.protocol("WM_DELETE_WINDOW", close_ping_window)

    # 7) UI Layout
    # Title label
    top_label = tk.Label(ping_window, text="Ping Monitor", font=("Arial", 16, "bold"))
    top_label.pack(side="top", pady=10)

    # Scrollable container
    container = tk.Frame(ping_window)
    container.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    canvas = tk.Canvas(container)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Create labels for each host
    for host_item in hosts:
        hostname = host_item["hostname"]
        lbl = tk.Label(scrollable_frame, text=hostname, font=("Arial", 12, "bold"))
        lbl.pack(pady=5, padx=10, anchor="w")
        labels.append(lbl)
        default_bg.append(lbl.cget("bg"))

    # Close button at bottom
    close_button = tk.Button(
        ping_window,
        text="Close",
        font=("Arial", 12, "bold"),
        command=close_ping_window
    )
    close_button.pack(pady=10)

    # 8) Start background thread
    thread = threading.Thread(target=ping_cycle, daemon=True)
    thread.start()


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
    global BN
    utilities_window = tk.Toplevel()
    utilities_window.title("Utilities")
    utilities_window.geometry("1000x800")
    utilities_window.iconbitmap(temp_icon_path)
    utilities_window.resizable(False, False)
    utilities_window.configure(bg="#2E2E2E")
    print(BN)

    if BN == 21:
        label_window = "- Regional"
    elif BN == "VSIL/CIWS":
        label_window = "- VSIL"
    elif BN == "1" or BN == "2" or BN == "3" or BN == "4" or BN == "5" or BN == "10":
        label_window = f"- Battery {BN}"
    else:
        label_window = ""
    print(label_window)

    # Sample fallback data
    default_hostnames_utilities = {
    "BMC1": {
        "ip": f"10.11.{BN}8.1",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
    "BMC2": {
        "ip": f"10.11.{BN}8.2",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
    "ICS1": {
        "ip": f"10.12.{BN}8.13",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"ICS2": {
        "ip": f"10.12.{BN}8.14",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"DB1": {
        "ip": f"10.11.{BN}8.3",
        "services": [
            {
                "name": "mDRS Agent Service",
                "user": "LocalSystem",
                "recovery": "Restart"
            },
            {
                "name": "mDRS Server Service",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"DB2": {
        "ip": f"10.11.{BN}8.4",
        "services": [
            {
                "name": "ServiceD",
                "user": "admin",
                "recovery": "Restart"
            },
            {
                "name": "ServiceE",
                "user": "user2",
                "recovery": "RunProgram"
            }
        ]
    },
	"Client1": {
        "ip": f"10.11.{BN}8.6",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"Client2": {
        "ip": f"10.11.{BN}8.7",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"Client3": {
        "ip": f"10.11.{BN}8.8",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"Client4": {
        "ip": f"10.11.{BN}8.9",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
        ]
    },
	"Client5": {
        "ip": f"10.11.{BN}8.10",
        "services": [
            {
                "name": "FBE Watchdog",
                "user": "LocalSystem",
                "recovery": "Restart"
            }
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
        text=f"Utilities {label_window}",
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

    # # Progress bar
    # style_progress_utilities = ttk.Style()
    # style_progress_utilities.theme_use("clam")
    #
    # # Configure progress bar style
    # style_progress_utilities.configure(
    #     "TProgressbar",
    #     thickness=14,
    #     troughcolor="lightgray",  # Track background color (classic look)
    #     background="green"  # Progress bar fill color (classic green)
    # )

    # Create Progress bar
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


# Tools phase
def open_finishscript():
    try:
        script_path = ".\\tools\\FinishScripts\\RunME.bat"

        if not os.path.exists(script_path):
            raise FileNotFoundError("FinishScript not found.")

        # Open in a new cmd window
        subprocess.Popen(f'start cmd /k "{script_path}"', shell=True)

    except FileNotFoundError:
        messagebox.showerror("Error", "FinishScript is not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start FinishScript: {e}")

def run_finishScript():
    threading.Thread(target=open_finishscript).start()

def open_ilspy():
    try:
        if not os.path.exists(".\\tools\\ILSpy\\ILSpy.exe"):
            raise FileNotFoundError("ILSpy.exe not found.")

        subprocess.run(".\\tools\\ILSpy\\ILSpy.exe", shell=True, check=True)
    except FileNotFoundError:
        messagebox.showerror("Error", "The file ILSpy.exe is not found.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to start ILSpy.exe: {e}")

def run_ilspy():
    threading.Thread(target=open_ilspy).start()


# Reusable function to create a button with hover effects
def create_button(parent, text, command, x, y, style=button_style, state='normal'):
    button = tk.Button(parent, text=text, **style, command=command, state=state)
    button.place(x=x, y=y)
    button.bind("<Enter>", lambda e: on_enter(button) if state == 'normal' else None)
    button.bind("<Leave>", lambda e: on_leave(button) if state == 'normal' else None)
    buttons.append(button)  # Add to buttons list for tracking
    return button

# Create a Button to Disable the Grayed-Out Button
def disable_button(window):
    window.config(state='disabled')  # Disable the grayed-out button


# Create a Button to Enable the Grayed-Out Button
def enable_button(window):
    window.config(state='normal')  # Enable the grayed-out button

# Database VSIL windows and functions

def set_server_vsil(choice):
    """Stores the server choice and moves to the next screen"""
    global selection_db_window_vsil, server_choice
    server_choice = choice  # Store choice if needed
    if selection_db_window_vsil:
        selection_db_window_vsil.destroy()  # Destroy the first popup
    open_vsil_database_window()  # Open the next screen

def selection_db_window_vsil_function():
    global set_server, selection_db_window_vsil
    # Create the first popup for server selection
    selection_db_window_vsil = tk.Toplevel()
    selection_db_window_vsil.title("Select DB")
    selection_db_window_vsil.geometry("250x250")
    selection_db_window_vsil.iconbitmap(temp_icon_path)
    selection_db_window_vsil.configure(bg="#C74375")
    selection_db_window_vsil.resizable(False, False)
    # selection_window.protocol("WM_DELETE_WINDOW",
    #                           lambda: messagebox.showerror("Error", "You must select a server!"))

    # Header label
    tk.Label(selection_db_window_vsil, text="Choose DB Server", font=("Arial", 16, "bold"), fg="white", bg="#C74375").pack(
        pady=15)

    # Buttons
    btn1 = tk.Button(selection_db_window_vsil, text="DB-BAT", font=("Arial", 14, "bold"), fg="white", bg="#9E003A",
                     padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0, width=8,
                     command=lambda: set_server_vsil(1))
    btn1.pack(pady=10)

    btn2 = tk.Button(selection_db_window_vsil, text="DB-CBMC", font=("Arial", 14, "bold"), fg="white", bg="#9E003A",
                     padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0, width=8,
                     command=lambda: set_server_vsil(2))
    btn2.pack(pady=10)

def open_vsil_database_window():

    # Define parameters based on the server choice
    database_window_vsil = tk.Toplevel()
    database_window_vsil.title("Table Management")
    database_window_vsil.geometry("400x500")
    database_window_vsil.resizable(False, False)
    database_window_vsil.configure(bg="#872657")
    database_window_vsil.iconbitmap(temp_icon_path)
    PN = 3

    if server_choice == 1:
        BN = 1
        hostname = "DB-BAT"
    else:
        BN = 21
        hostname = "DB-CBMC"
    print(server_choice)
    print(BN)

    # Title Label
    title_label = tk.Label(
        database_window_vsil, text=f"Database VSIL {hostname}", font=("Arial", 14, "bold"), fg="white", bg="#872657"
    )
    title_label.place(x=80, y=5)

    # Checkbox Variables
    operational_var = tk.BooleanVar()
    training_var = tk.BooleanVar()

    tk.Checkbutton(
        database_window_vsil, text="Operational", variable=operational_var,
        bg="#872657", fg="white", selectcolor="#872657", font=("Arial", 12)
    ).place(x=20, y=50)

    tk.Checkbutton(
        database_window_vsil, text="Training", variable=training_var,
        bg="#872657", fg="white", selectcolor="#872657", font=("Arial", 12)
    ).place(x=20, y=90)

    def on_close():
        database_window_vsil.destroy()  # Close the window

    def yes_no_keep_delete():
        response = messagebox.askyesno("Delete tables", "Are you sure you want to delete DB tables?", parent=None)
        if response:
            handle_delete_tables()
        else:
            return

    # Progress Bar
    progress_bar_db = ttk.Progressbar(database_window_vsil, orient="horizontal", mode="indeterminate", length=360)
    progress_bar_db.place(x=60, y=290, width=280, height=20)

    def start_progress():
        progress_bar_db.start(10)  # Starts animation with 10ms step

    def stop_progress():
        progress_bar_db.stop()  # Stops the animation

    # Wrap the existing functions with progress updates
    def run_with_progress(target_function):
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.", parent=None)
            return
        def wrapper():
            start_progress()
            target_function()
            stop_progress()
        threading.Thread(target=wrapper).start()


    def handle_create_empty_tables():
        global bat_file_name

        """
        Handles the "Create Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "CreateEmptyTablesOperational.bat"
        elif training_var.get():
            bat_file_name = "CreateEmptyTablesTraining.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, PN, current_bat_file=bat_file_name, results_text=results_text, parent_window=None)

    def create_empty_databases():
        run_with_progress(handle_create_empty_tables)


    def handle_delete_tables():
        global bat_file_name

        """
        Handles the "Create Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "DeleteDatabasesOperational.bat"
        elif training_var.get():
            bat_file_name = "DeleteDatabasesTraining.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, PN, current_bat_file=bat_file_name, results_text=results_text, parent_window=None)

    def delete_databases():
        run_with_progress(handle_delete_tables)

    def handle_import_tables():
        global bat_file_name

        """
        Handles the "Import Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "CreateTablesOperationalFBE.bat"
        elif training_var.get():
            bat_file_name = "CreateTablesTrainingFBE.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)


        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, PN,current_bat_file=bat_file_name, results_text=results_text, parent_window=None)


    def import_tables():
        run_with_progress(handle_import_tables)

    # Buttons on the right
    button_x = 210
    button_width = 170
    button_height = 40
    y_start = 50
    y_gap = 60

    tk.Button(
        database_window_vsil, text="Create Tables", font=("Arial", 12), bg="#C71585", fg="white",
        activebackground="#DC143C", command=create_empty_databases
    ).place(x=button_x, y=y_start, width=button_width, height=button_height)
    tk.Button(
        database_window_vsil, text="Delete Tables", font=("Arial", 12), bg="#C71585", fg="white",
        activebackground="#DC143C", command=yes_no_keep_delete
    ).place(x=button_x, y=y_start + y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_vsil, text="Import Tables", font=("Arial", 12), bg="#C71585", fg="white",
        activebackground="#DC143C", command=import_tables
    ).place(x=button_x, y=y_start + 2 * y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_vsil, text="Close", font=("Arial", 12), bg="#673147", fg="white",
        activebackground="#DC143C", command=on_close
    ).place(x=162, y=460, width=80, height=30)

    # Close button in the middle at the bottom


    # Results Display
    results_text = tk.Text(database_window_vsil, height=5, width=50, bg="#65000B", fg="white", font=("Arial", 10))
    results_text.place(x=20, y=330, width=360, height=120)


# Database Regional windows and functions

def set_server_regional(choice):
    """Stores the server choice and moves to the next screen"""
    global selection_DB_window_regional, server_choice
    server_choice = choice  # Store choice if needed
    if selection_db_window_regional:
        selection_db_window_regional.destroy()  # Destroy the first popup
    open_regional_database_window()  # Open the next screen

def selection_db_window_regional():
    global set_server, set_server_Battery, selection_db_window_regional
    # Create the first popup for server selection
    selection_db_window_regional = tk.Toplevel()
    selection_db_window_regional.title("Select DB")
    selection_db_window_regional.geometry("250x250")
    selection_db_window_regional.configure(bg="#301934")
    selection_db_window_regional.resizable(False, False)
    selection_db_window_regional.iconbitmap(temp_icon_path)
    # selection_window.protocol("WM_DELETE_WINDOW",
    #                           lambda: messagebox.showerror("Error", "You must select a server!"))

    # Header label
    tk.Label(selection_db_window_regional, text="Choose DB Server", font=("Arial", 16, "bold"), fg="white", bg="#301934").pack(
        pady=15)

    # Buttons
    btn1 = tk.Button(selection_db_window_regional, text="DB01", font=("Arial", 14, "bold"), fg="white", bg="#6F2DA8",
                     padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0,
                     command=lambda: set_server_regional(1))
    btn1.pack(pady=10)

    btn2 = tk.Button(selection_db_window_regional, text="DB02", font=("Arial", 14, "bold"), fg="white", bg="#6F2DA8",
                     padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0,
                     command=lambda: set_server_regional(2))
    btn2.pack(pady=10)

def open_regional_database_window():
    global BN

    # Define parameters based on the server choice
    database_window_regional = tk.Toplevel()
    database_window_regional.title("Table Management")
    database_window_regional.geometry("400x500")
    database_window_regional.resizable(False, False)
    database_window_regional.configure(bg="#663399")
    database_window_regional.iconbitmap(temp_icon_path)

    if server_choice == 1:
        PN = 3
    else:
        PN = 4

    # Title Label
    title_label = tk.Label(
        database_window_regional, text=f"Database Regional DB0{server_choice}", font=("Arial", 14, "bold"), fg="white", bg="#663399"
    )
    title_label.place(x=80, y=5)

    # Checkbox Variables
    operational_var = tk.BooleanVar()
    training_var = tk.BooleanVar()

    tk.Checkbutton(
        database_window_regional, text="Operational", variable=operational_var,
        bg="#663399", fg="white", selectcolor="#663399", font=("Arial", 12)
    ).place(x=20, y=50)

    tk.Checkbutton(
        database_window_regional, text="Training", variable=training_var,
        bg="#663399", fg="white", selectcolor="#663399", font=("Arial", 12)
    ).place(x=20, y=90)

    def on_close():
        database_window_regional.destroy()  # Close the window

    def yes_no_keep_delete():
        response = messagebox.askyesno("Delete tables", "Are you sure you want to delete DB tables?", parent=database_window_regional)
        if response:
            handle_delete_tables()
        else:
            return

    # Progress Bar
    progress_bar_db = ttk.Progressbar(database_window_regional, orient="horizontal", mode="indeterminate", length=360)
    progress_bar_db.place(x=60, y=290, width=280, height=20)

    def start_progress():
        progress_bar_db.start(10)  # Starts animation with 10ms step

    def stop_progress():
        progress_bar_db.stop()  # Stops the animation

    # Wrap the existing functions with progress updates
    def run_with_progress(target_function):
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.", parent=database_window_regional)
            return
        def wrapper():
            start_progress()
            target_function()
            stop_progress()
        threading.Thread(target=wrapper).start()


    def handle_create_empty_tables():
        global bat_num, bat_file_name

        """
        Handles the "Create Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "CreateEmptyTablesOperational.bat"
        elif training_var.get():
            bat_file_name = "CreateEmptyTablesTraining.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=21, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(21, PN, current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_regional)

    def create_empty_databases():
        run_with_progress(handle_create_empty_tables)


    def handle_delete_tables():
        global bat_num, bat_file_name

        """
        Handles the "Create Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "DeleteDatabasesOperational.bat"
        elif training_var.get():
            bat_file_name = "DeleteDatabasesTraining.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=21, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(21, PN, current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_regional)

    def delete_databases():
        run_with_progress(handle_delete_tables)

    def handle_import_tables():
        global bat_file_name

        """
        Handles the "Import Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "CreateTablesOperationalFBE.bat"
        elif training_var.get():
            bat_file_name = "CreateTablesTrainingFBE.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=21, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)


        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(21, PN,current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_regional)


    def import_tables():
        run_with_progress(handle_import_tables)

    # Buttons on the right
    button_x = 210
    button_width = 170
    button_height = 40
    y_start = 50
    y_gap = 60

    tk.Button(
        database_window_regional, text="Create Tables", font=("Arial", 12), bg="#663399", fg="white",
        activebackground="#4c2f66", command=create_empty_databases
    ).place(x=button_x, y=y_start, width=button_width, height=button_height)
    tk.Button(
        database_window_regional, text="Delete Tables", font=("Arial", 12), bg="#663399", fg="white",
        activebackground="#4c2f66", command=yes_no_keep_delete
    ).place(x=button_x, y=y_start + y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_regional, text="Import Tables", font=("Arial", 12), bg="#663399", fg="white",
        activebackground="#4c2f66", command=import_tables
    ).place(x=button_x, y=y_start + 2 * y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_regional, text="Close", font=("Arial", 12), bg="#A9A9A9", fg="black",
        activebackground="#F5F5DC", command=on_close
    ).place(x=162, y=460, width=80, height=30)

    # Close button in the middle at the bottom


    # Results Display
    results_text = tk.Text(database_window_regional, height=5, width=50, bg="#4c2f66", fg="white", font=("Arial", 10))
    results_text.place(x=20, y=330, width=360, height=120)

# Database Battery windows and functions

def set_server_Battery(choice):
    """Stores the server choice and moves to the next screen"""
    global selection_window_db_battery, server_choice
    server_choice = choice  # Store choice if needed
    if selection_window_db_battery:
        selection_window_db_battery.destroy()  # Destroy the first popup
    open_battery_database_window()  # Open the next screen

def selection_db_window_battery():
    global set_server, set_server_Battery, selection_window_db_battery
    # Create the first popup for server selection
    selection_window_db_battery = tk.Toplevel()
    selection_window_db_battery.title("Select DB")
    selection_window_db_battery.geometry("250x250")
    selection_window_db_battery.configure(bg="#2C3E50")
    selection_window_db_battery.resizable(False, False)
    selection_window_db_battery.iconbitmap(temp_icon_path)
    # selection_window.protocol("WM_DELETE_WINDOW",
    #                           lambda: messagebox.showerror("Error", "You must select a server!"))

    # Header label
    tk.Label(selection_window_db_battery, text="Choose DB Server", font=("Arial", 16, "bold"), fg="white", bg="#2C3E50").pack(
        pady=15)

    # Buttons
    btn1 = tk.Button(selection_window_db_battery, text="DB01", font=("Arial", 14, "bold"), fg="white", bg="#2196F3",
                     padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0,
                     command=lambda: set_server_Battery(1))
    btn1.pack(pady=10)

    btn2 = tk.Button(selection_window_db_battery, text="DB02", font=("Arial", 14, "bold"), fg="white", bg="#2196F3",
                     padx=20, pady=10, relief="flat", borderwidth=3, highlightthickness=0,
                     command=lambda: set_server_Battery(2))
    btn2.pack(pady=10)

def open_battery_database_window():
    global BN
    # Define parameters based on the server choice
    database_window_battery = tk.Toplevel()
    database_window_battery.title("Table Management")
    database_window_battery.geometry("400x500")
    database_window_battery.resizable(False, False)
    database_window_battery.configure(bg="#004d4d")
    database_window_battery.iconbitmap(temp_icon_path)

    if server_choice == 1:
        PN = 3
    else:
        PN = 4
    print(server_choice)
    print(PN)


    # Title Label
    title_label = tk.Label(
        database_window_battery, text=f"Database Battery {BN} DB0{server_choice}", font=("Arial", 14, "bold"), fg="white", bg="#004d4d"
    )
    title_label.place(x=80, y=5)

    # Checkbox Variables
    operational_var = tk.BooleanVar()
    training_var = tk.BooleanVar()

    tk.Checkbutton(
        database_window_battery, text="Operational", variable=operational_var,
        bg="#004d4d", fg="white", selectcolor="#004d4d", font=("Arial", 12)
    ).place(x=20, y=50)

    tk.Checkbutton(
        database_window_battery, text="Training", variable=training_var,
        bg="#004d4d", fg="white", selectcolor="#004d4d", font=("Arial", 12)
    ).place(x=20, y=90)

    def on_close():
        database_window_battery.destroy()  # Close the window

    def yes_no_keep_delete():
        response = messagebox.askyesno("Delete tables", "Are you sure you want to delete DB tables?", parent=database_window_battery)
        if response:
            handle_delete_tables()
        else:
            return

    # Progress Bar
    progress_bar_db = ttk.Progressbar(database_window_battery, orient="horizontal", mode="indeterminate", length=360)
    progress_bar_db.place(x=60, y=290, width=280, height=20)

    def start_progress():
        progress_bar_db.start(10)  # Starts animation with 10ms step

    def stop_progress():
        progress_bar_db.stop()  # Stops the animation

    # Wrap the existing functions with progress updates
    def run_with_progress(target_function):
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.", parent=database_window_battery)
            return
        def wrapper():
            start_progress()
            target_function()
            stop_progress()
        threading.Thread(target=wrapper).start()


    def handle_create_empty_tables():
        global BN, bat_file_name

        """
        Handles the "Create Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "CreateEmptyTablesOperational.bat"
        elif training_var.get():
            bat_file_name = "CreateEmptyTablesTraining.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, PN, current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_battery)

    def create_empty_databases():
        run_with_progress(handle_create_empty_tables)


    def handle_delete_tables():
        global BN, bat_file_name

        """
        Handles the "Create Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "DeleteDatabasesOperational.bat"
        elif training_var.get():
            bat_file_name = "DeleteDatabasesTraining.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, PN, current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_battery)

    def delete_databases():
        run_with_progress(handle_delete_tables)

    def handle_import_tables():
        global BN, bat_file_name

        """
        Handles the "Import Tables" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "CreateTablesOperationalFBE.bat"
        elif training_var.get():
            bat_file_name = "CreateTablesTrainingFBE.bat"
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name, results_text=results_text)


        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, PN,current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_battery)


    def import_tables():
        run_with_progress(handle_import_tables)

    def handle_adding_launchers():
        global BN, bat_file_name

        """
        Handles the "Adding launchers" button click.
        - Checks if either checkbox is selected.
        - Writes the BAT file.
        - Calls function to transfer & execute remotely.
        """
        if operational_var.get():
            bat_file_name = "AddingLaunchersOperationalFBE.bat"
            sql_file_name = "adding_launcher_operational_mode.sql"
        elif training_var.get():
            bat_file_name = "AddingLaunchersTrainingFBE.bat"
            sql_file_name = "adding_launcher_training_mode.sql"
            sql_code = generate_sql_script_training_launchers(BN)

            # Write it to a file
            with open(f"Scripts/SQL/adding_launcher_training_mode.sql", "w") as file:
                file.write(sql_code)
        else:
            print("No mode selected.")
            return

        # Step 1: Write BAT File
        write_bat_file_db_phase(BN=BN, PN=PN, BAT_FILE_NAME=bat_file_name,
                                results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_adding_launchers_battery(bat_num=BN,pos_num=PN, current_sql_file=sql_file_name, current_bat_file=bat_file_name, results_text=results_text, parent_window=database_window_battery)

    def adding_launchers():
        run_with_progress(handle_adding_launchers)

    # Buttons on the right
    button_x = 210
    button_width = 170
    button_height = 40
    y_start = 50
    y_gap = 60

    tk.Button(
        database_window_battery, text="Create Tables", font=("Arial", 12), bg="#006666", fg="white",
        activebackground="#008080", command=create_empty_databases
    ).place(x=button_x, y=y_start, width=button_width, height=button_height)
    tk.Button(
        database_window_battery, text="Delete Tables", font=("Arial", 12), bg="#006666", fg="white",
        activebackground="#008080", command=yes_no_keep_delete
    ).place(x=button_x, y=y_start + y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_battery, text="Import Tables", font=("Arial", 12), bg="#006666", fg="white",
        activebackground="#008080", command=import_tables
    ).place(x=button_x, y=y_start + 2 * y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_battery, text="Adding Launchers", font=("Arial", 12), bg="#006666", fg="white",
        activebackground="#008080", command=adding_launchers
    ).place(x=button_x, y=y_start + 3 * y_gap, width=button_width, height=button_height)

    tk.Button(
        database_window_battery, text="Close", font=("Arial", 12), bg="#800000", fg="white",
        activebackground="#990000", command=on_close
    ).place(x=162, y=460, width=80, height=30)

    # Close button in the middle at the bottom


    # Results Display
    results_text = tk.Text(database_window_battery, height=5, width=50, bg="#003333", fg="white", font=("Arial", 10))
    results_text.place(x=20, y=330, width=360, height=120)

# Function to open a new window for the App Installation
def open_vsil_window():
    vsil_window = tk.Toplevel(root)
    vsil_window.title("Remote App Installation - VSIL/CIWS")
    vsil_window.geometry("1000x900")
    vsil_window.resizable(False, False)
    vsil_window.configure(bg="#872657")  # Dark teal background
    vsil_window.iconbitmap(temp_icon_path)

    global progress_bar_ping
    global progress_bar_permissions
    global progress_bar_disk
    global progress_bar_version

    def on_close():
        global progress_bar_ping, progress_bar_permissions, progress_bar_disk, progress_bar_version
        # Reset the progress bar variable
        progress_bar_ping = None
        progress_bar_permissions = None
        progress_bar_disk = None
        progress_bar_version = None  # Global variable for the version check progress bar
        vsil_window.destroy()  # Close the window

    vsil_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hostnames and IPs
    default_hostnames_VSIL = {
        "BMC1": "192.168.1.1",
        "BMC2": "10.11.28.1",
        "BMC3": "10.11.38.1",
        "BMC4": "10.11.48.1",
        "ICS1": "10.12.18.13",
        "ICS2": "10.12.28.13",
        "ICS3": "10.12.38.13",
        "ICS4": "10.12.48.13",
        "DB-BAT": "10.11.18.3",
        "CBMC": "10.11.218.1",
        "DB-CBMC": "10.11.218.3",
        "TCS-Server": "10.11.18.2",
        "TCS-Client": "10.11.218.11",
        "CBMC-Client": "10.11.218.50",
        "AD-BAT": "10.11.13.20",
        "AD-CBMC": "10.11.213.20",
        "AV-BAT": "10.11.13.22",
        "AV-CBMC": "10.11.213.22",
    }

    hostnames_file_path_VSIL = ".\\Config\\hostnamesVSIL.json"

    if os.path.exists(hostnames_file_path_VSIL):
        # If the JSON file exists, read hostnames from it
        with open(hostnames_file_path_VSIL, 'r') as file:
            hostnames = json.load(file)
        print("Loaded hostnames from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        hostnames = default_hostnames_VSIL
        print("Loaded hostnames from default dictionary.")


    # Map host to corresponding bat file paths
    default_VSIL_bat_file_mapping = {
        "BMC1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\BMCServer.bat",
        "BMC2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\BMCServer.bat",
        "BMC3": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\BMCServer.bat",
        "BMC4": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\BMCServer.bat",
        "ICS1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\ICS.bat",
        "ICS2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\ICS.bat",
        "ICS3": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\ICS.bat",
        "ICS4": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\BMC\\ICS.bat",
        "DB-BAT": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\DB\\DBServer.bat",
        "CBMC": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\CBMC\\CBMCServer.bat",
        "DB-CBMC": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\DB\\DBServer.bat",
        "TCS-Server": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\TCS\\TCSServer.bat",
        "TCS-Client": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\TCS\\TCSClient.bat",
        "CBMC-Client": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\CBMC\\CBMCClient.bat",
        "AD-BAT": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\GeneralServer\\ADServer.bat",
        "AD-CBMC": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\GeneralServer\\ADServer.bat",
        "AV-BAT": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\GeneralServer\\AVServer.bat",
        "AV-CBMC": ".\\Scripts\\AppInstallation\\RemoteInstallation\\VSIL\\GeneralServer\\AVServer.bat",
    }

    bat_file_VSIL_file_mapping = ".\\Config\\batFileMappingVSIL.json"

    if os.path.exists(bat_file_VSIL_file_mapping):
        # If the JSON file exists, read hostnames from it
        with open(bat_file_VSIL_file_mapping, 'r') as file:
            VSIL_file_mapping = json.load(file)
        print("Loaded Bat file mapping from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        VSIL_file_mapping = default_VSIL_bat_file_mapping
        print("Loaded Bat file mapping from default dictionary.")

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Define the JSON file name
    json_file = "Config\\site.json"

    # Check if file exists
    if not os.path.exists(json_file):
        print("config.json file doesn't exist. Loading from default.")
        site = "VSIL"
    else:
        # Load JSON data
        with open(json_file, "r") as file:
            data = json.load(file)
        site = data.get("site")

    # Title Label
    title_label = tk.Label(vsil_window, text=f"Remote App Installation - {site}", font=("Arial", 20, "bold"), fg="white",
                           bg="#872657")
    title_label.place(x=270, y=10)

    # Create a scrollable frame for hostnames
    scroll_frame = tk.Frame(vsil_window, bg="#872657")
    scroll_frame.place(x=10, y=70, width=900, height=600)  # Ensure the frame starts at the correct position

    canvas = tk.Canvas(scroll_frame, bg="#872657", highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    host_frame = tk.Frame(canvas, bg="#872657")  # This will contain the hostnames and checkboxes

    # Configure the canvas and scrollbar
    host_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=host_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    scrollbar.pack(side="left", fill="y")  # Place the scrollbar on the left
    canvas.pack(side="right", fill="both", expand=True)  # Place the canvas to the right of the scrollbar

    def on_install():

        # Add progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(vsil_window, variable=progress_var, maximum=100)
        progress_bar.place(x=580, y=615, width=300, anchor="center")  # Centered horizontally with a width of 400px

        # Add percentage label
        progress_label = tk.Label(vsil_window, text="0%", font=("Arial", 14), fg="white", bg="#004d4d")
        progress_label.place(x=586, y=650, anchor="center")  # Positioned below the progress bar
        """
        Start the installation process for all selected hosts.
        """

        def install_task():
            global VSIL_BN
            logs = []  # Shared list to collect logs

            # Reset progress bar and results display
            progress_var.set(0)
            progress_label.config(text="0%")
            results_text.delete("1.0", tk.END)

            selected_hosts = [host for host, var in selections.items() if var.get()]
            if not selected_hosts:
                messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=vsil_window)
                return

            total_hosts = len(selected_hosts)
            steps_per_host = 5  # Number of steps per host (customize, copy script, copy zip, copy tools, execute)
            total_steps = total_hosts * steps_per_host
            step_increment = 100 / total_steps  # Progress increment per step

            for host in selected_hosts:
                ip = hostnames[host]
                try:
                    # Extract details for the host
                    fourth_octet = ip.split(".")[-1]
                    PN = fourth_octet
                    bat_file_path = VSIL_file_mapping.get(host)
                    print(bat_file_path)

                    if "AD-CBMC" in hostnames or "CBMC" in hostnames or "CBMC-Client" in hostnames or "DB-CBMC" in hostnames or "TCS-Client" in hostnames:
                        VSIL_BN = 21
                    else:
                        VSIL_BN = ip.split('.')[2][0]

                    # Create a unique temporary .bat file for the host

                    if "BMC1" in host or "BMC2" in host or "BMC3" in host or "BMC4" in host:
                        temp_bat_path = f".\\temp\\BMCServer_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"BMCServer_{VSIL_BN}_{PN}.bat"
                    elif "ICS1" in host or "ICS2" in host or "ICS3" in host or "ICS4" in host:
                        temp_bat_path = f".\\temp\\ICS_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"ICS_{VSIL_BN}_{PN}.bat"
                    elif "DB-BAT" in host or "DB-CBMC" in host:
                        temp_bat_path = f".\\temp\\DBServer_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"DBServer_{VSIL_BN}_{PN}.bat"
                    elif "TCS-Server" in host:
                        temp_bat_path = f".\\temp\\TCSServer_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"TCSServer_{VSIL_BN}_{PN}.bat"
                    elif "TCS-Client" in host:
                        temp_bat_path = f".\\temp\\TCSClient_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"TCSClient_{VSIL_BN}_{PN}.bat"
                    elif "AD-BAT" in host or "AD-CBMC" in host:
                        temp_bat_path = f".\\temp\\ADServer_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"ADServer_{VSIL_BN}_{PN}.bat"
                    elif "AV-BAT" in host or "AV-CBMC" in host:
                        temp_bat_path = f".\\temp\\AVServer_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"AVServer_{VSIL_BN}_{PN}.bat"
                    elif "CBMC-Client" in host:
                        temp_bat_path = f".\\temp\\CBMCClient_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"CBMCClient_{VSIL_BN}_{PN}.bat"
                    else:
                        temp_bat_path = f".\\temp\\CBMCServer_{VSIL_BN}_{PN}.bat"
                        name_bat_file = f"CBMCServer_{VSIL_BN}_{PN}.bat"

                    # Step 1: Customize the .bat file
                    logs.append(f"Customizing batch file for {host} ({ip})...")
                    change_bat_pos_function(
                        bat_file_path, BN=VSIL_BN, PN=PN, output_path=temp_bat_path, logs=logs
                    )
                    progress_var.set(progress_var.get() + step_increment)
                    progress_label.config(text=f"{int(progress_var.get())}%")
                    display_results(logs)

                    # Step 2-5: Transfer files and execute
                    logs.append(f"Starting installation process for {host} ({ip})...")
                    prepare_installation_battery(
                        ip_base=ip,
                        host_type=host,
                        current_bat_file=name_bat_file,
                        scripts_src=temp_bat_path,
                        logs=logs,
                        progress_var=progress_var,
                        progress_label=progress_label,
                        step_increment=step_increment,
                    )
                    logs.append(f"Installation completed for {host} ({ip}).")
                    display_results(logs)

                except Exception as e:
                    logs.append(f"Error during installation for {host} ({ip}): {e}")
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}", parent=vsil_window)
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.", parent=vsil_window)

            display_results(logs)

        threading.Thread(target=install_task).start()

    for host, ip in hostnames.items():
        # Create a frame for the checkbox and label
        item_frame = tk.Frame(host_frame, bg="#872657")  # Matches the background color

        # Add the checkbox
        tk.Checkbutton(
            item_frame,
            variable=selections[host],
            bg="#872657",
            fg="white",
            selectcolor="#872657",
            anchor="w"
        ).pack(side="left", padx=2)  # Pack the checkbox to the left with padding

        # Add the label
        labels[host] = tk.Label(
            item_frame,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#872657",
            anchor="w"
        )
        labels[host].pack(side="left", padx=4)  # Pack the label to the right of the checkbox with spacing

        # Pack the row into the scrollable host frame
        item_frame.pack(fill="x", pady=12)  # Add vertical space between rows

    # Functions for Check All and Uncheck All
    def mark_all():
        for var in selections.values():
            var.set(True)

    def unmark_all():
        for var in selections.values():
            var.set(False)

    # Buttons on the right
    button_x = 760
    button_width = 200
    tk.Button(
        vsil_window,
        text="Mark All",
        command=mark_all,
        font=("Arial", 14),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Unmark All",
        command=unmark_all,
        font=("Arial", 14),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=170, width=button_width, height=50)

    # Results Display
    results_text = tk.Text(vsil_window, height=10, width=60, bg="#65000B", fg="white", font=("Arial", 12))
    results_text.place(x=50, y=700, width=700, height=150)

    def display_results(results):
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "\n".join(results))

    def perform_version_check():
        global progress_bar_version
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=vsil_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_version is None:
            progress_bar_version = ttk.Progressbar(
                vsil_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_version.place(x=580, y=255, width=150, height=20)

        progress_bar_version.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]

                    # Determine the file path based on the host type
                    if host.startswith("DB"):
                        file_path = r"c$\mDRS\Server\mPrest.mDRS.dll"
                    else:
                        file_path = r"c$\VSIL\Watchdog\WDService\mPrest.IronDome.Watchdog.Service.dll"

                    # Call the version checker
                    version_info = get_remote_file_version(ip, file_path)

                    if "error" in version_info:
                        labels[host].config(fg="red")
                        logs.append(f"{host} (IP: {ip}): Version check failed - {version_info['error']}")
                    else:
                        product_version = version_info.get("Product Version", "Unknown")
                        labels[host].config(fg="green", text=f"{host} (IP: {ip}) - Version: {product_version}")
                        logs.append(f"{host} (IP: {ip}): Version: {product_version}")

            # Stop the progress bar and display results
            vsil_window.after(0, lambda: progress_bar_version.stop())
            vsil_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_communication_test():
        global progress_bar_ping
        logs = []  # Collect logs here

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=vsil_window)
            return

        # Create and show the progress bar the first time the button is pressed
        if progress_bar_ping is None:
            progress_bar_ping = ttk.Progressbar(
                vsil_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_ping.place(x=580, y=325, width=150, height=20)

        progress_bar_ping.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    success = check_communication(ip)
                    if success:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Communication successful.")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) C")
                        logs.append(f"{host} (IP: {ip}): Communication failed.")

            # Stop the progress bar after the test completes
            vsil_window.after(0, lambda: progress_bar_ping.stop())
            vsil_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_permission_test():
        global progress_bar_permissions
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=vsil_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_permissions is None:
            progress_bar_permissions = ttk.Progressbar(
                vsil_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_permissions.place(x=580, y=395, width=150, height=20)

        progress_bar_permissions.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    network_path = rf"\\{ip}\c$\temp"  # Adjust the network path format
                    permissions = check_permissions(network_path)  # Call the helper function

                    # Update GUI based on results
                    if permissions["readable"] and permissions["writable"]:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Permissions OK (Read/Write).")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) P")
                        logs.append(f"{host} (IP: {ip}): Permissions FAILED.")

            # Stop the progress bar and display results
            vsil_window.after(0, lambda: progress_bar_permissions.stop())
            vsil_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_disk_volume_test():
        global progress_bar_disk
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=vsil_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_disk is None:
            progress_bar_disk = ttk.Progressbar(
                vsil_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_disk.place(x=580, y=465, width=150, height=20)

        progress_bar_disk.start(10)  # Start the progress bar

        def run_test():
            pythoncom.CoInitialize()  # Initialize COM library for WMI
            try:
                for host, var in selections.items():
                    if var.get():
                        ip = hostnames[host]
                        free_space, total_space, percentage_free = get_drive_space(ip)

                        if free_space is None or total_space is None:
                            labels[host].config(fg="red")
                            logs.append(f"{host} (IP: {ip}): Failed to retrieve disk space information.")
                        elif free_space < 50:
                            labels[host].config(fg="red")
                            labels[host].config(text=f"{host} (IP: {ip}) D")
                            logs.append(
                                f"{host} (IP: {ip}): C Drive Disk space is {free_space:.2f}GB. Cannot install, please empty the disk."
                            )
                        else:
                            labels[host].config(fg="green")
                            logs.append(
                                f"{host} (IP: {ip}): Free space in C Drive is {free_space:.2f}GB. Disk space is sufficient."
                            )
                            logs.append(
                                f"Free space: {free_space:.2f}GB, Total space: {total_space:.2f}GB, Percentage free: {percentage_free:.2f}%.")
            finally:
                pythoncom.CoUninitialize()  # Uninitialize COM library

            # Stop the progress bar and display results
            vsil_window.after(0, lambda: progress_bar_disk.stop())
            vsil_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    # Buttons

    # 003d3d

    tk.Button(
        vsil_window,
        text="Get Version",
        command=perform_version_check,
        font=("Arial", 14),
        bg="#65000B",
        fg="white",
        activebackground="#65000B"
    ).place(x=button_x, y=240, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Communication Test",
        command=perform_communication_test,
        font=("Arial", 14),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=310, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Permission Test",
        command=perform_permission_test,
        font=("Arial", 14),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=380, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Disk Volume Test",
        command=perform_disk_volume_test,
        font=("Arial", 14),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=450, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Install App",
        command=on_install,
        font=("Arial", 14, 'bold'),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=590, width=button_width, height=50)

    # Close button in the middle at the bottom
    tk.Button(
        vsil_window,
        text="Close",
        command=on_close,
        font=("Arial", 14),
        bg="#673147",
        fg="white",
        activebackground="#A91B60"
    ).place(x=450, y=855, width=100, height=40)


def open_simulator_window():
    simulator_window = tk.Toplevel(root)
    simulator_window.title("Remote App Installation - Simulator mPrest")
    simulator_window.geometry("1000x900")
    simulator_window.resizable(False, False)
    simulator_window.configure(bg="#228B22")  # Dark teal background
    simulator_window.iconbitmap(temp_icon_path)

    global progress_bar_ping
    global progress_bar_permissions

    def on_close():
        global progress_bar_ping, progress_bar_permissions, progress_bar_disk, progress_bar_version
        # Reset the progress bar variable
        progress_bar_ping = None
        progress_bar_permissions = None
        progress_bar_disk = None
        progress_bar_version = None
        simulator_window.destroy()  # Close the window

    simulator_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hostnames and IPs
    default_hostnames_simulator = {
        "Sim Server": f"10.11.{BN}8.2",
        "Client1": f"192.168.{BN}8.6",
        "Client2": f"192.168.{BN}8.7",
        "Client3": f"192.168.{BN}8.8",
        "Client4": f"192.168.{BN}8.9",
        "Client5": f"192.168.{BN}8.10",
    }

    hostnames_file_path = ".\\Config\\hostnameSimulator.json."

    if os.path.exists(hostnames_file_path):
        # If the JSON file exists, read hostnames from it
        with open(hostnames_file_path, 'r') as file:
            hostnames = json.load(file)
        print("Loaded hostnames from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        hostnames = default_hostnames_simulator
        print("Loaded hostnames from default dictionary.")



    default_sim_file_mapping = {
        "Sim Server": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorServer.bat",
        "Client1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client3": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client4": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client5": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",

    }

    bat_file_sim_file_mapping = ".\\Config\\batFileMappingSimulator.json"

    if os.path.exists(bat_file_sim_file_mapping):
        # If the JSON file exists, read hostnames from it
        with open(bat_file_sim_file_mapping, 'r') as file:
            sim_file_mapping = json.load(file)
        print("Loaded Bat file mapping from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        sim_file_mapping = default_sim_file_mapping
        print("Loaded Bat file mapping from default dictionary.")


    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(simulator_window, text=f"Remote App Installation - Simulator", font=("Arial", 20, "bold"),
                           fg="white", bg="#228B22")
    title_label.place(x=270, y=10)

    def on_install():

        # Add progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(simulator_window, variable=progress_var, maximum=100)
        progress_bar.place(x=580, y=615, width=300, anchor="center")  # Centered horizontally with a width of 400px

        # Add percentage label
        progress_label = tk.Label(simulator_window, text="0%", font=("Arial", 14), fg="white", bg="#228B22")
        progress_label.place(x=586, y=650, anchor="center")  # Positioned below the progress bar
        """
        Start the installation process for all selected hosts.
        """

        def install_task():
            logs = []  # Shared list to collect logs

            # Reset progress bar and results display
            progress_var.set(0)
            progress_label.config(text="0%")
            results_text.delete("1.0", tk.END)

            selected_hosts = [host for host, var in selections.items() if var.get()]
            if not selected_hosts:
                messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=simulator_window)
                return

            total_hosts = len(selected_hosts)
            steps_per_host = 5  # Number of steps per host (customize, copy script, copy zip, copy tools, execute)
            total_steps = total_hosts * steps_per_host
            step_increment = 100 / total_steps  # Progress increment per step

            for host in selected_hosts:
                ip = hostnames[host]
                try:
                    # Extract details for the host
                    fourth_octet = ip.split(".")[-1]
                    third_octets = ip.split('.')[2][0]
                    logs.append(f"{fourth_octet}-{third_octets}")
                    PN = fourth_octet
                    bat_file_path = sim_file_mapping.get(host)
                    print(bat_file_path)

                    # Create a unique temporary .bat file for the host

                    if "BMC" in host:
                        temp_bat_path = f".\\temp\\BatteryServer_{PN}.bat"
                        name_bat_file = f"BatteryServer_{PN}.bat"
                    elif "ICS" in host:
                        temp_bat_path = f".\\temp\\ICS_{PN}.bat"
                        name_bat_file = f"ICS_{PN}.bat"
                    elif "DB" in host:
                        temp_bat_path = f".\\temp\\mDRS_{PN}.bat"
                        name_bat_file = f"mDRS_{PN}.bat"
                    else:
                        temp_bat_path = f".\\temp\\BatteryClient_{PN}.bat"
                        name_bat_file = f"BatteryClient_{PN}.bat"

                    # Step 1: Customize the .bat file
                    logs.append(f"Customizing batch file for {host} ({ip})...")
                    change_bat_pos_function(
                        bat_file_path, BN=BN, PN=PN, output_path=temp_bat_path, logs=logs
                    )
                    progress_var.set(progress_var.get() + step_increment)
                    progress_label.config(text=f"{int(progress_var.get())}%")
                    display_results(logs)

                    # Step 2-5: Transfer files and execute
                    logs.append(f"Starting installation process for {host} ({ip})...")
                    prepare_installation_simulator(
                        ip_base=ip,
                        host_type=host,
                        current_bat_file=name_bat_file,
                        scripts_src=temp_bat_path,
                        logs=logs,
                        progress_var=progress_var,
                        progress_label=progress_label,
                        step_increment=step_increment,
                    )
                    logs.append(f"Installation completed for {host} ({ip}).")
                    display_results(logs)

                except Exception as e:
                    logs.append(f"Error during installation for {host} ({ip}): {e}")
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}", parent=simulator_window)
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.", parent=simulator_window)

            display_results(logs)

        threading.Thread(target=install_task).start()

    # Hostnames Section
    y_offset = 98
    for host, ip in hostnames.items():
        label = tk.Label(
            simulator_window,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#228B22",
            anchor="w"
        )
        label.place(x=80, y=y_offset)
        labels[host] = label

        tk.Checkbutton(
            simulator_window,
            variable=selections[host],
            bg="#228B22",
            fg="white",
            selectcolor="#228B22",
            anchor="w"
        ).place(x=50, y=y_offset + 2)
        y_offset += 50

    # Functions for Check All and Uncheck All
    def check_all():
        for var in selections.values():
            var.set(True)

    def uncheck_all():
        for var in selections.values():
            var.set(False)

    # Buttons on the right
    button_x = 760
    button_width = 200
    tk.Button(
        simulator_window,
        text="Check All",
        command=check_all,
        font=("Arial", 14),
        bg="#32CD32",
        fg="white",
        activebackground="#6B8E23"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        simulator_window,
        text="Uncheck All",
        command=uncheck_all,
        font=("Arial", 14),
        bg="#32CD32",
        fg="white",
        activebackground="#32CD32"
    ).place(x=button_x, y=170, width=button_width, height=50)

    # Results Display
    results_text = tk.Text(simulator_window, height=10, width=60, bg="#013220", fg="white", font=("Arial", 12))
    results_text.place(x=50, y=700, width=700, height=150)

    def display_results(results):
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "\n".join(results))

    def perform_version_check():
        global progress_bar_version
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=simulator_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_version is None:
            progress_bar_version = ttk.Progressbar(
                simulator_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_version.place(x=580, y=255, width=150, height=20)

        progress_bar_version.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]

                    # Determine the file path based on the host type
                    ### need to change ###
                    if host.startswith("DB"):
                        file_path = r"c$\mDRS\Server\mPrest.mDRS.dll"
                    else:
                        file_path = r"c$\Firebolt\Watchdog\WDService\mPrest.IronDome.Watchdog.Service.dll"

                    # Call the version checker
                    version_info = get_remote_file_version(ip, file_path)

                    if "error" in version_info:
                        labels[host].config(fg="red")
                        logs.append(f"{host} (IP: {ip}): Version check failed - {version_info['error']}")
                    else:
                        product_version = version_info.get("Product Version", "Unknown")
                        labels[host].config(fg="green", text=f"{host} (IP: {ip}) - Version: {product_version}")
                        logs.append(f"{host} (IP: {ip}): Version: {product_version}")

            # Stop the progress bar and display results
            simulator_window.after(0, lambda: progress_bar_version.stop())
            simulator_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_communication_test():
        global progress_bar_ping
        logs = []  # Collect logs here

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=simulator_window)
            return

        # Create and show the progress bar the first time the button is pressed
        if progress_bar_ping is None:
            progress_bar_ping = ttk.Progressbar(
                simulator_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_ping.place(x=580, y=325, width=150, height=20)

        progress_bar_ping.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    success = check_communication(ip)
                    if success:
                        labels[host].config(fg="#013220")
                        logs.append(f"{host} (IP: {ip}): Communication successful.")
                    else:
                        labels[host].config(fg="#800020")
                        labels[host].config(text=f"{host} (IP: {ip}) C")
                        logs.append(f"{host} (IP: {ip}): Communication failed.")

            # Stop the progress bar after the test completes
            simulator_window.after(0, lambda: progress_bar_ping.stop())
            simulator_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_permission_test():
        global progress_bar_permissions
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=simulator_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_permissions is None:
            progress_bar_permissions = ttk.Progressbar(
                simulator_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_permissions.place(x=580, y=395, width=150, height=20)

        progress_bar_permissions.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    network_path = rf"\\{ip}\c$\temp"  # Adjust the network path format
                    permissions = check_permissions(network_path)  # Call the helper function

                    # Update GUI based on results
                    if permissions["readable"] and permissions["writable"]:
                        labels[host].config(fg="#013220")
                        logs.append(f"{host} (IP: {ip}): Permissions OK (Read/Write).")
                    else:
                        labels[host].config(fg="#800020")
                        labels[host].config(text=f"{host} (IP: {ip}) P")
                        logs.append(f"{host} (IP: {ip}): Permissions FAILED.")

            # Stop the progress bar and display results
            simulator_window.after(0, lambda: progress_bar_permissions.stop())
            simulator_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_disk_volume_test():
        global progress_bar_disk
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=simulator_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_disk is None:
            progress_bar_disk = ttk.Progressbar(
                simulator_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_disk.place(x=580, y=465, width=150, height=20)

        progress_bar_disk.start(10)  # Start the progress bar

        def run_test():
            pythoncom.CoInitialize()  # Initialize COM library for WMI
            try:
                for host, var in selections.items():
                    if var.get():
                        ip = hostnames[host]
                        free_space, total_space, percentage_free = get_drive_space(ip)
                        logs.append(f"free space:{free_space}, total space:{total_space}, percentage_free:{percentage_free}")

                        if free_space is None or total_space is None:
                            labels[host].config(fg="#013220")
                            logs.append(f"{host} (IP: {ip}): Failed to retrieve disk space information.")
                        elif percentage_free < 25:
                            labels[host].config(fg="#800020")
                            labels[host].config(text=f"{host} (IP: {ip}) D")
                            logs.append(
                                f"{host} (IP: {ip}): Disk volume is {percentage_free:.2f}%. Cannot install, please empty the disk."
                            )
                        else:
                            labels[host].config(fg="green")
                            logs.append(
                                f"{host} (IP: {ip}): Disk volume is {percentage_free:.2f}%. Disk space is sufficient."
                            )
            finally:
                pythoncom.CoUninitialize()  # Uninitialize COM library

            # Stop the progress bar and display results
            simulator_window.after(0, lambda: progress_bar_disk.stop())
            simulator_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    # Buttons

    tk.Button(
        simulator_window,
        text="Get Version",
        command=perform_version_check,
        font=("Arial", 14),
        bg="#013220",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=240, width=button_width, height=50)

    tk.Button(
        simulator_window,
        text="Communication Test",
        command=perform_communication_test,
        font=("Arial", 14),
        bg="#32CD32",
        fg="white",
        activebackground="#32CD32"
    ).place(x=button_x, y=310, width=button_width, height=50)

    tk.Button(
        simulator_window,
        text="Permission Test",
        command=perform_permission_test,
        font=("Arial", 14),
        bg="#32CD32",
        fg="white",
        activebackground="#32CD32"
    ).place(x=button_x, y=380, width=button_width, height=50)

    tk.Button(
        simulator_window,
        text="Disk Volume Test",
        command=perform_disk_volume_test,
        font=("Arial", 14),
        bg="#32CD32",
        fg="white",
        activebackground="#32CD32"
    ).place(x=button_x, y=450, width=button_width, height=50)

    tk.Button(
        simulator_window,
        text="Install App",
        command=on_install,
        font=("Arial", 14, 'bold'),
        bg="#32CD32",
        fg="white",
        activebackground="#32CD32"
    ).place(x=button_x, y=590, width=button_width, height=50)

    # Close button in the middle at the bottom
    tk.Button(
        simulator_window,
        text="Close",
        command=on_close,
        font=("Arial", 14),
        bg="#FFFDD0",
        fg="green",
        activebackground="#6B8E23"
    ).place(x=450, y=855, width=100, height=40)


def open_regional_window():
    regional_window = tk.Toplevel(root)
    regional_window.title("Remote App Installation - Regional")
    regional_window.geometry("1000x900")
    regional_window.resizable(False, False)
    regional_window.configure(bg="#663399")  # Dark teal background
    regional_window.iconbitmap(temp_icon_path)


    global progress_bar_ping
    global progress_bar_permissions

    def on_close():
        global progress_bar_ping, progress_bar_permissions, progress_bar_disk, progress_bar_version
        # Reset the progress bar variable
        progress_bar_ping = None
        progress_bar_permissions = None
        progress_bar_disk = None
        progress_bar_version = None
        regional_window.destroy()  # Close the window

    regional_window.protocol("WM_DELETE_WINDOW", on_close)

### We can save the hostnames in JSON file
    # Hostnames and IPs
    default_hostnames_regional = {
        "CBMC1": "192.168.218.1",
        "CBMC2": "192.168.218.2",
        "DB1": "192.168.218.3",
        "DB2": "192.168.218.4",
        "Client1": "192.168.218.50",
        "Client2": "192.168.218.51",
        "Client3": "192.168.218.52",
        "Client4": "192.168.218.53",
        "Client5": "192.168.218.54",
        "Client6": "192.168.218.55",
        "Client7": "192.168.218.56",
        "Client8": "192.168.3.141",
    }

    hostnames_file_path_regional = ".\\Config\\hostnameRegional.json"

    if os.path.exists(hostnames_file_path_regional):
        # If the JSON file exists, read hostnames from it
        with open(hostnames_file_path_regional, 'r') as file:
            hostnames = json.load(file)
        print("Loaded hostnames from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        hostnames = default_hostnames_regional
        print("Loaded hostnames from default dictionary.")

    # Map host to corresponding bat file paths
    default_reg_file_mapping = {
        "BMC1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalServer.bat",
        "BMC2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalServer.bat",
        "DB1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\DB\\mDRS.bat",
        "DB2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\DB\\mDRS.bat",
        "Client1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client3": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client4": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client5": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client6": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client7": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
        "Client8": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
    }

    bat_file_mapping_file_path = ".\\Config\\batFileMappingRegional.json"

    if os.path.exists(bat_file_mapping_file_path):
        # If the JSON file exists, read hostnames from it
        with open(bat_file_mapping_file_path, 'r') as file:
            reg_file_mapping = json.load(file)
        print("Loaded Bat file mapping from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        reg_file_mapping = default_reg_file_mapping
        print("Loaded Bat file mapping from default dictionary.")

    def on_install():

        # Add progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(regional_window, variable=progress_var, maximum=100)
        progress_bar.place(x=580, y=615, width=300, anchor="center")  # Centered horizontally with a width of 400px

        # Add percentage label
        progress_label = tk.Label(regional_window, text="0%", font=("Arial", 14), fg="white", bg="#663399")
        progress_label.place(x=586, y=650, anchor="center")  # Positioned below the progress bar
        """
        Start the installation process for all selected hosts.
        """

        def install_task():
            logs = []  # Shared list to collect logs

            # Reset progress bar and results display
            progress_var.set(0)
            progress_label.config(text="0%")
            results_text.delete("1.0", tk.END)

            selected_hosts = [host for host, var in selections.items() if var.get()]
            if not selected_hosts:
                messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=regional_window)
                return

            total_hosts = len(selected_hosts)
            steps_per_host = 5  # Number of steps per host (customize, copy script, copy zip, copy tools, execute)
            total_steps = total_hosts * steps_per_host
            step_increment = 100 / total_steps  # Progress increment per step

            for host in selected_hosts:
                ip = hostnames[host]
                try:
                    # Extract details for the host
                    fourth_octet = ip.split(".")[-1]
                    PN = fourth_octet
                    bat_file_path = reg_file_mapping.get(host)
                    print(bat_file_path)

                    # Create a unique temporary .bat file for the host

                    if "CBMC" in host:
                        temp_bat_path = f".\\temp\\RegionalServer_{PN}.bat"
                        name_bat_file = f"RegionalServer_{PN}.bat"
                    elif "DB" in host:
                        temp_bat_path = f".\\temp\\mDRS_{PN}.bat"
                        name_bat_file = f"mDRS_{PN}.bat"
                    else:
                        temp_bat_path = f".\\temp\\RegionalClient_{PN}.bat"
                        name_bat_file = f"RegionalClient_{PN}.bat"

                    # Step 1: Customize the .bat file
                    logs.append(f"Customizing batch file for {host} ({ip})...")
                    change_bat_pos_function(
                        bat_file_path, BN=21, PN=PN, output_path=temp_bat_path, logs=logs
                    )
                    progress_var.set(progress_var.get() + step_increment)
                    progress_label.config(text=f"{int(progress_var.get())}%")
                    display_results(logs)

                    # Step 2-5: Transfer files and execute
                    logs.append(f"Starting installation process for {host} ({ip})...")
                    prepare_installation_regional(
                        ip_base=ip,
                        host_type=host,
                        current_bat_file=name_bat_file,
                        scripts_src=temp_bat_path,
                        logs=logs,
                        progress_var=progress_var,
                        progress_label=progress_label,
                        step_increment=step_increment,
                    )
                    logs.append(f"Installation completed for {host} ({ip}).")
                    display_results(logs)

                except Exception as e:
                    logs.append(f"Error during installation for {host} ({ip}): {e}")
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}", parent=regional_window)
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.", parent=regional_window)

            display_results(logs)

        threading.Thread(target=install_task).start()


    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(regional_window, text=f"Remote App Installation - Regional", font=("Arial", 20, "bold"),
                           fg="white", bg="#663399")
    title_label.place(x=280, y=10)

    # Hostnames Section
    y_offset = 98
    for host, ip in hostnames.items():
        label = tk.Label(
            regional_window,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#663399",
            anchor="w"
        )
        label.place(x=80, y=y_offset)
        labels[host] = label

        tk.Checkbutton(
            regional_window,
            variable=selections[host],
            bg="#663399",
            fg="white",
            selectcolor="#663399",
            anchor="w"
        ).place(x=50, y=y_offset + 2)
        y_offset += 50

    # Functions for Check All and Uncheck All
    def check_all():
        for var in selections.values():
            var.set(True)

    def uncheck_all():
        for var in selections.values():
            var.set(False)

    # Buttons on the right
    button_x = 760
    button_width = 200
    tk.Button(
        regional_window,
        text="Check All",
        command=check_all,
        font=("Arial", 14),
        bg="#5a2c8a",
        fg="white",
        activebackground="#4c2f66"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        regional_window,
        text="Uncheck All",
        command=uncheck_all,
        font=("Arial", 14),
        bg="#5a2c8a",
        fg="white",
        activebackground="#4c2f66"
    ).place(x=button_x, y=170, width=button_width, height=50)

    def perform_test(test_function):
        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=regional_window)
            return
        results = [test_function(host, hostnames[host]) for host in selected_hosts]
        display_results(results)

    # Results Display
    results_text = tk.Text(regional_window, height=10, width=60, bg="#4c2f66", fg="white", font=("Arial", 12))
    results_text.place(x=50, y=700, width=700, height=150)

    def display_results(results):
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "\n".join(results))

    def perform_version_check():
        global progress_bar_version
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=regional_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_version is None:
            progress_bar_version = ttk.Progressbar(
                regional_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_version.place(x=580, y=255, width=150, height=20)

        progress_bar_version.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]

                    # Determine the file path based on the host type
                    if host.startswith("DB"):
                        file_path = r"c$\mDRS\Server\mPrest.mDRS.dll"
                    else:
                        file_path = r"c$\Firebolt\Watchdog\WDService\mPrest.IronDome.Watchdog.Service.dll"

                    # Call the version checker
                    version_info = get_remote_file_version(ip, file_path)

                    if "error" in version_info:
                        labels[host].config(fg="red")
                        logs.append(f"{host} (IP: {ip}): Version check failed - {version_info['error']}")
                    else:
                        product_version = version_info.get("Product Version", "Unknown")
                        labels[host].config(fg="green", text=f"{host} (IP: {ip}) - Version: {product_version}")
                        logs.append(f"{host} (IP: {ip}): Version: {product_version}")

            # Stop the progress bar and display results
            regional_window.after(0, lambda: progress_bar_version.stop())
            regional_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_communication_test():
        global progress_bar_ping
        logs = []  # Collect logs here

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=regional_window)
            return

        # Create and show the progress bar the first time the button is pressed
        if progress_bar_ping is None:
            progress_bar_ping = ttk.Progressbar(
                regional_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_ping.place(x=580, y=325, width=150, height=20)

        progress_bar_ping.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    success = check_communication(ip)
                    if success:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Communication successful.")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) C")
                        logs.append(f"{host} (IP: {ip}): Communication failed.")

            # Stop the progress bar after the test completes
            regional_window.after(0, lambda: progress_bar_ping.stop())
            regional_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_permission_test():
        global progress_bar_permissions
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=regional_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_permissions is None:
            progress_bar_permissions = ttk.Progressbar(
                regional_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_permissions.place(x=580, y=395, width=150, height=20)

        progress_bar_permissions.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    network_path = rf"\\{ip}\c$\temp"  # Adjust the network path format
                    permissions = check_permissions(network_path)  # Call the helper function

                    # Update GUI based on results
                    if permissions["readable"] and permissions["writable"]:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Permissions OK (Read/Write).")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) P")
                        logs.append(f"{host} (IP: {ip}): Permissions FAILED.")

            # Stop the progress bar and display results
            regional_window.after(0, lambda: progress_bar_permissions.stop())
            regional_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_disk_volume_test():
        global progress_bar_disk
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=regional_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_disk is None:
            progress_bar_disk = ttk.Progressbar(
                regional_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_disk.place(x=580, y=465, width=150, height=20)

        progress_bar_disk.start(10)  # Start the progress bar

        def run_test():
            pythoncom.CoInitialize()  # Initialize COM library for WMI
            try:
                for host, var in selections.items():
                    if var.get():
                        ip = hostnames[host]
                        free_space, total_space, percentage_free = get_drive_space(ip)

                        if free_space is None or total_space is None:
                            labels[host].config(fg="red")
                            logs.append(f"{host} (IP: {ip}): Failed to retrieve disk space information.")
                        elif percentage_free < 25:
                            labels[host].config(fg="red")
                            labels[host].config(text=f"{host} (IP: {ip}) D")
                            logs.append(
                                f"{host} (IP: {ip}): Disk volume is {percentage_free:.2f}%. Cannot install, please empty the disk."
                            )
                        else:
                            labels[host].config(fg="green")
                            logs.append(
                                f"{host} (IP: {ip}): Disk volume is {percentage_free:.2f}%. Disk space is sufficient."
                            )
                            logs.append(
                                f"Free space:{free_space:.2f}GB, Total space:{total_space:.2f}GB, Percentage free:{percentage_free:.2f}%.")

            finally:
                pythoncom.CoUninitialize()  # Uninitialize COM library

            # Stop the progress bar and display results
            regional_window.after(0, lambda: progress_bar_disk.stop())
            regional_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def disk_volume_test(host, ip):
        return f"Disk volume test passed for {host} (IP: {ip})"

    # Buttons
    tk.Button(
        regional_window,
        text="Get Version",
        command=perform_version_check,
        font=("Arial", 14),
        bg="#341a4d",
        fg="white",
        activebackground="#663399"
    ).place(x=button_x, y=240, width=button_width, height=50)

    tk.Button(
        regional_window,
        text="Communication Test",
        command=perform_communication_test,
        font=("Arial", 14),
        bg="#5a2c8a",
        fg="white",
        activebackground="#4c2f66"
    ).place(x=button_x, y=310, width=button_width, height=50)

    tk.Button(
        regional_window,
        text="Permission Test",
        command=perform_permission_test,
        font=("Arial", 14),
        bg="#5a2c8a",
        fg="white",
        activebackground="#4c2f66"
    ).place(x=button_x, y=380, width=button_width, height=50)

    tk.Button(
        regional_window,
        text="Disk Volume Test",
        command=perform_disk_volume_test,
        font=("Arial", 14),
        bg="#5a2c8a",
        fg="white",
        activebackground="#4c2f66"
    ).place(x=button_x, y=450, width=button_width, height=50)

    tk.Button(
        regional_window,
        text="Install App",
        command=on_install,
        font=("Arial", 14, 'bold'),
        bg="#5a2c8a",
        fg="white",
        activebackground="#663399"
    ).place(x=button_x, y=590, width=button_width, height=50)

    # Close button in the middle at the bottom
    tk.Button(
        regional_window,
        text="Close",
        command=on_close,
        font=("Arial", 14),
        bg="#C0C0C0",
        fg="black",
        activebackground="white"
    ).place(x=450, y=855, width=100, height=40)


def open_battery_window():
    battery_window = tk.Toplevel(root)
    battery_window.title(f"Remote App Installation - Battery {BN}")
    battery_window.geometry("1000x900")
    battery_window.resizable(False, False)
    battery_window.configure(bg="#004d4d")  # Dark teal background
    battery_window.iconbitmap(temp_icon_path)
    global progress_bar_ping
    global progress_bar_permissions
    global progress_bar_disk
    global progress_bar_version

    def on_close():
        global progress_bar_ping, progress_bar_permissions, progress_bar_disk, progress_bar_version
        # Reset the progress bar variable
        progress_bar_ping = None
        progress_bar_permissions = None
        progress_bar_disk = None
        progress_bar_version = None  # Global variable for the version check progress bar
        battery_window.destroy()  # Close the window

    battery_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hostnames and IPs
    default_hostnames_battery = {
        "BMC1": f"10.11.{BN}8.1",
        "BMC2": f"10.11.{BN}8.2",
        "ICS1": f"10.12.{BN}8.13",
        "ICS2": f"10.12.{BN}8.14",
        "DB1": f"10.11.{BN}8.3",
        "DB2": f"10.11.{BN}8.4",
        "Client1": f"10.11.{BN}8.6",
        "Client2": f"10.11.{BN}8.7",
        "Client3": f"10.11.{BN}8.8",
        "Client4": f"10.11.{BN}8.9",
        "Client5": f"10.11.{BN}8.10",
    }

    hostnames_file_path = ".\\Config\\hostnamesBattery.json"

    if os.path.exists(hostnames_file_path):
        # If the JSON file exists, read hostnames from it
        with open(hostnames_file_path, 'r') as file:
            hostnames = json.load(file)
        print("Loaded hostnames from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        hostnames = default_hostnames_battery
        print("Loaded hostnames from default dictionary.")

    # Map host to corresponding bat file paths
    default_bat_file_mapping = {
        "BMC1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryServer.bat",
        "BMC2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryServer.bat",
        "ICS1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\ICS.bat",
        "ICS2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\ICS.bat",
        "DB1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\DB\\mDRS.bat",
        "DB2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\DB\\mDRS.bat",
        "Client1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryClient.bat",
        "Client2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryClient.bat",
        "Client3": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryClient.bat",
        "Client4": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryClient.bat",
        "Client5": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryClient.bat",
        "Client6": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\BMC\\BatteryClient_test.bat",
    }

    bat_file_mapping_file_path = ".\\Config\\batFileMappingBattery.json"

    if os.path.exists(bat_file_mapping_file_path):
        # If the JSON file exists, read hostnames from it
        with open(bat_file_mapping_file_path, 'r') as file:
            bat_file_mapping = json.load(file)
        print("Loaded Bat file mapping from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        hostnames = default_bat_file_mapping
        print("Loaded Bat file mapping from default dictionary.")

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(battery_window, text=f"Remote App Installation - Battery {BN}", font=("Arial", 20, "bold"),
                           fg="white", bg="#004d4d")
    title_label.place(x=270, y=10)

    def yes_no_keep_install():
        response = messagebox.askyesno("Install App", "Are you sure you want to install the Battery?", parent=battery_window)
        if response:
            on_install()
        else:
            return

    def on_install():

        # Add progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(battery_window, variable=progress_var, maximum=100)
        progress_bar.place(x=580, y=615, width=300, anchor="center")  # Centered horizontally with a width of 400px

        # Add percentage label
        progress_label = tk.Label(battery_window, text="0%", font=("Arial", 14), fg="white", bg="#004d4d")
        progress_label.place(x=586, y=650, anchor="center")  # Positioned below the progress bar
        """
        Start the installation process for all selected hosts.
        """

        def install_task():
            logs = []  # Shared list to collect logs

            # Reset progress bar and results display
            progress_var.set(0)
            progress_label.config(text="0%")
            results_text.delete("1.0", tk.END)

            selected_hosts = [host for host, var in selections.items() if var.get()]
            if not selected_hosts:
                messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=battery_window)
                return

            total_hosts = len(selected_hosts)
            steps_per_host = 5  # Number of steps per host (customize, copy script, copy zip, copy tools, execute)
            total_steps = total_hosts * steps_per_host
            step_increment = 100 / total_steps  # Progress increment per step

            for host in selected_hosts:
                ip = hostnames[host]
                try:
                    # Extract details for the host
                    fourth_octet = ip.split(".")[-1]
                    PN = fourth_octet
                    bat_file_path = bat_file_mapping.get(host)
                    print(bat_file_path)

                    # Create a unique temporary .bat file for the host

                    if "BMC" in host:
                        temp_bat_path = f".\\temp\\BatteryServer_{PN}.bat"
                        name_bat_file = f"BatteryServer_{PN}.bat"
                    elif "ICS" in host:
                        temp_bat_path = f".\\temp\\ICS_{PN}.bat"
                        name_bat_file = f"ICS_{PN}.bat"
                    elif "DB" in host:
                        temp_bat_path = f".\\temp\\mDRS_{PN}.bat"
                        name_bat_file = f"mDRS_{PN}.bat"
                    else:
                        temp_bat_path = f".\\temp\\BatteryClient_{PN}.bat"
                        name_bat_file = f"BatteryClient_{PN}.bat"

                    # Step 1: Customize the .bat file
                    logs.append(f"Customizing batch file for {host} ({ip})...")
                    change_bat_pos_function(
                        bat_file_path, BN=BN, PN=PN, output_path=temp_bat_path, logs=logs
                    )
                    progress_var.set(progress_var.get() + step_increment)
                    progress_label.config(text=f"{int(progress_var.get())}%")
                    display_results(logs)

                    # Step 2-5: Transfer files and execute
                    logs.append(f"Starting installation process for {host} ({ip})...")
                    prepare_installation_battery(
                        ip_base=ip,
                        host_type=host,
                        current_bat_file=name_bat_file,
                        scripts_src=temp_bat_path,
                        logs=logs,
                        progress_var=progress_var,
                        progress_label=progress_label,
                        step_increment=step_increment,
                    )
                    logs.append(f"Installation completed for {host} ({ip}).")
                    display_results(logs)

                except Exception as e:
                    logs.append(f"Error during installation for {host} ({ip}): {e}")
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}", parent=battery_window)
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.", parent=battery_window)

            display_results(logs)

        threading.Thread(target=install_task).start()

    # Hostnames Section
    y_offset = 98
    for host, ip in hostnames.items():
        label = tk.Label(
            battery_window,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#004d4d",
            anchor="w"
        )
        label.place(x=80, y=y_offset)
        labels[host] = label

        tk.Checkbutton(
            battery_window,
            variable=selections[host],
            bg="#004d4d",
            fg="white",
            selectcolor="#004d4d",
            anchor="w"
        ).place(x=50, y=y_offset + 2)
        y_offset += 50

    # Functions for Check All and Uncheck All
    def check_all():
        for var in selections.values():
            var.set(True)

    def uncheck_all():
        for var in selections.values():
            var.set(False)

    # Buttons on the right
    button_x = 760
    button_width = 200
    tk.Button(
        battery_window,
        text="Check All",
        command=check_all,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Uncheck All",
        command=uncheck_all,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=170, width=button_width, height=50)

    # Results Display
    results_text = tk.Text(battery_window, height=10, width=60, bg="#003333", fg="white", font=("Arial", 12))
    results_text.place(x=50, y=700, width=700, height=150)

    def display_results(results):
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "\n".join(results))

    def perform_version_check():
        global progress_bar_version
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=battery_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_version is None:
            progress_bar_version = ttk.Progressbar(
                battery_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_version.place(x=580, y=255, width=150, height=20)

        progress_bar_version.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]

                    # Determine the file path based on the host type
                    if host.startswith("DB"):
                        file_path = r"c$\mDRS\Server\mPrest.mDRS.dll"
                        print("select - DB")
                    else:
                        file_path = r"c$\Firebolt\Watchdog\WDService\mPrest.IronDome.Watchdog.Service.dll"
                        print("select - not DB")

                    # Call the version checker
                    version_info = get_remote_file_version(ip, file_path)

                    if "error" in version_info:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) V")
                        logs.append(f"{host} (IP: {ip}): Version check failed - {version_info['error']}")
                    else:
                        product_version = version_info.get("Product Version", "Unknown")
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Version: {product_version}")

            # Stop the progress bar and display results
            battery_window.after(0, lambda: progress_bar_version.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_communication_test():
        global progress_bar_ping
        logs = []  # Collect logs here

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=battery_window)
            return

        # Create and show the progress bar the first time the button is pressed
        if progress_bar_ping is None:
            progress_bar_ping = ttk.Progressbar(
                battery_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_ping.place(x=580, y=325, width=150, height=20)

        progress_bar_ping.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    success = check_communication(ip)
                    if success:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Communication successful.")
                        labels[host].config(text=f"{host} (IP: {ip})")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) C")
                        logs.append(f"{host} (IP: {ip}): Communication failed.")

            # Stop the progress bar after the test completes
            battery_window.after(0, lambda: progress_bar_ping.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_permission_test():
        global progress_bar_permissions
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=battery_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_permissions is None:
            progress_bar_permissions = ttk.Progressbar(
                battery_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_permissions.place(x=580, y=395, width=150, height=20)

        progress_bar_permissions.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    network_path = rf"\\{ip}\c$\temp"  # Adjust the network path format

                    # Check if the folder exists
                    if not os.path.exists(network_path):
                        try:
                            os.makedirs(network_path)  # Create the folder
                            folder_created = True
                        except Exception as e:
                            logs.append(f"{host} (IP: {ip}): Failed to create folder - {e}")
                            labels[host].config(fg="red")
                            labels[host].config(text=f"{host} (IP: {ip}) P")
                            continue  # Skip further execution for this host
                    else:
                        folder_created = False  # The folder already existed

                    permissions = check_permissions(network_path)  # Call the helper function

                    # Update GUI based on results
                    if permissions["readable"] and permissions["writable"]:
                        labels[host].config(fg="green")
                        labels[host].config(text=f"{host} (IP: {ip})")
                        logs.append(f"{host} (IP: {ip}): Permissions OK (Read/Write).")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) P")
                        logs.append(f"{host} (IP: {ip}): Permissions FAILED.")

                    # If we created the folder, delete it after the test
                    if folder_created:
                        try:
                            for file in os.listdir(network_path):  # Remove all files first
                                file_path = os.path.join(network_path, file)
                                if os.path.isfile(file_path) or os.path.islink(file_path):
                                    os.remove(file_path)
                            os.rmdir(network_path)  # Now remove the empty directory
                        except Exception as e:
                            logs.append(f"{host} (IP: {ip}): Failed to delete folder - {e}")

            # Stop the progress bar and display results
            battery_window.after(0, lambda: progress_bar_permissions.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_disk_volume_test():
        global progress_bar_disk
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.", parent=battery_window)
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_disk is None:
            progress_bar_disk = ttk.Progressbar(
                battery_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_disk.place(x=580, y=465, width=150, height=20)

        progress_bar_disk.start(10)  # Start the progress bar

        def run_test():
            pythoncom.CoInitialize()  # Initialize COM library for WMI
            try:
                for host, var in selections.items():
                    if var.get():
                        ip = hostnames[host]
                        free_space, total_space, percentage_free = get_drive_space(ip)

                        if free_space is None or total_space is None:
                            labels[host].config(fg="red")
                            logs.append(f"{host} (IP: {ip}): Failed to retrieve disk space information.")
                        elif free_space < 10:
                            labels[host].config(fg="red")
                            labels[host].config(text=f"{host} (IP: {ip}) D")
                            logs.append(
                                f"{host} (IP: {ip}): C Drive Disk space is {free_space:.2f}GB. Cannot install, please empty the disk."
                            )
                        else:
                            labels[host].config(fg="green")
                            labels[host].config(text=f"{host} (IP: {ip})")
                            logs.append(
                                f"{host} (IP: {ip}): Free space in C Drive is {free_space:.2f}GB. Disk space is sufficient."
                            )
                            logs.append(
                                f"Free space: {free_space:.2f}GB, Total space: {total_space:.2f}GB, Percentage free: {percentage_free:.2f}%.")
            finally:
                pythoncom.CoUninitialize()  # Uninitialize COM library

            # Stop the progress bar and display results
            battery_window.after(0, lambda: progress_bar_disk.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    # Buttons
    tk.Button(
        battery_window,
        text="Get Version",
        command=perform_version_check,
        font=("Arial", 14),
        bg="#003d3d",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=240, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Communication Test",
        command=perform_communication_test,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=310, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Permission Test",
        command=perform_permission_test,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=380, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Disk Volume Test",
        command=perform_disk_volume_test,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=450, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Install App",
        command=yes_no_keep_install,
        font=("Arial", 14, 'bold'),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=590, width=button_width, height=50)

    # Close button in the middle at the bottom
    tk.Button(
        battery_window,
        text="Close",
        command=on_close,
        font=("Arial", 14),
        bg="#800000",
        fg="white",
        activebackground="#990000"
    ).place(x=450, y=855, width=100, height=40)

    # if len(installation_app_remote_message) == 0:
    #     messagebox.showinfo("Don't forget", "The new version of the application should be on the local disk: C:\\FBE")
    #     installation_app_remote_message.append("onetime")

def wireshark_screen():
    # Clear existing buttons
    on_button_click()

    # Add Label
    wireshark_label = tk.Label(root, text='Wireshark', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    wireshark_label.place(x=230, y=10)
    buttons.append(wireshark_label)

    # Create Buttons with Hover Effects
    create_button(root, 'Install Wireshark', run_install_wireshark, 178, 420)
    create_button(root, 'Install Npcap', run_npcap_install, 178, 490)
    create_button(root, 'Open Wireshark', run_open_wireshark, 178, 560)



    create_button(root, 'Back', tools_screen, 14, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)

def tools_screen():
    # Clear existing buttons
    on_button_click()

    # Add Label
    tools_label = tk.Label(root, text='Tools', fg='white', bg='#000000', font=('Arial', 20, 'bold'), anchor="center")
    tools_label.place(x=250, y=10)
    buttons.append(tools_label)

    # Create Buttons with Hover Effects
    create_button(root, 'Utilities', open_utilities_window, 156, 420, button_style_medium)
    create_button(root, 'FinishScript', run_finishScript, 320, 420, button_style_medium)
    create_button(root, 'Wireshark' , wireshark_screen, 156, 490, button_style_medium)
    create_button(root, 'ILSpy', run_ilspy, 320, 490, button_style_medium)
    create_button(root, 'Ping Monitor', open_ping_monitor, 156, 560, button_style_medium)
    create_button(root, 'Dep.', None, 320, 560, button_style_medium)


    create_button(root, 'Back', main_screen, 14, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)


def rai_screen():
    # Clear existing buttons
    on_button_click()

    # Add Label
    rai_label = tk.Label(root, text='Installation Phase', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    rai_label.place(x=170, y=10)
    buttons.append(rai_label)

    # Create Buttons with Hover Effects
    battery_install_window = create_button(root, 'Battery', open_battery_window, 178, 420)
    regional_install_window = create_button(root, 'Regional', open_regional_window, 178, 490)
    simulator_install_window = create_button(root, 'Simulator', open_simulator_window, 178, 560)
    vsil_install_window = create_button(root, 'VSIL/CIWS', open_vsil_window, 178, 630)

    if BN == "VSIL/CIWS":
        disable_button(battery_install_window)
        disable_button(regional_install_window)
        disable_button(simulator_install_window)
    else:
        disable_button(vsil_install_window)


    create_button(root, 'Back', phases_app_installation_screen, 14, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)


def db_screen():
    # Clear existing buttons
    on_button_click()

    # Add Label
    rai_label = tk.Label(root, text='Database Phase', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    rai_label.place(x=180, y=10)
    buttons.append(rai_label)

    # Create Buttons with Hover Effects
    battery_install_window = create_button(root, 'Battery', selection_db_window_battery, 178, 420)
    regional_install_window = create_button(root, 'Regional', selection_db_window_regional, 178, 490)
    vsil_install_window = create_button(root, 'VSIL/CIWS', selection_db_window_vsil_function, 178, 560)

    if BN == "VSIL/CIWS":
        disable_button(battery_install_window)
        disable_button(regional_install_window)
    else:
        disable_button(vsil_install_window)


    create_button(root, 'Back', phases_app_installation_screen, 14, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)

def phases_app_installation_screen():
    # Check if BN is chosen
    if BN == 0:
        messagebox.showerror("Battery number", "Please choose a battery number to continue.")
        return
    on_button_click()

    # Add Label
    phases_app_installation_label = tk.Label(root, text='Remote App Installation', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    phases_app_installation_label.place(x=145, y=10)
    buttons.append(phases_app_installation_label)

    # Create Buttons with Hover Effects
    create_button(root, 'Installation Phase', rai_screen, 178, 420)
    create_button(root, 'Database Phase', db_screen, 178, 490)

    create_button(root, 'Back', main_screen, 14, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)

def main_screen():
    on_button_click()

    def save_value():
        global BN
        selected_value = dropdown_var.get()
        if selected_value == "Select a number":
            return
        elif selected_value == "Regional":
            BN = 21
        else:
            BN = selected_value
        messagebox.showinfo("Save", f"The battery number was update to {BN}")

    # Add Main Label
    main_label = tk.Label(root, text='Main', fg='white', bg='#000000', font=('Arial', 20, 'bold'), anchor="center")
    main_label.place(x=266, y=10)
    buttons.append(main_label)

    # Dropdown Menu
    dropdown_var = tk.StringVar(value="Select a number")
    dropdown_label = tk.Label(root, text="Battery number:", fg='white', bg='#000000', font=('Arial', 14))
    dropdown_label.place(x=10, y=10)
    buttons.append(dropdown_label)

    dropdown = ttk.Combobox(root, textvariable=dropdown_var, state="readonly", font=('Arial', 10), width=16)
    dropdown['values'] = [1, 2, 3, 4, 5, 6,10, "Regional", "VSIL/CIWS"]
    dropdown.place(x=10, y=40)
    buttons.append(dropdown)

    # Save Button
    save_button = tk.Button(root, text='Save', width=6, height=2, bg='#444444', fg='white', font=('Arial', 8, 'bold'),
                            activebackground='#555555', command=save_value)
    save_button.place(x=10, y=70)
    buttons.append(save_button)

    # Create Buttons with Hover Effects
    create_button(root, 'App Installation', phases_app_installation_screen, 178, 420)
    create_button(root, 'Checks Components', coming_soon, 178, 490)
    create_button(root, 'Cyber Deployment', coming_soon, 178, 560)
    create_button(root, 'Tools', tools_screen, 360, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)


main_screen()
root.mainloop()
