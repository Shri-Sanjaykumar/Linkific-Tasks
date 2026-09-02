# Day 5 – Pandas & Basic Dataset Analysis

- **Date:** 02 September 2026
- **Training Day:** Day 5
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3

---

## 🎯 Objective

Learn how to work with tabular datasets using **Pandas**, understand DataFrames, inspect dataset structure, handle missing values, apply conditional filtering, and calculate summary statistics.

---

## 📖 Concepts Practiced

- **Pandas:** Primary library for structured data wrangling and analysis.
- **DataFrames:** 2D labeled tabular data structures with heterogeneous columns.
- **CSV Loading:** Reading flat files into DataFrames using `pd.read_csv()`.
- **head() and tail():** Inspecting top 5 and bottom 5 records.
- **Dataset Shape:** Checking dimensional attributes `(rows, columns)` using `df.shape`.
- **Missing Values:** Identifying and summing null values per column using `df.isnull().sum()`.
- **Filtering:** Subsetting data using relational conditions (`Salary > 70000`, `Department == 'Data Science'`, `Experience_Years >= 5`).
- **Summary Statistics:** Computing distribution metrics (count, mean, std, min, quartiles, max) with `df.describe()`.

---

## 💻 How to Run

### Run the Python Script via Terminal
```bash
python pandas_practice.py
```

### Run the Jupyter Notebook
Open [`pandas_practice.ipynb`](pandas_practice.ipynb) in VS Code or JupyterLab and run all cells.

---

## 🖥️ Execution Output

```text
Pandas Version: 3.0.3

Dataset 'dataset.csv' loaded successfully.

=== DataFrame Structure ===
Object Type: <class 'pandas.DataFrame'>
Columns    : ['Employee_ID', 'Name', 'Department', 'Age', 'Salary', 'Experience_Years']

Column Data Types:
Employee_ID           int64
Name                    str
Department              str
Age                   int64
Salary              float64
Experience_Years    float64
dtype: object

=== First 5 Rows (df.head()) ===
   Employee_ID          Name    Department  Age   Salary  Experience_Years
0          101  Aarav Sharma   Engineering   28  72000.0               4.0
1          102    Diya Patel     Marketing   24  52000.0               2.0
2          103   Rohan Verma   Engineering   32  88000.0               7.0
3          104   Ananya Iyer  Data Science   26  78000.0               3.0
4          105   Kavya Reddy     Marketing   29      NaN               5.0

=== Last 5 Rows (df.tail()) ===
   Employee_ID           Name    Department  Age   Salary  Experience_Years
5          106   Vikram Singh  Data Science   35  95000.0              10.0
6          107     Neha Joshi   Engineering   25  60000.0               2.0
7          108     Rahul Nair            HR   30  55000.0               NaN
8          109    Pooja Hegde  Data Science   27  82000.0               4.0
9          110  Siddharth Das            HR   31  58000.0               6.0

=== Dataset Dimensions ===
Shape: (10, 6)
Total Rows   : 10
Total Columns: 6

=== Missing Values Check (df.isnull().sum()) ===
Employee_ID         0
Name                0
Department          0
Age                 0
Salary              1
Experience_Years    1
dtype: int64
Total Missing Values in Dataset: 2

=== Filtering Condition 1: Salary > 70,000 ===
   Employee_ID          Name    Department  Age   Salary  Experience_Years
0          101  Aarav Sharma   Engineering   28  72000.0               4.0
2          103   Rohan Verma   Engineering   32  88000.0               7.0
3          104   Ananya Iyer  Data Science   26  78000.0               3.0
5          106  Vikram Singh  Data Science   35  95000.0              10.0
8          109   Pooja Hegde  Data Science   27  82000.0               4.0
Count: 5 employees meet this condition.

=== Filtering Condition 2: Department == 'Data Science' ===
   Employee_ID          Name    Department  Age   Salary  Experience_Years
3          104   Ananya Iyer  Data Science   26  78000.0               3.0
5          106  Vikram Singh  Data Science   35  95000.0              10.0
8          109   Pooja Hegde  Data Science   27  82000.0               4.0
Count: 3 employees in Data Science.

=== Filtering Condition 3: Experience_Years >= 5 ===
   Employee_ID           Name    Department  Age   Salary  Experience_Years
2          103    Rohan Verma   Engineering   32  88000.0               7.0
4          105    Kavya Reddy     Marketing   29      NaN               5.0
5          106   Vikram Singh  Data Science   35  95000.0              10.0
9          110  Siddharth Das            HR   31  58000.0               6.0
Count: 4 employees with 5+ years experience.

=== Summary Statistics of Numerical Columns (df.describe()) ===
       Employee_ID       Age        Salary  Experience_Years
count     10.00000  10.00000      9.000000          9.000000
mean     105.50000  28.70000  71111.111111          4.777778
std        3.02765   3.40098  15584.001768          2.587362
min      101.00000  24.00000  52000.000000          2.000000
25%      103.25000  26.25000  58000.000000          3.000000
50%      105.50000  28.50000  72000.000000          4.000000
75%      107.75000  30.75000  82000.000000          6.000000
max      110.00000  35.00000  95000.000000         10.000000

=== Summary Observations ===
- Total employees recorded: 10
- Missing data found in 'Salary' (1) and 'Experience_Years' (1).
- Average employee age is 28.7 years (ranging from 24 to 35).
- Average salary is 71111.11 (ranging from 52000 to 95000).
- 3 out of 10 employees belong to the Data Science team.
```

---

## 📦 Deliverables

- [`pandas_practice.py`](pandas_practice.py) — Standalone executable script with clear printouts.
- [`pandas_practice.ipynb`](pandas_practice.ipynb) — Interactive Jupyter Notebook with cell outputs.
- [`dataset.csv`](dataset.csv) — Sample tabular dataset.
- `README.md` — Day 5 summary documentation.

---

## 🔗 Learning References

- [Pandas Official Documentation — DataFrame Basics](https://pandas.pydata.org/docs/user_guide/dsintro.html#dataframe)
- [Codebasics](https://www.youtube.com/@codebasics)
- [CampusX](https://www.youtube.com/@CampusX-official)
- [Krish Naik](https://www.youtube.com/@krishnaik06)
