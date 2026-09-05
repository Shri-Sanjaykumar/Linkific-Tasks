# Student Performance Analysis — Week 1 Mini Project

- **Date:** 05 September 2026
- **Training Day:** Day 7 (Week 1 Mini Project)
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0 | Matplotlib 3.11.0 | Seaborn 0.13.2

---

## 🎯 Objective

Synthesize all the core concepts learned during Week 1 (Python, NumPy, Pandas, Matplotlib, and Seaborn) into a dynamic end-to-end data analysis dashboard. 

The project loads student academic records, performs data cleaning on missing entries, computes overall performance metrics across 5 core subjects, builds 4 distinct visual charts, and programmatically computes dynamic key insights that automatically refresh whenever dataset values change.

---

## 📂 Dataset

- **File:** `dataset.csv`
- **Size:** 25 student records across 10 features.
- **Columns:**
  - `Student_ID`: Unique integer identifier.
  - `Name`: Full student name (e.g., Aarav Sharma, Diya Patel, Rohan Verma, Arjun Sen).
  - `Gender`: Student gender (`Male`, `Female`).
  - `Study_Hours_Per_Week`: Weekly study duration in hours.
  - `Attendance_Percentage`: Course attendance percentage (0–100%).
  - `Maths`: Examination score in Mathematics (0–100).
  - `Science`: Examination score in Science (0–100).
  - `English`: Examination score in English (0–100).
  - `Social`: Examination score in Social Studies (0–100).
  - `Physical_Education`: Examination score in Physical Education (0–100).

---

## 🛠️ Technologies Used

- **Python (3.14.3):** Core programming language.
- **Pandas (3.0.3):** Tabular data manipulation, cleaning, and aggregation.
- **NumPy (2.5.0):** Numerical arrays, vectorized calculations, and rounding.
- **Matplotlib (3.11.0):** Bar, line, histogram, and pie chart rendering.
- **Seaborn (0.13.2):** Statistical aesthetic styling.
- **Jupyter Notebook & VS Code:** Interactive analysis, visual output, and documentation.

---

## 🧹 Data Cleaning

1. **Missing Value Check:** Checked initial data completeness with `df.isnull().sum()`. Exactly 3 missing values were detected:
   - `Study_Hours_Per_Week`: 1 missing record (Student 107, Neha Joshi).
   - `Science`: 1 missing record (Student 119, Riya Jain).
   - `English`: 1 missing record (Student 112, Aditya Kumar).
2. **Missing Value Imputation:**
   - Missing numerical values (`Study_Hours_Per_Week`, `Science`, `English`) were imputed using feature **medians** to prevent skewing from extreme values.
3. **Integrity Confirmation:** Re-checked with `df.isnull().sum()` confirming 0 missing values, and verified 0 duplicate rows with `df.duplicated().sum()`.

---

## 📊 Analysis Performed

- **Engineered Metrics:**
  - `Total_Marks = Maths + Science + English + Social + Physical_Education`
  - `Average_Marks = Total_Marks / 5`
  - `Grade`: Categorized into `Distinction` ($\ge 80$), `First Class` (60–79), `Second Class` (40–59), and `Needs Improvement` ($< 40$).
  - `Pass_Status`: Pass ($\ge 40$) vs Fail ($< 40$).
- **Overall Class Performance:**
  - Total Students Evaluated: 25
  - Overall Class Average: **74.24** marks
  - Top Scoring Student: **Rohan Verma** (**99.20** marks)
  - Lowest Scoring Student: **Rahul Nair** (**23.00** marks)
- **Subject-Wise Evaluation:**
  - Physical Education Average: **80.28**
  - Maths Average: **74.56**
  - Science Average: **73.68**
  - English Average: **72.34**
  - Social Average: **70.36**
- **Academic Standing Counts:**
  - First Class: 11 students (44.0%)
  - Distinction: 10 students (40.0%)
  - Second Class: 3 students (12.0%)
  - Needs Improvement: 1 student (4.0%)
- **Pass Rate:** 24 Passed (96.0%), 1 Failed (4.0%).

---

## 📈 Visualizations

All 4 charts are saved in `charts/` and dynamically rendered in the notebook:

1. **Bar Chart (`charts/bar_chart.png`):** Subject-wise average marks across all 5 subjects with exact values annotated on top of each bar.
2. **Histogram (`charts/histogram.png`):** Distribution of student average marks across 8 bins.
3. **Pie Chart (`charts/pie_chart.png`):** Percentage distribution across academic standing categories.
4. **Line Chart (`charts/line_chart.png`):** Score progression across a sample cohort with individual student names on the X-axis (shows Rohan Verma peaking at 99.20 marks).

---

## 🔍 Dynamically Generated Key Insights

*(Programmatically computed from live dataset values; automatically updates if `dataset.csv` is edited)*

1. **Top Performing Subject:** `Physical_Education` recorded the highest class average of **80.28** marks.
2. **Most Challenging Subject:** `Social` recorded the lowest class average of **70.36** marks, showing a **9.92**-point gap compared to Physical Education.
3. **Top Academic Achiever:** **Rohan Verma** achieved the highest overall average of **99.20** marks across all 5 subjects.
4. **Academic Standing:** **11 students (44.0%)** secured First Class, while **10 students (40.0%)** attained Distinction.
5. **Overall Class Pass Rate:** **24 out of 25 students (96.0%)** passed the examination with an average score of 40 or higher.
6. **Score Range & Spread:** Student averages range from **23.00** (Rahul Nair) to **99.20** (Rohan Verma), with a cohort average of **74.24** marks.

---

## 💻 How to Run & Refresh

### Run the Standalone Script
```bash
python data_analysis.py
```
*(Loads `dataset.csv`, cleans missing data, re-computes all metrics, saves the 4 charts in `charts/`, and prints dynamic insights).*

### Run the Jupyter Notebook
Open [`data_analysis.ipynb`](data_analysis.ipynb) in VS Code and click **Run All**.

---

## 📁 Project Structure

```text
Day-7/
├── dataset.csv            # Student dataset (25 rows x 10 columns)
├── data_analysis.ipynb    # Interactive notebook with dynamic charts & insights
├── data_analysis.py       # Standalone executable Python runner
├── README.md              # Project documentation and summary
└── charts/                # Exported high-resolution chart images
    ├── bar_chart.png
    ├── histogram.png
    ├── pie_chart.png
    └── line_chart.png
```

---

## 💡 Conclusion

This Week 1 Mini Project integrated data loading, cleaning, feature derivation, statistical visualization, and dynamic programmatic reporting into an end-to-end Python pipeline, providing actionable educational feedback with zero hardcoding.
