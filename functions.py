import os
import subprocess
import platform
import time

import pefile
import win32file
import wmi
import pythoncom  # Import pythoncom for WMI operations



def check_communication(ip):
    """
    Ping a server to test communication.

    Parameters:
        ip (str): The IP address to test.

    Returns:
        bool: True if communication is successful, False otherwise.
    """
    # Determine the ping command based on the operating system
    if platform.system().lower() == "windows":
        ping_command = ["ping", "-n", "1"]
    else:
        ping_command = ["ping", "-c", "1"]

    try:
        # Run the ping command and capture the output
        result = subprocess.run(
            ping_command + [ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Successful communication if return code is 0
        return result.returncode == 0
    except Exception as e:
        print(f"Error during communication check with {ip}: {e}")
        return False



def check_permissions(network_path):
    """
    Check if the user has read and write permissions on a network path.

    Args:
        network_path (str): The path to the network location.

    Returns:
        dict: A dictionary indicating read and write permissions.
    """
    result = {
        "readable": False,
        "writable": False
    }

    # Check if the path is accessible and readable
    if os.path.exists(network_path) and os.access(network_path, os.R_OK):
        result["readable"] = True

    # Check if the path is writable
    test_file = os.path.join(network_path, ".test_write_permission")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)  # Clean up
        result["writable"] = True
    except Exception as e:
        print(f"Write check failed for {network_path}: {e}")

    return result


def get_drive_space(remote_host):
    try:
        # Connect to the remote host using current session credentials
        connection = wmi.WMI(computer=remote_host)

        # Query the logical disk information for the C: drive
        for disk in connection.Win32_LogicalDisk(DriveType=3):
            if disk.DeviceID == "C:":
                free_space = int(disk.FreeSpace) / (1024 ** 3)  # Convert bytes to GB
                total_space = int(disk.Size) / (1024 ** 3)  # Convert bytes to GB
                percentage_free = (free_space / total_space) * 100  # Calculate free space percentage
                return free_space, total_space, percentage_free
        return None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None


def get_remote_file_version(remote_server, file_path):
    try:
        # Construct the UNC path for the remote file
        unc_path = fr"\\{remote_server}\{file_path}"

        # Open the remote file
        handle = win32file.CreateFile(
            unc_path,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

        # Read the file's content
        file_data = win32file.ReadFile(handle, os.path.getsize(unc_path))[1]
        handle.Close()

        # Use pefile to extract version information
        pe = pefile.PE(data=file_data)
        version_info = pe.FileInfo[0][0].StringTable[0].entries

        # Extract and decode version details
        product_version = version_info.get(b"ProductVersion", b"Unknown").decode()
        file_version = version_info.get(b"FileVersion", b"Unknown").decode()

        return {
            "Product Version": product_version,
            "File Version": file_version
        }

    except Exception as e:
        return {"error": str(e)}




def install_client(host, ip, bat_file_path, BN):
    """
    Handle the installation process for a single client.
    """
    try:
        # Customize the .bat file for the client
        fourth_octet = ip.split(".")[-1]
        current_bat_file = f"BatteryClient_{fourth_octet}.bat"
        print(current_bat_file)
        temp_bat_path = f".\\temp\\{current_bat_file}"

        change_bat_pos_function(bat_file_path, BN=BN, PN=fourth_octet, output_path=temp_bat_path)

        # Deploy and execute the customized .bat file
        prepare_installation(ip_base=ip, host_type=host)
        print(f"Installation completed for {host} ({ip})")
    except Exception as e:
        print(f"Error during installation for {host} ({ip}): {e}")


def change_bat_pos_function(bat_file_path, BN, PN, output_path, logs):
    """
    Update or create a customized .bat file for the client.
    """
    try:
        # Ensure the output directory exists
        temp_dir = os.path.dirname(output_path)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Read the content of the original .bat file
        with open(bat_file_path, "r") as bat_file:
            lines = bat_file.readlines()

        # Update the BN and PN variables
        for i, line in enumerate(lines):
            if line.strip().startswith("set /a BN="):
                lines[i] = f"set /a BN={BN}\n"
            if line.strip().startswith("set /a PN="):
                lines[i] = f"set /a PN={PN}\n"

        # Write the updated content to the output file
        with open(output_path, "w") as output_file:
            output_file.writelines(lines)

        logs.append(f"Customized .bat file created at {output_path} with BN={BN}, PN={PN}.")
    except Exception as e:
        logs.append(f"Error in change_bat_pos_function: {e}")








def prepare_installation(ip_base, host_type, current_bat_file, scripts_src=None, logs=None, progress_var=None, progress_label=None, step_increment=0):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    unc_path = f"\\\\{ip_base}\\c$"

    try:
        # Map the UNC path to a drive letter
        logs.append(f"Mapping {unc_path} to {drive_letter}...")
        os.system(f"net use {drive_letter} {unc_path}")

        # Define paths using the mapped drive
        scripts_dest = f"{drive_letter}\\FBE1\\Scripts\\BMC"
        zip_dest = f"{drive_letter}\\FBE1\\Zip"
        tools_dest = f"{drive_letter}\\FBE1\\Tools"
        remote_bat_path = f"{drive_letter}\\FBE1\\Scripts\\BMC\\{current_bat_file}"

        zip_src = "C:\\FBE\\Zip\\BatteryClient.7z"
        tools_src = "C:\\FBE\\Tools"

        # Step 1: Copy script file
        logs.append(f"Copying script file to {scripts_dest}...")
        os.system(f"echo D | xcopy \"{scripts_src}\" \"{scripts_dest}\" /E /Y /I")
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")

        # Step 2: Copy zip file
        logs.append(f"Copying zip file to {zip_dest}...")
        os.system(f"echo D | xcopy \"{zip_src}\" \"{zip_dest}\" /E /Y /I")
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")

        # Step 3: Copy tools
        logs.append(f"Copying tools to {tools_dest}...")
        os.system(f"echo D |xcopy \"{tools_src}\" \"{tools_dest}\" /E /Y /I")
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")

        # Step 4: Execute batch file
        logs.append(f"Executing batch file {remote_bat_path}...")
        subprocess.run(["cmd", "/c", remote_bat_path])
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")
    except Exception as e:
        logs.append(f"Error during installation: {e}")
    finally:
        # Remove the drive mapping
        logs.append(f"Unmapping {drive_letter}...")
        os.system(f"net use {drive_letter} /delete")







def cleanup_temp_files():
    """
    Delete all temporary .bat files created during installation.
    """
    temp_dir = ".\\temp"
    for file in os.listdir(temp_dir):
        if file.endswith(".bat"):
            os.remove(os.path.join(temp_dir, file))
    print("Temporary files cleaned up.")