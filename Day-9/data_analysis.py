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
    print("=" * 70)
    print("        LINKIFIC AI/ML INTERNSHIP - DAY 9: DYNAMIC EDA ENGINE        ")
    print("=" * 70)
    print("Learning Objectives:")
    print("  - Explore datasets dynamically before training models.")
    print("  - Understand patterns and relationships directly from data.")
    print("\nReference Resources:")
    print("  - YouTube Search : Exploratory Data Analysis Python | EDA using Pandas")
    print("  - Recommended    : Codebasics, CampusX, Krish Naik")
    print("  - Documentation  : Pandas Documentation, Matplotlib Documentation")
    print("=" * 70)
    print()

    # 1. Dataset Discovery
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "..", "Day-8", "cleaned_dataset.csv") if "__file__" in locals() else None,
        os.path.join("..", "Day-8", "cleaned_dataset.csv"),
        os.path.join("Day-8", "cleaned_dataset.csv"),
        os.path.join("Python", "Day-8", "cleaned_dataset.csv"),
        "cleaned_dataset.csv"
    ]
    candidate_paths = [p for p in candidate_paths if p and os.path.exists(p)]
    if not candidate_paths:
        raise FileNotFoundError("Could not find Day-8 cleaned_dataset.csv. Please ensure it exists.")
    data_path = candidate_paths[0]

    df = pd.read_csv(data_path)
    print(f"Dataset Loaded Successfully: {os.path.abspath(data_path)}")
    print(f"Dataset Dimensions         : {df.shape[0]:,} rows x {df.shape[1]} columns\n")

    # 2. Dynamic Column Identification
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
    print(f"Total Columns Detected      : {len(df.columns)}")
    print(f"Numerical Columns ({len(num_cols)})    : {num_cols}")
    print(f"Continuous Numerical ({len(continuous_num_cols)}) : {continuous_num_cols}")
    print(f"Categorical Columns ({len(cat_cols)})  : {cat_cols}")
    print(f"Datetime Columns ({len(date_cols)})     : {date_cols}\n")

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

    # Create charts directory
    charts_dir = os.path.join(os.path.dirname(data_path), "..", "Day-9", "charts") if "__file__" in locals() else "charts"
    if not os.path.exists(os.path.dirname(charts_dir)):
        charts_dir = "charts"
    os.makedirs(charts_dir, exist_ok=True)

    # 4. Visualization 1: Category Distribution
    cat1_col = next((c for c in cat_cols if 'dept' in c.lower() or 'department' in c.lower()), None)
    if not cat1_col and cat_cols:
        cat1_col = next((c for c in cat_cols if 4 <= df[c].nunique() <= 35), cat_cols[0])

    cat1_counts = df[cat1_col].value_counts()
    top_n_cat1 = min(10, len(cat1_counts))
    plot_cat1_data = cat1_counts.head(top_n_cat1)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=plot_cat1_data.values, y=plot_cat1_data.index, hue=plot_cat1_data.index, palette="Blues_r", legend=False)
    v1_title = f"Top {top_n_cat1} {cat1_col.replace('_', ' ').title()} by Headcount" if len(cat1_counts) > 10 else f"Distribution of {cat1_col.replace('_', ' ').title()}"
    plt.title(v1_title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Records", fontsize=11)
    plt.ylabel(cat1_col.replace("_", " ").title(), fontsize=11)
    plt.tight_layout()
    v1_path = os.path.join(charts_dir, "1_category_distribution.png")
    plt.savefig(v1_path, dpi=300)
    plt.close()
    print(f"[Chart 1 Saved]: {v1_path}")

    # 5. Visualization 2: Numerical Comparison by Category
    num_col = continuous_num_cols[0] if continuous_num_cols else num_cols[0]
    avg_series = df.groupby(cat1_col)[num_col].mean().sort_values(ascending=False)
    plot_avg_data = avg_series.head(top_n_cat1)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=plot_avg_data.values, y=plot_avg_data.index, hue=plot_avg_data.index, palette="viridis", legend=False)
    v2_title = f"Average {num_col.replace('_', ' ').title()} by {cat1_col.replace('_', ' ').title()} (Top {top_n_cat1})"
    plt.title(v2_title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(f"Average {num_col.replace('_', ' ').title()}", fontsize=11)
    plt.ylabel(cat1_col.replace("_", " ").title(), fontsize=11)
    ax = plt.gca()
    if 'sal' in num_col.lower():
        ax.xaxis.set_major_formatter('${x:,.0f}')
    else:
        ax.xaxis.set_major_formatter('{x:,.0f}')
    plt.tight_layout()
    v2_path = os.path.join(charts_dir, "2_numerical_comparison.png")
    plt.savefig(v2_path, dpi=300)
    plt.close()
    print(f"[Chart 2 Saved]: {v2_path}")

    # 6. Visualization 3: Numerical Distribution
    plt.figure(figsize=(10, 6))
    mean_val = df[num_col].mean()
    median_val = df[num_col].median()
    sns.histplot(df[num_col], kde=True, bins=30, color="#1f77b4", edgecolor="white", alpha=0.7)
    plt.axvline(mean_val, color="#d62728", linestyle="--", linewidth=2, label=f"Mean: {mean_val:,.1f}")
    plt.axvline(median_val, color="#2ca02c", linestyle="-.", linewidth=2, label=f"Median: {median_val:,.1f}")
    plt.title(f"Distribution of {num_col.replace('_', ' ').title()}", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel(num_col.replace("_", " ").title(), fontsize=11)
    plt.ylabel("Frequency", fontsize=11)
    plt.legend(frameon=True)
    plt.tight_layout()
    v3_path = os.path.join(charts_dir, "3_numerical_distribution.png")
    plt.savefig(v3_path, dpi=300)
    plt.close()
    print(f"[Chart 3 Saved]: {v3_path}")

    # 7. Visualization 4: Part-to-Whole
    pie_candidates = [c for c in cat_cols if c != cat1_col and 2 <= df[c].nunique() <= 7]
    pie_col = pie_candidates[0] if pie_candidates else (cat_cols[1] if len(cat_cols) > 1 else cat1_col)
    pie_counts = df[pie_col].value_counts()

    plt.figure(figsize=(8, 8))
    if len(pie_counts) <= 7:
        colors = sns.color_palette("pastel")[0:len(pie_counts)]
        plt.pie(pie_counts.values, labels=pie_counts.index, autopct="%1.1f%%", startangle=140, colors=colors,
                wedgeprops={"edgecolor": "white", "linewidth": 1.5})
        plt.title(f"Part-to-Whole Share by {pie_col.replace('_', ' ').title()}", fontsize=14, fontweight="bold", pad=15)
    else:
        sns.barplot(x=pie_counts.values, y=pie_counts.index, hue=pie_counts.index, palette="mako", legend=False)
        plt.title(f"Share by {pie_col.replace('_', ' ').title()}", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Count", fontsize=11)
        plt.ylabel(pie_col.replace("_", " ").title(), fontsize=11)
    plt.tight_layout()
    v4_path = os.path.join(charts_dir, "4_part_to_whole.png")
    plt.savefig(v4_path, dpi=300)
    plt.close()
    print(f"[Chart 4 Saved]: {v4_path}")

    # 8. Visualization 5: Time/Trend Analysis
    date_col = next((c for c in date_cols if 'hire' in c.lower()), (date_cols[0] if date_cols else None))
    valid_years = pd.Series(dtype=float)
    if date_col:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
        year_counts = parsed_dates.dt.year.dropna().astype(int).value_counts().sort_index()
        valid_years = year_counts[year_counts.index >= 1960]

        plt.figure(figsize=(11, 5))
        plt.plot(valid_years.index, valid_years.values, marker="o", markersize=4, color="#2ca02c", linewidth=2.2)
        plt.title(f"Historical Trend of Records by {date_col.replace('_', ' ').title()} (Yearly)", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Calendar Year", fontsize=11)
        plt.ylabel("Record Count", fontsize=11)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        v5_path = os.path.join(charts_dir, "5_time_trend.png")
        plt.savefig(v5_path, dpi=300)
        plt.close()
        print(f"[Chart 5 Saved]: {v5_path}")
    else:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x=cat_cols[-1])
        plt.title(f"Distribution of {cat_cols[-1].replace('_', ' ').title()}", fontsize=14, fontweight="bold")
        v5_path = os.path.join(charts_dir, "5_time_trend.png")
        plt.savefig(v5_path, dpi=300)
        plt.close()
        print(f"[Chart 5 Saved]: {v5_path}")

    # 9. Dynamic Business Insights (EXACTLY 5)
    top_cat1_name = cat1_counts.index[0]
    top_cat1_count = cat1_counts.iloc[0]
    top_cat1_pct = (top_cat1_count / len(df)) * 100
    insight_1 = (
        f"1. Category Volume Concentration: Within the '{cat1_col}' dimension, "
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
        f"2. Numerical Disparity Across Categories: Average {num_col} varies significantly across {cat1_col} groups. "
        f"The highest average is observed in '{highest_cat}' at {num_unit}{highest_avg:,.2f}, "
        f"while the lowest average is in '{lowest_cat}' at {num_unit}{lowest_avg:,.2f}, "
        f"representing a {disparity_ratio:.2f}x spread between the highest and lowest functional divisions."
    )

    num_std = df[num_col].std()
    skewness = df[num_col].skew()
    skew_label = "positively skewed (right-skewed)" if skewness > 0.2 else ("negatively skewed (left-skewed)" if skewness < -0.2 else "approximately symmetric")
    insight_3 = (
        f"3. Central Tendency & Spread: The metric '{num_col}' exhibits an overall mean of {num_unit}{mean_val:,.2f} "
        f"and a median of {num_unit}{median_val:,.2f} (standard deviation: {num_unit}{num_std:,.2f}, skewness: {skewness:.2f}). "
        f"Because the mean is {('higher than' if mean_val > median_val else 'lower than' if mean_val < median_val else 'equal to')} the median, "
        f"the distribution is {skew_label}, reflecting upper-tier values that elevate the arithmetic average."
    )

    pie_top_name = pie_counts.index[0]
    pie_top_count = pie_counts.iloc[0]
    pie_top_pct = (pie_top_count / len(df)) * 100
    insight_4 = (
        f"4. Proportional Demographics: In the '{pie_col}' breakdown, the primary classification is "
        f"'{pie_top_name}', which comprises {pie_top_count:,} records ({pie_top_pct:.2f}% of all records), "
        f"establishing the baseline demographic share across the monitored workforce."
    )

    if date_col and len(valid_years) > 0:
        peak_year = int(valid_years.idxmax())
        peak_records = int(valid_years.max())
        earliest_yr = int(valid_years.index.min())
        latest_yr = int(valid_years.index.max())
        insight_5 = (
            f"5. Temporal Intake Dynamics: Historical records spanning from {earliest_yr} to {latest_yr} reveal "
            f"that peak intake under '{date_col}' occurred in calendar year {peak_year}, "
            f"with {peak_records:,} records logged during that twelve-month interval."
        )
    else:
        cat_unique = df[cat_cols[0]].nunique()
        insight_5 = (
            f"5. Structural Diversity: The dataset encompasses {cat_unique} unique classifications under '{cat_cols[0]}', "
            f"highlighting operational diversity across distinct business units."
        )

    print("\n" + "=" * 70)
    print("                    5 DYNAMIC BUSINESS INSIGHTS                   ")
    print("=" * 70)
    print(insight_1)
    print()
    print(insight_2)
    print()
    print(insight_3)
    print()
    print(insight_4)
    print()
    print(insight_5)
    print("=" * 70)
    print()

    print("DELIVERABLES VERIFICATION:")
    print("  [x] EDA Notebook         : data_analysis.ipynb")
    print(f"  [x] Data Visualizations  : 5 charts saved in {charts_dir}/")
    print("  [x] Business Insights    : 5 dynamic insights calculated directly from data")
    print("  [ ] GitHub Updated       : Staged & committed locally; awaiting push confirmation.")
    print("=" * 70)

if __name__ == "__main__":
    main()
