import tkinter as tk
from tkinter import PhotoImage, ttk, messagebox
from functions import *
import tkinter.ttk as ttk
import threading
from tkinter.messagebox import showinfo
from tkinter.simpledialog import askstring



# Button hover effect
def on_enter(button):
    button.config(bg='#666666')  # Lighter gray when hovered

def on_leave(button):
    button.config(bg='#444444')  # Default background color

# Button click effect
def on_click(button):
    button.config(bg='#555555')  # Dark gray when clicked
    button.after(200, lambda: button.config(bg='#444444'))  # Reset after 200ms


def on_button_click():
    clear_all_buttons()

def clear_all_buttons():
    for button in buttons:
        button.destroy()


# Main Application
root = tk.Tk()
root.title("Software Helper Tools")
root.geometry("600x750")
root.resizable(False, False)
# root.eval('tk::PlaceWindow . center')


# Protect application
# try:
#     key = askstring('Lock', "Enter Master Key", show='*')
#     while key != "1234":
#         showinfo('Error', 'You type error master key!')
#         key = askstring('Enter Master Key', "The master key is invalid Please try again:", show='*')
# except:
#     pass
# else:
#     showinfo("Master key successful", "Welcome to \"FBE Software Helper Tool\"")

# Set Background Image
bg_image = PhotoImage(file='logo1.png')  # Ensure this image is in your directory
canvas = tk.Canvas(root, width=600, height=750, highlightthickness=0, borderwidth=0)
canvas.place(x=0, y=0)
canvas.create_image(0, 0, anchor='nw', image=bg_image)



# Button Styles
button_style = {
    'width': 24,
    'height': 2,
    'bg': '#444444',
    'fg': 'white',
    'font': ('Arial', 12, 'bold'),
    'activebackground': '#555555',
    'borderwidth': 0,
    'relief': 'flat'
}

button_style_small = {
    'width': 10,
    'height': 2,
    'bg': '#444444',
    'fg': 'white',
    'font': ('Arial', 12, 'bold'),
    'activebackground': '#555555',
    'borderwidth': 0,
    'relief': 'flat'
}

BN = 0
buttons = []
installation_app_remote_message = []
progress_bar_ping = None
progress_bar_permissions = None

# Reusable function to create a button with hover effects
def create_button(parent, text, command, x, y, style=button_style):
    button = tk.Button(parent, text=text, **style, command=command)
    button.place(x=x, y=y)
    button.bind("<Enter>", lambda e: on_enter(button))
    button.bind("<Leave>", lambda e: on_leave(button))
    buttons.append(button)  # Add to buttons list for tracking
    return button

# Function to open a new window for the Battery button
def open_battery_window():
    battery_window = tk.Toplevel(root)
    battery_window.title("Remote App Installation")
    battery_window.geometry("1000x900")
    battery_window.resizable(False, False)
    battery_window.configure(bg="#004d4d")  # Dark teal background
    global progress_bar_ping
    global progress_bar_permissions

    def on_close():
        global progress_bar_ping, progress_bar_permissions
        # Reset the progress bar variable
        progress_bar_ping = None
        progress_bar_permissions = None
        battery_window.destroy()  # Close the window

    x = battery_window.protocol("WM_DELETE_WINDOW", on_close)



    # Hostnames and IPs
    hostnames = {
        "BMC1": "192.168.3.141",
        "BMC2": "192.168.3.135",
        "ICS1": "192.168.3.136",
        "ICS2": "192.168.3.138",
        "DB1": "192.168.3.139",
        "DB2": "192.168.3.140",
        "Client1": "192.168.1.7",
        "Client2": "192.168.1.8",
        "Client3": "192.168.1.9",
        "Client4": "192.168.1.10",
        "Client5": "192.168.1.11",
        "Client6": "192.168.3.154",
    }

    # Track selections
    selections = {host: tk.BooleanVar() for host in hostnames}
    labels = {}

    # Title Label
    title_label = tk.Label(battery_window, text="Remote App Installation", font=("Arial", 20, "bold"), fg="white", bg="#004d4d")
    title_label.place(x=350, y=10)

    # Hostnames Section
    y_offset = 70
    for host, ip in hostnames.items():
        label = tk.Label(
            battery_window,
            text=f"{host} (IP: {ip})",
            font=("Arial", 14),
            fg="white",
            bg="#004d4d",
            anchor="w"
        )
        label.place(x=50, y=y_offset)
        labels[host] = label

        tk.Checkbutton(
            battery_window,
            variable=selections[host],
            bg="#004d4d",
            fg="white",
            selectcolor="#004d4d",
            anchor="w"
        ).place(x=330, y=y_offset + 5)
        y_offset += 50

    # Functions for Check All and Uncheck All
    def check_all():
        for var in selections.values():
            var.set(True)

    def uncheck_all():
        for var in selections.values():
            var.set(False)

    # Buttons on the right
    button_x = 760
    button_width = 200
    tk.Button(
        battery_window,
        text="Check All",
        command=check_all,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=100, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Uncheck All",
        command=uncheck_all,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=170, width=button_width, height=50)

    def perform_test(test_function):
        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
            return
        results = [test_function(host, hostnames[host]) for host in selected_hosts]
        display_results(results)

    # Results Display
    results_text = tk.Text(battery_window, height=10, width=60, bg="#003333", fg="white", font=("Arial", 12))
    results_text.place(x=50, y=700, width=700, height=150)


    def display_results(results):
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, "\n".join(results))

    def perform_communication_test():
        global progress_bar_ping
        logs = []  # Collect logs here

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
            return


        # Create and show the progress bar the first time the button is pressed
        if progress_bar_ping is None:
            progress_bar_ping = ttk.Progressbar(
                battery_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_ping.place(x=580, y=325, width=150, height=20)

        progress_bar_ping.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    success = check_communication(ip)
                    if success:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Communication successful.")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) C")
                        logs.append(f"{host} (IP: {ip}): Communication failed.")

            # Stop the progress bar after the test completes
            battery_window.after(0, lambda: progress_bar_ping.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()

    def perform_permission_test():
        global progress_bar_permissions
        logs = []  # Logs for test results

        selected_hosts = [host for host, var in selections.items() if var.get()]
        if not selected_hosts:
            messagebox.showwarning("No Selection", "Please select at least one hostname.")
            return

        # Create and show the progress bar if it's not already created
        if progress_bar_permissions is None:
            progress_bar_permissions = ttk.Progressbar(
                battery_window, orient="horizontal", mode="indeterminate", length=200
            )
            progress_bar_permissions.place(x=580, y=400, width=150, height=20)

        progress_bar_permissions.start(10)  # Start the progress bar

        def run_test():
            for host, var in selections.items():
                if var.get():
                    ip = hostnames[host]
                    network_path = rf"\\{ip}\c$\temp"  # Adjust the network path format
                    permissions = check_permissions(network_path)  # Call the helper function

                    # Update GUI based on results
                    if permissions["readable"] and permissions["writable"]:
                        labels[host].config(fg="green")
                        logs.append(f"{host} (IP: {ip}): Permissions OK (Read/Write).")
                    else:
                        labels[host].config(fg="red")
                        labels[host].config(text=f"{host} (IP: {ip}) P")
                        logs.append(f"{host} (IP: {ip}): Permissions FAILED.")

            # Stop the progress bar and display results
            battery_window.after(0, lambda: progress_bar_permissions.stop())
            battery_window.after(0, lambda: display_results(logs))

        # Run the test in a separate thread
        threading.Thread(target=run_test).start()



    def permission_test(host, ip):
        return f"Permission test passed for {host} (IP: {ip})"

    def disk_volume_test(host, ip):
        return f"Disk volume test passed for {host} (IP: {ip})"

        # Buttons

    tk.Button(
        battery_window,
        text="Communication Test",
        command=perform_communication_test,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=310, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Permission Test",
        command=perform_permission_test,
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=380, width=button_width, height=50)

    tk.Button(
        battery_window,
        text="Disk Volume Test",
        command=lambda: perform_test(disk_volume_test),
        font=("Arial", 14),
        bg="#006666",
        fg="white",
        activebackground="#008080"
    ).place(x=button_x, y=450, width=button_width, height=50)



    # Close button in the middle at the bottom
    tk.Button(
        battery_window,
        text="Close",
        command=on_close,
        font=("Arial", 14),
        bg="#800000",
        fg="white",
        activebackground="#990000"
).place(x=450, y=855, width=100, height=40)






def rai_screen():

    #Check if BN is chosen
    if BN == 0:
        messagebox.showerror("Battery number", "Please choose a battery number to continue.")
        return main_screen()

    # Clear existing buttons
    on_button_click()

    # Add Label
    rai_label = tk.Label(root, text='Remote App Installation', fg='white', bg='#000000', font=('Arial', 20, 'bold'))
    rai_label.place(x=150, y=10)
    buttons.append(rai_label)

    # Create Buttons with Hover Effects
    create_button(root, 'Battery', open_battery_window, 180, 440)
    create_button(root, 'Regional', lambda: on_click(None), 180, 510)
    create_button(root, 'Simulator', lambda: on_click(None), 180, 580)
    create_button(root, 'Back', main_screen, 10, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)

    # if len(installation_app_remote_message) == 0:
    #     messagebox.showinfo("Don't forget", "The new version of the application should be on the local disk: C:\\FBE")
    #     installation_app_remote_message.append("onetime")


def main_screen():
    on_button_click()

    def save_value():
        global BN
        selected_value = dropdown_var.get()
        BN = selected_value
        print(f"Saved value: {selected_value}")
        print(BN)  # Replace this with your desired save logic
        messagebox.showinfo("Save", f"The battery number was update to {BN}")

    # Add Main Label
    main_label = tk.Label(root, text='Main', fg='white', bg='#000000', font=('Arial', 18, 'bold'))
    main_label.place(x=268, y=10)
    buttons.append(main_label)

    # Dropdown Menu
    dropdown_var = tk.StringVar(value="Select a number")
    dropdown_label = tk.Label(root, text="Battery number:", fg='white', bg='#000000', font=('Arial', 14))
    dropdown_label.place(x=10, y=10)
    buttons.append(dropdown_label)

    dropdown = ttk.Combobox(root, textvariable=dropdown_var, state="readonly", font=('Arial', 10))
    dropdown['values'] = [1, 2, 3, 4, 5, 6, 21]
    dropdown.place(x=10, y=40)
    buttons.append(dropdown)

    # Save Button
    save_button = tk.Button(root, text='Save', width=6, height=2, bg='#444444', fg='white', font=('Arial', 8, 'bold'),
                            activebackground='#555555', command=save_value)
    save_button.place(x=10, y=70)
    buttons.append(save_button)

    # Create Buttons with Hover Effects
    create_button(root, 'Remote App Installation', rai_screen, 180, 440)
    create_button(root, 'Checks Remote Components', lambda: on_click(None), 180, 510)
    create_button(root, 'Cyber Deployment', open_battery_window, 180, 580)
    create_button(root, 'Tools', lambda: on_click(None), 360, 690, button_style_small)
    create_button(root, 'Exit', root.destroy, 480, 690, button_style_small)




main_screen()
root.mainloop()
