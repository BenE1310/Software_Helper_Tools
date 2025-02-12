import winreg


def query_remote_registry(remote_computer, registry_path, search_name):
    try:
        # Connect to the remote registry
        reg = winreg.ConnectRegistry(remote_computer, winreg.HKEY_LOCAL_MACHINE)

        # Open the specified registry key
        key = winreg.OpenKey(reg, registry_path)

        results = []

        # Iterate through subkeys
        i = 0
        while True:
            try:
                # Get the name of the subkey
                subkey_name = winreg.EnumKey(key, i)
                subkey_path = f"{registry_path}\\{subkey_name}"

                # Open the subkey
                subkey = winreg.OpenKey(reg, subkey_path)

                # Get the values for DisplayName and DisplayVersion
                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                display_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]

                # Check if the display name matches the search term
                if search_name.lower() in display_name.lower():
                    results.append({"DisplayName": display_name, "DisplayVersion": display_version})

                winreg.CloseKey(subkey)
            except FileNotFoundError:
                pass
            except OSError:
                break

            i += 1

        winreg.CloseKey(key)
        winreg.CloseKey(reg)

        return results

    except Exception as e:
        print(f"Error querying the registry: {e}")
        return []


# Parameters
remote_computer = r"\\pc-bene"  # Remote computer name (use \\ before the name)
registry_path_one = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
registry_path_two = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"

search_name = ["7-Zip", "Npcap", "Notepad++"]

# Query the remote registry
for software in search_name:

    results = query_remote_registry(remote_computer, registry_path_one, software)
# Display results
    if results:
        for result in results:
            print(f"DisplayName: {result['DisplayName']}, DisplayVersion: {result['DisplayVersion']}")
    elif len(results) == 0:
        results = query_remote_registry(remote_computer, registry_path_two, software)
        for result in results:
            print(f"DisplayName: {result['DisplayName']}, DisplayVersion: {result['DisplayVersion']}")
    else:
        print("No matching applications found.")


