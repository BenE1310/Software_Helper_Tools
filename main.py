import json
import shutil
import subprocess
import tkinter as tk
from tkinter import PhotoImage, ttk, messagebox
import pythoncom
import wmi

from functions import check_communication, check_permissions, get_drive_space, get_remote_file_version, \
    change_bat_pos_function, cleanup_temp_files, prepare_installation_battery, prepare_installation_regional, \
    prepare_installation_simulator, write_bat_file_db_phase, handle_tables_battery, handle_adding_launchers_battery, \
    generate_sql_script_training_launchers
import tkinter.ttk as ttk
import threading
import pythoncom  # Import pythoncom for WMI operations
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring
import os
import sys
import tkinter as tk


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
    utilities_window.geometry("1000x720")
    utilities_window.resizable(False, False)
    utilities_window.configure(bg="#2E2E2E")

    if BN == 21:
        label_window = "Regional"
    elif "VSIL" in str(BN):
        label_window = "VSIL"
    else:
        label_window = f"Battery {BN}"

    # Sample dictionary fallback in case JSON file is not found
    default_hostnames_utilities = {
        "Ben": {"ip": "25.129.220.99", "services": [{"name": "ServiceA", "user": "admin", "recovery": "Restart"}]},
        "Host2": {"ip": "192.168.0.2", "services": [{"name": "ServiceB", "user": "user1", "recovery": "RunProgram"}]},
    }


    hostnames_file_path_utilities = ".\\Config\\utilitisHostnames.json"

    if os.path.exists(hostnames_file_path_utilities):
        # If the JSON file exists, read hostnames from it
        with open(hostnames_file_path_utilities, 'r') as file:
            hostnames = json.load(file)
        print("Loaded hostnames from JSON file.")
    else:
        # If the JSON file does not exist, use the default dictionary
        hostnames = default_hostnames_utilities
        print("Loaded hostnames from default dictionary.")

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}

    # Add "Utilities" label
    tk.Label(
        utilities_window, text=f"Utilities - {label_window}", font=("Arial", 24, "bold"), bg="#2E2E2E", fg="white"
    ).place(x=500, y=30, anchor="center")

    # Scrollable Frame for Host Details
    scroll_frame = tk.Frame(utilities_window, bg="#2E2E2E")
    scroll_frame.place(x=30, y=100, width=220, height=540)  # Moved slightly to the right

    # Canvas & Scrollbar Setup
    canvas = tk.Canvas(scroll_frame, bg="#2E2E2E", highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    host_frame = tk.Frame(canvas, bg="#2E2E2E")

    host_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((10, 0), window=host_frame, anchor="nw")  # Moved content slightly right

    # Keep scrollbar on left
    scrollbar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)

    # Display Hosts with Checkboxes (Moved Right)
    for host in hostnames:
        item_frame = tk.Frame(host_frame, bg="#2E2E2E")

        # Checkbox (Shifted Right)
        checkbutton = tk.Checkbutton(
            item_frame, variable=selections[host], bg="#2E2E2E", fg="white", selectcolor="#2E2E2E", anchor="w"
        )
        checkbutton.grid(row=0, column=0, padx=15)  # Increased padding for right shift

        # Hostname Label (Shifted Right)
        tk.Label(
            item_frame, text=host, font=("Arial", 14, "bold"), fg="white", bg="#2E2E2E", anchor="w"
        ).grid(row=0, column=1, padx=10)  # Increased padding for right shift

        # Place in scroll area
        item_frame.pack(anchor="w", pady=5)

    # "Set All" & "Clear All" Functions
    def check_all():
        for var in selections.values():
            var.set(True)

    def uncheck_all():
        for var in selections.values():
            var.set(False)

    # Keep all original buttons (UNCHANGED)
    button_style = {"font": ("Arial", 14), "fg": "white", "bd": 3, "relief": "solid", "width": 18, "height": 2}

    tk.Button(utilities_window, text="Mark All", command=check_all, bg="green",
              **button_style).place(x=750, y=100)
    tk.Button(utilities_window, text="Unmark All", command=uncheck_all, bg="red",
              **button_style).place(x=750, y=180)
    tk.Button(utilities_window, text="Restart Watchdog", command=lambda: print("Restarting Watchdog..."), bg="#0099cc",
              **button_style).place(x=750, y=260)
    tk.Button(utilities_window, text="Start Watchdog", command=lambda: print("Starting Watchdog..."), bg="#0099cc",
              **button_style).place(x=750, y=340)
    tk.Button(utilities_window, text="Stop Watchdog", command=lambda: print("Stopping Watchdog..."), bg="#0099cc",
              **button_style).place(x=750, y=420)
    tk.Button(utilities_window, text="Restart Component", command=lambda: print("Restart component..."),
              bg="#0099cc", **button_style).place(x=750, y=500)
    tk.Button(utilities_window, text="Shutdown Component", command=lambda: print("Shutting down component..."),
              bg="#0099cc", **button_style).place(x=750, y=580)

    # Close button (UNCHANGED)
    close_button_style = {"font": ("Arial", 12), "fg": "white", "bd": 3, "relief": "solid", "width": 10, "height": 2}
    tk.Button(utilities_window, text="Close", command=utilities_window.destroy, bg="gray", **close_button_style).place(
        x=500, y=680, anchor="center")

    # Result Bar (UNCHANGED)
    result_text_widget = tk.Text(
        utilities_window, width=48, height=29, wrap=tk.WORD, bg="#333333", fg="white", bd=2, font=("Arial", 12)
    )
    result_text_widget.place(x=278, y=106)




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
    progress_bar = ttk.Progressbar(database_window_vsil, orient="horizontal", mode="indeterminate", length=360)
    progress_bar.place(x=60, y=290, width=280, height=20)

    def start_progress():
        progress_bar.start(10)  # Starts animation with 10ms step

    def stop_progress():
        progress_bar.stop()  # Stops the animation

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
    progress_bar = ttk.Progressbar(database_window_regional, orient="horizontal", mode="indeterminate", length=360)
    progress_bar.place(x=60, y=290, width=280, height=20)

    def start_progress():
        progress_bar.start(10)  # Starts animation with 10ms step

    def stop_progress():
        progress_bar.stop()  # Stops the animation

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
    progress_bar = ttk.Progressbar(database_window_battery, orient="horizontal", mode="indeterminate", length=360)
    progress_bar.place(x=60, y=290, width=280, height=20)

    def start_progress():
        progress_bar.start(10)  # Starts animation with 10ms step

    def stop_progress():
        progress_bar.stop()  # Stops the animation

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

    # Title Label
    title_label = tk.Label(vsil_window, text=f"Remote App Installation - VSIL/CIWS", font=("Arial", 20, "bold"), fg="white",
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
        vsil_window,
        text="Check All",
        command=check_all,
        font=("Arial", 14),
        bg="#C71585",
        fg="white",
        activebackground="#C71585"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Uncheck All",
        command=uncheck_all,
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
    create_button(root, 'Wireshark' , coming_soon, 156, 490, button_style_medium)
    create_button(root, 'ILSpy', run_ilspy, 320, 490, button_style_medium)
    create_button(root, 'Ping Tester', None, 156, 560, button_style_medium)
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

    dropdown = ttk.Combobox(root, textvariable=dropdown_var, state="readonly", font=('Arial', 10))
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
