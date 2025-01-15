import os

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

def check_multiple_permissions(paths):
    """
    Check read and write permissions for multiple paths.

    Args:
        paths (list): A list of network paths.

    Returns:
        dict: A dictionary with permissions for each path.
    """
    permissions = {}
    for path in paths:
        permissions[path] = check_permissions(path)
    return permissions


# Example usage
paths_to_check = [
    r"\\192.168.3.141\c$\temp",  # Replace with your first network path
    r"\\192.168.3.135\c$\temp"   # Replace with your second network path
]

permissions = check_multiple_permissions(paths_to_check)

for path, perms in permissions.items():
    print(f"\nPath: {path}")
    if perms["readable"]:
        print("  - Read access: YES")
    else:
        print("  - Read access: NO")

    if perms["writable"]:
        print("  - Write access: YES")
    else:
        print("  - Write access: NO")




network_path = r"\\192.168.3.141\c$\temp"  # Replace with your actual network path
