import pandas as pd

# Load your cleaned data
file_path = r"C:\Pavithra\csv files\combined_output.csv"
df = pd.read_csv(file_path)

# Remove leading numbers and dot from 'Movie Name'
df["Movie Name"] = df["Movie Name"].str.replace(r'^\d+\.\s*', '', regex=True)

print(df["Movie Name"].head(20))
df.to_csv(file_path, index=False)