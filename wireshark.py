import os
import subprocess

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
