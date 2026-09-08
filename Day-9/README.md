# Day 9 – Exploratory Data Analysis (EDA)

- **Date:** 08 September 2026
- **Training Day:** Day 9
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0 | Matplotlib 3.11.0 | Seaborn 0.13.2

---

## 🎯 Learning Objectives

- **Explore datasets before training models:** Conduct comprehensive schema discovery, statistical profiling, and distribution checks on cleaned data.
- **Understand patterns and relationships in data:** Surface multivariate correlations, structural imbalances, central tendencies, and historical trajectories directly from the dataset.

---

## 📺 Recommended Learning Resources

- **YouTube Search Topics:**
  - *Exploratory Data Analysis Python*
  - *EDA using Pandas*
  - *Data Analysis Project*
- **Recommended Channels:**
  - **Codebasics** (Step-by-step EDA workflows, practical business intelligence)
  - **CampusX** (Mathematical statistics, distributions, and outlier mechanics)
  - **Krish Naik** (End-to-end data preprocessing pipelines and feature analysis)
- **Official Documentation:**
  - [Pandas Documentation — Descriptive Statistics](https://pandas.pydata.org/docs/)
  - [Matplotlib Documentation — Pyplot API](https://matplotlib.org/stable/contents.html)

---

## 💻 Tasks & Workflow Architecture

Day 9 focuses on conducting an **Exploratory Data Analysis (EDA)** on the sanitized dataset from Day 8 (`cleaned_dataset.csv`):

```text
CLEANED DATASET (Day-8/cleaned_dataset.csv)
                      ↓
           SCHEMA & TYPE DISCOVERY
                      ↓
            DESCRIPTIVE STATISTICS
                      ↓
       OUTLIER DETECTION & SKEWNESS (IQR)
                      ↓
   5 STATISTICAL VISUALIZATIONS (With Exact Value Labels)
                      ↓
              5 BUSINESS INSIGHTS
                      ↓
               LOCAL GIT COMMITS
```

### Analysis Highlights:
1. **Accurate Value Annotations on Visualizations:** Every chart displays direct, legible data values (exact headcounts, percentages, dollar averages, and peak indicators) to prevent ambiguity and visual clutter.
2. **Comprehensive Statistical Coverage:** Evaluates central tendency (mean, median), dispersion (standard deviation, IQR), and distributional shape (skewness).
3. **Empirical Business Insights:** All insights describe verified relationships observed in the dataset.

---

## 📊 Summary of Deliverables

| Deliverable | Description | Status | File Location / Path |
| :--- | :--- | :---: | :--- |
| **EDA Notebook** | 16-section interactive notebook with inline figures and cell outputs | ✅ Completed | `Day-9/data_analysis.ipynb` |
| **Data Visualizations** | 5 high-resolution Seaborn/Matplotlib charts with exact value labels | ✅ Completed | `Day-9/charts/` |
| **Business Insights** | 5 comprehensive, empirical business insights derived from metrics | ✅ Completed | Documented in Notebook & Runner |
| **Standalone Runner** | Executable standalone Python script for headless analysis | ✅ Completed | `Day-9/data_analysis.py` |
| **Comprehensive README** | Full documentation and project walkthrough | ✅ Completed | `Day-9/README.md` |
| **GitHub Updated** | Staged & committed locally across all repositories | ⏳ Ready | Awaiting explicit push command (`PUSH DAY 9`) |

---

## 📈 5 Data Visualizations (Exported to `charts/`)

All visualizations are generated with **exact, verified data values labeled directly on the charts**:

1. **`1_category_distribution.png` — Department Distribution (Horizontal Bar Chart):**
   * **Plotted Feature:** `department` (all 24 departments)
   * **Exact Labels:** Displays exact headcount and percentage share next to every bar (e.g. *Houston Police Department-HPD: 638 (31.9%)*, *Houston Fire Department (HFD): 384 (19.2%)*, *Public Works & Engineering-PWE: 343 (17.2%)*).
   * **Title:** `Department Distribution (Total: 2,000 Records)`

2. **`2_numerical_comparison.png` — Average Base Salary by Department (Horizontal Bar Chart):**
   * **Plotted Features:** `base_salary` grouped by `department`
   * **Exact Labels:** Ranks all 24 departments from highest to lowest with exact dollar amounts labeled on every bar (from *Legal Department: $104,960* down to *Convention and Entertainment: $38,397*).
   * **Title:** `Average Base Salary by Department`

3. **`3_numerical_distribution.png` — Base Salary Distribution (Histogram & KDE):**
   * **Plotted Feature:** `base_salary` (30 bins with KDE curve)
   * **Exact Labels:** Displays explicit vertical reference lines for **Sample Mean ($55,696.17)** and **Sample Median ($54,509.00)**, plus a summary statistics callout box showing Mean, Median, Standard Deviation ($21,068.07), and Skewness (+2.05 Right-Skewed).
   * **Title:** `Base Salary Distribution`

4. **`4_part_to_whole.png` — Race / Ethnicity Distribution (Donut Chart):**
   * **Plotted Feature:** `race`
   * **Exact Labels:** Clean side legend preventing any text collisions: *Black or African American: 735 (36.8%)*, *White: 665 (33.2%)*, *Hispanic/Latino: 480 (24.0%)*, *Asian/Pacific Islander: 107 (5.3%)*, *American Indian or Alaskan Native: 11 (0.5%)*, *Others: 2 (0.1%)*. Center circle displays *Total 2,000 Records*.
   * **Title:** `Race / Ethnicity Distribution (Part-to-Whole)`

5. **`5_time_trend.png` — Yearly Hiring Trend Over Time (Line Chart):**
   * **Plotted Feature:** `hire_date` grouped by calendar year (1958–2016)
   * **Exact Labels:** Longitudinal line trajectory with circular markers, shaded area under curve, and an explicit callout box pointing to the **Historical Peak: 147 hires (2015)**.
   * **Title:** `Yearly Hiring Trend Over Time (hire_date)`

---

## 💡 5 Business Insights Derived from Dataset

1. **Category Volume Concentration:** Within the `department` dimension, **'Houston Police Department-HPD'** represents the largest single segment with **638 records**, constituting **31.90%** of the total analyzed dataset. Together with Fire and Public Works, the top three departments account for **68.3%** of all personnel.
2. **Salary Disparity Across Departments:** Average `base_salary` varies significantly across `department` groups. The highest average is observed in **'Legal Department' at $104,959.53**, while the lowest average is in **'Convention and Entertainment' at $38,397.00**, representing a **2.73x spread** between the highest and lowest functional divisions.
3. **Central Tendency & Skewness:** The metric `base_salary` exhibits an overall mean of **$55,696.17** and a median of **$54,509.00** (standard deviation: **$21,068.07**, skewness: **+2.05**). Because the mean exceeds the median, the distribution is **positively skewed (right-skewed)**, driven by upper-tier executive salaries that elevate the arithmetic average.
4. **Workforce Demographic Share:** In the `race` breakdown, the primary classification is **'Black or African American'**, which comprises **735 records (36.75% of all records)**, followed by **'White' with 665 records (33.25%)** and **'Hispanic/Latino' with 480 records (24.00%)**, establishing the demographic distribution of the municipal workforce.
5. **Longitudinal Hiring Trajectory:** Historical records spanning from **1958 to 2016** reveal that peak hiring occurred in calendar year **2015**, with **147 records** logged during that twelve-month period, reflecting a sustained hiring surge from 2012 to 2015.

---

## 💻 How to Run & Verify

### Option 1: Run the Interactive Jupyter Notebook
Open [`data_analysis.ipynb`](data_analysis.ipynb) in VS Code or JupyterLab and select **Run All**. All 14 sections execute with pre-rendered graphical displays and rich tables.

### Option 2: Run the Standalone Python Script
```bash
python data_analysis.py
```
*(Loads `Day-8/cleaned_dataset.csv`, computes summary statistics, generates all 5 labeled charts into `charts/`, and prints the 5 business insights).*
