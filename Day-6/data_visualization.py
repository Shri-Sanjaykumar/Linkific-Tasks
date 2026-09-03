import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Environment & Library Versions
print("=" * 60)
print("       DAY 6 – DYNAMIC DATA VISUALIZATION RUNNER       ")
print("=" * 60)
print(f"Pandas Version    : {pd.__version__}")
import matplotlib
print(f"Matplotlib Version: {matplotlib.__version__}")
print(f"Seaborn Version   : {sns.__version__}")
print()

# 2. Dynamically Load Day 5 Dataset
data_path = os.path.join(os.path.dirname(__file__), "..", "Day-5", "dataset.csv") if "__file__" in locals() else "../Day-5/dataset.csv"
if not os.path.exists(data_path):
    data_path = "dataset.csv"

df = pd.read_csv(data_path)
print(f"Loaded dataset from: {os.path.abspath(data_path)}")
print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
print()

# 3. Create charts output directory
charts_dir = os.path.join(os.path.dirname(__file__), "charts") if "__file__" in locals() else "charts"
os.makedirs(charts_dir, exist_ok=True)

# 4. Department Counts (Dynamically calculated)
dept_counts = df["Department"].value_counts()
print("Current Department Counts:")
for dept, count in dept_counts.items():
    print(f"  - {dept}: {count}")
print()

# -------------------------------------------------------------
# CHART 1: BAR CHART
# -------------------------------------------------------------
print("Generating Chart 1: Bar Chart...")
plt.figure(figsize=(7, 4))
plt.bar(dept_counts.index, dept_counts.values, color="skyblue", edgecolor="black")
plt.title("Number of Employees by Department")
plt.xlabel("Department")
plt.ylabel("Number of Employees")
plt.tight_layout()
bar_file = os.path.join(charts_dir, "bar_chart.png")
plt.savefig(bar_file)
plt.close()
print(f" -> Saved updated bar chart to: {bar_file}")

# -------------------------------------------------------------
# CHART 2: LINE CHART
# -------------------------------------------------------------
print("Generating Chart 2: Line Chart...")
salary_df = df.dropna(subset=["Salary"]).copy()
plt.figure(figsize=(8, 4))
plt.plot(salary_df["Employee_ID"].astype(str), salary_df["Salary"], marker="o", color="green", linewidth=2)
plt.title("Employee Salary across Employee IDs")
plt.xlabel("Employee ID")
plt.ylabel("Salary")
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
line_file = os.path.join(charts_dir, "line_chart.png")
plt.savefig(line_file)
plt.close()
print(f" -> Saved updated line chart to: {line_file}")

# -------------------------------------------------------------
# CHART 3: HISTOGRAM
# -------------------------------------------------------------
print("Generating Chart 3: Histogram...")
plt.figure(figsize=(7, 4))
plt.hist(df["Age"], bins=5, color="coral", edgecolor="black")
plt.title("Distribution of Employee Ages")
plt.xlabel("Age")
plt.ylabel("Frequency (Number of Employees)")
plt.tight_layout()
hist_file = os.path.join(charts_dir, "histogram.png")
plt.savefig(hist_file)
plt.close()
print(f" -> Saved updated histogram to: {hist_file}")

# -------------------------------------------------------------
# CHART 4: PIE CHART
# -------------------------------------------------------------
print("Generating Chart 4: Pie Chart...")
plt.figure(figsize=(6, 6))
plt.pie(dept_counts.values, labels=dept_counts.index, autopct="%1.1f%%", startangle=140, colors=["#66b3ff", "#99ff99", "#ffcc99", "#ff9999"])
plt.title("Department Distribution")
plt.tight_layout()
pie_file = os.path.join(charts_dir, "pie_chart.png")
plt.savefig(pie_file)
plt.close()
print(f" -> Saved updated pie chart to: {pie_file}")
print()

print("=" * 60)
print("ALL 4 CHARTS RE-GENERATED & SAVED IN charts/ FOLDER!")
print("=" * 60)
