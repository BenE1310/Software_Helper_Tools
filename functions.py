import json
import os
import subprocess
import platform
import sys
import threading
import time
import winreg
from datetime import datetime
from tkinter import messagebox
import re
import pefile
import win32file
import wmi
import tkinter as tk

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
    """
    Safely reads PE version info from a remote file or a mapped drive path.
    If the file doesn't contain version info, or is missing pieces,
    we handle it gracefully.
    """
    try:
        # If file_path starts with a drive letter (like "V:"), treat it as is.
        # Otherwise, build a UNC path.
        if os.path.splitdrive(file_path)[0]:  # means file_path has a drive letter
            final_path = file_path
        else:
            final_path = fr"\\{remote_server}\{file_path}"

        print("Opening file:", final_path)

        # Open the remote (or local) file handle
        handle = win32file.CreateFile(
            final_path,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

        # Read the file content
        size_on_disk = os.path.getsize(final_path)
        file_data = win32file.ReadFile(handle, size_on_disk)[1]
        handle.Close()

        # Parse the PE data
        pe = pefile.PE(data=file_data)

        product_version = None
        file_version = None

        # Safely extract version info
        if hasattr(pe, 'FileInfo') and pe.FileInfo:
            for fileinfo in pe.FileInfo:
                for entry in fileinfo:
                    # Check if this entry has a StringTable
                    if hasattr(entry, 'StringTable'):
                        for st in entry.StringTable:
                            if b"ProductVersion" in st.entries:
                                product_version = st.entries[b"ProductVersion"].decode(errors='replace')
                            if b"FileVersion" in st.entries:
                                file_version = st.entries[b"FileVersion"].decode(errors='replace')
                    # Some PE files store version info in a "Var" structure
                    # but typically "StringTable" is what we want.

        if not product_version and not file_version:
            # No version info found
            return {"error": "Version resource not found in PE"}

        # Default to "Unknown" if one of them is missing
        product_version = product_version if product_version else "Unknown"
        file_version = file_version if file_version else "Unknown"

        return {
            "Product Version": product_version,
            "File Version": file_version
        }

    except Exception as e:
        return {"error": str(e)}

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


def prepare_installation_vsil(ip_base, host_type, current_bat_file, scripts_src=None, logs=None, progress_var=None, progress_label=None, step_increment=0):
    """
    Prepare the installation process for a host.
    """
    # Define the JSON file name
    json_file = "Config\\site.json"

    # Check if file exists
    if not os.path.exists(json_file):
        print("site.json file doesn't exist. Loading from default.")
        site = "VSIL"
    else:
        # Load JSON data
        with open(json_file, "r") as file:
            data = json.load(file)
        site = data.get("site")

    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    unc_path = f"\\\\{ip_base}\\c$"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    zip_src_db_1 = f"C:\\{site}\\Zip\\DB.7z"
    zip_src_db_2 = f"C:\\{site}\\Zip\\WD_Common.7z"

    # Determine the destination folder based on host type
    if "BMC1" in host_type or "BMC2" in host_type or "BMC3" in host_type or "BMC4" in host_type or "ICS1" in host_type or "ICS2" in host_type or "ICS3" in host_type or "ICS4" in host_type:
        folder_name = "BMC"
    elif "DB-BAT" in host_type or "DB-CBMC" in host_type:
        folder_name = "DB"
    elif "TCS-Server" in host_type or "TCS-Client" in host_type:
        folder_name = "TCS"
    elif "AD-BAT" in host_type or "AD-CBMC" in host_type or "AV-BAT" in host_type or "AV-CBMC" in host_type:
        folder_name = "GeneralServer"
    else:
        folder_name = "CBMC"  # Fallback for any other type

    try:
        # Map the UNC path to a drive letter
        logs.append(f"Mapping {unc_path} to {drive_letter}...")
        os.system(f"net use {drive_letter} {unc_path}")

        # Define paths using the mapped drive and determined folder name
        scripts_dest = f"{drive_letter}\\{site}_{timestamp}\\Scripts\\{folder_name}"
        zip_dest = f"{drive_letter}\\{site}_{timestamp}\\Zip"
        tools_dest = f"{drive_letter}\\{site}_{timestamp}\\Tools"
        remote_bat_path = f"{scripts_dest}\\{current_bat_file}"

        if "BMC1" in host_type or "BMC2" in host_type or "BMC3" in host_type or "BMC4" in host_type:
            zip_src = f"C:\\{site}\\Zip\\BMC_Server.7z"
        elif "ICS1" in host_type or "ICS2" in host_type or "ICS3" in host_type or "ICS4" in host_type:
            zip_src = f"C:\\{site}\\Zip\\ICS.7z"
        elif "DB-BAT" in host_type or "DB-CBMC" in host_type:
            zip_src = f"C:\\{site}\\Zip\\mDRS.7z"
        elif "TCS-Server" in host_type:
            zip_src = f"C:\\{site}\\Zip\\TCS_Server.7z"
        elif "TCS Client" in host_type:
            zip_src = f"C:\\{site}\\Zip\\TCS_Client.7z"
        elif "AD-BAT" in host_type or "AD-CBMC" in host_type or "AV-BAT" in host_type or "AV-CBMC" in host_type:
            zip_src = f"C:\\{site}\\Zip\\WD_Common.7z"
        elif "CBMC Client" in host_type:
            zip_src = f"C:\\{site}\\Zip\\CBMC_Client.7z"
        else:
            zip_src = f"C:\\{site}\\Zip\\CBMC_Server.7z"

        tools_src = f"C:\\{site}\\Tools"

        # Step 1: Copy script file
        logs.append(f"Copying script file to {scripts_dest}...")
        os.system(f"echo D | xcopy \"{scripts_src}\" \"{scripts_dest}\" /E /Y /I")
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")

        # Step 2: Copy zip file
        if "DB-BAT" in host_type or "DB-CBMC" in host_type:
            logs.append(f"Copying zips file to {zip_dest}...")
            os.system(f"echo D | xcopy \"{zip_src}\" \"{zip_dest}\" /E /Y /I")
            os.system(f"echo D | xcopy \"{zip_src_db_1}\" \"{zip_dest}\" /E /Y /I")
            os.system(f"echo D | xcopy \"{zip_src_db_2}\" \"{zip_dest}\" /E /Y /I")
        else:
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


def prepare_installation_simulator(ip_base, host_type, current_bat_file, scripts_src=None, logs=None, progress_var=None, progress_label=None, step_increment=0):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    unc_path = f"\\\\{ip_base}\\c$"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")


    # Determine the destination folder based on host type

    folder_name = "Simulator"  # Fallback for any other type

    try:
        # Map the UNC path to a drive letter
        logs.append(f"Mapping {unc_path} to {drive_letter}...")
        os.system(f"net use {drive_letter} {unc_path}")

        # Define paths using the mapped drive and determined folder name
        scripts_dest = f"{drive_letter}\\FBE_{timestamp}\\Scripts\\{folder_name}"
        zip_dest = f"{drive_letter}\\FBE_{timestamp}\\Zip"
        tools_dest = f"{drive_letter}\\FBE_{timestamp}\\Tools"
        remote_bat_path = f"{scripts_dest}\\{current_bat_file}"

        if "BMC" in host_type:
            zip_src = "C:\\FBE\\Zip\\BatteryServer.7z"
        elif "DB" in host_type:
            zip_src = "C:\\FBE\\Zip\\mDRS.7z"
        elif "ICS" in host_type:
            zip_src = "C:\\FBE\\Zip\\ICS.7z"
        else:
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
        os.system(f"echo D | xcopy \"{tools_src}\" \"{tools_dest}\" /E /Y /I")
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


def prepare_installation_regional(ip_base, host_type, current_bat_file, scripts_src=None, logs=None, progress_var=None, progress_label=None, step_increment=0):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    unc_path = f"\\\\{ip_base}\\c$"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")


    # Determine the destination folder based on host type
    if "CBMC" in host_type or "Client" in host_type:
        folder_name = "CBMC"
    elif "DB" in host_type:
        folder_name = "DB"
    else:
        folder_name = "Default"  # Fallback for any other type

    try:
        # Map the UNC path to a drive letter
        logs.append(f"Mapping {unc_path} to {drive_letter}...")
        os.system(f"net use {drive_letter} {unc_path}")

        # Define paths using the mapped drive and determined folder name
        scripts_dest = f"{drive_letter}\\FBE_{timestamp}\\Scripts\\{folder_name}"
        zip_dest = f"{drive_letter}\\FBE_{timestamp}\\Zip"
        tools_dest = f"{drive_letter}\\FBE_{timestamp}\\Tools"
        remote_bat_path = f"{scripts_dest}\\{current_bat_file}"

        if "BMC" in host_type:
            zip_src = "C:\\FBE\\Zip\\BatteryServer.7z"
        elif "DB" in host_type:
            zip_src = "C:\\FBE\\Zip\\mDRS.7z"
        elif "ICS" in host_type:
            zip_src = "C:\\FBE\\Zip\\ICS.7z"
        else:
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
        os.system(f"echo D | xcopy \"{tools_src}\" \"{tools_dest}\" /E /Y /I")
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


def prepare_installation_battery(ip_base, host_type, current_bat_file, scripts_src=None, logs=None, progress_var=None, progress_label=None, step_increment=0):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    unc_path = f"\\\\{ip_base}\\c$"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    zip_src_db_1 = "C:\\FBE\\Zip\\DB.7z"


    # Determine the destination folder based on host type
    if "BMC" in host_type or "Client" in host_type or "ICS" in host_type:
        folder_name = "BMC"
    elif "DB" in host_type:
        folder_name = "DB"
    else:
        folder_name = "Default"  # Fallback for any other type

    try:
        # Map the UNC path to a drive letter
        logs.append(f"Mapping {unc_path} to {drive_letter}...")
        os.system(f"net use {drive_letter} {unc_path}")

        # Define paths using the mapped drive and determined folder name
        scripts_dest = f"{drive_letter}\\FBE_{timestamp}\\Scripts\\{folder_name}"
        zip_dest = f"{drive_letter}\\FBE_{timestamp}\\Zip"
        tools_dest = f"{drive_letter}\\FBE_{timestamp}\\Tools"
        remote_bat_path = f"{scripts_dest}\\{current_bat_file}"

        if "BMC" in host_type:
            zip_src = "C:\\FBE\\Zip\\BatteryServer.7z"
        elif "DB" in host_type:
            zip_src = "C:\\FBE\\Zip\\mDRS.7z"
        elif "ICS" in host_type:
            zip_src = "C:\\FBE\\Zip\\ICS.7z"
        else:
            zip_src = "C:\\FBE\\Zip\\BatteryClient.7z"

        tools_src = "C:\\FBE\\Tools"

        # Step 1: Copy script file
        logs.append(f"Copying script file to {scripts_dest}...")
        os.system(f"echo D | xcopy \"{scripts_src}\" \"{scripts_dest}\" /E /Y /I")
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")

        # Step 2: Copy zip file
        if "DB" in host_type:
            logs.append(f"Copying zips file to {zip_dest}...")
            os.system(f"echo D | xcopy \"{zip_src}\" \"{zip_dest}\" /E /Y /I")
            os.system(f"echo D | xcopy \"{zip_src_db_1}\" \"{zip_dest}\" /E /Y /I")
        else:
            logs.append(f"Copying zip file to {zip_dest}...")
            os.system(f"echo D | xcopy \"{zip_src}\" \"{zip_dest}\" /E /Y /I")
        progress_var.set(progress_var.get() + step_increment)
        progress_label.config(text=f"{int(progress_var.get())}%")

        # Step 3: Copy tools
        logs.append(f"Copying tools to {tools_dest}...")
        os.system(f"echo D | xcopy \"{tools_src}\" \"{tools_dest}\" /E /Y /I")
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

def handle_adding_launchers_battery(bat_num, pos_num, parent_window, current_bat_file, current_sql_file, logs=None, results_text=None):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    db_ip = f"10.11.{bat_num}8.{pos_num}"
    unc_path = f"\\\\{db_ip}\\c$"
    scripts_src = f".\\Scripts\\SQL\\{current_bat_file}"
    sql_script_src = f".\\Scripts\\SQL\\{current_sql_file}"

    # Determine the destination folder based on host type
    try:
        # Step 1: Map the drive
        log_message = f"Mapping {unc_path} to {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)

        mapping_result = subprocess.run(f'net use {drive_letter} {unc_path}', shell=True, capture_output=True, text=True)
        if mapping_result.stderr:
            print("Copy Error Output:")
            for line in mapping_result.stderr.splitlines():
                print(line)  # Print each line separately

        if "System error 64" in mapping_result.stderr or "System error 67" in mapping_result.stderr:
            messagebox.showerror("Error", "Network issue detected! Ensure the drive is not already mapped.", parent=parent_window)
            update_results_text(results_text, "Error: Network issue detected! Ensure the drive is not already mapped.")
            raise Exception(f"Mapping failed: {mapping_result.stderr.strip()}")  # Stops function execution

        # Step 2: Copy the script
        scripts_dest = f"{drive_letter}\\DB\\Scripts\\"
        sql_dest = f"{drive_letter}\\DB\\sql\\"
        remote_bat_path = f"{scripts_dest}{current_bat_file}"

        log_message = f"Copying script file to {scripts_dest}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        subprocess.run(f"echo D | xcopy \"{scripts_src}\" \"{scripts_dest}\" /E /Y /I", shell=True, capture_output=True, text=True)

        log_message_sql = f"Copying sql script file to {sql_dest}..."
        logs.append(log_message_sql)
        update_results_text(results_text, log_message_sql)
        subprocess.run(f"echo D | xcopy \"{sql_script_src}\" \"{sql_dest}\" /E /Y /I", shell=True, capture_output=True, text=True)


        # Step 3: Execute the batch file
        log_message = f"Executing batch file {remote_bat_path}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        run_remote_script = subprocess.run(["cmd", "/c", remote_bat_path], shell=True, capture_output=True, text=True)

        if run_remote_script.stderr:
            print("Copy Error Output:")
            for line in run_remote_script.stderr.splitlines():
                print(line)  # Print each line separately

        if "'sqlcmd' is not recognized as an internal or external command" in run_remote_script.stderr:
            messagebox.showerror("Error", "Check whether you have 'sqlcmd' installed in the component you are trying to install from.", parent=parent_window)
            update_results_text(results_text, "Error: 'sqlcmd' is not recognized as an internal or external command")
            raise Exception(f"Mapping failed: {run_remote_script.stderr.strip()}")  # Stops function execution

    except Exception as e:
        log_message = f"Error during execution: {e}"
        logs.append(log_message)
        update_results_text(results_text, log_message)
        messagebox.showerror("Error", "The process failed. Ensure all dependencies are installed and communication stability to the DB server and try again.", parent=parent_window)
        return

    finally:
        # Step 4: Unmap the drive
        log_message = f"Unmapping {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        os.system(f"net use {drive_letter} /delete")

def handle_tables_battery(bat_num, bat_pos, current_bat_file, parent_window, logs=None, results_text=None):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    db_ip = f"10.11.{bat_num}8.{bat_pos}"
    unc_path = f"\\\\{db_ip}\\c$"
    scripts_src = f".\\Scripts\\SQL\\{current_bat_file}"

    scripts_dest = f"{drive_letter}\\DB\\Scripts\\"
    remote_bat_path = f"{scripts_dest}{current_bat_file}"
    print(remote_bat_path)

    try:
        # Step 1: Map the drive
        log_message = f"Mapping {unc_path} to {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        logs.append(f'net use {drive_letter} {unc_path}')

        print(f'net use {drive_letter} {unc_path}')
        mapping_result = subprocess.run(f'net use {drive_letter} {unc_path}', shell=True, capture_output=True, text=True)

        if mapping_result.stderr:
            print("Copy Error Output:")
            for line in mapping_result.stderr.splitlines():
                print(line)  # Print each line separately

        if "System error 64" in mapping_result.stderr or "System error 67" in mapping_result.stderr:
            messagebox.showerror("Error", "Network issue detected! Ensure the drive is not already mapped.",parent=parent_window)
            update_results_text(results_text, "Error: Network issue detected! Ensure the drive is not already mapped.")
            raise Exception(f"Mapping failed: {mapping_result.stderr.strip()}")  # Stops function execution

        # Step 2: Copy the script


        log_message = f"Copying script file to {scripts_dest}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        subprocess.run(f'echo D | xcopy "{scripts_src}" "{scripts_dest}" /E /Y /I', shell=True, capture_output=True, text=True)


        # Step 3: Execute the batch file
        log_message = f"Executing batch file {remote_bat_path}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        run_remote_script = subprocess.run(["cmd", "/c", remote_bat_path], shell=True, capture_output=True, text=True)

        if run_remote_script.stderr:
            print("Copy Error Output:")
            for line in run_remote_script.stderr.splitlines():
                print(line)  # Print each line separately

        if "'sqlcmd' is not recognized as an internal or external command" in run_remote_script.stderr:
            messagebox.showerror("Error",
                                 "Check whether you have 'sqlcmd' installed in the component you are trying to install from.", parent=parent_window)
            update_results_text(results_text, "Error: 'sqlcmd' is not recognized as an internal or external command")
            raise Exception(f"Mapping failed: {run_remote_script.stderr.strip()}")  # Stops function execution


    except Exception as e:
        log_message = f"Error during execution: {e}"
        logs.append(log_message)
        update_results_text(results_text, log_message)

        # Ensure the error popup appears
        messagebox.showerror("Error", "The process failed. Ensure all dependencies are installed and check DB server connection.", parent=parent_window)

    finally:
        # Step 4: Unmap the drive
        log_message = f"Unmapping {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        os.system(f"net use {drive_letter} /delete")

# TODO: Add more argument to the function call 'folder' = FBE, VSIL or CIWS
def write_bat_file_db_phase(BN, PN, BAT_FILE_NAME, logs=None, results_text=None):
    """
    Writes BN, SQL_USER, and SQL_PASS values to lines 3, 4, and 5 in the BAT file.
    If the file exists, it updates only those lines. Otherwise, it creates a new file.
    """
    logs = logs or []

    new_lines = [
        f"set /a BN={BN}\n",
        f"set /a PN={PN}\n",
    ]

    BAT_FILE_PATH = f".\\Scripts\\SQL\\{BAT_FILE_NAME}"

    if os.path.exists(BAT_FILE_PATH):
        with open(BAT_FILE_PATH, "r") as file:
            existing_lines = file.readlines()

        # Ensure the file has at least 5 lines
        while len(existing_lines) < 4:
            existing_lines.append("\n")

        # Overwrite only lines 3, 4, and 5
        existing_lines[2] = new_lines[0]  # Line 3
        existing_lines[3] = new_lines[1]  # Line 4


        with open(BAT_FILE_PATH, "w") as file:
            file.writelines(existing_lines)

        log_message = f"Updated lines 3-4 in existing batch file: {BAT_FILE_PATH}"
        logs.append(log_message)
        update_results_text(results_text, log_message)
        print(f"Updated lines 3-4 in existing batch file: {BAT_FILE_PATH}")

    else:
        # If the file doesn't exist, create at least 2 empty lines before writing the values
        with open(BAT_FILE_PATH, "w") as file:
            file.writelines(["\n"] * 2)  # Ensure first 2 lines are empty
            file.writelines(new_lines)

        print(f"New batch file created with values starting at line 3: {BAT_FILE_PATH}")


def handle_adding_launchers_vsil(pos_num, parent_window, current_bat_file, current_sql_file, logs=None, results_text=None):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    db_ip = f"10.11.18.{pos_num}"
    unc_path = f"\\\\{db_ip}\\c$"
    scripts_src = f".\\Scripts\\SQL\\{current_bat_file}"
    sql_script_src = f".\\Scripts\\SQL\\{current_sql_file}"

    # Determine the destination folder based on host type
    try:
        # Step 1: Map the drive
        log_message = f"Mapping {unc_path} to {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)

        mapping_result = subprocess.run(f'net use {drive_letter} {unc_path}', shell=True, capture_output=True, text=True)
        if mapping_result.stderr:
            print("Copy Error Output:")
            for line in mapping_result.stderr.splitlines():
                print(line)  # Print each line separately

        if "System error 64" in mapping_result.stderr or "System error 67" in mapping_result.stderr:
            messagebox.showerror("Error", "Network issue detected! Ensure the drive is not already mapped.", parent=parent_window)
            update_results_text(results_text, "Error: Network issue detected! Ensure the drive is not already mapped.")
            raise Exception(f"Mapping failed: {mapping_result.stderr.strip()}")  # Stops function execution


        # Step 2: Copy the script
        scripts_dest = f"{drive_letter}\\DB\\Scripts\\"
        sql_dest = f"{drive_letter}\\DB\\sql\\"
        remote_bat_path = f"{scripts_dest}{current_bat_file}"

        log_message = f"Copying script file to {scripts_dest}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        subprocess.run(f"echo D | xcopy \"{scripts_src}\" \"{scripts_dest}\" /E /Y /I", shell=True, capture_output=True, text=True)

        log_message_sql = f"Copying sql script file to {sql_dest}..."
        logs.append(log_message_sql)
        update_results_text(results_text, log_message_sql)
        subprocess.run(f"echo D | xcopy \"{sql_script_src}\" \"{sql_dest}\" /E /Y /I", shell=True, capture_output=True, text=True)


        # Step 3: Execute the batch file
        log_message = f"Executing batch file {remote_bat_path}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        run_remote_script = subprocess.run(["cmd", "/c", remote_bat_path], shell=True, capture_output=True, text=True)

        if run_remote_script.stderr:
            print("Copy Error Output:")
            for line in run_remote_script.stderr.splitlines():
                print(line)  # Print each line separately

        if "'sqlcmd' is not recognized as an internal or external command" in run_remote_script.stderr:
            messagebox.showerror("Error", "Check whether you have 'sqlcmd' installed in the component you are trying to install from.", parent=parent_window)
            update_results_text(results_text, "Error: 'sqlcmd' is not recognized as an internal or external command")
            raise Exception(f"Mapping failed: {run_remote_script.stderr.strip()}")  # Stops function execution

    except Exception as e:
        log_message = f"Error during execution: {e}"
        logs.append(log_message)
        update_results_text(results_text, log_message)
        messagebox.showerror("Error", "The process failed. Ensure all dependencies are installed and communication stability to the DB server and try again.", parent=parent_window)
        return

    finally:
        # Step 4: Unmap the drive
        log_message = f"Unmapping {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        os.system(f"net use {drive_letter} /delete")

def update_results_text(results_text, message):
    """
    Updates the Tkinter Text widget with log messages.
    """
    if results_text:
        results_text.insert(tk.END, message + "\n")  # Append message
        results_text.see(tk.END)  # Auto-scroll to the latest log
        results_text.update_idletasks()  # Refresh GUI


def generate_sql_script_training_launchers(octet_value):
    sql_script = f"""
    -- Query for CombainTraining & Training Mode --
    DECLARE @serialNumber INTEGER
    DECLARE @sendPort INTEGER
    DECLARE @recievePort INTEGER
    SET @serialNumber = 301;
    SET @recievePort = 1301;
    SET @sendPort = 1801;

    WHILE @serialNumber < 325 
    BEGIN 
        INSERT INTO dbo.MfuAddressBook VALUES (@serialNumber, '10.12.{octet_value}8.2', @sendPort, @recievePort)
        SET @sendPort = @sendPort + 1;
        SET @serialNumber = @serialNumber + 1;
        SET @recievePort = @recievePort + 1;
    END
    """
    return sql_script


def install_wireshark():
    # Define paths
    extract_path = r'C:\WiresharkPortable'
    archive_path = r'.\Tools\Softwares\WiresharkPortable64.7z'
    seven_zip_path = r'.\Tools\7z.exe'

    # Check if the extraction path exists, if not, create it
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    # Command to extract the .7z file using 7z.exe
    command = [seven_zip_path, 'x', archive_path, f'-o{extract_path}', '-y']

    # Run the command
    subprocess.run(command, check=True)

    print("Extraction complete!")
    messagebox.showinfo("", "Done!")


def run_install_wireshark():
    threading.Thread(target=install_wireshark).start()



def install_npcap():
    try:
        npcap_exe_path = ".\\tools\\Softwares\\npcap-1.81.exe"

        if not os.path.exists(npcap_exe_path):
            raise FileNotFoundError("npcap not found.")

        # Open in a new cmd window
        subprocess.run(npcap_exe_path, shell=True, check=True)

    except FileNotFoundError:
        messagebox.showerror("Error", "npcap installation is not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start npcap installation: {e}")

def run_npcap_install():
    threading.Thread(target=install_npcap).start()


def open_wireshark():
    try:
        if not os.path.exists("C:\\WiresharkPortable\\WiresharkPortable64.exe"):
            raise FileNotFoundError("ILSpy.exe not found.")

        subprocess.run("C:\\WiresharkPortable\\WiresharkPortable64.exe", shell=True, check=True)
    except FileNotFoundError:
        messagebox.showerror("Error", "The file ILSpy.exe is not found.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to start ILSpy.exe: {e}")

def run_open_wireshark():
    threading.Thread(target=open_wireshark).start()


def install_msodbcsql():
    try:
        msodbcsql_msi_path = ".\\tools\\Softwares\\msodbcsql.msi"

        if not os.path.exists(msodbcsql_msi_path):
            raise FileNotFoundError("msodbcsql.msi not found.")

        # Open in a new cmd window
        subprocess.run(msodbcsql_msi_path, shell=True, check=True)

    except FileNotFoundError:
        messagebox.showerror("Error", "msodbcsql.msi installation is not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start msodbcsql.msi installation: {e}")

def run_msodbcsql_install():
    threading.Thread(target=install_msodbcsql).start()

def install_MsSqlCmdLnUtils():
    try:
        MsSqlCmdLnUtils_msi_path = ".\\tools\\Softwares\\MsSqlCmdLnUtils.msi"

        if not os.path.exists(MsSqlCmdLnUtils_msi_path):
            raise FileNotFoundError("MsSqlCmdLnUtils.msi not found.")

        # Open in a new cmd window
        subprocess.run(MsSqlCmdLnUtils_msi_path, shell=True, check=True)

    except FileNotFoundError:
        messagebox.showerror("Error", "MsSqlCmdLnUtils.msi installation is not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start MsSqlCmdLnUtils.msi installation: {e}")

def run_MsSqlCmdLnUtils_install():
    threading.Thread(target=install_MsSqlCmdLnUtils).start()


def add_sysinternals_to_path():
    # Determine base path depending on execution environment
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        script_dir = os.path.dirname(sys.executable)
    else:
        # Running as Python script
        script_dir = os.path.dirname(os.path.abspath(__file__))

    current_dir = os.path.normpath(os.path.join(script_dir, 'Tools'))

    # Check if there are executable files (.exe) in the Tools directory
    if not os.path.exists(current_dir):
        print(f"Tools directory not found: {current_dir}")
        input("Press Enter to exit...")
        exit()

    exe_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.exe')]

    if not exe_files:
        print("No executable files found in the Tools directory.")
        input("Press Enter to exit...")
        exit()

    # Add the Tools folder to the system PATH permanently
    def add_to_system_path(path_to_add):
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment',
                             0, winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            existing_path, regtype = winreg.QueryValueEx(key, 'Path')
            paths = existing_path.split(';')
            if path_to_add not in paths:
                paths.insert(0, path_to_add)
                new_path = ';'.join(paths)
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"Successfully added to PATH: {path_to_add}")
            else:
                print(f"Path already exists: {path_to_add}")
        except Exception as e:
            print(f"Failed to update PATH: {e}")
        finally:
            winreg.CloseKey(key)

    # Requires admin privileges
    add_to_system_path(current_dir)

    print("\nNow you can use the following Sysinternals tools from any command prompt:")
    for exe in exe_files:
        print(f"- {os.path.splitext(exe)[0]}")

    print("\nRestart your command prompt or system for changes to take effect.")
    messagebox.showinfo("Done!", "Now you can use the following Sysinternals tools" )


