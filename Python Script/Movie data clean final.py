import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv(r"C:\Pavithra\csv files\combined_output.csv")

# ---- Clean Rating ----
# Replace NaN with mean rating
df["Rating"] = df["Rating"].fillna(df["Rating"].mean())

# ---- Clean Voting Counts ----
# Replace NaN with 0
df["Voting Counts"] = df["Voting Counts"].fillna(0)

# ---- Clean Duration ----
def convert_duration(val):
    if pd.isna(val) or val == "0":
        return np.nan
    val = val.strip()
    hours, minutes = 0, 0
    if "h" in val:
        parts = val.split("h")
        hours = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
        if "m" in parts[1]:
            minutes_str = parts[1].replace("m", "").strip()
            minutes = int(minutes_str) if minutes_str.isdigit() else 0
    return hours * 60 + minutes

# Apply conversion
df["Duration"] = df["Duration"].astype(str).apply(convert_duration)

# Fill NaN with median
median_duration = df["Duration"].median()
df["Duration"] = df["Duration"].fillna(median_duration)

# Cap extreme values
df["Duration"] = df["Duration"].apply(
    lambda x: median_duration if x < 60 or x > 240 else x
)

file_path = r"C:\Pavithra\csv files\combined_output.csv"

df.to_csv(file_path, index=False)
# ---- Final Check ----
print(df.isnull().sum())
print(df.describe())