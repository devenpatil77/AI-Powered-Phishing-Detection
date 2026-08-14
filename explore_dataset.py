import pandas as pd

# Load the dataset
df = pd.read_excel("archive/dataset/phishing_dataset.xlsx")

print("="*60)
print("FIRST 5 ROWS")
print("="*60)
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nLabel Distribution:")
print(df["label"].value_counts())

print("\nDataset Information:")
print(df.info())