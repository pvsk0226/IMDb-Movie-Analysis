import pandas as pd
import glob
import os

# Path to your folder
path = r"C:\Pavithra\csv files"

# Get all CSV files in the folder
csv_files = glob.glob(os.path.join(path, "*.csv"))

# Read and combine
df_list = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(df_list, ignore_index=True)

# Save to a new CSV
combined_df.to_csv(os.path.join(path, "combined_output.csv"), index=False)

print("All CSV files combined into combined_output.csv")
