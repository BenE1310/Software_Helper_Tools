from datetime import datetime

# Your value
value = "ExampleValue"

# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

# Combine the value with the timestamp
value_with_timestamp = f"{timestamp} - {value}"

print(value_with_timestamp)