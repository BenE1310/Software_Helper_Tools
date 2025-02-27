import os
import json
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox
import pythoncom
import wmi

###############################################################################
#                               CHECK FUNCTIONS                               #
###############################################################################

def check_communication(ip):
    """Attempts to ping the given IP and returns True if successful, False otherwise."""
    try:
        result = subprocess.run(["ping", "-n", "2", ip],
                                capture_output=True, text=True, timeout=2)
        return (result.returncode == 0)
    except Exception as e:
        print(f"[EXCEPTION ping] {e}")
        return False

def check_services(ip, service_names):
    """
    Check if each service in 'service_names' is running on the remote machine (WMI).
    Returns dict {service_name: bool} indicating Running/NotRunning.
    """
    try:
        pythoncom.CoInitialize()
        conn = wmi.WMI(ip)
        statuses = {}
        for name in service_names:
            svc = conn.Win32_Service(Name=name)
            if svc:
                statuses[name] = (svc[0].State == "Running")
            else:
                statuses[name] = False
        return statuses
    except Exception as e:
        print(f"[EXCEPTION services] {e}")
        return {name: False for name in service_names}
    finally:
        pythoncom.CoUninitialize()

def check_service_user(ip, service_name, expected_user):
    """Returns True if the service is running as 'expected_user', else False."""
    try:
        pythoncom.CoInitialize()
        conn = wmi.WMI(ip)
        svc = conn.Win32_Service(Name=service_name)
        if svc:
            actual_user = svc[0].StartName
            return (actual_user == expected_user)
        return False
    except Exception as e:
        print(f"[EXCEPTION user] {e}")
        return False
    finally:
        pythoncom.CoUninitialize()

def check_service_recovery(ip, service_name, expected_recovery):
    """
    Checks service recovery with 'sc qfailure'. Expected values: 'Restart', 'RunProgram', or 'None'.
    """
    try:
        pythoncom.CoInitialize()
        cmd = ["sc"]
        if ip != "127.0.0.1":
            cmd.append(f"\\\\{ip}")
        cmd.extend(["qfailure", service_name])
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout.lower()
        restart_count = output.count("restart -- delay")

        valid = (
            (expected_recovery == "Restart" and restart_count == 3) or
            (expected_recovery == "RunProgram" and "run program" in output) or
            (expected_recovery == "None" and "none" in output)
        )
        return valid
    except Exception as e:
        print(f"[EXCEPTION recovery] {e}")
        return False
    finally:
        pythoncom.CoUninitialize()

###############################################################################
#                          BACKGROUND TEST WORKER                             #
###############################################################################

def worker_thread_func(hosts, selections, results_queue):
    """
    This function runs in a background thread.
    For each host that is 'selected' (checkbox= True), it performs all checks
    and puts the outcome in results_queue. Unselected hosts are simply reported as skipped.
    """
    total = len([h for h, var in selections.items() if var.get()])
    if total == 0:
        # If nothing is selected, just exit
        return

    processed_count = 0

    for host, info in hosts.items():
        # Skip if not selected
        if not selections[host].get():
            # We'll still send a "skipped" result to keep logic simple
            results_queue.put((host, "gray", f"{host} (Skipped)", [], processed_count, total))
            continue

        ip = info["ip"]
        logs = []
        color = "green"
        label_text = f"{host} (OK)"

        # 1) Communication
        if not check_communication(ip):
            color = "black"
            label_text = f"{host} (C)"
            logs.append(f"[{host}] No communication with {ip}")
            results_queue.put((host, color, label_text, logs, processed_count, total))
            processed_count += 1
            continue

        # 2) Services running?
        service_names = [svc["name"] for svc in info["services"]]
        statuses = check_services(ip, service_names)

        for svc_name in service_names:
            if not statuses.get(svc_name, False):
                color = "red"
                label_text = f"{host} (Down)"
                logs.append(f"[{host}] Watchdog service '{svc_name}' is down.")
                break

        if color == "red":
            results_queue.put((host, color, label_text, logs, processed_count, total))
            processed_count += 1
            continue

        # 3) If services up, check user and 4) recovery
        for svc_info in info["services"]:
            svc_name = svc_info["name"]
            expected_user = svc_info["user"]
            expected_recovery = svc_info["recovery"]

            if not check_service_user(ip, svc_name, expected_user):
                color = "yellow"
                label_text = f"{host} (Invalid User)"
                logs.append(f"[{host}] Invalid running user for '{svc_name}'.")
                break

            if not check_service_recovery(ip, svc_name, expected_recovery):
                color = "yellow"
                label_text = f"{host} (Invalid Recovery)"
                logs.append(f"[{host}] Recovery settings incorrect for '{svc_name}'.")
                break

        if color not in ["black", "red", "yellow"]:
            color = "green"
            label_text = f"{host} (Service OK)"
            logs.append(f"[{host}] Service is up properly.")

        results_queue.put((host, color, label_text, logs, processed_count, total))
        processed_count += 1

###############################################################################
#                            POLLING THE QUEUE                                #
###############################################################################

def poll_queue(utilities_window, results_queue, labels, result_text_widget, progress_bar):
    """
    Called periodically in the main thread to check for new results from the background thread.
    Updates label color/text, logs, and progress bar accordingly.
    """
    while True:
        try:
            host, color, text, logs, index, total = results_queue.get_nowait()
        except queue.Empty:
            break
        else:
            # Update label color/text
            labels[host].config(fg=color, text=text)
            # Update logs
            for line in logs:
                result_text_widget.insert(tk.END, line + '\n')
            result_text_widget.yview(tk.END)
            # Update progress
            progress = int(((index + 1) / total) * 100)
            progress_bar["value"] = progress

    # Schedule the next poll
    utilities_window.after(200, lambda: poll_queue(
        utilities_window, results_queue, labels, result_text_widget, progress_bar
    ))

###############################################################################
#                           OPEN UTILITIES WINDOW                             #
###############################################################################

def open_utilities_window():
    utilities_window = tk.Toplevel()
    utilities_window.title("Utilities")
    utilities_window.geometry("1000x800")
    utilities_window.resizable(False, False)
    utilities_window.configure(bg="#2E2E2E")

    label_window = "Regional"

    # Sample fallback data
    default_hostnames_utilities = {
        "Ben": {
            "ip": "12.9.95.10",
            "services": [
                {"name": "Spooler", "user": "admin", "recovery": "Restart"}
            ]
        },
        "Host2": {
            "ip": "192.168.0.2",
            "services": [
                {"name": "ServiceB", "user": "user1", "recovery": "RunProgram"}
            ]
        },
    }

    # Load from JSON or use default
    hostnames_file_path_utilities = ".\\Config\\utilitiesHostnames.json"
    if os.path.exists(hostnames_file_path_utilities):
        with open(hostnames_file_path_utilities, 'r') as file:
            hostnames = json.load(file)
    else:
        hostnames = default_hostnames_utilities

    # Title label
    tk.Label(
        utilities_window,
        text=f"Utilities - {label_window}",
        font=("Arial", 24, "bold"),
        bg="#2E2E2E",
        fg="white"
    ).place(x=500, y=30, anchor="center")

    # Scrollable frame
    scroll_frame = tk.Frame(utilities_window, bg="#2E2E2E")
    scroll_frame.place(x=10, y=100, width=275, height=620)

    canvas = tk.Canvas(scroll_frame, bg="#2E2E2E", highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    host_frame = tk.Frame(canvas, bg="#2E2E2E")

    host_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((10, 0), window=host_frame, anchor="nw")
    scrollbar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)

    # Selections + label references
    selections = {}
    labels = {}
    for host in hostnames:
        selections[host] = tk.BooleanVar(value=True)  # Initialize to True
        item_frame = tk.Frame(host_frame, bg="#2E2E2E")
        item_frame.pack(anchor="w", pady=10)

        checkbutton = tk.Checkbutton(
            item_frame,
            variable=selections[host],
            bg="#2E2E2E",
            fg="white",
            selectcolor="#2E2E2E",
            anchor="w"
        )
        checkbutton.grid(row=0, column=0, padx=5)

        host_label = tk.Label(
            item_frame,
            text=host,
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#2E2E2E",
            anchor="w"
        )
        host_label.grid(row=0, column=1, padx=5)
        labels[host] = host_label

    # Buttons
    button_style = {"font": ("Arial", 14), "fg": "white", "bd": 3, "relief": "solid", "width": 18, "height": 2}

    # Mark/Unmark all
    tk.Button(
        utilities_window,
        text="Mark All",
        command=lambda: [v.set(True) for v in selections.values()],
        bg="green", **button_style
    ).place(x=750, y=100)

    tk.Button(
        utilities_window,
        text="Unmark All",
        command=lambda: [v.set(False) for v in selections.values()],
        bg="red", **button_style
    ).place(x=750, y=180)

    # Some other example buttons

    tk.Button(
        utilities_window,
        text="Refresh",
        command=lambda: print("Refresh..."),
        bg="#0099cc", **button_style
    ).place(x=750, y=260)

    tk.Button(
        utilities_window,
        text="Restart Watchdog",
        command=lambda: print("Restarting Watchdog..."),
        bg="#0099cc", **button_style
    ).place(x=750, y=340)

    tk.Button(
        utilities_window,
        text="Start Watchdog",
        command=lambda: print("Starting Watchdog..."),
        bg="#0099cc", **button_style
    ).place(x=750, y=420)

    tk.Button(
        utilities_window,
        text="Stop Watchdog",
        command=lambda: print("Stopping Watchdog..."),
        bg="#0099cc", **button_style
    ).place(x=750, y=500)

    tk.Button(
        utilities_window,
        text="Restart Component",
        command=lambda: print("Restart component..."),
        bg="#0099cc", **button_style
    ).place(x=750, y=580)

    tk.Button(
        utilities_window,
        text="Shutdown Component",
        command=lambda: print("Shutting down component..."),
        bg="#0099cc", **button_style
    ).place(x=750, y=660)

    # Close
    close_button_style = {"font": ("Arial", 12), "fg": "white", "bd": 3,
                          "relief": "solid", "width": 10, "height": 2}
    tk.Button(
        utilities_window,
        text="Close",
        command=utilities_window.destroy,
        bg="gray", **close_button_style
    ).place(x=500, y=764, anchor="center")

    # Result Text
    result_text_widget = tk.Text(
        utilities_window,
        width=48,
        height=34,
        wrap=tk.WORD,
        bg="#333333",
        fg="white",
        bd=2,
        font=("Arial", 12)
    )
    result_text_widget.place(x=278, y=106)

    # Progress bar in the original location
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TProgressbar", thickness=14)
    progress_bar = ttk.Progressbar(
        utilities_window,
        style="TProgressbar",
        length=440,
        mode="determinate"
    )
    progress_bar.place(x=278, y=70)
    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    # 1) Create the queue:
    results_queue = queue.Queue()

    # 2) Start a background thread (worker_thread_func is your function that actually does the checks).
    #    Adjust the arguments as needed for your code (hosts, selections, or labels, etc.).
    thread = threading.Thread(
        target=worker_thread_func,
        args=(hostnames, selections, results_queue),  # <-- pass selections here
        daemon=True
    )
    thread.start()

    # 3) Start polling the queue in the main thread to update the UI as results come in.
    poll_queue(utilities_window, results_queue, labels, result_text_widget, progress_bar)

###############################################################################
#                          MAIN / DEMO APP LAUNCH                             #
###############################################################################

def main():
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("400x300")

    tk.Button(
        root, text="Open Utilities",
        command=open_utilities_window,
        font=("Arial", 16)
    ).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
