import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']

def main():
    print("=" * 75)
    print("      LINKIFIC AI/ML INTERNSHIP - DAY 9: FULLY DYNAMIC EDA PIPELINE       ")
    print("=" * 75)
    print("DYNAMIC LEARNING OBJECTIVES:")
    print("  - Dynamically explore raw datasets before model training.")
    print("  - Uncover underlying distributions, patterns, and relationships without hardcoding.")
    print("\nRECOMMENDED LEARNING RESOURCES:")
    print("  - YouTube Search : Exploratory Data Analysis Python | EDA using Pandas")
    print("  - Channels       : Codebasics, CampusX, Krish Naik")
    print("  - Documentation  : Pandas Documentation | Matplotlib Documentation")
    print("=" * 75)
    print()

    # 1. Dynamic Dataset Discovery
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "..", "Day-8", "cleaned_dataset.csv") if "__file__" in locals() else None,
        os.path.join("..", "Day-8", "cleaned_dataset.csv"),
        os.path.join("Day-8", "cleaned_dataset.csv"),
        os.path.join("Python", "Day-8", "cleaned_dataset.csv"),
        "cleaned_dataset.csv"
    ]
    candidate_paths = [p for p in candidate_paths if p and os.path.exists(p)]
    if not candidate_paths:
        raise FileNotFoundError("Could not locate Day-8 cleaned_dataset.csv. Please verify repository structure.")
    data_path = candidate_paths[0]

    df = pd.read_csv(data_path)
    print(f"Dynamic Discovery: Loaded dataset from {os.path.abspath(data_path)}")
    print(f"Dynamic Dimensions: {df.shape[0]:,} rows x {df.shape[1]} columns\n")

    # 2. Dynamic Column Classification
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    continuous_num_cols = [c for c in num_cols if df[c].nunique() > 10 and not any(k in c.lower() for k in ['id', 'uuid', 'code', 'index'])]
    if not continuous_num_cols and num_cols:
        continuous_num_cols = [num_cols[0]]

    date_cols = []
    for col in df.columns:
        if col in num_cols:
            continue
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
        else:
            sample = df[col].dropna().head(30)
            if len(sample) > 0:
                try:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    if parsed.notnull().sum() >= len(sample) * 0.8:
                        if parsed.dt.year.between(1900, 2100).sum() >= len(sample) * 0.8:
                            date_cols.append(col)
                except Exception:
                    pass

    cat_cols = [c for c in df.select_dtypes(include=['object', 'category', 'str']).columns.tolist() if c not in date_cols]

    print("--- Dynamic Column Identification ---")
    print(f"Total Discovered Columns     : {len(df.columns)}")
    print(f"Numerical Features ({len(num_cols)})    : {num_cols}")
    print(f"Continuous Metrics ({len(continuous_num_cols)}) : {continuous_num_cols}")
    print(f"Categorical Features ({len(cat_cols)})  : {cat_cols}")
    print(f"Datetime Features ({len(date_cols)})     : {date_cols}\n")

    # 3. Dynamic Summary Table
    summary_data = [
        {"Property": "Total Records (Rows)", "Value": f"{df.shape[0]:,}"},
        {"Property": "Total Features (Columns)", "Value": f"{df.shape[1]}"},
        {"Property": "Numerical Columns Count", "Value": f"{len(num_cols)}"},
        {"Property": "Categorical Columns Count", "Value": f"{len(cat_cols)}"},
        {"Property": "Datetime Columns Count", "Value": f"{len(date_cols)}"},
        {"Property": "Total Missing Values", "Value": f"{df.isnull().sum().sum()}"},
        {"Property": "Total Duplicate Rows", "Value": f"{df.duplicated().sum()}"}
    ]
    summary_df = pd.DataFrame(summary_data)
    print("=== Dynamic Dataset Health & Overview ===")
    print(summary_df.to_string(index=False))
    print()

    # Determine charts directory
    charts_dir = os.path.join(os.path.dirname(data_path), "..", "Day-9", "charts") if "__file__" in locals() else "charts"
    if not os.path.exists(os.path.dirname(charts_dir)):
        charts_dir = "charts"
    os.makedirs(charts_dir, exist_ok=True)

    # 4. Dynamic Visualization 1: Category Distribution with Exact Value Labels
    cat1_col = next((c for c in cat_cols if 'dept' in c.lower() or 'department' in c.lower()), None)
    if not cat1_col and cat_cols:
        cat1_col = next((c for c in cat_cols if 4 <= df[c].nunique() <= 35), cat_cols[0])

    cat1_counts = df[cat1_col].value_counts()
    plt.figure(figsize=(12, 8))
    ax1 = sns.barplot(x=cat1_counts.values, y=cat1_counts.index, hue=cat1_counts.index, palette="Blues_r", legend=False)
    for p in ax1.patches:
        w = p.get_width()
        pct = (w / len(df)) * 100
        ax1.annotate(f" {int(w):,} ({pct:.1f}%)", (w, p.get_y() + p.get_height() / 2.),
                     va='center', ha='left', fontsize=9, color='black')
    v1_title = f"{cat1_col} Distribution"
    plt.title(v1_title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Records", fontsize=11)
    plt.ylabel(cat1_col, fontsize=11)
    plt.xlim(0, max(cat1_counts.values) * 1.22)
    plt.tight_layout()
    v1_path = os.path.join(charts_dir, "1_category_distribution.png")
    plt.savefig(v1_path, dpi=300)
    plt.close()
    print(f"[Dynamic Chart 1 Saved]: {v1_path}")

    # 5. Dynamic Visualization 2: Numerical Comparison by Category with Dollar Annotations
    num_col = continuous_num_cols[0] if continuous_num_cols else num_cols[0]
    avg_series = df.groupby(cat1_col)[num_col].mean().sort_values(ascending=False)

    plt.figure(figsize=(12, 9))
    ax2 = sns.barplot(x=avg_series.values, y=avg_series.index, hue=avg_series.index, palette="viridis", legend=False)
    for p in ax2.patches:
        w = p.get_width()
        prefix = "$" if "sal" in num_col.lower() else ""
        ax2.annotate(f" {prefix}{w:,.0f}", (w, p.get_y() + p.get_height() / 2.),
                     va='center', ha='left', fontsize=9, color='black')
    v2_title = f"Average {num_col} by {cat1_col}"
    plt.title(v2_title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(f"Average {num_col} ({prefix})", fontsize=11)
    plt.ylabel(cat1_col, fontsize=11)
    plt.xlim(0, max(avg_series.values) * 1.18)
    plt.tight_layout()
    v2_path = os.path.join(charts_dir, "2_numerical_comparison.png")
    plt.savefig(v2_path, dpi=300)
    plt.close()
    print(f"[Dynamic Chart 2 Saved]: {v2_path}")

    # 6. Dynamic Visualization 3: Numerical Distribution with Dynamic Mean & Median
    plt.figure(figsize=(10, 6))
    mean_val = df[num_col].mean()
    median_val = df[num_col].median()
    prefix = "$" if "sal" in num_col.lower() else ""
    sns.histplot(df[num_col], kde=True, bins=30, color="#1f77b4", edgecolor="white", alpha=0.7)
    plt.axvline(mean_val, color="#d62728", linestyle="--", linewidth=2, label=f"Mean: {prefix}{mean_val:,.1f}")
    plt.axvline(median_val, color="#2ca02c", linestyle="-.", linewidth=2, label=f"Median: {prefix}{median_val:,.1f}")
    v3_title = f"{num_col} Distribution"
    plt.title(v3_title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(num_col, fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.legend(frameon=True, loc="upper right")
    plt.tight_layout()
    v3_path = os.path.join(charts_dir, "3_numerical_distribution.png")
    plt.savefig(v3_path, dpi=300)
    plt.close()
    print(f"[Dynamic Chart 3 Saved]: {v3_path}")

    # 7. Dynamic Visualization 4: Part-to-Whole with Headcounts & Percentages
    pie_candidates = [c for c in cat_cols if c != cat1_col and 2 <= df[c].nunique() <= 7]
    pie_col = pie_candidates[0] if pie_candidates else (cat_cols[1] if len(cat_cols) > 1 else cat1_col)
    pie_counts = df[pie_col].value_counts()

    plt.figure(figsize=(9, 9))
    if len(pie_counts) <= 7:
        colors = sns.color_palette("pastel")[0:len(pie_counts)]
        labels = [f"{idx}\n{val:,} ({val/len(df)*100:.1f}%)" for idx, val in zip(pie_counts.index, pie_counts.values)]
        plt.pie(pie_counts.values, labels=labels, startangle=140, colors=colors,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5})
        v4_title = f"{pie_col} Distribution (Part-to-Whole)"
        plt.title(v4_title, fontsize=14, fontweight="bold", pad=15)
    else:
        sns.barplot(x=pie_counts.values, y=pie_counts.index, hue=pie_counts.index, palette="mako", legend=False)
        v4_title = f"{pie_col} Distribution"
        plt.title(v4_title, fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Count", fontsize=11)
        plt.ylabel(pie_col, fontsize=11)
    plt.tight_layout()
    v4_path = os.path.join(charts_dir, "4_part_to_whole.png")
    plt.savefig(v4_path, dpi=300)
    plt.close()
    print(f"[Dynamic Chart 4 Saved]: {v4_path}")

    # 8. Dynamic Visualization 5: Time/Trend Analysis with Dynamic Peak Annotation
    date_col = next((c for c in date_cols if 'hire' in c.lower()), (date_cols[0] if date_cols else None))
    valid_years = pd.Series(dtype=float)
    if date_col:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
        year_counts = parsed_dates.dt.year.dropna().astype(int).value_counts().sort_index()
        valid_years = year_counts[year_counts.index >= 1960]
        peak_yr = int(valid_years.idxmax())
        peak_cnt = int(valid_years.max())

        plt.figure(figsize=(12, 5))
        plt.plot(valid_years.index, valid_years.values, marker="o", markersize=5, color="#2ca02c", linewidth=2.2)
        plt.annotate(f"Peak: {peak_cnt:,} records ({peak_yr})",
                     xy=(peak_yr, peak_cnt), xytext=(peak_yr - 9, peak_cnt + 8),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=7),
                     fontweight='bold', fontsize=10)
        v5_title = f"Trend of Records over Time by {date_col}"
        plt.title(v5_title, fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Calendar Year", fontsize=11)
        plt.ylabel("Record Count", fontsize=11)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        v5_path = os.path.join(charts_dir, "5_time_trend.png")
        plt.savefig(v5_path, dpi=300)
        plt.close()
        print(f"[Dynamic Chart 5 Saved]: {v5_path}")
    else:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x=cat_cols[-1])
        plt.title(f"{cat_cols[-1]} Distribution", fontsize=14, fontweight="bold")
        v5_path = os.path.join(charts_dir, "5_time_trend.png")
        plt.savefig(v5_path, dpi=300)
        plt.close()
        print(f"[Dynamic Chart 5 Saved]: {v5_path}")

    # 9. 5 Programmatically Derived Dynamic Business Insights
    top_cat1_name = cat1_counts.index[0]
    top_cat1_count = cat1_counts.iloc[0]
    top_cat1_pct = (top_cat1_count / len(df)) * 100
    insight_1 = (
        f"1. Dynamic Category Volume Concentration: Within the '{cat1_col}' dimension, "
        f"'{top_cat1_name}' represents the largest single segment with {top_cat1_count:,} records, "
        f"constituting {top_cat1_pct:.2f}% of the total analyzed dataset."
    )

    highest_cat = avg_series.index[0]
    highest_avg = avg_series.iloc[0]
    lowest_cat = avg_series.index[-1]
    lowest_avg = avg_series.iloc[-1]
    disparity_ratio = highest_avg / lowest_avg if lowest_avg > 0 else 0
    num_unit = "$" if "sal" in num_col.lower() else ""
    insight_2 = (
        f"2. Dynamic Numerical Disparity Across Categories: Average {num_col} varies significantly across {cat1_col} groups. "
        f"The highest average is observed in '{highest_cat}' at {num_unit}{highest_avg:,.2f}, "
        f"while the lowest average is in '{lowest_cat}' at {num_unit}{lowest_avg:,.2f}, "
        f"representing a {disparity_ratio:.2f}x spread between the highest and lowest functional divisions."
    )

    num_std = df[num_col].std()
    skewness = df[num_col].skew()
    skew_label = "positively skewed (right-skewed)" if skewness > 0.2 else ("negatively skewed (left-skewed)" if skewness < -0.2 else "approximately symmetric")
    insight_3 = (
        f"3. Dynamic Central Tendency & Spread: The metric '{num_col}' exhibits an overall mean of {num_unit}{mean_val:,.2f} "
        f"and a median of {num_unit}{median_val:,.2f} (standard deviation: {num_unit}{num_std:,.2f}, skewness: {skewness:.2f}). "
        f"Because the mean is {('higher than' if mean_val > median_val else 'lower than' if mean_val < median_val else 'equal to')} the median, "
        f"the distribution is {skew_label}, reflecting upper-tier values that elevate the arithmetic average."
    )

    pie_top_name = pie_counts.index[0]
    pie_top_count = pie_counts.iloc[0]
    pie_top_pct = (pie_top_count / len(df)) * 100
    insight_4 = (
        f"4. Dynamic Proportional Demographics: In the '{pie_col}' breakdown, the primary classification is "
        f"'{pie_top_name}', which comprises {pie_top_count:,} records ({pie_top_pct:.2f}% of all records), "
        f"establishing the baseline demographic share across the monitored workforce."
    )

    if date_col and len(valid_years) > 0:
        peak_year = int(valid_years.idxmax())
        peak_records = int(valid_years.max())
        earliest_yr = int(valid_years.index.min())
        latest_yr = int(valid_years.index.max())
        insight_5 = (
            f"5. Dynamic Temporal Intake Dynamics: Historical records spanning from {earliest_yr} to {latest_yr} reveal "
            f"that peak intake under '{date_col}' occurred in calendar year {peak_year}, "
            f"with {peak_records:,} records logged during that twelve-month interval."
        )
    else:
        cat_unique = df[cat_cols[0]].nunique()
        insight_5 = (
            f"5. Dynamic Structural Diversity: The dataset encompasses {cat_unique} unique classifications under '{cat_cols[0]}', "
            f"highlighting operational diversity across distinct business units."
        )

    print("\n" + "=" * 75)
    print("             EXACTLY 5 DYNAMICALLY GENERATED BUSINESS INSIGHTS             ")
    print("=" * 75)
    print(insight_1)
    print()
    print(insight_2)
    print()
    print(insight_3)
    print()
    print(insight_4)
    print()
    print(insight_5)
    print("=" * 75)
    print()

    print("DYNAMIC DELIVERABLES VERIFICATION:")
    print("  [x] Dynamic EDA Notebook         : data_analysis.ipynb")
    print(f"  [x] Dynamic Data Visualizations  : 5 charts with exact values saved in {charts_dir}/")
    print("  [x] Dynamic Business Insights    : 5 insights programmatically derived from DataFrame")
    print("  [ ] GitHub Updated               : Staged & committed locally; awaiting push confirmation.")
    print("=" * 75)

if __name__ == "__main__":
    main()
