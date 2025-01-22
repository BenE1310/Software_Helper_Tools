# Prompt the user to enter the BN value
BN=5
# Prompt the user to enter the PN value
PN=43

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





def change_bat_pos_function(bat_file_path):
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

change_bat_pos_function(ics_bat)







