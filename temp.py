import wmi
import pandas as pd

# List of remote computer names (hostnames or IPs)
computers = ["192.168.3.141"]  # Replace with your actual hosts

data = []

for comp in computers:
    print(f"Connecting to {comp}...")
    try:
        connection = wmi.WMI(computer=comp)  # No username/password here

        adapters = connection.Win32_NetworkAdapter()
        configs = {cfg.Description: cfg for cfg in connection.Win32_NetworkAdapterConfiguration()}

        for adapter in adapters:
            name = adapter.Name
            status = "Up" if adapter.NetEnabled else "Down"
            speed = adapter.Speed or "Unknown"
            ipv6_enabled = "Unknown"

            config = configs.get(adapter.Description)
            if config and config.IPEnabled and config.IPAddress:
                ipv6_enabled = any(":" in ip for ip in config.IPAddress)

            data.append({
                "Computer": comp,
                "Adapter": name,
                "Status": status,
                "Speed": speed,
                "IPv6Enabled": ipv6_enabled
            })

    except Exception as e:
        print(f"Error on {comp}: {e}")
        data.append({
            "Computer": comp,
            "Adapter": "N/A",
            "Status": "Error",
            "Speed": "N/A",
            "IPv6Enabled": str(e)
        })

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("network_adapter_status.csv", index=False)
print("Saved to network_adapter_status.csv")
