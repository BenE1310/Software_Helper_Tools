import os
import subprocess

# Variables


def install_client(ip_base):

    # Base IP address format

    # Define the source and destination paths
    scripts_src = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\BMC\\BatteryClient.bat"
    scripts_dest = f"\\\\{ip_base}\\c$\\FBE\\Scripts\\BMC"
    print(scripts_src)

    zip_src = "C:\\FBE\\Zip\\BatteryClient.7z"
    zip_dest = f"\\\\{ip_base}\\c$\\FBE\\Zip"

    tools_src = "C:\\FBE\\Tools"
    tools_dest = f"\\\\{ip_base}\\c$\\FBE\\Tools"

    # xcopy command template
    xcopy_command = "echo D | xcopy \"{}\" \"{}\" /E /Y /I"

    # Copy files
    os.system(xcopy_command.format(scripts_src, scripts_dest))
    os.system(xcopy_command.format(zip_src, zip_dest))
    os.system(xcopy_command.format(tools_src, tools_dest))

    # Run the .bat file on the remote server
    remote_bat_path = f"\\\\{ip_base}\\c$\\FBE\\Scripts\\BMC\\BatteryClient.bat"
    subprocess.run(["cmd", "/c", remote_bat_path])



# BMC
battery_client_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\BMC\\BatteryClient.bat"
battery_server_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\BMC\\BatteryServer.bat"
ics_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\BMC\\ICS.bat"

# CBMC
regional_client_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\CBMC\\RegionalClient.bat"
regional_server_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\CBMC\\RegionalServer.bat"

# DB
db_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\DB\\mDRS.bat"

# Simulator
simulator_client_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\Simulator\\SimulatorClient.bat"
simulator_server_bat = ".\\Scripts\\AppInstallation\\RemoteInstallation\\Installation_Scripts\\Simulator\\SimulatorServer.bat"





def change_bat_pos_function(bat_file_path, BN, PN):
# Define the path to the BAT file
    try:
        # Read the existing content of the BAT file
        with open(bat_file_path, "r") as bat_file:
            lines = bat_file.readlines()

        # Function to update or add a variable
        def update_or_add_variable_at_row(lines, row, variable_name, value):
            line_content = f"set /a {variable_name}={value}\n"
            if row < len(lines):
                # If the row exists, update it
                lines[row] = line_content
            else:
                # Otherwise, append blank lines until the row exists
                while len(lines) <= row:
                    lines.append("\n")
                lines[row] = line_content
            return lines

        # Update BN at row 6 (index 5) and PN at row 7 (index 6)
        lines = update_or_add_variable_at_row(lines, 5, "BN", BN)
        lines = update_or_add_variable_at_row(lines, 6, "PN", PN)

        # Write the modified content back to the BAT file
        with open(bat_file_path, "w") as bat_file:
            bat_file.writelines(lines)

        print(f"BN={BN} and PN={PN} have been updated in {bat_file_path}")

    except FileNotFoundError:
        print(f"Error: The file {bat_file_path} does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



# The IP address
ip = "192.168.1.141"

# Split the IP address by '.' and get the fourth octet
fourth_octet = ip.split(".")[3]

# Assign the fourth octet to the 'position' variable
PN = fourth_octet

print(f"The fourth octet is: {PN}")

BN = 1


def on_install():
    """
    Start the installation process with progress updates.
    """

    def install_task():
        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
            return

        total_hosts = len(selected_hosts)
        progress_increment = 100 / total_hosts  # Calculate progress step for each host

        for idx, host in enumerate(selected_hosts):
            ip = hostnames[host]
            try:
                # Set up paths dynamically based on host type
                if host.startswith("BMC"):
                    scripts_src = "./Scripts/AppInstallation/RemoteInstallation/Installation_Scripts/BMC/BatteryServer.bat"
                    zip_src = "C:\\FBE\\Zip\\BatteryServer.7z"
                    tools_src = "C:\\FBE\\Tools"
                elif host.startswith("Client"):
                    scripts_src = "./Scripts/AppInstallation/RemoteInstallation/Installation_Scripts/BMC/BatteryClient.bat"
                    zip_src = "C:\\FBE\\Zip\\BatteryClient.7z"
                    tools_src = "C:\\FBE\\Tools"
                else:
                    raise ValueError(f"Unsupported host type: {host}")

                scripts_dest = f"\\\\{ip}\\c$\\FBE1\\Scripts"
                zip_dest = f"\\\\{ip}\\c$\\FBE1\\Zip"
                tools_dest = f"\\\\{ip}\\c$\\FBE1\\Tools"
                remote_bat_path = f"{scripts_dest}\\{os.path.basename(scripts_src)}"

                # Execute installation steps
                print(f"Starting installation for {host} ({ip})...")
                remote_app_installation(
                    ip_base=ip,
                    scripts_src=scripts_src,
                    scripts_dest=scripts_dest,
                    zip_src=zip_src,
                    zip_dest=zip_dest,
                    tools_src=tools_src,
                    tools_dest=tools_dest,
                    remote_bat_path=remote_bat_path,
                )

                # Verify file transfer and execution
                if not os.path.exists(remote_bat_path):  # Example verification
                    raise FileNotFoundError(f"{remote_bat_path} not found on {ip}.")

                print(f"Installation completed successfully for {host} ({ip}).")

                # Update progress bar
                progress_var.set((idx + 1) * progress_increment)
                battery_window.update_idletasks()

            except Exception as e:
                print(f"Error during installation for {host}: {e}")
                messagebox.showerror("Installation Error", f"Failed for {host} ({ip}): {e}")

        print("All installations completed.")
        messagebox.showinfo("Installation Complete", "Installation process finished for all selected hosts.")

    # Run the installation in a separate thread
    threading.Thread(target=install_task).start()

