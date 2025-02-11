import tkinter as tk
from tkinter import PhotoImage, ttk, messagebox
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


# Main Application
root = tk.Tk()
root.title("Software Helper Tools")
root.geometry("600x750")
root.resizable(False, False)
# root.eval('tk::PlaceWindow . center')
root.iconbitmap("icon.ico")


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
bg_image = PhotoImage(file='logo1.png')  # Ensure this image is in your directory
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

BN = 0
VSIL_BN = 0

buttons = []
installation_app_remote_message = []
progress_bar_ping = None
progress_bar_permissions = None
progress_bar_disk = None
progress_bar_version = None


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

# def prompt_for_credentials():
#     global SQL_USER, SQL_PASS
#
#     # Create a dialog to request credentials
#     credentials_window = tk.Toplevel()
#     credentials_window.title("Enter SQL Credentials")
#     credentials_window.geometry("300x200")
#     credentials_window.resizable(False, False)
#     credentials_window.grab_set()  # Make it modal
#     credentials_window.iconbitmap("icon.ico")
#
#     tk.Label(credentials_window, text="Username:", font=("Arial", 12)).pack(pady=5)
#     username_entry = tk.Entry(credentials_window, font=("Arial", 12))
#     username_entry.pack(pady=5)
#
#     tk.Label(credentials_window, text="Password:", font=("Arial", 12)).pack(pady=5)
#     password_entry = tk.Entry(credentials_window, font=("Arial", 12), show="*")
#     password_entry.pack(pady=5)
#
#     def save_credentials():
#         global SQL_USER, SQL_PASS
#         SQL_USER = username_entry.get()
#         SQL_PASS = password_entry.get()
#         credentials_window.destroy()  # Close the credentials window
#
#     tk.Button(credentials_window, text="Submit", command=save_credentials, font=("Arial", 12)).pack(pady=10)
#
#     credentials_window.wait_window()  # Block execution until window is closed
# Function to open a new window for the Database

def open_battery_database_window():
    global BN

    # Ask for credentials before opening the main window
    # prompt_for_credentials()

    database_window_battery = tk.Toplevel()
    database_window_battery.title("Table Management")
    database_window_battery.geometry("400x470")
    database_window_battery.resizable(False, False)
    database_window_battery.configure(bg="#004d4d")
    database_window_battery.iconbitmap("icon.ico")

    # Title Label
    title_label = tk.Label(
        database_window_battery, text=f"Database Battery {BN}", font=("Arial", 14, "bold"), fg="white", bg="#004d4d"
    )
    title_label.place(x=100, y=5)

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
        response = messagebox.askyesno("Delete tables", "Are you sure you want to delete DB tables?")
        if response:
            handle_delete_tables()
        else:
            return


    def handle_create_empty_tables():
        global BN, bat_file_name

        # Ensure at least one mode is selected
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.")
            return

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
        write_bat_file_db_phase(BN=BN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN,current_bat_file=bat_file_name, results_text=results_text)

    def create_empty_databases():
        threading.Thread(target=handle_create_empty_tables).start()


    def handle_delete_tables():
        global BN, bat_file_name

        # Ensure at least one mode is selected
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.")
            return
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
        write_bat_file_db_phase(BN=BN, BAT_FILE_NAME=bat_file_name, results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN,current_bat_file=bat_file_name, results_text=results_text)

    def delete_databases():
        threading.Thread(target=handle_delete_tables).start()

    def handle_import_tables():
        global BN, bat_file_name

        # Ensure at least one mode is selected
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.")
            return

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
        write_bat_file_db_phase(BN=BN, BAT_FILE_NAME=bat_file_name,
                                results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_tables_battery(BN, current_bat_file=bat_file_name, results_text=results_text)

    def import_tables():
        threading.Thread(target=handle_import_tables).start()

    def handle_adding_launchers():
        global BN, bat_file_name

        # Ensure at least one mode is selected
        if not (operational_var.get() or training_var.get()):
            messagebox.showwarning("No Selection", "Please select at least one mode.")
            return

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
        write_bat_file_db_phase(BN=BN, BAT_FILE_NAME=bat_file_name,
                                results_text=results_text)

        # Step 2: Transfer & Execute Remotely
        handle_adding_launchers_battery(bat_num=BN, current_sql_file=sql_file_name, current_bat_file=bat_file_name, results_text=results_text)

    def adding_launchers():
        threading.Thread(target=handle_adding_launchers).start()

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
    ).place(x=162, y=430, width=80, height=30)

    # Close button in the middle at the bottom


    # Results Display
    results_text = tk.Text(database_window_battery, height=5, width=50, bg="#003333", fg="white", font=("Arial", 10))
    results_text.place(x=20, y=300, width=360, height=120)

# Function to open a new window for the App Installation
def open_vsil_window():
    vsil_window = tk.Toplevel(root)
    vsil_window.title("Remote App Installation - VSIL")
    vsil_window.geometry("1000x900")
    vsil_window.resizable(False, False)
    vsil_window.configure(bg="#FF69B4")  # Dark teal background
    vsil_window.iconbitmap("icon.ico")

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
    hostnames = {
        "BMC1": "192.168.3.154",
        "BMC2": "192.168.28.1",
        "BMC3": "192.168.38.1",
        "BMC4": "192.168.48.1",
        "ICS1": "192.169.18.13",
        "ICS2": "192.169.28.13",
        "ICS3": "192.169.38.13",
        "ICS4": "192.169.48.13",
        "DB-BAT": "192.168.18.3",
        "CBMC": "192.168.218.1",
        "DB-CBMC": "192.168.218.3",
        "TCS-Server": "192.168.18.2",
        "TCS-Client": "192.168.218.11",
        "CBMC-Client": "192.168.218.50",
        "AD-BAT": "192.168.13.20",
        "AD-CBMC": "192.168.213.20",
        "AV-BAT": "192.168.13.22",
        "AV-CBMC": "192.168.213.22",
    }

    # Map host to corresponding bat file paths
    bat_file_mapping = {
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

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(vsil_window, text=f"Remote App Installation - VSIL", font=("Arial", 20, "bold"), fg="white",
                           bg="#FF69B4")
    title_label.place(x=330, y=10)

    # Create a scrollable frame for hostnames
    scroll_frame = tk.Frame(vsil_window, bg="#FF69B4")
    scroll_frame.place(x=10, y=70, width=900, height=600)  # Ensure the frame starts at the correct position

    canvas = tk.Canvas(scroll_frame, bg="#FF69B4", highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    host_frame = tk.Frame(canvas, bg="#FF69B4")  # This will contain the hostnames and checkboxes

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
                messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}")
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.")

            display_results(logs)

        threading.Thread(target=install_task).start()

    for host, ip in hostnames.items():
        # Create a frame for the checkbox and label
        item_frame = tk.Frame(host_frame, bg="#FF69B4")  # Matches the background color

        # Add the checkbox
        tk.Checkbutton(
            item_frame,
            variable=selections[host],
            bg="#FF69B4",
            fg="white",
            selectcolor="#FF69B4",
            anchor="w"
        ).pack(side="left", padx=2)  # Pack the checkbox to the left with padding

        # Add the label
        labels[host] = tk.Label(
            item_frame,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#FF69B4",
            anchor="w"
        )
        labels[host].pack(side="left", padx=2)  # Pack the label to the right of the checkbox with spacing

        # Pack the row into the scrollable host frame
        item_frame.pack(fill="x", pady=10)  # Add vertical space between rows

    # Functions for Check All and Uncheck All
    def check_all():
        for var in selections.values():
            var.set(True)

    def uncheck_all():
        for var in selections.values():
            var.set(False)

        # test bat number

    # for hostnames, ip in hostnames.items():
    #     if "AD CBMC" in hostnames or "CBMC" in hostnames or "CBMC Client" in hostnames or "DB CBMC" in hostnames or "TCS Client" in hostnames:
    #         first_digits = 21
    #     else:
    #         first_digits = ip.split('.')[2][0]
    #     print(first_digits)

    # Buttons on the right
    button_x = 760
    button_width = 200
    tk.Button(
        vsil_window,
        text="Check All",
        command=check_all,
        font=("Arial", 14),
        bg="#FF1493",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Uncheck All",
        command=uncheck_all,
        font=("Arial", 14),
        bg="#FF1493",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=170, width=button_width, height=50)

    # Results Display
    results_text = tk.Text(vsil_window, height=10, width=60, bg="#C71585", fg="white", font=("Arial", 12))
    results_text.place(x=50, y=700, width=700, height=150)

    def display_results(results):
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "\n".join(results))

    def perform_version_check():
        global progress_bar_version
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                        file_path = r"c$\Program Files\7-Zip\7z.exe"
                    else:
                        file_path = r"c$\Program Files\7-Zip\7z.exe"

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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
        bg="#C71585",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=240, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Communication Test",
        command=perform_communication_test,
        font=("Arial", 14),
        bg="#FF1493",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=310, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Permission Test",
        command=perform_permission_test,
        font=("Arial", 14),
        bg="#FF1493",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=380, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Disk Volume Test",
        command=perform_disk_volume_test,
        font=("Arial", 14),
        bg="#FF1493",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=450, width=button_width, height=50)

    tk.Button(
        vsil_window,
        text="Install App",
        command=on_install,
        font=("Arial", 14, 'bold'),
        bg="#FF1493",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=590, width=button_width, height=50)

    # Close button in the middle at the bottom
    tk.Button(
        vsil_window,
        text="Close",
        command=on_close,
        font=("Arial", 14),
        bg="#800000",
        fg="white",
        activebackground="#990000"
    ).place(x=450, y=855, width=100, height=40)


def open_simulator_window():
    simulator_window = tk.Toplevel(root)
    simulator_window.title("Remote App Installation - Simulator mPrest")
    simulator_window.geometry("1000x900")
    simulator_window.resizable(False, False)
    simulator_window.configure(bg="#228B22")  # Dark teal background
    simulator_window.iconbitmap("icon.ico")

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
    hostnames = {
        "Sim Server": f"192.168.{BN}.141",
        "Client1": f"192.168.{BN}8.6",
        "Client2": f"192.168.{BN}8.7",
        "Client3": f"192.168.{BN}8.8",
        "Client4": f"192.168.{BN}8.9",
        "Client5": f"192.168.{BN}8.10",
    }

    sim_file_mapping = {
        "Sim Server": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorServer.bat",
        "Client1": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client2": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client3": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client4": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",
        "Client5": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\Simulator\\SimulatorClient.bat",

    }

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
                messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}")
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.")

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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                    if host.startswith("DB"):
                        file_path = r"c$\Program Files\7-Zip\7z.exe"
                    else:
                        file_path = r"c$\Program Files\7-Zip\7z.exe"

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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
    regional_window.iconbitmap("icon.ico")

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
    hostnames = {
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

    # Map host to corresponding bat file paths
    reg_file_mapping = {
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
        "Client8": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient_test.bat",
    }

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
                messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                        bat_file_path, BN=BN, PN=PN, output_path=temp_bat_path, logs=logs
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
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}")
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.")

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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                        file_path = r"c$\Program Files\7-Zip\7z.exe"
                    else:
                        file_path = r"c$\Program Files\7-Zip\7z.exe"

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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
    battery_window.iconbitmap("icon.ico")
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

    x = battery_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hostnames and IPs
    hostnames = {
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
        "Client6": f"192.168.{BN}.141",
    }

    # Map host to corresponding bat file paths
    bat_file_mapping = {
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

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(battery_window, text=f"Remote App Installation - Battery {BN}", font=("Arial", 20, "bold"),
                           fg="white", bg="#004d4d")
    title_label.place(x=270, y=10)

    def yes_no_keep_install():
        response = messagebox.askyesno("Install App", "Are you sure you want to install the Battery?")
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
                messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                    messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}")
                    display_results(logs)

            # Final progress update and logs
            progress_var.set(100)
            progress_label.config(text="100%")
            cleanup_temp_files()
            logs.append("All installations completed.")

            messagebox.showinfo("Installation Complete", "File transfer process finished for all selected hosts.")

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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
                        file_path = r"c$\Program Files\7-Zip\7z.exe"
                    else:
                        file_path = r"c$\Program Files\7-Zip\7z.exe"

                    # Call the version checker
                    version_info = get_remote_file_version(ip, file_path)

                    if "error" in version_info:
                        labels[host].config(fg="red")
                        logs.append(f"{host} (IP: {ip}): Version check failed - {version_info['error']}")
                    else:
                        product_version = version_info.get("Product Version", "Unknown")
                        0
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
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


def rai_screen():
    # Clear existing buttons
    on_button_click()

    # Add Label
    rai_label = tk.Label(root, text='Installation Phase', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    rai_label.place(x=138, y=10)
    buttons.append(rai_label)

    # Create Buttons with Hover Effects
    battery_install_window = create_button(root, 'Battery', open_battery_window, 178, 420)
    regional_install_window = create_button(root, 'Regional', open_regional_window, 178, 490)
    simulator_install_window = create_button(root, 'Simulator', open_simulator_window, 178, 560)
    vsil_install_window = create_button(root, 'VSIL', open_vsil_window, 178, 630)

    if BN == "VSIL":
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
    rai_label = tk.Label(root, text='Installation Phase', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    rai_label.place(x=138, y=10)
    buttons.append(rai_label)

    # Create Buttons with Hover Effects
    battery_install_window = create_button(root, 'Battery', open_battery_window, 178, 420)
    regional_install_window = create_button(root, 'Regional', open_regional_window, 178, 490)
    vsil_install_window = create_button(root, 'VSIL', open_vsil_window, 178, 560)

    if BN == "VSIL":
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
    phases_app_installation_label.place(x=170, y=10)
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
        BN = selected_value
        print(f"Saved value: {selected_value}")
        messagebox.showinfo("Save", f"The battery number was update to {BN}")

    # Add Main Label
    main_label = tk.Label(root, text='Main', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    main_label.place(x=266, y=10)
    buttons.append(main_label)

    # Dropdown Menu
    dropdown_var = tk.StringVar(value="Select a number")
    dropdown_label = tk.Label(root, text="Battery number:", fg='white', bg='#000000', font=('Arial', 14))
    dropdown_label.place(x=10, y=10)
    buttons.append(dropdown_label)

    dropdown = ttk.Combobox(root, textvariable=dropdown_var, state="readonly", font=('Arial', 10))
    dropdown['values'] = [1, 2, 3, 4, 5, 6,10, 21, "VSIL"]
    dropdown.place(x=10, y=40)
    buttons.append(dropdown)

    # Save Button
    save_button = tk.Button(root, text='Save', width=6, height=2, bg='#444444', fg='white', font=('Arial', 8, 'bold'),
                            activebackground='#555555', command=save_value)
    save_button.place(x=10, y=70)
    buttons.append(save_button)

    # Create Buttons with Hover Effects
    create_button(root, 'App Installation', phases_app_installation_screen, 178, 420)
    create_button(root, 'Checks Components', open_vsil_window, 178, 490)
    create_button(root, 'Cyber Deployment', open_battery_database_window, 178, 560)
    create_button(root, 'Tools', lambda: on_click(None), 360, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)


main_screen()
root.mainloop()
