import os
import subprocess
import platform

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