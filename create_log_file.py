import os
import shutil
import socket
import getpass
import ctypes
from datetime import datetime

# Define log directory and file
LOG_DIR = os.path.join(".", "logs")
LOG_FILE = os.path.join(LOG_DIR, "log_file.log")


def get_system_info():
    """Returns system information: Username, Admin status, Computer name, and IP Address."""
    username = getpass.getuser()
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0  # True if running as admin
    computer_name = socket.gethostname()

    # Get primary IP address
    try:
        ip_address = socket.gethostbyname(computer_name)
    except socket.gaierror:
        ip_address = "Unknown"

    return username, is_admin, computer_name, ip_address


def setup_logging():
    """Ensures the log directory exists, rotates the old log file, and initializes the new log file."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # Create logs directory if it doesn't exist

    if os.path.exists(LOG_FILE):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(LOG_DIR, f"log_file_{timestamp}.log")
        shutil.move(LOG_FILE, backup_file)  # Rename the old log file

    # Write initial log information
    username, is_admin, computer_name, ip_address = get_system_info()

    with open(LOG_FILE, "w") as log_file:
        log_file.write("Welcome to the \"Software Helper Tools\" program!\n")
        log_file.write(f"Username: {username}, Admin: {is_admin}\n")
        log_file.write(f"Computer Name: {computer_name}, IP Address: {ip_address}\n")
        log_file.write("-" * 60 + "\n")  # Separator for readability


def log_message(level, message):
    """Logs a message with a timestamp, level, and message to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Format timestamp
    log_entry = f"{timestamp} - {level.upper()} {message}\n"

    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)


# Setup logging at script start
setup_logging()

# Example Usage
log_message("ERROR", "'.NET Framework 3.5' is not installed")
log_message("INFO", "Application started successfully")
log_message("WARNING", "Low disk space on drive C")