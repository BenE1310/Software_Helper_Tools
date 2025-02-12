import win32file
import pefile
import os


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


# Example usage
remote_server = "192.168.3.141"  # Replace with the name or IP of the remote computer
file_path = r"C$\Program Files\7-Zip\7z.exe"  # Replace with the actual path to the file on the remote computer

version_info = get_remote_file_version(remote_server, file_path)
print(version_info['Product Version'])
