# Prompt the user to enter the BN value
bn_value = input("Enter the BN value: ")

# Prompt the user to enter the PN value
pn_value = input("Enter the PN value: ")

# Define the path to the BAT file
bat_file_path = "Scripts/Software_Installation/test.bat"

# Read the existing content of the BAT file
with open(bat_file_path, "r") as bat_file:
    lines = bat_file.readlines()

# Function to update or add a variable
def update_or_add_variable(lines, variable_name, value, position):
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{variable_name}="):
            lines[i] = f"{variable_name}={value}\n"
            found = True
            break
    if not found:
        # If the variable was not found, add it at the specified position
        lines.insert(position, f"{variable_name}={value}\n")
    return lines

# Update or add BN and PN values
lines = update_or_add_variable(lines, "BN", bn_value, 2)  # Third line (index 2)
lines = update_or_add_variable(lines, "PN", pn_value, 3)  # Fourth line (index 3)

# Write the modified content back to the BAT file
with open(bat_file_path, "w") as bat_file:
    bat_file.writelines(lines)

print(f"BN={bn_value} and PN={pn_value} have been updated in {bat_file_path}")








