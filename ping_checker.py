import subprocess
import platform

def check_server_communication(servers):
    """
    Check communication with a list of servers and identify problematic ones.

    Parameters:
        servers (list): List of server addresses to check.

    Returns:
        list: List of problematic servers with communication issues.
    """
    problematic_servers = []

    # Determine the ping command based on the operating system
    if platform.system().lower() == "windows":
        ping_command = ["ping", "-n", "1"]
    else:
        ping_command = ["ping", "-c", "1"]

    for server in servers:
        try:
            # Run the ping command and capture the output
            result = subprocess.run(
                ping_command + [server],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result.stdout.lower()

            # Check for failure messages or non-zero return code
            if "destination host unreachable" in output or "request timed out" in output or result.returncode != 0:
                print(f"Communication failed with server: {server}")
                problematic_servers.append(server)
            else:
                print(f"Communication is normal with server: {server}")
        except Exception as e:
            print(f"Error checking communication with server {server}: {e}")
            problematic_servers.append(server)

    return problematic_servers

# List of servers to check
server_list = [
    "192.168.3.240",  # Example server
    "example.com",     # Example server
    "8.8.8.8",
    "192.168.3.239"# Example server
]

# Check communication
problematic = check_server_communication(server_list)

if problematic:
    print("\nThe following servers have communication issues:")
    for server in problematic:
        print(f"- {server}")
else:
    print("All servers are reachable. Communication is normal, we can continue.")
