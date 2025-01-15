import wmi


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


if __name__ == "__main__":
    # Replace with the remote host's details
    remote_host = "192.168.3.141"  # Remote machine's IP address or hostname

    free_space, total_space, percentage_free = get_drive_space(remote_host)

    if free_space is not None and total_space is not None:
        print(f"Free space on C: drive: {free_space:.2f} GB")
        print(f"Total space on C: drive: {total_space:.2f} GB")
        print(f"Percentage of free space: {percentage_free:.2f}%")

        if percentage_free < 30:
            print("Cannot install")
        else:
            print("Installation can continue")
    else:
        print("Failed to retrieve drive space information.")
