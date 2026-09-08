# Day 9 – Dynamic Exploratory Data Analysis (EDA)

- **Date:** 08 September 2026
- **Training Day:** Day 9
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0 | Matplotlib 3.11.0 | Seaborn 0.13.2

---

## 🎯 Learning Objectives

- **Explore datasets before training models:** Acquire deep architectural understanding of data schemas, distributions, and demographic structures prior to downstream feature engineering or predictive modeling.
- **Understand patterns and relationships in data:** Formulate descriptive hypotheses by mapping bivariate and multivariate relationships dynamically without preconceived assumptions.

---

## 📺 Recommended Learning Resources

- **YouTube Search Topics:**
  - *Exploratory Data Analysis Python*
  - *EDA using Pandas*
  - *Data Analysis Project*
- **Recommended Channels:**
  - **Codebasics** (Step-by-step EDA workflows, business intelligence fundamentals)
  - **CampusX** (Mathematical statistics, univariate/multivariate distributions)
  - **Krish Naik** (Feature analysis pipelines, outlier detection, and visualization best practices)
- **Official Documentation:**
  - [Pandas Documentation](https://pandas.pydata.org/docs/)
  - [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

---

## 💻 Tasks & Dynamic Architecture

The Day 9 curriculum requires conducting a **100% Data-Driven, Dynamic Exploratory Data Analysis (EDA)** on the sanitized dataset from Day 8:

```text
RAW CLEANED DATA (cleaned_dataset.csv)
                 ↓
      DYNAMIC DATA DISCOVERY
                 ↓
       DYNAMIC STATISTICS
                 ↓
        DYNAMIC ANALYSIS
                 ↓
     DYNAMIC VISUALIZATIONS (5 Charts)
                 ↓
    DYNAMIC BUSINESS INSIGHTS (5 Insights)
                 ↓
            VALIDATION
                 ↓
           LOCAL GIT COMMIT
```

### Core Architecture Rules Applied:
1. **Zero Hardcoding:** No category names, row counts, percentage shares, chart labels, or fixed insight sentences are hardcoded.
2. **Schema Invariant:** If `cleaned_dataset.csv` is updated or replaced with an altered extract, all statistics, charts, labels, and business insight statements recompute automatically.
3. **Purely Descriptive:** Insights describe observed empirical patterns without unfounded causal claims.

---

## 📊 Summary of Dynamic Deliverables

| Deliverable | Requirement | Status | File Location / Path |
| :--- | :--- | :---: | :--- |
| **EDA Notebook** | 16-section interactive notebook | ✅ Completed | `Day-9/data_analysis.ipynb` |
| **Data Visualizations** | 5 high-resolution Seaborn/Matplotlib charts | ✅ Completed | `Day-9/charts/` |
| **Business Insights** | 5 dynamically derived business insights | ✅ Completed | Documented in Notebook & Runner |
| **Standalone Runner** | Executable standalone Python script | ✅ Completed | `Day-9/data_analysis.py` |
| **Project Summary** | Methodology & documentation | ✅ Completed | `Day-9/README.md` |
| **GitHub Updated** | Staged & committed locally | ⏳ Ready | Awaiting explicit push command (`PUSH DAY 9`) |

---

## 📈 Visualizations Generated (Exported to `charts/`)

1. **`1_category_distribution.png` — Category Distribution:**
   - Evaluates primary organizational or grouping distribution (e.g. department headcount) using ranked horizontal bar plotting.
2. **`2_numerical_comparison.png` — Numerical Comparison by Category:**
   - Dynamically pairs continuous numerical metrics with functional categories to analyze compensation/metric variation across divisions.
3. **`3_numerical_distribution.png` — Numerical Distribution:**
   - Renders univariate histogram with overlaid Kernel Density Estimation (KDE) curve, displaying dynamic dashed markers for sample Mean and Median.
4. **`4_part_to_whole.png` — Part-to-Whole Representation:**
   - Automatically assesses cardinality: renders an uncluttered donut/pie chart if categories $\le 7$; automatically transitions to horizontal bar ranking if cardinality $> 7$.
5. **`5_time_trend.png` — Time / Historical Intake Trend:**
   - Detects chronological features, isolates calendar years, and generates an annual intake volume line plot illustrating temporal trajectory.

---

## 💡 5 Programmatically Derived Business Insights

All insights are constructed dynamically from dataframe aggregates at runtime:
1. **Category Volume Concentration:** Computes dominant category volume and its exact percentage share of total records.
2. **Numerical Disparity Across Categories:** Determines highest and lowest categorical averages, computing the exact spread ratio between divisions.
3. **Central Tendency & Skewness:** Compares arithmetic mean against outlier-resistant median and standard deviation to determine distribution skewness.
4. **Proportional Demographics:** Evaluates part-to-whole categorical share of the largest demographic segment.
5. **Temporal Intake Dynamics:** Identifies historical recording span and determines the peak operational intake year.

---

## 💻 How to Run & Verify

### Option 1: Run the Interactive Jupyter Notebook
Open [`data_analysis.ipynb`](data_analysis.ipynb) in VS Code or JupyterLab and select **Run All**. All 16 sections execute sequentially with pre-rendered graphical outputs.

### Option 2: Run the Standalone Python Runner
```bash
python data_analysis.py
```
*(Automatically discovers `cleaned_dataset.csv`, computes statistics, generates all 5 charts in `charts/`, and outputs the 5 dynamic business insights).*
