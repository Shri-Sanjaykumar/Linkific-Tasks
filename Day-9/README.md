# Day 9 – Exploratory Data Analysis (EDA)

- **Date:** 08 September 2026
- **Training Day:** Day 9
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Organization:** Linkific
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | NumPy 2.5.0 | Matplotlib 3.11.0 | Seaborn 0.13.2

---

## 🎯 Day 9 Objective

The primary objective of Day 9 is to conduct an end-to-end Exploratory Data Analysis (EDA) on the preprocessed dataset prior to machine learning model training. This includes:
- Exploring dataset architecture, schema, feature types, and data completeness.
- Computing descriptive statistics, central tendencies, and dispersion metrics.
- Identifying trends, patterns, and group-level disparities directly from data.
- Creating 4–5 meaningful statistical visualizations with exact value annotations.
- Deriving 5 empirical business insights with practical interpretations.

---

## 📁 Dataset Source & Use

The analysis directly consumes the cleaned dataset generated during Day 8:
- **File:** `Day-8/cleaned_dataset.csv`
- **Integrity Status:** Verified with 0 missing values and 0 duplicate records.
- **Access Method:** Loaded via relative file path resolution to ensure complete repository portability.

---

## ⚙️ EDA Methodology

The analysis follows an automated, data-driven workflow:

```text
CLEANED DATASET (Day-8/cleaned_dataset.csv)
                      ↓
           SCHEMA & TYPE DISCOVERY
                      ↓
            DATA QUALITY AUDIT
                      ↓
            DESCRIPTIVE STATISTICS
                      ↓
          OUTLIER DETECTION & SPREAD (IQR)
                      ↓
          TREND & PATTERN IDENTIFICATION
                      ↓
    5 STATISTICAL VISUALIZATIONS (Exported to charts/)
                      ↓
             5 BUSINESS INSIGHTS
                      ↓
               LOCAL GIT COMMITS
```

1. **Schema & Type Discovery:** Programmatically classifies numerical columns, categorical features, and temporal dates.
2. **Data Quality Audit:** Confirms data cleanliness, missingness, and record uniqueness.
3. **Descriptive Statistics:** Calculates five-number summaries, mean, median, standard deviation, and variance.
4. **Distribution & Outlier Analysis:** Measures skewness and identifies statistical outliers using the Interquartile Range (IQR = Q3 - Q1) rule with 1.5x fence limits.
5. **Pattern Recognition:** Evaluates cross-category relationships and longitudinal trend patterns.

---

## 📈 Data Visualizations (Exported to `charts/`)

The analysis generates 5 high-resolution statistical visualizations saved to `Day-9/charts/`:

1. **`1_category_distribution.png` — Category Distribution (Horizontal Bar Chart):**
   - Evaluates record frequency across functional categories.
   - Annotates each bar with exact record count and percentage share.
2. **`2_numerical_comparison.png` — Group Comparison (Horizontal Bar Chart):**
   - Ranks categories by average continuous numerical metric.
   - Annotates each bar with exact currency/numerical values.
3. **`3_numerical_distribution.png` — Numerical Distribution (Histogram with KDE):**
   - Plots frequency distribution across 30 bins with a continuous KDE curve.
   - Features vertical reference dashed lines for sample mean and median.
   - Includes an inset callout box showing mean, median, standard deviation, and skewness.
4. **`4_part_to_whole.png` — Proportion Analysis (Donut Chart):**
   - Evaluates categorical part-to-whole composition.
   - Utilizes a structured side legend with exact counts and percentage shares, eliminating label overlap.
5. **`5_time_trend.png` — Longitudinal Trend Analysis (Line Chart):**
   - Tracks record intake volume over calendar years.
   - Features markers, a subtle filled area under the curve, and an annotated callout box highlighting historical peak intake with 25% upper headroom.

---

## 💡 Business Insights Methodology

The analysis derives 5 empirical business insights directly from calculated metrics. Each insight follows a two-part format:
- **Finding:** The precise quantitative observation calculated from the dataset.
- **Business Meaning:** A conservative, practical interpretation explaining why the finding is relevant for operational planning, budgeting, or workforce management without drawing unsupported causal conclusions.

---

## 🛠️ Tools and Technologies Used

- **Language:** Python 3.14.3
- **Data Manipulation:** Pandas 3.0.3, NumPy 2.5.0
- **Data Visualization:** Matplotlib 3.11.0, Seaborn 0.13.2
- **Environment:** Jupyter Notebook, VS Code, PowerShell
- **Version Control:** Git, GitHub

---

## 🏁 Conclusion

The Day 9 Exploratory Data Analysis establishes a solid analytical foundation for the dataset. By identifying feature distributions, category concentrations, salary variances, and historical trends directly through data-driven calculations, the pipeline ensures that subsequent machine learning models are built upon well-understood data patterns.

---

## 💻 How to Run & Verify

### Option 1: Run the Interactive Jupyter Notebook
Open [`data_analysis.ipynb`](data_analysis.ipynb) in VS Code or JupyterLab and select **Run All**. All 16 sections execute with pre-rendered displays and zero errors.

### Option 2: Run the Standalone Python Script
```bash
python data_analysis.py
```
*(Ingests `Day-8/cleaned_dataset.csv`, executes the analysis, saves all 5 charts to `charts/`, and outputs the 5 business insights).*
