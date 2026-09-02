import os
import pandas as pd

# 1. Library Version
print(f"Pandas Version: {pd.__version__}")
print()

# 2. Load Dataset
data_path = os.path.join(os.path.dirname(__file__), "dataset.csv") if "__file__" in locals() else "dataset.csv"
if not os.path.exists(data_path):
    data_path = "dataset.csv"

df = pd.read_csv(data_path)
print("Dataset 'dataset.csv' loaded successfully.")
print()

# 3. DataFrame Structure & Data Types
print("=== DataFrame Structure ===")
print("Object Type:", type(df))
print("Columns    :", list(df.columns))
print("\nColumn Data Types:")
print(df.dtypes)
print()

# 4. First 5 Rows (head)
print("=== First 5 Rows (df.head()) ===")
print(df.head())
print()

# 5. Last 5 Rows (tail)
print("=== Last 5 Rows (df.tail()) ===")
print(df.tail())
print()

# 6. Dimensions & Shape
print("=== Dataset Dimensions ===")
rows, cols = df.shape
print(f"Shape: {df.shape}")
print(f"Total Rows   : {rows}")
print(f"Total Columns: {cols}")
print()

# 7. Missing Value Detection
print("=== Missing Values Check (df.isnull().sum()) ===")
null_counts = df.isnull().sum()
print(null_counts)
print(f"Total Missing Values in Dataset: {null_counts.sum()}")
print()

# 8. Conditional Filtering
print("=== Filtering Condition 1: Salary > 70,000 ===")
high_salary = df[df["Salary"] > 70000]
print(high_salary)
print(f"Count: {len(high_salary)} employees meet this condition.")
print()

print("=== Filtering Condition 2: Department == 'Data Science' ===")
data_science = df[df["Department"] == "Data Science"]
print(data_science)
print(f"Count: {len(data_science)} employees in Data Science.")
print()

print("=== Filtering Condition 3: Experience_Years >= 5 ===")
senior_exp = df[df["Experience_Years"] >= 5]
print(senior_exp)
print(f"Count: {len(senior_exp)} employees with 5+ years experience.")
print()

# 9. Summary Statistics
print("=== Summary Statistics of Numerical Columns (df.describe()) ===")
print(df.describe())
print()

# 10. Key Observations from Data
print("=== Summary Observations ===")
print(f"- Total employees recorded: {rows}")
print(f"- Missing data found in 'Salary' ({null_counts['Salary']}) and 'Experience_Years' ({null_counts['Experience_Years']}).")
print(f"- Average employee age is {df['Age'].mean():.1f} years (ranging from {df['Age'].min()} to {df['Age'].max()}).")
print(f"- Average salary is {df['Salary'].mean():.2f} (ranging from {df['Salary'].min():.0f} to {df['Salary'].max():.0f}).")
print(f"- {len(data_science)} out of {rows} employees belong to the Data Science team.")
