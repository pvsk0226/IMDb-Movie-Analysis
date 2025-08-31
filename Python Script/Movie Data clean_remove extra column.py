import pandas as pd

# Load the file
file_path = r"C:\Pavithra\csv files\combined_output.csv"
df = pd.read_csv(file_path)

# Drop the unwanted column
df = df.drop(columns=["Voting count"])  # assign back to df

# Or: df.drop(columns=["Voting count"], inplace=True)

# Save back to CSV
df.to_csv(file_path, index=False)

print(df.head())

