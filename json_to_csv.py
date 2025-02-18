import json
import pandas as pd

# Load JSON file
with open("database.json", "r", encoding="utf-8") as file:
    data = json.load(file)  # This is a list of dictionaries

# Normalize nested JSON (convert nested lists/dictionaries into a tabular format)
df = pd.json_normalize(data, sep="_")  # Flatten JSON structure

# Save as CSV file
df.to_csv("output.csv", index=False)

# Print DataFrame to verify
print(df)


import pandas as pd

from tabulate import tabulate

# Load CSV file
df = pd.read_csv("output.csv")

# Print DataFrame as a table in the terminal
# print(df.to_string())  # Displays table format with all columns


print(tabulate(df, headers='keys', tablefmt='pretty'))  # Formats table with headers

