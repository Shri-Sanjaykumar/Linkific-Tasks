import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# STUDENT PERFORMANCE ANALYSIS — MINI PROJECT (DAY 7)
# Intern: Shri Sanjaykumar V | Role: AI/ML Intern | Organization: Linkific
# ==============================================================================

print("=" * 70)
print("     STUDENT PERFORMANCE ANALYSIS DASHBOARD (WEEK 1 MINI PROJECT)   ")
print("=" * 70)

# 1. Load Dataset Dynamically
data_path = os.path.join(os.path.dirname(__file__), "dataset.csv") if "__file__" in locals() else "dataset.csv"
df = pd.read_csv(data_path)
print(f"Dataset loaded from: {os.path.abspath(data_path)}")
print(f"Dataset Shape: {df.shape[0]} students, {df.shape[1]} columns")
print()

# 2. Data Inspection
print("=== First 5 Records ===")
print(df.head())
print()

print("=== Missing Values Before Cleaning ===")
print(df.isnull().sum())
print()

# 3. Data Cleaning (Impute with feature medians)
df["Study_Hours_Per_Week"] = df["Study_Hours_Per_Week"].fillna(df["Study_Hours_Per_Week"].median())
df["Science"] = df["Science"].fillna(df["Science"].median())
df["English"] = df["English"].fillna(df["English"].median())

print("=== Missing Values After Cleaning ===")
print(df.isnull().sum())
print(f"Duplicate rows count: {df.duplicated().sum()}")
print()

# 4. Feature Derivation
subjects = ["Maths", "Science", "English", "Social", "Physical_Education"]
df["Total_Marks"] = df[subjects].sum(axis=1)
df["Average_Marks"] = np.round(df["Total_Marks"] / len(subjects), 2)

def assign_grade(score):
    if score >= 80:
        return "Distinction"
    elif score >= 60:
        return "First Class"
    elif score >= 40:
        return "Second Class"
    else:
        return "Needs Improvement"

df["Grade"] = df["Average_Marks"].apply(assign_grade)
df["Pass_Status"] = np.where(df["Average_Marks"] >= 40, "Pass", "Fail")

# 5. Dynamic Summary Metrics
total_students = len(df)
class_avg = df["Average_Marks"].mean()
top_idx = df["Average_Marks"].idxmax()
top_student_name = df.loc[top_idx, "Name"]
top_student_score = df.loc[top_idx, "Average_Marks"]

low_idx = df["Average_Marks"].idxmin()
lowest_student_name = df.loc[low_idx, "Name"]
lowest_student_score = df.loc[low_idx, "Average_Marks"]

subject_means = df[subjects].mean().round(2)
highest_subject = subject_means.idxmax()
highest_sub_val = subject_means.max()
lowest_subject = subject_means.idxmin()
lowest_sub_val = subject_means.min()

grade_order = ["Distinction", "First Class", "Second Class", "Needs Improvement"]
grade_counts = df["Grade"].value_counts().reindex(grade_order, fill_value=0)
pass_counts = df["Pass_Status"].value_counts()
pass_num = pass_counts.get("Pass", 0)
pass_pct = round((pass_num / total_students) * 100, 1)

print("=== Overall Performance Metrics ===")
print(f"Total Students Evaluated : {total_students}")
print(f"Overall Class Average     : {class_avg:.2f}")
print(f"Top Scoring Student       : {top_student_name} ({top_student_score:.2f} marks)")
print(f"Lowest Scoring Student    : {lowest_student_name} ({lowest_student_score:.2f} marks)")
print()

print("=== Subject-Wise Average Marks ===")
for sub in subjects:
    print(f"  - {sub:<20}: {subject_means[sub]:.2f}")
print()

print("=== Grade Distribution ===")
for gr, count in grade_counts.items():
    pct = (count / total_students) * 100
    print(f"  - {gr:<20}: {count} students ({pct:.1f}%)")
print()

print("=== Pass / Fail Counts ===")
print(pass_counts.to_string())
print()

# 6. Generate and Save Visualizations
charts_dir = os.path.join(os.path.dirname(__file__), "charts") if "__file__" in locals() else "charts"
os.makedirs(charts_dir, exist_ok=True)

# Chart 1: Bar Chart — Subject-Wise Average Marks
plt.figure(figsize=(8, 4.5))
bar_colors = ["#4A90E2", "#50E3C2", "#F5A623", "#E94E77", "#7ED321"]
bars = plt.bar(subjects, subject_means.values, color=bar_colors, edgecolor="black")
plt.title("Subject-Wise Average Marks (5 Subjects)", fontsize=12, fontweight="bold")
plt.xlabel("Subjects", fontsize=10)
plt.ylabel("Average Marks (Out of 100)", fontsize=10)
plt.ylim(0, 100)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 1.5, f"{yval:.2f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
bar_file = os.path.join(charts_dir, "bar_chart.png")
plt.savefig(bar_file)
plt.close()
print(f"Saved: {bar_file}")

# Chart 2: Histogram — Distribution of Student Average Marks
plt.figure(figsize=(7, 4.5))
plt.hist(df["Average_Marks"], bins=8, color="#50E3C2", edgecolor="black")
plt.title("Distribution of Student Average Marks", fontsize=12, fontweight="bold")
plt.xlabel("Average Marks", fontsize=10)
plt.ylabel("Number of Students", fontsize=10)
plt.tight_layout()
hist_file = os.path.join(charts_dir, "histogram.png")
plt.savefig(hist_file)
plt.close()
print(f"Saved: {hist_file}")

# Chart 3: Pie Chart — Performance Category Distribution
plt.figure(figsize=(6, 6))
# Filter out non-zero categories for clean pie chart
active_grades = grade_counts[grade_counts > 0]
pie_colors = ["#F8E71C", "#50E3C2", "#4A90E2", "#D0021B"]
plt.pie(active_grades.values, labels=active_grades.index, autopct="%1.1f%%", startangle=140,
        colors=pie_colors[:len(active_grades)])
plt.title("Student Performance Category Distribution", fontsize=12, fontweight="bold")
plt.tight_layout()
pie_file = os.path.join(charts_dir, "pie_chart.png")
plt.savefig(pie_file)
plt.close()
print(f"Saved: {pie_file}")

# Chart 4: Line Chart — Student Performance Progression (Sample Cohort)
plt.figure(figsize=(9, 4.5))
sample_df = df.head(12)
plt.plot(sample_df["Name"], sample_df["Average_Marks"], marker="o", color="#9013FE", linewidth=2)
plt.title("Student Performance Progression (Sample Cohort)", fontsize=12, fontweight="bold")
plt.xlabel("Student Name", fontsize=10)
plt.ylabel("Average Marks", fontsize=10)
plt.xticks(rotation=45, ha="right")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
line_file = os.path.join(charts_dir, "line_chart.png")
plt.savefig(line_file)
plt.close()
print(f"Saved: {line_file}")
print()

# 7. Dynamic Key Insights Generation
dist_count = grade_counts.get("Distinction", 0)
fc_count = grade_counts.get("First Class", 0)

dynamic_insights = [
    f"1. Top Performing Subject: {highest_subject} recorded the highest class average of {highest_sub_val:.2f} marks.",
    f"2. Most Challenging Subject: {lowest_subject} recorded the lowest class average of {lowest_sub_val:.2f} marks, showing a {(highest_sub_val - lowest_sub_val):.2f}-point gap compared to {highest_subject}.",
    f"3. Top Academic Achiever: {top_student_name} achieved the highest overall average of {top_student_score:.2f} marks across all 5 subjects.",
    f"4. Academic Standing: {fc_count} students ({round(fc_count/total_students*100, 1)}%) secured First Class, while {dist_count} students ({round(dist_count/total_students*100, 1)}%) attained Distinction.",
    f"5. Overall Class Pass Rate: {pass_num} out of {total_students} students ({pass_pct}%) passed the examination with an average score of 40 or higher.",
    f"6. Score Range & Spread: Student averages range from {lowest_student_score:.2f} ({lowest_student_name}) to {top_student_score:.2f} ({top_student_name}), with a cohort average of {class_avg:.2f} marks."
]

print("=" * 70)
print("                    DYNAMICALLY GENERATED KEY INSIGHTS                  ")
print("=" * 70)
for insight in dynamic_insights:
    print(insight)
print("=" * 70)
