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
    global BN

    if BN == 0:
        messagebox.showerror("Battery number", "Please choose a battery number to continue.")
        return

    # 1) Create the Toplevel first, so message dialogs can use it as a parent
    ping_window = tk.Toplevel()
    ping_window.title("Ping Monitor")
    ping_window.resizable(False, False)  # Disallow resizing
    # ping_window.iconbitmap(temp_icon_path)  # Optional: set window icon
    ping_window.geometry("300x900")

    # 2) Define default data
    default_hosts_battery = [
      {
        "hostname": "BMC1",
        "ip": f"10.11.{BN}8.1"
      },
      {
        "hostname": "BMC2",
        "ip": f"10.11.{BN}8.2"
      },
      {
        "hostname": "ICS1",
        "ip": f"10.12.{BN}8.13"
      },
      {
        "hostname": "ICS2",
        "ip": f"10.12.{BN}8.14"
      },
      {
        "hostname": "DB1",
        "ip": f"10.11.{BN}8.3"
      },
      {
        "hostname": "DB2",
        "ip": f"10.11.{BN}8.4"
      },
      {
        "hostname": "AD1",
        "ip": f"10.11.{BN}3.20"
      },
      {
        "hostname": "AD2",
        "ip": f"10.11.{BN}3.21"
      },
      {
        "hostname": "AV",
        "ip": f"10.11.{BN}3.22"
      },
      {
        "hostname": "Client1",
        "ip": f"10.11.{BN}8.6"
      },
      {
        "hostname": "Client2",
        "ip": f"10.11.{BN}8.7"
      },
      {
        "hostname": "Client3",
        "ip": f"10.11.{BN}8.8"
      },
      {
        "hostname": "Client4",
        "ip": f"10.11.{BN}8.9"
      },
      {
        "hostname": "Client5",
        "ip": f"10.11.{BN}8.10"
      },
      {
        "hostname": "SW-BMC1",
        "ip": f"10.11.{BN}8.251"
      },
      {
        "hostname": "SW-BMC2",
        "ip": f"10.11.{BN}8.252"
      },
      {
        "hostname": "SW-ICS1",
        "ip": f"10.12.{BN}8.251"
      },
      {
        "hostname": "SW-ICS2",
        "ip": f"10.12.{BN}8.252"
      },
      {
        "hostname": "FW-BMC",
        "ip": f"10.11.{BN}8.199"
      },
      {
        "hostname": "FW-ICS",
        "ip": f"10.12.{BN}8.199"
      },
      {
        "hostname": "RTR-BMC",
        "ip": f"{BN}0.{BN}0.{BN}0.2"
      },
      {
        "hostname": "RTR-ICS",
        "ip": f"{BN}0.12.{BN}0.2"
      },
      {
        "hostname": "Rubidium",
        "ip": f"10.12.{BN}8.5"
      },
      {
        "hostname": "Uplink",
        "ip": f"10.12.{BN}8.12"
      },
    ]

    default_hosts_regional = [
      {
        "hostname": "CBMC1",
        "ip": "10.11.218.1"
      },
      {
        "hostname": "CBMC2",
        "ip": "10.11.218.2"
      },
      {
        "hostname": "CBMC-DB1",
        "ip": "10.11.218.3"
      },
      {
        "hostname": "CBMC-DB2",
        "ip": "10.11.218.4"
      },
      {
        "hostname": "AD1",
        "ip": "10.11.213.20"
      },
      {
        "hostname": "AD2",
        "ip": "10.11.213.21"
      },
      {
        "hostname": "AV1",
        "ip": "10.11.213.22"
      },
      {
        "hostname": "Client1",
        "ip": "10.11.218.50"
      },
      {
        "hostname": "Client2",
        "ip": "10.11.218.51"
      },
      {
        "hostname": "Client3",
        "ip": "10.11.218.52"
      },
      {
        "hostname": "Client4",
        "ip": "10.11.218.53"
      },
      {
        "hostname": "Client5",
        "ip": "10.11.218.54"
      },
      {
        "hostname": "Client6",
        "ip": "10.11.218.55"
      },
      {
        "hostname": "Client7",
        "ip": "10.11.218.56"
      },
      {
        "hostname": "Client8",
        "ip": "10.11.218.57"
      },
      {
        "hostname": "SW-CBMC1",
        "ip": "10.11.218.251"
      },
      {
        "hostname": "SW-CBMC2",
        "ip": "10.11.218.252"
      },
      {
        "hostname": "FW-CBMC",
        "ip": "10.11.218.199"
      },
      {
        "hostname": "RTR-BMC",
        "ip": "21.21.21.2"
      }
    ]

    default_hosts_vsil = [
      {
        "hostname": "BMC1",
        "ip": "10.11.18.1"
      },
      {
        "hostname": "BMC2",
        "ip": "10.11.28.1"
      },
      {
        "hostname": "BMC3",
        "ip": "10.11.38.1"
      },
      {
        "hostname": "BMC4",
        "ip": "10.11.48.2"
      },
      {
        "hostname": "ICS1",
        "ip": "10.12.18.13"
      },
      {
        "hostname": "ICS2",
        "ip": "10.12.28.13"
      },
      {
        "hostname": "ICS3",
        "ip": "10.12.38.13"
      },
      {
        "hostname": "ICS4",
        "ip": "10.12.48.13"
      },
      {
        "hostname": "DB-BAT",
        "ip": "10.11.18.3"
      },
      {
        "hostname": "CBMC",
        "ip": "10.11.218.1"
      },
      {
        "hostname": "DB-CBMC",
        "ip": "10.11.218.3"
      },
      {
        "hostname": "TCS Server",
        "ip": "10.11.218.2"
      },
      {
        "hostname": "TCS Client",
        "ip": "10.11.218.11"
      },
      {
        "hostname": "CBMC-Client",
        "ip": "10.11.218.50"
      },
      {
        "hostname": "AD-BAT",
        "ip": "10.11.13.20"
      },
      {
        "hostname": "AD-CBMC",
        "ip": "10.11.213.20"
      },
      {
        "hostname": "AV-BAT",
        "ip": "10.11.13.22"
      },
      {
        "hostname": "AV-CBMC",
        "ip": "10.11.213.22"
      },
      {
        "hostname": "SW-BMC",
        "ip": "10.11.18.254"
      },
      {
        "hostname": "SW-ICS",
        "ip": "10.12.18.254"
      },
      {
        "hostname": "SW-CBMC",
        "ip": "10.11.218.254"
      },
      {
        "hostname": "SW-Sec",
        "ip": "10.11.13.254"
      },
      {
        "hostname": "FW",
        "ip": "10.11.18.254"
      },
    ]

    if BN == "VSIL/CIWS":
        default_hosts = default_hosts_vsil
        env = "VSIL"
    elif BN == 21:
        default_hosts = default_hosts_regional
        env = "Regional"
    else:
        default_hosts = default_hosts_battery
        env = f"Battery {BN}"
    print(BN)



    # 3) Attempt to load JSON
    def load_json(filename, parent_window):
        """
        Check if file exists; if not, show an error & info message, return None.
        If file exists but has invalid JSON, also show an error & info, return None.
        Otherwise return the parsed JSON.
        """
        if not os.path.exists(filename):
            messagebox.showwarning(
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
    filename = 'Config\\ping.json'
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

    top_label = tk.Label(ping_window, text=env, font=("Arial", 8, "bold"))
    top_label.place(x=238,y=5)

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
        lbl.pack(pady=3, padx=10, anchor="w")
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
