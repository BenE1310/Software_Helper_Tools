import os
import subprocess
import platform
import time
from datetime import datetime
from tkinter import messagebox

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
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    unc_path = f"\\\\{ip_base}\\c$"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    zip_src_db_1 = "C:\\VSIL\\Zip\\DB.7z"
    zip_src_db_2 = "C:\\VSIL\\Zip\\WD_Common.7z"

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
        scripts_dest = f"{drive_letter}\\VSIL_{timestamp}\\Scripts\\{folder_name}"
        zip_dest = f"{drive_letter}\\VSIL_{timestamp}\\Zip"
        tools_dest = f"{drive_letter}\\VSIL_{timestamp}\\Tools"
        remote_bat_path = f"{scripts_dest}\\{current_bat_file}"

        if "BMC1" in host_type or "BMC2" in host_type or "BMC3" in host_type or "BMC4" in host_type:
            zip_src = "C:\\VSIL\\Zip\\BMC_Server.7z"
        elif "ICS1" in host_type or "ICS2" in host_type or "ICS3" in host_type or "ICS4" in host_type:
            zip_src = "C:\\VSIL\\Zip\\ICS.7z"
        elif "DB-BAT" in host_type or "DB-CBMC" in host_type:
            zip_src = "C:\\VSIL\\Zip\\mDRS.7z"
        elif "TCS-Server" in host_type:
            zip_src = "C:\\VSIL\\Zip\\TCS_Server.7z"
        elif "TCS Client" in host_type:
            zip_src = "C:\\VSIL\\Zip\\TCS_Client.7z"
        elif "AD-BAT" in host_type or "AD-CBMC" in host_type or "AV-BAT" in host_type or "AV-CBMC" in host_type:
            zip_src = "C:\\VSIL\\Zip\\WD_Common.7z"
        elif "CBMC Client" in host_type:
            zip_src = "C:\\VSIL\\Zip\\CBMC_Client.7z"
        else:
            zip_src = "C:\\VSIL\\Zip\\CBMC_Server.7z"

        tools_src = "C:\\VSIL\\Tools"

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


def handle_adding_launchers_battery(bat_num, pos_num, current_bat_file, current_sql_file, logs=None, results_text=None):
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
            messagebox.showerror("Error", "Network issue detected! Ensure the drive is not already mapped.")
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
            messagebox.showerror("Error", "Check whether you have 'sqlcmd' installed in the component you are trying to install from.")
            update_results_text(results_text, "Error: 'sqlcmd' is not recognized as an internal or external command")
            raise Exception(f"Mapping failed: {run_remote_script.stderr.strip()}")  # Stops function execution

    except Exception as e:
        log_message = f"Error during execution: {e}"
        logs.append(log_message)
        update_results_text(results_text, log_message)
        messagebox.showerror("Error", "The process failed. Ensure all dependencies are installed and communication stability to the DB server and try again.")
        return

    finally:
        # Step 4: Unmap the drive
        log_message = f"Unmapping {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        os.system(f"net use {drive_letter} /delete")



def handle_tables_battery(bat_num, bat_pos, current_bat_file, logs=None, results_text=None):
    """
    Prepare the installation process for a host.
    """
    logs = logs or []
    drive_letter = "P:"  # Use any available drive letter
    db_ip = f"10.11.{bat_num}8.{bat_pos}"
    unc_path = f"\\\\{db_ip}\\c$"
    scripts_src = f".\\Scripts\\SQL\\{current_bat_file}"

    try:
        # Step 1: Map the drive
        log_message = f"Mapping {unc_path} to {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)

        mapping_result = subprocess.run(f'net use {drive_letter} {unc_path}', shell=True, capture_output=True, text=True)

        if mapping_result.returncode != 0 or "System error 64" in mapping_result.stderr:
            raise Exception(f"System error 64: {mapping_result.stderr.strip()}")

        # Step 2: Copy the script
        scripts_dest = f"{drive_letter}\\DB\\Scripts\\"
        remote_bat_path = f"{scripts_dest}{current_bat_file}"
        log_message = f"Copying script file to {scripts_dest}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)

        copy_result = subprocess.run(f'echo D | xcopy "{scripts_src}" "{scripts_dest}" /E /Y /I', shell=True, capture_output=True, text=True)

        if copy_result.returncode != 0 or "The system cannot find the drive specified" in copy_result.stderr:
            raise Exception(f"Invalid drive specification: {copy_result.stderr.strip()}")

        # Step 3: Execute the batch file
        log_message = f"Executing batch file {remote_bat_path}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        subprocess.run(["cmd", "/c", remote_bat_path])

    except Exception as e:
        log_message = f"Error during execution: {e}"
        logs.append(log_message)
        update_results_text(results_text, log_message)

        # Ensure the error popup appears
        messagebox.showerror("Error", "The process failed. Ensure all dependencies are installed and check DB server connection.")

    finally:
        # Step 4: Unmap the drive
        log_message = f"Unmapping {drive_letter}..."
        logs.append(log_message)
        update_results_text(results_text, log_message)
        os.system(f"net use {drive_letter} /delete")



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
