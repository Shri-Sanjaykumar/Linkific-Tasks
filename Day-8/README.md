# Day 8 – Data Preprocessing & Data Cleaning

- **Date:** 07 September 2026
- **Training Day:** Day 8
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0

---

## 🎯 Learning Objectives

- Understand why data preprocessing is critical for data analysis and machine learning.
- Master practical, beginner-friendly data cleaning techniques in Pandas.
- Detect and impute missing values using statistically sound strategies (median, mode, logical fallback).
- Detect and handle duplicate records.
- Standardize column names to clean, readable conventions.
- Cast columns to correct data types (datetime64, category).

---

## 🔗 Learning References & Resources

- **Documentation:** [Pandas Documentation – Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- **Key Study Topics:** Data Cleaning in Python, Data Preprocessing using Pandas, Missing Values in Machine Learning
- **Recommended Learning Channels:** Krish Naik, CampusX, Codebasics

---\n\n## 📋 Project Scope & Tasks

Master foundational **Data Preprocessing & Data Cleaning** workflows using **Pandas**. In real-world data science and machine learning applications, raw datasets frequently contain missing values, duplicate records, non-standard column headers, and incorrect data types. 

The goal of this day is to build a robust, reproducible data sanitization pipeline that:
1. Ingests raw tabular data and inspects structural health (`head()`, `shape`, `dtypes`, `info()`).
2. Detects and handles missing values using domain-appropriate imputation (median for skewed numerics, mode for categoricals, domain fallback for dates).
3. Detects duplicate records, executes idempotent duplicate removal, and demonstrates duplicate handling.
4. Renames non-standard uppercase headers to clean Pythonic `snake_case`.
5. Converts string dates and low-cardinality features to appropriate storage types (`datetime64[ns]`, `category`).
6. Validates the sanitized DataFrame and exports the clean dataset separately (`cleaned_dataset.csv`), maintaining raw data lineage.

---

## 📂 Dataset Overview

- **Dataset Name:** City of Houston Public Employee Payroll Dataset
- **Source:** City of Houston Open Data Portal / Packt Pandas Cookbook (Ted Petrou)
- **Record Count (Rows):** 2,000
- **Feature Count (Columns):** 10
- **Primary Purpose:** Public sector workforce analytics, departmental salary allocation, and employment demographics.

### Raw Column Schema
| Column Name | Raw Data Type | Description |
| :--- | :--- | :--- |
| `UNIQUE_ID` | `int64` | Unique numeric identifier for each employee record. |
| `POSITION_TITLE` | `object` (string) | Official municipal job title. |
| `DEPARTMENT` | `object` (string) | Department or municipal division. |
| `BASE_SALARY` | `float64` | Annual base salary in USD. Contains 114 missing values. |
| `RACE` | `object` (string) | Self-reported racial demographic. Contains 35 missing values. |
| `EMPLOYMENT_TYPE` | `object` (string) | Full Time vs. Part Time classification. |
| `GENDER` | `object` (string) | Employee gender (`Female`, `Male`). |
| `EMPLOYMENT_STATUS` | `object` (string) | Current active employment status. |
| `HIRE_DATE` | `object` (string) | Date employee initially joined the organization (`YYYY-MM-DD`). |
| `JOB_DATE` | `object` (string) | Date employee assumed current job position. Contains 3 missing values. |

---

## 🧹 Cleaning Operations

### 1. Missing Values (Detection & Handling)
- **Detection:** Identified missing entries using `df.isnull().sum()` and computed total missing entries with `df.isnull().sum().sum()`:
  - `BASE_SALARY`: **114 missing values** (5.7% of total records)
  - `RACE`: **35 missing values** (1.75% of total records)
  - `JOB_DATE`: **3 missing values** (0.15% of total records)
  - **Total Missing Entries:** **152 missing values**
- **Handling Strategy:**
  - `BASE_SALARY` (Numerical): Imputed with **median** ($54,461.00). Salary distributions in organizations are positively skewed by high-earning management positions; the median provides an outlier-robust measure of central tendency without introducing artificial bias.
  - `RACE` (Categorical): Imputed with **mode** (`Black or African American`). Nominal categories cannot have a mathematical mean or median; the most frequent class preserves category distributions.
  - `JOB_DATE` (Date): Imputed using the employee's initial **`HIRE_DATE`** as the administrative baseline proxy for when their organizational tenure began.
- **Verification:** Post-imputation check confirmed `df.isnull().sum().sum() == 0`.

### 2. Duplicate Records (Detection & Removal)
- **Detection:** Checked with `df.duplicated().sum()`. The authentic 2,000-record payroll extract contained **0 duplicate rows**.
- **Removal:** Executed `df = df.drop_duplicates()` to enforce idempotency and protect against redundant records during pipeline execution.
- **Controlled Demonstration:** Implemented a dedicated demonstration cell on sample data showing duplicate detection (`1 duplicate found`) and removal (`0 duplicates remaining`).

### 3. Column Renaming
- **Rationale:** The raw dataset used all-uppercase names (`UNIQUE_ID`, `POSITION_TITLE`, `BASE_SALARY`), which is cumbersome and inconsistent with Python style standards. `UNIQUE_ID` was also renamed to `employee_id` for clarity.
- **Mapping Applied:**
  - `UNIQUE_ID` -> `employee_id`
  - `POSITION_TITLE` -> `position_title`
  - `DEPARTMENT` -> `department`
  - `BASE_SALARY` -> `base_salary`
  - `RACE` -> `race`
  - `EMPLOYMENT_TYPE` -> `employment_type`
  - `GENDER` -> `gender`
  - `EMPLOYMENT_STATUS` -> `employment_status`
  - `HIRE_DATE` -> `hire_date`
  - `JOB_DATE` -> `job_date`

### 4. Data Type Conversion
- **Dates (`hire_date`, `job_date`):** Converted from generic string `object` to `datetime64[ns]` using `pd.to_datetime(..., errors="coerce")`. Enables date math, duration calculations, and time-series aggregations.
- **Categoricals (`gender`, `employment_type`):** Converted from string `object` to `category` using `.astype("category")`. Significantly reduces memory footprint and accelerates grouping/filtering operations.

### 5. Cleaned Dataset Export
- Persisted sanitized data to `cleaned_dataset.csv` using `df.to_csv("cleaned_dataset.csv", index=False)`.
- The original raw `dataset.csv` is preserved, maintaining a clear audit trail and reproducible pipeline.

---

## 🛠️ Technologies Used

- **Python (3.14.3):** Core programming runtime.
- **Pandas (3.0.3):** Tabular data preprocessing, null imputation, duplicate filtering, column renaming, and type conversion.
- **NumPy (2.5.0):** Numerical arrays and median calculation.
- **Jupyter Notebook & VS Code:** Interactive experimentation, step-by-step documentation, and execution.
- **Git & GitHub:** Version control, multi-repository tracking, and portfolio documentation.

---

## 📊 Before vs After Summary

| Metric / Dimension | Raw Dataset (Before) | Cleaned Dataset (After) | Status |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 2,000 | 2,000 | Preserved all valid records |
| **Total Columns** | 10 | 10 | Standardized column names |
| **Missing Values (Total)** | **152** | **0** | All missing entries imputed |
| `BASE_SALARY` Missing | 114 | 0 | Imputed with median ($54,461.00) |
| `RACE` Missing | 35 | 0 | Imputed with mode (Black or African American) |
| `JOB_DATE` Missing | 3 | 0 | Imputed with corresponding `hire_date` |
| **Duplicate Rows** | 0 | 0 | Verified with `drop_duplicates()` |
| **Datetime Columns** | 0 | 2 (`hire_date`, `job_date`) | Converted to `datetime64[ns]` |
| **Category Columns** | 0 | 2 (`gender`, `employment_type`) | Converted to `category` |
| **Column Casing** | UPPERCASE (`BASE_SALARY`) | snake_case (`base_salary`) | Standardized |

---

## 💻 How to Run & Verify

### Run the Interactive Jupyter Notebook
Open [`data_preprocessing.ipynb`](data_preprocessing.ipynb) in VS Code and click **Run All**.
All sections will execute sequentially with zero errors.

### Run the Standalone Python Runner
```bash
python data_preprocessing.py
```
*(Loads `dataset.csv`, executes the complete 10-step cleaning pipeline, saves `cleaned_dataset.csv`, and prints the health check report).*

---

## 📁 Project Structure

```text
Day-8/
├── dataset.csv                 # Raw employee dataset (2,000 rows x 10 columns)
├── cleaned_dataset.csv         # Cleaned, standardized dataset (0 nulls, optimal dtypes)
├── data_preprocessing.ipynb    # Complete 15-section interactive cleaning notebook
├── data_preprocessing.py       # Standalone executable Python cleaning runner
└── README.md                   # Comprehensive Day 8 documentation and summary
```

---

## 💡 Conclusion

Day 8 established critical data engineering hygiene:
- Learned that data cleaning is not about blindly dropping missing data, but applying **statistically sound, domain-appropriate imputation** (median for skewed continuous variables, mode for categorical variables).
- Standardized column headers and optimized storage data types to ensure downstream analytics, visualizations, and machine learning models operate reliably and efficiently without type errors.
