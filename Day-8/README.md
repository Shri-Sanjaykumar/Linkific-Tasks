# Day 8 – Data Preprocessing & Data Cleaning

- **Date:** 07 September 2026
- **Training Day:** Day 8
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0
- **GitHub Status:** ✅ **Pushed & Up to Date** on both repositories:
  - [`Shri-Sanjaykumar/Linkific-Tasks`](https://github.com/Shri-Sanjaykumar/Linkific-Tasks)
  - [`Shri-Sanjaykumar/AI-ML-Internship`](https://github.com/Shri-Sanjaykumar/AI-ML-Internship)

---

## 🎯 Learning Objectives

- **Understand why data preprocessing is important:** Raw, real-world datasets often contain missing values, duplicate entries, unstandardized column headers, and incorrect data types that introduce bias into statistical analyses and cause machine learning models to fail.
- **Learn basic data cleaning techniques:** Gain hands-on competency in practical, reproducible data cleaning using Pandas and NumPy.

---

## 📺 Recommended Learning Resources

- **YouTube Search Topics:**
  - *Data Cleaning in Python*
  - *Data Preprocessing using Pandas*
  - *Missing Values in Machine Learning*
- **Recommended Channels:**
  - **Krish Naik** (End-to-end data preprocessing pipelines and feature engineering)
  - **CampusX** (Mathematical foundations of missing data imputation and outlier detection)
  - **Codebasics** (Practical, beginner-friendly Pandas tutorials and exercises)
- **Official Documentation:**
  - [Pandas Documentation – Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)

---

## 💻 Official Tasks & Implementation Workflow

The Day 8 curriculum requires the complete implementation of the following 7 data cleaning tasks:

### 1. Load a Dataset of Your Choice
- Ingested the authentic **City of Houston Public Employee Payroll Dataset** (`dataset.csv`).
- Dataset dimensions: **2,005 rows** and **10 columns**.
- Implemented robust dynamic path resolution supporting execution from both repository root and subdirectories.
- Inspected initial structural properties via `df.head()`, `df.shape`, `df.dtypes`, and `df.info()`.

### 2. Identify Missing Values
- Utilized `df.isnull().sum()` to quantify missing entries per column.
- Computed the grand total using `df.isnull().sum().sum()`.
- **Findings:**
  - `BASE_SALARY`: **114 missing values** (5.69%)
  - `RACE`: **35 missing values** (1.75%)
  - `JOB_DATE`: **3 missing values** (0.15%)
  - **Grand Total:** **152 missing values** across the dataset.

### 3. Handle Missing Values Using Appropriate Techniques
- **`BASE_SALARY` (Continuous Numerical):** Imputed with the **median** ($54,461.00). Salary distributions are positively skewed by high-earning management positions; the median is outlier-resistant and preserves central tendency better than the mean.
- **`RACE` (Nominal Categorical):** Imputed with the **mode** (`Black or African American`). Nominal categories cannot have a mathematical mean or median; the most frequent class preserves category distributions.
- **`JOB_DATE` (Date):** Imputed with the employee's initial **`HIRE_DATE`** as the logical administrative baseline for when their municipal tenure began.
- **Post-Imputation Verification:** Confirmed that total missing values remaining equals **0**.

### 4. Remove Duplicate Records
- Evaluated duplicate presence using `df.duplicated().sum()`.
- Detected **5 duplicate rows** in the raw dataset (indices 2000–2004 duplicating indices 10–14).
- Executed `df = df.drop_duplicates()` to eliminate redundant records.
- Verified that the row count reduced from **2,005 to 2,000**, with **0 duplicate rows remaining**.

### 5. Rename Columns Where Necessary
- The raw dataset used all-uppercase column names (`UNIQUE_ID`, `BASE_SALARY`).
- Standardized all 10 columns to Pythonic `snake_case` conventions to conform to PEP 8 standards:
  - `UNIQUE_ID` → `employee_id`
  - `POSITION_TITLE` → `position_title`
  - `DEPARTMENT` → `department`
  - `BASE_SALARY` → `base_salary`
  - `RACE` → `race`
  - `EMPLOYMENT_TYPE` → `employment_type`
  - `GENDER` → `gender`
  - `EMPLOYMENT_STATUS` → `employment_status`
  - `HIRE_DATE` → `hire_date`
  - `JOB_DATE` → `job_date`

### 6. Convert Incorrect Data Types
- Converted date strings (`hire_date`, `job_date`) from generic `object` to `datetime64[ns]` using `pd.to_datetime(..., errors="coerce")`, enabling temporal filtering and duration arithmetic.
- Converted low-cardinality discrete columns (`gender`, `employment_type`) to `category` dtype using `.astype("category")`, reducing memory footprint and accelerating grouping operations.

### 7. Save the Cleaned Dataset
- Persisted the sanitized DataFrame to `cleaned_dataset.csv` without synthetic index columns (`index=False`).
- Preserved the raw `dataset.csv` intact to maintain complete auditability and data lineage.

---

## 📊 Direct Two-CSV Comparative Analysis

Below is the side-by-side programmatic comparison between the raw input file (`dataset.csv`) and the sanitized output file (`cleaned_dataset.csv`), verified directly from disk:

| Metric / Feature | `dataset.csv` (Raw) | `cleaned_dataset.csv` (Cleaned) | Difference / Outcome |
| :--- | :--- | :--- | :--- |
| **Total Rows (Records)** | **2,005** | **2,000** | **-5 duplicate rows purged** |
| **Total Columns** | 10 | 10 | Schema integrity preserved |
| **Missing Values (Total)** | **152** | **0** | **-152 missing values eliminated** |
| ↳ `BASE_SALARY` Nulls | 114 | 0 | Imputed with median ($54,461.00) |
| ↳ `RACE` Nulls | 35 | 0 | Imputed with mode ('Black or African American') |
| ↳ `JOB_DATE` Nulls | 3 | 0 | Imputed with corresponding `HIRE_DATE` |
| **Duplicate Records** | **5** | **0** | **-5 duplicates removed via `drop_duplicates()`** |
| **Column Naming Style** | `UPPERCASE` (`UNIQUE_ID`) | `snake_case` (`employee_id`) | Standardized Pythonic conventions |
| **Date Column Format** | `object` (raw strings) | `ISO 8601` (`YYYY-MM-DD`) | Standardized temporal representation |
| **Memory Optimization** | `object` categorical strings | `category` dtype | Reduced memory footprint |
| **File Size on Disk** | 245,908 bytes | 246,951 bytes | Both files validated on disk |

---

## 📂 Deliverables Checklist

| Deliverable | Requirement | Status | File Location / Link |
| :--- | :--- | :---: | :--- |
| **Cleaned Dataset** | Save sanitized dataset separately | ✅ Completed | `Day-8/cleaned_dataset.csv` |
| **Data Cleaning Notebook** | Complete step-by-step interactive notebook | ✅ Completed | `Day-8/data_preprocessing.ipynb` |
| **Data Cleaning Script** | Executable standalone Python runner | ✅ Completed | `Day-8/data_preprocessing.py` |
| **GitHub Updated** | Pushed to GitHub repositories | ✅ Completed (PUSHED TO GIT) | [Linkific-Tasks](https://github.com/Shri-Sanjaykumar/Linkific-Tasks) & [AI-ML-Internship](https://github.com/Shri-Sanjaykumar/AI-ML-Internship) |

---

## 💻 How to Run & Verify

### Option 1: Run the Interactive Jupyter Notebook
1. Open [`data_preprocessing.ipynb`](data_preprocessing.ipynb) in VS Code or JupyterLab.
2. Select the **Python 3** kernel.
3. Click **Run All** — all 23 cells will execute sequentially with pre-rendered, clean outputs.

### Option 2: Run the Standalone Python Runner
Open a terminal in the `Day-8` directory and execute:
```bash
python data_preprocessing.py
```
*(Ingests `dataset.csv`, executes Tasks 1 through 7, saves `cleaned_dataset.csv`, and outputs the complete side-by-side comparison table).*

---

## 📁 Project Structure

```text
Day-8/
├── dataset.csv                 # Raw dataset (2,005 rows, 10 cols, 152 nulls, 5 duplicates)
├── cleaned_dataset.csv         # Sanitized dataset (2,000 rows, 10 cols, 0 nulls, 0 duplicates)
├── data_preprocessing.ipynb    # Complete interactive cleaning notebook with outputs
├── data_preprocessing.py       # Standalone executable Python runner
└── README.md                   # Comprehensive documentation, metrics, and comparison
```

---

## 💡 Key Takeaways & Conclusion

- Data preprocessing is foundational to all machine learning pipelines: models trained on raw, noisy, or incomplete data produce unreliable predictions (*"Garbage In, Garbage Out"*).
- Missing data handling should always be context-driven: using the **median** for skewed numerical variables protects against outlier distortion, while the **mode** preserves frequency distributions for categorical variables.
- Standardizing column headers to `snake_case` and casting features to appropriate types (`datetime64`, `category`) improves code readability, memory performance, and operational reliability.\n
