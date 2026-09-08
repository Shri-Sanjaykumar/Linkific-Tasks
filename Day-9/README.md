# Day 9 – Dynamic Exploratory Data Analysis (EDA)

- **Date:** 08 September 2026
- **Training Day:** Day 9
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0 | Matplotlib 3.11.0 | Seaborn 0.13.2

---

## 🎯 Dynamic Learning Objectives

- **Dynamically explore datasets before training models:** Conduct comprehensive, automated schema discovery, statistical profiling, and distribution checks on raw data without static assumptions.
- **Understand patterns and relationships directly from data:** Identify multivariate dependencies, structural imbalances, central tendencies, and historical trajectories driven 100% by programmatic DataFrame calculations.

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

## 💻 Tasks & Dynamic Architecture

The Day 9 curriculum requires executing a **100% Data-Driven, Dynamic Exploratory Data Analysis (EDA)** on the sanitized dataset from Day 8 (`cleaned_dataset.csv`):

```text
RAW CLEANED DATA (Day-8/cleaned_dataset.csv)
                      ↓
          DYNAMIC DATA DISCOVERY
                      ↓
           DYNAMIC STATISTICS
                      ↓
            DYNAMIC ANALYSIS
                      ↓
    DYNAMIC VISUALIZATIONS (5 Charts with Exact Value Labels)
                      ↓
    DYNAMIC BUSINESS INSIGHTS (5 Programmatic Insights)
                      ↓
       DYNAMIC ROBUSTNESS VALIDATION
                      ↓
           LOCAL GIT COMMIT
```

### Core Architecture Rules Enforced:
1. **Zero Hardcoded Data Values:** No row counts, categories, salary values, percentages, or static insight text are hardcoded.
2. **Schema-Adaptive Logic:** If `cleaned_dataset.csv` is updated, extended, or replaced, every metric, chart, label, and insight sentence updates automatically upon execution.
3. **Exact Value Annotations on Visualizations:** Every chart displays direct, legible data values (exact headcounts, percentages, dollar averages, and peak indicators) to prevent ambiguity.
4. **Descriptive Empirical Insights:** All business insights describe observable data relationships without making unfounded causal leaps.

---

## 📊 Summary of Dynamic Deliverables

| Deliverable | Requirement | Status | File Location / Path |
| :--- | :--- | :---: | :--- |
| **Dynamic EDA Notebook** | 16-section interactive notebook with inline figures | ✅ Completed | `Day-9/data_analysis.ipynb` |
| **Dynamic Visualizations** | 5 high-resolution Seaborn/Matplotlib charts with labels | ✅ Completed | `Day-9/charts/` |
| **Dynamic Business Insights** | 5 programmatically derived business insights | ✅ Completed | Documented in Notebook & Runner |
| **Dynamic Standalone Runner** | Executable standalone Python script | ✅ Completed | `Day-9/data_analysis.py` |
| **Comprehensive README** | Full methodology & dynamic documentation | ✅ Completed | `Day-9/README.md` |
| **GitHub Updated** | Staged & committed locally across all repositories | ⏳ Ready | Awaiting explicit push command (`PUSH DAY 9`) |

---

## 📈 5 Dynamic Visualizations (Exported to `charts/`)

All visualizations are generated with **exact, verified data values labeled directly on the charts**:

1. **`1_category_distribution.png` — Category Distribution (Bar Chart):**
   * **Plotted Feature:** `department`
   * **Enhancement:** Displays exact headcount and percentage share next to every bar (e.g. *Houston Police Department-HPD: 638 (31.9%)*, *Houston Fire Department: 384 (19.2%)*, *Public Works: 343 (17.2%)*).
   * **Dynamic Title:** `department Distribution`

2. **`2_numerical_comparison.png` — Numerical Comparison by Category (Bar Chart):**
   * **Plotted Features:** `base_salary` grouped by `department`
   * **Enhancement:** Ranks all 24 departments from highest to lowest with exact dollar amounts labeled on every bar (from *Legal Department: $104,960* down to *Convention and Entertainment: $38,397*).
   * **Dynamic Title:** `Average base_salary by department`

3. **`3_numerical_distribution.png` — Numerical Distribution (Histogram & KDE):**
   * **Plotted Feature:** `base_salary` (30 bins with KDE curve)
   * **Enhancement:** Displays explicit vertical reference lines and legend indicators for **Sample Mean ($55,696.17)** and **Sample Median ($54,509.00)**.
   * **Dynamic Title:** `base_salary Distribution`

4. **`4_part_to_whole.png` — Part-to-Whole Share (Donut / Pie Chart):**
   * **Plotted Feature:** `race` (cardinality $\le 7$)
   * **Enhancement:** Annotates each pie slice with category name, exact count, and percentage share (*Black or African American: 735 (36.8%)*, *White: 665 (33.2%)*, *Hispanic/Latino: 480 (24.0%)*, *Asian/Pacific Islander: 107 (5.4%)*).
   * **Dynamic Title:** `race Distribution (Part-to-Whole)`

5. **`5_time_trend.png` — Time / Longitudinal Intake Trend (Line Chart):**
   * **Plotted Feature:** `hire_date` grouped by calendar year (1968–2016)
   * **Enhancement:** Line trajectory with circular markers and an explicit callout arrow pointing to the **Historical Peak: 147 hires (2015)**.
   * **Dynamic Title:** `Trend of Records over Time by hire_date`

---

## 💡 5 Programmatically Derived Dynamic Business Insights

These insights are derived strictly from DataFrame variables calculated at runtime:

1. **Dynamic Category Volume Concentration:** Within the `department` dimension, **'Houston Police Department-HPD'** represents the largest single segment with **638 records**, constituting **31.90%** of the total analyzed dataset.
2. **Dynamic Numerical Disparity Across Categories:** Average `base_salary` varies significantly across `department` groups. The highest average is observed in **'Legal Department' at $104,959.53**, while the lowest average is in **'Convention and Entertainment' at $38,397.00**, representing a **2.73x spread** between the highest and lowest functional divisions.
3. **Dynamic Central Tendency & Spread:** The metric `base_salary` exhibits an overall mean of **$55,696.17** and a median of **$54,509.00** (standard deviation: **$21,068.07**, skewness: **2.05**). Because the mean is higher than the median, the distribution is **positively skewed (right-skewed)**, reflecting upper-tier values that elevate the arithmetic average.
4. **Dynamic Proportional Demographics:** In the `race` breakdown, the primary classification is **'Black or African American'**, which comprises **735 records (36.75% of all records)**, establishing the baseline demographic share across the monitored workforce.
5. **Dynamic Temporal Intake Dynamics:** Historical records spanning from **1968 to 2016** reveal that peak intake under `hire_date` occurred in calendar year **2015**, with **147 records** logged during that twelve-month interval.

---

## 🧪 Dynamic Robustness Verification

The dynamic architecture was verified using an automated perturbation test:
* Injected 800 synthetic employee records under an `'Artificial Intelligence Lab'` department with 2026 hire dates.
* Re-executed the dynamic engine:
  * Total shape adapted from `(2000, 10)` to `(2800, 10)`.
  * Top department dynamically adapted to `'Artificial Intelligence Lab'` (800 records).
  * Top average salary dynamically adapted to `'Artificial Intelligence Lab'` ($180,087.50).
  * Historical peak intake dynamically shifted to `2026`.
* Confirmed that zero hardcoded assumptions exist and purged all test files.

---

## 💻 How to Run & Verify

### Option 1: Run the Interactive Jupyter Notebook
Open [`data_analysis.ipynb`](data_analysis.ipynb) in VS Code or JupyterLab and click **Run All**. All 16 sections execute with pre-rendered graphical displays.

### Option 2: Run the Standalone Python Runner
```bash
python data_analysis.py
```
*(Ingests `Day-8/cleaned_dataset.csv`, executes dynamic analysis, exports all 5 labeled charts to `charts/`, and outputs the 5 dynamic business insights).*
