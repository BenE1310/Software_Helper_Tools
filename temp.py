import json
import os
import platform
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

def open_ping_monitor():
    """
    Open a Toplevel window that displays a scrollable list of hostnames,
    pings them continuously in a background thread, highlights the current host,
    shows user alerts if the file is missing or invalid, and falls back to defaults
    if necessary.
    """

    # 1) Create the Toplevel first, so message dialogs can use it as a parent
    ping_window = tk.Toplevel()
    ping_window.title("Ping Monitor")
    ping_window.resizable(False, False)  # Disallow resizing
    # ping_window.iconbitmap(temp_icon_path)  # Optional: set window icon
    ping_window.geometry("300x900")

    # 2) Define default data
    default_hosts = [
        {
            "hostname": "Default Host",
            "ip": "192.168.0.1"
        }
    ]

    # 3) Attempt to load JSON
    def load_json(filename, parent_window):
        """
        Check if file exists; if not, show an error & info message, return None.
        If file exists but has invalid JSON, also show an error & info, return None.
        Otherwise return the parsed JSON.
        """
        if not os.path.exists(filename):
            messagebox.showerror(
                "File Not Found",
                f"The file '{filename}' doesn't exist.",
                parent=parent_window
            )
            messagebox.showinfo(
                "Loading Hosts",
                "Loading default file instead.",
                parent=parent_window
            )
            return None

        # Now try to parse it
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror(
                "JSON Loading Error",
                f"Failed to load JSON from '{filename}':\n\n{e}",
                parent=parent_window
            )
            messagebox.showinfo(
                "Loading Hosts",
                "Loading default file instead.",
                parent=parent_window
            )
            return None

    # 4) Load or fallback
    filename = 'Config\\pingBat.json'
    hosts_data = load_json(filename, ping_window)
    if hosts_data is None:
        hosts = default_hosts
    else:
        hosts = hosts_data

    # 5) Event used to stop the ping cycle thread
    stop_event = threading.Event()

    # 6) Ping logic
    def ping_host(ip):
        current_os = platform.system().lower()
        if 'windows' in current_os:
            cmd = f'ping -n 1 {ip} > NUL 2>&1'
        else:
            cmd = f'ping -c 1 {ip} > /dev/null 2>&1'
        response = os.system(cmd)
        return (response == 0)

    labels = []
    default_bg = []

    # Safe UI update functions (avoid TclError if window closes mid-update)
    def highlight_label(index):
        try:
            labels[index].config(bg='yellow')
        except tk.TclError:
            pass

    def unhighlight_label(index):
        try:
            labels[index].config(bg=default_bg[index])
        except tk.TclError:
            pass

    def update_label_color(index, reachable):
        try:
            if reachable:
                labels[index].config(fg='green')
            else:
                labels[index].config(fg='red')
        except tk.TclError:
            pass

    def ping_cycle():
        while not stop_event.is_set():
            for i, host in enumerate(hosts):
                if stop_event.is_set():
                    break

                # Highlight
                ping_window.after(0, highlight_label, i)

                # Ping
                reachable = ping_host(host["ip"])

                # Update color
                ping_window.after(0, update_label_color, i, reachable)

                # Unhighlight
                ping_window.after(0, unhighlight_label, i)

                time.sleep(1)

    def close_ping_window():
        stop_event.set()
        ping_window.destroy()

    ping_window.protocol("WM_DELETE_WINDOW", close_ping_window)

    # 7) UI Layout
    # Title label
    top_label = tk.Label(ping_window, text="Ping Monitor", font=("Arial", 16, "bold"))
    top_label.pack(side="top", pady=10)

    # Scrollable container
    container = tk.Frame(ping_window)
    container.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    canvas = tk.Canvas(container)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Create labels for each host
    for host_item in hosts:
        hostname = host_item["hostname"]
        lbl = tk.Label(scrollable_frame, text=hostname, font=("Arial", 12, "bold"))
        lbl.pack(pady=5, padx=10, anchor="w")
        labels.append(lbl)
        default_bg.append(lbl.cget("bg"))

    # Close button at bottom
    close_button = tk.Button(
        ping_window,
        text="Close",
        font=("Arial", 12, "bold"),
        command=close_ping_window
    )
    close_button.pack(pady=10)

    # 8) Start background thread
    thread = threading.Thread(target=ping_cycle, daemon=True)
    thread.start()



def main():
    """Main window with a button to open the Ping Monitor."""
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("300x200")
    root.resizable(False, False)

    label = tk.Label(root, text="This is the main application window", font=("Arial", 12))
    label.pack(pady=20)

    open_button = tk.Button(
        root,
        text="Open Ping Monitor",
        font=("Arial", 12, "bold"),
        command=open_ping_monitor
    )
    open_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
