import tkinter as tk
from tkinter import PhotoImage, ttk, messagebox
from functions import check_communication, check_permissions, get_drive_space, get_remote_file_version, \
    change_bat_pos_function, cleanup_temp_files, prepare_installation_battery, prepare_installation_regional, \
    prepare_installation_simulator
import tkinter.ttk as ttk
import threading
import pythoncom  # Import pythoncom for WMI operations

from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring


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
buttons = []
installation_app_remote_message = []
progress_bar_ping = None
progress_bar_permissions = None
progress_bar_disk = None
progress_bar_version = None


# Reusable function to create a button with hover effects
def create_button(parent, text, command, x, y, style=button_style):
    button = tk.Button(parent, text=text, **style, command=command)
    button.place(x=x, y=y)
    button.bind("<Enter>", lambda e: on_enter(button))
    button.bind("<Leave>", lambda e: on_leave(button))
    buttons.append(button)  # Add to buttons list for tracking
    return button


# Function to open a new window for the Battery button

def open_vsil_window():
    vsil_window = tk.Toplevel(root)
    vsil_window.title("Remote App Installation")
    vsil_window.geometry("1000x900")
    vsil_window.resizable(False, False)
    vsil_window.configure(bg="#FF69B4")  # Dark teal background
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

    x = vsil_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hostnames and IPs
    hostnames = {
        "BMC1": "192.168.3.141",
        "BMC2": "192.168.3.135",
        "BMC3": "192.168.3.136",
        "BMC4": "192.168.3.138",
        "ICS1": "192.168.3.139",
        "ICS2": "192.168.3.140",
        "ICS3": "192.168.1.7",
        "ICS4": "192.168.1.8",
        "DB BAT": "192.168.1.9",
        "CBMC": "192.168.1.10",
        "DB-CBMC": "192.168.1.11",
        "TCS Server": "192.168.1.11",
        "TCS Client": "192.168.1.11",
        "CBMC Client": "192.168.1.11",
        "AD BAT": "192.168.1.11",
        "AD CBMC": "192.168.1.11",

    }

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(vsil_window, text=f"Remote App Installation - VSIL", font=("Arial", 20, "bold"), fg="white",
                           bg="#FF69B4")
    title_label.place(x=270, y=10)

    # Hostnames Section
    y_offset = 70
    for host, ip in hostnames.items():
        label = tk.Label(
            vsil_window,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#FF69B4",
            anchor="w"
        )
        label.place(x=80, y=y_offset)
        labels[host] = label

        tk.Checkbutton(
            vsil_window,
            variable=selections[host],
            bg="#FF69B4",
            fg="white",
            selectcolor="#FF69B4",
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
                        logs.append(f"free space:{free_space}, total space:{total_space}, percentage_free:{percentage_free}")

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
        command=on_close,
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
    simulator_window.title("Remote App Installation")
    simulator_window.geometry("1000x900")
    simulator_window.resizable(False, False)
    simulator_window.configure(bg="#228B22")  # Dark teal background
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
        "Sim Server": "192.168.3.141",
        "Client1": f"192.168.{BN}.6",
        "Client2": f"192.168.{BN}.7",
        "Client3": f"192.168.{BN}.8",
        "Client4": f"192.168.{BN}.9",
        "Client5": "172.16.10.108",
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
    regional_window.title("Remote App Installation")
    regional_window.geometry("1000x900")
    regional_window.resizable(False, False)
    regional_window.configure(bg="#663399")  # Dark teal background
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

    # Hostnames and IPs
    hostnames = {
        "CBMC1": "192.168.3.141",
        "CBMC2": "192.168.3.135",
        "DB1": "192.168.3.139",
        "DB2": "192.168.3.140",
        "Client1": "192.168.1.7",
        "Client2": "192.168.1.8",
        "Client3": "192.168.1.9",
        "Client4": "192.168.1.10",
        "Client5": "192.168.1.11",
        "Client6": "192.168.3.154",
        "Client7": "172.16.10.108",
        "Client8": "192.168.3.154",
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
        "Client8": ".\\Scripts\\AppInstallation\\RemoteInstallation\\FBE\\CBMC\\RegionalClient.bat",
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
    battery_window.title("Remote App Installation")
    battery_window.geometry("1000x900")
    battery_window.resizable(False, False)
    battery_window.configure(bg="#004d4d")  # Dark teal background
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
        "BMC1": "192.168.8.154",
        "BMC2": "192.168.8.141",
        "ICS1": "192.168.3.136",
        "ICS2": "192.168.3.138",
        "DB1": "172.16.10.108",
        "DB2": "192.168.3.140",
        "Client1": "192.168.3.154",
        "Client2": "192.168.3.141",
        "Client3": "192.168.1.9",
        "Client4": "192.168.1.10",
        "Client5": "172.16.10.108",
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
    }

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(battery_window, text=f"Remote App Installation - Battery {BN}", font=("Arial", 20, "bold"),
                           fg="white", bg="#004d4d")
    title_label.place(x=270, y=10)



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
                        labels[host].config(fg="green", text=f"{host} (IP: {ip}) - Version: {product_version}")
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
            battery_window.after(0, lambda: progress_bar_disk.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    # Buttons

    # 003d3d

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
        command=on_install,
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


def rai_screen():
    # Check if BN is chosen
    if BN == 0:
        messagebox.showerror("Battery number", "Please choose a battery number to continue.")
        return

    # Clear existing buttons
    on_button_click()

    # Add Label
    rai_label = tk.Label(root, text='Remote App Installation', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    rai_label.place(x=138, y=10)
    buttons.append(rai_label)

    # Create Buttons with Hover Effects
    create_button(root, 'Battery', open_battery_window, 178, 420)
    create_button(root, 'Regional', open_regional_window, 178, 490)
    create_button(root, 'VSIL', open_vsil_window, 178, 560)
    create_button(root, 'Simulator', open_simulator_window, 178, 630)
    create_button(root, 'Back', main_screen, 14, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)

    # if len(installation_app_remote_message) == 0:
    #     messagebox.showinfo("Don't forget", "The new version of the application should be on the local disk: C:\\FBE")
    #     installation_app_remote_message.append("onetime")


def main_screen():
    on_button_click()

    def save_value():
        global BN
        selected_value = dropdown_var.get()
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
    create_button(root, 'Remote App Installation', rai_screen, 178, 420)
    create_button(root, 'Checks Remote Components', open_vsil_window, 178, 490)
    create_button(root, 'Cyber Deployment', open_battery_window, 178, 560)
    create_button(root, 'Tools', lambda: on_click(None), 360, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)


main_screen()
root.mainloop()
